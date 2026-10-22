import re
import csv

HTML_FILE = "test_shop.html"
CSV_FILE = "products.csv"

html = """<!DOCTYPE html>
<html>
<head><title>Test Shop</title></head>
<body>
<div class="product">
  <h2 class="title">Ноутбук ASUS VivoBook</h2>
  <span class="price">49 990 ₽</span>
  <span class="old-price">59 990 ₽</span>
  <div class="rating">★★★★☆ <span class="reviews">(128 отзывов)</span></div>
  <span class="sku">SKU: NB-28471</span>
</div>
<div class="product">
  <h2 class="title">Смартфон Samsung Galaxy</h2>
  <span class="price">32 500руб</span>
  <div class="rating">★★★★★ <span class="reviews">(542 отзыва)</span></div>
  <span class="sku">SKU: SM-99312</span>
</div>
<div class="product">
  <h2 class="title">Наушники Sony WH-1000XM4</h2>
  <span class="price">$299.99</span>
  <div class="rating">★★★☆☆ <span class="reviews">(89 reviews)</span></div>
  <span class="sku">SKU: SN-44100</span>
</div>
<div class="product">
  <h2 class="title">Клавиатура Logitech MX Keys</h2>
  <span class="price">12 499 руб.</span>
  <div class="rating">★★★★☆ <span class="reviews">(215 отзывов)</span></div>
  <span class="sku">SKU: LG-77201</span>
</div>
<div class="product">
  <h2 class="title">Товар без цены</h2>
  <div class="rating">★★★★★ <span class="reviews">(10 отзывов)</span></div>
  <span class="sku">SKU: XX-00000</span>
</div>
<div class="product">
  <h2 class="title">Товар без SKU</h2>
  <span class="price">1 000 ₽</span>
  <div class="rating">★★☆☆☆ <span class="reviews">(5 отзывов)</span></div>
</div>
<div class="product">
  <h2 class="title">Битый SKU</h2>
  <span class="price">500 ₽</span>
  <div class="rating">★★★★☆ <span class="reviews">(30 отзывов)</span></div>
  <span class="sku">SKU: bad_sku</span>
</div>
</body>
</html>"""

with open(HTML_FILE, "w", encoding="utf-8") as f:
    f.write(html)

with open(HTML_FILE, "r", encoding="utf-8") as f:
    html = f.read()

products = re.findall(r'<div class="product">(.*?)</div>', html, re.DOTALL)

results = []
invalid_skus = 0
missing_fields = 0

for p in products:
    title_m = re.search(r'<h2 class="title">(.*?)</h2>', p)
    price_m = re.search(r'class="price">([\d\s,.]+(?:[₽$]|руб\.?))', p)
    old_price_m = re.search(r'class="old-price">([\d\s,.]+(?:[₽$]|руб\.?))', p)
    rating_m = re.search(r"([★]+)[☆]*", p)
    reviews_m = re.search(r"\((\d+)\s+(?:отзыв[а-я]*|reviews?)\)", p)
    sku_m = re.search(r"SKU:\s*([A-Z]{2}-\d{5})", p)
    sku_raw_m = re.search(r"SKU:\s*(\S+)", p)

    title = title_m.group(1).strip() if title_m else None
    price_raw = price_m.group(1).strip() if price_m else None
    old_price_raw = old_price_m.group(1).strip() if old_price_m else None
    rating = len(rating_m.group(1)) if rating_m else 0
    reviews = int(reviews_m.group(1)) if reviews_m else 0
    sku = sku_m.group(1) if sku_m else None
    sku_raw = sku_raw_m.group(1) if sku_raw_m else None

    if not sku and sku_raw:
        invalid_skus += 1

    if not price_raw or not sku:
        missing_fields += 1

    def normalize_price(raw):
        if not raw:
            return None
        cleaned = re.sub(r"[^\d.,]", "", raw)
        cleaned = cleaned.replace(" ", "").replace(",", ".")
        try:
            return float(cleaned)
        except ValueError:
            return None

    results.append(
        {
            "title": title,
            "price_raw": price_raw,
            "price": normalize_price(price_raw),
            "old_price_raw": old_price_raw,
            "old_price": normalize_price(old_price_raw),
            "rating": rating,
            "reviews": reviews,
            "sku": sku,
            "sku_valid": bool(sku),
        }
    )

with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "title",
            "price_raw",
            "price",
            "old_price_raw",
            "old_price",
            "rating",
            "reviews",
            "sku",
            "sku_valid",
        ],
    )
    writer.writeheader()
    writer.writerows(results)

prices = [r["price"] for r in results if r["price"] is not None]

print(f"Всего товаров: {len(results)}")
print(f"Валидных SKU: {sum(1 for r in results if r['sku_valid'])}")
print(f"Невалидных SKU: {invalid_skus}")
print(f"Товаров с пропущенными полями: {missing_fields}")
print(f"Средняя цена: {sum(prices) / len(prices):.2f}" if prices else "Цен нет")
print(f"Макс. цена: {max(prices):.2f}" if prices else "")
print(f"Мин. цена: {min(prices):.2f}" if prices else "")
print(f"\nCSV сохранён: {CSV_FILE}")
