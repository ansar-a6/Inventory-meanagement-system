import sqlite3
import io
from PIL import Image
from database.database import get_db_connection

def resize_and_convert_to_binary_data(file_path, size=(256, 256)):
    """Resizes an image and converts it to binary data."""
    if not file_path:
        return None
    try:
        img = Image.open(file_path)
        img.thumbnail(size, Image.Resampling.LANCZOS)
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG') # Save as PNG to preserve quality
        return img_byte_arr.getvalue()
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

def add_raw_material(name, quantity, price, image_path=None):
    """Adds a new raw material to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    image_data = resize_and_convert_to_binary_data(image_path)
    try:
        cursor.execute(
            "INSERT INTO raw_materials (name, quantity, price, image) VALUES (?, ?, ?, ?)",
            (name, quantity, price, image_data)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"Error: Raw material '{name}' already exists.")
        return None
    finally:
        conn.close()
    return cursor.lastrowid

def get_all_raw_materials(search_term=""):
    """Retrieves all raw materials from the database, with an optional search term."""
    conn = get_db_connection()
    cursor = conn.cursor()
    if search_term:
        cursor.execute("SELECT id, name, quantity, price, image FROM raw_materials WHERE name LIKE ?", ('%' + search_term + '%',))
    else:
        cursor.execute("SELECT id, name, quantity, price, image FROM raw_materials")
    raw_materials = cursor.fetchall()
    conn.close()
    return raw_materials

def get_raw_material(material_id):
    """Retrieves a single raw material by its ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM raw_materials WHERE id = ?", (material_id,))
    raw_material = cursor.fetchone()
    conn.close()
    return raw_material

def update_raw_material(material_id, name, quantity, price, image_path=None):
    """Updates an existing raw material."""
    conn = get_db_connection()
    cursor = conn.cursor()
    if image_path:
        image_data = resize_and_convert_to_binary_data(image_path)
        cursor.execute(
            "UPDATE raw_materials SET name = ?, quantity = ?, price = ?, image = ? WHERE id = ?",
            (name, quantity, price, image_data, material_id)
        )
    else:
        cursor.execute(
            "UPDATE raw_materials SET name = ?, quantity = ?, price = ? WHERE id = ?",
            (name, quantity, price, material_id)
        )
    conn.commit()
    conn.close()

def delete_raw_material(material_id):
    """Deletes a raw material from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM raw_materials WHERE id = ?", (material_id,))
    conn.commit()
    conn.close()

def add_product(name, quantity, price, components, image_path=None):
    """
    Adds a new product to the database and its components.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    image_data = resize_and_convert_to_binary_data(image_path)

    try:
        # Check for sufficient raw material stock
        for raw_material_id, qty_required in components:
            raw_material = get_raw_material(raw_material_id)
            if raw_material['quantity'] < qty_required * quantity:
                raise ValueError(f"Not enough stock for {raw_material['name']}.")
        
        # Add the product
        cursor.execute(
            "INSERT INTO products (name, quantity, price, image) VALUES (?, ?, ?, ?)",
            (name, quantity, price, image_data)
        )
        product_id = cursor.lastrowid

        # Add components and deduct stock
        for raw_material_id, qty_required in components:
            cursor.execute(
                "INSERT INTO product_components (product_id, raw_material_id, quantity) VALUES (?, ?, ?)",
                (product_id, raw_material_id, qty_required)
            )
            cursor.execute(
                "UPDATE raw_materials SET quantity = quantity - ? WHERE id = ?",
                (qty_required * quantity, raw_material_id)
            )
        conn.commit()
    except (sqlite3.Error, ValueError) as e:
        conn.rollback()
        print(f"Error creating product: {e}")
        return None
    finally:
        conn.close()
    return product_id

def get_all_products(search_term=""):
    """Retrieves all products from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    if search_term:
        cursor.execute("SELECT id, name, quantity, price, image FROM products WHERE name LIKE ?", ('%' + search_term + '%',))
    else:
        cursor.execute("SELECT id, name, quantity, price, image FROM products")
    products = cursor.fetchall()
    conn.close()
    return products

def get_product(product_id):
    """Retrieves a single product by its ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()
    conn.close()
    return product

def get_product_components(product_id):
    """Retrieves the components for a given product."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT rm.id as raw_material_id, rm.name, pc.quantity
        FROM product_components pc
        JOIN raw_materials rm ON pc.raw_material_id = rm.id
        WHERE pc.product_id = ?
    """, (product_id,))
    components = cursor.fetchall()
    conn.close()
    return components

def update_product(product_id, name, quantity, price, components, image_path=None):
    """
    Updates an existing product and its components.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if image_path:
            image_data = resize_and_convert_to_binary_data(image_path)
            cursor.execute(
                "UPDATE products SET name = ?, quantity = ?, price = ?, image = ? WHERE id = ?",
                (name, quantity, price, image_data, product_id)
            )
        else:
            cursor.execute(
                "UPDATE products SET name = ?, quantity = ?, price = ? WHERE id = ?",
                (name, quantity, price, product_id)
            )

        # Update components (clear and re-add)
        cursor.execute("DELETE FROM product_components WHERE product_id = ?", (product_id,))
        for raw_material_id, qty_required in components:
            cursor.execute(
                "INSERT INTO product_components (product_id, raw_material_id, quantity) VALUES (?, ?, ?)",
                (product_id, raw_material_id, qty_required)
            )
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Database error: {e}")
    finally:
        conn.close()

def delete_product(product_id):
    """Deletes a product and its components from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM product_components WHERE product_id = ?", (product_id,))
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Database error: {e}")
    finally:
        conn.close()

def add_raw_material_stock(material_id, quantity):
    """Adds stock to a raw material."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE raw_materials SET quantity = quantity + ? WHERE id = ?", (quantity, material_id))
    conn.commit()
    conn.close()

def deduct_raw_material_stock(material_id, quantity):
    """Deducts stock from a raw material."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT quantity FROM raw_materials WHERE id = ?", (material_id,))
    current_quantity = cursor.fetchone()['quantity']
    if current_quantity < quantity:
        print("Error: Not enough stock to deduct.")
        return False
    cursor.execute("UPDATE raw_materials SET quantity = quantity - ? WHERE id = ?", (quantity, material_id))
    conn.commit()
    conn.close()
    return True

def add_product_stock(product_id, quantity):
    """Adds stock to a product, deducting from raw materials."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        components = get_product_components(product_id)
        for comp in components:
            required = comp['quantity'] * quantity
            raw_material = get_raw_material(comp['raw_material_id'])
            if raw_material['quantity'] < required:
                raise ValueError(f"Not enough stock for {raw_material['name']}.")
        
        for comp in components:
            required = comp['quantity'] * quantity
            cursor.execute("UPDATE raw_materials SET quantity = quantity - ? WHERE id = ?", (required, comp['raw_material_id']))
        
        cursor.execute("UPDATE products SET quantity = quantity + ? WHERE id = ?", (quantity, product_id))
        conn.commit()
    except (sqlite3.Error, ValueError) as e:
        conn.rollback()
        print(f"Error adding product stock: {e}")
        return False
    finally:
        conn.close()
    return True

def deduct_product_stock(product_id, quantity):
    """Deducts stock from a product."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT quantity FROM products WHERE id = ?", (product_id,))
    current_quantity = cursor.fetchone()['quantity']
    if current_quantity < quantity:
        print("Error: Not enough stock to deduct.")
        return False
    cursor.execute("UPDATE products SET quantity = quantity - ? WHERE id = ?", (quantity, product_id))
    conn.commit()
    conn.close()
    return True