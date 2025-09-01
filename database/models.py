from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz

db = SQLAlchemy()

# EST timezone
EST = pytz.timezone('US/Eastern')

def get_est_now():
    """Get current time in EST"""
    return datetime.now(EST)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    amazon_url = db.Column(db.Text, nullable=False)
    asin = db.Column(db.String(20), unique=True, nullable=False)
    target_price = db.Column(db.Float, nullable=True)
    current_price = db.Column(db.Float, nullable=True)
    image_url = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=get_est_now)
    updated_at = db.Column(db.DateTime, default=get_est_now, onupdate=get_est_now)
    
    # Relationship
    price_history = db.relationship('PriceHistory', backref='product', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Product {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'amazon_url': self.amazon_url,
            'asin': self.asin,
            'target_price': self.target_price,
            'current_price': self.current_price,
            'image_url': self.image_url,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class PriceHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=get_est_now)
    
    def __repr__(self):
        return f'<PriceHistory {self.product_id}: ${self.price}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'price': self.price,
            'timestamp': self.timestamp.isoformat()
        }
