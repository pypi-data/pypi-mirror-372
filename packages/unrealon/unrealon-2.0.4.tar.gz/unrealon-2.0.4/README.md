# 🚀 UnrealOn v2.0

**The easiest way to build production-ready web scrapers in Python.**

[![PyPI version](https://badge.fury.io/py/unrealon.svg)](https://badge.fury.io/py/unrealon)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Why UnrealOn?

**Stop fighting infrastructure. Start building parsers.**

```python
# Just focus on YOUR parsing logic
class MyParser:
    def __init__(self, driver):
        self.driver = driver
    
    async def parse_products(self, url: str):
        html = await self.driver.http.get_html(url)  # Auto proxy, retries, etc.
        soup = BeautifulSoup(html, 'html.parser')
        
        products = []
        for item in soup.select('.product'):
            products.append({
                'title': item.select_one('.title').text,
                'price': item.select_one('.price').text
            })
        
        return products  # Auto-saved, logged, monitored

# Everything else is handled automatically!
```

**What you get for free:**
- ✅ **HTTP Client** with proxy rotation, retries, rate limiting
- ✅ **Browser Automation** with stealth mode and anti-detection  
- ✅ **Error Handling** with automatic retries and graceful failures
- ✅ **Logging & Monitoring** with structured logs and performance metrics
- ✅ **CLI Interface** auto-generated from your parser methods
- ✅ **Configuration** with YAML files and validation
- ✅ **Production Deployment** with RPC server integration

---

## 📦 Installation

```bash
pip install unrealon
```

That's it! No complex setup, no configuration files to write.

---

## 🚀 Quick Start

### 1. Create Your Parser

```python
# my_parser.py
from unrealon_driver import UniversalDriver, DriverConfig
from bs4 import BeautifulSoup

class MyWebsiteParser:
    def __init__(self, driver: UniversalDriver):
        self.driver = driver
    
    async def parse_products(self, search_query: str):
        """Parse products from search results."""
        
        # UnrealOn handles all the HTTP complexity
        url = f"https://example.com/search?q={search_query}"
        html = await self.driver.http.get_html(url)
        
        # Focus on YOUR parsing logic
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        
        for item in soup.select('.product-item'):
            product = {
                'title': item.select_one('.title').text.strip(),
                'price': item.select_one('.price').text.strip(),
                'url': item.select_one('a')['href']
            }
            products.append(product)
        
        # Results are automatically saved and logged
        await self.driver.logger.info(f"Found {len(products)} products")
        return products

# Setup (one time)
config = DriverConfig.for_development("my_parser")
driver = UniversalDriver(config)
parser = MyWebsiteParser(driver)

# Use it
await driver.initialize()
results = await parser.parse_products("laptop")
print(f"Found {len(results)} products!")
```

### 2. Add CLI Interface (Optional)

```python
# cli.py
import click
from my_parser import MyWebsiteParser, driver

@click.command()
@click.option('--query', required=True, help='Search query')
@click.option('--limit', default=10, help='Max results')
def search(query: str, limit: int):
    """Search for products."""
    
    async def run():
        await driver.initialize()
        parser = MyWebsiteParser(driver)
        results = await parser.parse_products(query)
        
        for i, product in enumerate(results[:limit], 1):
            print(f"{i}. {product['title']} - {product['price']}")
        
        await driver.shutdown()
    
    import asyncio
    asyncio.run(run())

if __name__ == '__main__':
    search()
```

```bash
# Now you have a CLI!
python cli.py search --query "laptop" --limit 5
```

### 3. Production Deployment (Optional)

```python
# For production, just add RPC task decorators
class ProductionParser(UniversalDriver):
    def __init__(self):
        super().__init__(DriverConfig.for_production("my_parser"))
        self.parser = MyWebsiteParser(self)
    
    @self.task("parse_products")  # Auto-registered RPC task
    async def parse_products_task(self, task_data):
        query = task_data.parameters['query']
        results = await self.parser.parse_products(query)
        
        return TaskResultData(
            task_id=task_data.task_id,
            status="completed",
            result=results
        )

# Deploy and scale automatically!
```

---

## 🎨 Features

### 🔧 HTTP Client (Built-in)
```python
# All of this is handled automatically:
html = await driver.http.get_html(url)
# ✅ Proxy rotation
# ✅ User-Agent rotation  
# ✅ Automatic retries
# ✅ Rate limiting
# ✅ Cookie management
# ✅ Session persistence
```

### 🌐 Browser Automation (Built-in)
```python
# When you need a real browser:
page = await driver.browser.get_page(url)
await page.click('.load-more')
html = await page.content()
# ✅ Stealth mode
# ✅ Anti-detection
# ✅ JavaScript execution
# ✅ Screenshot capture
```

### 📊 Monitoring & Logging (Built-in)
```python
# Structured logging that just works:
await driver.logger.info("Starting parse", extra={
    'url': url,
    'products_found': len(products)
})
# ✅ Centralized logging
# ✅ Performance metrics
# ✅ Error tracking
# ✅ Real-time monitoring
```

### ⚙️ Configuration (Built-in)
```yaml
# config.yaml - Simple YAML configuration
parser:
  name: "My Parser"
  max_pages: 10
  
http:
  request_delay: 1.0
  max_retries: 3
  
output:
  format: json
  directory: ./results
```

### 🚀 Production Scaling (Built-in)
```python
# Scale to multiple instances automatically
@driver.task("parse_category")
async def parse_category_task(self, task_data):
    # This runs on any available parser instance
    category = task_data.parameters['category']
    return await self.parse_category(category)

# Deploy multiple instances, they auto-coordinate!
```

---

## 📚 Examples

### E-commerce Parser
```python
class EcommerceParser:
    async def parse_product(self, product_url: str):
        html = await self.driver.http.get_html(product_url)
        soup = BeautifulSoup(html, 'html.parser')
        
        return {
            'title': soup.select_one('h1').text,
            'price': soup.select_one('.price').text,
            'description': soup.select_one('.description').text,
            'images': [img['src'] for img in soup.select('.gallery img')]
        }
```

### News Scraper
```python
class NewsParser:
    async def parse_articles(self, category: str):
        url = f"https://news-site.com/{category}"
        html = await self.driver.http.get_html(url)
        soup = BeautifulSoup(html, 'html.parser')
        
        articles = []
        for article in soup.select('.article'):
            articles.append({
                'headline': article.select_one('.headline').text,
                'summary': article.select_one('.summary').text,
                'published': article.select_one('.date').text,
                'url': article.select_one('a')['href']
            })
        
        return articles
```

### Real Estate Listings
```python
class RealEstateParser:
    async def parse_listings(self, city: str, max_price: int):
        url = f"https://realestate.com/search?city={city}&max_price={max_price}"
        
        # Use browser for JavaScript-heavy sites
        page = await self.driver.browser.get_page(url)
        await page.wait_for_selector('.listing')
        
        listings = await page.evaluate('''
            () => Array.from(document.querySelectorAll('.listing')).map(listing => ({
                address: listing.querySelector('.address').textContent,
                price: listing.querySelector('.price').textContent,
                bedrooms: listing.querySelector('.bedrooms').textContent,
                url: listing.querySelector('a').href
            }))
        ''')
        
        return listings
```

---

## 🆚 Why Not Scrapy/BeautifulSoup/Selenium?

| Feature | UnrealOn | Scrapy | BeautifulSoup + Requests | Selenium |
|---------|----------|--------|-------------------------|----------|
| **Setup Time** | ✅ 5 minutes | ❌ Hours | ❌ Hours | ❌ Hours |
| **Proxy Rotation** | ✅ Built-in | ❌ Manual setup | ❌ Manual setup | ❌ Manual setup |
| **Anti-Detection** | ✅ Built-in | ❌ Manual setup | ❌ Manual setup | ❌ Partial |
| **Error Handling** | ✅ Built-in | ❌ Manual setup | ❌ Manual setup | ❌ Manual setup |
| **Monitoring** | ✅ Built-in | ❌ Manual setup | ❌ Manual setup | ❌ Manual setup |
| **CLI Generation** | ✅ Automatic | ❌ Manual | ❌ Manual | ❌ Manual |
| **Production Deploy** | ✅ Built-in | ❌ Complex | ❌ Very complex | ❌ Very complex |
| **Learning Curve** | ✅ Minimal | ❌ Steep | ❌ Medium | ❌ Steep |

**UnrealOn = All the power, none of the setup.**

---

## 🛠️ Advanced Features

### Type-Safe Data Models
```python
from pydantic import BaseModel
from typing import Optional

class Product(BaseModel):
    title: str
    price: Optional[float] = None
    url: str
    in_stock: bool = True

# Automatic validation and serialization
product = Product(title="Laptop", price=999.99, url="https://...")
```

### Scheduled Tasks
```python
@driver.schedule("0 */6 * * *")  # Every 6 hours
async def monitor_prices():
    """Monitor price changes automatically."""
    products = await parser.parse_products("laptop")
    # Check for price drops, send alerts, etc.
```

### Batch Processing
```python
async def parse_multiple_categories():
    categories = ["electronics", "books", "clothing"]
    
    # Process all categories concurrently
    tasks = [parser.parse_category(cat) for cat in categories]
    results = await driver.threads.submit_batch(tasks, max_workers=3)
    
    return results
```

---

## 🚀 Getting Started

1. **Install**: `pip install unrealon`
2. **Create parser**: Write your parsing logic (focus on the scraping, not infrastructure)
3. **Run**: `python my_parser.py` 
4. **Scale**: Add `@driver.task` decorators for production

### Complete Example Repository
- **[Amazon Parser](https://github.com/markolofsen/unrealon-parser-amazon)** - Production-ready Amazon scraper

---

## 📚 Documentation

- **[GitHub Repository](https://github.com/markolofsen/unrealon-parser-amazon)** - Source code and examples
- **[API Documentation](https://unrealon.com)** - Full API reference

---

## 🎉 Success Stories

### 🚗 CarAPIs - Automotive Data Platform
**[carapis.com](https://carapis.com)** - Vehicle listings from 50+ dealerships  
*"Went from prototype to production in 2 days with UnrealOn"*

### 🛒 ShopAPIs - E-commerce Intelligence  
**[shopapis.com](https://shopapis.com)** - Price monitoring across 100+ stores  
*"Handles 1M+ products daily with zero maintenance"*

### 📊 StockAPIs - Financial Data Platform
**[stockapis.com](https://stockapis.com)** - Real-time market data collection  
*"Rock-solid reliability for financial data that can't afford downtime"*

---

## 📄 License

MIT License - Use it however you want!

---

**Stop building infrastructure. Start building parsers.** 🚀