import sqlite3
from datetime import date
import sys

conn = sqlite3.connect('restaurant.db')

c = conn.cursor()

def add_person():
	while True:
		try:
			num_pep = int(input("How many receipts you wanna enter :"))
			if num_pep >= 0:
				break
			else:
					print("Please enter a positive integer")
		except ValueError:
				print("Please enter a valid integer")
	orlist = []
	for i in range(0,num_pep,1):
		namp = input("Name :")
		while True:
			try:
				order_num = int(input("How many orders :"))
				if order_num >= 0:
					break
				else:
					print("Please enter a positive integer")
			except ValueError:
				print("Please enter a valid integer")
		for j in range(0,order_num):
			check = []
			while(len(check) < 1):
				orderf = input("Enter order :")
				c.execute("SELECT item FROM menu WHERE item LIKE ?;",[orderf])
				check = c.fetchall()
				if len(check) < 1:
					print("This element is not found in the menu")
			while True:
				try:
					quan = int(input("How many orders :"))
					if quan >= 1:
						break
					else:
						print("Please enter a positive integer")
				except ValueError:
					print("Please enter a valid integer")
			orlist.extend((namp,quan,orderf))
			c.execute("INSERT INTO customer VALUES(?,?,?);",orlist)
			orlist.clear()


def check_in_menu(element):
	c.execute("SELECT item FROM menu WHERE item LIKE ?;",[element])
	i = 0
	tmp = c.fetchall()


def add_to_menu():

	while True:
		try:
			num_menu = int(input("Enter num of elements in the menu : "))
			if num_menu >= 0:
				break
			else:
				print("Please enter a positive integer")
		except ValueError:
			print("Please enter a valid integer")
	menu = {}
	list1 = []
	for i in range(0,num_menu,1):
		temp = input("Enter name of the element :")
		while True:
			try:
				menu[temp] = int(input("How many orders :"))
				if menu[temp] >= 0:
					break
				else:
					print("Please enter a positive integer")
			except ValueError:
				print("Please enter a valid integer")
		list1.extend((temp,menu[temp]))
		c.execute("INSERT INTO menu VALUES(?,?);",list1)
		list1.clear()

def deletefrom_menu(string):
	c.execute("DELETE FROM menu WHERE item LIKE ?",[string])
	print(string)

def updateprice_menu(nam,new):
	tmplist = []
	tmplist.extend((int(new),nam))
	c.execute("UPDATE menu SET price =? WHERE item LIKE ?;",tmplist)
	tmplist.clear()

def get_prices(name):
	c.execute("SELECT orders FROM customer WHERE name LIKE ?;", [name])
	billist = c.fetchall()
	for i in range(0,len(billist)):
		c.execute("SELECT price FROM menu WHERE item LIKE ?",(billist[i][0],))
		if i == 0:
			price_list = c.fetchall()
		else:
			price_list += c.fetchall()
	c.execute("SELECT quantity FROM customer WHERE name LIKE ?",[name])
	quan = c.fetchall()
	each_price = []
	total = 0
	for i in range(0,len(billist)):
		each_price.append(int(quan[i][0])*int(price_list[i][0]))
	return each_price


def get_total(list_of_prices):
	total = 0
	for i in list_of_prices:
		total += i
	return total



def generate_receipt(name):
	prices = get_prices(name)
	total_price = get_total(prices)
	c.execute("SELECT orders FROM customer WHERE name LIKE ?",[name])
	food = c.fetchall()
	c.execute("SELECT quantity FROM customer WHERE name LIKE ?",[name])
	quantity = c.fetchall()
	print("\t******************************************")
	print("\t\t\tReceipt")
	print("\t******************************************")
	print(f"\tFor {name.upper()}",end="\t\t ")
	print(f" Date :{date.today()}")
	print("\t------------------------------------------")
	for i in range(0,len(food)):
		print(f"\t{quantity[i][0]} x {food[i][0]}\t\t\t{prices[i]}")
	print("\t------------------------------------------")
	print("\t------------------------------------------")
	print(f"\tTotal Amount\t\t\t{total_price}")
	print("\t------------------------------------------")
	print("\t\t****** THANK YOU ! ******")


def main():
	add_person()

if __name__ == '__main__':
	main()
