
import sqlite3
from datetime import date
import sys
from db import create_connection, init_db, seed_menu_if_empty

# Initialize database and seed with a starter menu if empty
conn = create_connection()
c = conn.cursor()
init_db(conn)
seed_menu_if_empty(conn)
#id user not cooperative loop command till valid ineteger
def error_int(text):
    while True:
        try:
            exp = int(input(text)) 
            if exp >= 0:
                break
            else:
                    print("\n\t\tPlease enter a positive integer\n")
        except ValueError:
                print("\n\t\tPlease enter a valid integer\n")
    return exp

def max_orderid():
    c.execute("SELECT MAX(order_id) FROM customer;")
    tmp = c.fetchall()
    x = None
    if tmp[0][0] == x:
        return 0
    else:
        return (int(tmp[0][0]))


#check if the name enterd match a menus element if not loop
def check_inmenu(tex):
    check = []
    while(len(check) < 1):
        item = input(tex)
        c.execute("SELECT item FROM menu WHERE item = ?;", [item])
        check = c.fetchall()
        if len(check) < 1:
            print("\n\t\tThis element is not found in the menu\n")
    return item


#add a person into the customer table in the database
def add_person():
    receipt_input = "How many receipts you wanna enter : "
    num_pep = error_int(receipt_input)
    orlist = []
    order_id = max_orderid() + 1
    for i in range(0,num_pep,1):
        namp = input("Name :")
        orders_input = "How many orders : "
        order_num = error_int(orders_input)
        for j in range(0,order_num):
            inp = "Enter order :"
            orderf = check_inmenu(inp)
            quan_input = "How many : "
            quan = error_int(quan_input)
            orlist.extend((namp,quan,orderf,order_id))    
            c.execute("INSERT INTO customer VALUES(?,?,?,?);",orlist)
            orlist.clear()
        order_id += 1


#add an element to the menu 

def add_to_menu():
    menu_input = "Enter num of elements to add : "
    num_menu = error_int(menu_input)
    menu = {}
    list1 = []
    for i in range(0,num_menu,1):
        temp = input("Enter name of the element : ")
        menutemp_input = "Enter Price : "
        menu[temp] = error_int(menutemp_input)
        try:
            list1.extend((temp, menu[temp]))
            c.execute("INSERT INTO menu(item, price) VALUES(?, ?);", list1)
            print(f"Added '{temp}' to menu.")
        except sqlite3.IntegrityError:
            print(f"Item '{temp}' already exists. Updating price instead.")
            c.execute("UPDATE menu SET price = ? WHERE item = ?;", (menu[temp], temp))
        finally:
            list1.clear()
#delete a customer from the table takes the name as argument
def delete_customer(name):
    c.execute("DELETE FROM customer WHERE name = ?", [name])


#checks if name is in the database
def check_name(inp):
    listf = []
    while len(listf) < 1:
        name = input(inp)
        c.execute("SELECT name FROM customer WHERE name = ?", [name])
        listf = c.fetchall()
        if len(listf) < 1:
            print("\n\t\tThere's no customer with the given name\n")
    return name		


#deletes element from teh menu takes the element name as argument
def deletefrom_menu(ele):
    c.execute("DELETE FROM menu WHERE item = ?", [ele])


#updates an element price takes name and new price as arguemnt
def updateprice_menu(nam,new):
    tmplist = []
    tmplist.extend((int(new), nam))
    c.execute("UPDATE menu SET price = ? WHERE item = ?;", tmplist)
    tmplist.clear()


#get the prices of each order of a customer takes customers name as argument
def get_prices(order_id):
    # Return per-line totals for a given order_id
    c.execute("SELECT orders, quantity FROM customer WHERE order_id = ?;", [order_id])
    rows = c.fetchall()
    each_price = []
    for orders, quantity in rows:
        c.execute("SELECT price FROM menu WHERE item = ?;", (orders,))
        price_row = c.fetchone()
        price = int(price_row[0]) if price_row else 0
        each_price.append(int(quantity) * price)
    return each_price


