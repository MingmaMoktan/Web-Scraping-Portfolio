import pandas as pd
import re
from bs4 import BeautifulSoup
from pathlib import Path

def parse_yellowpages_plumbers(html_file="yellowpages_plumbers.html"):
    """
    Parse Yellow Pages plumbers HTML and extract clean business data.
    FIXED: Proper phone number extraction with capture groups.
    """
    
    # Read HTML file
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    businesses = []
    
    # Target all listing containers
    listings = soup.find_all('div', class_=re.compile(r'srp-listing|result'))
    
    for i, listing in enumerate(listings):
        try:
            business = {}
            
            # Skip non-business listings
            if not listing.find('a', class_='business-name') and not listing.find('h2'):
                continue
                
            # BUSINESS NAME
            name_elem = (listing.find('a', class_='business-name') or 
                        listing.find('h2', class_='n') or 
                        listing.find('span', class_='business-name'))
            business['name'] = name_elem.get_text(strip=True) if name_elem else f"Business {i}"
            
            # CATEGORIES
            cats = listing.select('.categories a, .category a')
            business['categories'] = [c.get_text(strip=True) for c in cats if c.get_text(strip=True)]
            
            # RATING
            rating_elem = listing.find('div', class_=re.compile(r'result-rating'))
            if rating_elem:
                classes = rating_elem.get('class', [])
                if 'five' in classes:
                    business['rating'] = 5.0
                elif 'four' in classes:
                    business['rating'] = 4.0
                elif 'three' in classes:
                    business['rating'] = 3.0
                else:
                    business['rating'] = None
            else:
                business['rating'] = None
            
            # REVIEW COUNT
            review_span = listing.find('span', class_='count')
            business['review_count'] = (int(review_span.get_text(strip=True).rstrip('()')) 
                                     if review_span and review_span.get_text().strip('()').isdigit() 
                                     else None)
            
            # PHONE NUMBER - FIXED
            phone_elem = None
            phone_selectors = ['.phones .primary', '.phone', '[class*="phone"]']
            for selector in phone_selectors:
                phone_elem = listing.select_one(selector)
                if phone_elem:
                    break
            business['phone'] = phone_elem.get_text(strip=True) if phone_elem else None
            
            # ADDRESS
            address_elem = listing.find(class_='adr') or listing.select_one('.street-address')
            business['address'] = address_elem.get_text(strip=True) if address_elem else None
            
            # WEBSITE
            website_link = listing.find('a', rel='nofollow noopener') or listing.find('a', href=re.compile(r'http'))
            business['website'] = website_link['href'] if website_link and website_link.get('href') else None
            
            # IS AD
            business['is_ad'] = bool(listing.find('span', class_='ad-pill'))
            
            # OPEN STATUS
            open_elem = listing.find(class_=re.compile(r'open-status'))
            business['open_status'] = open_elem.get_text(strip=True) if open_elem else None
            
            # YEARS IN BUSINESS
            years_elem = listing.find(class_=re.compile(r'years-in-business'))
            if years_elem:
                years_match = re.search(r'(\d+)', years_elem.get_text())
                business['years_in_business'] = int(years_match.group(1)) if years_match else None
            else:
                business['years_in_business'] = None
            
            business['rank'] = len(businesses) + 1
            businesses.append(business)
            
        except Exception as e:
            print(f"Skipping malformed listing {i}: {e}")
            continue
    
    # Create DataFrame
    df = pd.DataFrame(businesses)
    df = df.dropna(subset=['name'], how='all')
    
    # FIXED PHONE CLEANING - Use simple replace instead of regex extract
    if 'phone' in df.columns:
        df['phone'] = df['phone'].astype(str).str.replace(r'[^\d\-\(\)\s\+]', '', regex=True)
        # Remove extra whitespace and None values
        df['phone'] = df['phone'].str.strip()
        df['phone'] = df['phone'].replace('', None)
    
    # Format categories
    df['categories'] = df['categories'].apply(lambda x: ', '.join(x) if isinstance(x, list) else str(x))
    
    # Convert numerics
    numeric_cols = ['rating', 'review_count', 'years_in_business']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df[['rank', 'name', 'categories', 'rating', 'review_count', 'phone', 
              'address', 'website', 'is_ad', 'open_status', 'years_in_business']]

def save_and_analyze(file_path="yellowpages_plumbers.html"):
    """Parse, clean, save, and show analysis."""
    
    print("🔍 Parsing Yellow Pages plumbers data...")
    df = parse_yellowpages_plumbers(file_path)
    
    # Save clean CSV
    output_file = "la_plumbers_clean.csv"
    df.to_csv(output_file, index=False)
    print(f"✅ Saved {len(df)} businesses to {output_file}")
    
    # Quick analysis
    print("\n📊 QUICK ANALYSIS")
    print(f"Total businesses: {len(df)}")
    print(f"Ads: {df['is_ad'].sum()}/{len(df)} ({df['is_ad'].mean():.1%})")
    print(f"With phones: {df['phone'].notna().sum()}")
    print(f"With websites: {df['website'].notna().sum()}")
    print(f"Avg rating: {df['rating'].mean():.1f} stars" if df['rating'].notna().sum() > 0 else "No ratings found")
    
    print("\n🏆 TOP 5 LISTINGS")
    print(df.head().to_string(index=False))
    
    return df

# Run it!
if __name__ == "__main__":
    df = save_and_analyze("yellowpages_plumbers.html")