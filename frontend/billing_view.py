
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from backend.billing import create_bill, generate_bill_docx
from backend.inventory import get_all_products, get_product
import os
from PIL import Image, ImageTk
import io

class BillingView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="TFrame")
        self.pack(fill=tk.BOTH, expand=True)
        
        self.cart = []
        self.product_images = []
        self.products = []
        self.last_canvas_width = 0
        self.ITEM_WIDTH = 150 # Adjusted item width

        self.create_widgets()
        self.load_products()

    def create_widgets(self):
        products_frame = ttk.LabelFrame(self, text="Available Products")
        products_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2) # Reduced padx, pady for consistency

        search_frame = ttk.Frame(products_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)

        self.product_search_term_billing = tk.StringVar()
        ttk.Label(search_frame, text="Search Product:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(search_frame, textvariable=self.product_search_term_billing).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(search_frame, text="Search", command=self.search_products_billing).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Clear", command=self.clear_product_search_billing).pack(side=tk.LEFT, padx=5)

        self.canvas = tk.Canvas(products_frame, bg="#2E2E2E", highlightthickness=0)
        scrollbar = ttk.Scrollbar(products_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas, style="TFrame")

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.canvas.bind('<Configure>', self.on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel) # Added mousewheel binding

        cart_frame = ttk.LabelFrame(self, text="Shopping Cart")
        cart_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.cart_tree = self.create_treeview(cart_frame, ["Product", "Quantity", "Price", "Total"])
        self.cart_tree.pack(fill=tk.X, expand=True, side=tk.LEFT)
        self.cart_tree.bind("<<TreeviewSelect>>", self.on_cart_select)

        cart_actions_frame = ttk.Frame(cart_frame)
        cart_actions_frame.pack(side=tk.RIGHT, padx=10)

        self.edit_qty_button = ttk.Button(cart_actions_frame, text="Edit Quantity", command=self.edit_cart_item_quantity, state=tk.DISABLED)
        self.edit_qty_button.pack(pady=2)
        
        self.edit_price_button = ttk.Button(cart_actions_frame, text="Edit Price", command=self.edit_cart_item_price, state=tk.DISABLED)
        self.edit_price_button.pack(pady=2)

        self.remove_item_button = ttk.Button(cart_actions_frame, text="Remove Item", command=self.remove_from_cart, state=tk.DISABLED)
        self.remove_item_button.pack(pady=2)

        confirm_bill_button = ttk.Button(cart_actions_frame, text="Confirm Bill", command=self.confirm_bill)
        confirm_bill_button.pack(pady=5)

    def on_mousewheel(self, event): # Added on_mousewheel function
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def search_products_billing(self):
        search_term = self.product_search_term_billing.get()
        self.load_products(search_term)

    def clear_product_search_billing(self):
        self.product_search_term_billing.set("")
        self.load_products()

    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)
        if self.last_canvas_width != event.width:
            self.last_canvas_width = event.width
            self.redraw_products()

    def create_treeview(self, parent, columns):
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=5)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor=tk.CENTER)
        return tree

    def load_products(self, search_term=""):
        self.products = get_all_products(search_term)
        self.redraw_products()

    def redraw_products(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.product_images.clear()
        
        num_cols = 11 # Changed to 10 columns
        for i in range(num_cols):
            self.scrollable_frame.columnconfigure(i, weight=1)

        row, col = 0, 0
        for p in self.products:
            if p['quantity'] > 0:
                product_frame = ttk.Frame(self.scrollable_frame, relief="solid", borderwidth=1)
                product_frame.grid(row=row, column=col, padx=2, pady=2, sticky="nsew") # Reduced padx, pady
                self.scrollable_frame.rowconfigure(row, weight=1, uniform='product_rows') # Uniform row height

                img_data = p['image']
                if img_data:
                    try:
                        img = Image.open(io.BytesIO(img_data)).resize((100, 100), Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                        self.product_images.append(photo)
                        ttk.Label(product_frame, image=photo).pack(pady=5)
                    except Exception as e:
                        print(f"Error loading image for {p['name']}: {e}")
                        ttk.Label(product_frame, text="No Image").pack(pady=5)
                else:
                    ttk.Label(product_frame, text="No Image").pack(pady=5)

                ttk.Label(product_frame, text=p['name'], font=("Arial", 10, "bold"), wraplength=80).pack() # Added wraplength, reduced to 80
                ttk.Label(product_frame, text=f"Qty: {p['quantity']}").pack()
                ttk.Label(product_frame, text=f"{p['price']:.2f}").pack()
                
                add_button = ttk.Button(product_frame, text="Add to Cart", command=lambda prod=p: self.add_to_cart(prod))
                add_button.pack(side=tk.BOTTOM, fill=tk.X, pady=2) # Pushed button to bottom

                col += 1
                if col >= num_cols:
                    col = 0
                    row += 1

    def add_to_cart(self, product):
        product_id, name, available_qty, price = product['id'], product['name'], product['quantity'], product['price']
        quantity = simpledialog.askinteger("Quantity", f"Enter quantity for {name}:", minvalue=1, maxvalue=int(available_qty), parent=self)
        
        if quantity:
            for item in self.cart:
                if item['product_id'] == product_id:
                    item['quantity'] += quantity
                    self.update_cart_display()
                    return
            self.cart.append({'product_id': product_id, 'name': name, 'quantity': quantity, 'price': price})
            self.update_cart_display()

    def update_cart_display(self):
        for i in self.cart_tree.get_children():
            self.cart_tree.delete(i)
        
        total_bill = 0
        for item in self.cart:
            total_item_price = item['quantity'] * item['price']
            total_bill += total_item_price
            self.cart_tree.insert("", tk.END, values=(item['name'], item['quantity'], f"{item['price']:.2f}", f"{total_item_price:.2f}"))
        
        if total_bill > 0:
            self.cart_tree.insert("", tk.END, values=("", "", "TOTAL:", f"{total_bill:.2f}"))
        self.on_cart_select(None)

    def on_cart_select(self, event):
        selected_item = self.cart_tree.focus()
        try:
            is_total_row = self.cart_tree.item(selected_item)['values'][2] == "TOTAL:"
        except (IndexError, KeyError):
            is_total_row = False
        
        if selected_item and not is_total_row:
            self.edit_qty_button.config(state=tk.NORMAL)
            self.edit_price_button.config(state=tk.NORMAL)
            self.remove_item_button.config(state=tk.NORMAL)
        else:
            self.edit_qty_button.config(state=tk.DISABLED)
            self.edit_price_button.config(state=tk.DISABLED)
            self.remove_item_button.config(state=tk.DISABLED)

    def edit_cart_item_quantity(self):
        selected_item = self.cart_tree.focus()
        if not selected_item: return

        item_values = self.cart_tree.item(selected_item)['values']
        product_name = item_values[0]
        
        cart_item_to_edit = next((item for item in self.cart if str(item['name']) == str(product_name)), None)
        
        if cart_item_to_edit:
            product = get_product(cart_item_to_edit['product_id'])
            new_quantity = simpledialog.askinteger("Edit Quantity", f"Enter new quantity for {product_name}:",
                                                   minvalue=1, maxvalue=int(product['quantity']), parent=self)
            if new_quantity:
                cart_item_to_edit['quantity'] = new_quantity
                self.update_cart_display()

    def edit_cart_item_price(self):
        selected_item = self.cart_tree.focus()
        if not selected_item: return

        item_values = self.cart_tree.item(selected_item)['values']
        product_name = item_values[0]

        cart_item_to_edit = next((item for item in self.cart if str(item['name']) == str(product_name)), None)

        if cart_item_to_edit:
            new_price = simpledialog.askfloat("Edit Price", f"Enter new price for {product_name}:",
                                               minvalue=0.01, parent=self)
            if new_price is not None:
                cart_item_to_edit['price'] = new_price
                self.update_cart_display()

    def remove_from_cart(self):
        selected_item = self.cart_tree.focus()
        if not selected_item: return

        item_values = self.cart_tree.item(selected_item)['values']
        product_name = item_values[0]

        self.cart = [item for item in self.cart if str(item['name']) != str(product_name)]
        self.update_cart_display()

    def confirm_bill(self):
        if not self.cart:
            messagebox.showerror("Error", "Your cart is empty.")
            return

        items_to_bill = [{'product_id': item['product_id'], 'quantity': item['quantity'], 'price': item['price']} for item in self.cart]
        bill_id = create_bill(items_to_bill)
        
        if bill_id:
            full_docx_path = generate_bill_docx(bill_id)
            
            self.cart.clear()
            self.update_cart_display()
            self.load_products()
            
            if messagebox.askyesno("Success", f"Bill #{bill_id} created as a DOCX file. Do you want to open it?"):
                if full_docx_path:
                    try:
                        os.startfile(full_docx_path)
                    except Exception as e:
                        messagebox.showerror("Error", f"Could not open DOCX file: {e}")
                else:
                    messagebox.showerror("Error", "DOCX file not found or could not be created.")
        else:
            messagebox.showerror("Error", "Failed to create the bill. Check stock levels.")
