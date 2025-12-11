"""
Enhanced Purchase Module - Multi-item orders with data integrity (Part 1/2)
Save this as: purchase_module.py
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class PurchaseModule:
    def __init__(self, notebook, db, app):
        self.notebook = notebook
        self.db = db
        self.app = app
        self.create_inventory_tab()
        self.create_purchase_order_tab()
        self.create_suppliers_tab()
        self.create_goods_receipt_tab()
        self.create_alerts_tab()
    
    def refresh_all(self):
        self.refresh_inventory()
        self.refresh_purchase_orders()
        self.refresh_suppliers()
        self.refresh_receipt_history()
        self.refresh_alerts()
    
    def create_inventory_tab(self):
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
        for item in self.inv_tree.get_children():
            self.inv_tree.delete(item)
        self.db.execute('''SELECT i.item_id, i.name, i.category, inv.quantity_on_hand, 
            inv.reorder_level, i.unit_price, i.selling_price, inv.location
            FROM Items i JOIN Inventory inv ON i.item_id = inv.item_id ORDER BY i.name''')
        for row in self.db.fetchall():
            status = "LOW" if row[3] <= row[4] else "OK"
            tag = 'low' if status == "LOW" else ''
            self.inv_tree.insert('', 'end', values=row + (status,), tags=(tag,))
        self.inv_tree.tag_configure('low', background='#ffcccc')
    
    def validate_item_data(self, name, price, sell_price, qty, reorder):
        if not name or not name.strip():
            raise ValueError("Item name cannot be empty")
        try:
            price_val = float(price)
            if price_val < 0:
                raise ValueError("Purchase price cannot be negative")
        except (ValueError, TypeError):
            raise ValueError("Invalid purchase price")
        try:
            sell_val = float(sell_price)
            if sell_val < 0:
                raise ValueError("Selling price cannot be negative")
        except (ValueError, TypeError):
            raise ValueError("Invalid selling price")
        try:
            qty_val = int(qty)
            if qty_val < 0:
                raise ValueError("Quantity cannot be negative")
        except (ValueError, TypeError):
            raise ValueError("Invalid quantity")
        try:
            reorder_val = int(reorder)
            if reorder_val < 0:
                raise ValueError("Reorder level cannot be negative")
        except (ValueError, TypeError):
            raise ValueError("Invalid reorder level")
        return price_val, sell_val, qty_val, reorder_val
    
    def add_new_item(self):
        dialog = tk.Toplevel(self.app.root)
        dialog.title("Add New Item")
        dialog.geometry("450x450")
        dialog.transient(self.app.root)
        dialog.grab_set()
        fields = [("Item Name:*", "name"), ("Description:", "desc"), ("Category:", "cat"),
            ("Unit of Measure:", "uom"), ("Purchase Price:*", "price"), ("Selling Price:*", "sell_price"),
            ("Initial Quantity:*", "qty"), ("Reorder Level:*", "reorder"), ("Location:", "loc")]
        entries = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(row=i, column=0, padx=10, pady=8, sticky='w')
            entry = ttk.Entry(dialog, width=30)
            entry.grid(row=i, column=1, padx=10, pady=8)
            entries[key] = entry
        def save():
            try:
                price_val, sell_val, qty_val, reorder_val = self.validate_item_data(
                    entries["name"].get(), entries["price"].get(), entries["sell_price"].get(),
                    entries["qty"].get(), entries["reorder"].get())
                self.db.execute("INSERT INTO Items (name, description, category, unit_of_measure, unit_price, selling_price) VALUES (?, ?, ?, ?, ?, ?)",
                    (entries["name"].get().strip(), entries["desc"].get(), entries["cat"].get(), 
                     entries["uom"].get(), price_val, sell_val))
                item_id = self.db.lastrowid()
                self.db.execute("INSERT INTO Inventory (item_id, quantity_on_hand, reorder_level, location, last_updated) VALUES (?, ?, ?, ?, ?)",
                    (item_id, qty_val, reorder_val, entries["loc"].get(), datetime.now()))
                self.db.commit()
                messagebox.showinfo("Success", "Item added successfully!")
                dialog.destroy()
                self.app.refresh_all_tabs()
            except ValueError as ve:
                messagebox.showerror("Validation Error", str(ve))
            except Exception as e:
                messagebox.showerror("Error", f"Failed: {str(e)}")
        ttk.Button(dialog, text="Save", command=save).grid(row=len(fields), column=0, columnspan=2, pady=15)
    
    def edit_item(self):
        selected = self.inv_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item")
            return
        item_id = self.inv_tree.item(selected[0])['values'][0]
        self.db.execute('''SELECT i.name, i.description, i.category, i.unit_of_measure, i.unit_price, i.selling_price,
            inv.quantity_on_hand, inv.reorder_level, inv.location
            FROM Items i JOIN Inventory inv ON i.item_id = inv.item_id WHERE i.item_id = ?''', (item_id,))
        data = self.db.fetchone()
        dialog = tk.Toplevel(self.app.root)
        dialog.title("Edit Item")
        dialog.geometry("450x450")
        dialog.transient(self.app.root)
        dialog.grab_set()
        fields = [("Item Name:", data[0]), ("Description:", data[1] or ""), ("Category:", data[2] or ""),
            ("Unit of Measure:", data[3] or ""), ("Purchase Price:", data[4]), ("Selling Price:", data[5]),
            ("Quantity:", data[6]), ("Reorder Level:", data[7]), ("Location:", data[8] or "")]
        entries = []
        for i, (label, value) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(row=i, column=0, padx=10, pady=8, sticky='w')
            entry = ttk.Entry(dialog, width=30)
            entry.insert(0, value)
            entry.grid(row=i, column=1, padx=10, pady=8)
            entries.append(entry)
        def update():
            try:
                price_val, sell_val, qty_val, reorder_val = self.validate_item_data(
                    entries[0].get(), entries[4].get(), entries[5].get(), entries[6].get(), entries[7].get())
                self.db.execute("UPDATE Items SET name=?, description=?, category=?, unit_of_measure=?, unit_price=?, selling_price=? WHERE item_id=?",
                    (entries[0].get().strip(), entries[1].get(), entries[2].get(), entries[3].get(), price_val, sell_val, item_id))
                self.db.execute("UPDATE Inventory SET quantity_on_hand=?, reorder_level=?, location=?, last_updated=? WHERE item_id=?",
                    (qty_val, reorder_val, entries[8].get(), datetime.now(), item_id))
                self.db.commit()
                messagebox.showinfo("Success", "Item updated!")
                dialog.destroy()
                self.app.refresh_all_tabs()
            except ValueError as ve:
                messagebox.showerror("Validation Error", str(ve))
            except Exception as e:
                messagebox.showerror("Error", f"Failed: {str(e)}")
        ttk.Button(dialog, text="Update", command=update).grid(row=len(fields), column=0, columnspan=2, pady=15)
    
    def delete_item(self):
        selected = self.inv_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item")
            return
        item_values = self.inv_tree.item(selected[0])['values']
        item_id, item_name = item_values[0], item_values[1]
        self.db.execute("SELECT COUNT(*) FROM Purchase_Order_Items WHERE item_id = ?", (item_id,))
        po_count = self.db.fetchone()[0]
        self.db.execute("SELECT COUNT(*) FROM Sales_Order_Items WHERE item_id = ?", (item_id,))
        so_count = self.db.fetchone()[0]
        self.db.execute("SELECT COUNT(*) FROM Goods_Receipt WHERE item_id = ?", (item_id,))
        gr_count = self.db.fetchone()[0]
        if po_count > 0 or so_count > 0 or gr_count > 0:
            msg = f"Cannot delete '{item_name}'\n\nReferenced in:\n"
            if po_count > 0: msg += f"- {po_count} Purchase Order(s)\n"
            if so_count > 0: msg += f"- {so_count} Sales Order(s)\n"
            if gr_count > 0: msg += f"- {gr_count} Goods Receipt(s)\n"
            msg += "\nData integrity protected."
            messagebox.showerror("Cannot Delete", msg)
            return
        if messagebox.askyesno("Confirm", f"Delete '{item_name}'?"):
            try:
                self.db.execute("DELETE FROM Inventory WHERE item_id = ?", (item_id,))
                self.db.execute("DELETE FROM Items WHERE item_id = ?", (item_id,))
                self.db.commit()
                messagebox.showinfo("Success", "Deleted!")
                self.app.refresh_all_tabs()
            except Exception as e:
                messagebox.showerror("Error", str(e))


    def create_purchase_order_tab(self):
        po_frame = ttk.Frame(self.notebook)
        self.notebook.add(po_frame, text="🛒 Purchase Orders")
        top_btn_frame = ttk.Frame(po_frame)
        top_btn_frame.pack(side='top', fill='x', padx=10, pady=8)
        ttk.Button(top_btn_frame, text="➕ Create PO", command=self.create_purchase_order).pack(side='left', padx=3)
        ttk.Button(top_btn_frame, text="👁️ View Details", command=self.view_po_details).pack(side='left', padx=3)
        ttk.Button(top_btn_frame, text="🗑️ Delete PO", command=self.delete_purchase_order).pack(side='left', padx=3)
        ttk.Button(top_btn_frame, text="🔄 Refresh", command=self.refresh_purchase_orders).pack(side='right', padx=3)
        columns = ("PO#", "Supplier", "Order Date", "Delivery", "Status", "Amount", "Items")
        self.po_tree = ttk.Treeview(po_frame, columns=columns, show='headings', height=25)
        widths = [60, 150, 100, 100, 100, 100, 60]
        for i, col in enumerate(columns):
            self.po_tree.heading(col, text=col)
            self.po_tree.column(col, width=widths[i])
        self.po_tree.pack(side='left', fill='both', expand=True, padx=10, pady=(0, 10))
        scrollbar = ttk.Scrollbar(po_frame, orient='vertical', command=self.po_tree.yview)
        scrollbar.pack(side='right', fill='y', pady=(0, 10), padx=(0, 10))
        self.po_tree.configure(yscrollcommand=scrollbar.set)
        self.refresh_purchase_orders()
    
    def refresh_purchase_orders(self):
        for item in self.po_tree.get_children():
            self.po_tree.delete(item)
        self.db.execute('''SELECT po.po_number, s.name, po.order_date, po.expected_delivery, po.status, po.total_amount,
            (SELECT COUNT(*) FROM Purchase_Order_Items WHERE po_number = po.po_number) as item_count
            FROM Purchase_Orders po JOIN Suppliers s ON po.supplier_id = s.supplier_id ORDER BY po.po_number DESC''')
        for row in self.db.fetchall():
            self.po_tree.insert('', 'end', values=row)
    
    def create_purchase_order(self):
        self.db.execute("SELECT COUNT(*) FROM Suppliers")
        if self.db.fetchone()[0] == 0:
            messagebox.showwarning("Warning", "Add suppliers first")
            return
        self.db.execute("SELECT COUNT(*) FROM Items")
        if self.db.fetchone()[0] == 0:
            messagebox.showwarning("Warning", "Add items first")
            return
        dialog = tk.Toplevel(self.app.root)
        dialog.title("Create Purchase Order - Multi-Item")
        dialog.geometry("850x650")
        dialog.transient(self.app.root)
        dialog.grab_set()
        
        # Supplier
        ttk.Label(dialog, text="Supplier:*", font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.db.execute("SELECT supplier_id, name FROM Suppliers ORDER BY name")
        suppliers = self.db.fetchall()
        supplier_dict = {f"{s[1]} (ID: {s[0]})": s[0] for s in suppliers}
        supplier_var = tk.StringVar()
        supplier_combo = ttk.Combobox(dialog, textvariable=supplier_var, values=list(supplier_dict.keys()), width=40, state='readonly')
        supplier_combo.grid(row=0, column=1, padx=10, pady=10, columnspan=2)
        
        # Delivery Date
        ttk.Label(dialog, text="Delivery Date (YYYY-MM-DD):*", font=('Arial', 10, 'bold')).grid(row=1, column=0, padx=10, pady=10, sticky='w')
        delivery_entry = ttk.Entry(dialog, width=42)
        delivery_entry.grid(row=1, column=1, padx=10, pady=10, columnspan=2)
        
        # Item Selection
        ttk.Label(dialog, text="Add Items:", font=('Arial', 11, 'bold')).grid(row=2, column=0, padx=10, pady=(20, 10), sticky='w', columnspan=3)
        item_frame = ttk.LabelFrame(dialog, text="Item Selection", padding=10)
        item_frame.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky='ew')
        
        ttk.Label(item_frame, text="Item:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.db.execute("SELECT item_id, name, unit_price FROM Items ORDER BY name")
        items = self.db.fetchall()
        item_dict = {f"{i[1]} (${i[2]:.2f})": (i[0], i[2]) for i in items}
        item_var = tk.StringVar()
        item_combo = ttk.Combobox(item_frame, textvariable=item_var, values=list(item_dict.keys()), width=35, state='readonly')
        item_combo.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(item_frame, text="Qty:").grid(row=0, column=2, padx=5, pady=5)
        qty_entry = ttk.Entry(item_frame, width=10)
        qty_entry.grid(row=0, column=3, padx=5, pady=5)
        
        selected_items = []
        
        def add_item():
            if not item_var.get():
                messagebox.showwarning("Warning", "Select an item")
                return
            try:
                qty = int(qty_entry.get())
                if qty <= 0:
                    messagebox.showerror("Error", "Quantity must be positive")
                    return
                item_id, unit_price = item_dict[item_var.get()]
                item_name = item_var.get().split(' ($')[0]
                for existing in selected_items:
                    if existing[0] == item_id:
                        messagebox.showwarning("Warning", "Item already added")
                        return
                subtotal = unit_price * qty
                selected_items.append((item_id, item_name, qty, unit_price, subtotal))
                items_tree.insert('', 'end', values=(item_name, qty, f"${unit_price:.2f}", f"${subtotal:.2f}"))
                update_total()
                item_var.set('')
                qty_entry.delete(0, tk.END)
            except ValueError:
                messagebox.showerror("Error", "Invalid quantity")
        
        def remove_item():
            selected = items_tree.selection()
            if not selected:
                messagebox.showwarning("Warning", "Select item to remove")
                return
            idx = items_tree.index(selected[0])
            selected_items.pop(idx)
            items_tree.delete(selected[0])
            update_total()
        
        def update_total():
            total = sum(item[4] for item in selected_items)
            total_label.config(text=f"Total Amount: ${total:.2f}")
        
        ttk.Button(item_frame, text="➕ Add", command=add_item).grid(row=0, column=4, padx=5, pady=5)
        ttk.Button(item_frame, text="➖ Remove", command=remove_item).grid(row=0, column=5, padx=5, pady=5)
        
        # Items List
        list_frame = ttk.LabelFrame(dialog, text="Items in Order", padding=10)
        list_frame.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky='nsew')
        columns = ("Item", "Quantity", "Unit Price", "Subtotal")
        items_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)
        for col in columns:
            items_tree.heading(col, text=col)
            items_tree.column(col, width=180)
        items_tree.pack(fill='both', expand=True)
        
        total_label = ttk.Label(dialog, text="Total Amount: $0.00", font=('Arial', 12, 'bold'), foreground='blue')
        total_label.grid(row=5, column=0, columnspan=3, pady=10)
        
        def save_po():
            try:
                if not supplier_var.get():
                    messagebox.showerror("Error", "Select a supplier")
                    return
                if not delivery_entry.get().strip():
                    messagebox.showerror("Error", "Enter delivery date")
                    return
                if not selected_items:
                    messagebox.showerror("Error", "Add at least one item")
                    return
                supplier_id = supplier_dict[supplier_var.get()]
                total_amount = sum(item[4] for item in selected_items)
                self.db.execute("INSERT INTO Purchase_Orders (supplier_id, order_date, expected_delivery, status, total_amount) VALUES (?, ?, ?, ?, ?)",
                    (supplier_id, datetime.now().date(), delivery_entry.get(), "Pending", total_amount))
                po_number = self.db.lastrowid()
                for item_id, item_name, qty, unit_price, subtotal in selected_items:
                    self.db.execute("INSERT INTO Purchase_Order_Items (po_number, item_id, quantity, unit_price, subtotal) VALUES (?, ?, ?, ?, ?)",
                        (po_number, item_id, qty, unit_price, subtotal))
                self.db.commit()
                messagebox.showinfo("Success", f"PO #{po_number} created!\n{len(selected_items)} items, Total: ${total_amount:.2f}")
                dialog.destroy()
                self.refresh_purchase_orders()
            except Exception as e:
                messagebox.showerror("Error", f"Failed: {str(e)}")
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.grid(row=6, column=0, columnspan=3, pady=20)
        ttk.Button(btn_frame, text="✅ Create Purchase Order", command=save_po, width=25).pack()
    
    def delete_purchase_order(self):
        selected = self.po_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a purchase order")
            return
        po_number = self.po_tree.item(selected[0])['values'][0]
        self.db.execute("SELECT COUNT(*) FROM Goods_Receipt WHERE po_number = ?", (po_number,))
        gr_count = self.db.fetchone()[0]
        if gr_count > 0:
            messagebox.showerror("Cannot Delete", f"PO #{po_number} has {gr_count} goods receipt(s).\nData integrity protected.")
            return
        if messagebox.askyesno("Confirm", f"Delete PO #{po_number} and all items?"):
            try:
                self.db.execute("DELETE FROM Purchase_Order_Items WHERE po_number = ?", (po_number,))
                self.db.execute("DELETE FROM Purchase_Orders WHERE po_number = ?", (po_number,))
                self.db.commit()
                messagebox.showinfo("Success", f"PO #{po_number} deleted!")
                self.refresh_purchase_orders()
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def view_po_details(self):
        selected = self.po_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a PO")
            return
        po_number = self.po_tree.item(selected[0])['values'][0]
        dialog = tk.Toplevel(self.app.root)
        dialog.title(f"PO #{po_number} Details")
        dialog.geometry("900x550")
        dialog.transient(self.app.root)
        dialog.grab_set()
        self.db.execute('''SELECT po.po_number, s.name, po.order_date, po.expected_delivery, po.status, po.total_amount
            FROM Purchase_Orders po JOIN Suppliers s ON po.supplier_id = s.supplier_id WHERE po.po_number = ?''', (po_number,))
        po_info = self.db.fetchone()
        info_frame = ttk.LabelFrame(dialog, text="Order Info", padding=10)
        info_frame.pack(fill='x', padx=10, pady=10)
        labels = [f"PO#: {po_info[0]}", f"Supplier: {po_info[1]}", f"Order Date: {po_info[2]}",
            f"Delivery: {po_info[3]}", f"Status: {po_info[4]}", f"Total: ${po_info[5]:.2f}"]
        for i, text in enumerate(labels):
            ttk.Label(info_frame, text=text, font=('Arial', 10)).grid(row=i//3, column=i%3, sticky='w', padx=15, pady=5)
        items_frame = ttk.LabelFrame(dialog, text="Items", padding=10)
        items_frame.pack(fill='both', expand=True, padx=10, pady=10)
        columns = ("Item", "Quantity", "Unit Price", "Subtotal")
        tree = ttk.Treeview(items_frame, columns=columns, show='headings', height=12)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=200)
        tree.pack(fill='both', expand=True)
        self.db.execute('''SELECT i.name, poi.quantity, poi.unit_price, poi.subtotal
            FROM Purchase_Order_Items poi JOIN Items i ON poi.item_id = i.item_id WHERE poi.po_number = ?''', (po_number,))
        for row in self.db.fetchall():
            tree.insert('', 'end', values=(row[0], row[1], f"${row[2]:.2f}", f"${row[3]:.2f}"))
    
    def create_suppliers_tab(self):
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
        for item in self.sup_tree.get_children():
            self.sup_tree.delete(item)
        self.db.execute("SELECT supplier_id, name, contact_person, phone, email, payment_terms FROM Suppliers")
        for row in self.db.fetchall():
            self.sup_tree.insert('', 'end', values=row)
    
    def add_supplier(self):
        dialog = tk.Toplevel(self.app.root)
        dialog.title("Add Supplier")
        dialog.geometry("450x350")
        dialog.transient(self.app.root)
        dialog.grab_set()
        fields = ["Name:*", "Contact Person:", "Phone:", "Email:", "Address:", "Payment Terms:"]
        entries = []
        for i, field in enumerate(fields):
            ttk.Label(dialog, text=field).grid(row=i, column=0, padx=10, pady=8, sticky='w')
            entry = ttk.Entry(dialog, width=30)
            entry.grid(row=i, column=1, padx=10, pady=8)
            entries.append(entry)
        def save():
            try:
                if not entries[0].get().strip():
                    messagebox.showerror("Error", "Supplier name required")
                    return
                self.db.execute("INSERT INTO Suppliers (name, contact_person, phone, email, address, payment_terms) VALUES (?, ?, ?, ?, ?, ?)",
                    tuple(e.get() for e in entries))
                self.db.commit()
                messagebox.showinfo("Success", "Supplier added!")
                dialog.destroy()
                self.refresh_suppliers()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        ttk.Button(dialog, text="Save", command=save).grid(row=len(fields), column=0, columnspan=2, pady=15)
    
    def edit_supplier(self):
        selected = self.sup_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a supplier")
            return
        supplier_id = self.sup_tree.item(selected[0])['values'][0]
        self.db.execute("SELECT name, contact_person, phone, email, address, payment_terms FROM Suppliers WHERE supplier_id = ?", (supplier_id,))
        data = self.db.fetchone()
        dialog = tk.Toplevel(self.app.root)
        dialog.title("Edit Supplier")
        dialog.geometry("450x350")
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
                if not entries[0].get().strip():
                    messagebox.showerror("Error", "Name required")
                    return
                self.db.execute("UPDATE Suppliers SET name=?, contact_person=?, phone=?, email=?, address=?, payment_terms=? WHERE supplier_id=?",
                    tuple(e.get() for e in entries) + (supplier_id,))
                self.db.commit()
                messagebox.showinfo("Success", "Updated!")
                dialog.destroy()
                self.refresh_suppliers()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        ttk.Button(dialog, text="Update", command=update).grid(row=len(fields), column=0, columnspan=2, pady=15)
    
    def delete_supplier(self):
        selected = self.sup_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a supplier")
            return
        supplier_id, name = self.sup_tree.item(selected[0])['values'][0], self.sup_tree.item(selected[0])['values'][1]
        self.db.execute("SELECT COUNT(*) FROM Purchase_Orders WHERE supplier_id = ?", (supplier_id,))
        if self.db.fetchone()[0] > 0:
            messagebox.showerror("Cannot Delete", f"'{name}' has purchase orders.\nData integrity protected.")
            return
        if messagebox.askyesno("Confirm", f"Delete '{name}'?"):
            try:
                self.db.execute("DELETE FROM Suppliers WHERE supplier_id = ?", (supplier_id,))
                self.db.commit()
                messagebox.showinfo("Success", "Deleted!")
                self.refresh_suppliers()
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def create_goods_receipt_tab(self):
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
        for item in self.receipt_tree.get_children():
            self.receipt_tree.delete(item)
        self.db.execute('''SELECT gr.receipt_id, gr.po_number, s.name, i.name, gr.invoice_number,
            gr.received_quantity, gr.accepted_quantity, gr.rejected_quantity, gr.receipt_date
            FROM Goods_Receipt gr JOIN Suppliers s ON gr.supplier_id = s.supplier_id
            JOIN Items i ON gr.item_id = i.item_id ORDER BY gr.receipt_id DESC''')
        for row in self.db.fetchall():
            self.receipt_tree.insert('', 'end', values=row)
    
    def new_goods_receipt(self):
        # [Keep existing new_goods_receipt implementation from original code]
        # Due to length, use the original implementation
        pass
    
    def create_alerts_tab(self):
        alert_frame = ttk.Frame(self.notebook)
        self.notebook.add(alert_frame, text="⚠️ Alerts")
        top_btn_frame = ttk.Frame(alert_frame)
        top_btn_frame.pack(side='top', fill='x', padx=10, pady=8)
        ttk.Label(top_btn_frame, text="Low Stock Alerts", font=('Arial', 12, 'bold')).pack(side='left', padx=5)
        ttk.Button(top_btn_frame, text="🔄 Refresh", command=self.refresh_alerts).pack(side='right', padx=3)
        columns = ("Item ID", "Item Name", "Current Stock", "Reorder Level", "Action Needed")
        self.alert_tree = ttk.Treeview(alert_frame, columns=columns, show='headings', height=20)
        for col in columns:
            self.alert_tree.heading(col, text=col)
            self.alert_tree.column(col, width=180)
        self.alert_tree.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        self.refresh_alerts()
    
    def refresh_alerts(self):
        for item in self.alert_tree.get_children():
            self.alert_tree.delete(item)
        self.db.execute('''SELECT i.item_id, i.name, inv.quantity_on_hand, inv.reorder_level
            FROM Items i JOIN Inventory inv ON i.item_id = inv.item_id
            WHERE inv.quantity_on_hand <= inv.reorder_level
            ORDER BY (inv.quantity_on_hand - inv.reorder_level)''')
        for row in self.db.fetchall():
            action = f"Order {row[3] * 2 - row[2]} units"
            self.alert_tree.insert('', 'end', values=row + (action,))
