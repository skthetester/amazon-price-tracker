from database.models import db, Product, PriceHistory, get_est_now
from datetime import datetime, timedelta
import statistics
import pytz

# EST timezone
EST = pytz.timezone('US/Eastern')

class DatabaseManager:
    
    @staticmethod
    def add_product(name, amazon_url, asin, target_price=None, image_url=None):
        """Add a new product to track"""
        product = Product(
            name=name,
            amazon_url=amazon_url,
            asin=asin,
            target_price=target_price,
            image_url=image_url
        )
        db.session.add(product)
        db.session.commit()
        return product
    
    @staticmethod
    def get_all_products():
        """Get all active products"""
        return Product.query.filter_by(is_active=True).all()
    
    @staticmethod
    def get_product_by_id(product_id):
        """Get product by ID"""
        return Product.query.get(product_id)
    
    @staticmethod
    def get_product_by_asin(asin):
        """Get product by ASIN"""
        return Product.query.filter_by(asin=asin).first()
    
    @staticmethod
    def update_product_price(product_id, new_price):
        """Update current price and add to price history"""
        product = Product.query.get(product_id)
        if product:
            # Add to price history
            price_entry = PriceHistory(product_id=product_id, price=new_price)
            db.session.add(price_entry)
            
            # Update current price
            product.current_price = new_price
            product.updated_at = get_est_now()
            
            db.session.commit()
            return product
        return None
    
    @staticmethod
    def delete_product(product_id):
        """Soft delete a product"""
        product = Product.query.get(product_id)
        if product:
            product.is_active = False
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def get_price_history(product_id, days=30):
        """Get price history for a product"""
        cutoff_date = get_est_now() - timedelta(days=days)
        return PriceHistory.query.filter(
            PriceHistory.product_id == product_id,
            PriceHistory.timestamp >= cutoff_date
        ).order_by(PriceHistory.timestamp.desc()).all()
    
    @staticmethod
    def get_price_trend(product_id):
        """Get price trend for a product (last 2 price points)"""
        recent_prices = PriceHistory.query.filter_by(product_id=product_id)\
            .order_by(PriceHistory.timestamp.desc()).limit(2).all()
        
        if len(recent_prices) < 2:
            return {'trend': 'neutral', 'change': 0, 'change_percent': 0}
        
        current_price = recent_prices[0].price
        previous_price = recent_prices[1].price
        
        change = current_price - previous_price
        change_percent = (change / previous_price) * 100 if previous_price > 0 else 0
        
        if change > 0:
            trend = 'up'
        elif change < 0:
            trend = 'down'
        else:
            trend = 'neutral'
        
        return {
            'trend': trend,
            'change': change,
            'change_percent': change_percent,
            'current_price': current_price,
            'previous_price': previous_price
        }
    
    @staticmethod
    def get_price_statistics(product_id, days=30):
        """Get price statistics for a product"""
        history = DatabaseManager.get_price_history(product_id, days)
        if not history:
            return None
        
        prices = [entry.price for entry in history]
        current_price = prices[0] if prices else 0
        
        stats = {
            'current_price': current_price,
            'min_price': min(prices),
            'max_price': max(prices),
            'avg_price': statistics.mean(prices),
            'price_points': len(prices),
            'days_tracked': days
        }
        
        # Calculate price change from first recorded price
        if len(prices) > 1:
            first_price = prices[-1]
            price_change = current_price - first_price
            price_change_percent = (price_change / first_price) * 100
            stats['price_change'] = price_change
            stats['price_change_percent'] = price_change_percent
        else:
            stats['price_change'] = 0
            stats['price_change_percent'] = 0
            
        return stats
