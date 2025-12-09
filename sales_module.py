"""
Sales Module - Handles all sales department operations
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

class SalesModule:
    def __init__(self, notebook, db, app):
        self.notebook = notebook
        self.db = db
        self.app = app
        
        # Create all sales tabs
        self.create_customers_tab()
        self.create_sales_order_tab()
        self.create_invoices_tab()
        self.create_sales_reports_tab()
    
    def refresh_all(self):
        """Refresh all sales tabs"""
        self.refresh_customers()
        self.refresh_sales_orders()
        self.refresh_invoices()
        self.refresh_sales_reports()
    
    # ==================== CUSTOMERS TAB ====================
    
    def create_customers_tab(self):
        """Create customers management tab"""
        cust_frame = ttk.Frame(self.notebook)
        self.notebook.add(cust_frame, text="👥 Customers")
        
        top_btn_frame = ttk.Frame(cust_frame)
        top_btn_frame.pack(side='top', fill='x', padx=10, pady=8)
        
        ttk.Button(top_btn_frame, text="➕ Add Customer", command=self.add_customer).pack(side='left', padx=3)
        ttk.Button(top_btn_frame, text="✏️ Edit", command=self.edit_customer).pack(side='left', padx=3)
        ttk.Button(top_btn_frame, text="🗑️ Delete", command=self.delete_customer).pack(side='left', padx=3)
        ttk.Button(top_btn_frame, text="🔄 Refresh", command=self.refresh_customers).pack(side='right', padx=3)
        
        columns = ("ID", "Name", "Contact", "Phone", "Email", "Credit Limit", "Terms")
        self.cust_tree = ttk.Treeview(cust_frame, columns=columns, show='headings', height=25)
        
        widths = [50, 150, 120, 100, 150, 100, 120]
        for i, col in enumerate(columns):
            self.cust_tree.heading(col, text=col)
            self.cust_tree.column(col, width=widths[i])
        
        self.cust_tree.pack(side='left', fill='both', expand=True, padx=10, pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(cust_frame, orient='vertical', command=self.cust_tree.yview)
        scrollbar.pack(side='right', fill='y', pady=(0, 10), padx=(0, 10))
        self.cust_tree.configure(yscrollcommand=scrollbar.set)
        
        self.refresh_customers()
    
    def refresh_customers(self):
        """Refresh customers display"""
        for item in self.cust_tree.get_children():
            self.cust_tree.delete(item)
        
        self.db.execute("SELECT customer_id, name, contact_person, phone, email, credit_limit, payment_terms FROM Customers")
        
        for row in self.db.fetchall():
            self.cust_tree.insert('', 'end', values=row)
    
    def add_customer(self):
        """Add new customer"""
        dialog = tk.Toplevel(self.app.root)
        dialog.title("Add Customer")
        dialog.geometry("450x400")
        dialog.resizable(False, False)
        dialog.transient(self.app.root)
        dialog.grab_set()
        
        fields = [
            ("Customer Name:", "name"),
            ("Contact Person:", "contact"),
            ("Phone:", "phone"),
            ("Email:", "email"),
            ("Address:", "address"),
            ("Credit Limit:", "credit"),
            ("Payment Terms:", "terms")
        ]
        
        entries = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(row=i, column=0, padx=10, pady=8, sticky='w')
            entry = ttk.Entry(dialog, width=30)
            entry.grid(row=i, column=1, padx=10, pady=8)
            entries[key] = entry
        
        def save():
            try:
                self.db.execute(
                    "INSERT INTO Customers (name, contact_person, phone, email, address, credit_limit, payment_terms) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (entries["name"].get(), entries["contact"].get(), entries["phone"].get(),
                     entries["email"].get(), entries["address"].get(), 
                     float(entries["credit"].get()) if entries["credit"].get() else 0,
                     entries["terms"].get())
                )
                self.db.commit()
                messagebox.showinfo("Success", "Customer added!")
                dialog.destroy()
                self.refresh_customers()
            except Exception as e:
                messagebox.showerror("Error", f"Failed: {str(e)}")
        
        ttk.Button(dialog, text="Save", command=save).grid(row=len(fields), column=0, columnspan=2, pady=15)
    
    def edit_customer(self):
        """Edit selected customer"""
        selected = self.cust_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a customer")
            return
        
        customer_id = self.cust_tree.item(selected[0])['values'][0]
        
        self.db.execute("SELECT name, contact_person, phone, email, address, credit_limit, payment_terms FROM Customers WHERE customer_id = ?", (customer_id,))
        data = self.db.fetchone()
        
        dialog = tk.Toplevel(self.app.root)
        dialog.title("Edit Customer")
        dialog.geometry("450x400")
        dialog.resizable(False, False)
        dialog.transient(self.app.root)
        dialog.grab_set()
        
        fields = ["Name:", "Contact:", "Phone:", "Email:", "Address:", "Credit Limit:", "Terms:"]
        entries = []
        
        for i, (field, value) in enumerate(zip(fields, data)):
            ttk.Label(dialog, text=field).grid(row=i, column=0, padx=10, pady=8, sticky='w')
            entry = ttk.Entry(dialog, width=30)
            entry.insert(0, value or "")
            entry.grid(row=i, column=1, padx=10, pady=8)
            entries.append(entry)
        
        def update():
            try:
                self.db.execute(
                    "UPDATE Customers SET name=?, contact_person=?, phone=?, email=?, address=?, credit_limit=?, payment_terms=? WHERE customer_id=?",
                    (entries[0].get(), entries[1].get(), entries[2].get(), entries[3].get(),
                     entries[4].get(), float(entries[5].get()) if entries[5].get() else 0,
                     entries[6].get(), customer_id)
                )
                self.db.commit()
                messagebox.showinfo("Success", "Customer updated!")
                dialog.destroy()
                self.refresh_customers()
            except Exception as e:
                messagebox.showerror("Error", f"Failed: {str(e)}")
        
        ttk.Button(dialog, text="Update", command=update).grid(row=len(fields), column=0, columnspan=2, pady=15)
    
    def delete_customer(self):
        """Delete selected customer"""
        selected = self.cust_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a customer")
            return
        
        values = self.cust_tree.item(selected[0])['values']
        customer_id, name = values[0], values[1]
        
        # Check if customer has orders
        self.db.execute("SELECT COUNT(*) FROM Sales_Orders WHERE customer_id = ?", (customer_id,))
        if self.db.fetchone()[0] > 0:
            messagebox.showwarning("Warning", f"Cannot delete '{name}' - has sales orders")
            return
        
        if messagebox.askyesno("Confirm", f"Delete customer '{name}'?"):
            try:
                self.db.execute("DELETE FROM Customers WHERE customer_id = ?", (customer_id,))
                self.db.commit()
                messagebox.showinfo("Success", "Customer deleted!")
                self.refresh_customers()
            except Exception as e:
                messagebox.showerror("Error", f"Failed: {str(e)}")
    
    # ==================== SALES ORDERS TAB ====================
    
    def create_sales_order_tab(self):
        """Create sales order tab"""
        so_frame = ttk.Frame(self.notebook)
        self.notebook.add(so_frame, text="🛍️ Sales Orders")
        
        top_btn_frame = ttk.Frame(so_frame)
        top_btn_frame.pack(side='top', fill='x', padx=10, pady=8)
        
        ttk.Button(top_btn_frame, text="➕ Create SO", command=self.create_sales_order).pack(side='left', padx=3)
        ttk.Button(top_btn_frame, text="👁️ View Details", command=self.view_so_details).pack(side='left', padx=3)
        ttk.Button(top_btn_frame, text="📄 Generate Invoice", command=self.generate_invoice_from_so).pack(side='left', padx=3)
        ttk.Button(top_btn_frame, text="🔄 Refresh", command=self.refresh_sales_orders).pack(side='right', padx=3)
        
        columns = ("SO#", "Customer", "Order Date", "Delivery Date", "Status", "Amount")
        self.so_tree = ttk.Treeview(so_frame, columns=columns, show='headings', height=25)
        
        for col in columns:
            self.so_tree.heading(col, text=col)
            self.so_tree.column(col, width=150)
        
        self.so_tree.pack(side='left', fill='both', expand=True, padx=10, pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(so_frame, orient='vertical', command=self.so_tree.yview)
        scrollbar.pack(side='right', fill='y', pady=(0, 10), padx=(0, 10))
        self.so_tree.configure(yscrollcommand=scrollbar.set)
        
        self.refresh_sales_orders()
    
    def refresh_sales_orders(self):
        """Refresh sales orders"""
        for item in self.so_tree.get_children():
            self.so_tree.delete(item)
        
        self.db.execute('''
            SELECT so.so_number, c.name, so.order_date, so.delivery_date, 
                   so.status, so.total_amount
            FROM Sales_Orders so
            JOIN Customers c ON so.customer_id = c.customer_id
            ORDER BY so.so_number DESC
        ''')
        
        for row in self.db.fetchall():
            self.so_tree.insert('', 'end', values=row)
    
    def create_sales_order(self):
        """Create new sales order"""
        self.db.execute("SELECT COUNT(*) FROM Customers")
        if self.db.fetchone()[0] == 0:
            messagebox.showwarning("Warning", "Add customers first")
            return
        
        self.db.execute("SELECT COUNT(*) FROM Items")
        if self.db.fetchone()[0] == 0:
            messagebox.showwarning("Warning", "Add items first")
            return
        
        dialog = tk.Toplevel(self.app.root)
        dialog.title("Create Sales Order")
        dialog.geometry("600x400")
        dialog.resizable(False, False)
        dialog.transient(self.app.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Customer:").grid(row=0, column=0, padx=10, pady=10, sticky='w')
        
        self.db.execute("SELECT customer_id, name FROM Customers")
        customers = self.db.fetchall()
        customer_dict = {f"{c[1]} (ID: {c[0]})": c[0] for c in customers}
        
        customer_var = tk.StringVar()
        customer_combo = ttk.Combobox(dialog, textvariable=customer_var, values=list(customer_dict.keys()), width=40, state='readonly')
        customer_combo.grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="Delivery Date (YYYY-MM-DD):").grid(row=1, column=0, padx=10, pady=10, sticky='w')
        delivery_entry = ttk.Entry(dialog, width=42)
        delivery_entry.insert(0, (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'))
        delivery_entry.grid(row=1, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="Item:").grid(row=2, column=0, padx=10, pady=10, sticky='w')
        
        self.db.execute('''
            SELECT i.item_id, i.name, i.selling_price, inv.quantity_on_hand
            FROM Items i
            JOIN Inventory inv ON i.item_id = inv.item_id
            WHERE inv.quantity_on_hand > 0
        ''')
        items = self.db.fetchall()
        
        if not items:
            messagebox.showwarning("Warning", "No items available in stock!")
            dialog.destroy()
            return
        
        item_dict = {f"{i[1]} (${i[2]}) [Stock: {i[3]}]": (i[0], i[2], i[3]) for i in items}
        
        item_var = tk.StringVar()
        item_combo = ttk.Combobox(dialog, textvariable=item_var, values=list(item_dict.keys()), width=40, state='readonly')
        item_combo.grid(row=2, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="Quantity:").grid(row=3, column=0, padx=10, pady=10, sticky='w')
        qty_entry = ttk.Entry(dialog, width=42)
        qty_entry.grid(row=3, column=1, padx=10, pady=10)
        
        # Stock availability label
        stock_label = ttk.Label(dialog, text="", foreground="blue")
        stock_label.grid(row=4, column=0, columnspan=2, pady=5)
        
        def on_item_select(event):
            if item_var.get():
                _, _, stock = item_dict[item_var.get()]
                stock_label.config(text=f"Available Stock: {stock} units")
        
        item_combo.bind('<<ComboboxSelected>>', on_item_select)
        
        def save():
            try:
                if not customer_var.get() or not item_var.get():
                    messagebox.showerror("Error", "Select customer and item")
                    return
                
                customer_id = customer_dict[customer_var.get()]
                item_id, selling_price, available_stock = item_dict[item_var.get()]
                quantity = int(qty_entry.get())
                
                # Check stock availability
                if quantity > available_stock:
                    messagebox.showerror("Error", f"Insufficient stock! Available: {available_stock}")
                    return
                
                if quantity <= 0:
                    messagebox.showerror("Error", "Quantity must be positive")
                    return
                
                subtotal = selling_price * quantity
                
                # Create sales order
                self.db.execute(
                    "INSERT INTO Sales_Orders (customer_id, order_date, delivery_date, status, total_amount) VALUES (?, ?, ?, ?, ?)",
                    (customer_id, datetime.now().date(), delivery_entry.get(), "Pending", subtotal)
                )
                so_number = self.db.lastrowid()
                
                # Add order items
                self.db.execute(
                    "INSERT INTO Sales_Order_Items (so_number, item_id, quantity, unit_price, subtotal) VALUES (?, ?, ?, ?, ?)",
                    (so_number, item_id, quantity, selling_price, subtotal)
                )
                
                # Reduce inventory
                self.db.execute(
                    "UPDATE Inventory SET quantity_on_hand = quantity_on_hand - ?, last_updated = ? WHERE item_id = ?",
                    (quantity, datetime.now(), item_id)
                )
                
                # Update SO status to Completed (since we're reducing inventory immediately)
                self.db.execute(
                    "UPDATE Sales_Orders SET status = 'Completed' WHERE so_number = ?",
                    (so_number,)
                )
                
                self.db.commit()
                messagebox.showinfo("Success", f"Sales Order #{so_number} created!\nInventory reduced by {quantity} units.")
                dialog.destroy()
                self.app.refresh_all_tabs()
            except Exception as e:
                messagebox.showerror("Error", f"Failed: {str(e)}")
        
        ttk.Button(dialog, text="Create Sales Order", command=save).grid(row=5, column=0, columnspan=2, pady=20)
    
    def view_so_details(self):
        """View sales order details"""
        selected = self.so_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a sales order")
            return
        
        so_number = self.so_tree.item(selected[0])['values'][0]
        
        dialog = tk.Toplevel(self.app.root)
        dialog.title(f"Sales Order #{so_number} Details")
        dialog.geometry("700x400")
        dialog.resizable(False, False)
        dialog.transient(self.app.root)
        dialog.grab_set()
        
        self.db.execute('''
            SELECT so.so_number, c.name, so.order_date, so.delivery_date, so.status, so.total_amount
            FROM Sales_Orders so
            JOIN Customers c ON so.customer_id = c.customer_id
            WHERE so.so_number = ?
        ''', (so_number,))
        
        so_info = self.db.fetchone()
        
        info_frame = ttk.LabelFrame(dialog, text="Order Info", padding=10)
        info_frame.pack(fill='x', padx=10, pady=10)
        
        labels = [
            f"SO#: {so_info[0]}",
            f"Customer: {so_info[1]}",
            f"Order Date: {so_info[2]}",
            f"Delivery: {so_info[3]}",
            f"Status: {so_info[4]}",
            f"Total: ${so_info[5]:.2f}"
        ]
        
        for i, text in enumerate(labels):
            ttk.Label(info_frame, text=text).grid(row=i//2, column=i%2, sticky='w', padx=10, pady=3)
        
        items_frame = ttk.LabelFrame(dialog, text="Items", padding=10)
        items_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        columns = ("Item", "Quantity", "Price", "Subtotal")
        tree = ttk.Treeview(items_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            tree.heading(col, text=col)
        
        tree.pack(fill='both', expand=True)
        
        self.db.execute('''
            SELECT i.name, soi.quantity, soi.unit_price, soi.subtotal
            FROM Sales_Order_Items soi
            JOIN Items i ON soi.item_id = i.item_id
            WHERE soi.so_number = ?
        ''', (so_number,))
        
        for row in self.db.fetchall():
            tree.insert('', 'end', values=row)
    
    def generate_invoice_from_so(self):
        """Generate invoice from selected SO"""
        selected = self.so_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a sales order")
            return
        
        so_values = self.so_tree.item(selected[0])['values']
        so_number = so_values[0]
        
        # Check if invoice already exists
        self.db.execute("SELECT invoice_id FROM Invoices WHERE so_number = ?", (so_number,))
        existing = self.db.fetchone()
        if existing:
            messagebox.showinfo("Info", f"Invoice #{existing[0]} already exists for this order")
            return
        
        # Get SO details
        self.db.execute('''
            SELECT customer_id, total_amount
            FROM Sales_Orders
            WHERE so_number = ?
        ''', (so_number,))
        
        customer_id, total_amount = self.db.fetchone()
        
        # Create invoice
        invoice_date = datetime.now().date()
        due_date = (datetime.now() + timedelta(days=30)).date()
        
        self.db.execute(
            "INSERT INTO Invoices (so_number, customer_id, invoice_date, due_date, total_amount, status) VALUES (?, ?, ?, ?, ?, ?)",
            (so_number, customer_id, invoice_date, due_date, total_amount, "Unpaid")
        )
        
        invoice_id = self.db.lastrowid()
        self.db.commit()
        
        messagebox.showinfo("Success", f"Invoice #{invoice_id} generated!\nDue Date: {due_date}")
        self.refresh_invoices()
    
    # ==================== INVOICES TAB ====================
    
    def create_invoices_tab(self):
        """Create invoices tab"""
        inv_frame = ttk.Frame(self.notebook)
        self.notebook.add(inv_frame, text="📄 Invoices")
        
        top_btn_frame = ttk.Frame(inv_frame)
        top_btn_frame.pack(side='top', fill='x', padx=10, pady=8)
        
        ttk.Button(top_btn_frame, text="💰 Mark as Paid", command=self.mark_invoice_paid).pack(side='left', padx=3)
        ttk.Button(top_btn_frame, text="👁️ View Details", command=self.view_invoice_details).pack(side='left', padx=3)
        ttk.Button(top_btn_frame, text="🔄 Refresh", command=self.refresh_invoices).pack(side='right', padx=3)
        
        columns = ("Invoice#", "SO#", "Customer", "Invoice Date", "Due Date", "Amount", "Status")
        self.invoice_tree = ttk.Treeview(inv_frame, columns=columns, show='headings', height=25)
        
        for col in columns:
            self.invoice_tree.heading(col, text=col)
            self.invoice_tree.column(col, width=130)
        
        self.invoice_tree.pack(side='left', fill='both', expand=True, padx=10, pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(inv_frame, orient='vertical', command=self.invoice_tree.yview)
        scrollbar.pack(side='right', fill='y', pady=(0, 10), padx=(0, 10))
        self.invoice_tree.configure(yscrollcommand=scrollbar.set)
        
        self.refresh_invoices()
    
    def refresh_invoices(self):
        """Refresh invoices"""
        for item in self.invoice_tree.get_children():
            self.invoice_tree.delete(item)
        
        self.db.execute('''
            SELECT inv.invoice_id, inv.so_number, c.name, inv.invoice_date, 
                   inv.due_date, inv.total_amount, inv.status
            FROM Invoices inv
            JOIN Customers c ON inv.customer_id = c.customer_id
            ORDER BY inv.invoice_id DESC
        ''')
        
        for row in self.db.fetchall():
            tag = 'unpaid' if row[6] == 'Unpaid' else 'paid'
            self.invoice_tree.insert('', 'end', values=row, tags=(tag,))
        
        self.invoice_tree.tag_configure('unpaid', background='#ffe6e6')
        self.invoice_tree.tag_configure('paid', background='#e6ffe6')
    
    def mark_invoice_paid(self):
        """Mark selected invoice as paid"""
        selected = self.invoice_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select an invoice")
            return
        
        invoice_id = self.invoice_tree.item(selected[0])['values'][0]
        
        self.db.execute("UPDATE Invoices SET status = 'Paid' WHERE invoice_id = ?", (invoice_id,))
        self.db.commit()
        
        messagebox.showinfo("Success", f"Invoice #{invoice_id} marked as Paid!")
        self.refresh_invoices()
    
    def view_invoice_details(self):
        """View invoice details"""
        selected = self.invoice_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select an invoice")
            return
        
        invoice_values = self.invoice_tree.item(selected[0])['values']
        
        msg = f"Invoice Details\n\n"
        msg += f"Invoice #: {invoice_values[0]}\n"
        msg += f"Sales Order #: {invoice_values[1]}\n"
        msg += f"Customer: {invoice_values[2]}\n"
        msg += f"Invoice Date: {invoice_values[3]}\n"
        msg += f"Due Date: {invoice_values[4]}\n"
        msg += f"Amount: ${invoice_values[5]:.2f}\n"
        msg += f"Status: {invoice_values[6]}\n"
        
        messagebox.showinfo("Invoice Details", msg)
    
    # ==================== SALES REPORTS TAB ====================
    
    def create_sales_reports_tab(self):
        """Create sales reports tab"""
        report_frame = ttk.Frame(self.notebook)
        self.notebook.add(report_frame, text="📊 Sales Reports")
        
        # Summary frame
        summary_frame = ttk.LabelFrame(report_frame, text="Sales Summary", padding=20)
        summary_frame.pack(fill='x', padx=10, pady=10)
        
        self.total_sales_label = ttk.Label(summary_frame, text="Total Sales: $0.00", font=('Arial', 12, 'bold'))
        self.total_sales_label.grid(row=0, column=0, padx=20, pady=5, sticky='w')
        
        self.total_orders_label = ttk.Label(summary_frame, text="Total Orders: 0", font=('Arial', 12))
        self.total_orders_label.grid(row=0, column=1, padx=20, pady=5, sticky='w')
        
        self.pending_orders_label = ttk.Label(summary_frame, text="Pending: 0", font=('Arial', 12))
        self.pending_orders_label.grid(row=1, column=0, padx=20, pady=5, sticky='w')
        
        self.completed_orders_label = ttk.Label(summary_frame, text="Completed: 0", font=('Arial', 12))
        self.completed_orders_label.grid(row=1, column=1, padx=20, pady=5, sticky='w')
        
        self.unpaid_invoices_label = ttk.Label(summary_frame, text="Unpaid Invoices: 0 ($0.00)", font=('Arial', 12))
        self.unpaid_invoices_label.grid(row=2, column=0, columnspan=2, padx=20, pady=5, sticky='w')
        
        ttk.Button(summary_frame, text="🔄 Refresh Reports", command=self.refresh_sales_reports).grid(row=3, column=0, columnspan=2, pady=15)
        
        # Top selling items frame
        items_frame = ttk.LabelFrame(report_frame, text="Top Selling Items", padding=10)
        items_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        columns = ("Item", "Quantity Sold", "Revenue")
        self.top_items_tree = ttk.Treeview(items_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.top_items_tree.heading(col, text=col)
            self.top_items_tree.column(col, width=200)
        
        self.top_items_tree.pack(fill='both', expand=True)
        
        self.refresh_sales_reports()
    
    def refresh_sales_reports(self):
        """Refresh sales reports"""
        # Total sales amount
        self.db.execute("SELECT COALESCE(SUM(total_amount), 0) FROM Sales_Orders")
        total_sales = self.db.fetchone()[0]
        self.total_sales_label.config(text=f"Total Sales: ${total_sales:.2f}")
        
        # Total orders count
        self.db.execute("SELECT COUNT(*) FROM Sales_Orders")
        total_orders = self.db.fetchone()[0]
        self.total_orders_label.config(text=f"Total Orders: {total_orders}")
        
        # Pending orders
        self.db.execute("SELECT COUNT(*) FROM Sales_Orders WHERE status = 'Pending'")
        pending = self.db.fetchone()[0]
        self.pending_orders_label.config(text=f"Pending: {pending}")
        
        # Completed orders
        self.db.execute("SELECT COUNT(*) FROM Sales_Orders WHERE status = 'Completed'")
        completed = self.db.fetchone()[0]
        self.completed_orders_label.config(text=f"Completed: {completed}")
        
        # Unpaid invoices
        self.db.execute("SELECT COUNT(*), COALESCE(SUM(total_amount), 0) FROM Invoices WHERE status = 'Unpaid'")
        unpaid_count, unpaid_amount = self.db.fetchone()
        self.unpaid_invoices_label.config(text=f"Unpaid Invoices: {unpaid_count} (${unpaid_amount:.2f})")
            
    def generate_invoice_from_so(self):
        """Generate invoice from selected SO"""
        selected = self.so_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a sales order")
            return
        
        so_number = self.so_tree.item(selected[0])['values'][0]

        # Fetch SO info
        self.db.execute("""
            SELECT customer_id, total_amount 
            FROM Sales_Orders 
            WHERE so_number = ?
        """, (so_number,))
        so_data = self.db.fetchone()

        if not so_data:
            messagebox.showerror("Error", "Sales order not found")
            return
        
        customer_id, so_total = so_data

        # Check if invoice already exists
        self.db.execute("""
            SELECT COUNT(*) FROM Invoices WHERE so_number = ?
        """, (so_number,))
        if self.db.fetchone()[0] > 0:
            messagebox.showwarning("Warning", "Invoice already generated for this SO")
            return
        
        # Create invoice
        invoice_date = datetime.now().date()

        self.db.execute("""
            INSERT INTO Invoices (customer_id, so_number, invoice_date, total_amount)
            VALUES (?, ?, ?, ?)
        """, (customer_id, so_number, invoice_date, so_total))
        
        invoice_id = self.db.lastrowid()

        # Fetch SO items
        self.db.execute("""
            SELECT item_id, quantity, unit_price, subtotal
            FROM Sales_Order_Items
            WHERE so_number = ?
        """, (so_number,))
        
        so_items = self.db.fetchall()

        # Create invoice items
        for item_id, qty, price, subtotal in so_items:
            self.db.execute("""
                INSERT INTO Invoice_Items (invoice_id, item_id, quantity, unit_price, subtotal)
                VALUES (?, ?, ?, ?, ?)
            """, (invoice_id, item_id, qty, price, subtotal))

        # Update order status
        self.db.execute("""
            UPDATE Sales_Orders SET status = 'Invoiced' WHERE so_number = ?
        """, (so_number,))

        self.db.commit()
        messagebox.showinfo("Success", f"Invoice #{invoice_id} generated for SO #{so_number}")
        self.refresh_invoices()
