"""
Database Auto-Fill Script - Populate with Test Data
Run this script to fill an empty database with realistic test data
"""

import sqlite3
from datetime import datetime, timedelta
import random

def check_database_empty(db_name='integrated_system.db'):
    """Check if database exists and is empty"""
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        # Check if Items table has data
        cursor.execute("SELECT COUNT(*) FROM Items")
        item_count = cursor.fetchone()[0]
        
        conn.close()
        return item_count == 0
    except:
        return True  # Database doesn't exist or error occurred

def fill_database(db_name='integrated_system.db'):
    """Fill database with realistic test data"""
    
    # First initialize database structure
    from database import Database
    db = Database(db_name)
    
    print("🔄 Filling database with test data...")
    
    # ==================== ITEMS ====================
    print("📦 Adding items...")
    
    items = [
        # Electronics (18% GST)
        ("Laptop - Dell Inspiron 15", "15.6 inch, i5, 8GB RAM, 512GB SSD", "Electronics", "Piece", "12345", 
         35000, 18.0, 41300, 45000, 18.0, 53100, 25, 5, "Warehouse A"),
        ("Wireless Mouse - Logitech M331", "Silent clicking, 2.4GHz wireless", "Electronics", "Piece", "12346",
         450, 18.0, 531, 650, 18.0, 767, 50, 10, "Warehouse A"),
        ("USB-C Hub - 7-in-1", "HDMI, USB 3.0, SD card reader", "Electronics", "Piece", "12347",
         800, 18.0, 944, 1200, 18.0, 1416, 30, 8, "Warehouse A"),
        ("Mechanical Keyboard", "RGB backlit, Cherry MX switches", "Electronics", "Piece", "12348",
         2500, 18.0, 2950, 3800, 18.0, 4484, 20, 5, "Warehouse A"),
        ("LED Monitor 24 inch", "Full HD, IPS panel, 75Hz", "Electronics", "Piece", "12349",
         8000, 18.0, 9440, 11500, 18.0, 13570, 15, 3, "Warehouse B"),
        
        # Office Supplies (18% GST)
        ("A4 Paper Ream", "500 sheets, 75 GSM", "Office Supplies", "Ream", "23456",
         180, 18.0, 212.4, 280, 18.0, 330.4, 200, 30, "Warehouse C"),
        ("Ballpoint Pens - Pack of 10", "Blue ink, smooth writing", "Office Supplies", "Pack", "23457",
         60, 18.0, 70.8, 100, 18.0, 118, 150, 25, "Warehouse C"),
        ("Stapler - Heavy Duty", "50 sheet capacity", "Office Supplies", "Piece", "23458",
         250, 18.0, 295, 400, 18.0, 472, 40, 8, "Warehouse C"),
        ("Whiteboard Marker Set", "Pack of 4 colors", "Office Supplies", "Pack", "23459",
         120, 18.0, 141.6, 200, 18.0, 236, 80, 15, "Warehouse C"),
        ("File Folders - Pack of 25", "Legal size, assorted colors", "Office Supplies", "Pack", "23460",
         180, 18.0, 212.4, 300, 18.0, 354, 60, 12, "Warehouse C"),
        
        # Furniture (18% GST)
        ("Office Chair - Ergonomic", "Adjustable height, lumbar support", "Furniture", "Piece", "34567",
         4500, 18.0, 5310, 7000, 18.0, 8260, 12, 3, "Warehouse D"),
        ("Standing Desk", "Electric height adjustable", "Furniture", "Piece", "34568",
         15000, 18.0, 17700, 22000, 18.0, 25960, 8, 2, "Warehouse D"),
        ("Bookshelf - 5 Tier", "Wooden, dark brown finish", "Furniture", "Piece", "34569",
         3200, 18.0, 3776, 5000, 18.0, 5900, 10, 2, "Warehouse D"),
        
        # Beverages (12% GST)
        ("Coffee Powder - Premium Blend", "500g pack, Arabica beans", "Beverages", "Kg", "45678",
         280, 12.0, 313.6, 450, 12.0, 504, 100, 20, "Warehouse E"),
        ("Green Tea Bags - 100 count", "Organic, premium quality", "Beverages", "Box", "45679",
         180, 12.0, 201.6, 300, 12.0, 336, 80, 15, "Warehouse E"),
        
        # Snacks (12% GST)
        ("Biscuits - Assorted Pack", "500g variety pack", "Snacks", "Pack", "56789",
         120, 12.0, 134.4, 200, 12.0, 224, 150, 25, "Warehouse E"),
        ("Potato Chips - Family Pack", "200g, multiple flavors", "Snacks", "Pack", "56790",
         80, 12.0, 89.6, 140, 12.0, 156.8, 200, 30, "Warehouse E"),
        
        # Cleaning Supplies (18% GST)
        ("Floor Cleaner - 5L", "Multi-surface, lemon scent", "Cleaning", "Liter", "67890",
         350, 18.0, 413, 600, 18.0, 708, 50, 10, "Warehouse F"),
        ("Hand Sanitizer - 500ml", "70% alcohol, gel formula", "Cleaning", "Bottle", "67891",
         80, 18.0, 94.4, 150, 18.0, 177, 120, 20, "Warehouse F"),
        ("Tissue Paper - 200 pulls", "3-ply, soft and strong", "Cleaning", "Box", "67892",
         45, 18.0, 53.1, 80, 18.0, 94.4, 180, 30, "Warehouse F"),
        
        # Stationery (18% GST)
        ("Notebook - Hardbound A5", "200 pages, ruled", "Stationery", "Piece", "78901",
         85, 18.0, 100.3, 150, 18.0, 177, 90, 15, "Warehouse C"),
        ("Highlighter Set - 6 colors", "Chisel tip, vibrant colors", "Stationery", "Set", "78902",
         95, 18.0, 112.1, 160, 18.0, 188.8, 70, 12, "Warehouse C"),
        
        # Pantry Items (5% GST)
        ("Sugar - 1 Kg Pack", "Refined, granulated", "Pantry", "Kg", "89012",
         42, 5.0, 44.1, 70, 5.0, 73.5, 250, 40, "Warehouse E"),
        ("Salt - 1 Kg Pack", "Iodized, free-flow", "Pantry", "Kg", "89013",
         20, 5.0, 21, 35, 5.0, 36.75, 300, 50, "Warehouse E"),
        
        # IT Accessories (18% GST)
        ("HDMI Cable - 2m", "4K support, gold plated", "Electronics", "Piece", "90123",
         180, 18.0, 212.4, 320, 18.0, 377.6, 60, 10, "Warehouse A")
    ]
    
    for item in items:
        db.execute("""INSERT INTO Items (name, description, category, unit_of_measure, hsn_code,
            purchase_rate, purchase_gst_percent, purchase_price, 
            selling_rate, selling_gst_percent, selling_price) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", item[:11])
        item_id = db.lastrowid()
        
        # Add to inventory
        db.execute("INSERT INTO Inventory (item_id, quantity_on_hand, reorder_level, location, last_updated) VALUES (?, ?, ?, ?, ?)",
            (item_id, item[11], item[12], item[13], datetime.now()))
    
    db.commit()
    print(f"✅ Added {len(items)} items")
    
    # ==================== SUPPLIERS ====================
    print("🏢 Adding suppliers...")
    
    suppliers = [
        ("Tech Solutions Pvt Ltd", "Rajesh Kumar", "+91-9876543210", "rajesh@techsolutions.com",
         "123 MG Road, Bangalore, Karnataka 560001", "29ABCDE1234F1Z5", "Net 30"),
        ("Office Mart Supplies", "Priya Sharma", "+91-9876543211", "priya@officemart.com",
         "456 Park Street, Kolkata, West Bengal 700016", "19FGHIJ5678K2L6", "Net 45"),
        ("Furniture World", "Amit Patel", "+91-9876543212", "amit@furnitureworld.com",
         "789 FC Road, Pune, Maharashtra 411004", "27KLMNO9012P3Q7", "Net 30"),
        ("Green Beverages Co", "Sneha Reddy", "+91-9876543213", "sneha@greenbeverages.com",
         "321 Hitech City, Hyderabad, Telangana 500081", "36RSTUV3456W4X8", "Net 60"),
        ("Fresh Snacks Ltd", "Vikram Singh", "+91-9876543214", "vikram@freshsnacks.com",
         "654 Connaught Place, New Delhi 110001", "07YZABC7890D5E9", "Net 30"),
        ("Clean & Shine Products", "Meera Iyer", "+91-9876543215", "meera@cleanshine.com",
         "987 Anna Salai, Chennai, Tamil Nadu 600002", "33FGHIJ1234K6L0", "Net 45"),
        ("Smart Electronics Hub", "Arjun Mehta", "+91-9876543216", "arjun@smartelectronics.com",
         "147 Residency Road, Bangalore, Karnataka 560025", "29MNOPQ5678R7S1", "Net 30"),
        ("Stationery Express", "Kavya Nair", "+91-9876543217", "kavya@stationeryexpress.com",
         "258 Marine Drive, Mumbai, Maharashtra 400020", "27TUVWX9012Y8Z2", "Net 60"),
        ("Global Imports Trading", "Ravi Gupta", "+91-9876543218", "ravi@globalimports.com",
         "369 Salt Lake, Kolkata, West Bengal 700091", "19ABCDE3456F9G3", "Net 45"),
        ("Quality Office Solutions", "Ananya Das", "+91-9876543219", "ananya@qualityoffice.com",
         "741 Banjara Hills, Hyderabad, Telangana 500034", "36HIJKL7890M0N4", "Net 30")
    ]
    
    for supplier in suppliers:
        db.execute("INSERT INTO Suppliers (name, contact_person, phone, email, address, gstin, payment_terms) VALUES (?, ?, ?, ?, ?, ?, ?)", supplier)
    
    db.commit()
    print(f"✅ Added {len(suppliers)} suppliers")
    
    # ==================== CUSTOMERS ====================
    print("👥 Adding customers...")
    
    customers = [
        ("Acme Corporation", "Suresh Patel", "+91-9123456780", "suresh@acmecorp.com",
         "12 Industrial Area, Ahmedabad, Gujarat 380015", "24OPQRS1234T5U6", 500000, "Net 30"),
        ("BrightTech Solutions", "Neha Kapoor", "+91-9123456781", "neha@brighttech.com",
         "34 IT Park, Noida, Uttar Pradesh 201301", "09VWXYZ5678A6B7", 300000, "Net 45"),
        ("Creative Designs Studio", "Karan Malhotra", "+91-9123456782", "karan@creativedesigns.com",
         "56 Art District, Jaipur, Rajasthan 302001", "08CDEFG9012H7I8", 200000, "Net 30"),
        ("EduTech Institute", "Deepa Rao", "+91-9123456783", "deepa@edutech.com",
         "78 Knowledge Park, Bangalore, Karnataka 560100", "29JKLMN3456O8P9", 400000, "Net 60"),
        ("FinServe Banking Corp", "Aditya Khanna", "+91-9123456784", "aditya@finserve.com",
         "90 Business District, Mumbai, Maharashtra 400051", "27QRSTU7890V9W0", 1000000, "Net 45"),
        ("GreenLife Organic Foods", "Pooja Verma", "+91-9123456785", "pooja@greenlife.com",
         "23 Eco Plaza, Pune, Maharashtra 411001", "27XYZAB1234C0D1", 250000, "Net 30"),
        ("HealthCare Plus Hospital", "Dr. Rohit Sharma", "+91-9123456786", "rohit@healthcareplus.com",
         "45 Medical Hub, Chennai, Tamil Nadu 600001", "33EFGHI5678J1K2", 600000, "Net 60"),
        ("InfoSystems Ltd", "Sanjay Joshi", "+91-9123456787", "sanjay@infosystems.com",
         "67 Tech Tower, Hyderabad, Telangana 500032", "36LMNOP9012Q2R3", 350000, "Net 45"),
        ("JoyFul Retail Stores", "Ritu Agarwal", "+91-9123456788", "ritu@joyfulretail.com",
         "89 Shopping Complex, Kolkata, West Bengal 700001", "19STUVW3456X3Y4", 450000, "Net 30"),
        ("KnowledgeHub Library", "Manoj Kumar", "+91-9123456789", "manoj@knowledgehub.com",
         "12 Education Zone, Lucknow, Uttar Pradesh 226001", "09ZABCD7890E4F5", 150000, "Net 60"),
        ("LogiServe Warehousing", "Anjali Desai", "+91-9123456790", "anjali@logiserve.com",
         "34 Logistics Park, Surat, Gujarat 395007", "24GHIJK1234L5M6", 800000, "Net 45"),
        ("MegaMart Supermarket", "Vishal Reddy", "+91-9123456791", "vishal@megamart.com",
         "56 Retail Hub, Visakhapatnam, Andhra Pradesh 530001", "37NOPQR5678S6T7", 700000, "Net 30"),
        ("NexGen Startups Inc", "Priyanka Saxena", "+91-9123456792", "priyanka@nexgenstartups.com",
         "78 Innovation Center, Bangalore, Karnataka 560001", "29UVWXY9012Z7A8", 300000, "Net 60"),
        ("OmniTech Electronics", "Rahul Mishra", "+91-9123456793", "rahul@omnitech.com",
         "90 Electronic City, Gurgaon, Haryana 122001", "06BCDEF3456G8H9", 550000, "Net 45"),
        ("PrimeCare Hospitals", "Dr. Lakshmi Iyer", "+91-9123456794", "lakshmi@primecare.com",
         "23 Health Sector, Kochi, Kerala 682001", "32IJKLM7890N9O0", 900000, "Net 30")
    ]
    
    for customer in customers:
        db.execute("INSERT INTO Customers (name, contact_person, phone, email, address, gstin, credit_limit, payment_terms) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", customer)
    
    db.commit()
    print(f"✅ Added {len(customers)} customers")
    
    # ==================== PURCHASE ORDERS ====================
    print("🛒 Creating purchase orders...")
    
    # Create 15 purchase orders with varying statuses
    po_count = 0
    for i in range(15):
        supplier_id = random.randint(1, 10)
        order_date = datetime.now() - timedelta(days=random.randint(1, 90))
        expected_delivery = order_date + timedelta(days=random.randint(7, 30))
        
        # Select 2-5 random items
        num_items = random.randint(2, 5)
        selected_items = random.sample(range(1, 26), num_items)
        
        subtotal = 0
        total_gst = 0
        
        items_data = []
        for item_id in selected_items:
            db.execute("SELECT purchase_rate, purchase_gst_percent FROM Items WHERE item_id = ?", (item_id,))
            rate, gst_percent = db.fetchone()
            qty = random.randint(5, 30)
            
            item_subtotal = rate * qty
            item_gst = (item_subtotal * gst_percent) / 100
            item_total = item_subtotal + item_gst
            
            subtotal += item_subtotal
            total_gst += item_gst
            
            items_data.append((item_id, qty, rate, gst_percent, item_gst, item_total))
        
        total_amount = subtotal + total_gst
        
        # Vary statuses
        if i < 5:
            status = "Completed"
        elif i < 10:
            status = "Partially Received"
        else:
            status = "Pending"
        
        db.execute("INSERT INTO Purchase_Orders (supplier_id, order_date, expected_delivery, status, subtotal, total_gst, total_amount) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (supplier_id, order_date.date(), expected_delivery.date(), status, subtotal, total_gst, total_amount))
        po_number = db.lastrowid()
        
        for item_id, qty, rate, gst_percent, gst_amt, total in items_data:
            db.execute("INSERT INTO Purchase_Order_Items (po_number, item_id, quantity, rate, gst_percent, gst_amount, total_price) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (po_number, item_id, qty, rate, gst_percent, gst_amt, total))
        
        po_count += 1
    
    db.commit()
    print(f"✅ Created {po_count} purchase orders")
    
    # ==================== GOODS RECEIPTS ====================
    print("📥 Creating goods receipts...")
    
    # Create receipts for completed/partially received POs
    db.execute("SELECT po_number, supplier_id FROM Purchase_Orders WHERE status IN ('Completed', 'Partially Received')")
    pos_to_receive = db.fetchall()
    
    gr_count = 0
    for po_number, supplier_id in pos_to_receive:
        db.execute("SELECT item_id, quantity FROM Purchase_Order_Items WHERE po_number = ?", (po_number,))
        items = db.fetchall()
        
        invoice_num = f"INV-PO{po_number}-{random.randint(1000, 9999)}"
        receipt_date = datetime.now() - timedelta(days=random.randint(1, 60))
        
        for item_id, ordered_qty in items:
            received_qty = ordered_qty if random.random() > 0.2 else random.randint(int(ordered_qty * 0.7), ordered_qty)
            rejected_qty = random.randint(0, max(1, int(received_qty * 0.05)))
            accepted_qty = received_qty - rejected_qty
            
            db.execute("""INSERT INTO Goods_Receipt 
                (po_number, item_id, supplier_id, invoice_number, received_quantity, 
                accepted_quantity, rejected_quantity, receipt_date, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (po_number, item_id, supplier_id, invoice_num, received_qty, accepted_qty, 
                 rejected_qty, receipt_date.date(), "Quality checked and verified"))
            
            # Update inventory
            db.execute("UPDATE Inventory SET quantity_on_hand = quantity_on_hand + ?, last_updated = ? WHERE item_id = ?",
                (accepted_qty, datetime.now(), item_id))
            
            gr_count += 1
    
    db.commit()
    print(f"✅ Created {gr_count} goods receipt entries")
    
    # ==================== SALES ORDERS ====================
    print("🛍️ Creating sales orders...")
    
    so_count = 0
    for i in range(20):
        customer_id = random.randint(1, 15)
        order_date = datetime.now() - timedelta(days=random.randint(1, 60))
        delivery_date = order_date + timedelta(days=random.randint(7, 21))
        
        # Select 1-4 random items that have stock
        db.execute("SELECT item_id FROM Inventory WHERE quantity_on_hand > 10")
        available_items = [row[0] for row in db.fetchall()]
        
        if not available_items:
            continue
        
        num_items = random.randint(1, min(4, len(available_items)))
        selected_items = random.sample(available_items, num_items)
        
        subtotal = 0
        total_gst = 0
        
        items_data = []
        for item_id in selected_items:
            db.execute("SELECT selling_rate, selling_gst_percent, quantity_on_hand FROM Items i JOIN Inventory inv ON i.item_id = inv.item_id WHERE i.item_id = ?", (item_id,))
            rate, gst_percent, stock = db.fetchone()
            qty = random.randint(1, min(10, stock // 2))
            
            item_subtotal = rate * qty
            item_gst = (item_subtotal * gst_percent) / 100
            item_total = item_subtotal + item_gst
            
            subtotal += item_subtotal
            total_gst += item_gst
            
            items_data.append((item_id, qty, rate, gst_percent, item_gst, item_total))
        
        total_amount = subtotal + total_gst
        
        # Vary statuses
        if i < 8:
            status = "Delivered"
        elif i < 14:
            status = "Partially Delivered"
        else:
            status = "Pending"
        
        db.execute("INSERT INTO Sales_Orders (customer_id, order_date, delivery_date, status, subtotal, total_gst, total_amount) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (customer_id, order_date.date(), delivery_date.date(), status, subtotal, total_gst, total_amount))
        so_number = db.lastrowid()
        
        for item_id, qty, rate, gst_percent, gst_amt, total in items_data:
            db.execute("INSERT INTO Sales_Order_Items (so_number, item_id, quantity, rate, gst_percent, gst_amount, total_price) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (so_number, item_id, qty, rate, gst_percent, gst_amt, total))
            
            # Reduce inventory for delivered orders
            if status in ["Delivered", "Partially Delivered"]:
                reduce_qty = qty if status == "Delivered" else random.randint(int(qty * 0.5), qty)
                db.execute("UPDATE Inventory SET quantity_on_hand = quantity_on_hand - ?, last_updated = ? WHERE item_id = ?",
                    (reduce_qty, datetime.now(), item_id))
        
        so_count += 1
    
    db.commit()
    print(f"✅ Created {so_count} sales orders")
    
    # ==================== INVOICES ====================
    print("💰 Creating invoices...")
    
    # Create invoices for delivered sales orders
    db.execute("SELECT so_number, customer_id, subtotal, total_gst, total_amount, delivery_date FROM Sales_Orders WHERE status = 'Delivered'")
    delivered_orders = db.fetchall()
    
    inv_count = 0
    for so_number, customer_id, subtotal, total_gst, total_amount, delivery_date in delivered_orders:
        invoice_date = datetime.strptime(delivery_date, '%Y-%m-%d')
        due_date = invoice_date + timedelta(days=30)
        
        # 60% paid, 40% unpaid
        status = "Paid" if random.random() < 0.6 else "Unpaid"
        
        db.execute("""INSERT INTO Invoices (so_number, customer_id, invoice_date, due_date, 
            subtotal, total_gst, total_amount, status) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (so_number, customer_id, invoice_date.date(), due_date.date(), 
             subtotal, total_gst, total_amount, status))
        
        inv_count += 1
    
    db.commit()
    print(f"✅ Created {inv_count} invoices")
    
    db.close()
    print("\n🎉 Database filled successfully with test data!")
    print(f"\n📊 Summary:")
    print(f"   - Items: 25")
    print(f"   - Suppliers: 10")
    print(f"   - Customers: 15")
    print(f"   - Purchase Orders: {po_count}")
    print(f"   - Goods Receipts: {gr_count} entries")
    print(f"   - Sales Orders: {so_count}")
    print(f"   - Invoices: {inv_count}")

if __name__ == "__main__":
    print("=" * 60)
    print("DATABASE AUTO-FILL SCRIPT")
    print("=" * 60)
    
    db_name = 'integrated_system.db'
    
    if check_database_empty(db_name):
        print("\n✅ Database is empty or doesn't exist. Filling with test data...\n")
        fill_database(db_name)
    else:
        print("\n⚠️  Database already contains data.")
        print("Do you want to:")
        print("1. Keep existing data (Cancel)")
        print("2. Clear and refill with test data")
        
        choice = input("\nEnter choice (1 or 2): ").strip()
        
        if choice == "2":
            import os
            if os.path.exists(db_name):
                os.remove(db_name)
                print(f"\n🗑️  Deleted existing database")
            fill_database(db_name)
        else:
            print("\n✅ Keeping existing data. No changes made.")
    
    print("\n" + "=" * 60)
    print("Script completed. You can now run main.py")
    print("=" * 60)