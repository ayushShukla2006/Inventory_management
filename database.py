"""
Database Module - Updated with GST Support for India
"""

import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_name='integrated_system.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.init_tables()
    
    def init_tables(self):
        """Initialize all database tables with GST support"""
        # COMPANY DETAILS TABLE (for company information)
        # FIXED: Removed CHECK constraint from column definition
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Company_Details (
                id INTEGER PRIMARY KEY,
                company_name TEXT NOT NULL,
                legal_name TEXT,
                gstin TEXT,
                pan TEXT,
                address_line1 TEXT,
                address_line2 TEXT,
                city TEXT,
                state TEXT,
                pincode TEXT,
                country TEXT DEFAULT 'India',
                phone TEXT,
                email TEXT,
                website TEXT,
                logo_path TEXT,
                financial_year_start TEXT,
                created_date DATE,
                last_updated DATE
            )
        ''')  
        # SHARED TABLES (used by both Purchase and Sales)
        
        # Items table - Now with GST rates
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Items (
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                category TEXT,
                unit_of_measure TEXT,
                purchase_rate REAL,
                purchase_gst_percent REAL DEFAULT 18.0,
                purchase_price REAL,
                selling_rate REAL,
                selling_gst_percent REAL DEFAULT 18.0,
                selling_price REAL,
                hsn_code TEXT
            )
        ''')
        
        # Inventory table
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
        
        # PURCHASE DEPARTMENT TABLES
        
        # Suppliers table - with GST details
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Suppliers (
                supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                contact_person TEXT,
                phone TEXT,
                email TEXT,
                address TEXT,
                gstin TEXT,
                payment_terms TEXT
            )
        ''')
        
        # Purchase Orders table - with GST breakdown
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Purchase_Orders (
                po_number INTEGER PRIMARY KEY AUTOINCREMENT,
                supplier_id INTEGER,
                order_date DATE,
                expected_delivery DATE,
                status TEXT DEFAULT 'Pending',
                subtotal REAL,
                total_gst REAL,
                total_amount REAL,
                FOREIGN KEY (supplier_id) REFERENCES Suppliers(supplier_id)
            )
        ''')
        
        # Purchase Order Items table - with GST per item
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Purchase_Order_Items (
                po_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                po_number INTEGER,
                item_id INTEGER,
                quantity INTEGER,
                rate REAL,
                gst_percent REAL,
                gst_amount REAL,
                total_price REAL,
                FOREIGN KEY (po_number) REFERENCES Purchase_Orders(po_number),
                FOREIGN KEY (item_id) REFERENCES Items(item_id)
            )
        ''')
        
        # Goods Receipt table
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
        
        # SALES DEPARTMENT TABLES
        
        # Customers table - with GST details
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Customers (
                customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                contact_person TEXT,
                phone TEXT,
                email TEXT,
                address TEXT,
                gstin TEXT,
                credit_limit REAL,
                payment_terms TEXT
            )
        ''')
        
        # Sales Orders table - with GST breakdown
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Sales_Orders (
                so_number INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                order_date DATE,
                delivery_date DATE,
                status TEXT DEFAULT 'Pending',
                subtotal REAL,
                total_gst REAL,
                total_amount REAL,
                FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
            )
        ''')
        
        # Sales Order Items table - with GST per item
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Sales_Order_Items (
                so_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                so_number INTEGER,
                item_id INTEGER,
                quantity INTEGER,
                rate REAL,
                gst_percent REAL,
                gst_amount REAL,
                total_price REAL,
                FOREIGN KEY (so_number) REFERENCES Sales_Orders(so_number),
                FOREIGN KEY (item_id) REFERENCES Items(item_id)
            )
        ''')
        
        # Invoices table - with GST breakdown
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Invoices (
                invoice_id INTEGER PRIMARY KEY AUTOINCREMENT,
                so_number INTEGER,
                customer_id INTEGER,
                invoice_date DATE,
                due_date DATE,
                subtotal REAL,
                total_gst REAL,
                total_amount REAL,
                status TEXT DEFAULT 'Unpaid',
                FOREIGN KEY (so_number) REFERENCES Sales_Orders(so_number),
                FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
            )
        ''')
        
        self.conn.commit()
    
    def execute(self, query, params=()):
        """Execute a query"""
        return self.cursor.execute(query, params)
    
    def fetchall(self):
        """Fetch all results"""
        return self.cursor.fetchall()
    
    def fetchone(self):
        """Fetch one result"""
        return self.cursor.fetchone()
    
    def commit(self):
        """Commit changes"""
        self.conn.commit()
    
    def lastrowid(self):
        """Get last inserted row ID"""
        return self.cursor.lastrowid
    
    def close(self):
        """Close database connection"""
        self.conn.close()
        
    def company_exists(self):
        """Check if company details exist"""
        self.cursor.execute("SELECT COUNT(*) FROM Company_Details WHERE id = 1")
        return self.cursor.fetchone()[0] > 0
    
    def get_company_details(self):
        """Get company details"""
        self.cursor.execute("SELECT * FROM Company_Details WHERE id = 1")
        return self.cursor.fetchone()
    
    def save_company_details(self, details):
        """Save or update company details
        
        Args:
            details: tuple of (company_name, legal_name, gstin, pan, 
                              address_line1, address_line2, city, state, pincode, country,
                              phone, email, website, financial_year_start)
        """
        if self.company_exists():
            # Update existing record
            self.cursor.execute('''
                UPDATE Company_Details SET
                    company_name=?, legal_name=?, gstin=?, pan=?,
                    address_line1=?, address_line2=?, city=?, state=?, pincode=?, country=?,
                    phone=?, email=?, website=?, financial_year_start=?, last_updated=?
                WHERE id = 1
            ''', details + (datetime.now().date(),))
        else:
            # Insert new record
            self.cursor.execute('''
                INSERT INTO Company_Details (
                    id, company_name, legal_name, gstin, pan,
                    address_line1, address_line2, city, state, pincode, country,
                    phone, email, website, logo_path, financial_year_start, 
                    created_date, last_updated
                ) VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, ?, ?, ?)
            ''', details + (datetime.now().date(), datetime.now().date()))
        
        self.conn.commit()