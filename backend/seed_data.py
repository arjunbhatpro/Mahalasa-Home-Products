import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import uuid
from datetime import datetime, timezone

load_dotenv()

mongo_url = os.environ['MONGO_URL']
db_name = os.environ['DB_NAME']

client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

# Your actual products
products = [
    {
        "id": str(uuid.uuid4()),
        "name": "Banana Chips Plain",
        "description": "Crispy banana chips made from premium quality bananas",
        "price": 440.00,
        "stock": 100,
        "unit": "kg",
        "weight_options": [0.5, 1, 2, 3],
        "available": True,
        "images": ["https://images.unsplash.com/photo-1621939514649-280e2ee25f60?w=500"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Banana Chips Chilli",
        "description": "Spicy chilli flavored banana chips",
        "price": 440.00,
        "stock": 100,
        "unit": "kg",
        "weight_options": [0.5, 1, 2, 3],
        "available": True,
        "images": ["https://images.unsplash.com/photo-1621939514649-280e2ee25f60?w=500"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Kokum Squash",
        "description": "Refreshing kokum squash - Coming Soon",
        "price": 130.00,
        "stock": 0,
        "unit": "Litre",
        "weight_options": [1],
        "available": False,
        "coming_soon": True,
        "images": ["https://images.unsplash.com/photo-1546173159-315724a31696?w=500"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Banana Chips Pepper",
        "description": "Black pepper flavored banana chips",
        "price": 440.00,
        "stock": 100,
        "unit": "kg",
        "weight_options": [0.5, 1, 2, 3],
        "available": True,
        "images": ["https://images.unsplash.com/photo-1621939514649-280e2ee25f60?w=500"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Jackfruit Chips Coconut Oil",
        "description": "Premium jackfruit chips fried in coconut oil - Coming Soon",
        "price": 650.00,
        "stock": 0,
        "unit": "kg",
        "weight_options": [0.5, 1, 2, 3],
        "available": False,
        "coming_soon": True,
        "images": ["https://images.unsplash.com/photo-1599490659213-e2b9527bd087?w=500"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Banana Chips Tomato",
        "description": "Tangy tomato flavored banana chips",
        "price": 440.00,
        "stock": 100,
        "unit": "kg",
        "weight_options": [0.5, 1, 2, 3],
        "available": True,
        "images": ["https://images.unsplash.com/photo-1621939514649-280e2ee25f60?w=500"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Jackfruit Chips Sunflower Oil",
        "description": "Jackfruit chips fried in sunflower oil - Coming Soon",
        "price": 580.00,
        "stock": 0,
        "unit": "kg",
        "weight_options": [0.5, 1, 2, 3],
        "available": False,
        "coming_soon": True,
        "images": ["https://images.unsplash.com/photo-1599490659213-e2b9527bd087?w=500"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Banana Chips Coconut Oil",
        "description": "Traditional banana chips fried in pure coconut oil",
        "price": 490.00,
        "stock": 100,
        "unit": "kg",
        "weight_options": [0.5, 1, 2, 3],
        "available": True,
        "images": ["https://images.unsplash.com/photo-1621939514649-280e2ee25f60?w=500"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Garlic Mini Papad",
        "description": "Crispy mini papads with garlic flavor",
        "price": 500.00,
        "stock": 100,
        "unit": "kg",
        "weight_options": [0.5, 1, 2, 3],
        "available": True,
        "images": ["https://images.unsplash.com/photo-1601050690597-df0568f70950?w=500"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Masala Peanuts",
        "description": "Crunchy peanuts with special masala coating",
        "price": 410.00,
        "stock": 100,
        "unit": "kg",
        "weight_options": [0.5, 1, 2, 3],
        "available": True,
        "images": ["https://images.unsplash.com/photo-1599599810769-bcde5a160d32?w=500"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Rasam Powder",
        "description": "Authentic South Indian rasam powder - Coming Soon",
        "price": 610.00,
        "stock": 0,
        "unit": "kg",
        "weight_options": [0.5, 1, 2, 3],
        "available": False,
        "coming_soon": True,
        "images": ["https://images.unsplash.com/photo-1596040033229-a0b676ec4c14?w=500"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Chutney Powder",
        "description": "Versatile chutney powder for instant chutneys",
        "price": 610.00,
        "stock": 100,
        "unit": "kg",
        "weight_options": [0.5, 1, 2, 3],
        "available": True,
        "images": ["https://images.unsplash.com/photo-1596040033229-a0b676ec4c14?w=500"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Onion Mini Papad",
        "description": "Crispy mini papads with onion flavor",
        "price": 500.00,
        "stock": 100,
        "unit": "kg",
        "weight_options": [0.5, 1, 2, 3],
        "available": True,
        "images": ["https://images.unsplash.com/photo-1601050690597-df0568f70950?w=500"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Garlic Mixture",
        "description": "Spicy garlic flavored mixture",
        "price": 420.00,
        "stock": 100,
        "unit": "kg",
        "weight_options": [0.5, 1, 2, 3],
        "available": True,
        "images": ["https://images.unsplash.com/photo-1599599810769-bcde5a160d32?w=500"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Traditional Uddina Papad",
        "description": "Classic urad dal papad",
        "price": 140.00,
        "stock": 1000,
        "unit": "50 Pieces",
        "piece_options": [
            {"pieces": 50, "price": 140},
            {"pieces": 100, "price": 280},
            {"pieces": 200, "price": 560},
            {"pieces": 500, "price": 1400}
        ],
        "available": True,
        "images": ["https://images.unsplash.com/photo-1601050690597-df0568f70950?w=500"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Traditional Uddina Chilli Papad",
        "description": "Spicy urad dal papad with chilli",
        "price": 140.00,
        "stock": 1000,
        "unit": "50 Pieces",
        "piece_options": [
            {"pieces": 50, "price": 140},
            {"pieces": 100, "price": 280},
            {"pieces": 200, "price": 560}
        ],
        "available": True,
        "images": ["https://images.unsplash.com/photo-1601050690597-df0568f70950?w=500"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Potato Papad",
        "description": "Crispy potato papad",
        "price": 100.00,
        "stock": 500,
        "unit": "20 Pieces",
        "piece_options": [
            {"pieces": 20, "price": 100},
            {"pieces": 40, "price": 190},
            {"pieces": 100, "price": 470}
        ],
        "available": True,
        "images": ["https://images.unsplash.com/photo-1601050690597-df0568f70950?w=500"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Plain Sev",
        "description": "Classic plain sev",
        "price": 380.00,
        "stock": 100,
        "unit": "kg",
        "weight_options": [0.5, 1, 2, 3],
        "available": True,
        "images": ["https://images.unsplash.com/photo-1599599810769-bcde5a160d32?w=500"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Sambar Powder",
        "description": "Authentic South Indian sambar powder",
        "price": 600.00,
        "stock": 100,
        "unit": "kg",
        "weight_options": [0.5, 1, 2, 3],
        "available": True,
        "images": ["https://images.unsplash.com/photo-1596040033229-a0b676ec4c14?w=500"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Papad Combo",
        "description": "Assorted papad combo pack",
        "price": 350.00,
        "stock": 50,
        "unit": "Combo",
        "combo_options": [1, 2, 3],
        "available": True,
        "images": ["https://images.unsplash.com/photo-1601050690597-df0568f70950?w=500"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Kod Bale",
        "description": "Traditional kod bale snack",
        "price": 400.00,
        "stock": 100,
        "unit": "kg",
        "weight_options": [0.5, 1, 2, 3],
        "available": True,
        "images": ["https://images.unsplash.com/photo-1599599810769-bcde5a160d32?w=500"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
]

async def seed_products():
    print("Seeding actual products...")
    
    # Clear existing products
    await db.products.delete_many({})
    
    # Insert actual products
    await db.products.insert_many(products)
    
    print(f"Successfully seeded {len(products)} products!")
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_products())
