import tkinter as tk
from tkinter import ttk, messagebox
from backend.billing import get_all_bills, generate_bill_docx
import os

class BillsHistoryView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="TFrame")
        self.pack(fill=tk.BOTH, expand=True)
        
        self.search_query = tk.StringVar()
        self.search_by = tk.StringVar(value="Bill ID")

        self.create_widgets()
        self.load_bills()

    def create_widgets(self):
        title = ttk.Label(self, text="Bills History", font=("Arial", 16, "bold"))
        title.pack(pady=10)

        action_frame = ttk.Frame(self)
        action_frame.pack(fill=tk.X, padx=20, pady=5)
        
        search_frame = ttk.Frame(action_frame)
        search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(search_frame, text="Search by:").pack(side=tk.LEFT, padx=5)
        search_criteria_menu = ttk.Combobox(search_frame, textvariable=self.search_by, values=["Bill ID", "Date", "Price"])
        search_criteria_menu.pack(side=tk.LEFT, padx=5)
        
        search_entry = ttk.Entry(search_frame, textvariable=self.search_query)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        search_button = ttk.Button(search_frame, text="Search", command=self.load_bills)
        search_button.pack(side=tk.LEFT, padx=5)
        clear_button = ttk.Button(search_frame, text="Clear", command=self.clear_search)
        clear_button.pack(side=tk.LEFT, padx=5)
        
        self.reprint_button = ttk.Button(action_frame, text="Reprint Bill", command=self.reprint_bill, state=tk.DISABLED)
        self.reprint_button.pack(side=tk.RIGHT, padx=5)
        
        refresh_button = ttk.Button(action_frame, text="Refresh", command=self.load_bills)
        refresh_button.pack(side=tk.RIGHT, padx=5)

        self.bills_tree = self.create_treeview(self, ["Bill ID", "Date", "Total Amount"])
        self.bills_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        self.bills_tree.bind("<<TreeviewSelect>>", self.on_bill_select)

    def clear_search(self):
        self.search_query.set("")
        self.load_bills()

    def create_treeview(self, parent, columns):
        tree = ttk.Treeview(parent, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor=tk.CENTER)
        return tree

    def load_bills(self):
        for i in self.bills_tree.get_children():
            self.bills_tree.delete(i)
        
        query = self.search_query.get().lower()
        search_by = self.search_by.get()
        bills = get_all_bills()
        
        if query:
            filtered_bills = []
            for b in bills:
                if search_by == "Bill ID":
                    if query in str(b['id']):
                        filtered_bills.append(b)
                elif search_by == "Date":
                    if query in b['bill_date']:
                        filtered_bills.append(b)
                elif search_by == "Price":
                    if query in f"{b['total_amount']:.2f}":
                        filtered_bills.append(b)
            bills = filtered_bills

        for bill in bills:
            self.bills_tree.insert("", tk.END, values=(bill['id'], bill['bill_date'], f"{bill['total_amount']:.2f}"))
        self.reprint_button.config(state=tk.DISABLED)

    def on_bill_select(self, event):
        if self.bills_tree.focus():
            self.reprint_button.config(state=tk.NORMAL)
        else:
            self.reprint_button.config(state=tk.DISABLED)

    def reprint_bill(self):
        selected_item = self.bills_tree.focus()
        if not selected_item:
            return

        bill_id = self.bills_tree.item(selected_item)['values'][0]
        full_docx_path = generate_bill_docx(bill_id, filename_suffix="_reprint")
        
        if messagebox.askyesno("Reprint Successful", f"Bill #{bill_id} has been reprinted as a DOCX file. Do you want to open it?"):
            if full_docx_path:
                try:
                    os.startfile(full_docx_path)
                except Exception as e:
                    messagebox.showerror("Error", f"Could not open DOCX file: {e}")
            else:
                messagebox.showerror("Error", "DOCX file not found or could not be created.")