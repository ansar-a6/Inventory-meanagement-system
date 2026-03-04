import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from backend.inventory import (
    add_raw_material, get_all_raw_materials, update_raw_material, delete_raw_material,
    add_product, get_all_products, update_product, delete_product, get_product_components,
    add_raw_material_stock, deduct_raw_material_stock, add_product_stock, deduct_product_stock
)

class ManageItemsView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="TFrame")
        self.pack(fill=tk.BOTH, expand=True)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.raw_materials_frame = ttk.Frame(self.notebook)
        self.raw_materials_frame.pack(fill=tk.BOTH, expand=True)
        self.notebook.add(self.raw_materials_frame, text="Raw Materials")
        self.create_raw_materials_tab()

        self.products_frame = ttk.Frame(self.notebook)
        self.products_frame.pack(fill=tk.BOTH, expand=True)
        self.notebook.add(self.products_frame, text="Products")
        self.create_products_tab()

    def create_raw_materials_tab(self):
        self.raw_materials_frame.columnconfigure(0, weight=1)
        self.raw_materials_frame.rowconfigure(3, weight=1)

        form_frame = ttk.LabelFrame(self.raw_materials_frame, text="Add/Edit Raw Material")
        form_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        form_frame.columnconfigure(1, weight=1)

        self.raw_material_id = None
        self.raw_material_name = tk.StringVar()
        self.raw_material_quantity = tk.DoubleVar()
        self.raw_material_price = tk.DoubleVar()
        self.raw_material_image_path = tk.StringVar()

        ttk.Label(form_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(form_frame, textvariable=self.raw_material_name).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        ttk.Label(form_frame, text="Quantity:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(form_frame, textvariable=self.raw_material_quantity).grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        ttk.Label(form_frame, text="Price:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(form_frame, textvariable=self.raw_material_price).grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        ttk.Label(form_frame, text="Image:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(form_frame, textvariable=self.raw_material_image_path, state="readonly").grid(row=3, column=1, padx=5, pady=5, sticky=tk.EW)
        ttk.Button(form_frame, text="Browse...", command=self.browse_image).grid(row=3, column=2, padx=5, pady=5)

        save_button = ttk.Button(form_frame, text="Save", command=self.save_raw_material)
        save_button.grid(row=4, column=0, columnspan=3, pady=10)
        
        action_frame = ttk.Frame(self.raw_materials_frame)
        action_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        self.add_stock_rm_button = ttk.Button(action_frame, text="Add Stock", command=self.add_stock_raw_material, state=tk.DISABLED)
        self.add_stock_rm_button.pack(side=tk.LEFT, padx=5)
        self.deduct_stock_rm_button = ttk.Button(action_frame, text="Deduct Stock", command=self.deduct_stock_raw_material, state=tk.DISABLED)
        self.deduct_stock_rm_button.pack(side=tk.LEFT, padx=5)
        self.delete_rm_button = ttk.Button(action_frame, text="Delete", command=self.delete_raw_material_item, state=tk.DISABLED)
        self.delete_rm_button.pack(side=tk.LEFT, padx=5)

        search_frame = ttk.Frame(self.raw_materials_frame)
        search_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        self.raw_material_search_term = tk.StringVar()
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(search_frame, textvariable=self.raw_material_search_term).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(search_frame, text="Search", command=self.search_raw_materials).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Clear", command=self.clear_raw_material_search).pack(side=tk.LEFT, padx=5)

        self.raw_materials_tree = self.create_treeview(self.raw_materials_frame, ["ID", "Name", "Quantity", "Price"])
        self.raw_materials_tree.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)
        self.raw_materials_tree.bind("<<TreeviewSelect>>", self.on_raw_material_select)

        self.load_raw_materials()

    def clear_raw_material_search(self):
        self.raw_material_search_term.set("")
        self.load_raw_materials()

    def search_raw_materials(self):
        term = self.raw_material_search_term.get()
        self.load_raw_materials(term)

    def create_products_tab(self):
        self.products_frame.columnconfigure(0, weight=1)
        self.products_frame.rowconfigure(5, weight=1)

        form_frame = ttk.LabelFrame(self.products_frame, text="Add/Edit Product")
        form_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        form_frame.columnconfigure(1, weight=1)

        self.product_id = None
        self.product_name = tk.StringVar()
        self.product_quantity = tk.DoubleVar()
        self.product_price = tk.DoubleVar()
        self.product_image_path = tk.StringVar()

        ttk.Label(form_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(form_frame, textvariable=self.product_name).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        ttk.Label(form_frame, text="Quantity:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(form_frame, textvariable=self.product_quantity).grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        ttk.Label(form_frame, text="Price:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(form_frame, textvariable=self.product_price).grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        ttk.Label(form_frame, text="Image:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(form_frame, textvariable=self.product_image_path, state="readonly").grid(row=3, column=1, padx=5, pady=5, sticky=tk.EW)
        ttk.Button(form_frame, text="Browse...", command=self.browse_product_image).grid(row=3, column=2, padx=5, pady=5)

        components_frame = ttk.LabelFrame(self.products_frame, text="Components")
        components_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        components_frame.columnconfigure(0, weight=1)
        components_frame.columnconfigure(2, weight=1)

        available_rm_search_frame = ttk.Frame(components_frame)
        available_rm_search_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.available_raw_material_search_term = tk.StringVar()
        ttk.Label(available_rm_search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(available_rm_search_frame, textvariable=self.available_raw_material_search_term).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(available_rm_search_frame, text="Search", command=self.search_available_raw_materials).pack(side=tk.LEFT, padx=5)
        ttk.Button(available_rm_search_frame, text="Clear", command=self.clear_available_raw_material_search).pack(side=tk.LEFT, padx=5)

        self.available_raw_materials = tk.Listbox(components_frame, selectmode=tk.MULTIPLE)
        self.available_raw_materials.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        
        buttons_frame = ttk.Frame(components_frame)
        buttons_frame.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(buttons_frame, text=">>", command=self.add_component).pack(pady=5)
        ttk.Button(buttons_frame, text="<<", command=self.remove_component).pack(pady=5)

        self.product_components_list = tk.Listbox(components_frame)
        self.product_components_list.grid(row=1, column=2, padx=5, pady=5, sticky="nsew")

        save_button = ttk.Button(self.products_frame, text="Save Product", command=self.save_product)
        save_button.grid(row=2, column=0, pady=10)

        product_action_frame = ttk.Frame(self.products_frame)
        product_action_frame.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        self.add_stock_prod_button = ttk.Button(product_action_frame, text="Add Stock", command=self.add_stock_product, state=tk.DISABLED)
        self.add_stock_prod_button.pack(side=tk.LEFT, padx=5)
        self.deduct_stock_prod_button = ttk.Button(product_action_frame, text="Deduct Stock", command=self.deduct_stock_product, state=tk.DISABLED)
        self.deduct_stock_prod_button.pack(side=tk.LEFT, padx=5)
        self.delete_prod_button = ttk.Button(product_action_frame, text="Delete", command=self.delete_product_item, state=tk.DISABLED)
        self.delete_prod_button.pack(side=tk.LEFT, padx=5)

        product_search_frame = ttk.Frame(self.products_frame)
        product_search_frame.grid(row=4, column=0, padx=10, pady=5, sticky="ew")

        self.product_search_term = tk.StringVar()
        ttk.Label(product_search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(product_search_frame, textvariable=self.product_search_term).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(product_search_frame, text="Search", command=self.search_products).pack(side=tk.LEFT, padx=5)
        ttk.Button(product_search_frame, text="Clear", command=self.clear_product_search).pack(side=tk.LEFT, padx=5)

        self.products_tree = self.create_treeview(self.products_frame, ["ID", "Name", "Quantity", "Price"])
        self.products_tree.grid(row=5, column=0, padx=10, pady=10, sticky="nsew")
        self.products_tree.bind("<<TreeviewSelect>>", self.on_product_select)

        self.load_products_data()

    def search_products(self):
        term = self.product_search_term.get()
        self.load_products_data(product_search_term=term)

    def clear_product_search(self):
        self.product_search_term.set("")
        self.load_products_data(product_search_term="")

    def add_stock_raw_material(self):
        if not self.raw_material_id: return
        quantity = simpledialog.askfloat("Add Stock", "Enter quantity to add:", minvalue=0.01, parent=self)
        if quantity:
            add_raw_material_stock(self.raw_material_id, quantity)
            self.load_raw_materials()

    def deduct_stock_raw_material(self):
        if not self.raw_material_id: return
        quantity = simpledialog.askfloat("Deduct Stock", "Enter quantity to deduct:", minvalue=0.01, parent=self)
        if quantity:
            if not deduct_raw_material_stock(self.raw_material_id, quantity):
                messagebox.showerror("Error", "Not enough stock to deduct.")
            self.load_raw_materials()

    def delete_raw_material_item(self):
        if not self.raw_material_id: return
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this raw material?"):
            delete_raw_material(self.raw_material_id)
            self.clear_raw_material_form()
            self.load_raw_materials()
            
    def add_stock_product(self):
        if not self.product_id: return
        quantity = simpledialog.askfloat("Add Stock", "Enter quantity to add:", minvalue=0.01, parent=self)
        if quantity:
            if not add_product_stock(self.product_id, quantity):
                messagebox.showerror("Error", "Failed to add product stock. Check raw material levels.")
            self.load_products_data()
            self.load_raw_materials()

    def deduct_stock_product(self):
        if not self.product_id: return
        quantity = simpledialog.askfloat("Deduct Stock", "Enter quantity to deduct:", minvalue=0.01, parent=self)
        if quantity:
            if not deduct_product_stock(self.product_id, quantity):
                messagebox.showerror("Error", "Not enough stock to deduct.")
            self.load_products_data()

    def delete_product_item(self):
        if not self.product_id: return
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this product?"):
            delete_product(self.product_id)
            self.clear_product_form()
            self.load_products_data()
    
    def browse_product_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")])
        if file_path:
            self.product_image_path.set(file_path)

    def search_available_raw_materials(self):
        term = self.available_raw_material_search_term.get()
        self.load_products_data(term)

    def clear_available_raw_material_search(self):
        self.available_raw_material_search_term.set("")
        self.load_products_data()

    def add_component(self):
        selected_indices = self.available_raw_materials.curselection()
        for i in selected_indices:
            item_text = self.available_raw_materials.get(i)
            # Remove minvalue and add a more robust check for a positive quantity.
            quantity = simpledialog.askfloat("Quantity", f"Enter quantity for {item_text.split(' (ID:')[0]}:", parent=self)
            if quantity is not None and quantity > 0:
                self.product_components_list.insert(tk.END, f"{item_text} - Qty: {quantity}")
            elif quantity is not None:
                messagebox.showwarning("Invalid Quantity", "Component quantity must be greater than zero.", parent=self)

    def remove_component(self):
        selected_indices = self.product_components_list.curselection()
        for i in selected_indices[::-1]:
            self.product_components_list.delete(i)

    def save_product(self):
        name = self.product_name.get()
        quantity = self.product_quantity.get()
        price = self.product_price.get()
        image_path = self.product_image_path.get()
        
        components = []
        for i in range(self.product_components_list.size()):
            item_text = self.product_components_list.get(i)
            parts = item_text.split(" (ID:")
            raw_material_id = int(parts[1].split(')')[0])
            qty = float(item_text.split("Qty: ")[1])
            components.append((raw_material_id, qty))

        if not name or not price:
            messagebox.showerror("Error", "Please fill all fields.")
            return
            
        if self.product_id:
            update_product(self.product_id, name, quantity, price, components, image_path or None)
        else:
            if not components:
                messagebox.showerror("Error", "Please add components to the product.")
                return
            add_product(name, quantity, price, components, image_path or None)
        
        self.clear_product_form()
        self.load_products_data()
        self.load_raw_materials()

    def on_product_select(self, event):
        selected_item = self.products_tree.focus()
        if selected_item:
            item = self.products_tree.item(selected_item)
            values = item['values']
            self.product_id = values[0]
            self.product_name.set(values[1])
            self.product_quantity.set(values[2])
            self.product_price.set(values[3])
            self.product_image_path.set("")
            self.add_stock_prod_button.config(state=tk.NORMAL)
            self.deduct_stock_prod_button.config(state=tk.NORMAL)
            self.delete_prod_button.config(state=tk.NORMAL)
            self.product_components_list.delete(0, tk.END)
            components = get_product_components(self.product_id)
            for comp in components:
                self.product_components_list.insert(tk.END, f"{comp['name']} (ID:{comp['raw_material_id']}) - Qty: {comp['quantity']}")

    def on_raw_material_select(self, event):
        selected_item = self.raw_materials_tree.focus()
        if selected_item:
            item = self.raw_materials_tree.item(selected_item)
            values = item['values']
            self.raw_material_id = values[0]
            self.raw_material_name.set(values[1])
            self.raw_material_quantity.set(values[2])
            self.raw_material_price.set(values[3])
            self.raw_material_image_path.set("")
            self.add_stock_rm_button.config(state=tk.NORMAL)
            self.deduct_stock_rm_button.config(state=tk.NORMAL)
            self.delete_rm_button.config(state=tk.NORMAL)

    def clear_product_form(self):
        self.product_id = None
        self.product_name.set("")
        self.product_quantity.set(0.0)
        self.product_price.set(0.0)
        self.product_image_path.set("")
        self.product_components_list.delete(0, tk.END)
        self.add_stock_prod_button.config(state=tk.DISABLED)
        self.deduct_stock_prod_button.config(state=tk.DISABLED)
        self.delete_prod_button.config(state=tk.DISABLED)

    def clear_raw_material_form(self):
        self.raw_material_id = None
        self.raw_material_name.set("")
        self.raw_material_quantity.set(0.0)
        self.raw_material_price.set(0.0)
        self.raw_material_image_path.set("")
        self.add_stock_rm_button.config(state=tk.DISABLED)
        self.deduct_stock_rm_button.config(state=tk.DISABLED)
        self.delete_rm_button.config(state=tk.DISABLED)

    def load_products_data(self, search_term="", product_search_term=""):
        self.available_raw_materials.delete(0, tk.END)
        raw_materials = get_all_raw_materials(search_term)
        for item in raw_materials:
            self.available_raw_materials.insert(tk.END, f"{item['name']} (ID:{item['id']})")
        
        for i in self.products_tree.get_children():
            self.products_tree.delete(i)
        products = get_all_products(product_search_term)
        for item in products:
            self.products_tree.insert("", tk.END, values=(item['id'], item['name'], item['quantity'], f"{item['price']:.2f}"))

    def load_raw_materials(self, search_term=""):
        for i in self.raw_materials_tree.get_children():
            self.raw_materials_tree.delete(i)
        raw_materials = get_all_raw_materials(search_term)
        for item in raw_materials:
            self.raw_materials_tree.insert("", tk.END, values=(item['id'], item['name'], item['quantity'], f"{item['price']:.2f}"))

    def create_treeview(self, parent, columns):
        tree = ttk.Treeview(parent, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor=tk.CENTER)
        return tree
        
    def browse_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")])
        if file_path:
            self.raw_material_image_path.set(file_path)

    def save_raw_material(self):
        name = self.raw_material_name.get()
        quantity = self.raw_material_quantity.get()
        price = self.raw_material_price.get()
        image_path = self.raw_material_image_path.get()

        if not name or not price:
            messagebox.showerror("Error", "Please fill all fields.")
            return

        if self.raw_material_id:
            update_raw_material(self.raw_material_id, name, quantity, price, image_path or None)
        else:
            add_raw_material(name, quantity, price, image_path or None)

        self.clear_raw_material_form()
        self.load_raw_materials()