import tkinter as tk
from tkinter import ttk
import sqlite3

conn = sqlite3.connect('test.db')
c = conn.cursor()


def show_menu():
	c.execute("SELECT item FROM menu;")
	menu = c.fetchall()
	return menu

list_entry = []
list_order = []
input_num = 0

def max_orderid():
	c.execute("SELECT MAX(order_id) FROM customer;")
	tmp = c.fetchall()
	x = None
	if tmp[0][0] == x:
		return 0
	else:
		return (int(tmp[0][0]))

def menu_list():
    list1 = show_menu()
    list2 = []
    for i in range(0,len(list1)):
        list2.append(list1[i][0])
    return list2


def get_quantity(order_id,order):
    quan_extract = []
    quantity = []
    for i in range(len(order)):
        total_quan = 0
        quan_extract.extend((order_id,order[i][0]))
        c.execute("SELECT quantity FROM customer WHERE order_id =? AND orders LIKE ?;", quan_extract)
        quan = c.fetchall()
        for j in range(len(quan)):
            total_quan += quan[j][0]
        quantity.append(total_quan)
        quan_extract.clear()
    return quantity


def get_prices(order_id):
    c.execute("SELECT DISTINCT orders FROM customer WHERE order_id =?;", [order_id])
    billist = c.fetchall()
    for i in range(0,len(billist)):
        c.execute("SELECT price FROM menu WHERE item LIKE ?",(billist[i][0],))
        if i == 0:
            price_list = c.fetchall()
        else:
            price_list += c.fetchall()
    quantity = get_quantity(order_id,billist)
    each_price = []
    for i in range(0,len(billist)):
        each_price.append(int(quantity[i])*int(price_list[i][0]))
    return each_price

def get_total(list_of_prices):
	total = 0
	for i in list_of_prices:
		total += i
	return total

def clear_frame():
    for widget in frame.winfo_children():
        widget.destroy()
def back():
    clear_frame()
    func()
def get_quan(button):
    quantity = []
    for i in range(0,len(list_entry)):
        quantity.append(int(list_entry[i].get())) #id user not cooperative loop command till valid ineteger
    orders = []
    name = entry_name.get()
    for i in range(0,len(list_order)):
        orders.append(list_order[i].get())
    full_list = []
    order_id = max_orderid()
    num = len(list_entry)
    order_id += 1
    for i in range(0,num):
        full_list.extend((name,quantity[i],orders[i],order_id))     
        c.execute("INSERT INTO customer VALUES(?,?,?,?);",full_list)
        full_list.clear()
        list_order[i].destroy()
        list_entry[i].destroy()
    global input_num
    input_num += 1
    quantity.clear()
    orders.clear()
    full_list.clear()
    list_entry.clear()
    list_order.clear()
    get_input()
        
def get_all(num_e):
    label_add.destroy()
    num = num_e.get()
    num = int(num)
    list2 = menu_list()
    global list_entry
    global list_order
    for i in range(0,num):
        item = ttk.Combobox(frame)
        item['values'] = list2
        item.pack(padx=2, pady=1)
        entry1 = tk.Entry(frame)
        entry1.pack()
        list_entry.append(entry1)
        list_order.append(item)
    button_num = tk.Button(frame,text="order",command = lambda: get_quan(button_num))
    button_num.pack()

def get_input():
    clear_frame()
    global entry_name
    entry_name = tk.Entry(frame,text="Name : ")
    entry_name.pack()
    order_num = tk.IntVar()
    entry_num = tk.Entry(frame,text="How many elements you ordering : ",textvariable =order_num)
    entry_num.pack()
    if order_num != 0:
        global label_add
        label_add = tk.Label(frame,text="added succefully")
        label_add.pack()
    button_num = tk.Button(frame,text="hrtr",command = lambda: get_all(order_num))
    button_num.pack()
    button_b = tk.Button(frame,text="back",command=lambda: back())
    button_b.pack()



def add_element_data(elem,pric):
    element = elem.get()
    price = int(pric.get())
    list_price = []
    list_cmp = []
    j = 0
    list_price.extend((element,price))
    c.execute("SELECT item FROM menu;")
    list_cmp = c.fetchall()
    for i in range(0,len(list_cmp)):
        if element == list_cmp[i][0]:
            label_e = tk.Label(frame,text="This element already exists")
            label_e.pack()
            j += 1
    if j == 0:
        c.execute("INSERT INTO menu VALUES(?,?);",list_price)
        label_d = tk.Label(frame,text="Added Succefully")
        label_d.pack()
    list_price.clear()

def add_element():
    clear_frame()
    element = tk.StringVar()
    entry_element = tk.Entry(frame,text="Element : ",textvariable=element)
    entry_element.pack()
    price = tk.IntVar()
    entry_price = tk.Entry(frame,text="price : ",textvariable =price)
    entry_price.pack()
    button_num = tk.Button(frame,text="element",command = lambda: add_element_data(element,price))
    button_num.pack()
    button_b = tk.Button(frame,text="back",command=lambda: back())
    button_b.pack()
    



def delete_name(box):
    name = box.get()
    c.execute("DELETE FROM customer WHERE name LIKE ?;",[name])
    label = tk.Label(frame,text="deleted succefully")
    label.pack()
    delete_cus()

def delete_cus():
    clear_frame()
    label = tk.Label(frame,text="select customer to delete")
    label.pack()
    c.execute("SELECT DISTINCT name FROM customer;")
    list_n = c.fetchall()
    list_name = []
    for i in range(len(list_n)):
        list_name.append(list_n[i][0])
    names = ttk.Combobox(frame)
    names['values'] = list_name
    names.pack(padx=2, pady=1)
    button = tk.Button(frame,text="delete",command=lambda: delete_name(names))
    button.pack()
    button_b = tk.Button(frame,text="back",command=lambda: back())
    button_b.pack()