#total of a customer purchase takes the list of all orders
def get_total(list_of_prices):
    total = 0
    for i in list_of_prices:
        total += i
    return total

def show_menu():
    c.execute("SELECT item, price FROM menu;")
    menu = c.fetchall()
    print("\n\tITEMS\t\t\t\tPRICES")
    print("\t******************************************")
    for i in range(0,len(menu)):
        print(f"\t{menu[i][0]}\t\t\t\t{menu[i][1]}")
        print("\t******************************************")




#generates a recipt for a customer takes name as argument
def generate_receipt(name):
    c.execute("SELECT DISTINCT order_id FROM customer WHERE name = ?", [name])
    order_id = c.fetchall()
    name = name.upper()
    s = ""
    if len(order_id) > 1:
        s += "S"
    print(f"\t\t   {name} HAS {len(order_id)} ORDER{s} :\n")
    for i in range(0,len(order_id)):
        prices = get_prices(order_id[i][0])
        c.execute("SELECT orders FROM customer WHERE order_id = ?", [order_id[i][0]])
        food = c.fetchall()
        total_price = get_total(prices)
        c.execute("SELECT quantity FROM customer WHERE order_id = ?", [order_id[i][0]])
        quantity = c.fetchall()
        print("\t******************************************")
        print("\t\t\tReceipt")
        print("\t******************************************")
        print(f"\tFor {name.upper()}",end="\t\t ")
        print(f" Date :{date.today()}")
        print("\t------------------------------------------")
        for j in range(0,len(food)):
            print(f"\t{quantity[j][0]} x {food[j][0]}\t\t\t{prices[j]}")
        print("\t------------------------------------------")
        print("\t------------------------------------------")
        print(f"\tTotal Amount\t\t\t{total_price}")
        print("\t------------------------------------------")
        print("\t\t****** THANK YOU ! ******\n\n")
        prices.clear()
        food.clear()
        quantity.clear()
    

#generates receipts of all customers
def all_receipts(): 
    c.execute("SELECT DISTINCT name FROM customer")
    names = c.fetchall()
    for i in range(0,len(names)):
        generate_receipt(names[i][0])

def main():
    while True:
        print("\t******************************************")
        print("\t\t     List of commands")
        print("\t******************************************")
        print("\t*\t1- Add customer")
        print("\t******************************************")
        print("\t*\t2- Add an element to the menu")
        print("\t******************************************")
        print("\t*\t3- Delete Customer")
        print("\t******************************************")
        print("\t*\t4- Delete element from the menu")
        print("\t******************************************")
        print("\t*\t5- Update the price of an element")
        print("\t******************************************")
        print("\t*\t6- Get a customer's receipt")
        print("\t******************************************")
        print("\t*\t7- Show all receipts")
        print("\t******************************************")
        print("\t*\t8- Show the menu")
        print("\t******************************************")

        command = "\n\tEnter a command : "
        choice = error_int(command)
        if choice == 1:
            add_person()
            conn.commit()
        
        elif choice == 2:
            add_to_menu()
            conn.commit()

        elif choice == 3:
            del_inp = "Enter the customer to delete : "
            name = check_name(del_inp)
            delete_customer(name)
            conn.commit()
        

        elif choice == 4:
            dele_inp = "Enter element to delete : "
            item = check_inmenu(dele_inp)
            deletefrom_menu(item)
            conn.commit()
        elif choice == 5:
            inp = "Enter element's name : "
            nam = check_inmenu(inp)
            price_inp = "Enter the new price : "
            price = error_int(price_inp)
            updateprice_menu(nam,price)
            conn.commit()


        elif choice == 6:
            cus_inp = "Enter a customer's name : "
            custom = check_name(cus_inp)
            generate_receipt(custom)

        elif choice == 7:
            all_receipts()
        elif choice == 8:
            show_menu()

        else:
            print(f"Check the list of commands no {choice} found")
        an = input("Do you want to do another operation ?\ny/yes or n/no : ")
        if an.lower() == 'n' or an.lower() == 'no':
            conn.close()
            break



if __name__ == '__main__':
    main()
