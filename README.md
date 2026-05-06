# MERawi Pharmacy Pro 🏥

A **professional, offline‑first pharmacy management system** designed for Ethiopian pharmacies.  
Complete inventory management, sales tracking, credit sales (invoices), business intelligence, user roles, activity logging, and reporting – all in one secure application.

---

## 📋 Features

### 💊 Inventory Management
- Complete medicine database with batch tracking
- Expiry date monitoring (colour‑coded alerts for expiring/expired)
- Low stock notifications and reorder suggestions
- Category and manufacturer grouping
- Stock movement history (purchases, sales, adjustments)

### 💰 Point of Sale (POS)
- Quick live‑search medicines
- Government mode (includes TIN, fixed VAT 15%) and private mode (custom VAT)
- Credit sales (invoices) with customer details and due dates
- Partial / full payment recording for invoices
- Professional receipt printing & saving (text or PDF)
- Cashier name printed on every receipt
- Payment methods: Cash, Card, Transfer, Other

### 📊 Business Intelligence
- **Live Dashboard** – resizable popup with real‑time KPIs:
  - Total investment, potential revenue, profit margin
  - Inventory health (healthy / low stock / expiring / expired)
  - Expiry calendar (units expiring each month)
  - Top 5 best‑selling products
  - Sales trend over 12 months
  - Best‑selling days and price range distribution
- **Business Intelligence Report** – deep financial analysis, turnover rate, inventory days, health score, risk assessment, and actionable recommendations

### 📈 Reports & Analytics
- Low stock report
- Expiring medicines (next 30 days)
- Today’s sales report
- Invoice analysis (overdue tracking, search by customer/invoice/phone)
- Activity log (full audit trail with user, action, timestamp)
- Excel export & import (backup/restore)

### 🔐 User & Security
- Multi‑user login (admin / cashier roles)
- Role‑based access control:
  - Admin: full access, user management, activity log, analytics, settings
  - Cashier: sales, inventory view, reports (read‑only)
- Activity logging – every critical action is recorded (sales, invoices, payments, medicine changes)
- My Account – users can change their own password and full name
- Logout functionality (returns to login screen)
- **License system**:
  - 30‑day free trial (one trial per computer)
  - Paid license (lifetime, generated from computer ID)
  - Automatic expiry detection & license file management

### 🧾 Invoices (Credit Sales)
- Create invoices with customer name, phone, address, due date
- Stock deducted immediately (items leave inventory)
- Track payments (partial or full)
- Overdue invoices alert on app startup
- Invoice analysis window with real‑time search & overdue filter
- Reprint invoice PDF at any time

### 💾 Data & Backup
- All data stored locally (SQLite) in user’s AppData folder – safe from updates
- Backup to Excel (all medicines)
- Import from Excel (bulk add/update)
- Receipts and invoices saved as PDFs in dedicated folder

---

## 💻 System Requirements

- **Operating System**: Windows 7/8/10/11, macOS, Linux
- **Python**: 3.8 or higher (if running from source)
- **Disk Space**: 100 MB minimum
- **RAM**: 2 GB (4 GB recommended for large inventories)
- **Internet**: Not required (fully offline)

---

## 🚀 Quick Start

1. **Run the executable** (or run `pharmacy_app.py` from source).
2. **Login** with default admin credentials:
   - Username: `admin`
   - Password: `admin123`
3. **Add medicines** from the Medicines tab.
4. **Start selling** from the Sales tab.
5. **Create invoices** for credit customers (use the “Credit Invoice” button).
6. **Monitor overdue invoices** via Reports → Invoice Analysis.
7. **Admin users** can add new users, view activity log, and access Business Intelligence tools from Settings → User Management / Analytics.

---

## 🔧 Default Admin Account (first run)

| Field      | Value        |
|------------|--------------|
| Username   | `admin`      |
| Password   | `admin123`   |
| Role       | `admin`      |

⚠️ **Change the default password after first login** (Settings → My Account).

---

## 📦 License & Trial

- **30‑day free trial** – one trial period per computer.
- **Paid license** – lifetime, generated from your computer ID.
- Contact the developer to obtain a paid license key.
- After trial expires, the app will show the activation dialog; you can then enter a paid key.

---

## 👨‍💻 Developer Contact

Merawi Yohannes  
📱 0921-540-245 | 0960-633-549  
📧 merawiyohannes@gmail.com  
📍 Addis Ababa, Ethiopia

---

## 📝 Version History

**v2.0 (current)**
- Added multi‑user login with roles (admin/cashier)
- Added activity log (full audit trail)
- Added invoice system (credit sales, partial/full payments)
- Added overdue invoice alerts & invoice analysis window
- Added resizable live dashboard (popup) with refresh button
- Added Business Intelligence Report
- Reworked license system: 30‑day trial + paid lifetime license
- Added “My Account” for users to change password/name
- Added logout feature
- Moved admin‑only tools (User Management, Analytics) under Settings
- Improved status bar to show logged‑in user
- Various UI polish and bug fixes

**v1.0** (initial)
- Inventory management, POS, basic reports, Excel backup, receipt PDF

---

## 🙏 Acknowledgements

Built with Python, Tkinter, and SQLite – special thanks to the open‑source community.

---

> **Note:** This software is intended for legal pharmacy operations. The developer is not responsible for misuse or violation of local tax laws.