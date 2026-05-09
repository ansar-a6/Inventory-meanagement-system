
import sys
import os

# Add the current directory to sys.path so we can import backend/database
sys.path.append(os.getcwd())

try:
    from database.database import initialize_database, get_db_connection
    from backend.billing import create_bill, generate_bill_docx
    from backend.inventory import add_product, add_raw_material
    print("Imports successful.")
except Exception as e:
    print(f"Import failed: {e}")
    sys.exit(1)

def test_billing():
    try:
        print("Initializing database...")
        initialize_database()
        
        # Add a dummy product for testing
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if we have any products
        cursor.execute("SELECT id FROM products LIMIT 1")
        product = cursor.fetchone()
        
        if not product:
            print("No products found, adding a test product...")
            # We need raw materials first
            rm_id = add_raw_material("Test Material", 100, 10.0)
            p_id = add_product("Test Product", 50, 25.0, [(rm_id, 1)])
            product_id = p_id
        else:
            product_id = product['id']
        
        print(f"Creating bill for product ID: {product_id}...")
        items = [{'product_id': product_id, 'quantity': 1, 'price': 25.0}]
        bill_id = create_bill(items)
        
        if bill_id:
            print(f"Bill #{bill_id} created in database. Generating DOCX...")
            docx_path = generate_bill_docx(bill_id)
            if docx_path:
                print(f"SUCCESS: DOCX generated at: {docx_path}")
            else:
                print("FAILURE: generate_bill_docx returned None.")
        else:
            print("FAILURE: create_bill returned None.")
            
    except Exception as e:
        print(f"An error occurred during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_billing()
