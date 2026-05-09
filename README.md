# 📦 Inventory & Billing Management System

A robust, local-first Desktop Application built with Python, designed to streamline inventory tracking, product manufacturing logic, and automated invoice generation.

## 🚀 Key Features
- **Dynamic Inventory:** Track raw materials and finished products with automated stock deduction.
- **Billing Engine:** Full-featured shopping cart with real-time price and quantity adjustments.
- **Document Automation:** Generates professional invoices from a `.docx` template.
- **LibreOffice Integration:** Automated workflow to open and process bills via LibreOffice.
- **Dark Mode UI:** A modern, customized Tkinter interface for comfortable long-term use.
- **Local Database:** Powered by SQLite3 for speed, reliability, and easy backups.

## 🛠️ Tech Stack
- **Language:** Python 3.11+
- **GUI:** Tkinter (Custom Theming)
- **Database:** SQLite3
- **Libraries:** 
  - `python-docx`: Dynamic Word document manipulation.
  - `Pillow`: Image processing for product thumbnails.
  - `pywin32`: Windows system integration.
- **External Dependencies:** LibreOffice (for document viewing/printing).

## 📥 Installation
1. Clone the repository.
2. Ensure Python 3.11 or 3.12 is installed.
3. Install dependencies:
   ```bash
   pip install Pillow==10.2.0 python-docx==1.1.0 pywin32==306
   ```
4. Run the application:
   ```bash
   python main.pyw
   ```
Note: For a binary software please create a binary setup file using pyinstaller. command is saved in a seprate file.