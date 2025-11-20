"""
Bulk Insert Products Script
Quick way to add multiple products to the database
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.database import db

# Sample products data - Add your products here
PRODUCTS = [
    {
        'name': 'Cappuccino',
        'category_id': 1,
        'description': 'Espresso với sữa sánh mịn và bọt sữa dày',
        'base_price': 55000,
        'image': '☕',
        'ingredients': 'Espresso, Sữa tươi',
        'calories_small': 120,
        'calories_medium': 180,
        'calories_large': 240,
        'is_hot': True,
        'is_cold': False,
        'is_new': False,
        'is_bestseller': True,
        'is_seasonal': False,
        'is_available': True
    },
    {
        'name': 'Latte',
        'category_id': 1,
        'description': 'Espresso với nhiều sữa tươi, hương vị êm dịu',
        'base_price': 50000,
        'image': '☕',
        'ingredients': 'Espresso, Sữa tươi',
        'calories_small': 150,
        'calories_medium': 220,
        'calories_large': 290,
        'is_hot': True,
        'is_cold': True,
        'is_new': False,
        'is_bestseller': True,
        'is_seasonal': False,
        'is_available': True
    },
    {
        'name': 'Mocha',
        'category_id': 1,
        'description': 'Espresso kết hợp sô-cô-la đắng và sữa tươi',
        'base_price': 60000,
        'image': '☕',
        'ingredients': 'Espresso, Chocolate, Sữa tươi, Whipped cream',
        'calories_small': 200,
        'calories_medium': 280,
        'calories_large': 360,
        'is_hot': True,
        'is_cold': True,
        'is_new': False,
        'is_bestseller': True,
        'is_seasonal': False,
        'is_available': True
    },
    {
        'name': 'Caramel Macchiato',
        'category_id': 1,
        'description': 'Espresso với vanilla, sữa và caramel ngọt ngào',
        'base_price': 65000,
        'image': '☕',
        'ingredients': 'Espresso, Vanilla syrup, Sữa tươi, Caramel sauce',
        'calories_small': 180,
        'calories_medium': 260,
        'calories_large': 340,
        'is_hot': True,
        'is_cold': True,
        'is_new': False,
        'is_bestseller': True,
        'is_seasonal': False,
        'is_available': True
    },
    {
        'name': 'Flat White',
        'category_id': 1,
        'description': 'Espresso với microfoam sữa mịn màng',
        'base_price': 52000,
        'image': '☕',
        'ingredients': 'Espresso, Sữa tươi',
        'calories_small': 110,
        'calories_medium': 165,
        'calories_large': 220,
        'is_hot': True,
        'is_cold': False,
        'is_new': False,
        'is_bestseller': False,
        'is_seasonal': False,
        'is_available': True
    },
    {
        'name': 'Trà Đào Cam Sả',
        'category_id': 2,
        'description': 'Trà đen thanh mát với đào, cam và sả thơm',
        'base_price': 45000,
        'image': '🍑',
        'ingredients': 'Trà đen, Đào, Cam, Sả',
        'calories_small': 80,
        'calories_medium': 120,
        'calories_large': 160,
        'is_hot': False,
        'is_cold': True,
        'is_new': False,
        'is_bestseller': True,
        'is_seasonal': False,
        'is_available': True
    },
    {
        'name': 'Trà Ô Long Tứ Quý',
        'category_id': 2,
        'description': 'Trà ô long hảo hạng với hương thơm tinh tế',
        'base_price': 48000,
        'image': '🍵',
        'ingredients': 'Trà ô long cao cấp',
        'calories_small': 50,
        'calories_medium': 70,
        'calories_large': 90,
        'is_hot': True,
        'is_cold': True,
        'is_new': False,
        'is_bestseller': False,
        'is_seasonal': False,
        'is_available': True
    },
    {
        'name': 'Trà Sữa Trân Châu Đường Đen',
        'category_id': 2,
        'description': 'Trà sữa thơm ngon với trân châu đường đen dẻo mềm',
        'base_price': 55000,
        'image': '🧋',
        'ingredients': 'Trà đen, Sữa tươi, Trân châu đường đen',
        'calories_small': 250,
        'calories_medium': 350,
        'calories_large': 450,
        'is_hot': False,
        'is_cold': True,
        'is_new': False,
        'is_bestseller': True,
        'is_seasonal': False,
        'is_available': True
    },
    {
        'name': 'Matcha Latte',
        'category_id': 2,
        'description': 'Bột trà xanh Matcha Nhật Bản với sữa tươi',
        'base_price': 58000,
        'image': '🍵',
        'ingredients': 'Matcha Nhật, Sữa tươi',
        'calories_small': 140,
        'calories_medium': 200,
        'calories_large': 260,
        'is_hot': True,
        'is_cold': True,
        'is_new': False,
        'is_bestseller': True,
        'is_seasonal': False,
        'is_available': True
    },
    {
        'name': 'Croissant Bơ',
        'category_id': 3,
        'description': 'Bánh sừng bò giòn tan với lớp bơ thơm phức',
        'base_price': 35000,
        'image': '🥐',
        'ingredients': 'Bột mì, Bơ, Trứng',
        'calories_small': 280,
        'calories_medium': 280,
        'calories_large': 280,
        'is_hot': False,
        'is_cold': False,
        'is_new': False,
        'is_bestseller': True,
        'is_seasonal': False,
        'is_available': True
    },
    {
        'name': 'Bánh Mì Que Pháp',
        'category_id': 3,
        'description': 'Bánh mì que giòn rụm, thơm vị bơ tỏi',
        'base_price': 28000,
        'image': '🥖',
        'ingredients': 'Bột mì, Bơ tỏi',
        'calories_small': 220,
        'calories_medium': 220,
        'calories_large': 220,
        'is_hot': False,
        'is_cold': False,
        'is_new': False,
        'is_bestseller': False,
        'is_seasonal': False,
        'is_available': True
    },
    {
        'name': 'Muffin Chocolate Chip',
        'category_id': 3,
        'description': 'Bánh muffin xốp mềm với chocolate chip',
        'base_price': 38000,
        'image': '🧁',
        'ingredients': 'Bột mì, Trứng, Chocolate chip',
        'calories_small': 320,
        'calories_medium': 320,
        'calories_large': 320,
        'is_hot': False,
        'is_cold': False,
        'is_new': False,
        'is_bestseller': True,
        'is_seasonal': False,
        'is_available': True
    },
    {
        'name': 'Tiramisu',
        'category_id': 3,
        'description': 'Bánh tiramisu Ý truyền thống với cà phê đậm đà',
        'base_price': 50000,
        'image': '🍰',
        'ingredients': 'Mascarpone, Espresso, Ladyfinger, Cocoa',
        'calories_small': 380,
        'calories_medium': 380,
        'calories_large': 380,
        'is_hot': False,
        'is_cold': False,
        'is_new': False,
        'is_bestseller': True,
        'is_seasonal': False,
        'is_available': True
    },
    {
        'name': 'Sinh Tố Bơ',
        'category_id': 4,
        'description': 'Sinh tố bơ sánh mịn, bổ dưỡng',
        'base_price': 42000,
        'image': '🥑',
        'ingredients': 'Bơ, Sữa tươi, Đường',
        'calories_small': 280,
        'calories_medium': 380,
        'calories_large': 480,
        'is_hot': False,
        'is_cold': True,
        'is_new': False,
        'is_bestseller': True,
        'is_seasonal': False,
        'is_available': True
    },
    {
        'name': 'Sinh Tố Dâu',
        'category_id': 4,
        'description': 'Sinh tố dâu tươi ngọt mát',
        'base_price': 40000,
        'image': '🍓',
        'ingredients': 'Dâu tây, Sữa tươi, Đường',
        'calories_small': 200,
        'calories_medium': 280,
        'calories_large': 360,
        'is_hot': False,
        'is_cold': True,
        'is_new': False,
        'is_bestseller': True,
        'is_seasonal': False,
        'is_available': True
    },
    {
        'name': 'Nước Ép Cam',
        'category_id': 4,
        'description': 'Nước cam vắt tươi 100%',
        'base_price': 38000,
        'image': '🍊',
        'ingredients': 'Cam tươi',
        'calories_small': 110,
        'calories_medium': 165,
        'calories_large': 220,
        'is_hot': False,
        'is_cold': True,
        'is_new': False,
        'is_bestseller': True,
        'is_seasonal': False,
        'is_available': True
    },
    {
        'name': 'Nước Ép Dưa Hấu',
        'category_id': 4,
        'description': 'Nước ép dưa hấu mát lạnh giải nhiệt',
        'base_price': 35000,
        'image': '🍉',
        'ingredients': 'Dưa hấu tươi',
        'calories_small': 90,
        'calories_medium': 135,
        'calories_large': 180,
        'is_hot': False,
        'is_cold': True,
        'is_new': False,
        'is_bestseller': False,
        'is_seasonal': True,
        'is_available': True
    },
    {
        'name': 'Chocolate Sữa Đá Xay',
        'category_id': 4,
        'description': 'Chocolate đá xay với whipped cream',
        'base_price': 58000,
        'image': '🍫',
        'ingredients': 'Chocolate, Sữa tươi, Đá, Whipped cream',
        'calories_small': 320,
        'calories_medium': 450,
        'calories_large': 580,
        'is_hot': False,
        'is_cold': True,
        'is_new': False,
        'is_bestseller': True,
        'is_seasonal': False,
        'is_available': True
    }
]

def insert_products():
    """Insert all products into database"""
    conn = db.get_connection()
    if not conn:
        print("❌ Không thể kết nối database!")
        return
    
    cursor = conn.cursor()
    
    inserted = 0
    skipped = 0
    
    for product in PRODUCTS:
        try:
            # Check if product already exists
            cursor.execute(
                "SELECT id FROM products WHERE name = %s",
                (product['name'],)
            )
            
            if cursor.fetchone():
                print(f"⚠️  Sản phẩm '{product['name']}' đã tồn tại - Bỏ qua")
                skipped += 1
                continue
            
            # Insert product
            query = """
                INSERT INTO products (
                    name, category_id, description, base_price, image,
                    ingredients, calories_small, calories_medium, calories_large,
                    is_hot, is_cold, is_new, is_bestseller, is_seasonal, is_available
                ) VALUES (
                    %(name)s, %(category_id)s, %(description)s, %(base_price)s, %(image)s,
                    %(ingredients)s, %(calories_small)s, %(calories_medium)s, %(calories_large)s,
                    %(is_hot)s, %(is_cold)s, %(is_new)s, %(is_bestseller)s, %(is_seasonal)s, %(is_available)s
                )
            """
            
            cursor.execute(query, product)
            conn.commit()
            
            print(f"✅ Đã thêm: {product['name']} - {product['base_price']:,}đ")
            inserted += 1
            
        except Exception as e:
            print(f"❌ Lỗi khi thêm '{product['name']}': {e}")
            conn.rollback()
    
    cursor.close()
    conn.close()
    
    print(f"\n{'='*50}")
    print(f"✅ Thêm thành công: {inserted} sản phẩm")
    print(f"⚠️  Bỏ qua (đã tồn tại): {skipped} sản phẩm")
    print(f"📊 Tổng cộng: {len(PRODUCTS)} sản phẩm")
    print(f"{'='*50}")

if __name__ == "__main__":
    print("🚀 Bắt đầu thêm sản phẩm hàng loạt...\n")
    insert_products()
    print("\n✨ Hoàn tất!")
