"""
Main Application File - Integrated Purchase & Sales Management System with Menu Bar UI
Run this file to start the application
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from purchase_module import PurchaseModule
from sales_module import SalesModule


# ==================== GLOBAL UI SETTINGS ====================

UI_SCALING = 1.60 # 1.10 subtle | 1.15 comfortable | 1.20 accessibility

BASE_FONT = ("Arial", 12)
SMALL_FONT = ("Arial", 14)
TITLE_FONT = ("Arial", 18, "bold")
HEADER_FONT = ("Arial", 16, "bold")

class IntegratedManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Integrated Purchase & Sales Management System")
        self.root.geometry("1440x900")
        
        # Initialize database
        self.db = Database()
        
        # Check if company details exist - FIRST TIME SETUP
        if not self.db.company_exists():
            # Show first-time setup wizard
            self.show_company_setup_wizard()
            return
        
        # Normal initialization if company exists
        self.initialize_main_app()

    def initialize_main_app(self):
        """Initialize the main application after company setup"""
        # Create main content area with notebook (before menu bar)
        self.create_main_content()
        
        # Initialize modules (before menu bar)
        self.purchase_module = PurchaseModule(self.notebook, self.db, self)
        self.sales_module = SalesModule(self.notebook, self.db, self)
        
        # Create menu bar (after modules are initialized)
        self.create_menu_bar()
        
        # Show welcome screen by default
        self.show_dashboard()
        
    # ==================== MENU BAR ====================

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
        
        home_menu.add_command(label="📖 About", command=self.show_about)
        home_menu.add_command(label="ℹ️ System Info", command=self.show_system_info)
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
        masters_menu.add_command(label="🏭 Company Details", 
                            command=self.show_company_details)

    # ==================== TRANSACTIONS MENU ====================
        transactions_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="💼 Transactions", menu=transactions_menu)
    
        # Purchase submenu
        purchase_submenu = tk.Menu(transactions_menu, tearoff=0)
        transactions_menu.add_cascade(label="🛒 Purchase", menu=purchase_submenu)
        purchase_submenu.add_command(
            label="📄 Purchase Orders",
            command=lambda: self.switch_to_tab("🛒 Purchase Orders")
        )
        purchase_submenu.add_command(label="➕ Create Purchase Order", 
                                    command=self.purchase_module.create_purchase_order)
        purchase_submenu.add_command(label="📋 View Goods Receipts", 
                                    command=lambda: self.switch_to_tab("📥 Goods Receipt"))
        purchase_submenu.add_command(label="📥 Record Goods Receipt", 
                                    command=self.purchase_module.new_goods_receipt)

        transactions_menu.add_separator()
    
        # Sales submenu
        sales_submenu = tk.Menu(transactions_menu, tearoff=0)
        transactions_menu.add_cascade(label="🛍️ Sales", menu=sales_submenu)
        sales_submenu.add_command(
            label="📄 Sales Orders",
            command=lambda: self.switch_to_tab("🛒 Sales Orders")
        )
        sales_submenu.add_command(label="➕ Create Sales Order", 
                                 command=self.sales_module.create_sales_order)
        sales_submenu.add_command(label="📋 View Deliveries", 
                                 command=lambda: self.switch_to_tab("🚚 Delivery"))
        sales_submenu.add_command(label="🚚 Process Delivery", 
                                 command=self.sales_module.new_delivery)
    
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
    
        

    
    def create_main_content(self):
        """Create the main content area"""
        # Header frame
        header = ttk.Frame(self.root)
        header.pack(fill='x', padx=10, pady=(5))
        
        ttk.Label(header,
                  text="Integrated Purchase & Sales Management System",
                  font=HEADER_FONT).pack(side="left", pady=10)

        quick = ttk.Frame(header)
        quick.pack(side="right")
        
        # Quick action buttons
        quick_frame = ttk.Frame(header)
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
    
        # ==================== NAVIGATION ====================
    
    def switch_to_tab(self, tab_name):
        """Switch to a specific tab by name"""
        for i in range(self.notebook.index("end")):
            if self.notebook.tab(i, "text") == tab_name:
                self.notebook.select(i)
                return
        messagebox.showinfo("Info", f"Tab '{tab_name}' not found")
    
    # ==================== DASHBOARD ====================
    
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
                  font=TITLE_FONT).pack(anchor="w")
        ttk.Label(title_frame,
                  text="Quick overview of your business operations",
                  font=SMALL_FONT,
                  foreground="gray").pack(anchor="w")
        
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
        canvas_window = canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
    
        # Make scrollable frame expand to fill canvas width
        def configure_canvas_width(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind("<Configure>", configure_canvas_width)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # === INVENTORY SECTION - HORIZONTAL ===
        inv_section = ttk.LabelFrame(scrollable, text="📦 Inventory Status", padding=15)
        inv_section.pack(fill='x', pady=(0, 15), padx=10)

        self.db.execute("SELECT COUNT(*) FROM Items")
        total_items = self.db.fetchone()[0]

        self.db.execute("SELECT COUNT(*) FROM Items i JOIN Inventory inv ON i.item_id = inv.item_id WHERE inv.quantity_on_hand <= inv.reorder_level")
        low_stock = self.db.fetchone()[0]

        self.db.execute("SELECT COALESCE(SUM(quantity_on_hand), 0) FROM Inventory")
        total_stock = self.db.fetchone()[0]

        stats_frame = ttk.Frame(inv_section)
        stats_frame.pack(fill='both', expand=True)

        # Configure columns to distribute evenly
        for i in range(3):
            stats_frame.grid_columnconfigure(i, weight=1)
        stats_frame.grid_rowconfigure(0, weight=1)

        self.create_stat_card(stats_frame, "Total Items", str(total_items), "blue", 0, 0)
        self.create_stat_card(stats_frame, "Low Stock Items", str(low_stock), "red" if low_stock > 0 else "green", 0, 1)
        self.create_stat_card(stats_frame, "Total Stock Units", str(total_stock), "blue", 0, 2)

        # === PURCHASE SECTION - HORIZONTAL ===
        purchase_section = ttk.LabelFrame(scrollable, text="🛒 Purchase Overview", padding=15)
        purchase_section.pack(fill='x', pady=(0, 15), padx=10)

        self.db.execute("SELECT COUNT(*) FROM Purchase_Orders")
        total_pos = self.db.fetchone()[0]

        self.db.execute("SELECT COUNT(*) FROM Purchase_Orders WHERE status = 'Pending'")
        pending_pos = self.db.fetchone()[0]

        self.db.execute("SELECT COALESCE(SUM(total_amount), 0) FROM Purchase_Orders")
        total_purchase = self.db.fetchone()[0]

        self.db.execute("SELECT COUNT(*) FROM Suppliers")
        total_suppliers = self.db.fetchone()[0]

        stats_frame = ttk.Frame(purchase_section)
        stats_frame.pack(fill='both', expand=True)

        for i in range(4):
            stats_frame.grid_columnconfigure(i, weight=1)
        stats_frame.grid_rowconfigure(0, weight=1)
    
        self.create_stat_card(stats_frame, "Total POs", str(total_pos), "blue", 0, 0)
        self.create_stat_card(stats_frame, "Pending POs", str(pending_pos), "orange", 0, 1)
        self.create_stat_card(stats_frame, "Total Purchase Value", f"₹{total_purchase:,.2f}", "green", 0, 2)
        self.create_stat_card(stats_frame, "Suppliers", str(total_suppliers), "blue", 0, 3)

        # === SALES SECTION - HORIZONTAL ===
        sales_section = ttk.LabelFrame(scrollable, text="🛍️ Sales Overview", padding=15)
        sales_section.pack(fill='x', pady=(0, 15), padx=10)

        self.db.execute("SELECT COUNT(*) FROM Sales_Orders")
        total_sos = self.db.fetchone()[0]

        self.db.execute("SELECT COUNT(*) FROM Sales_Orders WHERE status = 'Pending'")
        pending_sos = self.db.fetchone()[0]

        self.db.execute("SELECT COALESCE(SUM(total_amount), 0) FROM Sales_Orders")
        total_sales = self.db.fetchone()[0]

        self.db.execute("SELECT COUNT(*) FROM Customers")
        total_customers = self.db.fetchone()[0]

        stats_frame = ttk.Frame(sales_section)
        stats_frame.pack(fill='both', expand=True)

        for i in range(4):
            stats_frame.grid_columnconfigure(i, weight=1)
        stats_frame.grid_rowconfigure(0, weight=1)
    
        self.create_stat_card(stats_frame, "Total SOs", str(total_sos), "blue", 0, 0)
        self.create_stat_card(stats_frame, "Pending SOs", str(pending_sos), "orange", 0, 1)
        self.create_stat_card(stats_frame, "Total Sales Value", f"₹{total_sales:,.2f}", "green", 0, 2)
        self.create_stat_card(stats_frame, "Customers", str(total_customers), "blue", 0, 3)

        # === INVOICES SECTION - HORIZONTAL ===
        invoice_section = ttk.LabelFrame(scrollable, text="📄 Invoice Status", padding=15)
        invoice_section.pack(fill='x', pady=(0, 15), padx=10)

        self.db.execute("SELECT COUNT(*) FROM Invoices")
        total_invoices = self.db.fetchone()[0]

        self.db.execute("SELECT COUNT(*) FROM Invoices WHERE status = 'Unpaid'")
        unpaid_invoices = self.db.fetchone()[0]

        self.db.execute("SELECT COALESCE(SUM(total_amount), 0) FROM Invoices WHERE status = 'Unpaid'")
        unpaid_amount = self.db.fetchone()[0]

        stats_frame = ttk.Frame(invoice_section)
        stats_frame.pack(fill='both', expand=True)

        for i in range(3):
            stats_frame.grid_columnconfigure(i, weight=1)
        stats_frame.grid_rowconfigure(0, weight=1)
    
        self.create_stat_card(stats_frame, "Total Invoices", str(total_invoices), "blue", 0, 0)
        self.create_stat_card(stats_frame, "Unpaid Invoices", str(unpaid_invoices), "red" if unpaid_invoices > 0 else "green", 0, 1)
        self.create_stat_card(stats_frame, "Unpaid Amount", f"₹{unpaid_amount:,.2f}", "red" if unpaid_amount > 0 else "green", 0, 2)

        # === GST SECTION - HORIZONTAL ===
        gst_section = ttk.LabelFrame(scrollable, text="💰 GST Summary", padding=15)
        gst_section.pack(fill='x', pady=(0, 15), padx=10)

        self.db.execute("SELECT COALESCE(SUM(total_gst), 0) FROM Sales_Orders")
        output_gst = self.db.fetchone()[0]

        self.db.execute("SELECT COALESCE(SUM(total_gst), 0) FROM Purchase_Orders")
        input_gst = self.db.fetchone()[0]

        net_gst = output_gst - input_gst

        stats_frame = ttk.Frame(gst_section)
        stats_frame.pack(fill='both', expand=True)

        for i in range(3):
            stats_frame.grid_columnconfigure(i, weight=1)
        stats_frame.grid_rowconfigure(0, weight=1)
    
        self.create_stat_card(stats_frame, "Output GST (Collected)", f"₹{output_gst:,.2f}", "green", 0, 0)
        self.create_stat_card(stats_frame, "Input GST (Paid)", f"₹{input_gst:,.2f}", "orange", 0, 1)
        self.create_stat_card(stats_frame, "Net GST Liability", f"₹{net_gst:,.2f}", "red" if net_gst > 0 else "blue", 0, 2)

        # Quick Actions - HORIZONTAL
        actions_section = ttk.LabelFrame(scrollable, text="⚡ Quick Actions", padding=15)
        actions_section.pack(fill='x', pady=(0, 15), padx=10)

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
        parent.grid_rowconfigure(row, weight=1)
    
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

    # ==================== COMPANY SETUP & DETAILS ====================
    
    def show_company_setup_wizard(self):
        """First-time setup wizard for company details"""
        wizard = tk.Toplevel(self.root)
        wizard.title("Welcome - Company Setup")
        wizard.geometry("700x750")
        wizard.resizable(True, True)
        
        # Make it modal
        wizard.transient(self.root)
        wizard.grab_set()
        
        # Prevent closing without completing setup
        wizard.protocol("WM_DELETE_WINDOW", lambda: None)
        
        # Header
        header_frame = ttk.Frame(wizard, padding=20)
        header_frame.pack(fill='x')
        
        ttk.Label(header_frame, text="🏭 Company Setup Wizard", 
                  font=('Arial', 18, 'bold')).pack()
        ttk.Label(header_frame, text="Let's set up your company details to get started", 
                  font=('Arial', 11), foreground='gray').pack(pady=5)
        
        ttk.Separator(wizard, orient='horizontal').pack(fill='x', padx=20, pady=10)
        
        # Scrollable form
        canvas = tk.Canvas(wizard)
        scrollbar = ttk.Scrollbar(wizard, orient="vertical", command=canvas.yview)
        form_frame = ttk.Frame(canvas)
        
        form_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=form_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=20)
        scrollbar.pack(side="right", fill="y")
        
        # Form fields
        fields = [
            ("Basic Information", None),
            ("Company Name:*", "company_name", True),
            ("Legal/Registered Name:", "legal_name", False),
            ("", None),
            ("Tax Information", None),
            ("GSTIN (GST Number):", "gstin", False),
            ("PAN Number:", "pan", False),
            ("", None),
            ("Address Details", None),
            ("Address Line 1:*", "address_line1", True),
            ("Address Line 2:", "address_line2", False),
            ("City:*", "city", True),
            ("State:*", "state", True),
            ("PIN Code:*", "pincode", True),
            ("Country:", "country", False),
            ("", None),
            ("Contact Information", None),
            ("Phone Number:*", "phone", True),
            ("Email Address:*", "email", True),
            ("Website:", "website", False),
            ("", None),
            ("Financial Settings", None),
            ("Financial Year Start (MM-DD):", "fy_start", False)
        ]
        
        entries = {}
        row = 0
        
        for field in fields:
            if field[1] is None:
                if field[0]:  # Section header
                    ttk.Label(form_frame, text=field[0], 
                             font=('Arial', 12, 'bold'), 
                             foreground='#2c3e50').grid(row=row, column=0, columnspan=2, 
                                                       sticky='w', padx=10, pady=(15, 5))
                else:  # Empty space
                    ttk.Label(form_frame, text="").grid(row=row, column=0, pady=5)
                row += 1
                continue
            
            label_text, key, required = field
            
            ttk.Label(form_frame, text=label_text, 
                     font=('Arial', 10, 'bold' if required else 'normal')).grid(
                row=row, column=0, padx=10, pady=8, sticky='w')
            
            entry = ttk.Entry(form_frame, width=40)
            
            # Set default values
            if key == "country":
                entry.insert(0, "India")
            elif key == "fy_start":
                entry.insert(0, "04-01")  # April 1st default
            
            entry.grid(row=row, column=1, padx=10, pady=8, sticky='ew')
            entries[key] = entry
            row += 1
        
        form_frame.grid_columnconfigure(1, weight=1)
        
        # Buttons at TOP - FIXED position
        btn_frame = ttk.Frame(wizard, padding=15)
        btn_frame.pack(fill='x', before=canvas)  # <-- Add before=canvas

        # Info note (move after button frame definition, before validate function)
        info_frame = ttk.Frame(wizard, padding=10)
        info_frame.pack(fill='x', padx=20, before=canvas)  # <-- Add before=canvas

        ttk.Label(info_frame, text="* Required fields", 
             font=('Arial', 9), foreground='red').pack(anchor='w')
        ttk.Label(info_frame, text="ℹ️ You can edit these details later from Masters > Company Details", 
             font=('Arial', 9), foreground='blue').pack(anchor='w', pady=2)
        
        def validate_and_save():
            """Validate and save company details"""
            # Validate required fields
            required_fields = {
                'company_name': 'Company Name',
                'address_line1': 'Address Line 1',
                'city': 'City',
                'state': 'State',
                'pincode': 'PIN Code',
                'phone': 'Phone Number',
                'email': 'Email Address'
            }
            
            for key, label in required_fields.items():
                if not entries[key].get().strip():
                    messagebox.showerror("Required Field", f"{label} is required")
                    entries[key].focus()
                    return
            
            # Validate email format
            email = entries['email'].get().strip()
            if '@' not in email or '.' not in email:
                messagebox.showwarning("Invalid Email", "Please enter a valid email address")
                entries['email'].focus()
                return
            
            # Validate GSTIN format if provided
            gstin = entries['gstin'].get().strip()
            if gstin and len(gstin) != 15:
                messagebox.showwarning("Invalid GSTIN", 
                                     "GSTIN should be 15 characters long")
                entries['gstin'].focus()
                return
            
            # Validate PAN format if provided
            pan = entries['pan'].get().strip().upper()
            if pan and len(pan) != 10:
                messagebox.showwarning("Invalid PAN", 
                                     "PAN should be 10 characters long")
                entries['pan'].focus()
                return
            
            try:
                # Save company details
                details = (
                    entries['company_name'].get().strip(),
                    entries['legal_name'].get().strip() or None,
                    entries['gstin'].get().strip().upper() or None,
                    entries['pan'].get().strip().upper() or None,
                    entries['address_line1'].get().strip(),
                    entries['address_line2'].get().strip() or None,
                    entries['city'].get().strip(),
                    entries['state'].get().strip(),
                    entries['pincode'].get().strip(),
                    entries['country'].get().strip() or 'India',
                    entries['phone'].get().strip(),
                    entries['email'].get().strip(),
                    entries['website'].get().strip() or None,
                    entries['fy_start'].get().strip() or '04-01'
                )
                
                self.db.save_company_details(details)
                
                messagebox.showinfo("Setup Complete", 
                                  f"Welcome to {entries['company_name'].get()}!\n\n"
                                  "Your company details have been saved.\n"
                                  "The application will now start.")
                
                wizard.destroy()
                
                # Now initialize the main application
                self.initialize_main_app()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save company details: {str(e)}")
        
        ttk.Button(btn_frame, text="✅ Complete Setup & Start", 
                  command=validate_and_save, width=30).pack(side='right', padx=5)
        ttk.Label(btn_frame, text="Setup must be completed to use the application", 
                 font=('Arial', 9), foreground='gray').pack(side='left')
    
    def show_company_details(self):
        """View and edit company details"""
        company = self.db.get_company_details()
        
        if not company:
            messagebox.showerror("Error", "Company details not found")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Company Details")
        dialog.geometry("700x750")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Header
        header_frame = ttk.Frame(dialog, padding=15)
        header_frame.pack(fill='x')
        
        ttk.Label(header_frame, text="🏭 Company Details", 
                 font=('Arial', 16, 'bold')).pack()
        ttk.Label(header_frame, text=f"Created: {company[16]} | Last Updated: {company[17]}", 
                 font=('Arial', 9), foreground='gray').pack(pady=3)
        
        ttk.Separator(dialog, orient='horizontal').pack(fill='x', padx=10, pady=5)
        
        # Scrollable content
        canvas = tk.Canvas(dialog)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        content_frame = ttk.Frame(canvas)
        
        content_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=content_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10)
        scrollbar.pack(side="right", fill="y")
        
        # Map database columns to display
        fields = [
            ("Basic Information", None, None),
            ("Company Name:", company[1], "company_name"),
            ("Legal Name:", company[2], "legal_name"),
            ("", None, None),
            ("Tax Information", None, None),
            ("GSTIN:", company[3], "gstin"),
            ("PAN:", company[4], "pan"),
            ("", None, None),
            ("Address", None, None),
            ("Address Line 1:", company[5], "address_line1"),
            ("Address Line 2:", company[6], "address_line2"),
            ("City:", company[7], "city"),
            ("State:", company[8], "state"),
            ("PIN Code:", company[9], "pincode"),
            ("Country:", company[10], "country"),
            ("", None, None),
            ("Contact Information", None, None),
            ("Phone:", company[11], "phone"),
            ("Email:", company[12], "email"),
            ("Website:", company[13], "website"),
            ("", None, None),
            ("Financial Settings", None, None),
            ("Financial Year Start:", company[15], "fy_start")
        ]
        
        entries = {}
        row = 0
        
        for field in fields:
            if field[1] is None:
                if field[0]:  # Section header
                    ttk.Label(content_frame, text=field[0], 
                             font=('Arial', 12, 'bold'), 
                             foreground='#2c3e50').grid(row=row, column=0, columnspan=2, 
                                                       sticky='w', padx=10, pady=(15, 5))
                else:  # Empty space
                    ttk.Label(content_frame, text="").grid(row=row, column=0, pady=5)
                row += 1
                continue
            
            label_text, value, key = field
            
            ttk.Label(content_frame, text=label_text, 
                     font=('Arial', 10, 'bold')).grid(row=row, column=0, 
                                                      padx=10, pady=6, sticky='w')
            
            entry = ttk.Entry(content_frame, width=40)
            entry.insert(0, value or "")
            entry.grid(row=row, column=1, padx=10, pady=6, sticky='ew')
            entries[key] = entry
            row += 1
        
        content_frame.grid_columnconfigure(1, weight=1)
        
        # Buttons at TOP - FIXED position
        btn_frame = ttk.Frame(dialog, padding=10)
        btn_frame.pack(fill='x', before=canvas)  # <-- Add before=canvas

        # Info notes
        info_frame = ttk.Frame(dialog, padding=10)
        info_frame.pack(fill='x', before=canvas)  # <-- Add before=canvas

        ttk.Label(info_frame, text="ℹ️ Some fields like GSTIN and PAN should match government records", 
           font=('Arial', 9), foreground='blue').pack(anchor='w')
        ttk.Label(info_frame, text="⚠️ Company name changes may affect reports and invoices", 
             font=('Arial', 9), foreground='orange').pack(anchor='w', pady=2)
        
        def save_changes():
            """Save updated company details"""
            # Validate required fields
            if not entries['company_name'].get().strip():
                messagebox.showerror("Error", "Company Name is required")
                return
            
            if not entries['email'].get().strip() or '@' not in entries['email'].get():
                messagebox.showerror("Error", "Valid email is required")
                return
            
            # Confirm changes
            if not messagebox.askyesno("Confirm Changes", 
                                      "Are you sure you want to update company details?"):
                return
            
            try:
                details = (
                    entries['company_name'].get().strip(),
                    entries['legal_name'].get().strip() or None,
                    entries['gstin'].get().strip().upper() or None,
                    entries['pan'].get().strip().upper() or None,
                    entries['address_line1'].get().strip(),
                    entries['address_line2'].get().strip() or None,
                    entries['city'].get().strip(),
                    entries['state'].get().strip(),
                    entries['pincode'].get().strip(),
                    entries['country'].get().strip() or 'India',
                    entries['phone'].get().strip(),
                    entries['email'].get().strip(),
                    entries['website'].get().strip() or None,
                    entries['fy_start'].get().strip() or '04-01'
                )
                
                self.db.save_company_details(details)
                messagebox.showinfo("Success", "Company details updated successfully!")
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update: {str(e)}")
        
        ttk.Button(btn_frame, text="💾 Save Changes", 
                  command=save_changes).pack(side='right', padx=5)
        ttk.Button(btn_frame, text="❌ Cancel", 
                  command=dialog.destroy).pack(side='right', padx=5)


if __name__ == "__main__":
    root = tk.Tk()

    # Global scaling (THIS fixes small text everywhere)
    root.tk.call("tk", "scaling", UI_SCALING)

    # Treeview readability
    style = ttk.Style()
    style.configure("Treeview", font=BASE_FONT, rowheight=28)
    style.configure("Treeview.Heading", font=(BASE_FONT[0], BASE_FONT[1], "bold"))

    app = IntegratedManagementSystem(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
