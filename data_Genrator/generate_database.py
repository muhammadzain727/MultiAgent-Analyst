#!/usr/bin/env python3
"""
MyFashionHub synthetic PostgreSQL database generator.

Creates a relational fashion retail database for 2023 through 2026.
Run:
    pip install -r requirements.txt
    python generate_database.py

The script creates the database if it does not exist, recreates its tables,
generates synthetic records, and inserts them in dependency order.
"""

import os
import random
import calendar
from datetime import date, datetime, timedelta
from decimal import Decimal
from collections import defaultdict

import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv()

SEED = int(os.getenv("RANDOM_SEED", "42"))
random.seed(SEED)

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "myfashionhub")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_ADMIN_DB = os.getenv("DB_ADMIN_DB", "postgres")


START_DATE = date(2023, 1, 1)
END_DATE = date(2026, 12, 31)

CUSTOMER_COUNT = 2000
ORDER_COUNT = 20000
REVIEW_COUNT = 10000

CATEGORIES = [
    ("Hoodies", "Unisex"),
    ("T Shirts", "Unisex"),
    ("Shirts", "Unisex"),
    ("Jackets", "Unisex"),
    ("Belts", "Unisex"),
    ("Jeans", "Unisex"),
    ("Formal Pants", "Unisex"),
    ("Dresses", "Women"),
    ("Skirts", "Women"),
    ("Sneakers", "Unisex"),
    ("Boots", "Unisex"),
    ("Sweatshirts", "Unisex"),
    ("Coats", "Unisex"),
    ("Sportswear", "Unisex"),
    ("Accessories", "Unisex"),
]

DESIGNS = {
    "Hoodies": ["Fleece Hoodie", "Gym Hoodie", "Sleeveless Hoodie", "Oversized Hoodie",
                "Zip Hoodie", "Cropped Hoodie", "Pullover Hoodie", "Graphic Hoodie",
                "Lightweight Hoodie", "Heavyweight Hoodie", "Relaxed Hoodie", "Basic Hoodie"],
    "T Shirts": ["Classic T Shirt", "Oversized T Shirt", "Graphic T Shirt", "V Neck T Shirt",
                 "Crew Neck T Shirt", "Polo T Shirt", "Ribbed T Shirt", "Cropped T Shirt",
                 "Longline T Shirt", "Gym T Shirt", "Basic T Shirt", "Printed T Shirt"],
    "Shirts": ["Oxford Shirt", "Linen Shirt", "Formal Shirt", "Casual Shirt", "Denim Shirt",
               "Flannel Shirt", "Striped Shirt", "Checked Shirt", "Oversized Shirt",
               "Slim Fit Shirt", "Short Sleeve Shirt", "Textured Shirt"],
    "Jackets": ["Denim Jacket", "Bomber Jacket", "Puffer Jacket", "Leather Look Jacket",
                "Windbreaker", "Track Jacket", "Utility Jacket", "Cropped Jacket",
                "Quilted Jacket", "Rain Jacket", "Biker Jacket", "Lightweight Jacket"],
    "Belts": ["Classic Leather Belt", "Casual Belt", "Braided Belt", "Reversible Belt",
              "Canvas Belt", "Formal Belt", "Wide Belt", "Slim Belt", "Studded Belt",
              "Textured Belt", "Minimal Belt", "Everyday Belt"],
    "Jeans": ["Slim Jeans", "Straight Jeans", "Skinny Jeans", "Relaxed Jeans", "Wide Leg Jeans",
              "Bootcut Jeans", "Tapered Jeans", "Mom Jeans", "Boyfriend Jeans",
              "Ripped Jeans", "High Rise Jeans", "Classic Jeans"],
    "Formal Pants": ["Slim Formal Pants", "Straight Formal Pants", "Pleated Pants",
                     "Tapered Formal Pants", "Wide Leg Formal Pants", "Cropped Formal Pants",
                     "Classic Trousers", "Stretch Trousers", "Tailored Pants",
                     "High Waist Pants", "Relaxed Formal Pants", "Ankle Pants"],
    "Dresses": ["Midi Dress", "Maxi Dress", "Shirt Dress", "Wrap Dress", "Bodycon Dress",
                "A Line Dress", "Slip Dress", "Knit Dress", "Casual Dress", "Formal Dress",
                "Floral Dress", "Summer Dress"],
    "Skirts": ["Mini Skirt", "Midi Skirt", "Maxi Skirt", "Pleated Skirt", "Denim Skirt",
               "Wrap Skirt", "A Line Skirt", "Pencil Skirt", "Satin Skirt",
               "Cargo Skirt", "Printed Skirt", "Casual Skirt"],
    "Sneakers": ["Everyday Sneakers", "Running Sneakers", "Court Sneakers", "High Top Sneakers",
                 "Low Top Sneakers", "Training Sneakers", "Retro Sneakers", "Canvas Sneakers",
                 "Minimal Sneakers", "Chunky Sneakers", "Slip On Sneakers", "Lifestyle Sneakers"],
    "Boots": ["Chelsea Boots", "Ankle Boots", "Combat Boots", "Lace Up Boots", "Winter Boots",
              "Hiking Boots", "Leather Look Boots", "Platform Boots", "Rain Boots",
              "Work Boots", "Classic Boots", "Casual Boots"],
    "Sweatshirts": ["Crew Neck Sweatshirt", "Oversized Sweatshirt", "Graphic Sweatshirt",
                    "Cropped Sweatshirt", "Fleece Sweatshirt", "Zip Sweatshirt",
                    "Basic Sweatshirt", "Relaxed Sweatshirt", "Printed Sweatshirt",
                    "Lightweight Sweatshirt", "Heavyweight Sweatshirt", "Sport Sweatshirt"],
    "Coats": ["Wool Blend Coat", "Trench Coat", "Puffer Coat", "Long Coat", "Peacoat",
              "Wrap Coat", "Rain Coat", "Quilted Coat", "Belted Coat", "Classic Coat",
              "Oversized Coat", "Winter Coat"],
    "Sportswear": ["Training Leggings", "Gym Shorts", "Sports Bra", "Track Pants",
                   "Running Top", "Training Jacket", "Cycling Shorts", "Workout Tank",
                   "Performance Tee", "Training Set", "Joggers", "Compression Top"],
    "Accessories": ["Beanie", "Baseball Cap", "Scarf", "Gloves", "Socks", "Wallet",
                    "Crossbody Bag", "Tote Bag", "Backpack", "Bucket Hat", "Hair Accessory",
                    "Small Pouch"],
}

