import re
from bs4 import BeautifulSoup
import pandas as pd

# Read the HTML content from paste.txt
with open('data.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, 'html.parser')

# Find all product cards
product_cards = soup.find_all('article', class_='product-card')

products = []

for card in product_cards:
    product = {}
    
    # Product name and URL
    link = card.find('a', class_='no-style-link')
    if link:
        product['url'] = link.get('href', '')
        name_elem = card.find('h3')
        product['name'] = name_elem.get_text(strip=True) if name_elem else 'Unknown'
    
    # Product ID
    wishlist_btn = card.find('a', class_='wl-add-to')
    product['product_id'] = wishlist_btn.get('data-productid', '') if wishlist_btn else ''
    
    # Images
    images = card.find_all('img', class_='lozad')
    if images:
        product['main_image'] = images[0].get('data-srcset', '').split(',')[0].split()[0] if images else ''
        product['hover_image'] = images[1].get('data-srcset', '').split(',')[0].split()[0] if len(images) > 1 else ''
    
    # Color swatches
    swatches = card.find_all('img', class_='product-card-swatch')
    colors = []
    for swatch in swatches:
        color_url = swatch.get('data-breeze', '')
        if color_url:
            color_match = re.search(r'/([^/-]+)(-\d+x\d+)?-', color_url)
            if color_match:
                colors.append(color_match.group(1).replace('-', ' ').title())
    product['colors'] = ', '.join(colors)
    
    # Category from URL
    if product['url']:
        cat_match = re.search(r'/product(?:/[^/]+)*/([^/]+)/?', product['url'])
        product['category'] = cat_match.group(1).replace('-', ' ').title() if cat_match else 'Products'
    
    products.append(product)

# Convert to DataFrame and save CSV
df = pd.DataFrame(products)

# Select and reorder columns
df = df[['name', 'product_id', 'url', 'main_image', 'hover_image', 'colors', 'category']]

# Save to CSV (no index)
df.to_csv('frovi_products.csv', index=False, encoding='utf-8')

print(f"✅ SAVED {len(df)} products to frovi_products.csv")
print("\n📊 Preview:")
print(df[['name', 'product_id', 'category']].to_string(index=False))
