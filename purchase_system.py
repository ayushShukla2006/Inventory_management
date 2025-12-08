import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class PurchaseInventorySystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Purchase Department - Inventory Management System")
        self.root.geometry("1200x700")
        
        # Initialize database
        self.init_database()
        
        # Create UI
        self.create_widgets()
        
    def init_database(self):
        """Initialize SQLite database with all required tables"""
        self.conn = sqlite3.connect('purchase_inventory.db')
        self.cursor = self.conn.cursor()
        
        # Create Suppliers table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Suppliers (
                supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                contact_person TEXT,
                phone TEXT,
                email TEXT,
                address TEXT,
                payment_terms TEXT
            )
        ''')
        
        # Create Items table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Items (
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                category TEXT,
                unit_of_measure TEXT,
                unit_price REAL
            )
        ''')
        
        # Create Inventory table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Inventory (
                item_id INTEGER PRIMARY KEY,
                quantity_on_hand INTEGER DEFAULT 0,
                reorder_level INTEGER DEFAULT 10,
                location TEXT,
                last_updated TIMESTAMP,
                FOREIGN KEY (item_id) REFERENCES Items(item_id)
            )
        ''')
        
        # Create Purchase_Orders table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Purchase_Orders (
                po_number INTEGER PRIMARY KEY AUTOINCREMENT,
                supplier_id INTEGER,
                order_date DATE,
                expected_delivery DATE,
                status TEXT DEFAULT 'Pending',
                total_amount REAL,
                FOREIGN KEY (supplier_id) REFERENCES Suppliers(supplier_id)
            )
        ''')
        
        # Create Purchase_Order_Items table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Purchase_Order_Items (
                po_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                po_number INTEGER,
                item_id INTEGER,
                quantity INTEGER,
                unit_price REAL,
                subtotal REAL,
                FOREIGN KEY (po_number) REFERENCES Purchase_Orders(po_number),
                FOREIGN KEY (item_id) REFERENCES Items(item_id)
            )
        ''')
        
        # Create Enhanced Goods_Receipt table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Goods_Receipt (
                receipt_id INTEGER PRIMARY KEY AUTOINCREMENT,
                po_number INTEGER,
                item_id INTEGER,
                supplier_id INTEGER,
                invoice_number TEXT,
                received_quantity INTEGER,
                accepted_quantity INTEGER,
                rejected_quantity INTEGER,
                receipt_date DATE,
                notes TEXT,
                FOREIGN KEY (po_number) REFERENCES Purchase_Orders(po_number),
                FOREIGN KEY (item_id) REFERENCES Items(item_id),
                FOREIGN KEY (supplier_id) REFERENCES Suppliers(supplier_id)
            )
        ''')
        
        self.conn.commit()
        
    def create_widgets(self):
        """Create the main UI components"""
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_inventory_tab()
        self.create_purchase_order_tab()
        self.create_suppliers_tab()
        self.create_goods_receipt_tab()
        self.create_alerts_tab()
        
    def create_inventory_tab(self):
        """Create inventory management tab"""
        inv_frame = ttk.Frame(self.notebook)
        self.notebook.add(inv_frame, text="Inventory")
        
        # Top button frame
        top_btn_frame = ttk.Frame(inv_frame)
        top_btn_frame.pack(side='top', fill='x', padx=10, pady=8)
        
        ttk.Button(top_btn_frame, text="➕ Add New Item", command=self.add_new_item).pack(side='left', padx=3)
        ttk.Button(top_btn_frame, text="✏️ Edit Item", command=self.edit_item).pack(side='left', padx=3)
        ttk.Button(top_btn_frame, text="📉 Reduce Stock", command=self.reduce_stock).pack(side='left', padx=3)
        ttk.Button(top_btn_frame, text="🗑️ Delete Item", command=self.delete_item).pack(side='left', padx=3)
        ttk.Button(top_btn_frame, text="🔄 Refresh", command=self.refresh_inventory).pack(side='right', padx=3)
        
        # Treeview for inventory
        columns = ("ID", "Item Name", "Category", "Quantity", "Reorder Level", "Location", "Status")
        self.inv_tree = ttk.Treeview(inv_frame, columns=columns, show='headings', height=25)
        
        for col in columns:
            self.inv_tree.heading(col, text=col)
            self.inv_tree.column(col, width=120)
        
        self.inv_tree.pack(side='left', fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(inv_frame, orient='vertical', command=self.inv_tree.yview)
        scrollbar.pack(side='right', fill='y', pady=(0, 10), padx=(0, 10))
        self.inv_tree.configure(yscrollcommand=scrollbar.set)
        
        self.refresh_inventory()
    
    def refresh_inventory(self):
        """Refresh inventory display"""
        for item in self.inv_tree.get_children():
            self.inv_tree.delete(item)
        
        self.cursor.execute('''
            SELECT i.item_id, i.name, i.category, inv.quantity_on_hand, 
                   inv.reorder_level, inv.location
            FROM Items i
            JOIN Inventory inv ON i.item_id = inv.item_id
            ORDER BY i.name
        ''')
        
        for row in self.cursor.fetchall():
            status = "LOW STOCK" if row[3] <= row[4] else "OK"
            tag = 'low' if status == "LOW STOCK" else ''
            self.inv_tree.insert('', 'end', values=row + (status,), tags=(tag,))
        
        self.inv_tree.tag_configure('low', background='#ffcccc')
    
    def add_new_item(self):
        """Add new item dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Item")
        dialog.geometry("450x400")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Item Name:").grid(row=0, column=0, padx=10, pady=8, sticky='w')
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.grid(row=0, column=1, padx=10, pady=8)
        
        ttk.Label(dialog, text="Description:").grid(row=1, column=0, padx=10, pady=8, sticky='w')
        desc_entry = ttk.Entry(dialog, width=30)
        desc_entry.grid(row=1, column=1, padx=10, pady=8)
        
        ttk.Label(dialog, text="Category:").grid(row=2, column=0, padx=10, pady=8, sticky='w')
        cat_entry = ttk.Entry(dialog, width=30)
        cat_entry.grid(row=2, column=1, padx=10, pady=8)
        
        ttk.Label(dialog, text="Unit of Measure:").grid(row=3, column=0, padx=10, pady=8, sticky='w')
        uom_entry = ttk.Entry(dialog, width=30)
        uom_entry.grid(row=3, column=1, padx=10, pady=8)
        
        ttk.Label(dialog, text="Unit Price:").grid(row=4, column=0, padx=10, pady=8, sticky='w')
        price_entry = ttk.Entry(dialog, width=30)
        price_entry.grid(row=4, column=1, padx=10, pady=8)
        
        ttk.Label(dialog, text="Initial Quantity:").grid(row=5, column=0, padx=10, pady=8, sticky='w')
        qty_entry = ttk.Entry(dialog, width=30)
        qty_entry.grid(row=5, column=1, padx=10, pady=8)
        
        ttk.Label(dialog, text="Reorder Level:").grid(row=6, column=0, padx=10, pady=8, sticky='w')
        reorder_entry = ttk.Entry(dialog, width=30)
        reorder_entry.grid(row=6, column=1, padx=10, pady=8)
        
        ttk.Label(dialog, text="Location:").grid(row=7, column=0, padx=10, pady=8, sticky='w')
        loc_entry = ttk.Entry(dialog, width=30)
        loc_entry.grid(row=7, column=1, padx=10, pady=8)
        
        def save_item():
            try:
                self.cursor.execute(
                    "INSERT INTO Items (name, description, category, unit_of_measure, unit_price) VALUES (?, ?, ?, ?, ?)",
                    (name_entry.get(), desc_entry.get(), cat_entry.get(), uom_entry.get(), float(price_entry.get()))
                )
                item_id = self.cursor.lastrowid
                
                self.cursor.execute(
                    "INSERT INTO Inventory (item_id, quantity_on_hand, reorder_level, location, last_updated) VALUES (?, ?, ?, ?, ?)",
                    (item_id, int(qty_entry.get()), int(reorder_entry.get()), loc_entry.get(), datetime.now())
                )
                
                self.conn.commit()
                messagebox.showinfo("Success", "Item added successfully!")
                dialog.destroy()
                self.refresh_inventory()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add item: {str(e)}")
        
        ttk.Button(dialog, text="Save", command=save_item).grid(row=8, column=0, columnspan=2, pady=15)
    
    def edit_item(self):
        """Edit selected item"""
        selected = self.inv_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item to edit")
            return
        
        item_values = self.inv_tree.item(selected[0])['values']
        item_id = item_values[0]
        
        # Fetch full item details
        self.cursor.execute('''
            SELECT i.name, i.description, i.category, i.unit_of_measure, i.unit_price,
                   inv.quantity_on_hand, inv.reorder_level, inv.location
            FROM Items i
            JOIN Inventory inv ON i.item_id = inv.item_id
            WHERE i.item_id = ?
        ''', (item_id,))
        
        item_data = self.cursor.fetchone()
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Item")
        dialog.geometry("450x400")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Item Name:").grid(row=0, column=0, padx=10, pady=8, sticky='w')
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.insert(0, item_data[0])
        name_entry.grid(row=0, column=1, padx=10, pady=8)
        
        ttk.Label(dialog, text="Description:").grid(row=1, column=0, padx=10, pady=8, sticky='w')
        desc_entry = ttk.Entry(dialog, width=30)
        desc_entry.insert(0, item_data[1] if item_data[1] else "")
        desc_entry.grid(row=1, column=1, padx=10, pady=8)
        
        ttk.Label(dialog, text="Category:").grid(row=2, column=0, padx=10, pady=8, sticky='w')
        cat_entry = ttk.Entry(dialog, width=30)
        cat_entry.insert(0, item_data[2] if item_data[2] else "")
        cat_entry.grid(row=2, column=1, padx=10, pady=8)
        
        ttk.Label(dialog, text="Unit of Measure:").grid(row=3, column=0, padx=10, pady=8, sticky='w')
        uom_entry = ttk.Entry(dialog, width=30)
        uom_entry.insert(0, item_data[3] if item_data[3] else "")
        uom_entry.grid(row=3, column=1, padx=10, pady=8)
        
        ttk.Label(dialog, text="Unit Price:").grid(row=4, column=0, padx=10, pady=8, sticky='w')
        price_entry = ttk.Entry(dialog, width=30)
        price_entry.insert(0, item_data[4])
        price_entry.grid(row=4, column=1, padx=10, pady=8)
        
        ttk.Label(dialog, text="Current Quantity:").grid(row=5, column=0, padx=10, pady=8, sticky='w')
        qty_entry = ttk.Entry(dialog, width=30)
        qty_entry.insert(0, item_data[5])
        qty_entry.grid(row=5, column=1, padx=10, pady=8)
        
        ttk.Label(dialog, text="Reorder Level:").grid(row=6, column=0, padx=10, pady=8, sticky='w')
        reorder_entry = ttk.Entry(dialog, width=30)
        reorder_entry.insert(0, item_data[6])
        reorder_entry.grid(row=6, column=1, padx=10, pady=8)
        
        ttk.Label(dialog, text="Location:").grid(row=7, column=0, padx=10, pady=8, sticky='w')
        loc_entry = ttk.Entry(dialog, width=30)
        loc_entry.insert(0, item_data[7] if item_data[7] else "")
        loc_entry.grid(row=7, column=1, padx=10, pady=8)
        
        def update_item():
            try:
                self.cursor.execute(
                    "UPDATE Items SET name=?, description=?, category=?, unit_of_measure=?, unit_price=? WHERE item_id=?",
                    (name_entry.get(), desc_entry.get(), cat_entry.get(), uom_entry.get(), float(price_entry.get()), item_id)
                )
                
                self.cursor.execute(
                    "UPDATE Inventory SET quantity_on_hand=?, reorder_level=?, location=?, last_updated=? WHERE item_id=?",
                    (int(qty_entry.get()), int(reorder_entry.get()), loc_entry.get(), datetime.now(), item_id)
                )
                
                self.conn.commit()
                messagebox.showinfo("Success", "Item updated successfully!")
                dialog.destroy()
                self.refresh_inventory()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update item: {str(e)}")
        
        ttk.Button(dialog, text="Update", command=update_item).grid(row=8, column=0, columnspan=2, pady=15)
    
    def reduce_stock(self):
        """Reduce stock for selected item"""
        selected = self.inv_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item to reduce stock")
            return
        
        item_values = self.inv_tree.item(selected[0])['values']
        item_id = item_values[0]
        item_name = item_values[1]
        current_qty = item_values[3]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Reduce Stock")
        dialog.geometry("400x250")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text=f"Item: {item_name}", font=('Arial', 10, 'bold')).pack(pady=10)
        ttk.Label(dialog, text=f"Current Stock: {current_qty}").pack(pady=5)
        
        ttk.Label(dialog, text="Quantity to Reduce:").pack(pady=5)
        qty_entry = ttk.Entry(dialog, width=20)
        qty_entry.pack(pady=5)
        
        ttk.Label(dialog, text="Reason:").pack(pady=5)
        reason_entry = ttk.Entry(dialog, width=30)
        reason_entry.pack(pady=5)
        
        def reduce():
            try:
                reduce_qty = int(qty_entry.get())
                if reduce_qty <= 0:
                    messagebox.showerror("Error", "Quantity must be positive")
                    return
                if reduce_qty > current_qty:
                    messagebox.showerror("Error", "Cannot reduce more than current stock")
                    return
                
                self.cursor.execute(
                    "UPDATE Inventory SET quantity_on_hand = quantity_on_hand - ?, last_updated = ? WHERE item_id = ?",
                    (reduce_qty, datetime.now(), item_id)
                )
                
                self.conn.commit()
                messagebox.showinfo("Success", f"Reduced {reduce_qty} units from stock")
                dialog.destroy()
                self.refresh_inventory()
                self.refresh_alerts()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reduce stock: {str(e)}")
        
        ttk.Button(dialog, text="Reduce Stock", command=reduce).pack(pady=10)
    
    def delete_item(self):
        """Delete selected item"""
        selected = self.inv_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item to delete")
            return
        
        item_values = self.inv_tree.item(selected[0])['values']
        item_id = item_values[0]
        item_name = item_values[1]
        
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{item_name}'?\n\nThis will also delete all related inventory records.")
        
        if confirm:
            try:
                self.cursor.execute("DELETE FROM Inventory WHERE item_id = ?", (item_id,))
                self.cursor.execute("DELETE FROM Items WHERE item_id = ?", (item_id,))
                self.conn.commit()
                messagebox.showinfo("Success", "Item deleted successfully!")
                self.refresh_inventory()
                self.refresh_alerts()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete item: {str(e)}")
    
    def create_purchase_order_tab(self):
        """Create purchase order tab"""
        po_frame = ttk.Frame(self.notebook)
        self.notebook.add(po_frame, text="Purchase Orders")
        
        # Top button frame
        top_btn_frame = ttk.Frame(po_frame)
        top_btn_frame.pack(side='top', fill='x', padx=10, pady=8)
        
        ttk.Button(top_btn_frame, text="➕ Create New PO", command=self.create_purchase_order).pack(side='left', padx=3)
        ttk.Button(top_btn_frame, text="👁️ View PO Details", command=self.view_po_details).pack(side='left', padx=3)
        ttk.Button(top_btn_frame, text="🔄 Refresh", command=self.refresh_purchase_orders).pack(side='right', padx=3)
        
        # Treeview for POs
        columns = ("PO#", "Supplier", "Order Date", "Expected Delivery", "Status", "Total Amount")
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
        """Refresh purchase orders display"""
        for item in self.po_tree.get_children():
            self.po_tree.delete(item)
        
        self.cursor.execute('''
            SELECT po.po_number, s.name, po.order_date, po.expected_delivery, 
                   po.status, po.total_amount
            FROM Purchase_Orders po
            JOIN Suppliers s ON po.supplier_id = s.supplier_id
            ORDER BY po.po_number DESC
        ''')
        
        for row in self.cursor.fetchall():
            self.po_tree.insert('', 'end', values=row)
    
    def view_po_details(self):
        """View purchase order details"""
        selected = self.po_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a purchase order to view")
            return
        
        po_values = self.po_tree.item(selected[0])['values']
        po_number = po_values[0]
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Purchase Order #{po_number} Details")
        dialog.geometry("750x450")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # PO Header Info
        header_frame = ttk.LabelFrame(dialog, text="Order Information", padding=10)
        header_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(header_frame, text=f"PO Number: {po_values[0]}").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        ttk.Label(header_frame, text=f"Supplier: {po_values[1]}").grid(row=0, column=1, sticky='w', padx=5, pady=2)
        ttk.Label(header_frame, text=f"Order Date: {po_values[2]}").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        ttk.Label(header_frame, text=f"Expected Delivery: {po_values[3]}").grid(row=1, column=1, sticky='w', padx=5, pady=2)
        ttk.Label(header_frame, text=f"Status: {po_values[4]}").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        ttk.Label(header_frame, text=f"Total Amount: ${po_values[5]:.2f}").grid(row=2, column=1, sticky='w', padx=5, pady=2)
        
        # Line Items
        items_frame = ttk.LabelFrame(dialog, text="Order Items", padding=10)
        items_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        columns = ("Item ID", "Item Name", "Quantity", "Unit Price", "Subtotal")
        items_tree = ttk.Treeview(items_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            items_tree.heading(col, text=col)
            items_tree.column(col, width=120)
        
        items_tree.pack(fill='both', expand=True)
        
        self.cursor.execute('''
            SELECT poi.item_id, i.name, poi.quantity, poi.unit_price, poi.subtotal
            FROM Purchase_Order_Items poi
            JOIN Items i ON poi.item_id = i.item_id
            WHERE poi.po_number = ?
        ''', (po_number,))
        
        for row in self.cursor.fetchall():
            items_tree.insert('', 'end', values=row)
    
    def create_purchase_order(self):
        """Create new purchase order dialog"""
        # Check if there are suppliers
        self.cursor.execute("SELECT COUNT(*) FROM Suppliers")
        if self.cursor.fetchone()[0] == 0:
            messagebox.showwarning("Warning", "Please add suppliers first before creating purchase orders")
            return
        
        # Check if there are items
        self.cursor.execute("SELECT COUNT(*) FROM Items")
        if self.cursor.fetchone()[0] == 0:
            messagebox.showwarning("Warning", "Please add items first before creating purchase orders")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Create Purchase Order")
        dialog.geometry("600x350")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Select Supplier:").grid(row=0, column=0, padx=10, pady=10, sticky='w')
        
        self.cursor.execute("SELECT supplier_id, name FROM Suppliers")
        suppliers = self.cursor.fetchall()
        supplier_dict = {f"{s[1]} (ID: {s[0]})": s[0] for s in suppliers}
        
        supplier_var = tk.StringVar()
        supplier_combo = ttk.Combobox(dialog, textvariable=supplier_var, values=list(supplier_dict.keys()), width=40)
        supplier_combo.grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="Expected Delivery (YYYY-MM-DD):").grid(row=1, column=0, padx=10, pady=10, sticky='w')
        delivery_entry = ttk.Entry(dialog, width=42)
        delivery_entry.grid(row=1, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="Select Item:").grid(row=2, column=0, padx=10, pady=10, sticky='w')
        
        self.cursor.execute("SELECT item_id, name, unit_price FROM Items")
        items = self.cursor.fetchall()
        item_dict = {f"{i[1]} (${i[2]})": (i[0], i[2]) for i in items}
        
        item_var = tk.StringVar()
        item_combo = ttk.Combobox(dialog, textvariable=item_var, values=list(item_dict.keys()), width=40)
        item_combo.grid(row=2, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="Quantity:").grid(row=3, column=0, padx=10, pady=10, sticky='w')
        qty_entry = ttk.Entry(dialog, width=42)
        qty_entry.grid(row=3, column=1, padx=10, pady=10)
        
        def save_po():
            try:
                if not supplier_var.get():
                    messagebox.showerror("Error", "Please select a supplier")
                    return
                if not item_var.get():
                    messagebox.showerror("Error", "Please select an item")
                    return
                
                supplier_id = supplier_dict[supplier_var.get()]
                item_id, unit_price = item_dict[item_var.get()]
                quantity = int(qty_entry.get())
                subtotal = unit_price * quantity
                
                self.cursor.execute(
                    "INSERT INTO Purchase_Orders (supplier_id, order_date, expected_delivery, status, total_amount) VALUES (?, ?, ?, ?, ?)",
                    (supplier_id, datetime.now().date(), delivery_entry.get(), "Pending", subtotal)
                )
                po_number = self.cursor.lastrowid
                
                self.cursor.execute(
                    "INSERT INTO Purchase_Order_Items (po_number, item_id, quantity, unit_price, subtotal) VALUES (?, ?, ?, ?, ?)",
                    (po_number, item_id, quantity, unit_price, subtotal)
                )
                
                self.conn.commit()
                messagebox.showinfo("Success", f"Purchase Order #{po_number} created successfully!")
                dialog.destroy()
                self.refresh_purchase_orders()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create PO: {str(e)}")
        
        ttk.Button(dialog, text="Create PO", command=save_po).grid(row=4, column=0, columnspan=2, pady=20)
    
    def create_suppliers_tab(self):
        """Create suppliers management tab"""
        sup_frame = ttk.Frame(self.notebook)
        self.notebook.add(sup_frame, text="Suppliers")
        
        # Top button frame
        top_btn_frame = ttk.Frame(sup_frame)
        top_btn_frame.pack(side='top', fill='x', padx=10, pady=8)
        
        ttk.Button(top_btn_frame, text="➕ Add New Supplier", command=self.add_new_supplier).pack(side='left', padx=3)
        ttk.Button(top_btn_frame, text="✏️ Edit Supplier", command=self.edit_supplier).pack(side='left', padx=3)
        ttk.Button(top_btn_frame, text="🗑️ Delete Supplier", command=self.delete_supplier).pack(side='left', padx=3)
        ttk.Button(top_btn_frame, text="🔄 Refresh", command=self.refresh_suppliers).pack(side='right', padx=3)
        
        columns = ("ID", "Name", "Contact", "Phone", "Email", "Payment Terms")
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
        """Refresh suppliers display"""
        for item in self.sup_tree.get_children():
            self.sup_tree.delete(item)
        
        self.cursor.execute("SELECT supplier_id, name, contact_person, phone, email, payment_terms FROM Suppliers")
        
        for row in self.cursor.fetchall():
            self.sup_tree.insert('', 'end', values=row)
    
    def add_new_supplier(self):
        """Add new supplier dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Supplier")
        dialog.geometry("450x350")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Supplier Name:").grid(row=0, column=0, padx=10, pady=8, sticky='w')
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.grid(row=0, column=1, padx=10, pady=8)
        
        ttk.Label(dialog, text="Contact Person:").grid(row=1, column=0, padx=10, pady=8, sticky='w')
        contact_entry = ttk.Entry(dialog, width=30)
        contact_entry.grid(row=1, column=1, padx=10, pady=8)
        
        ttk.Label(dialog, text="Phone:").grid(row=2, column=0, padx=10, pady=8, sticky='w')
        phone_entry = ttk.Entry(dialog, width=30)
        phone_entry.grid(row=2, column=1, padx=10, pady=8)
        
        ttk.Label(dialog, text="Email:").grid(row=3, column=0, padx=10, pady=8, sticky='w')
        email_entry = ttk.Entry(dialog, width=30)
        email_entry.grid(row=3, column=1, padx=10, pady=8)
        
        ttk.Label(dialog, text="Address:").grid(row=4, column=0, padx=10, pady=8, sticky='w')
        address_entry = ttk.Entry(dialog, width=30)
        address_entry.grid(row=4, column=1, padx=10, pady=8)
        
        ttk.Label(dialog, text="Payment Terms:").grid(row=5, column=0, padx=10, pady=8, sticky='w')
        terms_entry = ttk.Entry(dialog, width=30)
        terms_entry.grid(row=5, column=1, padx=10, pady=8)
        
        def save_supplier():
            try:
                self.cursor.execute(
                    "INSERT INTO Suppliers (name, contact_person, phone, email, address, payment_terms) VALUES (?, ?, ?, ?, ?, ?)",
                    (name_entry.get(), contact_entry.get(), phone_entry.get(), email_entry.get(), address_entry.get(), terms_entry.get())
                )
                self.conn.commit()
                messagebox.showinfo("Success", "Supplier added successfully!")
                dialog.destroy()
                self.refresh_suppliers()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add supplier: {str(e)}")
        
        ttk.Button(dialog, text="Save", command=save_supplier).grid(row=6, column=0, columnspan=2, pady=15)
    
    def edit_supplier(self):
        """Edit selected supplier"""
        selected = self.sup_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a supplier to edit")
            return
        
        sup_values = self.sup_tree.item(selected[0])['values']
        supplier_id = sup_values[0]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Supplier")
        dialog.geometry("450x350")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Supplier Name:").grid(row=0, column=0, padx=10, pady=8, sticky='w')
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.insert(0, sup_values[1])
        name_entry.grid(row=0, column=1, padx=10, pady=8)
        
        ttk.Label(dialog, text="Contact Person:").grid(row=1, column=0, padx=10, pady=8, sticky='w')
        contact_entry = ttk.Entry(dialog, width=30)
        contact_entry.insert(0, sup_values[2] if sup_values[2] else "")
        contact_entry.grid(row=1, column=1, padx=10, pady=8)
        
        ttk.Label(dialog, text="Phone:").grid(row=2, column=0, padx=10, pady=8, sticky='w')
        phone_entry = ttk.Entry(dialog, width=30)
        phone_entry.insert(0, sup_values[3] if sup_values[3] else "")
        phone_entry.grid(row=2, column=1, padx=10, pady=8)
        
        ttk.Label(dialog, text="Email:").grid(row=3, column=0, padx=10, pady=8, sticky='w')
        email_entry = ttk.Entry(dialog, width=30)
        email_entry.insert(0, sup_values[4] if sup_values[4] else "")
        email_entry.grid(row=3, column=1, padx=10, pady=8)
        
        # Get full address from database
        self.cursor.execute("SELECT address, payment_terms FROM Suppliers WHERE supplier_id = ?", (supplier_id,))
        extra_data = self.cursor.fetchone()
        
        ttk.Label(dialog, text="Address:").grid(row=4, column=0, padx=10, pady=8, sticky='w')
        address_entry = ttk.Entry(dialog, width=30)
        address_entry.insert(0, extra_data[0] if extra_data[0] else "")
        address_entry.grid(row=4, column=1, padx=10, pady=8)
        
        ttk.Label(dialog, text="Payment Terms:").grid(row=5, column=0, padx=10, pady=8, sticky='w')
        terms_entry = ttk.Entry(dialog, width=30)
        terms_entry.insert(0, sup_values[5] if sup_values[5] else "")
        terms_entry.grid(row=5, column=1, padx=10, pady=8)
        
        def update_supplier():
            try:
                self.cursor.execute(
                    "UPDATE Suppliers SET name=?, contact_person=?, phone=?, email=?, address=?, payment_terms=? WHERE supplier_id=?",
                    (name_entry.get(), contact_entry.get(), phone_entry.get(), email_entry.get(), address_entry.get(), terms_entry.get(), supplier_id)
                )
                self.conn.commit()
                messagebox.showinfo("Success", "Supplier updated successfully!")
                dialog.destroy()
                self.refresh_suppliers()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update supplier: {str(e)}")
        
        ttk.Button(dialog, text="Update", command=update_supplier).grid(row=6, column=0, columnspan=2, pady=15)
    
    def delete_supplier(self):
        """Delete selected supplier"""
        selected = self.sup_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a supplier to delete")
            return
        
        sup_values = self.sup_tree.item(selected[0])['values']
        supplier_id = sup_values[0]
        supplier_name = sup_values[1]
        
        # Check if supplier has purchase orders
        self.cursor.execute("SELECT COUNT(*) FROM Purchase_Orders WHERE supplier_id = ?", (supplier_id,))
        po_count = self.cursor.fetchone()[0]
        
        if po_count > 0:
            messagebox.showwarning("Warning", f"Cannot delete supplier '{supplier_name}' because they have {po_count} purchase order(s).")
            return
        
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete supplier '{supplier_name}'?")
        
        if confirm:
            try:
                self.cursor.execute("DELETE FROM Suppliers WHERE supplier_id = ?", (supplier_id,))
                self.conn.commit()
                messagebox.showinfo("Success", "Supplier deleted successfully!")
                self.refresh_suppliers()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete supplier: {str(e)}")
    
    def create_goods_receipt_tab(self):
        """Create enhanced goods receipt tab"""
        gr_frame = ttk.Frame(self.notebook)
        self.notebook.add(gr_frame, text="Goods Receipt")
        
        # Top section
        top_frame = ttk.Frame(gr_frame)
        top_frame.pack(side='top', fill='x', padx=10, pady=10)
        
        ttk.Label(top_frame, text="Record Goods Receipt", font=('Arial', 14, 'bold')).pack(pady=10)
        ttk.Button(top_frame, text="➕ New Goods Receipt", command=self.new_goods_receipt).pack(pady=5)
        
        # Receipt history
        history_frame = ttk.LabelFrame(gr_frame, text="Receipt History", padding=10)
        history_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        columns = ("Receipt ID", "PO#", "Supplier", "Item", "Invoice#", "Received", "Accepted", "Rejected", "Date")
        self.receipt_tree = ttk.Treeview(history_frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            self.receipt_tree.heading(col, text=col)
            self.receipt_tree.column(col, width=100)
        
        self.receipt_tree.pack(side='left', fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(history_frame, orient='vertical', command=self.receipt_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.receipt_tree.configure(yscrollcommand=scrollbar.set)
        
        self.refresh_receipt_history()
    
    def refresh_receipt_history(self):
        """Refresh goods receipt history"""
        for item in self.receipt_tree.get_children():
            self.receipt_tree.delete(item)
        
        self.cursor.execute('''
            SELECT gr.receipt_id, gr.po_number, s.name, i.name, gr.invoice_number,
                   gr.received_quantity, gr.accepted_quantity, gr.rejected_quantity, gr.receipt_date
            FROM Goods_Receipt gr
            JOIN Suppliers s ON gr.supplier_id = s.supplier_id
            JOIN Items i ON gr.item_id = i.item_id
            ORDER BY gr.receipt_id DESC
        ''')
        
        for row in self.cursor.fetchall():
            self.receipt_tree.insert('', 'end', values=row)
    
    def new_goods_receipt(self):
        """Open new goods receipt dialog"""
        # Check if there are suppliers
        self.cursor.execute("SELECT COUNT(*) FROM Suppliers")
        if self.cursor.fetchone()[0] == 0:
            messagebox.showwarning("Warning", "No suppliers found. Please add suppliers first.")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("New Goods Receipt")
        dialog.geometry("550x550")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Step 1: Select Supplier
        ttk.Label(dialog, text="Step 1: Select Supplier", font=('Arial', 11, 'bold')).grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky='w')
        
        ttk.Label(dialog, text="Supplier:").grid(row=1, column=0, padx=10, pady=8, sticky='w')
        
        self.cursor.execute("SELECT supplier_id, name FROM Suppliers ORDER BY name")
        suppliers = self.cursor.fetchall()
        supplier_dict = {f"{s[1]} (ID: {s[0]})": s[0] for s in suppliers}
        
        supplier_var = tk.StringVar()
        supplier_combo = ttk.Combobox(dialog, textvariable=supplier_var, values=list(supplier_dict.keys()), width=40, state='readonly')
        supplier_combo.grid(row=1, column=1, padx=10, pady=8)
        
        # Step 2: PO and Item (initially disabled)
        ttk.Label(dialog, text="Step 2: Select PO & Item", font=('Arial', 11, 'bold')).grid(row=2, column=0, columnspan=2, padx=10, pady=(20, 10), sticky='w')
        
        ttk.Label(dialog, text="Purchase Order:").grid(row=3, column=0, padx=10, pady=8, sticky='w')
        po_var = tk.StringVar()
        po_combo = ttk.Combobox(dialog, textvariable=po_var, width=40, state='disabled')
        po_combo.grid(row=3, column=1, padx=10, pady=8)
        
        ttk.Label(dialog, text="Item:").grid(row=4, column=0, padx=10, pady=8, sticky='w')
        item_var = tk.StringVar()
        item_combo = ttk.Combobox(dialog, textvariable=item_var, width=40, state='disabled')
        item_combo.grid(row=4, column=1, padx=10, pady=8)
        
        # Step 3: Receipt Details (initially disabled)
        ttk.Label(dialog, text="Step 3: Receipt Details", font=('Arial', 11, 'bold')).grid(row=5, column=0, columnspan=2, padx=10, pady=(20, 10), sticky='w')
        
        ttk.Label(dialog, text="Invoice Number:").grid(row=6, column=0, padx=10, pady=8, sticky='w')
        invoice_entry = ttk.Entry(dialog, width=42, state='disabled')
        invoice_entry.grid(row=6, column=1, padx=10, pady=8)
        
        ttk.Label(dialog, text="Receipt Date (YYYY-MM-DD):").grid(row=7, column=0, padx=10, pady=8, sticky='w')
        date_entry = ttk.Entry(dialog, width=42, state='disabled')
        date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        date_entry.grid(row=7, column=1, padx=10, pady=8)
        
        ttk.Label(dialog, text="Received Quantity:").grid(row=8, column=0, padx=10, pady=8, sticky='w')
        recv_qty_entry = ttk.Entry(dialog, width=42, state='disabled')
        recv_qty_entry.grid(row=8, column=1, padx=10, pady=8)
        
        ttk.Label(dialog, text="Accepted Quantity:").grid(row=9, column=0, padx=10, pady=8, sticky='w')
        accept_qty_entry = ttk.Entry(dialog, width=42, state='disabled')
        accept_qty_entry.grid(row=9, column=1, padx=10, pady=8)
        
        ttk.Label(dialog, text="Rejected Quantity:").grid(row=10, column=0, padx=10, pady=8, sticky='w')
        reject_qty_entry = ttk.Entry(dialog, width=42, state='disabled')
        reject_qty_entry.grid(row=10, column=1, padx=10, pady=8)
        
        ttk.Label(dialog, text="Notes:").grid(row=11, column=0, padx=10, pady=8, sticky='w')
        notes_entry = ttk.Entry(dialog, width=42, state='disabled')
        notes_entry.grid(row=11, column=1, padx=10, pady=8)
        
        # Store references
        po_dict = {}
        item_dict = {}
        
        def on_supplier_selected(event):
            """When supplier is selected, enable PO selection"""
            if not supplier_var.get():
                return
            
            supplier_id = supplier_dict[supplier_var.get()]
            
            # Get POs for this supplier
            self.cursor.execute('''
                SELECT po_number, order_date, status 
                FROM Purchase_Orders 
                WHERE supplier_id = ? 
                ORDER BY po_number DESC
            ''', (supplier_id,))
            
            pos = self.cursor.fetchall()
            if not pos:
                messagebox.showinfo("Info", "No purchase orders found for this supplier")
                po_combo['state'] = 'disabled'
                return
            
            po_dict.clear()
            po_list = [f"PO #{po[0]} - {po[1]} ({po[2]})" for po in pos]
            for i, po in enumerate(pos):
                po_dict[po_list[i]] = po[0]
            
            po_combo['values'] = po_list
            po_combo['state'] = 'readonly'
            po_combo.set('')
            item_combo['state'] = 'disabled'
            item_combo.set('')
        
        def on_po_selected(event):
            """When PO is selected, enable item selection"""
            if not po_var.get():
                return
            
            po_number = po_dict[po_var.get()]
            
            # Get items for this PO
            self.cursor.execute('''
                SELECT poi.item_id, i.name, poi.quantity
                FROM Purchase_Order_Items poi
                JOIN Items i ON poi.item_id = i.item_id
                WHERE poi.po_number = ?
            ''', (po_number,))
            
            items = self.cursor.fetchall()
            if not items:
                messagebox.showinfo("Info", "No items found for this purchase order")
                item_combo['state'] = 'disabled'
                return
            
            item_dict.clear()
            item_list = [f"{item[1]} (Qty: {item[2]})" for item in items]
            for i, item in enumerate(items):
                item_dict[item_list[i]] = item[0]
            
            item_combo['values'] = item_list
            item_combo['state'] = 'readonly'
            item_combo.set('')
        
        def on_item_selected(event):
            """When item is selected, enable all receipt detail fields"""
            if item_var.get():
                invoice_entry['state'] = 'normal'
                date_entry['state'] = 'normal'
                recv_qty_entry['state'] = 'normal'
                accept_qty_entry['state'] = 'normal'
                reject_qty_entry['state'] = 'normal'
                notes_entry['state'] = 'normal'
        
        def validate_quantities():
            """Validate received, accepted, and rejected quantities"""
            try:
                recv = int(recv_qty_entry.get())
                accept = int(accept_qty_entry.get())
                reject = int(reject_qty_entry.get())
                
                if recv <= 0:
                    messagebox.showerror("Error", "Received quantity must be positive")
                    return False
                
                if accept < 0 or reject < 0:
                    messagebox.showerror("Error", "Accepted/Rejected quantities cannot be negative")
                    return False
                
                if accept + reject != recv:
                    messagebox.showerror("Error", f"Accepted ({accept}) + Rejected ({reject}) must equal Received ({recv})")
                    return False
                
                return True
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers for quantities")
                return False
        
        def save_receipt():
            """Save the goods receipt"""
            if not supplier_var.get():
                messagebox.showerror("Error", "Please select a supplier")
                return
            if not po_var.get():
                messagebox.showerror("Error", "Please select a purchase order")
                return
            if not item_var.get():
                messagebox.showerror("Error", "Please select an item")
                return
            if not invoice_entry.get():
                messagebox.showerror("Error", "Please enter invoice number")
                return
            
            if not validate_quantities():
                return
            
            try:
                supplier_id = supplier_dict[supplier_var.get()]
                po_number = po_dict[po_var.get()]
                item_id = item_dict[item_var.get()]
                invoice_no = invoice_entry.get()
                receipt_date = date_entry.get()
                recv_qty = int(recv_qty_entry.get())
                accept_qty = int(accept_qty_entry.get())
                reject_qty = int(reject_qty_entry.get())
                notes = notes_entry.get()
                
                # Insert goods receipt
                self.cursor.execute('''
                    INSERT INTO Goods_Receipt 
                    (po_number, item_id, supplier_id, invoice_number, received_quantity, 
                     accepted_quantity, rejected_quantity, receipt_date, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (po_number, item_id, supplier_id, invoice_no, recv_qty, accept_qty, reject_qty, receipt_date, notes))
                
                # Update inventory with ONLY accepted quantity
                self.cursor.execute('''
                    UPDATE Inventory 
                    SET quantity_on_hand = quantity_on_hand + ?, 
                        last_updated = ?
                    WHERE item_id = ?
                ''', (accept_qty, datetime.now(), item_id))
                
                # Check if all items in the PO have been received
                # Get total ordered quantity for this item in this PO
                self.cursor.execute('''
                    SELECT quantity FROM Purchase_Order_Items
                    WHERE po_number = ? AND item_id = ?
                ''', (po_number, item_id))
                ordered_qty = self.cursor.fetchone()[0]
                
                # Get total received quantity for this item in this PO (including current receipt)
                self.cursor.execute('''
                    SELECT SUM(received_quantity) FROM Goods_Receipt
                    WHERE po_number = ? AND item_id = ?
                ''', (po_number, item_id))
                total_received = self.cursor.fetchone()[0] or 0
                
                # Check if all items in PO have been fully received
                self.cursor.execute('''
                    SELECT COUNT(*) FROM Purchase_Order_Items poi
                    WHERE poi.po_number = ?
                    AND poi.quantity > (
                        SELECT COALESCE(SUM(gr.received_quantity), 0)
                        FROM Goods_Receipt gr
                        WHERE gr.po_number = poi.po_number 
                        AND gr.item_id = poi.item_id
                    )
                ''', (po_number,))
                
                unreceived_items = self.cursor.fetchone()[0]
                
                # Update PO status
                if unreceived_items == 0:
                    # All items fully received
                    self.cursor.execute('''
                        UPDATE Purchase_Orders 
                        SET status = 'Completed'
                        WHERE po_number = ?
                    ''', (po_number,))
                else:
                    # Partial receipt
                    self.cursor.execute('''
                        UPDATE Purchase_Orders 
                        SET status = 'Partially Received'
                        WHERE po_number = ?
                    ''', (po_number,))
                
                self.conn.commit()
                
                msg = f"Goods receipt recorded successfully!\n\n"
                msg += f"Received: {recv_qty} units\n"
                msg += f"Accepted: {accept_qty} units (added to inventory)\n"
                msg += f"Rejected: {reject_qty} units (to be returned)"
                
                messagebox.showinfo("Success", msg)
                dialog.destroy()
                self.refresh_receipt_history()
                self.refresh_inventory()
                self.refresh_alerts()
                self.refresh_purchase_orders()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to record receipt: {str(e)}")
        
        # Bind events
        supplier_combo.bind('<<ComboboxSelected>>', on_supplier_selected)
        po_combo.bind('<<ComboboxSelected>>', on_po_selected)
        item_combo.bind('<<ComboboxSelected>>', on_item_selected)
        
        # Save button
        ttk.Button(dialog, text="Save Receipt", command=save_receipt).grid(row=12, column=0, columnspan=2, pady=20)
    
    def create_alerts_tab(self):
        """Create alerts/reports tab"""
        alert_frame = ttk.Frame(self.notebook)
        self.notebook.add(alert_frame, text="Alerts & Reports")
        
        # Top button frame
        top_btn_frame = ttk.Frame(alert_frame)
        top_btn_frame.pack(side='top', fill='x', padx=10, pady=8)
        
        ttk.Label(top_btn_frame, text="⚠️ Low Stock Alerts", font=('Arial', 12, 'bold')).pack(side='left', padx=5)
        ttk.Button(top_btn_frame, text="🔄 Refresh Alerts", command=self.refresh_alerts).pack(side='right', padx=3)
        
        columns = ("Item ID", "Item Name", "Current Stock", "Reorder Level", "Action Needed")
        self.alert_tree = ttk.Treeview(alert_frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            self.alert_tree.heading(col, text=col)
            self.alert_tree.column(col, width=200)
        
        self.alert_tree.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        self.refresh_alerts()
    
    def refresh_alerts(self):
        """Refresh low stock alerts"""
        for item in self.alert_tree.get_children():
            self.alert_tree.delete(item)
        
        self.cursor.execute('''
            SELECT i.item_id, i.name, inv.quantity_on_hand, inv.reorder_level
            FROM Items i
            JOIN Inventory inv ON i.item_id = inv.item_id
            WHERE inv.quantity_on_hand <= inv.reorder_level
            ORDER BY (inv.quantity_on_hand - inv.reorder_level)
        ''')
        
        for row in self.cursor.fetchall():
            action = f"Order {row[3] * 2 - row[2]} units"
            self.alert_tree.insert('', 'end', values=row + (action,))
    
    def __del__(self):
        """Close database connection on exit"""
        if hasattr(self, 'conn'):
            self.conn.close()

# Main application
if __name__ == "__main__":
    root = tk.Tk()
    app = PurchaseInventorySystem(root)
    root.mainloop()
