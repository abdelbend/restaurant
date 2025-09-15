import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from db import create_connection, init_db, seed_menu_if_empty

# -----------------------------
# Small UI helpers
# -----------------------------


class ToolTip:
    """Very small tooltip helper for ttk widgets."""

    def __init__(self, widget, text, delay=600):
        self.widget = widget
        self.text = text
        self.delay = delay
        self._id = None
        self.tip = None
        widget.bind("<Enter>", self._schedule)
        widget.bind("<Leave>", self._hide)

    def _schedule(self, _):
        self._id = self.widget.after(self.delay, self._show)

    def _show(self):
        if self.tip is not None:
            return
        x, y, cx, cy = self.widget.bbox("insert") or (0, 0, 0, 0)
        x += self.widget.winfo_rootx() + 20
        y += self.widget.winfo_rooty() + 30
        self.tip = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        frame = ttk.Frame(tw, style="Tooltip.TFrame", padding=(8, 5))
        frame.pack()
        lbl = ttk.Label(frame, text=self.text, style="Tooltip.TLabel")
        lbl.pack()

    def _hide(self, _):
        if self._id:
            self.widget.after_cancel(self._id)
            self._id = None
        if self.tip:
            self.tip.destroy()
            self.tip = None


class RestaurantManagementSystem:
    def __init__(self):
        # -----------------------------
        # Root window
        # -----------------------------
        self.root = tk.Tk()
        self.root.title("Restaurant Management System · v1.1")
        self.root.geometry("1024x640")
        self.root.minsize(920, 560)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        # -----------------------------
        # Styling (clean, professional, subtle accent)
        # -----------------------------
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")  # stable, skinnable theme
        except Exception:
            pass

        # Palette
        self.COLOR_BG = "#0f172a"  # slate-900 header
        self.COLOR_CARD = "#ffffff"  # cards
        self.COLOR_ACCENT = "#2563eb"  # blue-600
        self.COLOR_ACCENT_DK = "#1e40af"  # blue-800
        self.COLOR_MUTED = "#64748b"  # slate-500
        self.COLOR_BORDER = "#e2e8f0"  # slate-200
        self.ROW_ALT = "#f8fafc"  # slate-50

        base_font = ("Segoe UI", 11)
        self.style.configure("TLabel", font=base_font, padding=2)
        self.style.configure("TButton", font=base_font, padding=(12, 8))
        self.style.configure("TEntry", padding=4)
        self.style.configure("TCombobox", padding=4)
        self.style.configure("Header.TLabel", font=(
            "Segoe UI Semibold", 20), foreground="#ffffff", background=self.COLOR_BG)
        self.style.configure("SubHeader.TLabel", font=(
            "Segoe UI", 12), foreground="#cbd5e1", background=self.COLOR_BG)
        self.style.configure("Toolbar.TFrame", background="#ffffff")
        self.style.configure(
            "Card.TLabelframe", background=self.COLOR_CARD, relief="solid", borderwidth=1)
        self.style.configure("Card.TLabelframe.Label", font=(
            "Segoe UI Semibold", 12), foreground="#0f172a")
        self.style.configure("Status.TLabel", anchor="w", padding=(12, 8))

        # Buttons (primary / danger / ghost)
        self.style.configure(
            "Primary.TButton", background=self.COLOR_ACCENT, foreground="#ffffff")
        self.style.map(
            "Primary.TButton",
            background=[("active", self.COLOR_ACCENT_DK),
                        ("pressed", self.COLOR_ACCENT_DK)],
            foreground=[("disabled", "#cbd5e1")],
        )
        self.style.configure(
            "Danger.TButton", background="#dc2626", foreground="#ffffff")
        self.style.map(
            "Danger.TButton",
            background=[("active", "#b91c1c"), ("pressed", "#b91c1c")],
        )
        self.style.configure(
            "Ghost.TButton", background="#ffffff", foreground="#0f172a")

        # Treeview polish
        self.style.configure(
            "Treeview",
            rowheight=28,
            bordercolor=self.COLOR_BORDER,
            lightcolor=self.COLOR_BORDER,
            darkcolor=self.COLOR_BORDER,
        )
        self.style.configure("Treeview.Heading",
                             font=("Segoe UI Semibold", 11))

        # Tooltip style
        self.style.configure(
            "Tooltip.TFrame", background="#111827", borderwidth=0)
        self.style.configure("Tooltip.TLabel", background="#111827",
                             foreground="#f9fafb", font=("Segoe UI", 10))

        # -----------------------------
        # DB
        # -----------------------------
        self.connect_to_database()

        # -----------------------------
        # Layout: Header, Toolbar, Content, Statusbar
        # -----------------------------
        self._build_header()
        self._build_toolbar()
        self._build_content()
        self._build_statusbar()

        # Default view
        self.show_dashboard()

        # Validators
        self.only_int = self.root.register(lambda P: P == "" or P.isdigit())

    # -----------------------------
    # Window sections
    # -----------------------------
    def _build_header(self):
        header = tk.Frame(self.root, bg=self.COLOR_BG, height=68)
        header.grid(row=0, column=0, sticky="nsew")
        header.grid_columnconfigure(0, weight=1)

        title = ttk.Label(
            header, text="Restaurant Management System", style="Header.TLabel")
        title.grid(row=0, column=0, sticky="w", padx=20, pady=(12, 0))
        subtitle = ttk.Label(
            header, text="Orders · Menu · Customers", style="SubHeader.TLabel")
        subtitle.grid(row=1, column=0, sticky="w", padx=20, pady=(0, 12))

    def _build_toolbar(self):
        toolbar = ttk.Frame(self.root, style="Toolbar.TFrame")
        toolbar.grid(row=1, column=0, sticky="ew")
        for i in range(1):
            toolbar.grid_columnconfigure(i, weight=1)

        # Toolbar buttons
        btns = [
            ("➕ Add Order", self.get_input, "Create a new customer order"),
            ("🍽️ Add Menu Item", self.add_element, "Insert or update a menu item"),
            ("✏️ Update Price", self.update_p, "Change the price of a menu item"),
            ("🧾 Customer Receipt", self.name_to_show,
             "View a customer's orders and totals"),
            ("🗑️ Delete Customer", self.delete_cus,
             "Remove all orders by a customer"),
            ("🗑️ Delete Menu Item", self.delete_ele,
             "Remove an item from the menu"),
        ]
        btnbar = ttk.Frame(toolbar)
        btnbar.grid(row=0, column=0, sticky="w", padx=16, pady=10)

        for i, (label, cmd, tip) in enumerate(btns):
            style = "Primary.TButton" if i in (0, 1) else "TButton"
            b = ttk.Button(btnbar, text=label, command=cmd, style=style)
            b.grid(row=0, column=i, padx=(0 if i == 0 else 8, 8))
            ToolTip(b, tip)

    def _build_content(self):
        # Main content area (uses a single swapping frame)
        self.content = ttk.Frame(self.root, padding=16)
        self.content.grid(row=2, column=0, sticky="nsew")
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def _build_statusbar(self):
        self.status_var = tk.StringVar(value="Ready")
        self.status = ttk.Label(
            self.root, textvariable=self.status_var, style="Status.TLabel")
        self.status.grid(row=3, column=0, sticky="ew")

    # -----------------------------
    # DB
    # -----------------------------
    def connect_to_database(self):
        try:
            self.conn = create_connection()
            self.cursor = self.conn.cursor()
            init_db(self.conn)
            seed_menu_if_empty(self.conn)
        except sqlite3.Error as e:
            messagebox.showerror("Database error", str(e))
            raise

    # -----------------------------
    # Utilities
    # -----------------------------
    def set_status(self, text: str, kind: str = "info"):
        prefix = {"info": "ℹ️", "ok": "✅",
                  "warn": "⚠️", "err": "❌"}.get(kind, "ℹ️")
        self.status_var.set(f"{prefix} {text}")

    def clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    def execute_query(self, query, parameters=None):
        try:
            if parameters is not None:
                self.cursor.execute(query, parameters)
            else:
                self.cursor.execute(query)
            qt = query.lstrip().split(" ", 1)[0].upper()
            if qt in {"INSERT", "UPDATE", "DELETE", "REPLACE"}:
                self.conn.commit()
                return []
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            self.set_status(f"DB error: {e}", "err")
            return []

    # -----------------------------
    # Dashboard (read-only snapshots)
    # -----------------------------
    def show_dashboard(self):
        self.clear_content()
        wrap = ttk.Frame(self.content)
        wrap.pack(fill="both", expand=True)
        wrap.grid_columnconfigure(0, weight=1)
        wrap.grid_columnconfigure(1, weight=1)

        # Card: Menu overview
        menu_card = ttk.Labelframe(
            wrap, text="Menu Overview", style="Card.TLabelframe", padding=12)
        menu_card.grid(row=0, column=0, sticky="nsew",
                       padx=(0, 12), pady=(0, 12))
        self._menu_tree = ttk.Treeview(menu_card, columns=(
            "item", "price"), show="headings", height=10)
        self._menu_tree.heading("item", text="Item")
        self._menu_tree.heading("price", text="Price")
        self._menu_tree.column("item", anchor="w", width=240)
        self._menu_tree.column("price", anchor="e", width=120)
        self._menu_tree.pack(fill="both", expand=True)
        self._refresh_menu_tree(self._menu_tree)

        # Card: Recent customers (names only)
        cust_card = ttk.Labelframe(
            wrap, text="Recent Customers", style="Card.TLabelframe", padding=12)
        cust_card.grid(row=0, column=1, sticky="nsew",
                       padx=(12, 0), pady=(0, 12))
        self._cust_tree = ttk.Treeview(cust_card, columns=(
            "name", "orders"), show="headings", height=10)
        self._cust_tree.heading("name", text="Customer")
        self._cust_tree.heading("orders", text="# Orders")
        self._cust_tree.column("name", anchor="w", width=240)
        self._cust_tree.column("orders", anchor="e", width=120)
        self._cust_tree.pack(fill="both", expand=True)
        self._refresh_recent_customers(self._cust_tree)

        self.set_status("Dashboard ready", "ok")

    def _refresh_menu_tree(self, tree):
        for i in tree.get_children():
            tree.delete(i)
        rows = self.execute_query(
            "SELECT item, price FROM menu ORDER BY item COLLATE NOCASE;")
        for idx, (item, price) in enumerate(rows):
            tag = "even" if idx % 2 == 0 else "odd"
            tree.insert("", "end", values=(item, price), tags=(tag,))
        tree.tag_configure("odd", background=self.ROW_ALT)

    def _refresh_recent_customers(self, tree):
        for i in tree.get_children():
            tree.delete(i)
        rows = self.execute_query(
            """
            SELECT name, COUNT(DISTINCT order_id) as cnt
            FROM customer
            GROUP BY name
            ORDER BY MAX(order_id) DESC
            LIMIT 20;
            """
        )
        for idx, (name, cnt) in enumerate(rows):
            tag = "even" if idx % 2 == 0 else "odd"
            tree.insert("", "end", values=(name, cnt), tags=(tag,))
        tree.tag_configure("odd", background=self.ROW_ALT)

    # -----------------------------
    # Menu helpers
    # -----------------------------
    def menu_list(self):
        rows = self.execute_query(
            "SELECT item FROM menu ORDER BY item COLLATE NOCASE;")
        return [r[0] for r in rows]

    def max_orderid(self):
        row = self.execute_query("SELECT MAX(order_id) FROM customer;")
        return row[0][0] if row and row[0][0] is not None else 0

    # -----------------------------
    # Views
    # -----------------------------
    def get_input(self):
        self.clear_content()
        card = ttk.Labelframe(self.content, text="Add Order",
                              style="Card.TLabelframe", padding=12)
        card.pack(fill="x", pady=(0, 12))

        form = ttk.Frame(card)
        form.pack(fill="x")

        ttk.Label(form, text="Customer Name") .grid(
            row=0, column=0, sticky="w", padx=(0, 8), pady=4)
        name_var = tk.StringVar()
        name_ent = ttk.Entry(form, textvariable=name_var, width=32)
        name_ent.grid(row=0, column=1, sticky="w", pady=4)

        ttk.Label(form, text="# of Items").grid(
            row=0, column=2, sticky="w", padx=(16, 8), pady=4)
        num_var = tk.StringVar()
        num_ent = ttk.Entry(form, textvariable=num_var, width=10, validate="key",
                            validatecommand=(self.only_int, "%P"))
        num_ent.grid(row=0, column=3, sticky="w", pady=4)

        nxt = ttk.Button(form, text="Next", style="Primary.TButton",
                         command=lambda: self.get_all(name_var, num_var))
        nxt.grid(row=0, column=4, padx=(16, 0))
        ToolTip(nxt, "Proceed to select items and quantities")

        self.set_status("Enter customer name and number of items")

    def get_all(self, name_var, num_var):
        name = name_var.get().strip()
        if not name:
            self.set_status("Please enter a customer name", "warn")
            return
        try:
            num = int(num_var.get())
        except ValueError:
            self.set_status("Please enter a valid number of items", "warn")
            return
        if num <= 0:
            self.set_status("Number of items must be > 0", "warn")
            return

        self.clear_content()
        card = ttk.Labelframe(self.content, text="Order Items",
                              style="Card.TLabelframe", padding=12)
        card.pack(fill="x", pady=(0, 12))

        list2 = self.menu_list()
        if not list2:
            self.set_status("Menu is empty. Add menu items first.", "warn")
            return

        rows_frame = ttk.Frame(card)
        rows_frame.pack(fill="x")

        item_vars = []
        qty_vars = []

        for i in range(num):
            ttk.Label(rows_frame, text=f"Item {i+1}").grid(row=i,
                                                           column=0, sticky="w", padx=(0, 8), pady=3)
            item_var = tk.StringVar(value=list2[0])
            cmb = ttk.Combobox(rows_frame, textvariable=item_var,
                               values=list2, width=36, state="readonly")
            cmb.grid(row=i, column=1, sticky="w", pady=3)

            ttk.Label(rows_frame, text="Qty").grid(
                row=i, column=2, sticky="w", padx=(12, 8))
            qty_var = tk.StringVar(value="1")
            qty = ttk.Entry(rows_frame, textvariable=qty_var, width=10, validate="key",
                            validatecommand=(self.only_int, "%P"))
            qty.grid(row=i, column=3, sticky="w")

            item_vars.append(item_var)
            qty_vars.append(qty_var)

        actions = ttk.Frame(card)
        actions.pack(fill="x", pady=(8, 0))
        place_btn = ttk.Button(actions, text="Place Order", style="Primary.TButton",
                               command=lambda: self.get_quan(name, item_vars, qty_vars))
        place_btn.pack(side="left")

        ttk.Button(actions, text="Cancel", command=self.show_dashboard).pack(
            side="left", padx=8)

        self.set_status("Select items and enter quantities")

    def get_quan(self, name, item_vars, qty_vars):
        try:
            quantities = [int(q.get()) for q in qty_vars]
        except ValueError:
            self.set_status("Enter numeric quantities for all items", "warn")
            return

        orders = [v.get() for v in item_vars]
        if any(not o for o in orders):
            self.set_status("All rows must have an item selected", "warn")
            return

        order_id = self.max_orderid() + 1
        for qty, item in zip(quantities, orders):
            if qty <= 0:
                self.set_status("Quantities must be > 0", "warn")
                return

        # Insert lines
        for qty, item in zip(quantities, orders):
            query = "INSERT INTO customer(name, quantity, orders, order_id) VALUES(?,?,?,?);"
            self.execute_query(query, (name, qty, item, order_id))

        self.set_status(f"Order #{order_id} for {name} placed", "ok")
        self.show_dashboard()

    def add_element(self):
        self.clear_content()
        card = ttk.Labelframe(
            self.content, text="Add / Update Menu Item", style="Card.TLabelframe", padding=12)
        card.pack(fill="x")

        form = ttk.Frame(card)
        form.pack(fill="x")

        ttk.Label(form, text="Item Name").grid(
            row=0, column=0, sticky="w", padx=(0, 8), pady=4)
        name_var = tk.StringVar()
        name_ent = ttk.Entry(form, textvariable=name_var, width=36)
        name_ent.grid(row=0, column=1, sticky="w", pady=4)

        ttk.Label(form, text="Price").grid(
            row=0, column=2, sticky="w", padx=(16, 8))
        price_var = tk.StringVar()
        price_ent = ttk.Entry(form, textvariable=price_var, width=12, validate="key",
                              validatecommand=(self.only_int, "%P"))
        price_ent.grid(row=0, column=3, sticky="w")

        def submit():
            item = name_var.get().strip()
            if not item:
                self.set_status("Please enter an item name", "warn")
                return
            try:
                price = int(price_var.get())
            except ValueError:
                self.set_status("Please enter a valid integer price", "warn")
                return

            exists = self.execute_query(
                "SELECT 1 FROM menu WHERE item = ?;", (item,))
            if exists:
                self.execute_query(
                    "UPDATE menu SET price = ? WHERE item = ?;", (price, item))
                self.set_status(f"Updated price for '{item}'", "ok")
            else:
                self.execute_query(
                    "INSERT INTO menu(item, price) VALUES(?, ?);", (item, price))
                self.set_status(f"Added '{item}' to menu", "ok")
            self.show_dashboard()

        ttk.Button(form, text="Save", style="Primary.TButton",
                   command=submit).grid(row=0, column=4, padx=(16, 0))
        ttk.Button(form, text="Back", command=self.show_dashboard).grid(
            row=0, column=5, padx=(8, 0))

        # Live menu table
        table_card = ttk.Labelframe(
            self.content, text="Current Menu", style="Card.TLabelframe", padding=12)
        table_card.pack(fill="both", expand=True, pady=(12, 0))
        tree = ttk.Treeview(table_card, columns=(
            "item", "price"), show="headings")
        tree.heading("item", text="Item")
        tree.heading("price", text="Price")
        tree.column("item", width=320, anchor="w")
        tree.column("price", width=120, anchor="e")
        tree.pack(fill="both", expand=True)
        self._refresh_menu_tree(tree)

    def delete_cus(self):
        self.clear_content()
        card = ttk.Labelframe(
            self.content, text="Delete Customer", style="Card.TLabelframe", padding=12)
        card.pack(fill="x")

        ttk.Label(card, text="Select customer to delete").grid(
            row=0, column=0, sticky="w")
        names = [r[0] for r in self.execute_query(
            "SELECT DISTINCT name FROM customer ORDER BY name COLLATE NOCASE;")]
        name_var = tk.StringVar()
        box = ttk.Combobox(card, textvariable=name_var,
                           values=names, width=36, state="readonly")
        box.grid(row=1, column=0, sticky="w", pady=6)

        def do_delete():
            name = name_var.get()
            if not name:
                self.set_status("Select a customer name", "warn")
                return
            if not messagebox.askyesno("Confirm", f"Delete ALL orders for '{name}'? This cannot be undone."):
                return
            self.execute_query("DELETE FROM customer WHERE name = ?;", (name,))
            self.set_status("Customer deleted", "ok")
            self.delete_cus()

        ttk.Button(card, text="Delete", style="Danger.TButton",
                   command=do_delete).grid(row=2, column=0, pady=(4, 0))
        ttk.Button(card, text="Back", command=self.show_dashboard).grid(
            row=2, column=1, padx=8)

    def delete_ele(self):
        self.clear_content()
        card = ttk.Labelframe(
            self.content, text="Delete Menu Item", style="Card.TLabelframe", padding=12)
        card.pack(fill="x")

        ttk.Label(card, text="Select item to delete").grid(
            row=0, column=0, sticky="w")
        elements = self.menu_list()
        item_var = tk.StringVar()
        box = ttk.Combobox(card, textvariable=item_var,
                           values=elements, width=36, state="readonly")
        box.grid(row=1, column=0, sticky="w", pady=6)

        def do_delete():
            item = item_var.get()
            if not item:
                self.set_status("Select an item to delete", "warn")
                return
            if not messagebox.askyesno("Confirm", f"Delete menu item '{item}'?"):
                return
            self.execute_query("DELETE FROM menu WHERE item = ?;", (item,))
            self.set_status("Menu item deleted", "ok")
            self.delete_ele()

        ttk.Button(card, text="Delete", style="Danger.TButton",
                   command=do_delete).grid(row=2, column=0, pady=(4, 0))
        ttk.Button(card, text="Back", command=self.show_dashboard).grid(
            row=2, column=1, padx=8)

    def update_p(self):
        self.clear_content()
        card = ttk.Labelframe(self.content, text="Update Price",
                              style="Card.TLabelframe", padding=12)
        card.pack(fill="x")

        ttk.Label(card, text="Select item").grid(row=0, column=0, sticky="w")
        elements = self.menu_list()
        item_var = tk.StringVar()
        box = ttk.Combobox(card, textvariable=item_var,
                           values=elements, width=36, state="readonly")
        box.grid(row=1, column=0, sticky="w", pady=6)

        ttk.Label(card, text="New Price").grid(
            row=1, column=1, sticky="w", padx=(16, 8))
        price_var = tk.StringVar()
        price_ent = ttk.Entry(card, textvariable=price_var, width=12, validate="key",
                              validatecommand=(self.only_int, "%P"))
        price_ent.grid(row=1, column=2, sticky="w")

        def do_update():
            item = item_var.get()
            if not item:
                self.set_status("Select an item to update", "warn")
                return
            try:
                price = int(price_var.get())
            except ValueError:
                self.set_status("Enter a valid integer price", "warn")
                return
            self.execute_query(
                "UPDATE menu SET price = ? WHERE item = ?;", (price, item))
            self.set_status("Price updated", "ok")
            self.update_p()

        ttk.Button(card, text="Update", style="Primary.TButton",
                   command=do_update).grid(row=2, column=0, pady=(4, 0))
        ttk.Button(card, text="Back", command=self.show_dashboard).grid(
            row=2, column=1, padx=8)

    def name_to_show(self):
        self.clear_content()
        card = ttk.Labelframe(
            self.content, text="Customer Receipt", style="Card.TLabelframe", padding=12)
        card.pack(fill="both", expand=True)

        top = ttk.Frame(card)
        top.pack(fill="x")

        names = [r[0] for r in self.execute_query(
            "SELECT DISTINCT name FROM customer ORDER BY name COLLATE NOCASE;")]
        ttk.Label(top, text="Customer").pack(side="left")
        name_var = tk.StringVar()
        box = ttk.Combobox(top, textvariable=name_var,
                           values=names, width=36, state="readonly")
        box.pack(side="left", padx=(8, 8))

        ttk.Button(top, text="Show Receipt", style="Primary.TButton",
                   command=lambda: self.show_receipt(box)).pack(side="left")

        # Tree
        cols = ("qty", "item", "price", "total")
        self.receipt = ttk.Treeview(
            card, columns=cols, show="headings", height=16)
        self.receipt.heading("qty", text="Qty")
        self.receipt.heading("item", text="Item")
        self.receipt.heading("price", text="Unit Price")
        self.receipt.heading("total", text="Line Total")
        self.receipt.column("qty", width=80, anchor="e")
        self.receipt.column("item", width=320, anchor="w")
        self.receipt.column("price", width=120, anchor="e")
        self.receipt.column("total", width=140, anchor="e")
        self.receipt.pack(fill="both", expand=True, pady=(8, 0))

        # scrollbar
        vs = ttk.Scrollbar(self.receipt, orient=tk.VERTICAL,
                           command=self.receipt.yview)
        self.receipt.configure(yscrollcommand=vs.set)
        vs.place(relx=1.0, rely=0, relheight=1.0, anchor="ne")

        self.total_label = ttk.Label(
            card, text="Total: 0", font=("Segoe UI Semibold", 12))
        self.total_label.pack(anchor="w", pady=(8, 0))

    def show_receipt(self, box):
        name = box.get()
        if not name:
            self.set_status("Select a customer to show receipt", "warn")
            return
        for i in self.receipt.get_children():
            self.receipt.delete(i)

        orderid_list = self.execute_query(
            "SELECT DISTINCT order_id FROM customer WHERE name = ? ORDER BY order_id;",
            (name,),
        )
        grand_total = 0
        row_index = 0

        for (oid,) in orderid_list:
            # Section label row
            self.receipt.insert("", "end", values=(
                "", f"Order #{oid}", "", ""))
            row_index += 1

            rows = self.execute_query(
                """
                SELECT c.quantity, c.orders, m.price
                FROM customer c
                JOIN menu m ON m.item = c.orders
                WHERE c.order_id = ?
                ORDER BY c.rowid
                """,
                (oid,),
            )
            order_total = 0
            for qty, item_name, unit_price in rows:
                line_total = int(qty) * int(unit_price)
                order_total += line_total
                tag = "odd" if (row_index % 2 == 1) else "even"
                self.receipt.insert("", "end", values=(
                    qty, item_name, unit_price, line_total), tags=(tag,))
                row_index += 1
            grand_total += order_total
            self.receipt.insert("", "end", values=(
                "", "—", "—", f"Subtotal: {order_total}"))
            row_index += 1

        self.receipt.tag_configure("odd", background=self.ROW_ALT)
        self.total_label.configure(text=f"Total: {grand_total}")
        self.set_status(f"Loaded receipt for {name}")

    # -----------------------------
    # Run
    # -----------------------------
    def run(self):
        self.root.mainloop()
        try:
            self.conn.commit()
            self.conn.close()
        except Exception:
            pass


if __name__ == "__main__":
    app = RestaurantManagementSystem()
    app.run()
