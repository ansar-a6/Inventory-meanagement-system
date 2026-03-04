import tkinter as tk
from tkinter import ttk
from frontend.inventory_view import InventoryView
from frontend.manage_items_view import ManageItemsView
from frontend.billing_view import BillingView
from frontend.bills_history_view import BillsHistoryView

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Inventory Management System")
        self.geometry("1200x800")

        # Apply dark theme
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.configure(bg="#2E2E2E")
        self.style.configure("TFrame", background="#2E2E2E")
        self.style.configure("TLabel", background="#2E2E2E", foreground="white", font=("Arial", 12))
        self.style.configure("TButton", background="#4A4A4A", foreground="white", font=("Arial", 12), borderwidth=0)
        self.style.map("TButton", background=[("active", "#646464")])

        # Main container
        main_container = ttk.Frame(self, style="TFrame")
        main_container.pack(fill=tk.BOTH, expand=True)

        # Left navigation panel
        self.nav_frame = ttk.Frame(main_container, width=200, style="TFrame")
        self.nav_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.nav_frame.pack_propagate(False)

        # Content frame
        self.content_frame = ttk.Frame(main_container, style="TFrame")
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.create_navigation()
        self.show_inventory_view() # Show default view

    def create_navigation(self):
        """Creates the navigation buttons."""
        buttons = {
            "View Inventory": self.show_inventory_view,
            "Add/Edit Items": self.show_manage_items_view,
            "Billing": self.show_billing_view,
            "Bills History": self.show_bills_history_view,
        }

        for text, command in buttons.items():
            btn = ttk.Button(self.nav_frame, text=text, command=command, style="TButton")
            btn.pack(fill=tk.X, pady=5, padx=10)

    def show_inventory_view(self):
        self.clear_content_frame()
        inventory_frame = InventoryView(self.content_frame)
        # No need to pack here as it's handled in the view itself

    def show_manage_items_view(self):
        self.clear_content_frame()
        manage_items_frame = ManageItemsView(self.content_frame)

    def show_billing_view(self):
        self.clear_content_frame()
        billing_frame = BillingView(self.content_frame)

    def show_bills_history_view(self):
        self.clear_content_frame()
        bills_history_frame = BillsHistoryView(self.content_frame)

    def clear_content_frame(self):
        """Clears all widgets from the content frame."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()