COLORS = ["Black", "White", "Navy", "Grey", "Olive", "Beige", "Burgundy", "Blue"]
SIZES = ["XS", "S", "M", "L", "XL", "XXL"]
COUNTRIES = ["Estonia", "Finland", "Latvia", "Lithuania", "Germany", "Sweden",
             "Poland", "Netherlands", "France", "United Kingdom"]
FIRST_NAMES = ["Alex", "Sam", "Jordan", "Taylor", "Morgan", "Jamie", "Robin", "Chris",
               "Ava", "Mia", "Emma", "Noah", "Liam", "Oliver", "Sofia", "Lucas",
               "Amir", "Sara", "Daniel", "Anna", "Maya", "Adam", "Ella", "Leo"]
LAST_NAMES = ["Smith", "Brown", "Wilson", "Taylor", "Anderson", "Martin", "Clark",
              "Lee", "Walker", "Hall", "Young", "King", "Wright", "Scott", "Green"]

REVIEW_POSITIVE = [
    "Really happy with this {design}. The {color} colour looks great and the material feels comfortable.",
    "Good quality for the price. The fit is {fit} and I would consider buying it again.",
    "The product looks like the pictures. Stitching and finish are better than I expected.",
    "Comfortable and easy to style. Delivery was smooth and the item arrived in good condition.",
    "I have worn this several times and it is holding up well after washing.",
]
REVIEW_NEUTRAL = [
    "The {design} is okay overall. The colour is accurate, but the material is fairly ordinary.",
    "Decent product. The fit is {fit}, although I expected slightly better finishing.",
    "It does the job. Nothing especially impressive, but no major issue either.",
    "The product is close to the description. Packaging and delivery were average.",
]
REVIEW_NEGATIVE = [
    "Disappointed with this {design}. The stitching started coming loose after limited use.",
    "The material feels thinner than expected and the fit is not comfortable.",
    "The colour faded after washing. I expected better quality at this price.",
    "Sizing is inconsistent. The item feels much smaller than the size guide suggested.",
    "The zipper or finishing is poor and the product does not feel durable.",
]
SUSPICIOUS_REVIEW = [
    "Amazing product best quality ever buy now everyone should order this perfect perfect.",
    "Five stars excellent excellent product best store guaranteed buy immediately.",
    "Outstanding item no problems at all. This is the best product in the whole world.",
]

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS products (
    product_id VARCHAR(20) PRIMARY KEY,
    brand_name VARCHAR(80) NOT NULL DEFAULT 'MyFashionHub',
    product_name VARCHAR(160) NOT NULL,
    category VARCHAR(60) NOT NULL,
    product_type VARCHAR(100) NOT NULL,
    target_gender VARCHAR(20) NOT NULL,
    description TEXT,
    base_price NUMERIC(10,2) NOT NULL CHECK (base_price > 0),
    production_cost NUMERIC(10,2) NOT NULL CHECK (production_cost >= 0),
    launch_date DATE NOT NULL,
    product_status VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS product_variants (
    sku_id VARCHAR(40) PRIMARY KEY,
    product_id VARCHAR(20) NOT NULL REFERENCES products(product_id),
    color VARCHAR(30) NOT NULL,
    size VARCHAR(10) NOT NULL,
    selling_price NUMERIC(10,2) NOT NULL CHECK (selling_price > 0),
    unit_cost NUMERIC(10,2) NOT NULL CHECK (unit_cost >= 0),
    UNIQUE(product_id, color, size)
);

CREATE TABLE IF NOT EXISTS customers (
    customer_id VARCHAR(20) PRIMARY KEY,
    first_name VARCHAR(60) NOT NULL,
    last_name VARCHAR(60) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    country VARCHAR(60) NOT NULL,
    gender VARCHAR(20),
    age_group VARCHAR(20),
    customer_segment VARCHAR(30),
    registration_date DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    order_id VARCHAR(24) PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL REFERENCES customers(customer_id),
    order_date TIMESTAMP NOT NULL,
    country VARCHAR(60) NOT NULL,
    order_status VARCHAR(20) NOT NULL,
    payment_status VARCHAR(20) NOT NULL,
    shipping_cost NUMERIC(10,2) NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS order_items (
    order_item_id BIGINT PRIMARY KEY,
    order_id VARCHAR(24) NOT NULL REFERENCES orders(order_id),
    sku_id VARCHAR(40) NOT NULL REFERENCES product_variants(sku_id),
    product_id VARCHAR(20) NOT NULL REFERENCES products(product_id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10,2) NOT NULL,
    discount_amount NUMERIC(10,2) NOT NULL DEFAULT 0,
    line_revenue NUMERIC(12,2) NOT NULL,
    unit_cost NUMERIC(10,2) NOT NULL,
    line_cost NUMERIC(12,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS reviews (
    review_id BIGINT PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL REFERENCES customers(customer_id),
    product_id VARCHAR(20) NOT NULL REFERENCES products(product_id),
    sku_id VARCHAR(40) REFERENCES product_variants(sku_id),
    order_item_id BIGINT REFERENCES order_items(order_item_id),
    review_date DATE NOT NULL,
    rating SMALLINT CHECK (rating BETWEEN 1 AND 5),
    review_text TEXT,
    review_type VARCHAR(20) NOT NULL CHECK (review_type IN ('both', 'rating_only', 'text_only')),
    verified_purchase BOOLEAN NOT NULL,
    authenticity_label VARCHAR(30) NOT NULL CHECK (authenticity_label IN ('Normal synthetic', 'Suspicious synthetic'))
);

CREATE TABLE IF NOT EXISTS inventory_movements (
    movement_id BIGINT PRIMARY KEY,
    sku_id VARCHAR(40) NOT NULL REFERENCES product_variants(sku_id),
    movement_date DATE NOT NULL,
    movement_type VARCHAR(30) NOT NULL,
    quantity_change INTEGER NOT NULL,
    reference_type VARCHAR(30),
    reference_id VARCHAR(40),
    notes TEXT
);

CREATE TABLE IF NOT EXISTS returns (
    return_id BIGINT PRIMARY KEY,
    order_item_id BIGINT NOT NULL REFERENCES order_items(order_item_id),
    return_date DATE NOT NULL,
    quantity_returned INTEGER NOT NULL CHECK (quantity_returned > 0),
    return_reason VARCHAR(60) NOT NULL,
    refund_amount NUMERIC(12,2) NOT NULL,
    item_condition VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS expenses (
    expense_id BIGINT PRIMARY KEY,
    expense_date DATE NOT NULL,
    expense_month DATE NOT NULL,
    expense_category VARCHAR(40) NOT NULL,
    amount NUMERIC(12,2) NOT NULL CHECK (amount >= 0),
    description TEXT
);

CREATE TABLE IF NOT EXISTS monthly_targets (
    target_id BIGINT PRIMARY KEY,
    target_month DATE NOT NULL,
    product_id VARCHAR(20) NOT NULL REFERENCES products(product_id),
    target_units INTEGER NOT NULL,
    target_revenue NUMERIC(12,2) NOT NULL,
    UNIQUE(target_month, product_id)
);

CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product ON order_items(product_id);
CREATE INDEX IF NOT EXISTS idx_reviews_product_date ON reviews(product_id, review_date);
CREATE INDEX IF NOT EXISTS idx_reviews_customer ON reviews(customer_id);
CREATE INDEX IF NOT EXISTS idx_inventory_sku_date ON inventory_movements(sku_id, movement_date);
CREATE INDEX IF NOT EXISTS idx_returns_date ON returns(return_date);
CREATE INDEX IF NOT EXISTS idx_targets_month ON monthly_targets(target_month);
"""

TABLES_TO_RESET = [
    "returns", "reviews", "inventory_movements", "order_items", "orders",
    "monthly_targets", "expenses", "product_variants", "products", "customers"
]


def money(value):
    return Decimal(str(value)).quantize(Decimal("0.01"))


def random_date(start=START_DATE, end=END_DATE):
    span = (end - start).days
    return start + timedelta(days=random.randint(0, span))


def month_start(year, month):
    return date(year, month, 1)


def seasonal_factor(category, month):
    winter = month in (11, 12, 1, 2)
    summer = month in (5, 6, 7, 8)
    if category in ("Coats", "Boots", "Jackets", "Hoodies"):
        return 1.65 if winter else (0.62 if summer else 1.0)
    if category in ("Dresses", "Skirts", "T Shirts", "Sneakers"):
        return 1.45 if summer else 0.82
    if category == "Sportswear":
        return 1.15
    return 1.0


def connect_admin():
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_ADMIN_DB,
        user=DB_USER, password=DB_PASSWORD
    )


def ensure_database():
    conn = connect_admin()
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
            exists = cur.fetchone()
            if not exists:
                cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
                print(f"Created PostgreSQL database: {DB_NAME}")
            else:
                print(f"Using existing PostgreSQL database: {DB_NAME}")
    finally:
        conn.close()


def insert_many(cur, statement, rows, page_size=2000):
    if rows:
        execute_values(cur, statement, rows, page_size=page_size)


def generate_products():
    rows = []
    product_meta = {}
    product_num = 1
    for category, gender in CATEGORIES:
        for design in DESIGNS[category]:
            product_id = f"MFH{product_num:04d}"
            price = round(random.uniform(12, 115), 2)
            if category in ("Belts", "Accessories"):
                price = round(random.uniform(8, 48), 2)
            if category in ("Coats", "Boots", "Jackets"):
                price = round(random.uniform(45, 150), 2)
            cost = round(price * random.uniform(0.28, 0.58), 2)
            launch = random_date(date(2022, 10, 1), date(2026, 6, 30))
            status = "active" if launch <= END_DATE else "planned"
            description = f"MyFashionHub {design.lower()} in the {category.lower()} collection."
            rows.append((product_id, "MyFashionHub", design, category, design, gender,
                         description, money(price), money(cost), launch, status))
            product_meta[product_id] = {
                "category": category, "design": design, "gender": gender,
                "price": price, "cost": cost, "launch": launch
            }
            product_num += 1
    return rows, product_meta


def generate_variants(product_meta):
    rows = []
    variant_meta = {}
    for product_id, meta in product_meta.items():
        colors = random.sample(COLORS, 4)
        if meta["category"] in ("Belts", "Accessories"):
            sizes = ["ONE"]
        elif meta["category"] in ("Sneakers", "Boots"):
            sizes = ["38", "39", "40", "41", "42", "43", "44"]
        elif meta["gender"] == "Women" and meta["category"] in ("Dresses", "Skirts"):
            sizes = ["XS", "S", "M", "L", "XL"]
        else:
            sizes = ["S", "M", "L", "XL", "XXL"]
        for color in colors:
            for size in sizes:
                sku_id = f"{product_id}-{color[:3].upper()}-{size}"
                price = money(meta["price"] * random.uniform(0.97, 1.04))
                cost = money(meta["cost"] * random.uniform(0.97, 1.03))
                rows.append((sku_id, product_id, color, size, price, cost))
                variant_meta[sku_id] = {
                    "product_id": product_id, "category": meta["category"],
                    "price": float(price), "cost": float(cost),
                    "launch": meta["launch"], "color": color, "size": size
                }
    return rows, variant_meta


def generate_customers():
    rows = []
    customer_meta = {}
    for i in range(1, CUSTOMER_COUNT + 1):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        customer_id = f"CUST{i:05d}"
        country = random.choice(COUNTRIES)
        gender = random.choice(["Female", "Male", "Non-binary", "Prefer not to say"])
        age_group = random.choice(["18-24", "25-34", "35-44", "45-54", "55+"])
        segment = random.choices(
            ["New", "Regular", "Loyal", "Occasional"], weights=[20, 35, 20, 25]
        )[0]
        registration = random_date(date(2022, 10, 1), END_DATE)
        email = f"{first.lower()}.{last.lower()}.{i}@example.com"
        rows.append((customer_id, first, last, email, country, gender,
                     age_group, segment, registration))
        customer_meta[customer_id] = {
            "country": country, "registration": registration
        }
    return rows, customer_meta


def generate_orders_and_items(customers, variants):
    orders = []
    items = []
    movements = []
    item_meta = {}
    product_sales = defaultdict(int)
    sku_stock = {sku: random.randint(12, 35) for sku in variants}
    sku_last_restock = {}
    sku_movement_id = 1
    item_id = 1

    # Opening inventory for each SKU.
    for sku, stock in sku_stock.items():
        movements.append((sku_movement_id, sku, date(2023, 1, 1),
                          "opening_stock", stock, "initial", None, "Opening stock balance"))
        sku_movement_id += 1

    order_dates = sorted(random_date() for _ in range(ORDER_COUNT))
    customer_ids = list(customers.keys())
    sku_ids = list(variants.keys())
    product_to_skus = defaultdict(list)
    for sku, meta in variants.items():
        product_to_skus[meta["product_id"]].append(sku)

    for order_number, order_day in enumerate(order_dates, start=1):
        order_id = f"ORD{order_number:07d}"
        eligible_customers = [
            cid for cid in customer_ids
            if customers[cid]["registration"] <= order_day
        ]
        if not eligible_customers:
            eligible_customers = customer_ids
        customer_id = random.choice(eligible_customers)
        country = customers[customer_id]["country"]
        order_status = random.choices(
            ["delivered", "shipped", "processing", "cancelled"],
            weights=[88, 5, 3, 4]
        )[0]
        payment_status = "refunded" if order_status == "cancelled" else "paid"
        shipping = money(random.choice([0, 3.99, 4.99, 5.99]))
        order_timestamp = datetime.combine(
            order_day, datetime.min.time()
        ) + timedelta(minutes=random.randint(0, 1439))
        orders.append((order_id, customer_id, order_timestamp, country,
                       order_status, payment_status, shipping, order_timestamp))

        line_count = random.choices([1, 2, 3, 4], weights=[48, 34, 14, 4])[0]
        chosen_products = random.choices(
            list(product_to_skus.keys()),
            weights=[
                1.8 if variants[product_to_skus[p][0]]["category"] in
                ("T Shirts", "Hoodies", "Jeans", "Sportswear") else 1.0
                for p in product_to_skus
            ],
            k=line_count
        )
        for product_id in chosen_products:
            meta_product = next(iter(product_to_skus[product_id]))
            category = variants[meta_product]["category"]
            candidates = product_to_skus[product_id]
            sku_id = random.choice(candidates)
            vmeta = variants[sku_id]
            if vmeta["launch"] > order_day:
                earlier = [s for s in candidates if variants[s]["launch"] <= order_day]
                if not earlier:
                    continue
                sku_id = random.choice(earlier)
                vmeta = variants[sku_id]

            # Replenish a SKU when stock is low. This is recorded as a ledger movement.
            if sku_stock[sku_id] < 4:
                received = random.randint(12, 30)
                sku_stock[sku_id] += received
                movements.append((sku_movement_id, sku_id, order_day,
                                  "restock", received, "purchase_order",
                                  f"PO{sku_movement_id:08d}", "Synthetic supplier replenishment"))
                sku_movement_id += 1

            if sku_stock[sku_id] <= 0:
                continue

            quantity = min(random.choices([1, 2, 3], weights=[78, 19, 3])[0], sku_stock[sku_id])
            sku_stock[sku_id] -= quantity
            unit_price = money(vmeta["price"])
            discount_rate = random.choices([0, 0.05, 0.10, 0.15, 0.20],
                                           weights=[48, 18, 18, 11, 5])[0]
            gross = unit_price * quantity
            discount = money(gross * Decimal(str(discount_rate)))
            revenue = money(gross - discount)
            unit_cost = money(vmeta["cost"])
            line_cost = money(unit_cost * quantity)
            items.append((item_id, order_id, sku_id, product_id, quantity,
                          unit_price, discount, revenue, unit_cost, line_cost))
            item_meta[item_id] = {
                "order_id": order_id, "sku_id": sku_id, "product_id": product_id,
                "customer_id": customer_id, "date": order_day,
                "quantity": quantity, "revenue": float(revenue),
                "unit_price": float(unit_price), "unit_cost": float(unit_cost),
                "category": category, "color": vmeta["color"]
            }
            product_sales[product_id] += quantity
            movements.append((sku_movement_id, sku_id, order_day, "sale",
                              -quantity, "order_item", str(item_id),
                              "Stock issued for customer order"))
            sku_movement_id += 1
            item_id += 1

    return orders, items, movements, item_meta, product_sales


def generate_reviews(item_meta, product_meta):
    # Select 10,000 distinct purchased customer/product combinations where possible.
    combinations = {}
    for item_id, item in item_meta.items():
        key = (item["customer_id"], item["product_id"])
        combinations.setdefault(key, []).append((item_id, item))
    keys = list(combinations.keys())
    if len(keys) < REVIEW_COUNT:
        raise RuntimeError(
            f"Only {len(keys)} unique customer/product purchases are available. "
            f"Cannot create {REVIEW_COUNT} distinct verified reviews."
        )
    selected = random.sample(keys, REVIEW_COUNT)
    rows = []
    for review_id, key in enumerate(selected, start=1):
        item_id, item = random.choice(combinations[key])
        product = product_meta[item["product_id"]]
        # Product quality differs by design. Lower quality items attract lower ratings.
        quality = random.random()
        if quality < 0.12:
            rating = random.choices([1, 2, 3, 4, 5], [24, 35, 25, 12, 4])[0]
        elif quality < 0.28:
            rating = random.choices([1, 2, 3, 4, 5], [8, 18, 34, 28, 12])[0]
        else:
            rating = random.choices([1, 2, 3, 4, 5], [2, 5, 13, 35, 45])[0]

        authenticity = "Suspicious synthetic" if random.random() < 0.035 else "Normal synthetic"
        if authenticity == "Suspicious synthetic":
            rating = 5
            text = random.choice(SUSPICIOUS_REVIEW)
        else:
            if rating >= 4:
                text = random.choice(REVIEW_POSITIVE).format(
                    design=product["design"], color=item["color"], fit=random.choice(["relaxed", "true to size", "slim"])
                )
            elif rating == 3:
                text = random.choice(REVIEW_NEUTRAL).format(
                    design=product["design"], color=item["color"], fit=random.choice(["relaxed", "true to size", "slim"])
                )
            else:
                text = random.choice(REVIEW_NEGATIVE).format(
                    design=product["design"], color=item["color"], fit=random.choice(["relaxed", "too tight", "too loose"])
                )

        review_type = random.choices(
            ["both", "rating_only", "text_only"], weights=[72, 18, 10]
        )[0]
        stored_rating = rating if review_type != "text_only" else None
        stored_text = text if review_type != "rating_only" else None
        review_day = item["date"] + timedelta(days=random.randint(1, 45))
        if review_day > END_DATE:
            review_day = END_DATE
        rows.append((review_id, item["customer_id"], item["product_id"],
                     item["sku_id"], item_id, review_day, stored_rating,
                     stored_text, review_type, True, authenticity))
    return rows


def generate_returns(item_meta, variant_meta):
    rows = []
    movements = []
    return_id = 1
    movement_id = 1
    reason_weights = [
        "Wrong size", "Changed mind", "Damaged item", "Not as described",
        "Poor quality", "Wrong colour", "Late delivery"
    ]
    for item_id, item in item_meta.items():
        if random.random() > 0.075:
            continue
        quantity = random.randint(1, item["quantity"])
        return_day = item["date"] + timedelta(days=random.randint(2, 35))
        if return_day > END_DATE:
            continue
        reason = random.choice(reason_weights)
        condition = random.choices(["resalable", "damaged"], [78, 22])[0]
        refund = money(item["unit_price"] * quantity * random.uniform(0.85, 1.0))
        rows.append((return_id, item_id, return_day, quantity, reason, refund, condition))
        if condition == "resalable":
            movements.append((movement_id, item["sku_id"], return_day,
                              "customer_return", quantity, "return", str(return_id),
                              "Resalable returned stock"))
        else:
            movements.append((movement_id, item["sku_id"], return_day,
                              "damaged_return", 0, "return", str(return_id),
                              "Returned item recorded as damaged and not added to stock"))
        return_id += 1
        movement_id += 1
    return rows, movements


def generate_expenses():
    rows = []
    expense_id = 1
    categories = {
        "Marketing": (1800, 5200),
        "Warehouse": (900, 2100),
        "Salaries": (5000, 8500),
        "Shipping": (700, 2400),
        "Platform": (250, 650),
        "Utilities": (180, 500),
        "Other": (150, 700),
    }
    for year in range(2023, 2027):
        for month in range(1, 13):
            first = month_start(year, month)
            for category, bounds in categories.items():
                amount = money(random.uniform(*bounds))
                day = min(random.randint(1, 28), calendar.monthrange(year, month)[1])
                expense_date = date(year, month, day)
                rows.append((expense_id, expense_date, first, category, amount,
                             f"Synthetic monthly {category.lower()} expense"))
                expense_id += 1
    return rows


def generate_targets(product_meta, product_sales):
    rows = []
    target_id = 1
    for year in range(2023, 2027):
        for month in range(1, 13):
            first = month_start(year, month)
            for product_id, meta in product_meta.items():
                if meta["launch"] > first + timedelta(days=27):
                    target_units = 0
                else:
                    historical_monthly_average = max(1, product_sales[product_id] // 48)
                    factor = seasonal_factor(meta["category"], month)
                    target_units = max(1, int(historical_monthly_average * factor * random.uniform(0.85, 1.35)))
                target_revenue = money(target_units * meta["price"] * random.uniform(0.94, 1.0))
                rows.append((target_id, first, product_id, target_units, target_revenue))
                target_id += 1
    return rows


def reset_and_create_tables(conn):
    with conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
        for table in TABLES_TO_RESET:
            cur.execute(sql.SQL("DROP TABLE IF EXISTS {} CASCADE").format(sql.Identifier(table)))
        cur.execute(SCHEMA_SQL)
    conn.commit()


def main():
    print("Starting MyFashionHub database generation...")
    ensure_database()
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
        user=DB_USER, password=DB_PASSWORD
    )
    conn.autocommit = False

    try:
        reset_and_create_tables(conn)
        print("Created database tables and relationships.")

        product_rows, product_meta = generate_products()
        variant_rows, variant_meta = generate_variants(product_meta)
        customer_rows, customer_meta = generate_customers()

        print("Generating 20,000 orders and their order items...")
        order_rows, item_rows, inventory_rows, item_meta, product_sales = generate_orders_and_items(
            customer_meta, variant_meta
        )

        print("Generating 10,000 verified synthetic reviews...")
        review_rows = generate_reviews(item_meta, product_meta)

        print("Generating returns, expenses and monthly targets...")
        return_rows, return_movements = generate_returns(item_meta, variant_meta)
        expense_rows = generate_expenses()
        target_rows = generate_targets(product_meta, product_sales)
        inventory_rows.extend(
            (len(inventory_rows) + i + 1, *movement[1:])
            for i, movement in enumerate(return_movements)
        )

        with conn.cursor() as cur:
            insert_many(cur, """
                INSERT INTO products
                (product_id, brand_name, product_name, category, product_type, target_gender,
                 description, base_price, production_cost, launch_date, product_status)
                VALUES %s
            """, product_rows)

            insert_many(cur, """
                INSERT INTO product_variants
                (sku_id, product_id, color, size, selling_price, unit_cost)
                VALUES %s
            """, variant_rows)

            insert_many(cur, """
                INSERT INTO customers
                (customer_id, first_name, last_name, email, country, gender, age_group,
                 customer_segment, registration_date)
                VALUES %s
            """, customer_rows)

            insert_many(cur, """
                INSERT INTO orders
                (order_id, customer_id, order_date, country, order_status, payment_status,
                 shipping_cost, created_at)
                VALUES %s
            """, order_rows)

            insert_many(cur, """
                INSERT INTO order_items
                (order_item_id, order_id, sku_id, product_id, quantity, unit_price,
                 discount_amount, line_revenue, unit_cost, line_cost)
                VALUES %s
            """, item_rows)

            insert_many(cur, """
                INSERT INTO reviews
                (review_id, customer_id, product_id, sku_id, order_item_id, review_date,
                 rating, review_text, review_type, verified_purchase, authenticity_label)
                VALUES %s
            """, review_rows)

            insert_many(cur, """
                INSERT INTO inventory_movements
                (movement_id, sku_id, movement_date, movement_type, quantity_change,
                 reference_type, reference_id, notes)
                VALUES %s
            """, inventory_rows)

            insert_many(cur, """
                INSERT INTO returns
                (return_id, order_item_id, return_date, quantity_returned, return_reason,
                 refund_amount, item_condition)
                VALUES %s
            """, return_rows)

            insert_many(cur, """
                INSERT INTO expenses
                (expense_id, expense_date, expense_month, expense_category, amount, description)
                VALUES %s
            """, expense_rows)

            insert_many(cur, """
                INSERT INTO monthly_targets
                (target_id, target_month, product_id, target_units, target_revenue)
                VALUES %s
            """, target_rows)

        conn.commit()
        print("\nDatabase generation completed successfully.")
        print(f"Database: {DB_NAME}")
        print("Records inserted:")
        print(f"  Products:              {len(product_rows):,}")
        print(f"  Product variants:      {len(variant_rows):,}")
        print(f"  Customers:             {len(customer_rows):,}")
        print(f"  Orders:                {len(order_rows):,}")
        print(f"  Order items:           {len(item_rows):,}")
        print(f"  Reviews:               {len(review_rows):,}")
        print(f"  Inventory movements:   {len(inventory_rows):,}")
        print(f"  Returns:               {len(return_rows):,}")
        print(f"  Expenses:              {len(expense_rows):,}")
        print(f"  Monthly targets:       {len(target_rows):,}")

        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    (SELECT COUNT(*) FROM products),
                    (SELECT COUNT(*) FROM product_variants),
                    (SELECT COUNT(*) FROM customers),
                    (SELECT COUNT(*) FROM orders),
                    (SELECT COUNT(*) FROM order_items),
                    (SELECT COUNT(*) FROM reviews)
            """)
            print("\nPostgreSQL verification:", cur.fetchone())

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
