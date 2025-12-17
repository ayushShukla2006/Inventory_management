"""
Main Application File - Integrated Purchase & Sales Management System with Menu Bar UI
Run this file to start the application
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from purchase_module import PurchaseModule
from sales_module import SalesModule

class IntegratedManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Integrated Purchase & Sales Management System")
        self.root.geometry("1440x900")
        
        # Initialize database
        self.db = Database()
        
        # Create main content area with notebook (before menu bar)
        self.create_main_content()
        
        # Initialize modules (before menu bar)
        self.purchase_module = PurchaseModule(self.notebook, self.db, self)
        self.sales_module = SalesModule(self.notebook, self.db, self)
        
        # Create menu bar (after modules are initialized)
        self.create_menu_bar()
        
        # Show welcome screen by default
        self.show_dashboard()
        
    
    def create_menu_bar(self):
        """Create the top menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
    
        # ==================== HOME MENU ====================
        home_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="🏠 Home", menu=home_menu)
    
        home_menu.add_command(label="📊 Dashboard", command=self.show_dashboard)
        home_menu.add_separator()
        home_menu.add_command(label="🔄 Refresh All Data", command=self.refresh_all_tabs)
        home_menu.add_separator()
        home_menu.add_command(label="🚪 Exit", command=self.on_closing)
    
        # ==================== MASTERS MENU ====================
        masters_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="📋 Masters", menu=masters_menu)
    
        masters_menu.add_command(label="📦 Items & Inventory", 
                            command=lambda: self.switch_to_tab("📦 Inventory"))
        masters_menu.add_separator()
        masters_menu.add_command(label="🏢 Suppliers", 
                            command=lambda: self.switch_to_tab("🏢 Suppliers"))
        masters_menu.add_command(label="👥 Customers", 
                            command=lambda: self.switch_to_tab("👥 Customers"))
        masters_menu.add_separator()
            # MOVED: Purchase and Sales Orders to Masters
        masters_menu.add_command(label="🛒 Purchase Orders", 
                            command=lambda: self.switch_to_tab("🛒 Purchase Orders"))
        masters_menu.add_command(label="🛍 Sales Orders", 
                            command=lambda: self.switch_to_tab("🛍 Sales Orders"))

    # ==================== TRANSACTIONS MENU ====================
        transactions_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="💼 Transactions", menu=transactions_menu)
    
        # Purchase submenu
        purchase_submenu = tk.Menu(transactions_menu, tearoff=0)
        transactions_menu.add_cascade(label="🛒 Purchase", menu=purchase_submenu)
        purchase_submenu.add_command(label="➕ Create Purchase Order", 
                                    command=self.purchase_module.create_purchase_order)
        purchase_submenu.add_command(label="📥 Record Goods Receipt", 
                                    command=self.purchase_module.new_goods_receipt)
        purchase_submenu.add_command(label="📋 View Goods Receipts", 
                                    command=lambda: self.switch_to_tab("📥 Goods Receipt"))
    
        transactions_menu.add_separator()
    
        # Sales submenu
        sales_submenu = tk.Menu(transactions_menu, tearoff=0)
        transactions_menu.add_cascade(label="🛍️ Sales", menu=sales_submenu)
        sales_submenu.add_command(label="➕ Create Sales Order", 
                                 command=self.sales_module.create_sales_order)
        sales_submenu.add_command(label="🚚 Process Delivery", 
                                 command=self.sales_module.new_delivery)
        sales_submenu.add_command(label="📋 View Deliveries", 
                                 command=lambda: self.switch_to_tab("🚚 Delivery"))
    
        transactions_menu.add_separator()
    
        # Invoice submenu
        invoice_submenu = tk.Menu(transactions_menu, tearoff=0)
        transactions_menu.add_cascade(label="📄 Invoices", menu=invoice_submenu)
        invoice_submenu.add_command(label="➕ Generate Invoice", 
                                   command=self.sales_module.generate_invoice)
        invoice_submenu.add_command(label="📋 View Invoices", 
                                   command=lambda: self.switch_to_tab("📄 Invoices"))
        invoice_submenu.add_command(label="💰 Mark as Paid", 
                                   command=self.sales_module.mark_invoice_paid)
    
        # ==================== REPORTS MENU ====================
        reports_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="📊 Reports", menu=reports_menu)
    
        reports_menu.add_command(label="💰 GST Summary", 
                                command=lambda: self.switch_to_tab("💰 GST Summary"))
        reports_menu.add_command(label="📊 Sales Reports", 
                                command=lambda: self.switch_to_tab("📊 Reports"))
        reports_menu.add_command(label="⚠️ Low Stock Alerts", 
                                command=lambda: self.switch_to_tab("⚠️ Alerts"))
    
        # ==================== HELP MENU ====================
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="❓ Help", menu=help_menu)
    
        help_menu.add_command(label="📖 About", command=self.show_about)
        help_menu.add_command(label="ℹ️ System Info", command=self.show_system_info)

    
    def create_main_content(self):
        """Create the main content area"""
        # Header frame
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill='x', padx=10, pady=(5, 0))
        
        # Title
        title_label = ttk.Label(header_frame, 
                               text="Integrated Purchase & Sales Management System", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(side='left', pady=10)
        
        # Quick action buttons
        quick_frame = ttk.Frame(header_frame)
        quick_frame.pack(side='right', pady=10)
        
        ttk.Button(quick_frame, text="🏠 Dashboard", 
                  command=self.show_dashboard, width=12).pack(side='left', padx=2)
        ttk.Button(quick_frame, text="🔄 Refresh", 
                  command=self.refresh_all_tabs, width=10).pack(side='left', padx=2)
        
        # Separator
        ttk.Separator(self.root, orient='horizontal').pack(fill='x', padx=10)
        
        # Create main notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # HIDE NOTEBOOK TABS
        style = ttk.Style()
        style.layout("TNotebook.Tab", [])
    
    def switch_to_tab(self, tab_name):
        """Switch to a specific tab by name"""
        for i in range(self.notebook.index("end")):
            if self.notebook.tab(i, "text") == tab_name:
                self.notebook.select(i)
                return
        messagebox.showinfo("Info", f"Tab '{tab_name}' not found")
    
    def show_dashboard(self):
        """Show dashboard with summary statistics"""
        # Check if dashboard tab already exists
        for i in range(self.notebook.index("end")):
            if self.notebook.tab(i, "text") == "🏠 Dashboard":
                self.notebook.select(i)
                self.refresh_dashboard()
                return
        
        # Create dashboard tab
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.insert(0, dashboard_frame, text="🏠 Dashboard")
        self.notebook.select(0)
        
        # Title
        title_frame = ttk.Frame(dashboard_frame)
        title_frame.pack(fill='x', padx=20, pady=20)
        
        ttk.Label(title_frame, text="System Dashboard", 
                 font=('Arial', 18, 'bold')).pack(anchor='w')
        ttk.Label(title_frame, text="Quick overview of your business operations", 
                 font=('Arial', 10), foreground='gray').pack(anchor='w')
        
        # Create dashboard content
        self.dashboard_frame = dashboard_frame
        self.refresh_dashboard()
    
    def refresh_dashboard(self):
        """Refresh dashboard statistics - HORIZONTAL LAYOUT"""
        if not hasattr(self, 'dashboard_frame'):
            return
    
        # Clear existing widgets (except title)
        for widget in self.dashboard_frame.winfo_children()[1:]:
           widget.destroy()
    
        # Create scrollable frame
        canvas = tk.Canvas(self.dashboard_frame, bg='#f5f5f5')
        scrollbar = ttk.Scrollbar(self.dashboard_frame, orient="vertical", command=canvas.yview)
        scrollable = ttk.Frame(canvas)
    
        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
    
        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=(0, 20))
        scrollbar.pack(side="right", fill="y", pady=(0, 20))
    
        # === INVENTORY SECTION - HORIZONTAL ===
        inv_section = ttk.LabelFrame(scrollable, text="📦 Inventory Status", padding=15)
        inv_section.pack(fill='x', pady=(0, 15))
    
        self.db.execute("SELECT COUNT(*) FROM Items")
        total_items = self.db.fetchone()[0]
    
        self.db.execute("SELECT COUNT(*) FROM Items i JOIN Inventory inv ON i.item_id = inv.item_id WHERE inv.quantity_on_hand <= inv.reorder_level")
        low_stock = self.db.fetchone()[0]
    
        self.db.execute("SELECT COALESCE(SUM(quantity_on_hand), 0) FROM Inventory")
        total_stock = self.db.fetchone()[0]
    
        stats_frame = ttk.Frame(inv_section)
        stats_frame.pack(fill='x')
    
        # Configure columns to distribute evenly
        for i in range(3):
            stats_frame.grid_columnconfigure(i, weight=1)
    
        self.create_stat_card(stats_frame, "Total Items", str(total_items), "blue", 0, 0)
        self.create_stat_card(stats_frame, "Low Stock Items", str(low_stock), "red" if low_stock > 0 else "green", 0, 1)
        self.create_stat_card(stats_frame, "Total Stock Units", str(total_stock), "blue", 0, 2)
    
        # === PURCHASE SECTION - HORIZONTAL ===
        purchase_section = ttk.LabelFrame(scrollable, text="🛒 Purchase Overview", padding=15)
        purchase_section.pack(fill='x', pady=(0, 15))
    
        self.db.execute("SELECT COUNT(*) FROM Purchase_Orders")
        total_pos = self.db.fetchone()[0]
    
        self.db.execute("SELECT COUNT(*) FROM Purchase_Orders WHERE status = 'Pending'")
        pending_pos = self.db.fetchone()[0]
    
        self.db.execute("SELECT COALESCE(SUM(total_amount), 0) FROM Purchase_Orders")
        total_purchase = self.db.fetchone()[0]
    
        self.db.execute("SELECT COUNT(*) FROM Suppliers")
        total_suppliers = self.db.fetchone()[0]
    
        stats_frame = ttk.Frame(purchase_section)
        stats_frame.pack(fill='x')
    
        for i in range(4):
            stats_frame.grid_columnconfigure(i, weight=1)
    
        self.create_stat_card(stats_frame, "Total POs", str(total_pos), "blue", 0, 0)
        self.create_stat_card(stats_frame, "Pending POs", str(pending_pos), "orange", 0, 1)
        self.create_stat_card(stats_frame, "Total Purchase Value", f"₹{total_purchase:,.2f}", "green", 0, 2)
        self.create_stat_card(stats_frame, "Suppliers", str(total_suppliers), "blue", 0, 3)
    
        # === SALES SECTION - HORIZONTAL ===
        sales_section = ttk.LabelFrame(scrollable, text="🛍️ Sales Overview", padding=15)
        sales_section.pack(fill='x', pady=(0, 15))
    
        self.db.execute("SELECT COUNT(*) FROM Sales_Orders")
        total_sos = self.db.fetchone()[0]
    
        self.db.execute("SELECT COUNT(*) FROM Sales_Orders WHERE status = 'Pending'")
        pending_sos = self.db.fetchone()[0]
    
        self.db.execute("SELECT COALESCE(SUM(total_amount), 0) FROM Sales_Orders")
        total_sales = self.db.fetchone()[0]
    
        self.db.execute("SELECT COUNT(*) FROM Customers")
        total_customers = self.db.fetchone()[0]
    
        stats_frame = ttk.Frame(sales_section)
        stats_frame.pack(fill='x')
    
        for i in range(4):
            stats_frame.grid_columnconfigure(i, weight=1)
    
        self.create_stat_card(stats_frame, "Total SOs", str(total_sos), "blue", 0, 0)
        self.create_stat_card(stats_frame, "Pending SOs", str(pending_sos), "orange", 0, 1)
        self.create_stat_card(stats_frame, "Total Sales Value", f"₹{total_sales:,.2f}", "green", 0, 2)
        self.create_stat_card(stats_frame, "Customers", str(total_customers), "blue", 0, 3)
    
        # === INVOICES SECTION - HORIZONTAL ===
        invoice_section = ttk.LabelFrame(scrollable, text="📄 Invoice Status", padding=15)
        invoice_section.pack(fill='x', pady=(0, 15))
    
        self.db.execute("SELECT COUNT(*) FROM Invoices")
        total_invoices = self.db.fetchone()[0]
    
        self.db.execute("SELECT COUNT(*) FROM Invoices WHERE status = 'Unpaid'")
        unpaid_invoices = self.db.fetchone()[0]
    
        self.db.execute("SELECT COALESCE(SUM(total_amount), 0) FROM Invoices WHERE status = 'Unpaid'")
        unpaid_amount = self.db.fetchone()[0]
    
        stats_frame = ttk.Frame(invoice_section)
        stats_frame.pack(fill='x')
    
        for i in range(3):
            stats_frame.grid_columnconfigure(i, weight=1)
    
        self.create_stat_card(stats_frame, "Total Invoices", str(total_invoices), "blue", 0, 0)
        self.create_stat_card(stats_frame, "Unpaid Invoices", str(unpaid_invoices), "red" if unpaid_invoices > 0 else "green", 0, 1)
        self.create_stat_card(stats_frame, "Unpaid Amount", f"₹{unpaid_amount:,.2f}", "red" if unpaid_amount > 0 else "green", 0, 2)
    
        # === GST SECTION - HORIZONTAL ===
        gst_section = ttk.LabelFrame(scrollable, text="💰 GST Summary", padding=15)
        gst_section.pack(fill='x', pady=(0, 15))
    
        self.db.execute("SELECT COALESCE(SUM(total_gst), 0) FROM Sales_Orders")
        output_gst = self.db.fetchone()[0]
    
        self.db.execute("SELECT COALESCE(SUM(total_gst), 0) FROM Purchase_Orders")
        input_gst = self.db.fetchone()[0]
    
        net_gst = output_gst - input_gst
    
        stats_frame = ttk.Frame(gst_section)
        stats_frame.pack(fill='x')
    
        for i in range(3):
            stats_frame.grid_columnconfigure(i, weight=1)
    
        self.create_stat_card(stats_frame, "Output GST (Collected)", f"₹{output_gst:,.2f}", "green", 0, 0)
        self.create_stat_card(stats_frame, "Input GST (Paid)", f"₹{input_gst:,.2f}", "orange", 0, 1)
        self.create_stat_card(stats_frame, "Net GST Liability", f"₹{net_gst:,.2f}", "red" if net_gst > 0 else "blue", 0, 2)
    
        # Quick Actions - HORIZONTAL
        actions_section = ttk.LabelFrame(scrollable, text="⚡ Quick Actions", padding=15)
        actions_section.pack(fill='x', pady=(0, 15))
    
        actions_frame = ttk.Frame(actions_section)
        actions_frame.pack()
    
        # Make buttons horizontal
        ttk.Button(actions_frame, text="➕ Create Purchase Order", 
                  command=self.purchase_module.create_purchase_order, width=25).pack(side='left', padx=5, pady=5)
        ttk.Button(actions_frame, text="➕ Create Sales Order", 
                  command=self.sales_module.create_sales_order, width=25).pack(side='left', padx=5, pady=5)
        ttk.Button(actions_frame, text="➕ Add New Item", 
                  command=self.purchase_module.add_new_item, width=25).pack(side='left', padx=5, pady=5)
        ttk.Button(actions_frame, text="📄 Generate Invoice", 
                  command=self.sales_module.generate_invoice, width=25).pack(side='left', padx=5, pady=5)
    
    def create_stat_card(self, parent, label, value, color, row, col):
        """Create a statistics card"""
        card_frame = ttk.Frame(parent, relief='solid', borderwidth=1)
        card_frame.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        parent.grid_columnconfigure(col, weight=1)
        
        ttk.Label(card_frame, text=label, font=('Arial', 9), 
                 foreground='gray').pack(pady=(10, 5))
        ttk.Label(card_frame, text=value, font=('Arial', 16, 'bold'), 
                 foreground=color).pack(pady=(0, 10))
    
    def show_about(self):
        """Show about dialog"""
        about_text = """Integrated Purchase & Sales Management System
        
Version: 1.0
        
A comprehensive ERP solution for managing:
• Inventory & Stock Control
• Purchase Orders & Supplier Management
• Sales Orders & Customer Management
• Goods Receipt & Delivery Tracking
• Invoice Generation & Payment Tracking
• GST Compliance & Tax Management
• Reports & Analytics

Developed with Python & Tkinter
© 2025 All Rights Reserved"""
        
        messagebox.showinfo("About", about_text)
    
    def show_system_info(self):
        """Show system information"""
        self.db.execute("SELECT COUNT(*) FROM Items")
        items = self.db.fetchone()[0]
        
        self.db.execute("SELECT COUNT(*) FROM Suppliers")
        suppliers = self.db.fetchone()[0]
        
        self.db.execute("SELECT COUNT(*) FROM Customers")
        customers = self.db.fetchone()[0]
        
        self.db.execute("SELECT COUNT(*) FROM Purchase_Orders")
        pos = self.db.fetchone()[0]
        
        self.db.execute("SELECT COUNT(*) FROM Sales_Orders")
        sos = self.db.fetchone()[0]
        
        info_text = f"""System Information

Database: SQLite (integrated_system.db)

Current Data:
• Items: {items}
• Suppliers: {suppliers}
• Customers: {customers}
• Purchase Orders: {pos}
• Sales Orders: {sos}

Status: Operational ✓"""
        
        messagebox.showinfo("System Information", info_text)
    
    def refresh_all_tabs(self):
        """Refresh all tabs across both modules"""
        self.purchase_module.refresh_all()
        self.sales_module.refresh_all()
        if hasattr(self, 'dashboard_frame'):
            self.refresh_dashboard()
        messagebox.showinfo("Success", "All data refreshed successfully!")
    
    def on_closing(self):
        """Handle application close"""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.db.close()
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = IntegratedManagementSystem(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