def delete_from_menu(box):
    elem = box.get()
    c.execute("DELETE FROM menu WHERE item LIKE ?;",[elem])
    label = tk.Label(frame,text="deleted succefully")
    label.pack()
    delete_ele()

def delete_ele():
    clear_frame()
    label = tk.Label(frame,text="select element to delete")
    label.pack()
    list_ele = menu_list()
    elements = ttk.Combobox(frame)
    elements['values'] = list_ele
    elements.pack(padx=2, pady=1)
    button = tk.Button(frame,text="delete",command=lambda: delete_from_menu(elements))
    button.pack()
    button_b = tk.Button(frame,text="back",command=lambda: back())
    button_b.pack()



def update_price(ele,num):
    element = ele.get()
    prices = int(num.get())
    list1 = []
    list1.extend((element,prices))
    c.execute("UPDATE menu SET price =? WHERE item LIKE ?;",list1)
    list1.clear()
    label = tk.Label(frame,text="update succefully")
    label.pack()
    update_p()

def update_p():
    clear_frame()
    label = tk.Label(frame,text="select element to update")
    label.pack()
    list_ele = menu_list()
    elements = ttk.Combobox(frame)
    elements['values'] = list_ele
    elements.pack(padx=2, pady=1)
    new = tk.IntVar()
    new_price = tk.Entry(frame,textvariable=new)
    new_price.pack()
    button = tk.Button(frame,text="update",command=lambda: update_price(elements,new))
    button.pack()
    button_b = tk.Button(frame,text="back",command=lambda: back())
    button_b.pack()

    

def show_receipt(entry):
    name = entry.get()
    c.execute("SELECT DISTINCT order_id FROM customer WHERE name LIKE ?;",[name])
    orderid_list = c.fetchall()
    quan_row = 4
    c.execute("SELECT orders FROM customer WHERE order_id LIKE '5'")
    list222 = c.fetchall()
    foo_row = 4
    price_row = 4
    for i in range(0,len(orderid_list)):
        prices = get_prices(orderid_list[i][0])
        c.execute("SELECT DISTINCT orders FROM customer WHERE order_id LIKE ?",[orderid_list[i][0]])
        food = c.fetchall()
        total_price = get_total(prices)
        quantity = get_quantity(orderid_list[i][0],food)
        orders_num = str(len(orderid_list))
        orders_num = orders_num + "Orders"
        label = tk.Label(frame,text=orders_num)
        label.grid(row = 3,column=3)
        for j in range(0,len(quantity)):
            label1 = tk.Label(frame,text=quantity[j])
            label1.grid(row=quan_row,column=2)
            label2 = tk.Label(frame,text=food[j][0])
            label2.grid(row=foo_row,column=0)
            label3 = tk.Label(frame,text=prices[j])
            label3.grid(row=price_row,column=4)
            foo_row += 1
            quan_row += 1
            price_row += 1
        label3 = tk.Label(frame,textvariable=total_price)
        label3.grid(row=6,column=3)
        if i == len(orderid_list) - 1:
            continue
        else:
            label = tk.Label(frame,text="new order")
            label.grid(row = quan_row,column=3)
        foo_row += 1
        quan_row += 1
        price_row += 1
        prices.clear()
        food.clear()
        quantity.clear()

def name_to_show():
    clear_frame()
    c.execute("SELECT DISTINCT name FROM customer;")
    list1 = c.fetchall()
    names = []
    for i in range(len(list1)):
        names.append(list1[i][0])
    item = ttk.Combobox(frame)
    item['values'] = names
    item.grid(row=0, column=0)
    button = tk.Button(frame,text="show receipt",command=lambda: show_receipt(item))
    button.grid(row=2,column=2)
    button_b = tk.Button(frame,text="back",command=lambda: back())
    button_b.grid(row = 0,column=6)











root = tk.Tk()
canvas = tk.Canvas(root,width=800,height=100)
canvas.grid()
frame = tk.Frame(root,width=500,height=500)
frame.grid()
def func():
    clear_frame()
    button = tk.Button(frame,text="choose",command=lambda: get_input())
    button.grid(row=0,column=3,sticky='e')
    label1 = tk.Label(frame,text="1-Add a customer")
    label1.grid(row=0,column=0,sticky='w')

    button = tk.Button(frame,text="choose",command=lambda: add_element())
    button.grid(row=5,column=3,sticky='e')
    label1 = tk.Label(frame,text="2-Add an element")
    label1.grid(row=5,column=0,sticky='w')

    button = tk.Button(frame,text="choose",command=lambda: delete_cus())
    button.grid(row=10,column=3,sticky='e')
    label1 = tk.Label(frame,text="3-delete cus")
    label1.grid(row=10,column=0,sticky='w')

    button = tk.Button(frame,text="choose",command=lambda: delete_ele())
    button.grid(row=15,column=3,sticky='e')
    label1 = tk.Label(frame,text="4-delete eleme")
    label1.grid(row=15,column=0,sticky='w')

    button = tk.Button(frame,text="choose",command=lambda: update_p())
    button.grid(row=20,column=3,sticky='e')
    label1 = tk.Label(frame,text="5-update the price")
    label1.grid(row=20,column=0,sticky='w')

    button = tk.Button(frame,text="choose",command=lambda: name_to_show())
    button.grid(row=25,column=3,sticky='e')
    label1 = tk.Label(frame,text="6- Get a customer's receipt")
    label1.grid(row=25,column=0,sticky='w')
    

func()
root.mainloop()
conn.commit()
conn.close()
