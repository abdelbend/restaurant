import tkinter as tk
from tkinter import ttk
import sqlite3

class RestaurantManagementSystem:
    def __init__(self):
        # Initialize the GUI
        self.root = tk.Tk()
        self.root.title("Restaurant Management System v1.0")
        self.root.geometry("600x400")

        # Configure the style for ttk widgets
        self.style = ttk.Style()
        self.style.configure("TButton", padding=5, relief="flat", foreground="white", background="#007BFF")
        self.style.configure("TLabel", padding=5, font=('Arial', 12))
        self.style.configure("TCombobox", padding=5, font=('Arial', 12))

        # Create widgets and connect to the database
        self.create_widgets()
        self.connect_to_database()

    def run(self):
        # Run the GUI main loop and commit changes to the database on exit
        self.root.mainloop()
        self.conn.commit()
        self.conn.close()

    def connect_to_database(self):
        # Connect to the SQLite database and create necessary tables
        try:
            self.conn = sqlite3.connect('restaurant.db')
            self.cursor = self.conn.cursor()
            self.create_tables()
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")

    def create_tables(self):
        # Create database tables if they do not exist
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS menu (
                    item TEXT PRIMARY KEY,
                    price INTEGER
                );
            ''')
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS customer (
                    name TEXT,
                    quantity INTEGER,
                    orders TEXT,
                    order_id INTEGER
                );
            ''')
        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")

    def create_widgets(self):
        # Create the main GUI widgets
        self.frame = ttk.Frame(self.root, padding="20")
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Label(self.frame, text="Restaurant Management System", style="TLabel").grid(row=0, column=0, columnspan=2, pady=10)
        
        # Define menu options and corresponding functions
        options = [
            ("Add a Customer", self.get_input),
            ("Add an Element", self.add_element),
            ("Delete Customer", self.delete_cus),
            ("Delete Element", self.delete_ele),
            ("Update the Price", self.update_p),
            ("Get a Customer's Receipt", self.name_to_show)
        ]

        # Create buttons for each menu option
        row_counter = 1
        for text, command in options:
            ttk.Button(self.frame, text=text, command=command, style="TButton").grid(row=row_counter, column=0, pady=5, sticky=tk.W)
            row_counter += 1

    def execute_query(self, query, parameters=None):
        # Execute an SQL query and return the result
        try:
            if parameters:
                self.cursor.execute(query, parameters)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error executing query: {e}")
            return []

    def clear_frame(self):
        # Clear all widgets in the main frame
        for widget in self.frame.winfo_children():
            widget.destroy()

    def get_input(self):
        # Function to get customer input for placing an order
        self.clear_frame()
        ttk.Label(self.frame, text="Enter Customer Name: ").grid(row=0, column=0)
        name_var = tk.StringVar()
        ttk.Entry(self.frame, textvariable=name_var).grid(row=0, column=1)
        order_num = tk.IntVar()
        ttk.Label(self.frame, text="How many elements are you ordering: ").grid(row=1, column=0)
        ttk.Entry(self.frame, textvariable=order_num).grid(row=1, column=1)
        ttk.Button(self.frame, text="Add", command=lambda: self.get_all(name_var, order_num)).grid(row=2, column=0)
        ttk.Button(self.frame, text="Back", command=self.create_widgets).grid(row=3, column=0)

    def get_all(self, name_var, num_e):
        # Function to get details of multiple items in an order
        self.clear_frame()
        label_add = ttk.Label(self.frame, text="Added Successfully")
        label_add.grid(row=0, column=0)

        name = name_var.get()
        num = num_e.get()
        num = int(num)
        list2 = self.menu_list()

        list_entry = []
        list_order = []

        for i in range(0, num):
            # Create dropdowns for menu items and entry fields for quantities
            item = ttk.Combobox(self.frame)
            item['values'] = list2
            item.grid(padx=2, pady=1)
            entry1 = ttk.Entry(self.frame)
            entry1.grid()
            list_entry.append(entry1)
            list_order.append(item)

        button_num = ttk.Button(self.frame, text="Order", command=lambda: self.get_quan(name, button_num, list_entry, list_order))
        button_num.grid()

    def add_element(self):
        # Function to add a new element (menu item)
        self.clear_frame()
        element = tk.StringVar()
        ttk.Label(self.frame, text="Enter Element Name: ").grid(row=0, column=0)
        ttk.Entry(self.frame, textvariable=element).grid(row=0, column=1)
        price = tk.IntVar()
        ttk.Label(self.frame, text="Enter Price: ").grid(row=1, column=0)
        ttk.Entry(self.frame, textvariable=price).grid(row=1, column=1)
        ttk.Button(self.frame, text="Add Element", command=lambda: self.add_element_data(element, price)).grid(row=2, column=0)
        ttk.Button(self.frame, text="Back", command=self.create_widgets).grid(row=3, column=0)

    def add_element_data(self, elem, pric):
        # Function to add data for a new element to the database
        element = elem.get()
        price = int(pric.get())
        list_price = []
        list_cmp = []

        list_price.extend((element, price))
        query = "SELECT item FROM menu;"
        list_cmp = self.execute_query(query)

        for i in range(len(list_cmp)):
            if element == list_cmp[i][0]:
                label_e = ttk.Label(self.frame, text="This element already exists")
                label_e.grid()
                return

        query = "INSERT INTO menu VALUES(?,?);"
        self.execute_query(query, list_price)

        label_d = ttk.Label(self.frame, text="Added Successfully")
        label_d.grid()

    def get_quan(self, name, button, list_entry, list_order):
        # Function to get quantities and process the customer's order
        quantity = [int(entry.get()) for entry in list_entry]

        orders = [order.get() for order in list_order]
        full_list = []

        order_id = self.max_orderid() + 1

        for i in range(len(list_entry)):
            full_list.extend((name, quantity[i], orders[i], order_id))
            query = "INSERT INTO customer VALUES(?,?,?,?);"
            self.execute_query(query, full_list)
            full_list.clear()
            list_order[i].destroy()
            list_entry[i].destroy()

        self.create_widgets()

    def delete_cus(self):
        # Function to delete a customer's record
        self.clear_frame()
        label = ttk.Label(self.frame, text="Select customer to delete")
        label.grid()

        query = "SELECT DISTINCT name FROM customer;"
        list_n = self.execute_query(query)
        list_name = [item[0] for item in list_n]

        names = ttk.Combobox(self.frame)
        names['values'] = list_name
        names.grid(padx=2, pady=1)

        button = ttk.Button(self.frame, text="Delete", command=lambda: self.delete_name(names))
        button.grid()
        ttk.Button(self.frame, text="Back", command=self.create_widgets).grid()

    def delete_name(self, box):
        # Function to delete a customer's record based on name
        name = box.get()
        query = "DELETE FROM customer WHERE name LIKE ?;"
        self.execute_query(query, [name])
        label = ttk.Label(self.frame, text="Deleted Successfully")
        label.grid()
        self.delete_cus()

    def delete_ele(self):
        # Function to delete a menu element
        self.clear_frame()
        label = ttk.Label(self.frame, text="Select element to delete")
        label.grid()

        list_ele = self.menu_list()
        elements = ttk.Combobox(self.frame)
        elements['values'] = list_ele
        elements.grid(padx=2, pady=1)

        button = ttk.Button(self.frame, text="Delete", command=lambda: self.delete_from_menu(elements))
        button.grid()
        ttk.Button(self.frame, text="Back", command=self.create_widgets).grid()

    def delete_from_menu(self, box):
        # Function to delete a menu element based on item name
        elem = box.get()
        query = "DELETE FROM menu WHERE item LIKE ?;"
        self.execute_query(query, [elem])
        label = ttk.Label(self.frame, text="Deleted Successfully")
        label.grid()
        self.delete_ele()

    def update_p(self):
        # Function to update the price of a menu element
        self.clear_frame()
        label = ttk.Label(self.frame, text="Select element to update")
        label.grid()

        list_ele = self.menu_list()
        elements = ttk.Combobox(self.frame)
        elements['values'] = list_ele
        elements.grid(padx=2, pady=1)

        new = tk.IntVar()
        ttk.Label(self.frame, text="Enter New Price: ").grid(row=1, column=2)
        ttk.Entry(self.frame, textvariable=new).grid(row=1, column=1)
        button = ttk.Button(self.frame, text="Update", command=lambda: self.update_price(elements, new))
        button.grid()
        ttk.Button(self.frame, text="Back", command=self.create_widgets).grid()

    def update_price(self, ele, num):
        # Function to update the price of a menu element in the database
        element = ele.get()
        prices = int(num.get())
        list1 = [element, prices]
        query = "UPDATE menu SET price =? WHERE item LIKE ?;"
        self.execute_query(query, list1)
        label = ttk.Label(self.frame, text="Update Successful")
        label.grid()
        self.update_p()
    
    def menu_list(self):
        # Function to retrieve the list of menu items from the database
        query = "SELECT item FROM menu;"
        menu_items = self.execute_query(query)
        return [item[0] for item in menu_items]

    def add_menu_item(self):
        # Function to add a new menu item to the database
        self.clear_frame()
        name_var = tk.StringVar()
        ttk.Label(self.frame, text="Enter New Menu Item: ").grid(row=0, column=0)
        ttk.Entry(self.frame, textvariable=name_var).grid(row=0, column=1)
        price_var = tk.DoubleVar()
        ttk.Label(self.frame, text="Enter Price: ").grid(row=1, column=0)
        ttk.Entry(self.frame, textvariable=price_var).grid(row=1, column=1)
        ttk.Button(self.frame, text="Add Menu Item", command=lambda: self.add_new_menu_item(name_var, price_var)).grid(row=2, column=0)
        ttk.Button(self.frame, text="Back", command=self.create_widgets).grid(row=3, column=0)

    def add_new_menu_item(self, name_var, price_var):
        # Function to add a new menu item to the database
        name = name_var.get()
        price = price_var.get()
        if name and price:
            query = "INSERT INTO menu VALUES (?, ?);"
            self.execute_query(query, (name, price))
            label = ttk.Label(self.frame, text="Menu Item Added Successfully")
            label.grid()
        else:
            label = ttk.Label(self.frame, text="Please enter both name and price")
            label.grid()

    def name_to_show(self):
        # Function to display a customer's receipt
        self.clear_frame()
        query = "SELECT DISTINCT name FROM customer;"
        list1 = self.execute_query(query)
        names = [item[0] for item in list1]

        item = ttk.Combobox(self.frame)
        item['values'] = names
        item.grid(row=0, column=0)

        button = ttk.Button(self.frame, text="Show Receipt", command=lambda: self.show_receipt(item))
        button.grid(row=2, column=2)
        ttk.Button(self.frame, text="Back", command=self.create_widgets).grid(row=0, column=6)

    def show_receipt(self, entry):
        # Function to display a customer's receipt with details of their orders
        name = entry.get()
        query = "SELECT DISTINCT order_id FROM customer WHERE name LIKE ?;"
        query_2 = "SELECT orders FROM customer WHERE name LIKE ?;"
        orderid_list = self.execute_query(query, [name])
        food_list = self.execute_query(query_2, [name])
        total_price = 0


        quan_row = 4
        foo_row = 4
        price_row = 4

        for i in range(len(orderid_list)):

            query = "SELECT DISTINCT orders FROM customer WHERE order_id LIKE ?;"
            food = self.execute_query(query, [orderid_list[i][0]])
            prices = self.get_prices(food_list[i][0])
            quantity = self.get_quantity(orderid_list[i][0], food)
            total_price += prices[0]* quantity[0]
        
            orders_num = str(len(orderid_list))
            orders_num = orders_num + " Orders"
            label = ttk.Label(self.frame, text=orders_num)
            label.grid(row=3, column=3)

            for j in range(len(quantity)):
                if j < len(prices):  # Check if j is within the valid range of prices
                    label1 = ttk.Label(self.frame, text=f"Quantity: {quantity[j]}")
                    label1.grid(row=quan_row, column=2)
                    label2 = ttk.Label(self.frame, text=f"Food: {food[j][0]}")
                    label2.grid(row=foo_row, column=0)
                    label3 = ttk.Label(self.frame, text=f"Price: {prices[j]}")
                    label3.grid(row=price_row, column=4)
                    foo_row += 1
                    quan_row += 1
                    price_row += 1

            if i == len(orderid_list) - 1:
                continue
            else:
                label = ttk.Label(self.frame, text="Next Order")
                label.grid(row=quan_row, column=2)

            foo_row += 1
            quan_row += 1
            price_row += 1
            prices.clear()
            food.clear()
            quantity.clear()
        label3 = ttk.Label(self.frame, text=f"Total Price: {total_price}")
        label3.grid()


    def get_prices(self, food):
        query = "SELECT DISTINCT price FROM menu WHERE item LIKE ?;"
        prices = self.execute_query(query, [food])
        return [price[0] for price in prices]

    def get_total(self, prices):
        total = sum(prices)
        return f"Total: {total}"

    def get_quantity(self, order_id, food):
        query = "SELECT DISTINCT quantity FROM customer WHERE order_id LIKE ?;"
        quantities = self.execute_query(query, [order_id])
        return [quantity[0] for quantity in quantities]

    def max_orderid(self):
        query = "SELECT MAX(order_id) FROM customer;"
        max_order_id = self.execute_query(query)
        return max_order_id[0][0] if max_order_id[0][0] else 0
    

    

if __name__ == "__main__":
    app = RestaurantManagementSystem()
    app.run()
