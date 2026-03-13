# pharmacy_app.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime, timedelta
import os
import csv
import hashlib
import uuid
import platform
import shutil
from pathlib import Path
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np

class PharmacyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MERawi Pharmacy Pro - Complete Pharmacy Management System")
        self.root.geometry("1200x700")
        
        # Initialize data directories FIRST
        self.ensure_data_directories()
        
        # Configure style
        self.setup_styles()
        
        # Create database and tables
        self.create_database()
        
        # Create menu bar
        self.create_menu()
        
        # Create status bar
        self.create_status_bar()
        
        # Create main content area with notebook
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create tabs
        self.create_medicines_tab()
        self.create_sales_tab()
        self.create_reports_tab()
        self.create_dashboard_tab()
        
        # Load initial data
        self.load_medicines()
        self.check_alerts()
    
    # ========== DATA DIRECTORY MANAGEMENT ==========
    
    def get_app_data_dir(self):
        """Get the appropriate application data directory for all platforms"""
        system = platform.system()
        
        if system == "Windows":
            base_dir = os.path.join(os.environ['LOCALAPPDATA'], 'MERawiPharmacy')
        elif system == "Darwin":  # macOS
            base_dir = os.path.join(str(Path.home()), 'Library', 'Application Support', 'MERawiPharmacy')
        else:  # Linux
            base_dir = os.path.join(str(Path.home()), '.local', 'share', 'MERawiPharmacy')
        
        os.makedirs(base_dir, exist_ok=True)
        return base_dir
    
    def get_database_path(self):
        """Get the database file path"""
        return os.path.join(self.get_app_data_dir(), 'pharmacy.db')
    
    def get_license_path(self):
        """Get license file path"""
        return os.path.join(self.get_app_data_dir(), 'license.key')
    
    def get_backups_dir(self):
        """Get the backups directory"""
        backups_dir = os.path.join(self.get_app_data_dir(), 'backups')
        os.makedirs(backups_dir, exist_ok=True)
        return backups_dir
    
    def get_receipts_dir(self):
        """Get the receipts directory"""
        receipts_dir = os.path.join(self.get_app_data_dir(), 'receipts')
        os.makedirs(receipts_dir, exist_ok=True)
        return receipts_dir
    
    def get_exports_dir(self):
        """Get the exports directory"""
        exports_dir = os.path.join(self.get_app_data_dir(), 'exports')
        os.makedirs(exports_dir, exist_ok=True)
        return exports_dir
    
    def ensure_data_directories(self):
        """Create all necessary data directories"""
        self.get_app_data_dir()
        self.get_backups_dir()
        self.get_receipts_dir()
        self.get_exports_dir()
    
    def show_data_location(self):
        """Show where data is stored"""
        data_dir = self.get_app_data_dir()
        
        message = f"📍 DATA STORAGE LOCATION\n\n"
        message += f"All your pharmacy data is stored at:\n{data_dir}\n\n"
        message += f"Contents:\n"
        message += f"• pharmacy.db - Main database\n"
        message += f"• license.key - License activation\n"
        message += f"• backups/ - Excel backup files\n"
        message += f"• receipts/ - Saved receipts\n"
        message += f"• exports/ - Imported files\n\n"
        message += f"This location is NOT affected when you update the app.\n"
        message += f"Your data is safe even if you uninstall the app!"
        
        if messagebox.askyesno("📍 Data Location", message + "\n\nOpen this folder?"):
            if platform.system() == "Windows":
                os.startfile(data_dir)
            else:
                os.system(f'open "{data_dir}"')
    
    # ========== LICENSE MANAGEMENT ==========
    
    def check_license(self):
        """Professional license check"""
        license_file = self.get_license_path()
        
        # If license file exists, app is activated
        if os.path.exists(license_file):
            return True
        
        # No license - show purchase dialog
        # Don't hide anything yet
        result = self.show_purchase_dialog()
        return result

    def show_purchase_dialog(self):
        """Professional purchase dialog with scrollbar"""
        # Create dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("License Activation")
        dialog.geometry("550x650")
        dialog.configure(bg='#f5f5f5')
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Center window
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (550 // 2)
        y = (dialog.winfo_screenheight() // 2) - (650 // 2)
        dialog.geometry(f'+{x}+{y}')
        
        # Bring to front
        dialog.lift()
        dialog.focus_force()
        
        # Variable to track activation
        activated = tk.BooleanVar(value=False)
        
        # Create canvas and scrollbar
        canvas = tk.Canvas(dialog, bg='#f5f5f5', highlightthickness=0)
        scrollbar = tk.Scrollbar(dialog, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f5f5f5')
        
        scrollable_frame.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), 'units')
        
        scrollable_frame.bind('<Enter>', lambda e: canvas.bind_all('<MouseWheel>', _on_mousewheel))
        scrollable_frame.bind('<Leave>', lambda e: canvas.unbind_all('<MouseWheel>'))
        
        # Pack canvas and scrollbar
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Main content frame
        main_frame = tk.Frame(scrollable_frame, bg='white', padx=30, pady=30)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Header
        tk.Label(main_frame, text="🔒", bg='white', font=('Segoe UI', 40)).pack(pady=(0, 10))
        tk.Label(main_frame, text="MERawi PHARMACY PRO", bg='white', fg='#2c3e50',
                font=('Segoe UI', 18, 'bold')).pack()
        tk.Label(main_frame, text="License Required", bg='white', fg='#e67e22',
                font=('Segoe UI', 12)).pack(pady=(5, 20))
        
        # Computer ID
        id_frame = tk.Frame(main_frame, bg='#f8f9fa', padx=15, pady=15)
        id_frame.pack(fill='x', pady=10)
        
        tk.Label(id_frame, text="YOUR COMPUTER ID:", bg='#f8f9fa', fg='#2c3e50',
                font=('Segoe UI', 10, 'bold')).pack(anchor='w')
        
        computer_id = self.get_pc_fingerprint()
        
        id_display = tk.Entry(id_frame, font=('Courier', 11), bg='white', fg='#2c3e50',
                            relief='solid', bd=1)
        id_display.insert(0, computer_id)
        id_display.config(state='readonly')
        id_display.pack(fill='x', pady=5)
        
        def copy_id():
            dialog.clipboard_clear()
            dialog.clipboard_append(computer_id)
            copy_btn.config(text="✓ Copied!", bg='#27ae60')
            dialog.after(1500, lambda: copy_btn.config(text="📋 Copy Computer ID", bg='#3498db'))
        
        copy_btn = tk.Button(id_frame, text="📋 Copy Computer ID", bg='#3498db', fg='white',
                            font=('Segoe UI', 9), relief='flat', command=copy_id)
        copy_btn.pack(pady=5)
        
        tk.Label(id_frame, text="Send this ID to get your license key", bg='#f8f9fa', fg='#7f8c8d',
                font=('Segoe UI', 8, 'italic')).pack()
        
        # Contact information
        contact_frame = tk.Frame(main_frame, bg='#f8f9fa', padx=15, pady=15)
        contact_frame.pack(fill='x', pady=10)
        
        tk.Label(contact_frame, text="CONTACT FOR LICENSE", bg='#f8f9fa', fg='#2c3e50',
                font=('Segoe UI', 10, 'bold')).pack(pady=(0, 10))
        
        contacts = [
            ("Developer:", "Merawi Yohannes"),
            ("Phone 1:", "0921-540-245"),
            ("Phone 2:", "0960-633-549"),
            ("Email:", "merawiyohannes@gmail.com"),
        ]
        
        for label, value in contacts:
            frame = tk.Frame(contact_frame, bg='#f8f9fa')
            frame.pack(fill='x', pady=2)
            tk.Label(frame, text=label, bg='#f8f9fa', fg='#7f8c8d',
                    font=('Segoe UI', 9), width=10, anchor='w').pack(side='left')
            tk.Label(frame, text=value, bg='#f8f9fa', fg='#2c3e50',
                    font=('Segoe UI', 9)).pack(side='left')
        
        # Price
        price_frame = tk.Frame(main_frame, bg='#2c3e50', padx=15, pady=10)
        price_frame.pack(fill='x', pady=10)
        
        tk.Label(price_frame, text="15,000 ETB", bg='#2c3e50', fg='white',
                font=('Segoe UI', 18, 'bold')).pack()
        tk.Label(price_frame, text="One-time payment · Lifetime license", bg='#2c3e50', fg='#ecf0f1',
                font=('Segoe UI', 9)).pack()
        
        # License entry
        entry_frame = tk.Frame(main_frame, bg='white', padx=15, pady=15)
        entry_frame.pack(fill='x', pady=10)
        
        tk.Label(entry_frame, text="ENTER LICENSE KEY:", bg='white', fg='#2c3e50',
                font=('Segoe UI', 10, 'bold')).pack(anchor='w')
        
        key_entry = tk.Entry(entry_frame, width=25, font=('Courier', 11),
                            justify='center', relief='solid', bd=1)
        key_entry.pack(pady=5, ipady=5)
        key_entry.focus_set()
        
        def activate():
            key = key_entry.get().strip().upper()
            expected_key = self.generate_license_key(computer_id)
            
            if key == expected_key:
                with open(self.get_license_path(), 'w') as f:
                    f.write("activated")
                messagebox.showinfo("✅ Success", "License activated successfully!\n\nYour data is stored in:\n" + self.get_app_data_dir())
                activated.set(True)
                dialog.destroy()
            else:
                messagebox.showerror("❌ Error", "Invalid license key.\n\nPlease check and try again.")
                key_entry.delete(0, tk.END)
                key_entry.focus_set()
        
        def close_dialog():
            dialog.destroy()
            activated.set(False)
        
        # Buttons
        btn_frame = tk.Frame(main_frame, bg='white')
        btn_frame.pack(fill='x', pady=15)
        
        tk.Button(btn_frame, text="Activate License", bg='#2c3e50', fg='white',
                font=('Segoe UI', 10), padx=20, pady=8, relief='flat',
                command=activate).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="Exit", bg='#95a5a6', fg='white',
                font=('Segoe UI', 10), padx=20, pady=8, relief='flat',
                command=close_dialog).pack(side='left', padx=5)
        
        # Handle window close button
        dialog.protocol("WM_DELETE_WINDOW", close_dialog)
        
        # Wait for dialog to close
        self.root.wait_window(dialog)
        
        return activated.get()
    
    def get_pc_fingerprint(self):
        """Get unique computer ID"""
        fingerprint = str(uuid.getnode())
        return hashlib.md5(fingerprint.encode()).hexdigest()[:16].upper()
    
    def generate_license_key(self, computer_id):
        """Generate license key from computer ID"""
        secret = "MERAWI2026PRO"
        combined = computer_id + secret
        key = hashlib.md5(combined.encode()).hexdigest()[:16].upper()
        return f"{key[:4]}-{key[4:8]}-{key[8:12]}-{key[12:16]}"
    
   
    # ========== DATABASE MANAGEMENT ==========
    
    def create_database(self):
        """Create SQLite database and tables if they don't exist"""
        try:
            db_path = self.get_database_path()
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create medicines table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS medicines (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category TEXT,
                    manufacturer TEXT,
                    batch_number TEXT,
                    expiry_date TEXT,
                    quantity INTEGER DEFAULT 0,
                    purchase_price REAL DEFAULT 0,
                    selling_price REAL DEFAULT 0,
                    min_stock INTEGER DEFAULT 10,
                    location TEXT,
                    date_added TEXT,
                    UNIQUE(name, batch_number)
                )
            ''')
            
            # Create sales table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    medicine_id INTEGER,
                    medicine_name TEXT,
                    quantity INTEGER,
                    price_per_unit REAL,
                    total_price REAL,
                    sale_date TEXT,
                    customer_name TEXT,
                    FOREIGN KEY (medicine_id) REFERENCES medicines (id)
                )
            ''')
            
            conn.commit()
            conn.close()
            
            # Show welcome message (first time only)
            welcome_file = os.path.join(self.get_app_data_dir(), '.welcome_shown')
            if not os.path.exists(welcome_file):
                messagebox.showinfo("📍 Data Location", 
                                   f"Your pharmacy data will be stored at:\n\n{self.get_app_data_dir()}\n\n"
                                   f"This location is safe and won't be affected by app updates.\n"
                                   f"You can always find your data in File → Data Location")
                with open(welcome_file, 'w') as f:
                    f.write('welcome')
                    
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not create database:\n{str(e)}")
    
    def setup_styles(self):
        """Configure styles"""
        style = ttk.Style()
        style.configure('Treeview.Heading', font=('Segoe UI', 10, 'bold'))
        style.configure('Treeview', font=('Segoe UI', 9), rowheight=25)
    
    def create_status_bar(self):
        """Create status bar - visible on all pages"""
        status_frame = tk.Frame(self.root, bg='#34495e', height=30)
        status_frame.pack(side='bottom', fill='x')
        status_frame.pack_propagate(False)
        
        # Left side - Date & Version
        left_text = f"📅 {datetime.now().strftime('%Y-%m-%d')}  |  v1.0"
        tk.Label(status_frame, text=left_text, bg='#34495e', fg='#bdc3c7',
                font=('Segoe UI', 9)).pack(side='left', padx=15, pady=5)
        
        # Center - Developer Info
        center_text = "👨‍💻 Merawi Yohannes  |  📱 0921-540-245  |  📱 0960-633-549"
        tk.Label(status_frame, text=center_text, bg='#34495e', fg='white',
                font=('Segoe UI', 9, 'bold')).pack(side='left', padx=20, pady=5)
        
        # Right side - Location & Support
        right_text = "📍 Addis Ababa, Ethiopia  |  ⚕️ Support 24/7"
        tk.Label(status_frame, text=right_text, bg='#34495e', fg='#bdc3c7',
                font=('Segoe UI', 9)).pack(side='right', padx=15, pady=5)
    
    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="📁 File", menu=file_menu)
        file_menu.add_command(label="💾 Backup to Excel", command=self.backup_to_excel)
        file_menu.add_command(label="📂 Import from Excel", command=self.import_from_excel)
        file_menu.add_separator()
        file_menu.add_command(label="📍 Data Location", command=self.show_data_location)
        file_menu.add_separator()
        file_menu.add_command(label="🚪 Exit", command=self.root.quit)
        
        # Reports menu
        reports_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="📊 Reports", menu=reports_menu)
        reports_menu.add_command(label="⚠️ Low Stock Report", command=self.low_stock_report)
        reports_menu.add_command(label="⏰ Expiring Medicines", command=self.expiring_report)
        reports_menu.add_command(label="💰 Today's Sales", command=self.today_sales_report)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="❓ Help", menu=help_menu)
        help_menu.add_command(label="ℹ️ About", command=self.show_about)
    
    # ========== DASHBOARD TAB ==========
    
    def create_dashboard_tab(self):
        """Create professional dashboard with essential KPIs and charts"""
        self.dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_frame, text="📊 Dashboard")
        
        # Get comprehensive data
        conn = sqlite3.connect(self.get_database_path())
        cursor = conn.cursor()
        
        # ========== ESSENTIAL KPI DATA ==========
        
        # 1. Inventory Value (Most Important)
        cursor.execute('SELECT SUM(quantity * selling_price) FROM medicines')
        total_inventory_value = cursor.fetchone()[0] or 0
        
        # 2. Total Cost (What you paid)
        cursor.execute('SELECT SUM(quantity * purchase_price) FROM medicines')
        total_cost = cursor.fetchone()[0] or 0
        
        # 3. Potential Profit
        potential_profit = total_inventory_value - total_cost
        profit_margin = (potential_profit / total_inventory_value * 100) if total_inventory_value > 0 else 0
        
        # 4. Today's Sales
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute('SELECT SUM(total_price), COUNT(*) FROM sales WHERE sale_date LIKE ?', (f'{today}%',))
        today_data = cursor.fetchone()
        today_revenue = today_data[0] or 0
        today_transactions = today_data[1] or 0
        
        # 5. Total Products
        cursor.execute('SELECT COUNT(*) FROM medicines')
        total_products = cursor.fetchone()[0]
        
        # 6. Total Units in Stock
        cursor.execute('SELECT SUM(quantity) FROM medicines')
        total_units = cursor.fetchone()[0] or 0
        
        # 7. Low Stock Count
        cursor.execute('SELECT COUNT(*) FROM medicines WHERE quantity <= min_stock')
        low_stock = cursor.fetchone()[0]
        
        # 8. Expiring Soon Count & Value
        today_date = datetime.now().date()
        cursor.execute('SELECT expiry_date, quantity, selling_price FROM medicines')
        expiring_count = 0
        expiring_value = 0
        expiring_units = 0
        
        for exp, qty, price in cursor.fetchall():
            if exp and len(exp) == 10:
                try:
                    expiry = datetime.strptime(exp, '%Y-%m-%d').date()
                    days = (expiry - today_date).days
                    if 0 <= days <= 30:
                        expiring_count += 1
                        expiring_units += qty
                        expiring_value += qty * price
                except:
                    pass
        
        # 9. Expired Loss
        cursor.execute('SELECT expiry_date, quantity, purchase_price FROM medicines')
        expired_loss = 0
        expired_count = 0
        
        for exp, qty, cost in cursor.fetchall():
            if exp and len(exp) == 10:
                try:
                    expiry = datetime.strptime(exp, '%Y-%m-%d').date()
                    if expiry < today_date:
                        expired_count += 1
                        expired_loss += qty * cost
                except:
                    pass
        
        # 10. All-Time Sales
        cursor.execute('SELECT SUM(total_price), COUNT(*) FROM sales')
        all_sales = cursor.fetchone()
        total_revenue = all_sales[0] or 0
        total_transactions = all_sales[1] or 0
        
        # 11. Inventory Turnover Rate
        turnover_rate = (total_revenue / total_inventory_value) if total_inventory_value > 0 else 0
        
        # 12. Days of Inventory
        avg_daily_sales = total_revenue / 30 if total_revenue > 0 else 1
        days_of_inventory = total_inventory_value / avg_daily_sales if avg_daily_sales > 0 else 0
        
        # Category data for pie chart
        cursor.execute('''
            SELECT category, COUNT(*) as count, SUM(quantity) as total_qty 
            FROM medicines 
            WHERE category IS NOT NULL AND category != ''
            GROUP BY category 
            ORDER BY count DESC 
            LIMIT 5
        ''')
        categories = cursor.fetchall()
        
        # Expiry data for bar chart
        cursor.execute('SELECT expiry_date, quantity FROM medicines')
        expiry_status = {'Healthy': 0, 'Expiring Soon': 0, 'Expired': 0}
        
        for exp, qty in cursor.fetchall():
            if exp and len(exp) == 10:
                try:
                    expiry = datetime.strptime(exp, '%Y-%m-%d').date()
                    days = (expiry - today_date).days
                    if days < 0:
                        expiry_status['Expired'] += qty
                    elif days <= 30:
                        expiry_status['Expiring Soon'] += qty
                    else:
                        expiry_status['Healthy'] += qty
                except:
                    expiry_status['Healthy'] += qty
            else:
                expiry_status['Healthy'] += qty
        
        conn.close()
        
        # ========== DASHBOARD UI ==========
        
        # Header with refresh button
        header_frame = tk.Frame(self.dashboard_frame, bg='white', padx=20, pady=10)
        header_frame.pack(fill='x')
        
        tk.Label(header_frame, text="📊 BUSINESS INTELLIGENCE DASHBOARD", 
                bg='white', fg='#2c3e50', font=('Segoe UI', 16, 'bold')).pack(side='left')
        
        # Refresh button (NOW VISIBLE)
        refresh_btn = tk.Button(header_frame, text="🔄 Refresh", bg='#3498db', fg='white',
                            font=('Segoe UI', 10, 'bold'), padx=15, pady=5,
                            relief='flat', command=self.refresh_dashboard)
        refresh_btn.pack(side='right')
        
        # Hover effect
        def on_enter(e): refresh_btn['background'] = '#2980b9'
        def on_leave(e): refresh_btn['background'] = '#3498db'
        refresh_btn.bind('<Enter>', on_enter)
        refresh_btn.bind('<Leave>', on_leave)
        
        tk.Label(header_frame, text=f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                bg='white', fg='#7f8c8d', font=('Segoe UI', 9)).pack(anchor='w')
        
        # ========== TOP KPI CARDS (ESSENTIAL METRICS) ==========
        cards_frame = tk.Frame(self.dashboard_frame, bg='#f8f9fa', padx=15, pady=15)
        cards_frame.pack(fill='x')
        
        # Row 1: Financial KPIs
        row1 = tk.Frame(cards_frame, bg='#f8f9fa')
        row1.pack(fill='x', pady=2)
        
        # Card: Inventory Value
        card1 = tk.Frame(row1, bg='white', padx=10, pady=10, relief='ridge', bd=1)
        card1.pack(side='left', expand=True, fill='both', padx=2)
        tk.Label(card1, text="💰 INVENTORY VALUE", bg='white', fg='#7f8c8d',
                font=('Segoe UI', 8)).pack()
        tk.Label(card1, text=f"{total_inventory_value:,.0f}", bg='white', fg='#27ae60',
                font=('Segoe UI', 18, 'bold')).pack()
        tk.Label(card1, text="Birr", bg='white', fg='#95a5a6',
                font=('Segoe UI', 8)).pack()
        
        # Card: Potential Profit
        card2 = tk.Frame(row1, bg='white', padx=10, pady=10, relief='ridge', bd=1)
        card2.pack(side='left', expand=True, fill='both', padx=2)
        tk.Label(card2, text="📈 POTENTIAL PROFIT", bg='white', fg='#7f8c8d',
                font=('Segoe UI', 8)).pack()
        tk.Label(card2, text=f"{potential_profit:,.0f}", bg='white', fg='#f39c12',
                font=('Segoe UI', 18, 'bold')).pack()
        tk.Label(card2, text=f"Margin: {profit_margin:.1f}%", bg='white', fg='#95a5a6',
                font=('Segoe UI', 8)).pack()
        
        # Card: Today's Sales
        card3 = tk.Frame(row1, bg='white', padx=10, pady=10, relief='ridge', bd=1)
        card3.pack(side='left', expand=True, fill='both', padx=2)
        tk.Label(card3, text="📊 TODAY'S SALES", bg='white', fg='#7f8c8d',
                font=('Segoe UI', 8)).pack()
        tk.Label(card3, text=f"{today_revenue:,.0f}", bg='white', fg='#3498db',
                font=('Segoe UI', 18, 'bold')).pack()
        tk.Label(card3, text=f"{today_transactions} transactions", bg='white', fg='#95a5a6',
                font=('Segoe UI', 8)).pack()
        
        # Row 2: Operational KPIs
        row2 = tk.Frame(cards_frame, bg='#f8f9fa')
        row2.pack(fill='x', pady=2)
        
        # Card: Total Products
        card4 = tk.Frame(row2, bg='white', padx=10, pady=10, relief='ridge', bd=1)
        card4.pack(side='left', expand=True, fill='both', padx=2)
        tk.Label(card4, text="💊 TOTAL PRODUCTS", bg='white', fg='#7f8c8d',
                font=('Segoe UI', 8)).pack()
        tk.Label(card4, text=f"{total_products}", bg='white', fg='#2c3e50',
                font=('Segoe UI', 18, 'bold')).pack()
        tk.Label(card4, text=f"{int(total_units):,} units", bg='white', fg='#95a5a6',
                font=('Segoe UI', 8)).pack()
        
        # Card: Low Stock Alert
        card5 = tk.Frame(row2, bg='white', padx=10, pady=10, relief='ridge', bd=1)
        card5.pack(side='left', expand=True, fill='both', padx=2)
        tk.Label(card5, text="⚠️ LOW STOCK", bg='white', fg='#7f8c8d',
                font=('Segoe UI', 8)).pack()
        tk.Label(card5, text=f"{low_stock}", bg='white', fg='#e67e22',
                font=('Segoe UI', 18, 'bold')).pack()
        tk.Label(card5, text="items need reorder", bg='white', fg='#95a5a6',
                font=('Segoe UI', 8)).pack()
        
        # Card: Expiring Soon
        card6 = tk.Frame(row2, bg='white', padx=10, pady=10, relief='ridge', bd=1)
        card6.pack(side='left', expand=True, fill='both', padx=2)
        tk.Label(card6, text="⏰ EXPIRING SOON", bg='white', fg='#7f8c8d',
                font=('Segoe UI', 8)).pack()
        tk.Label(card6, text=f"{expiring_count}", bg='white', fg='#e74c3c',
                font=('Segoe UI', 18, 'bold')).pack()
        tk.Label(card6, text=f"{expiring_value:,.0f} Birr at risk", bg='white', fg='#95a5a6',
                font=('Segoe UI', 8)).pack()
        
        # Row 3: Performance KPIs
        row3 = tk.Frame(cards_frame, bg='#f8f9fa')
        row3.pack(fill='x', pady=2)
        
        # Card: Turnover Rate
        card7 = tk.Frame(row3, bg='white', padx=10, pady=10, relief='ridge', bd=1)
        card7.pack(side='left', expand=True, fill='both', padx=2)
        tk.Label(card7, text="🔄 TURNOVER RATE", bg='white', fg='#7f8c8d',
                font=('Segoe UI', 8)).pack()
        turnover_color = '#2ecc71' if turnover_rate >= 4 else '#f39c12' if turnover_rate >= 2 else '#e74c3c'
        tk.Label(card7, text=f"{turnover_rate:.2f}x", bg='white', fg=turnover_color,
                font=('Segoe UI', 18, 'bold')).pack()
        tk.Label(card7, text="Industry avg: 4-6x", bg='white', fg='#95a5a6',
                font=('Segoe UI', 8)).pack()
        
        # Card: Days of Inventory
        card8 = tk.Frame(row3, bg='white', padx=10, pady=10, relief='ridge', bd=1)
        card8.pack(side='left', expand=True, fill='both', padx=2)
        tk.Label(card8, text="📅 DAYS OF INVENTORY", bg='white', fg='#7f8c8d',
                font=('Segoe UI', 8)).pack()
        days_color = '#e74c3c' if days_of_inventory > 60 else '#f39c12' if days_of_inventory > 30 else '#2ecc71'
        tk.Label(card8, text=f"{days_of_inventory:.0f}", bg='white', fg=days_color,
                font=('Segoe UI', 18, 'bold')).pack()
        tk.Label(card8, text="days until stockout", bg='white', fg='#95a5a6',
                font=('Segoe UI', 8)).pack()
        
        # Card: Expired Loss
        card9 = tk.Frame(row3, bg='white', padx=10, pady=10, relief='ridge', bd=1)
        card9.pack(side='left', expand=True, fill='both', padx=2)
        tk.Label(card9, text="❌ EXPIRED LOSS", bg='white', fg='#7f8c8d',
                font=('Segoe UI', 8)).pack()
        tk.Label(card9, text=f"{expired_loss:,.0f}", bg='white', fg='#c0392b',
                font=('Segoe UI', 18, 'bold')).pack()
        tk.Label(card9, text=f"{expired_count} items", bg='white', fg='#95a5a6',
                font=('Segoe UI', 8)).pack()
        
        # ========== CHARTS SECTION ==========
        charts_frame = tk.Frame(self.dashboard_frame, bg='white', padx=15, pady=15)
        charts_frame.pack(fill='both', expand=True, pady=5)
        
        # Create figure for charts
        fig = Figure(figsize=(10, 4), dpi=100)
        fig.patch.set_facecolor('white')
        
        # Category Pie Chart
        ax1 = fig.add_subplot(121)
        if categories:
            cat_names = [c[0][:12] + '...' if len(c[0]) > 12 else c[0] for c in categories]
            cat_counts = [c[1] for c in categories]
            colors = plt.cm.Set3(np.linspace(0, 1, len(cat_names)))
            
            wedges, texts, autotexts = ax1.pie(cat_counts, labels=cat_names, autopct='%1.1f%%',
                                            colors=colors, startangle=90)
            
            for text in texts:
                text.set_fontsize(8)
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(8)
            
            ax1.set_title('Top Categories by Product Count', fontsize=11, fontweight='bold', pad=10)
        else:
            ax1.text(0.5, 0.5, 'No Category Data', ha='center', va='center')
            ax1.set_title('Categories', fontsize=11, fontweight='bold')
        
        # Expiry Bar Chart
        ax2 = fig.add_subplot(122)
        status_names = list(expiry_status.keys())
        status_values = list(expiry_status.values())
        bar_colors = ['#2ecc71', '#f39c12', '#e74c3c']
        
        bars = ax2.bar(status_names, status_values, color=bar_colors, width=0.6)
        ax2.set_title('Stock by Expiry Status', fontsize=11, fontweight='bold', pad=10)
        ax2.set_ylabel('Units', fontsize=9)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height):,}', ha='center', va='bottom', fontsize=8, fontweight='bold')
        
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.grid(axis='y', linestyle='--', alpha=0.3)
        
        plt.tight_layout()
        
        # Embed charts
        canvas = FigureCanvasTkAgg(fig, charts_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # ========== ALERT SUMMARY ==========
        alert_frame = tk.Frame(self.dashboard_frame, bg='#f8f9fa', padx=15, pady=10)
        alert_frame.pack(fill='x', pady=5)
        
        if low_stock > 0 or expiring_count > 0 or expired_count > 0:
            tk.Label(alert_frame, text="🔔 ACTION REQUIRED", bg='#f8f9fa', fg='#2c3e50',
                    font=('Segoe UI', 10, 'bold')).pack(anchor='w')
            
            if low_stock > 0:
                tk.Label(alert_frame, text=f"• ⚠️ {low_stock} products need reordering immediately",
                        bg='#f8f9fa', fg='#e67e22', font=('Segoe UI', 9)).pack(anchor='w')
            
            if expiring_count > 0:
                tk.Label(alert_frame, text=f"• ⏰ {expiring_count} products expiring soon ({expiring_value:,.0f} Birr at risk)",
                        bg='#f8f9fa', fg='#e74c3c', font=('Segoe UI', 9)).pack(anchor='w')
            
            if expired_count > 0:
                tk.Label(alert_frame, text=f"• ❌ {expired_count} products expired ({expired_loss:,.0f} Birr loss)",
                        bg='#f8f9fa', fg='#c0392b', font=('Segoe UI', 9)).pack(anchor='w')
        else:
            tk.Label(alert_frame, text="✅ All systems normal. No immediate action needed.",
                    bg='#f8f9fa', fg='#27ae60', font=('Segoe UI', 10)).pack()
    
    # ========== MEDICINES TAB ==========
    
    def create_medicines_tab(self):
        """Create medicines management tab"""
        self.medicines_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.medicines_frame, text="💊 Medicines")
        
        # Toolbar
        toolbar = tk.Frame(self.medicines_frame, bg='#ecf0f1', height=50)
        toolbar.pack(fill='x')
        toolbar.pack_propagate(False)
        
        tk.Button(toolbar, text="➕ Add Medicine", bg='#27ae60', fg='white',
                 font=('Segoe UI', 10), padx=10, command=self.add_medicine_dialog).pack(side='left', padx=5, pady=10)
        tk.Button(toolbar, text="✏️ Edit", bg='#2980b9', fg='white',
                 font=('Segoe UI', 10), padx=10, command=self.edit_medicine_dialog).pack(side='left', padx=5, pady=10)
        tk.Button(toolbar, text="🗑️ Delete", bg='#c0392b', fg='white',
                 font=('Segoe UI', 10), padx=10, command=self.delete_medicine).pack(side='left', padx=5, pady=10)
        tk.Button(toolbar, text="🔄 Refresh", bg='#f39c12', fg='white',
                 font=('Segoe UI', 10), padx=10, command=self.load_medicines).pack(side='left', padx=5, pady=10)
        tk.Button(toolbar, text="🔍 Test DB", bg='#9b59b6', fg='white',
                 font=('Segoe UI', 10), padx=10, command=self.test_database_contents).pack(side='left', padx=5, pady=10)
        
        # Search
        search_frame = tk.Frame(self.medicines_frame, bg='white', relief='groove', bd=2)
        search_frame.pack(fill='x', padx=5, pady=5)
        
        tk.Label(search_frame, text="🔍 Search:", bg='white', font=('Segoe UI', 10)).pack(side='left', padx=5)
        self.search_entry = tk.Entry(search_frame, width=40, font=('Segoe UI', 10))
        self.search_entry.pack(side='left', padx=5, pady=5)
        self.search_entry.bind('<KeyRelease>', self.search_medicines)
        
        tk.Button(search_frame, text="Clear", bg='#95a5a6', fg='white',
                 font=('Segoe UI', 9), command=self.clear_search).pack(side='left', padx=5)
        
        # Treeview
        columns = ('ID', 'Name', 'Category', 'Batch', 'Expiry', 'Qty', 'Price', 'Location', 'Status')
        self.medicines_tree = ttk.Treeview(self.medicines_frame, columns=columns, show='headings', height=18)
        
        widths = [50, 200, 100, 100, 100, 70, 100, 100, 100]
        for i, col in enumerate(columns):
            self.medicines_tree.heading(col, text=col)
            self.medicines_tree.column(col, width=widths[i])
        
        scrollbar = ttk.Scrollbar(self.medicines_frame, orient='vertical', command=self.medicines_tree.yview)
        self.medicines_tree.configure(yscrollcommand=scrollbar.set)
        
        self.medicines_tree.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        scrollbar.pack(side='right', fill='y')
        
        # Tags
        self.medicines_tree.tag_configure('expired', background='#ffcdd2')
        self.medicines_tree.tag_configure('expiring', background='#fff9c4')
        self.medicines_tree.tag_configure('lowstock', background='#ffe0b2')
    
    def load_medicines(self):
        """Load medicines into treeview"""
        for item in self.medicines_tree.get_children():
            self.medicines_tree.delete(item)
        
        try:
            conn = sqlite3.connect(self.get_database_path())
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM medicines ORDER BY name')
            medicines = cursor.fetchall()
            conn.close()
        except:
            medicines = []
        
        today = datetime.now().date()
        
        for med in medicines:
            status = "Good"
            tag = ''
            
            if med[5] and len(med[5]) == 10:
                try:
                    expiry = datetime.strptime(med[5], '%Y-%m-%d').date()
                    if expiry < today:
                        status = "EXPIRED"
                        tag = 'expired'
                    elif (expiry - today).days <= 30:
                        status = "Expiring Soon"
                        tag = 'expiring'
                except:
                    pass
            
            if status == "Good" and med[6] <= med[9]:
                status = "Low Stock"
                tag = 'lowstock'
            
            self.medicines_tree.insert('', 'end', values=(
                med[0], med[1], med[2] or "", med[4] or "", med[5] or "",
                med[6], f"{med[8]:.2f}", med[10] or "", status
            ), tags=(tag,))
    
    def search_medicines(self, event=None):
        """Search medicines"""
        search = self.search_entry.get().lower()
        
        for item in self.medicines_tree.get_children():
            self.medicines_tree.delete(item)
        
        try:
            conn = sqlite3.connect(self.get_database_path())
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM medicines WHERE LOWER(name) LIKE ? OR LOWER(category) LIKE ?',
                          (f'%{search}%', f'%{search}%'))
            medicines = cursor.fetchall()
            conn.close()
        except:
            medicines = []
        
        today = datetime.now().date()
        
        for med in medicines:
            status = "Good"
            tag = ''
            
            if med[5] and len(med[5]) == 10:
                try:
                    expiry = datetime.strptime(med[5], '%Y-%m-%d').date()
                    if expiry < today:
                        status = "EXPIRED"
                        tag = 'expired'
                    elif (expiry - today).days <= 30:
                        status = "Expiring Soon"
                        tag = 'expiring'
                except:
                    pass
            
            if status == "Good" and med[6] <= med[9]:
                status = "Low Stock"
                tag = 'lowstock'
            
            self.medicines_tree.insert('', 'end', values=(
                med[0], med[1], med[2] or "", med[4] or "", med[5] or "",
                med[6], f"{med[8]:.2f}", med[10] or "", status
            ), tags=(tag,))
    
    def clear_search(self):
        """Clear search"""
        self.search_entry.delete(0, tk.END)
        self.load_medicines()
    
    # ========== SALES TAB ==========
    
    def create_sales_tab(self):
        """Create sales tab"""
        self.sales_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.sales_frame, text="💰 Sales")
        
        # Tax rate
        tax_frame = tk.Frame(self.sales_frame, bg='#34495e', height=40)
        tax_frame.pack(fill='x')
        tax_frame.pack_propagate(False)
        
        tk.Label(tax_frame, text="Tax Rate:", bg='#34495e', fg='white',
                font=('Segoe UI', 10)).pack(side='left', padx=20, pady=8)
        
        self.tax_var = tk.StringVar(value="15")
        tax_combo = ttk.Combobox(tax_frame, textvariable=self.tax_var,
                                values=["0", "5", "10", "15"], width=5)
        tax_combo.pack(side='left', padx=5)
        tk.Label(tax_frame, text="%", bg='#34495e', fg='white').pack(side='left')
        
        # Main area
        paned = ttk.PanedWindow(self.sales_frame, orient='horizontal')
        paned.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Left panel
        left = tk.Frame(paned, bg='white', relief='groove', bd=1)
        paned.add(left, weight=1)
        
        tk.Label(left, text="🔍 Search Products", font=('Segoe UI', 11, 'bold'),
                bg='white', fg='#2c3e50').pack(pady=10)
        
        self.sale_search_entry = tk.Entry(left, width=30, font=('Segoe UI', 11))
        self.sale_search_entry.pack(pady=5)
        self.sale_search_entry.bind('<KeyRelease>', self.search_sale_medicines)
        
        self.search_listbox = tk.Listbox(left, height=8, font=('Segoe UI', 10))
        self.search_listbox.pack(fill='both', expand=True, padx=10, pady=10)
        self.search_listbox.bind('<<ListboxSelect>>', self.on_medicine_select)
        
        qty_frame = tk.Frame(left, bg='white')
        qty_frame.pack(pady=10)
        
        tk.Label(qty_frame, text="Quantity:", font=('Segoe UI', 10)).pack(side='left', padx=5)
        self.sale_qty = tk.Entry(qty_frame, width=10, font=('Segoe UI', 11))
        self.sale_qty.pack(side='left', padx=5)
        
        tk.Button(qty_frame, text="Add to Bill", bg='#27ae60', fg='white',
                 font=('Segoe UI', 10), padx=15, command=self.add_to_bill).pack(side='left', padx=5)
        
        # Right panel
        right = tk.Frame(paned, bg='white', relief='groove', bd=1)
        paned.add(right, weight=1)
        
        tk.Label(right, text="CURRENT BILL", font=('Segoe UI', 11, 'bold'),
                bg='white', fg='#2c3e50').pack(pady=10)
        
        columns = ('Item', 'Product', 'Price', 'Qty', 'Total')
        self.bill_tree = ttk.Treeview(right, columns=columns, show='headings', height=12)
        
        widths = [50, 200, 80, 50, 100]
        for i, col in enumerate(columns):
            self.bill_tree.heading(col, text=col)
            self.bill_tree.column(col, width=widths[i])
        
        self.bill_tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Summary
        summary = tk.Frame(right, bg='#f8f9fa', padx=15, pady=15)
        summary.pack(fill='x', padx=5, pady=5)
        
        subtotal_frame = tk.Frame(summary, bg='#f8f9fa')
        subtotal_frame.pack(fill='x', pady=2)
        tk.Label(subtotal_frame, text="Subtotal:", bg='#f8f9fa').pack(side='left')
        self.subtotal_label = tk.Label(subtotal_frame, text="0.00", bg='#f8f9fa', font=('Segoe UI', 10, 'bold'))
        self.subtotal_label.pack(side='right')
        
        tax_frame2 = tk.Frame(summary, bg='#f8f9fa')
        tax_frame2.pack(fill='x', pady=2)
        tk.Label(tax_frame2, text="VAT (15%):", bg='#f8f9fa').pack(side='left')
        self.tax_label = tk.Label(tax_frame2, text="0.00", bg='#f8f9fa', font=('Segoe UI', 10, 'bold'))
        self.tax_label.pack(side='right')
        
        tk.Frame(summary, bg='#bdc3c7', height=1).pack(fill='x', pady=5)
        
        total_frame = tk.Frame(summary, bg='#f8f9fa')
        total_frame.pack(fill='x', pady=2)
        tk.Label(total_frame, text="TOTAL:", bg='#f8f9fa', font=('Segoe UI', 12, 'bold')).pack(side='left')
        self.total_label = tk.Label(total_frame, text="0.00 Birr", bg='#f8f9fa',
                                   font=('Segoe UI', 14, 'bold'), fg='#27ae60')
        self.total_label.pack(side='right')
        
        # Buttons
        btn_frame = tk.Frame(right, bg='white')
        btn_frame.pack(fill='x', padx=5, pady=5)
        
        tk.Button(btn_frame, text="❌ Remove", bg='#e67e22', fg='white',
                 font=('Segoe UI', 9), command=self.remove_from_bill).pack(side='left', padx=2)
        tk.Button(btn_frame, text="🔄 Clear", bg='#7f8c8d', fg='white',
                 font=('Segoe UI', 9), command=self.clear_bill).pack(side='left', padx=2)
        tk.Button(btn_frame, text="✅ Complete Sale", bg='#27ae60', fg='white',
                 font=('Segoe UI', 10, 'bold'), padx=15, command=self.complete_sale).pack(side='right', padx=2)
        
        self.bill_items = []
    
    def search_sale_medicines(self, event=None):
        """Search medicines for sale"""
        search = self.sale_search_entry.get().lower()
        self.search_listbox.delete(0, tk.END)
        
        if len(search) < 2:
            return
        
        try:
            conn = sqlite3.connect(self.get_database_path())
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, selling_price, quantity, expiry_date
                FROM medicines
                WHERE LOWER(name) LIKE ? AND quantity > 0
                ORDER BY name
            ''', (f'%{search}%',))
            medicines = cursor.fetchall()
            conn.close()
        except:
            medicines = []
        
        today = datetime.now().date()
        
        for med in medicines:
            if med[4] and len(med[4]) == 10:
                try:
                    expiry = datetime.strptime(med[4], '%Y-%m-%d').date()
                    if expiry < today:
                        continue
                except:
                    pass
            
            self.search_listbox.insert(tk.END, f"{med[0]}|{med[1]}|{med[2]}")
    
    def on_medicine_select(self, event=None):
        """Handle medicine selection"""
        if self.search_listbox.curselection():
            self.sale_qty.focus()
    
    def add_to_bill(self):
        """Add to bill"""
        if not self.search_listbox.curselection():
            messagebox.showwarning("Warning", "Please select a medicine")
            return
        
        try:
            qty = int(self.sale_qty.get())
            if qty <= 0:
                messagebox.showerror("Error", "Quantity must be positive")
                return
        except:
            messagebox.showerror("Error", "Invalid quantity")
            return
        
        med_info = self.search_listbox.get(self.search_listbox.curselection()[0])
        med_id, name, price = med_info.split('|')
        med_id = int(med_id)
        price = float(price)
        
        try:
            conn = sqlite3.connect(self.get_database_path())
            cursor = conn.cursor()
            cursor.execute('SELECT quantity FROM medicines WHERE id = ?', (med_id,))
            available = cursor.fetchone()[0]
            conn.close()
        except:
            available = 0
        
        if qty > available:
            messagebox.showerror("Error", f"Only {available} available")
            return
        
        total = price * qty
        
        self.bill_items.append({
            'id': med_id,
            'name': name,
            'price': price,
            'qty': qty,
            'total': total
        })
        
        self.bill_tree.insert('', 'end', values=(len(self.bill_items), name, f"{price:.2f}", qty, f"{total:.2f}"))
        self.update_bill_total()
        
        self.sale_search_entry.delete(0, tk.END)
        self.sale_qty.delete(0, tk.END)
        self.search_listbox.delete(0, tk.END)
    
    def remove_from_bill(self):
        """Remove from bill"""
        if not self.bill_tree.selection():
            messagebox.showwarning("Warning", "Please select an item")
            return
        
        selected = self.bill_tree.selection()[0]
        item_id = int(self.bill_tree.item(selected)['values'][0]) - 1
        
        if 0 <= item_id < len(self.bill_items):
            self.bill_items.pop(item_id)
            self.refresh_bill_display()
    
    def refresh_bill_display(self):
        """Refresh bill display"""
        for item in self.bill_tree.get_children():
            self.bill_tree.delete(item)
        
        for i, item in enumerate(self.bill_items, 1):
            self.bill_tree.insert('', 'end', values=(
                i, item['name'], f"{item['price']:.2f}", item['qty'], f"{item['total']:.2f}"
            ))
        
        self.update_bill_total()
    
    def update_bill_total(self):
        """Update bill total"""
        subtotal = sum(item['total'] for item in self.bill_items)
        tax_rate = float(self.tax_var.get()) / 100
        tax = subtotal * tax_rate
        total = subtotal + tax
        
        self.subtotal_label.config(text=f"{subtotal:.2f}")
        self.tax_label.config(text=f"{tax:.2f}")
        self.total_label.config(text=f"{total:.2f} Birr")
    
    def clear_bill(self):
        """Clear bill"""
        self.bill_items = []
        for item in self.bill_tree.get_children():
            self.bill_tree.delete(item)
        self.update_bill_total()
    
    def complete_sale(self):
        """Complete sale"""
        if not self.bill_items:
            messagebox.showwarning("Warning", "No items in bill")
            return
        
        if not messagebox.askyesno("Confirm", "Complete this sale?"):
            return
        
        try:
            conn = sqlite3.connect(self.get_database_path())
            cursor = conn.cursor()
            
            sale_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            for item in self.bill_items:
                cursor.execute('''
                    INSERT INTO sales (medicine_id, medicine_name, quantity, price_per_unit, total_price, sale_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (item['id'], item['name'], item['qty'], item['price'], item['total'], sale_date))
                
                cursor.execute('UPDATE medicines SET quantity = quantity - ? WHERE id = ?',
                             (item['qty'], item['id']))
            
            conn.commit()
            conn.close()
            
            self.show_receipt()
            self.clear_bill()
            self.load_medicines()
            
        except Exception as e:
            messagebox.showerror("Error", f"Sale failed: {str(e)}")
    
    def show_receipt(self):
        """Show receipt"""
        receipt = tk.Toplevel(self.root)
        receipt.title("🧾 Receipt")
        receipt.geometry("400x600")
        receipt.configure(bg='white')
        
        # Header
        tk.Label(receipt, text="MERAWI PHARMACY PRO", bg='#2c3e50', fg='white',
                font=('Segoe UI', 14, 'bold'), pady=10).pack(fill='x')
        
        tk.Label(receipt, text="Tax Invoice", bg='white', fg='#34495e',
                font=('Segoe UI', 12)).pack()
        
        # Details
        details = tk.Frame(receipt, bg='white', padx=20, pady=10)
        details.pack(fill='x')
        
        receipt_no = f"R{datetime.now().strftime('%Y%m%d%H%M%S')}"
        tk.Label(details, text=f"Receipt No: {receipt_no}", bg='white',
                font=('Segoe UI', 9)).pack(anchor='w')
        tk.Label(details, text=f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                bg='white', font=('Segoe UI', 9)).pack(anchor='w')
        
        tk.Label(receipt, text="="*50, bg='white').pack()
        
        # Items
        text = tk.Text(receipt, height=15, width=45, bg='white', font=('Courier', 9))
        text.pack(padx=20, pady=10)
        
        text.insert('end', "\n")
        for item in self.bill_items:
            text.insert('end', f"{item['name'][:25]:25}\n")
            text.insert('end', f"  {item['qty']:3} x {item['price']:7.2f} = {item['total']:8.2f}\n")
        
        text.insert('end', "\n" + "-"*40 + "\n")
        
        subtotal = sum(item['total'] for item in self.bill_items)
        tax_rate = float(self.tax_var.get())
        tax = subtotal * (tax_rate/100)
        total = subtotal + tax
        
        text.insert('end', f"Subtotal: {subtotal:27.2f}\n")
        text.insert('end', f"VAT ({tax_rate}%): {tax:24.2f}\n")
        text.insert('end', "-"*40 + "\n")
        text.insert('end', f"TOTAL: {total:30.2f} Birr\n")
        text.insert('end', "="*40 + "\n")
        text.insert('end', "Thank you for your business!\n")
        
        text.config(state='disabled')
        
        # Buttons
        btn_frame = tk.Frame(receipt, bg='white')
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="💾 Save PDF", bg='#3498db', fg='white',
                 font=('Segoe UI', 10), command=lambda: self.save_receipt_pdf(text.get(1.0, 'end-1c'))).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="📄 Save Text", bg='#2ecc71', fg='white',
                 font=('Segoe UI', 10), command=lambda: self.save_receipt_text(text.get(1.0, 'end-1c'))).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="🖨️ Print", bg='#e67e22', fg='white',
                 font=('Segoe UI', 10), command=lambda: self.print_receipt(text.get(1.0, 'end-1c'))).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="❌ Close", bg='#e74c3c', fg='white',
                 font=('Segoe UI', 10), command=receipt.destroy).pack(side='left', padx=5)
    
    def save_receipt_pdf(self, receipt_text):
        """Save receipt as PDF"""
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            
            receipts_dir = self.get_receipts_dir()
            filename = f"receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join(receipts_dir, filename)
            
            doc = SimpleDocTemplate(filepath, pagesize=A4,
                                   rightMargin=72, leftMargin=72,
                                   topMargin=72, bottomMargin=18)
            
            styles = getSampleStyleSheet()
            story = []
            
            # Header
            header_style = ParagraphStyle('CustomHeader', parent=styles['Heading1'],
                                         fontSize=16, textColor=colors.HexColor('#2c3e50'),
                                         spaceAfter=30, alignment=1)
            story.append(Paragraph("MERawi PHARMACY PRO", header_style))
            story.append(Paragraph("Tax Invoice", styles['Heading2']))
            story.append(Spacer(1, 12))
            
            # Content
            content_style = ParagraphStyle('CustomBody', parent=styles['Normal'],
                                          fontSize=10, spaceAfter=6)
            
            for line in receipt_text.split('\n'):
                if line.strip():
                    story.append(Paragraph(line.replace(' ', '&nbsp;'), content_style))
            
            doc.build(story)
            
            messagebox.showinfo("✅ PDF Saved", f"Receipt saved as PDF:\n{filepath}")
            
            if messagebox.askyesno("Open Folder", "Open receipts folder?"):
                if platform.system() == "Windows":
                    os.startfile(receipts_dir)
                else:
                    os.system(f'open "{receipts_dir}"')
                    
        except ImportError:
            messagebox.showwarning("PDF Library Missing", 
                                 "PDF library not installed. Saving as text instead.\n\n"
                                 "To enable PDF: pip install reportlab")
            self.save_receipt_text(receipt_text)
        except Exception as e:
            messagebox.showerror("Error", f"Could not save PDF: {str(e)}")
    
    def save_receipt_text(self, receipt_text):
        """Save receipt as text"""
        receipts_dir = self.get_receipts_dir()
        filename = f"receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join(receipts_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(receipt_text)
        
        messagebox.showinfo("✅ Receipt Saved", f"Receipt saved:\n{filepath}")
        
        if messagebox.askyesno("Open Folder", "Open receipts folder?"):
            if platform.system() == "Windows":
                os.startfile(receipts_dir)
            else:
                os.system(f'open "{receipts_dir}"')
    
    def print_receipt(self, receipt_text):
        """Print receipt"""
        try:
            import tempfile
            import subprocess
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                f.write(receipt_text)
                temp_file = f.name
            
            if platform.system() == "Windows":
                os.startfile(temp_file, "print")
            elif platform.system() == "Darwin":
                subprocess.run(['lp', temp_file])
            else:
                subprocess.run(['lp', temp_file])
            
            messagebox.showinfo("🖨️ Printing", "Receipt sent to printer.")
            
        except Exception as e:
            messagebox.showerror("Print Error", f"Could not print: {str(e)}")
    
    # ========== REPORTS TAB ==========
    
    def create_reports_tab(self):
        """Create reports tab"""
        self.reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.reports_frame, text="📊 Reports")
        
        # Buttons
        btn_frame = tk.Frame(self.reports_frame, bg='#ecf0f1', height=60)
        btn_frame.pack(fill='x')
        btn_frame.pack_propagate(False)
        
        reports = [
            ("⚠️ Low Stock", '#e67e22', self.low_stock_report),
            ("⏰ Expiring", '#f39c12', self.expiring_report),
            ("💰 Today's Sales", '#27ae60', self.today_sales_report),
            ("📋 All Medicines", '#2980b9', self.all_medicines_report)
        ]
        
        for text, color, cmd in reports:
            tk.Button(btn_frame, text=text, bg=color, fg='white',
                     font=('Segoe UI', 11), padx=20, command=cmd).pack(side='left', padx=10, pady=15)
        
        # Text area
        container = tk.Frame(self.reports_frame)
        container.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.report_text = tk.Text(container, height=25, font=('Courier', 10),
                                  wrap='word', bg='white', fg='#2c3e50')
        scrollbar = ttk.Scrollbar(container, orient='vertical', command=self.report_text.yview)
        self.report_text.configure(yscrollcommand=scrollbar.set)
        
        self.report_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
    
    def low_stock_report(self):
        """Low stock report"""
        self.notebook.select(self.reports_frame)
        self.report_text.config(state='normal')
        self.report_text.delete(1.0, tk.END)
        
        try:
            conn = sqlite3.connect(self.get_database_path())
            cursor = conn.cursor()
            cursor.execute('SELECT name, quantity, min_stock, location FROM medicines WHERE quantity <= min_stock ORDER BY quantity')
            items = cursor.fetchall()
            conn.close()
        except:
            items = []
        
        self.report_text.insert('end', "⚠️ LOW STOCK REPORT\n")
        self.report_text.insert('end', "="*60 + "\n\n")
        self.report_text.insert('end', f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        
        if items:
            for item in items:
                self.report_text.insert('end', f"📦 {item[0]}\n")
                self.report_text.insert('end', f"   Stock: {item[1]} (Min: {item[2]})\n")
                self.report_text.insert('end', f"   Location: {item[3]}\n")
                self.report_text.insert('end', "-"*40 + "\n")
        else:
            self.report_text.insert('end', "✅ No low stock items\n")
        
        self.report_text.config(state='disabled')
    
    def expiring_report(self):
        """Expiring report"""
        self.notebook.select(self.reports_frame)
        self.report_text.config(state='normal')
        self.report_text.delete(1.0, tk.END)
        
        today = datetime.now().date()
        expiring = []
        
        try:
            conn = sqlite3.connect(self.get_database_path())
            cursor = conn.cursor()
            cursor.execute('SELECT name, expiry_date, quantity, location FROM medicines WHERE expiry_date IS NOT NULL')
            all_meds = cursor.fetchall()
            conn.close()
        except:
            all_meds = []
        
        for med in all_meds:
            if med[1] and len(med[1]) == 10:
                try:
                    expiry = datetime.strptime(med[1], '%Y-%m-%d').date()
                    days = (expiry - today).days
                    if 0 <= days <= 30:
                        expiring.append((med[0], med[1], days, med[2], med[3]))
                except:
                    pass
        
        expiring.sort(key=lambda x: x[2])
        
        self.report_text.insert('end', "⏰ EXPIRING MEDICINES (Next 30 Days)\n")
        self.report_text.insert('end', "="*60 + "\n\n")
        
        if expiring:
            for item in expiring:
                self.report_text.insert('end', f"💊 {item[0]}\n")
                self.report_text.insert('end', f"   Expires: {item[1]} (in {item[2]} days)\n")
                self.report_text.insert('end', f"   Quantity: {item[3]} at {item[4]}\n")
                self.report_text.insert('end', "-"*40 + "\n")
        else:
            self.report_text.insert('end', "✅ No medicines expiring soon\n")
        
        self.report_text.config(state='disabled')
    
    def today_sales_report(self):
        """Today's sales report"""
        self.notebook.select(self.reports_frame)
        self.report_text.config(state='normal')
        self.report_text.delete(1.0, tk.END)
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        try:
            conn = sqlite3.connect(self.get_database_path())
            cursor = conn.cursor()
            cursor.execute('SELECT medicine_name, quantity, price_per_unit, total_price, sale_date FROM sales WHERE sale_date LIKE ? ORDER BY sale_date', (f'{today}%',))
            items = cursor.fetchall()
            
            cursor.execute('SELECT SUM(total_price) FROM sales WHERE sale_date LIKE ?', (f'{today}%',))
            total = cursor.fetchone()[0] or 0
            conn.close()
        except:
            items = []
            total = 0
        
        self.report_text.insert('end', f"💰 SALES REPORT FOR {today}\n")
        self.report_text.insert('end', "="*60 + "\n\n")
        
        if items:
            for item in items:
                self.report_text.insert('end', f"💊 {item[0]}\n")
                self.report_text.insert('end', f"   {item[1]} x {item[2]:.2f} = {item[3]:.2f}\n")
                self.report_text.insert('end', f"   Time: {item[4].split()[1] if ' ' in item[4] else item[4]}\n")
                self.report_text.insert('end', "-"*40 + "\n")
            
            self.report_text.insert('end', f"\n📊 TOTAL SALES: {total:.2f} Birr\n")
        else:
            self.report_text.insert('end', "No sales today\n")
        
        self.report_text.config(state='disabled')
    
    def all_medicines_report(self):
        """All medicines report"""
        self.notebook.select(self.reports_frame)
        self.report_text.config(state='normal')
        self.report_text.delete(1.0, tk.END)
        
        try:
            conn = sqlite3.connect(self.get_database_path())
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM medicines ORDER BY name')
            medicines = cursor.fetchall()
            conn.close()
        except:
            medicines = []
        
        self.report_text.insert('end', "📋 COMPLETE INVENTORY\n")
        self.report_text.insert('end', "="*80 + "\n\n")
        self.report_text.insert('end', f"Total: {len(medicines)} products\n\n")
        
        for med in medicines:
            self.report_text.insert('end', f"ID: {med[0]} | {med[1]}\n")
            self.report_text.insert('end', f"Batch: {med[4] or 'N/A'} | Exp: {med[5] or 'N/A'}\n")
            self.report_text.insert('end', f"Stock: {med[6]} | Price: {med[8]:.2f} | Loc: {med[10] or 'N/A'}\n")
            self.report_text.insert('end', "-"*50 + "\n")
        
        self.report_text.config(state='disabled')

    def refresh_dashboard(self):
        """Refresh dashboard data"""
        # Remove current dashboard tab
        for i in range(self.notebook.index('end')):
            if self.notebook.tab(i, 'text') == "📊 Dashboard":
                self.notebook.forget(i)
                break
        
        # Create new dashboard tab
        self.create_dashboard_tab()
        
        # Select dashboard tab
        for i in range(self.notebook.index('end')):
            if self.notebook.tab(i, 'text') == "📊 Dashboard":
                self.notebook.select(i)
                break 
   
    # ========== MEDICINE DIALOGS ==========
    
    def add_medicine_dialog(self):
        """Add medicine dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("➕ Add Medicine")
        dialog.geometry("450x600")
        dialog.configure(bg='white')
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (dialog.winfo_screenheight() // 2) - (600 // 2)
        dialog.geometry(f'+{x}+{y}')
        
        tk.Label(dialog, text="Add New Medicine", bg='#2c3e50', fg='white',
                font=('Segoe UI', 14, 'bold'), pady=10).pack(fill='x')
        
        main = tk.Frame(dialog, bg='white', padx=20, pady=20)
        main.pack(fill='both', expand=True)
        
        fields = [
            ("Medicine Name:", True),
            ("Category:", False),
            ("Manufacturer:", False),
            ("Batch Number:", True),
            ("Expiry Date (YYYY-MM-DD):", False),
            ("Quantity:", False),
            ("Purchase Price:", False),
            ("Selling Price:", False),
            ("Minimum Stock Alert:", False),
            ("Location:", False)
        ]
        
        entries = {}
        
        for label, required in fields:
            frame = tk.Frame(main, bg='white')
            frame.pack(fill='x', pady=5)
            
            text = label + (" *" if required else "")
            tk.Label(frame, text=text, bg='white', font=('Segoe UI', 10),
                    width=20, anchor='w').pack(side='left')
            
            entry = tk.Entry(frame, font=('Segoe UI', 10), width=25)
            entry.pack(side='left', padx=5)
            entries[label] = entry
        
        entries["Minimum Stock Alert:"].insert(0, "10")
        entries["Quantity:"].insert(0, "0")
        
        def save():
            name = entries["Medicine Name:"].get().strip()
            if not name:
                messagebox.showerror("Error", "Medicine name is required")
                return
            
            try:
                conn = sqlite3.connect(self.get_database_path())
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO medicines (
                        name, category, manufacturer, batch_number, expiry_date,
                        quantity, purchase_price, selling_price, min_stock, location, date_added
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    name,
                    entries["Category:"].get().strip(),
                    entries["Manufacturer:"].get().strip(),
                    entries["Batch Number:"].get().strip(),
                    entries["Expiry Date (YYYY-MM-DD):"].get().strip(),
                    int(entries["Quantity:"].get() or 0),
                    float(entries["Purchase Price:"].get() or 0),
                    float(entries["Selling Price:"].get() or 0),
                    int(entries["Minimum Stock Alert:"].get() or 10),
                    entries["Location:"].get().strip(),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ))
                
                conn.commit()
                conn.close()
                
                dialog.destroy()
                self.load_medicines()
                messagebox.showinfo("Success", "Medicine added successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not save: {str(e)}")
        
        # Buttons
        btn_frame = tk.Frame(dialog, bg='white')
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Save", bg='#27ae60', fg='white',
                 font=('Segoe UI', 12), padx=30, command=save).pack(side='left', padx=10)
        tk.Button(btn_frame, text="Cancel", bg='#e74c3c', fg='white',
                 font=('Segoe UI', 12), padx=30, command=dialog.destroy).pack(side='left', padx=10)
    
    def edit_medicine_dialog(self):
        """Edit medicine dialog"""
        selected = self.medicines_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a medicine")
            return
        
        item = self.medicines_tree.item(selected[0])
        med_id = item['values'][0]
        
        try:
            conn = sqlite3.connect(self.get_database_path())
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM medicines WHERE id = ?', (med_id,))
            med = cursor.fetchone()
            conn.close()
        except:
            med = None
        
        if not med:
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("✏️ Edit Medicine")
        dialog.geometry("450x600")
        dialog.configure(bg='white')
        dialog.transient(self.root)
        dialog.grab_set()
        
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (dialog.winfo_screenheight() // 2) - (600 // 2)
        dialog.geometry(f'+{x}+{y}')
        
        tk.Label(dialog, text="Edit Medicine", bg='#2980b9', fg='white',
                font=('Segoe UI', 14, 'bold'), pady=10).pack(fill='x')
        
        main = tk.Frame(dialog, bg='white', padx=20, pady=20)
        main.pack(fill='both', expand=True)
        
        fields = [
            ("Medicine Name:", med[1]),
            ("Category:", med[2] or ""),
            ("Manufacturer:", med[3] or ""),
            ("Batch Number:", med[4] or ""),
            ("Expiry Date:", med[5] or ""),
            ("Quantity:", med[6]),
            ("Purchase Price:", med[7]),
            ("Selling Price:", med[8]),
            ("Minimum Stock Alert:", med[9]),
            ("Location:", med[10] or "")
        ]
        
        entries = {}
        
        for label, value in fields:
            frame = tk.Frame(main, bg='white')
            frame.pack(fill='x', pady=5)
            
            tk.Label(frame, text=label, bg='white', font=('Segoe UI', 10),
                    width=20, anchor='w').pack(side='left')
            
            entry = tk.Entry(frame, font=('Segoe UI', 10), width=25)
            entry.pack(side='left', padx=5)
            entry.insert(0, str(value))
            entries[label] = entry
        
        def update():
            try:
                conn = sqlite3.connect(self.get_database_path())
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE medicines SET
                        name = ?, category = ?, manufacturer = ?, batch_number = ?,
                        expiry_date = ?, quantity = ?, purchase_price = ?,
                        selling_price = ?, min_stock = ?, location = ?
                    WHERE id = ?
                ''', (
                    entries["Medicine Name:"].get(),
                    entries["Category:"].get(),
                    entries["Manufacturer:"].get(),
                    entries["Batch Number:"].get(),
                    entries["Expiry Date:"].get(),
                    int(entries["Quantity:"].get() or 0),
                    float(entries["Purchase Price:"].get() or 0),
                    float(entries["Selling Price:"].get() or 0),
                    int(entries["Minimum Stock Alert:"].get() or 10),
                    entries["Location:"].get(),
                    med_id
                ))
                conn.commit()
                conn.close()
                
                dialog.destroy()
                self.load_medicines()
                messagebox.showinfo("Success", "Medicine updated!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Update failed: {str(e)}")
        
        btn_frame = tk.Frame(dialog, bg='white')
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Update", bg='#2980b9', fg='white',
                 font=('Segoe UI', 12), padx=30, command=update).pack(side='left', padx=10)
        tk.Button(btn_frame, text="Cancel", bg='#e74c3c', fg='white',
                 font=('Segoe UI', 12), padx=30, command=dialog.destroy).pack(side='left', padx=10)
    
    def delete_medicine(self):
        """Delete medicine"""
        selected = self.medicines_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a medicine")
            return
        
        if messagebox.askyesno("Confirm", "Delete this medicine?"):
            item = self.medicines_tree.item(selected[0])
            med_id = item['values'][0]
            
            try:
                conn = sqlite3.connect(self.get_database_path())
                cursor = conn.cursor()
                cursor.execute('DELETE FROM medicines WHERE id = ?', (med_id,))
                conn.commit()
                conn.close()
                
                self.load_medicines()
                messagebox.showinfo("Success", "Medicine deleted")
                
            except Exception as e:
                messagebox.showerror("Error", f"Delete failed: {str(e)}")
    
    # ========== BACKUP & IMPORT ==========
    
    def backup_to_excel(self):
        """Backup to Excel"""
        backups_dir = self.get_backups_dir()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        try:
            conn = sqlite3.connect(self.get_database_path())
            cursor = conn.cursor()
            
            # Medicines
            cursor.execute('SELECT * FROM medicines')
            medicines = cursor.fetchall()
            
            med_file = os.path.join(backups_dir, f'medicines_{timestamp}.csv')
            with open(med_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Name', 'Category', 'Manufacturer', 'Batch', 'Expiry',
                               'Quantity', 'Purchase Price', 'Selling Price', 'Min Stock', 'Location', 'Date Added'])
                writer.writerows(medicines)
            
            # Sales
            cursor.execute('SELECT * FROM sales')
            sales = cursor.fetchall()
            
            sales_file = os.path.join(backups_dir, f'sales_{timestamp}.csv')
            with open(sales_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Medicine ID', 'Medicine Name', 'Quantity', 'Price/Unit',
                               'Total', 'Sale Date', 'Customer'])
                writer.writerows(sales)
            
            conn.close()
            
            messagebox.showinfo("✅ Backup Complete",
                              f"Backup saved to:\n{backups_dir}\n\n"
                              f"Files:\n{os.path.basename(med_file)}\n{os.path.basename(sales_file)}")
            
            if messagebox.askyesno("Open Folder", "Open backups folder?"):
                if platform.system() == "Windows":
                    os.startfile(backups_dir)
                else:
                    os.system(f'open "{backups_dir}"')
                    
        except Exception as e:
            messagebox.showerror("Error", f"Backup failed: {str(e)}")
    
    def import_from_excel(self):
        """Import from Excel"""
        filename = filedialog.askopenfilename(
            title="Select File",
            filetypes=[("Excel files", "*.csv *.xlsx"), ("All files", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            # Save copy
            exports_dir = self.get_exports_dir()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            import_copy = os.path.join(exports_dir, f"imported_{timestamp}_{os.path.basename(filename)}")
            shutil.copy2(filename, import_copy)
            
            conn = sqlite3.connect(self.get_database_path())
            cursor = conn.cursor()
            
            import_count = 0
            update_count = 0
            skip_count = 0
            
            if filename.lower().endswith('.csv'):
                with open(filename, 'r', encoding='utf-8-sig') as f:
                    reader = csv.reader(f)
                    next(reader)  # Skip header
                    
                    for row in reader:
                        if len(row) < 6:
                            skip_count += 1
                            continue
                        
                        try:
                            name = row[1].strip() if len(row) > 1 else ""
                            if not name:
                                skip_count += 1
                                continue
                            
                            category = row[2].strip() if len(row) > 2 else ""
                            manufacturer = row[3].strip() if len(row) > 3 else ""
                            batch = row[4].strip() if len(row) > 4 else ""
                            expiry = row[5].strip() if len(row) > 5 else ""
                            
                            try:
                                qty = int(float(row[6])) if len(row) > 6 and row[6] else 0
                            except:
                                qty = 0
                            
                            try:
                                purchase = float(row[7]) if len(row) > 7 and row[7] else 0
                            except:
                                purchase = 0
                            
                            try:
                                selling = float(row[8]) if len(row) > 8 and row[8] else 0
                            except:
                                selling = 0
                            
                            try:
                                min_stock = int(float(row[9])) if len(row) > 9 and row[9] else 10
                            except:
                                min_stock = 10
                            
                            location = row[10].strip() if len(row) > 10 else ""
                            
                            # Check if exists
                            cursor.execute('SELECT id, quantity FROM medicines WHERE name = ? AND batch_number = ?',
                                         (name, batch))
                            existing = cursor.fetchone()
                            
                            if existing:
                                new_qty = existing[1] + qty
                                cursor.execute('''
                                    UPDATE medicines SET quantity = ?, purchase_price = ?,
                                    selling_price = ?, expiry_date = ?, location = ?
                                    WHERE id = ?
                                ''', (new_qty, purchase, selling, expiry, location, existing[0]))
                                update_count += 1
                            else:
                                cursor.execute('''
                                    INSERT INTO medicines (name, category, manufacturer, batch_number,
                                    expiry_date, quantity, purchase_price, selling_price, min_stock, location, date_added)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (name, category, manufacturer, batch, expiry, qty, purchase,
                                     selling, min_stock, location, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                                import_count += 1
                                
                        except Exception as e:
                            skip_count += 1
                            continue
            
            elif filename.lower().endswith('.xlsx'):
                from openpyxl import load_workbook
                wb = load_workbook(filename, data_only=True)
                sheet = wb.active
                
                for row in sheet.iter_rows(min_row=2, values_only=True):
                    if not row or not any(row):
                        continue
                    
                    try:
                        name = str(row[1]) if len(row) > 1 and row[1] else ""
                        if not name:
                            skip_count += 1
                            continue
                        
                        category = str(row[2]) if len(row) > 2 and row[2] else ""
                        manufacturer = str(row[3]) if len(row) > 3 and row[3] else ""
                        batch = str(row[4]) if len(row) > 4 and row[4] else ""
                        
                        expiry = row[5]
                        if isinstance(expiry, datetime):
                            expiry = expiry.strftime('%Y-%m-%d')
                        else:
                            expiry = str(expiry) if expiry else ""
                        
                        try:
                            qty = int(float(row[6])) if len(row) > 6 and row[6] else 0
                        except:
                            qty = 0
                        
                        try:
                            purchase = float(row[7]) if len(row) > 7 and row[7] else 0
                        except:
                            purchase = 0
                        
                        try:
                            selling = float(row[8]) if len(row) > 8 and row[8] else 0
                        except:
                            selling = 0
                        
                        try:
                            min_stock = int(float(row[9])) if len(row) > 9 and row[9] else 10
                        except:
                            min_stock = 10
                        
                        location = str(row[10]) if len(row) > 10 and row[10] else ""
                        
                        # Check if exists
                        cursor.execute('SELECT id, quantity FROM medicines WHERE name = ? AND batch_number = ?',
                                     (name, batch))
                        existing = cursor.fetchone()
                        
                        if existing:
                            new_qty = existing[1] + qty
                            cursor.execute('''
                                UPDATE medicines SET quantity = ?, purchase_price = ?,
                                selling_price = ?, expiry_date = ?, location = ?
                                WHERE id = ?
                            ''', (new_qty, purchase, selling, expiry, location, existing[0]))
                            update_count += 1
                        else:
                            cursor.execute('''
                                INSERT INTO medicines (name, category, manufacturer, batch_number,
                                expiry_date, quantity, purchase_price, selling_price, min_stock, location, date_added)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (name, category, manufacturer, batch, expiry, qty, purchase,
                                 selling, min_stock, location, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                            import_count += 1
                            
                    except Exception as e:
                        skip_count += 1
                        continue
            
            conn.commit()
            
            # Get total
            cursor.execute('SELECT COUNT(*) FROM medicines')
            total = cursor.fetchone()[0]
            conn.close()
            
            self.load_medicines()
            
            messagebox.showinfo("✅ Import Complete",
                              f"File: {os.path.basename(filename)}\n\n"
                              f"Results:\n"
                              f"• New: {import_count}\n"
                              f"• Updated: {update_count}\n"
                              f"• Skipped: {skip_count}\n"
                              f"• Total now: {total}\n\n"
                              f"Copy saved to:\n{import_copy}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Import failed:\n{str(e)}")
    
    # ========== ADVANCED DATABASE ANALYSIS ==========
    
    def test_database_contents(self):
        """PREMIUM BUSINESS INTELLIGENCE DASHBOARD"""
        conn = sqlite3.connect(self.get_database_path())
        cursor = conn.cursor()
        
        # Basic metrics
        cursor.execute('SELECT COUNT(*) FROM medicines')
        total_products = cursor.fetchone()[0]
        
        cursor.execute('SELECT SUM(quantity) FROM medicines')
        total_units = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT SUM(quantity * selling_price) FROM medicines')
        total_value = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT SUM(quantity * purchase_price) FROM medicines')
        total_cost = cursor.fetchone()[0] or 0
        
        potential_profit = total_value - total_cost
        profit_margin = (potential_profit / total_value * 100) if total_value > 0 else 0
        
        # Sales
        cursor.execute('SELECT SUM(total_price), COUNT(*) FROM sales')
        sales = cursor.fetchone()
        total_revenue = sales[0] or 0
        total_transactions = sales[1] or 0
        
        # Today
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute('SELECT SUM(total_price), COUNT(*) FROM sales WHERE sale_date LIKE ?', (f'{today}%',))
        today_data = cursor.fetchone()
        today_revenue = today_data[0] or 0
        today_transactions = today_data[1] or 0
        
        # Status analysis
        today_date = datetime.now().date()
        cursor.execute('SELECT expiry_date, quantity, min_stock, selling_price, purchase_price FROM medicines')
        all_meds = cursor.fetchall()
        
        status = {
            'healthy': {'count': 0, 'units': 0, 'value': 0},
            'low_stock': {'count': 0, 'units': 0, 'value': 0},
            'expiring': {'count': 0, 'units': 0, 'value': 0},
            'expired': {'count': 0, 'units': 0, 'value': 0, 'loss': 0}
        }
        
        for expiry_str, qty, min_stock, sell_price, buy_price in all_meds:
            item_value = qty * sell_price
            item_cost = qty * buy_price
            is_expired = False
            is_expiring = False
            
            if expiry_str and len(expiry_str) == 10:
                try:
                    expiry = datetime.strptime(expiry_str, '%Y-%m-%d').date()
                    days = (expiry - today_date).days
                    
                    if days < 0:
                        status['expired']['count'] += 1
                        status['expired']['units'] += qty
                        status['expired']['value'] += item_value
                        status['expired']['loss'] += item_cost
                        is_expired = True
                    elif days <= 30:
                        status['expiring']['count'] += 1
                        status['expiring']['units'] += qty
                        status['expiring']['value'] += item_value
                        is_expiring = True
                except:
                    pass
            
            if not is_expired and not is_expiring:
                if qty <= min_stock:
                    status['low_stock']['count'] += 1
                    status['low_stock']['units'] += qty
                    status['low_stock']['value'] += item_value
                else:
                    status['healthy']['count'] += 1
                    status['healthy']['units'] += qty
                    status['healthy']['value'] += item_value
        
        # Categories
        cursor.execute('''
            SELECT category, COUNT(*) FROM medicines
            WHERE category IS NOT NULL AND category != ''
            GROUP BY category ORDER BY COUNT(*) DESC LIMIT 5
        ''')
        categories = cursor.fetchall()
        
        conn.close()
        
        # Turnover
        turnover = total_revenue / total_value if total_value > 0 else 0
        days_inventory = total_value / (total_revenue / 30) if total_revenue > 0 else 0
        
        # Create window
        dashboard = tk.Toplevel(self.root)
        dashboard.title("📊 BUSINESS INTELLIGENCE")
        dashboard.geometry("900x750")
        dashboard.configure(bg='#1a2634')
        dashboard.transient(self.root)
        dashboard.grab_set()
        
        # Center
        dashboard.update_idletasks()
        x = (dashboard.winfo_screenwidth() // 2) - (900 // 2)
        y = (dashboard.winfo_screenheight() // 2) - (750 // 2)
        dashboard.geometry(f'+{x}+{y}')
        
        # Scrollable
        canvas = tk.Canvas(dashboard, bg='#1a2634', highlightthickness=0)
        scrollbar = tk.Scrollbar(dashboard, orient='vertical', command=canvas.yview)
        scrollable = tk.Frame(canvas, bg='#1a2634')
        
        scrollable.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=scrollable, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        def wheel(e): canvas.yview_scroll(int(-1*(e.delta/120)), 'units')
        scrollable.bind('<Enter>', lambda e: canvas.bind_all('<MouseWheel>', wheel))
        scrollable.bind('<Leave>', lambda e: canvas.unbind_all('<MouseWheel>'))
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Main content
        main = tk.Frame(scrollable, bg='#1a2634', padx=25, pady=25)
        main.pack(fill='both', expand=True)
        
        # Header
        header = tk.Frame(main, bg='#1a2634')
        header.pack(fill='x', pady=(0, 20))
        
        tk.Label(header, text="⚕️ MERawi PHARMACY PRO", bg='#1a2634', fg='#f1c40f',
                font=('Segoe UI', 18, 'bold')).pack(anchor='w')
        tk.Label(header, text="Business Intelligence Dashboard", bg='#1a2634', fg='#95a5a6',
                font=('Segoe UI', 10)).pack(anchor='w')
        
        tk.Label(header, text=datetime.now().strftime('%B %d, %Y %I:%M %p'),
                bg='#1a2634', fg='#7f8c8d', font=('Segoe UI', 9)).pack(anchor='e')
        
        # KPI Row 1
        kpi1 = tk.Frame(main, bg='#1a2634')
        kpi1.pack(fill='x', pady=5)
        
        # Card 1
        card1 = tk.Frame(kpi1, bg='#2c3e50', padx=15, pady=15)
        card1.pack(side='left', fill='both', expand=True, padx=2)
        tk.Label(card1, text="TOTAL VALUE", bg='#2c3e50', fg='#bdc3c7',
                font=('Segoe UI', 8)).pack(anchor='w')
        tk.Label(card1, text=f"{total_value:,.0f}", bg='#2c3e50', fg='#2ecc71',
                font=('Segoe UI', 20, 'bold')).pack(anchor='w')
        tk.Label(card1, text="Birr", bg='#2c3e50', fg='#95a5a6',
                font=('Segoe UI', 8)).pack(anchor='w')
        
        # Card 2
        card2 = tk.Frame(kpi1, bg='#2c3e50', padx=15, pady=15)
        card2.pack(side='left', fill='both', expand=True, padx=2)
        tk.Label(card2, text="POTENTIAL PROFIT", bg='#2c3e50', fg='#bdc3c7',
                font=('Segoe UI', 8)).pack(anchor='w')
        tk.Label(card2, text=f"{potential_profit:,.0f}", bg='#2c3e50', fg='#f1c40f',
                font=('Segoe UI', 20, 'bold')).pack(anchor='w')
        tk.Label(card2, text=f"Margin: {profit_margin:.1f}%", bg='#2c3e50', fg='#95a5a6',
                font=('Segoe UI', 8)).pack(anchor='w')
        
        # Card 3
        card3 = tk.Frame(kpi1, bg='#2c3e50', padx=15, pady=15)
        card3.pack(side='left', fill='both', expand=True, padx=2)
        tk.Label(card3, text="ACTUAL REVENUE", bg='#2c3e50', fg='#bdc3c7',
                font=('Segoe UI', 8)).pack(anchor='w')
        tk.Label(card3, text=f"{total_revenue:,.0f}", bg='#2c3e50', fg='#3498db',
                font=('Segoe UI', 20, 'bold')).pack(anchor='w')
        tk.Label(card3, text=f"{total_transactions} sales", bg='#2c3e50', fg='#95a5a6',
                font=('Segoe UI', 8)).pack(anchor='w')
        
        # KPI Row 2
        kpi2 = tk.Frame(main, bg='#1a2634')
        kpi2.pack(fill='x', pady=5)
        
        # Card 4
        card4 = tk.Frame(kpi2, bg='#2c3e50', padx=15, pady=15)
        card4.pack(side='left', fill='both', expand=True, padx=2)
        tk.Label(card4, text="TODAY'S SALES", bg='#2c3e50', fg='#bdc3c7',
                font=('Segoe UI', 8)).pack(anchor='w')
        tk.Label(card4, text=f"{today_revenue:,.0f}", bg='#2c3e50', fg='#2ecc71',
                font=('Segoe UI', 18, 'bold')).pack(side='left', padx=5)
        tk.Label(card4, text=f"({today_transactions})", bg='#2c3e50', fg='#95a5a6',
                font=('Segoe UI', 10)).pack(side='left')
        
        # Card 5
        card5 = tk.Frame(kpi2, bg='#2c3e50', padx=15, pady=15)
        card5.pack(side='left', fill='both', expand=True, padx=2)
        tk.Label(card5, text="TURNOVER RATE", bg='#2c3e50', fg='#bdc3c7',
                font=('Segoe UI', 8)).pack(anchor='w')
        color = '#2ecc71' if turnover >= 4 else '#f39c12' if turnover >= 2 else '#e74c3c'
        tk.Label(card5, text=f"{turnover:.2f}x", bg='#2c3e50', fg=color,
                font=('Segoe UI', 18, 'bold')).pack(anchor='w')
        
        # Card 6
        card6 = tk.Frame(kpi2, bg='#2c3e50', padx=15, pady=15)
        card6.pack(side='left', fill='both', expand=True, padx=2)
        tk.Label(card6, text="INVENTORY DAYS", bg='#2c3e50', fg='#bdc3c7',
                font=('Segoe UI', 8)).pack(anchor='w')
        days_color = '#e74c3c' if days_inventory > 60 else '#f39c12' if days_inventory > 30 else '#2ecc71'
        tk.Label(card6, text=f"{days_inventory:.0f}", bg='#2c3e50', fg=days_color,
                font=('Segoe UI', 18, 'bold')).pack(anchor='w')
        
        # Status section
        status_frame = tk.Frame(main, bg='#1a2634')
        status_frame.pack(fill='x', pady=15)
        
        tk.Label(status_frame, text="📊 INVENTORY HEALTH", bg='#1a2634', fg='#ecf0f1',
                font=('Segoe UI', 12, 'bold')).pack(anchor='w', pady=(0, 10))
        
        health_items = [
            ("✅ HEALTHY", status['healthy']['count'], status['healthy']['units'], status['healthy']['value'], '#2ecc71'),
            ("⚠️ LOW STOCK", status['low_stock']['count'], status['low_stock']['units'], status['low_stock']['value'], '#f39c12'),
            ("⏰ EXPIRING", status['expiring']['count'], status['expiring']['units'], status['expiring']['value'], '#e67e22'),
            ("❌ EXPIRED", status['expired']['count'], status['expired']['units'], status['expired']['value'], '#e74c3c')
        ]
        
        for label, count, units, value, color in health_items:
            item = tk.Frame(status_frame, bg='#2c3e50', padx=15, pady=8)
            item.pack(fill='x', pady=2)
            
            tk.Label(item, text=label, bg='#2c3e50', fg=color,
                    font=('Segoe UI', 10, 'bold'), width=12, anchor='w').pack(side='left')
            tk.Label(item, text=f"{count} products", bg='#2c3e50', fg='#ecf0f1',
                    font=('Segoe UI', 10), width=10).pack(side='left')
            tk.Label(item, text=f"{units:,} units", bg='#2c3e50', fg='#bdc3c7',
                    font=('Segoe UI', 10), width=12).pack(side='left')
            tk.Label(item, text=f"{value:,.0f} Birr", bg='#2c3e50', fg='#f1c40f',
                    font=('Segoe UI', 10, 'bold')).pack(side='right')
        
        # Loss analysis
        loss_frame = tk.Frame(main, bg='#1a2634')
        loss_frame.pack(fill='x', pady=15)
        
        tk.Label(loss_frame, text="💰 RISK ASSESSMENT", bg='#1a2634', fg='#ecf0f1',
                font=('Segoe UI', 12, 'bold')).pack(anchor='w', pady=(0, 10))
        
        loss_container = tk.Frame(loss_frame, bg='#2c3e50', padx=20, pady=15)
        loss_container.pack(fill='x')
        
        rows = [
            ("Cash in Inventory:", f"{total_cost:,.0f} Birr", '#3498db'),
            ("Expired Loss:", f"{status['expired']['loss']:,.0f} Birr", '#e74c3c'),
            ("At Risk (Expiring):", f"{status['expiring']['value'] * 0.3:,.0f} Birr", '#f39c12'),
        ]
        
        for label, value, color in rows:
            row = tk.Frame(loss_container, bg='#2c3e50')
            row.pack(fill='x', pady=3)
            tk.Label(row, text=label, bg='#2c3e50', fg='#bdc3c7',
                    font=('Segoe UI', 10)).pack(side='left')
            tk.Label(row, text=value, bg='#2c3e50', fg=color,
                    font=('Segoe UI', 11, 'bold')).pack(side='right')
        
        total_loss = status['expired']['loss'] + (status['expiring']['value'] * 0.3)
        tk.Frame(loss_container, bg='#34495e', height=1).pack(fill='x', pady=10)
        
        total_row = tk.Frame(loss_container, bg='#2c3e50')
        total_row.pack(fill='x')
        tk.Label(total_row, text="TOTAL POTENTIAL LOSS:", bg='#2c3e50', fg='#ecf0f1',
                font=('Segoe UI', 11, 'bold')).pack(side='left')
        tk.Label(total_row, text=f"{total_loss:,.0f} Birr", bg='#2c3e50', fg='#e74c3c',
                font=('Segoe UI', 13, 'bold')).pack(side='right')
        
        # Recommendations
        recommendations = []
        if status['low_stock']['count'] > 0:
            recommendations.append(f"🔴 Restock {status['low_stock']['count']} low items")
        if status['expiring']['count'] > 0:
            recommendations.append(f"🟡 Run sale on {status['expiring']['count']} expiring items")
        if status['expired']['count'] > 0:
            recommendations.append(f"❌ Remove {status['expired']['count']} expired items")
        if turnover < 2:
            recommendations.append("📉 Slow turnover - consider promotions")
        elif turnover > 6:
            recommendations.append("📈 High demand - increase stock")
        
        if recommendations:
            rec_frame = tk.Frame(main, bg='#1a2634')
            rec_frame.pack(fill='x', pady=15)
            
            tk.Label(rec_frame, text="🎯 RECOMMENDATIONS", bg='#1a2634', fg='#f1c40f',
                    font=('Segoe UI', 12, 'bold')).pack(anchor='w', pady=(0, 10))
            
            for rec in recommendations:
                r = tk.Frame(rec_frame, bg='#2c3e50', padx=15, pady=8)
                r.pack(fill='x', pady=2)
                tk.Label(r, text=rec, bg='#2c3e50', fg='#ecf0f1',
                        font=('Segoe UI', 10)).pack(anchor='w')
        
        # Executive summary
        summary_frame = tk.Frame(main, bg='#1a2634')
        summary_frame.pack(fill='x', pady=15)
        
        tk.Label(summary_frame, text="📋 EXECUTIVE SUMMARY", bg='#1a2634', fg='#ecf0f1',
                font=('Segoe UI', 12, 'bold')).pack(anchor='w', pady=(0, 10))
        
        summary_box = tk.Frame(summary_frame, bg='#2c3e50', padx=20, pady=15)
        summary_box.pack(fill='x')
        
        health_score = 100
        health_score -= status['expired']['count'] * 5
        health_score -= status['expiring']['count'] * 2
        health_score -= status['low_stock']['count'] * 3
        health_score = max(0, min(100, health_score))
        
        score_color = '#2ecc71' if health_score >= 70 else '#f39c12' if health_score >= 40 else '#e74c3c'
        
        score_row = tk.Frame(summary_box, bg='#2c3e50')
        score_row.pack(fill='x', pady=5)
        tk.Label(score_row, text="Health Score:", bg='#2c3e50', fg='#bdc3c7',
                font=('Segoe UI', 11)).pack(side='left')
        tk.Label(score_row, text=f"{health_score}/100", bg='#2c3e50', fg=score_color,
                font=('Segoe UI', 16, 'bold')).pack(side='right')
        
        summary = f"Your pharmacy has {total_products} products worth {total_value:,.0f} Birr. "
        summary += f"Profit margin is {profit_margin:.1f}%. "
        if status['expired']['loss'] > 0:
            summary += f"Lost {status['expired']['loss']:,.0f} Birr to expired items. "
        
        tk.Label(summary_box, text=summary, bg='#2c3e50', fg='#ecf0f1',
                font=('Segoe UI', 10), wraplength=700).pack(pady=10)
        
        # Footer
        footer = tk.Frame(main, bg='#1a2634')
        footer.pack(fill='x', pady=(20, 10))
        
        tk.Label(footer, text="MERawi PHARMACY PRO · Business Intelligence", 
                bg='#1a2634', fg='#5d6d7e', font=('Segoe UI', 8)).pack()
        tk.Label(footer, text="Merawi Yohannes · 0921-540-245 · merawiyohannes@gmail.com", 
                bg='#1a2634', fg='#5d6d7e', font=('Segoe UI', 8)).pack()
        
        # Close button
        tk.Button(main, text="CLOSE DASHBOARD", bg='#34495e', fg='white',
                 font=('Segoe UI', 10, 'bold'), padx=40, pady=8,
                 relief='flat', command=dashboard.destroy).pack(pady=15)
    
    # ========== ALERTS ==========
    
    def check_alerts(self):
        """Check for alerts on startup"""
        alerts = []
        
        try:
            conn = sqlite3.connect(self.get_database_path())
            cursor = conn.cursor()
            
            # Low stock
            cursor.execute('SELECT COUNT(*) FROM medicines WHERE quantity <= min_stock')
            low = cursor.fetchone()[0]
            if low > 0:
                alerts.append(f"⚠️ {low} medicines low in stock")
            
            # Expiring
            today = datetime.now().date()
            cursor.execute('SELECT expiry_date FROM medicines')
            expiring = 0
            for exp in cursor.fetchall():
                if exp[0] and len(exp[0]) == 10:
                    try:
                        expiry = datetime.strptime(exp[0], '%Y-%m-%d').date()
                        if 0 <= (expiry - today).days <= 30:
                            expiring += 1
                    except:
                        pass
            
            if expiring > 0:
                alerts.append(f"⏰ {expiring} medicines expiring soon")
            
            conn.close()
            
        except:
            pass
        
        if alerts:
            messagebox.showwarning("🔔 Alerts", "\n".join(alerts))
    
    # ========== ABOUT ==========
    
    def show_about(self):
        """Professional about dialog with scrollbar"""
        about = tk.Toplevel(self.root)
        about.title("About MERawi Pharmacy Pro")
        about.geometry("550x650")
        about.configure(bg='#f5f5f5')
        about.transient(self.root)
        about.grab_set()
        
        # Center window
        about.update_idletasks()
        x = (about.winfo_screenwidth() // 2) - (550 // 2)
        y = (about.winfo_screenheight() // 2) - (650 // 2)
        about.geometry(f'+{x}+{y}')
        
        # Create canvas and scrollbar
        canvas = tk.Canvas(about, bg='#f5f5f5', highlightthickness=0)
        scrollbar = tk.Scrollbar(about, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f5f5f5')
        
        scrollable_frame.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), 'units')
        
        scrollable_frame.bind('<Enter>', lambda e: canvas.bind_all('<MouseWheel>', _on_mousewheel))
        scrollable_frame.bind('<Leave>', lambda e: canvas.unbind_all('<MouseWheel>'))
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Main content
        main = tk.Frame(scrollable_frame, bg='white', padx=30, pady=30)
        main.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Logo/Icon
        tk.Label(main, text="🏥", bg='white', font=('Segoe UI', 48)).pack(pady=(0, 10))
        
        # App name
        tk.Label(main, text="MERawi PHARMACY PRO", bg='white', fg='#2c3e50',
                font=('Segoe UI', 20, 'bold')).pack()
        
        tk.Label(main, text="Version 1.0", bg='white', fg='#7f8c8d',
                font=('Segoe UI', 11)).pack(pady=(5, 20))
        
        # Separator
        tk.Frame(main, bg='#ecf0f1', height=1).pack(fill='x', pady=10)
        
        # Description
        tk.Label(main, text="COMPLETE PHARMACY MANAGEMENT SYSTEM", bg='white', fg='#2c3e50',
                font=('Segoe UI', 12, 'bold')).pack(pady=(0, 15))
        
        tk.Label(main, text="Designed for Ethiopian pharmacies to manage inventory, sales, and business intelligence with ease.",
                bg='white', fg='#34495e', font=('Segoe UI', 10), wraplength=450, justify='center').pack(pady=(0, 20))
        
        # Features Section
        features_frame = tk.Frame(main, bg='#f8f9fa', padx=20, pady=20)
        features_frame.pack(fill='x', pady=10)
        
        tk.Label(features_frame, text="📊 KEY FEATURES", bg='#f8f9fa', fg='#2c3e50',
                font=('Segoe UI', 12, 'bold')).pack(anchor='w', pady=(0, 10))
        
        features = [
            "✓ Complete inventory management with batch tracking",
            "✓ Point of sale with tax calculation (VAT 15%)",
            "✓ Business intelligence dashboard with charts",
            "✓ Expiry date monitoring and alerts",
            "✓ Low stock notifications",
            "✓ Professional receipt printing (PDF/Text)",
            "✓ Excel import/export for data backup",
            "✓ Sales reports and analytics",
            "✓ Category-wise inventory analysis",
            "✓ Offline operation - no internet needed",
            "✓ Secure license protection",
            "✓ Automatic data backup in AppData folder"
        ]
        
        for feature in features:
            tk.Label(features_frame, text=feature, bg='#f8f9fa', fg='#34495e',
                    font=('Segoe UI', 9), anchor='w', justify='left').pack(anchor='w', pady=2)
        
        # Developer Section
        dev_frame = tk.Frame(main, bg='#f8f9fa', padx=20, pady=20)
        dev_frame.pack(fill='x', pady=10)
        
        tk.Label(dev_frame, text="👨‍💻 DEVELOPER", bg='#f8f9fa', fg='#2c3e50',
                font=('Segoe UI', 12, 'bold')).pack(anchor='w', pady=(0, 10))
        
        tk.Label(dev_frame, text="Merawi Yohannes", bg='#f8f9fa', fg='#2c3e50',
                font=('Segoe UI', 14, 'bold')).pack(anchor='w')
        
        tk.Label(dev_frame, text="Software Engineer", bg='#f8f9fa', fg='#7f8c8d',
                font=('Segoe UI', 10, 'italic')).pack(anchor='w', pady=(0, 10))
        
        # Contact Information
        contact_frame = tk.Frame(dev_frame, bg='#f8f9fa')
        contact_frame.pack(fill='x', pady=5)
        
        contacts = [
            ("📱 Phone 1:", "0921-540-245"),
            ("📱 Phone 2:", "0960-633-549"),
            ("📧 Email:", "merawiyohannes@gmail.com"),
            ("📍 Address:", "Addis Ababa, Ethiopia")
        ]
        
        for icon, value in contacts:
            row = tk.Frame(contact_frame, bg='#f8f9fa')
            row.pack(fill='x', pady=2)
            tk.Label(row, text=icon, bg='#f8f9fa', fg='#27ae60',
                    font=('Segoe UI', 9, 'bold'), width=8, anchor='w').pack(side='left')
            tk.Label(row, text=value, bg='#f8f9fa', fg='#34495e',
                    font=('Segoe UI', 9)).pack(side='left')
        
        # Support
        support_frame = tk.Frame(main, bg='#2c3e50', padx=20, pady=15)
        support_frame.pack(fill='x', pady=20)
        
        tk.Label(support_frame, text="⚕️ SUPPORT 24/7", bg='#2c3e50', fg='#f1c40f',
                font=('Segoe UI', 11, 'bold')).pack()
        tk.Label(support_frame, text="Response within 1 hour", bg='#2c3e50', fg='#ecf0f1',
                font=('Segoe UI', 9)).pack()
        
        # Copyright
        tk.Label(main, text="© 2024 MERawi Pharmacy Pro. All rights reserved.",
                bg='white', fg='#95a5a6', font=('Segoe UI', 8)).pack(pady=(10, 5))
        tk.Label(main, text="Licensed per computer - One-time payment",
                bg='white', fg='#bdc3c7', font=('Segoe UI', 7)).pack()
        
        # Close button
        close_btn = tk.Button(main, text="Close", bg='#ecf0f1', fg='#2c3e50',
                            font=('Segoe UI', 10), padx=30, pady=5,
                            relief='flat', command=about.destroy)
        close_btn.pack(pady=(20, 0))
        
        # Hover effect
        def on_enter(e): close_btn['background'] = '#d0d3d4'
        def on_leave(e): close_btn['background'] = '#ecf0f1'
        close_btn.bind('<Enter>', on_enter)
        close_btn.bind('<Leave>', on_leave)
# ========== MAIN ==========

def main():
    """Main entry point with error handling"""
    try:
        root = tk.Tk()
        app = PharmacyApp(root)
        
        if not app.check_license():
            root.quit()
            return
        
        root.mainloop()
        
    except Exception as e:
        # Show detailed error message with contact info
        error_msg = f"""❌ APPLICATION ERROR

An unexpected error occurred:

{str(e)}

Please contact the developer immediately:

👨‍💻 Merawi Yohannes
📱 0921-540-245  |  0960-633-549
📧 merawiyohannes@gmail.com

Please send a screenshot of this error message."""
        
        messagebox.showerror("🚨 Critical Error", error_msg)
        
        # Also write to log file
        try:
            log_dir = os.path.join(os.environ['LOCALAPPDATA'], 'MERawiPharmacy', 'logs')
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
            
            with open(log_file, 'w') as f:
                f.write(f"Error Time: {datetime.now()}\n")
                f.write(f"Error: {str(e)}\n")
                f.write(f"Type: {type(e).__name__}\n")
                import traceback
                f.write(f"Traceback:\n{traceback.format_exc()}")
            
            messagebox.showinfo("📝 Log Saved", f"Error log saved to:\n{log_file}")
            
        except:
            pass
        
        # Don't quit immediately - let user see the error
        root.mainloop()

if __name__ == "__main__":
    main()
             