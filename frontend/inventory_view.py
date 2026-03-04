
import tkinter as tk
from tkinter import ttk
from backend.inventory import get_all_raw_materials, get_all_products, get_product_components
from PIL import Image, ImageTk
import io

class InventoryView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="TFrame")
        self.pack(fill=tk.BOTH, expand=True)

        self.view_mode = tk.StringVar(value="Table")
        self.item_images = []

        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        top_frame = ttk.Frame(self)
        top_frame.pack(fill=tk.X, padx=2, pady=2) # Reduced padx

        ttk.Label(top_frame, text="View Mode:").pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(top_frame, text="Table", variable=self.view_mode, value="Table", command=self.switch_view).pack(side=tk.LEFT)
        ttk.Radiobutton(top_frame, text="Image", variable=self.view_mode, value="Image", command=self.switch_view).pack(side=tk.LEFT)
        
        # Add a search bar
        self.search_term = tk.StringVar()
        search_frame = ttk.Frame(top_frame)
        search_frame.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        ttk.Entry(search_frame, textvariable=self.search_term).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(search_frame, text="Search", command=self.search_inventory).pack(side=tk.LEFT, padx=2)
        ttk.Button(search_frame, text="Clear", command=self.clear_search).pack(side=tk.LEFT, padx=2)

        refresh_button = ttk.Button(top_frame, text="Refresh", command=self.load_data)
        refresh_button.pack(side=tk.RIGHT, padx=2)

        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        self.table_view_frame = ttk.Frame(self.content_frame)
        self.create_table_view()

        self.image_view_canvas = tk.Canvas(self.content_frame, bg="#2E2E2E", highlightthickness=0)
        self.image_view_scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=self.image_view_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.image_view_canvas, style="TFrame")
        
        self.scrollable_frame.bind("<Configure>", lambda e: self.image_view_canvas.configure(scrollregion=self.image_view_canvas.bbox("all")))
        self.image_view_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.image_view_canvas.configure(yscrollcommand=self.image_view_scrollbar.set)
        
        # Bind mouse wheel for scrolling
        self.image_view_canvas.bind_all("<MouseWheel>", self.on_mousewheel)

        self.switch_view()
        
    def on_mousewheel(self, event):
        if self.view_mode.get() == "Image":
            self.image_view_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def switch_view(self):
        if self.view_mode.get() == "Table":
            self.table_view_frame.grid(row=0, column=0, sticky="nsew")
            self.image_view_canvas.grid_remove()
            self.image_view_scrollbar.grid_remove()
        else:
            self.table_view_frame.grid_remove()
            self.image_view_canvas.grid(row=0, column=0, sticky="nsew")
            self.image_view_scrollbar.grid(row=0, column=1, sticky="ns")
        self.load_data()

    def create_table_view(self):
        self.table_view_frame.columnconfigure(0, weight=1)
        self.table_view_frame.rowconfigure(1, weight=1)
        self.table_view_frame.rowconfigure(3, weight=1)

        raw_materials_label = ttk.Label(self.table_view_frame, text="Raw Materials", font=("Arial", 16, "bold"))
        raw_materials_label.grid(row=0, column=0, pady=2, sticky='ew') # Reduced pady
        self.raw_materials_tree = self.create_treeview(self.table_view_frame, ["ID", "Name", "Quantity", "Price"])
        self.raw_materials_tree.grid(row=1, column=0, sticky="nsew", padx=2, pady=2) # Reduced padx, pady

        products_label = ttk.Label(self.table_view_frame, text="Products", font=("Arial", 16, "bold"))
        products_label.grid(row=2, column=0, pady=2, sticky='ew') # Reduced pady
        self.products_tree = self.create_treeview(self.table_view_frame, ["ID", "Name", "Quantity", "Price"])
        self.products_tree.grid(row=3, column=0, sticky="nsew", padx=2, pady=2) # Reduced padx, pady

    def search_inventory(self):
        self.load_data(search_term=self.search_term.get())

    def clear_search(self):
        self.search_term.set("")
        self.load_data()

    def load_data(self, search_term=""):
        self.item_images.clear()
        if self.view_mode.get() == "Table":
            self.load_table_data(search_term)
        else:
            self.load_image_data(search_term)

    def load_table_data(self, search_term=""):
        for i in self.raw_materials_tree.get_children(): self.raw_materials_tree.delete(i)
        for i in self.products_tree.get_children(): self.products_tree.delete(i)

        for item in get_all_raw_materials(search_term):
            self.raw_materials_tree.insert("", tk.END, values=(item['id'], item['name'], item['quantity'], f"{item['price']:.2f}"))
        for item in get_all_products(search_term):
            self.products_tree.insert("", tk.END, values=(item['id'], item['name'], item['quantity'], f"{item['price']:.2f}"))

    def load_image_data(self, search_term=""):
        for widget in self.scrollable_frame.winfo_children(): widget.destroy()
        
        ttk.Label(self.scrollable_frame, text="Raw Materials", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=9, pady=2, sticky='w', padx=2) # Reduced pady, padx
        row_after_rm = self.display_items_as_images(get_all_raw_materials(search_term), 1, "raw_material")
        
        ttk.Label(self.scrollable_frame, text="Products", font=("Arial", 16, "bold")).grid(row=row_after_rm, column=0, columnspan=9, pady=2, sticky='w', padx=2) # Reduced pady, padx
        self.display_items_as_images(get_all_products(search_term), row_after_rm + 1, "product")
        
        self.scrollable_frame.update_idletasks()
        self.image_view_canvas.configure(scrollregion=self.image_view_canvas.bbox("all"))

    def display_items_as_images(self, items, start_row, item_type):
        num_cols = 9
        for i in range(num_cols): # Configure columns to expand
            self.scrollable_frame.columnconfigure(i, weight=1)

        row, col = start_row, 0
        for item in items:
            frame = ttk.Frame(self.scrollable_frame, relief="solid", borderwidth=1)
            frame.grid(row=row, column=col, padx=2, pady=2, sticky="nsew") # Reduced padx, pady

            self.add_image_label(frame, item)
            
            ttk.Label(frame, text=item['name'], font=("Arial", 10, "bold"), wraplength=90).pack() # Reduced wraplength
            ttk.Label(frame, text=f"Qty: {item['quantity']}").pack()
            ttk.Label(frame, text=f"{item['price']:.2f}").pack()

            if item_type == "product":
                components = get_product_components(item['id'])
                if components:
                    comp_label = ttk.Label(frame, text="Components:", font=("Arial", 8, "bold"))
                    comp_label.pack(pady=(1,0)) # Reduced pady
                    for comp in components:
                        ttk.Label(frame, text=f"- {comp['name']} (Qty: {comp['quantity']})", font=("Arial", 8)).pack()
            col += 1
            if col >= num_cols:
                col = 0
                row += 1
        return row + 1

    def add_image_label(self, parent, item):
        img_data = item['image']
        if img_data:
            try:
                img = Image.open(io.BytesIO(img_data)).resize((100, 100), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.item_images.append(photo)
                ttk.Label(parent, image=photo).pack(pady=5)
            except Exception:
                ttk.Label(parent, text="No Image").pack(pady=5)
        else:
            ttk.Label(parent, text="No Image").pack(pady=5)

    def create_treeview(self, parent, columns):
        tree = ttk.Treeview(parent, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor=tk.CENTER)
        return tree
