"""
Purchase Module - Handles all purchase department operations
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class PurchaseModule:
    def __init__(self, notebook, db, app):
        self.notebook = notebook
        self.db = db
        self.app = app
        
        # Create all purchase tabs
        self.create_inventory_tab()
        self.create_purchase_order_tab()
        self.create_suppliers_tab()
        self.create_goods_receipt_tab()
        self.create_alerts_tab()
    
    def refresh_all(self):
        """Refresh all purchase tabs"""
        self.refresh_inventory()
        self.refresh_purchase_orders()
        self.refresh_suppliers()
        self.refresh_receipt_history()
        self.refresh_alerts()
    
    # ==================== INVENTORY TAB ====================
    
    def create_inventory_tab(self):
        """Create inventory management tab"""
        inv_frame = ttk.Frame(self.notebook)
        self.notebook.add(inv_frame, text="📦 Inventory")
        
        top_btn_frame = ttk.Frame(inv_frame)
        top_btn_frame.pack(side='top', fill='x', padx=10, pady=8)
        
        ttk.Button(top_btn_frame, text="➕ Add Item", command=self.add_new_item).pack(side='left', padx=3)
        ttk.Button(top_btn_frame, text="✏️ Edit", command=self.edit_item).pack(side='left', padx=3)
        ttk.Button(top_btn_frame, text="🗑️ Delete", command=self.delete_item).pack(side='left', padx=3)
        ttk.Button(top_btn_frame, text="🔄 Refresh", command=self.refresh_inventory).pack(side='right', padx=3)
        
        columns = ("ID", "Name", "Category", "Qty", "Reorder", "Buy", "Sell", "Location", "Status")
        self.inv_tree = ttk.Treeview(inv_frame, columns=columns, show='headings', height=25)
        
        widths = [50, 150, 100, 60, 70, 80, 80, 100, 70]
        for i, col in enumerate(columns):
            self.inv_tree.heading(col, text=col)
            self.inv_tree.column(col, width=widths[i])
        
        self.inv_tree.pack(side='left', fill='both', expand=True, padx=10, pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(inv_frame, orient='vertical', command=self.inv_tree.yview)
        scrollbar.pack(side='right', fill='y', pady=(0, 10), padx=(0, 10))
        self.inv_tree.configure(yscrollcommand=scrollbar.set)
        
        self.refresh_inventory()
    
    def refresh_inventory(self):
        """Refresh inventory display"""
        for item in self.inv_tree.get_children():
            self.inv_tree.delete(item)
        
        self.db.execute('''
            SELECT i.item_id, i.name, i.category, inv.quantity_on_hand, 
                   inv.reorder_level, i.unit_price, i.selling_price, inv.location
            FROM Items i
            JOIN Inventory inv ON i.item_id = inv.item_id
            ORDER BY i.name
        ''')
        
        for row in self.db.fetchall():
            status = "LOW" if row[3] <= row[4] else "OK"
            tag = 'low' if status == "LOW" else ''
            self.inv_tree.insert('', 'end', values=row + (status,), tags=(tag,))
        
        self.inv_tree.tag_configure('low', background='#ffcccc')
    
    def add_new_item(self):
        """Add new item dialog"""
        dialog = tk.Toplevel(self.app.root)
        dialog.title("Add New Item")
        dialog.geometry("450x450")
        dialog.resizable(False, False)
        dialog.transient(self.app.root)
        dialog.grab_set()
        
        fields = [
            ("Item Name:", "name"),
            ("Description:", "desc"),
            ("Category:", "cat"),
            ("Unit of Measure:", "uom"),
            ("Purchase Price:", "price"),
            ("Selling Price:", "sell_price"),
            ("Initial Quantity:", "qty"),
            ("Reorder Level:", "reorder"),
            ("Location:", "loc")
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
                    "INSERT INTO Items (name, description, category, unit_of_measure, unit_price, selling_price) VALUES (?, ?, ?, ?, ?, ?)",
                    (entries["name"].get(), entries["desc"].get(), entries["cat"].get(), 
                     entries["uom"].get(), float(entries["price"].get()), float(entries["sell_price"].get()))
                )
                item_id = self.db.lastrowid()
                
                self.db.execute(
                    "INSERT INTO Inventory (item_id, quantity_on_hand, reorder_level, location, last_updated) VALUES (?, ?, ?, ?, ?)",
                    (item_id, int(entries["qty"].get()), int(entries["reorder"].get()), entries["loc"].get(), datetime.now())
                )
                
                self.db.commit()
                messagebox.showinfo("Success", "Item added!")
                dialog.destroy()
                self.app.refresh_all_tabs()
            except Exception as e:
                messagebox.showerror("Error", f"Failed: {str(e)}")
        
        ttk.Button(dialog, text="Save", command=save).grid(row=len(fields), column=0, columnspan=2, pady=15)
    
    def edit_item(self):
        """Edit selected item"""
        selected = self.inv_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item")
            return
        
        item_id = self.inv_tree.item(selected[0])['values'][0]
        
        self.db.execute('''
            SELECT i.name, i.description, i.category, i.unit_of_measure, i.unit_price, i.selling_price,
                   inv.quantity_on_hand, inv.reorder_level, inv.location
            FROM Items i JOIN Inventory inv ON i.item_id = inv.item_id WHERE i.item_id = ?
        ''', (item_id,))
        
        data = self.db.fetchone()
        
        dialog = tk.Toplevel(self.app.root)
        dialog.title("Edit Item")
        dialog.geometry("450x450")
        dialog.resizable(False, False)
        dialog.transient(self.app.root)
        dialog.grab_set()
        
        fields = [
            ("Item Name:", data[0]),
            ("Description:", data[1] or ""),
            ("Category:", data[2] or ""),
            ("Unit of Measure:", data[3] or ""),
            ("Purchase Price:", data[4]),
            ("Selling Price:", data[5]),
            ("Quantity:", data[6]),
            ("Reorder Level:", data[7]),
            ("Location:", data[8] or "")
        ]
        
        entries = []
        for i, (label, value) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(row=i, column=0, padx=10, pady=8, sticky='w')
            entry = ttk.Entry(dialog, width=30)
            entry.insert(0, value)
            entry.grid(row=i, column=1, padx=10, pady=8)
            entries.append(entry)
        
        def update():
            try:
                self.db.execute(
                    "UPDATE Items SET name=?, description=?, category=?, unit_of_measure=?, unit_price=?, selling_price=? WHERE item_id=?",
                    (entries[0].get(), entries[1].get(), entries[2].get(), entries[3].get(), 
                     float(entries[4].get()), float(entries[5].get()), item_id)
                )
                self.db.execute(
                    "UPDATE Inventory SET quantity_on_hand=?, reorder_level=?, location=?, last_updated=? WHERE item_id=?",
                    (int(entries[6].get()), int(entries[7].get()), entries[8].get(), datetime.now(), item_id)
                )
                self.db.commit()
                messagebox.showinfo("Success", "Item updated!")
                dialog.destroy()
                self.app.refresh_all_tabs()
            except Exception as e:
                messagebox.showerror("Error", f"Failed: {str(e)}")
        
        ttk.Button(dialog, text="Update", command=update).grid(row=len(fields), column=0, columnspan=2, pady=15)
    
    def delete_item(self):
        """Delete selected item"""
        selected = self.inv_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item")
            return
        
        item_values = self.inv_tree.item(selected[0])['values']
        
        if messagebox.askyesno("Confirm", f"Delete '{item_values[1]}'?"):
            try:
                self.db.execute("DELETE FROM Inventory WHERE item_id = ?", (item_values[0],))
                self.db.execute("DELETE FROM Items WHERE item_id = ?", (item_values[0],))
                self.db.commit()
                messagebox.showinfo("Success", "Item deleted!")
                self.app.refresh_all_tabs()
            except Exception as e:
                messagebox.showerror("Error", f"Failed: {str(e)}")
    
    # ==================== PURCHASE ORDERS TAB ====================
    
    def create_purchase_order_tab(self):
        """Create purchase order tab"""
        po_frame = ttk.Frame(self.notebook)
        self.notebook.add(po_frame, text="🛒 Purchase Orders")
        
        top_btn_frame = ttk.Frame(po_frame)
        top_btn_frame.pack(side='top', fill='x', padx=10, pady=8)
        
        ttk.Button(top_btn_frame, text="➕ Create PO", command=self.create_purchase_order).pack(side='left', padx=3)
        ttk.Button(top_btn_frame, text="👁️ View Details", command=self.view_po_details).pack(side='left', padx=3)
        ttk.Button(top_btn_frame, text="🔄 Refresh", command=self.refresh_purchase_orders).pack(side='right', padx=3)
        
        columns = ("PO#", "Supplier", "Order Date", "Delivery", "Status", "Amount")
        self.po_tree = ttk.Treeview(po_frame, columns=columns, show='headings', height=25)
        
        for col in columns:
            self.po_tree.heading(col, text=col)
            self.po_tree.column(col, width=150)
        
        self.po_tree.pack(side='left', fill='both', expand=True, padx=10, pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(po_frame, orient='vertical', command=self.po_tree.yview)
        scrollbar.pack(side='right', fill='y', pady=(0, 10), padx=(0, 10))
        self.po_tree.configure(yscrollcommand=scrollbar.set)
        
        self.refresh_purchase_orders()
    
    def refresh_purchase_orders(self):
        """Refresh purchase orders"""
        for item in self.po_tree.get_children():
            self.po_tree.delete(item)
        
        self.db.execute('''
            SELECT po.po_number, s.name, po.order_date, po.expected_delivery, 
                   po.status, po.total_amount
            FROM Purchase_Orders po
            JOIN Suppliers s ON po.supplier_id = s.supplier_id
            ORDER BY po.po_number DESC
        ''')
        
        for row in self.db.fetchall():
            self.po_tree.insert('', 'end', values=row)
    
    def create_purchase_order(self):
        """Create new PO"""
        self.db.execute("SELECT COUNT(*) FROM Suppliers")
        if self.db.fetchone()[0] == 0:
            messagebox.showwarning("Warning", "Add suppliers first")
            return
        
        self.db.execute("SELECT COUNT(*) FROM Items")
        if self.db.fetchone()[0] == 0:
            messagebox.showwarning("Warning", "Add items first")
            return
        
        dialog = tk.Toplevel(self.app.root)
        dialog.title("Create Purchase Order")
        dialog.geometry("600x350")
        dialog.resizable(False, False)
        dialog.transient(self.app.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Supplier:").grid(row=0, column=0, padx=10, pady=10, sticky='w')
        
        self.db.execute("SELECT supplier_id, name FROM Suppliers")
        suppliers = self.db.fetchall()
        supplier_dict = {f"{s[1]} (ID: {s[0]})": s[0] for s in suppliers}
        
        supplier_var = tk.StringVar()
        supplier_combo = ttk.Combobox(dialog, textvariable=supplier_var, values=list(supplier_dict.keys()), width=40, state='readonly')
        supplier_combo.grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="Delivery Date (YYYY-MM-DD):").grid(row=1, column=0, padx=10, pady=10, sticky='w')
        delivery_entry = ttk.Entry(dialog, width=42)
        delivery_entry.grid(row=1, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="Item:").grid(row=2, column=0, padx=10, pady=10, sticky='w')
        
        self.db.execute("SELECT item_id, name, unit_price FROM Items")
        items = self.db.fetchall()
        item_dict = {f"{i[1]} (${i[2]})": (i[0], i[2]) for i in items}
        
        item_var = tk.StringVar()
        item_combo = ttk.Combobox(dialog, textvariable=item_var, values=list(item_dict.keys()), width=40, state='readonly')
        item_combo.grid(row=2, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="Quantity:").grid(row=3, column=0, padx=10, pady=10, sticky='w')
        qty_entry = ttk.Entry(dialog, width=42)
        qty_entry.grid(row=3, column=1, padx=10, pady=10)
        
        def save():
            try:
                if not supplier_var.get() or not item_var.get():
                    messagebox.showerror("Error", "Select supplier and item")
                    return
                
                supplier_id = supplier_dict[supplier_var.get()]
                item_id, unit_price = item_dict[item_var.get()]
                quantity = int(qty_entry.get())
                subtotal = unit_price * quantity
                
                self.db.execute(
                    "INSERT INTO Purchase_Orders (supplier_id, order_date, expected_delivery, status, total_amount) VALUES (?, ?, ?, ?, ?)",
                    (supplier_id, datetime.now().date(), delivery_entry.get(), "Pending", subtotal)
                )
                po_number = self.db.lastrowid()
                
                self.db.execute(
                    "INSERT INTO Purchase_Order_Items (po_number, item_id, quantity, unit_price, subtotal) VALUES (?, ?, ?, ?, ?)",
                    (po_number, item_id, quantity, unit_price, subtotal)
                )
                
                self.db.commit()
                messagebox.showinfo("Success", f"PO #{po_number} created!")
                dialog.destroy()
                self.refresh_purchase_orders()
            except Exception as e:
                messagebox.showerror("Error", f"Failed: {str(e)}")
        
        ttk.Button(dialog, text="Create PO", command=save).grid(row=4, column=0, columnspan=2, pady=20)
    
    def view_po_details(self):
        """View PO details"""
        selected = self.po_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a PO")
            return
        
        po_number = self.po_tree.item(selected[0])['values'][0]
        
        dialog = tk.Toplevel(self.app.root)
        dialog.title(f"PO #{po_number} Details")
        dialog.geometry("700x400")
        dialog.resizable(False, False)
        dialog.transient(self.app.root)
        dialog.grab_set()
        
        self.db.execute('''
            SELECT po.po_number, s.name, po.order_date, po.expected_delivery, po.status, po.total_amount
            FROM Purchase_Orders po
            JOIN Suppliers s ON po.supplier_id = s.supplier_id
            WHERE po.po_number = ?
        ''', (po_number,))
        
        po_info = self.db.fetchone()
        
        info_frame = ttk.LabelFrame(dialog, text="Order Info", padding=10)
        info_frame.pack(fill='x', padx=10, pady=10)
        
        labels = [
            f"PO#: {po_info[0]}",
            f"Supplier: {po_info[1]}",
            f"Order Date: {po_info[2]}",
            f"Delivery: {po_info[3]}",
            f"Status: {po_info[4]}",
            f"Total: ${po_info[5]:.2f}"
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
            SELECT i.name, poi.quantity, poi.unit_price, poi.subtotal
            FROM Purchase_Order_Items poi
            JOIN Items i ON poi.item_id = i.item_id
            WHERE poi.po_number = ?
        ''', (po_number,))
        
        for row in self.db.fetchall():
            tree.insert('', 'end', values=row)
    
    # ==================== SUPPLIERS TAB ====================
    
    def create_suppliers_tab(self):
        """Create suppliers tab"""
        sup_frame = ttk.Frame(self.notebook)
        self.notebook.add(sup_frame, text="🏢 Suppliers")
        
        top_btn_frame = ttk.Frame(sup_frame)
        top_btn_frame.pack(side='top', fill='x', padx=10, pady=8)
        
        ttk.Button(top_btn_frame, text="➕ Add", command=self.add_supplier).pack(side='left', padx=3)
        ttk.Button(top_btn_frame, text="✏️ Edit", command=self.edit_supplier).pack(side='left', padx=3)
        ttk.Button(top_btn_frame, text="🗑️ Delete", command=self.delete_supplier).pack(side='left', padx=3)
        ttk.Button(top_btn_frame, text="🔄 Refresh", command=self.refresh_suppliers).pack(side='right', padx=3)
        
        columns = ("ID", "Name", "Contact", "Phone", "Email", "Terms")
        self.sup_tree = ttk.Treeview(sup_frame, columns=columns, show='headings', height=25)
        
        for col in columns:
            self.sup_tree.heading(col, text=col)
            self.sup_tree.column(col, width=150)
        
        self.sup_tree.pack(side='left', fill='both', expand=True, padx=10, pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(sup_frame, orient='vertical', command=self.sup_tree.yview)
        scrollbar.pack(side='right', fill='y', pady=(0, 10), padx=(0, 10))
        self.sup_tree.configure(yscrollcommand=scrollbar.set)
        
        self.refresh_suppliers()
    
    def refresh_suppliers(self):
        """Refresh suppliers"""
        for item in self.sup_tree.get_children():
            self.sup_tree.delete(item)
        
        self.db.execute("SELECT supplier_id, name, contact_person, phone, email, payment_terms FROM Suppliers")
        
        for row in self.db.fetchall():
            self.sup_tree.insert('', 'end', values=row)
    
    def add_supplier(self):
        """Add supplier"""
        dialog = tk.Toplevel(self.app.root)
        dialog.title("Add Supplier")
        dialog.geometry("450x350")
        dialog.resizable(False, False)
        dialog.transient(self.app.root)
        dialog.grab_set()
        
        fields = ["Name:", "Contact Person:", "Phone:", "Email:", "Address:", "Payment Terms:"]
        entries = []
        
        for i, field in enumerate(fields):
            ttk.Label(dialog, text=field).grid(row=i, column=0, padx=10, pady=8, sticky='w')
            entry = ttk.Entry(dialog, width=30)
            entry.grid(row=i, column=1, padx=10, pady=8)
            entries.append(entry)
        
        def save():
            try:
                self.db.execute(
                    "INSERT INTO Suppliers (name, contact_person, phone, email, address, payment_terms) VALUES (?, ?, ?, ?, ?, ?)",
                    tuple(e.get() for e in entries)
                )
                self.db.commit()
                messagebox.showinfo("Success", "Supplier added!")
                dialog.destroy()
                self.refresh_suppliers()
            except Exception as e:
                messagebox.showerror("Error", f"Failed: {str(e)}")
        
        ttk.Button(dialog, text="Save", command=save).grid(row=len(fields), column=0, columnspan=2, pady=15)
    
    def edit_supplier(self):
        """Edit supplier"""
        selected = self.sup_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a supplier")
            return
        
        values = self.sup_tree.item(selected[0])['values']
        supplier_id = values[0]
        
        self.db.execute("SELECT name, contact_person, phone, email, address, payment_terms FROM Suppliers WHERE supplier_id = ?", (supplier_id,))
        data = self.db.fetchone()
        
        dialog = tk.Toplevel(self.app.root)
        dialog.title("Edit Supplier")
        dialog.geometry("450x350")
        dialog.resizable(False, False)
        dialog.transient(self.app.root)
        dialog.grab_set()
        
        fields = ["Name:", "Contact:", "Phone:", "Email:", "Address:", "Terms:"]
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
                    "UPDATE Suppliers SET name=?, contact_person=?, phone=?, email=?, address=?, payment_terms=? WHERE supplier_id=?",
                    tuple(e.get() for e in entries) + (supplier_id,)
                )
                self.db.commit()
                messagebox.showinfo("Success", "Updated!")
                dialog.destroy()
                self.refresh_suppliers()
            except Exception as e:
                messagebox.showerror("Error", f"Failed: {str(e)}")
        
        ttk.Button(dialog, text="Update", command=update).grid(row=len(fields), column=0, columnspan=2, pady=15)
    
    def delete_supplier(self):
        """Delete supplier"""
        selected = self.sup_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a supplier")
            return
        
        values = self.sup_tree.item(selected[0])['values']
        supplier_id, name = values[0], values[1]
        
        # Check if supplier has POs
        self.db.execute("SELECT COUNT(*) FROM Purchase_Orders WHERE supplier_id = ?", (supplier_id,))
        if self.db.fetchone()[0] > 0:
            messagebox.showwarning("Warning", f"Cannot delete '{name}' - has purchase orders")
            return
        
        if messagebox.askyesno("Confirm", f"Delete supplier '{name}'?"):
            try:
                self.db.execute("DELETE FROM Suppliers WHERE supplier_id = ?", (supplier_id,))
                self.db.commit()
                messagebox.showinfo("Success", "Supplier deleted!")
                self.refresh_suppliers()
            except Exception as e:
                messagebox.showerror("Error", f"Failed: {str(e)}")
    
    # ==================== GOODS RECEIPT TAB ====================
    
    def create_goods_receipt_tab(self):
        """Create goods receipt tab"""
        gr_frame = ttk.Frame(self.notebook)
        self.notebook.add(gr_frame, text="📥 Goods Receipt")
        
        top_frame = ttk.Frame(gr_frame)
        top_frame.pack(side='top', fill='x', padx=10, pady=10)
        
        ttk.Label(top_frame, text="Record Goods Receipt", font=('Arial', 14, 'bold')).pack(pady=10)
        ttk.Button(top_frame, text="➕ New Receipt", command=self.new_goods_receipt).pack(pady=5)
        
        history_frame = ttk.LabelFrame(gr_frame, text="Receipt History", padding=10)
        history_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        columns = ("ID", "PO#", "Supplier", "Item", "Invoice", "Received", "Accepted", "Rejected", "Date")
        self.receipt_tree = ttk.Treeview(history_frame, columns=columns, show='headings', height=20)
        
        widths = [50, 60, 120, 120, 100, 80, 80, 80, 100]
        for i, col in enumerate(columns):
            self.receipt_tree.heading(col, text=col)
            self.receipt_tree.column(col, width=widths[i])
        
        self.receipt_tree.pack(side='left', fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(history_frame, orient='vertical', command=self.receipt_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.receipt_tree.configure(yscrollcommand=scrollbar.set)
        
        self.refresh_receipt_history()
    
    def refresh_receipt_history(self):
        """Refresh goods receipt history"""
        for item in self.receipt_tree.get_children():
            self.receipt_tree.delete(item)
        
        self.db.execute('''
            SELECT gr.receipt_id, gr.po_number, s.name, i.name, gr.invoice_number,
                   gr.received_quantity, gr.accepted_quantity, gr.rejected_quantity, gr.receipt_date
            FROM Goods_Receipt gr
            JOIN Suppliers s ON gr.supplier_id = s.supplier_id
            JOIN Items i ON gr.item_id = i.item_id
            ORDER BY gr.receipt_id DESC
        ''')
        
        for row in self.db.fetchall():
            self.receipt_tree.insert('', 'end', values=row)
    
    def new_goods_receipt(self):
        """Create new goods receipt"""
        self.db.execute("SELECT COUNT(*) FROM Suppliers")
        if self.db.fetchone()[0] == 0:
            messagebox.showwarning("Warning", "Add suppliers first")
            return
        
        dialog = tk.Toplevel(self.app.root)
        dialog.title("New Goods Receipt")
        dialog.geometry("550x600")
        dialog.resizable(False, False)
        dialog.transient(self.app.root)
        dialog.grab_set()
        
        # Step 1: Supplier
        ttk.Label(dialog, text="Step 1: Select Supplier", font=('Arial', 11, 'bold')).grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky='w')
        
        ttk.Label(dialog, text="Supplier:").grid(row=1, column=0, padx=10, pady=8, sticky='w')
        
        self.db.execute("SELECT supplier_id, name FROM Suppliers ORDER BY name")
        suppliers = self.db.fetchall()
        supplier_dict = {f"{s[1]} (ID: {s[0]})": s[0] for s in suppliers}
        
        supplier_var = tk.StringVar()
        supplier_combo = ttk.Combobox(dialog)
