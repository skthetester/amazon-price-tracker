#!/usr/bin/env python3
"""
Amazon Price Tracker - Main Flask Application

This file is part of the Amazon Price Tracker project.
Licensed under the MIT License - see LICENSE file for details.

A web application for tracking Amazon product prices with notifications and trend analysis.
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from database.models import db, Product, PriceHistory, get_est_now
from database.db_manager import DatabaseManager
from scraper.amazon_scraper import AmazonScraper
from notifications.slack_notifier import SlackNotifier
from config.settings import Config
import plotly.graph_objects as go
import plotly.utils
import json
from datetime import datetime, timedelta
import logging
import pytz

# EST timezone
EST = pytz.timezone('US/Eastern')

# Create Flask app with correct template and static directories
app = Flask(__name__, 
           template_folder=os.path.join(project_root, 'templates'),
           static_folder=os.path.join(project_root, 'static'))
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Make zip function available in templates
app.jinja_env.globals.update(zip=zip)

# Initialize components
scraper = AmazonScraper()
slack_notifier = SlackNotifier()

# Initialize and start price scheduler
from scraper.scheduler import PriceScheduler
price_scheduler = PriceScheduler(app)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Template filters
@app.template_filter('est_datetime')
def est_datetime_filter(dt):
    """Format datetime in EST with timezone indicator"""
    if dt.tzinfo is None:
        # If datetime is naive, assume it's already in EST
        return dt.strftime('%m/%d/%Y %I:%M %p EST')
    else:
        # Convert to EST if timezone-aware
        est_dt = dt.astimezone(EST)
        return est_dt.strftime('%m/%d/%Y %I:%M %p EST')

@app.template_filter('est_date')
def est_date_filter(dt):
    """Format date in EST"""
    if dt.tzinfo is None:
        return dt.strftime('%m/%d/%Y EST')
    else:
        est_dt = dt.astimezone(EST)
        return est_dt.strftime('%m/%d/%Y EST')

@app.template_filter('est_time')
def est_time_filter(dt):
    """Format time in EST"""
    if dt.tzinfo is None:
        return dt.strftime('%I:%M %p EST')
    else:
        est_dt = dt.astimezone(EST)
        return est_dt.strftime('%I:%M %p EST')

# Create application context
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    """Main page - list all tracked products"""
    products = DatabaseManager.get_all_products()
    
    # Add trend data for each product
    products_with_trends = []
    for product in products:
        trend_data = DatabaseManager.get_price_trend(product.id)
        product_dict = product.to_dict()
        product_dict['trend'] = trend_data
        products_with_trends.append(product_dict)
    
    return render_template('index.html', products=products, products_with_trends=products_with_trends)

@app.route('/manage')
def manage():
    """Manage products page"""
    products = DatabaseManager.get_all_products()
    return render_template('manage.html', products=products)

@app.route('/add_product', methods=['POST'])
def add_product():
    """Add a new product to track"""
    try:
        name = request.form.get('name')
        amazon_url = request.form.get('amazon_url')
        target_price = request.form.get('target_price')
        
        if not name or not amazon_url:
            flash('Name and Amazon URL are required!', 'error')
            return redirect(url_for('manage'))
        
        # Extract ASIN from URL
        asin = scraper.extract_asin_from_url(amazon_url)
        if not asin:
            flash('Could not extract ASIN from Amazon URL!', 'error')
            return redirect(url_for('manage'))
        
        # Check if product already exists
        existing_product = DatabaseManager.get_product_by_asin(asin)
        if existing_product:
            flash('This product is already being tracked!', 'error')
            return redirect(url_for('manage'))
        
        # Scrape initial product info
        product_info = scraper.scrape_product(amazon_url)
        if product_info and product_info.get('name'):
            name = product_info['name']  # Use scraped name
        
        # Parse target price
        target_price_float = None
        if target_price:
            try:
                target_price_float = float(target_price)
            except ValueError:
                flash('Invalid target price!', 'error')
                return redirect(url_for('manage'))
        
        # Add product
        product = DatabaseManager.add_product(
            name=name,
            amazon_url=amazon_url,
            asin=asin,
            target_price=target_price_float,
            image_url=product_info.get('image_url') if product_info else None
        )
        
        # Add initial price if available
        if product_info and product_info.get('price'):
            DatabaseManager.update_product_price(product.id, product_info['price'])
        
        flash(f'Product "{name}" added successfully!', 'success')
        
    except Exception as e:
        logger.error(f"Error adding product: {e}")
        flash('Error adding product. Please try again.', 'error')
    
    return redirect(url_for('manage'))

@app.route('/edit_product/<int:product_id>', methods=['POST'])
def edit_product(product_id):
    """Edit an existing product"""
    try:
        product = DatabaseManager.get_product_by_id(product_id)
        if not product:
            flash('Product not found!', 'error')
            return redirect(url_for('manage'))
        
        name = request.form.get('name')
        target_price = request.form.get('target_price')
        
        if name:
            product.name = name
        
        if target_price:
            try:
                product.target_price = float(target_price)
            except ValueError:
                flash('Invalid target price!', 'error')
                return redirect(url_for('manage'))
        
        product.updated_at = get_est_now()
        db.session.commit()
        
        flash(f'Product "{product.name}" updated successfully!', 'success')
        
    except Exception as e:
        logger.error(f"Error editing product: {e}")
        flash('Error updating product. Please try again.', 'error')
    
    return redirect(url_for('manage'))

@app.route('/delete_product/<int:product_id>')
def delete_product(product_id):
    """Delete a product"""
    try:
        success = DatabaseManager.delete_product(product_id)
        if success:
            flash('Product deleted successfully!', 'success')
        else:
            flash('Product not found!', 'error')
    except Exception as e:
        logger.error(f"Error deleting product: {e}")
        flash('Error deleting product. Please try again.', 'error')
    
    return redirect(url_for('manage'))

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """Product detail page with price trends"""
    product = DatabaseManager.get_product_by_id(product_id)
    if not product:
        flash('Product not found!', 'error')
        return redirect(url_for('index'))
    
    # Get price history and statistics
    price_history = DatabaseManager.get_price_history(product_id, days=30)
    stats = DatabaseManager.get_price_statistics(product_id, days=30)
    
    # Create price chart
    chart_json = None
    if price_history:
        dates = [entry.timestamp for entry in reversed(price_history)]
        prices = [entry.price for entry in reversed(price_history)]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=prices,
            mode='lines+markers',
            name='Price',
            line=dict(color='#1f77b4', width=2),
            marker=dict(size=6)
        ))
        
        # Add target price line if set
        if product.target_price:
            fig.add_hline(
                y=product.target_price,
                line_dash="dash",
                line_color="red",
                annotation_text=f"Target: ${product.target_price:.2f}"
            )
        
        fig.update_layout(
            title=f'Price History - {product.name}',
            xaxis_title='Date',
            yaxis_title='Price ($)',
            hovermode='x unified',
            template='plotly_white'
        )
        
        chart_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return render_template('product_detail.html', 
                         product=product, 
                         price_history=price_history[:10],  # Show last 10 entries
                         stats=stats,
                         chart_json=chart_json)

@app.route('/check_all_prices')
def check_all_prices():
    """Manually trigger price check for all products"""
    try:
        products = DatabaseManager.get_all_products()
        updated_count = 0
        error_count = 0
        
        for product in products:
            try:
                # Scrape current price
                product_info = scraper.scrape_product(product.amazon_url)
                
                if product_info and product_info.get('price'):
                    old_price = product.current_price
                    new_price = product_info['price']
                    
                    # Update price in database
                    DatabaseManager.update_product_price(product.id, new_price)
                    updated_count += 1
                    
                    # Check for significant price change
                    if old_price and abs(new_price - old_price) / old_price * 100 >= Config.PRICE_CHANGE_THRESHOLD:
                        price_change_percent = ((new_price - old_price) / old_price) * 100
                        if Config.ENABLE_SLACK_NOTIFICATIONS:
                            slack_notifier.send_price_drop_alert(product, old_price, new_price, price_change_percent)
                    
                    # Check if target price reached
                    if product.target_price and new_price <= product.target_price:
                        if Config.ENABLE_SLACK_NOTIFICATIONS:
                            slack_notifier.send_target_price_alert(product)
                else:
                    error_count += 1
                    logger.warning(f"Could not scrape price for {product.name}")
                    
            except Exception as e:
                error_count += 1
                logger.error(f"Error scraping product {product.id}: {e}")
        
        if error_count == 0:
            flash(f'Successfully updated prices for all {updated_count} products!', 'success')
        else:
            flash(f'Updated {updated_count} products. {error_count} products had errors.', 'warning')
            
    except Exception as e:
        logger.error(f"Error in check_all_prices: {e}")
        flash('Error checking prices. Please try again.', 'error')
    
    return redirect(url_for('index'))

@app.route('/scrape_now/<int:product_id>')
def scrape_now(product_id):
    """Manually trigger scraping for a product"""
    try:
        product = DatabaseManager.get_product_by_id(product_id)
        if not product:
            flash('Product not found!', 'error')
            return redirect(url_for('index'))
        
        # Scrape current price
        product_info = scraper.scrape_product(product.amazon_url)
        
        if product_info and product_info.get('price'):
            old_price = product.current_price
            new_price = product_info['price']
            
            # Update price in database
            DatabaseManager.update_product_price(product_id, new_price)
            
            # Check for significant price change
            if old_price and abs(new_price - old_price) / old_price * 100 >= Config.PRICE_CHANGE_THRESHOLD:
                price_change_percent = ((new_price - old_price) / old_price) * 100
                if Config.ENABLE_SLACK_NOTIFICATIONS:
                    slack_notifier.send_price_drop_alert(product, old_price, new_price, price_change_percent)
            
            # Check if target price reached
            if product.target_price and new_price <= product.target_price:
                if Config.ENABLE_SLACK_NOTIFICATIONS:
                    slack_notifier.send_target_price_alert(product)
            
            flash(f'Price updated: ${new_price:.2f}', 'success')
        else:
            flash('Could not scrape current price. Please try again later.', 'error')
            
    except Exception as e:
        logger.error(f"Error scraping product {product_id}: {e}")
        flash('Error scraping product. Please try again.', 'error')
    
    return redirect(url_for('product_detail', product_id=product_id))

@app.route('/api/products')
def api_products():
    """API endpoint to get all products"""
    products = DatabaseManager.get_all_products()
    return jsonify([product.to_dict() for product in products])

@app.route('/api/product/<int:product_id>/history')
def api_product_history(product_id):
    """API endpoint to get product price history"""
    days = request.args.get('days', 30, type=int)
    history = DatabaseManager.get_price_history(product_id, days)
    return jsonify([entry.to_dict() for entry in history])

@app.route('/api/scheduler/status')
def scheduler_status():
    """API endpoint to get scheduler status"""
    try:
        status = price_scheduler.get_scheduler_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/slack/test')
def test_slack():
    """Test Slack connection and send a test message"""
    try:
        # Test connection
        connection_ok = slack_notifier.test_connection()
        
        if not connection_ok:
            return jsonify({
                'success': False,
                'message': 'Slack connection failed. Check your SLACK_BOT_TOKEN.'
            }), 400
        
        # Send test message
        from database.models import Product
        test_product = Product(
            name="Test Product",
            amazon_url="https://amazon.com/test",
            current_price=99.99,
            target_price=85.00
        )
        
        success = slack_notifier.send_price_drop_alert(
            test_product, 
            old_price=109.99, 
            new_price=99.99, 
            price_change_percent=-9.1
        )
        
        return jsonify({
            'success': success,
            'message': 'Test notification sent!' if success else 'Failed to send test notification'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000)
