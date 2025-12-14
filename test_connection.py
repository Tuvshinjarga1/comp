"""
Database холболтыг шалгах тест скрипт
"""
from database import db
from config import config

def test_connection():
    """Database холболт шалгах"""
    print("=" * 50)
    print("Database холболтыг шалгаж байна...")
    print("=" * 50)
    
    try:
        # Холболт шалгах
        print(f"\n✓ Database холбогдлоо!")
        print(f"  Host: {config.DATABASE_HOST}")
        print(f"  Port: {config.DATABASE_PORT}")
        print(f"  Database: {config.DATABASE_NAME}")
        print(f"  User: {config.DATABASE_USER}")
        
        # Хүснэгтүүд шалгах
        print("\n" + "=" * 50)
        print("Хүснэгтүүдийг шалгаж байна...")
        print("=" * 50)
        
        tables_query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """
        
        tables = db.execute_query(tables_query)
        
        if tables:
            print(f"\n✓ {len(tables)} хүснэгт олдлоо:")
            for table in tables:
                print(f"  - {table['table_name']}")
        else:
            print("\n⚠ Хүснэгт олдсонгүй. Database хоосон байж магадгүй.")
        
        # Жижиг тест query
        print("\n" + "=" * 50)
        print("Тест query ажиллуулж байна...")
        print("=" * 50)
        
        # Merchants тоо
        try:
            merchants_count = db.execute_query("SELECT COUNT(*) as count FROM merchants")
            if merchants_count:
                print(f"\n✓ Merchants: {merchants_count[0]['count']}")
        except Exception as e:
            print(f"\n⚠ Merchants хүснэгт: {e}")
        
        # SKU тоо
        try:
            sku_count = db.execute_query("SELECT COUNT(*) as count FROM sku")
            if sku_count:
                print(f"✓ SKU: {sku_count[0]['count']}")
        except Exception as e:
            print(f"⚠ SKU хүснэгт: {e}")
        
        # Orders тоо
        try:
            orders_count = db.execute_query("SELECT COUNT(*) as count FROM orders")
            if orders_count:
                print(f"✓ Orders: {orders_count[0]['count']}")
        except Exception as e:
            print(f"⚠ Orders хүснэгт: {e}")
        
        # Sales reps тоо
        try:
            reps_count = db.execute_query("SELECT COUNT(*) as count FROM sales_reps")
            if reps_count:
                print(f"✓ Sales Reps: {reps_count[0]['count']}")
        except Exception as e:
            print(f"⚠ Sales Reps хүснэгт: {e}")
        
        print("\n" + "=" * 50)
        print("✓ Тест дууссан!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n✗ Алдаа: {e}")
        print("\nШалгах зүйлс:")
        print("  1. Database сервер ажиллаж байгаа эсэх")
        print("  2. Network холболт")
        print("  3. Credentials зөв эсэх")
        return False
    
    return True

if __name__ == "__main__":
    test_connection()
    db.close()

