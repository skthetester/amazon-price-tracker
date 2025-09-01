import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import logging

class SlackNotifier:
    def __init__(self):
        self.client = WebClient(token=os.getenv('SLACK_BOT_TOKEN'))
        self.channel = os.getenv('SLACK_CHANNEL', '#price-alerts')
        self.logger = logging.getLogger(__name__)
    
    def send_price_drop_alert(self, product, old_price, new_price, price_change_percent):
        """Send alert when price drops significantly"""
        try:
            change_emoji = "📉" if new_price < old_price else "📈"
            price_diff = abs(new_price - old_price)
            
            message = f"""
{change_emoji} *Price Alert: {product.name}*

💰 *Price Change:* ${old_price:.2f} → ${new_price:.2f}
📊 *Change:* ${price_diff:.2f} ({price_change_percent:+.1f}%)
🎯 *Target Price:* ${product.target_price:.2f} {'✅' if product.target_price and new_price <= product.target_price else ''}

🔗 <{product.amazon_url}|View on Amazon>
📱 <http://localhost:5000/product/{product.id}|View Trends>
            """.strip()
            
            response = self.client.chat_postMessage(
                channel=self.channel,
                text=message,
                unfurl_links=False,
                unfurl_media=False
            )
            
            self.logger.info(f"Price alert sent for {product.name}")
            return True
            
        except SlackApiError as e:
            self.logger.error(f"Slack API error: {e.response['error']}")
            return False
        except Exception as e:
            self.logger.error(f"Error sending Slack notification: {e}")
            return False
    
    def send_target_price_alert(self, product):
        """Send alert when product reaches target price"""
        try:
            message = f"""
🎯 *Target Price Reached!*

*{product.name}*

💰 *Current Price:* ${product.current_price:.2f}
🎯 *Target Price:* ${product.target_price:.2f}
✅ *Savings:* ${product.target_price - product.current_price:.2f}

🔗 <{product.amazon_url}|Buy Now on Amazon>
📱 <http://localhost:5000/product/{product.id}|View Trends>
            """.strip()
            
            response = self.client.chat_postMessage(
                channel=self.channel,
                text=message,
                unfurl_links=False,
                unfurl_media=False
            )
            
            self.logger.info(f"Target price alert sent for {product.name}")
            return True
            
        except SlackApiError as e:
            self.logger.error(f"Slack API error: {e.response['error']}")
            return False
        except Exception as e:
            self.logger.error(f"Error sending Slack notification: {e}")
            return False
    
    def send_error_alert(self, product, error_message):
        """Send alert when scraping fails"""
        try:
            message = f"""
⚠️ *Scraping Error*

*Product:* {product.name}
*Error:* {error_message}
*URL:* {product.amazon_url}

Please check the product URL and try again.
            """.strip()
            
            response = self.client.chat_postMessage(
                channel=self.channel,
                text=message,
                unfurl_links=False,
                unfurl_media=False
            )
            
            self.logger.info(f"Error alert sent for {product.name}")
            return True
            
        except SlackApiError as e:
            self.logger.error(f"Slack API error: {e.response['error']}")
            return False
        except Exception as e:
            self.logger.error(f"Error sending Slack notification: {e}")
            return False
    
    def test_connection(self):
        """Test Slack connection"""
        try:
            response = self.client.auth_test()
            return response['ok']
        except SlackApiError as e:
            self.logger.error(f"Slack connection test failed: {e.response['error']}")
            return False
        except Exception as e:
            self.logger.error(f"Error testing Slack connection: {e}")
            return False
