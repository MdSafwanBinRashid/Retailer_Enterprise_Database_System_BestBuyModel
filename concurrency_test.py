import mysql.connector
import threading
import time

def make_sale(customer_id, product_id, quantity):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="FUSIONtec777@",
        database="bestbuy_db"
    )
    cursor = conn.cursor()
    
    try:
        cursor.execute("START TRANSACTION")
        cursor.execute("SELECT price FROM Product WHERE product_id = %s", (product_id,))
        price = cursor.fetchone()[0]
        
        cursor.execute(
            "INSERT INTO Sales (customer_id, store_id, total_amount) VALUES (%s, 1, 0)",
            (customer_id,)
        )
        sale_id = cursor.lastrowid
        
        cursor.execute(
            "INSERT INTO SaleItem (sale_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)",
            (sale_id, product_id, quantity, price)
        )
        
        cursor.execute("UPDATE Sales SET total_amount = %s WHERE sale_id = %s", (price * quantity, sale_id))
        
        conn.commit()
        print(f"Sale {sale_id} completed for customer {customer_id}")
        
    except Exception as e:
        conn.rollback()
        print(f"Error for customer {customer_id}: {e}")
    finally:
        cursor.close()
        conn.close()

# Simulate two customers buying the same product at the same time
def simulate_concurrent_sales():
    threads = []
    for i in range(2):
        t = threading.Thread(target=make_sale, args=(i+1, 1, 1))  # customer_id, product_id=1 (Sony TV), qty=1
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    print("Concurrency test complete.")

if __name__ == "__main__":
    simulate_concurrent_sales()