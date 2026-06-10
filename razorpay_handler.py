import razorpay
import logging
import config

logger = logging.getLogger(__name__)

client = razorpay.Client(auth=(config.RAZORPAY_KEY_ID, config.RAZORPAY_KEY_SECRET))

def create_order(amount_inr: int, user_id: int, days: int):
    """Razorpay order create karo"""
    try:
        order_data = {
            "amount": amount_inr * 100,  # Paise me convert karo
            "currency": "INR",
            "receipt": f"user_{user_id}_days_{days}",
            "notes": {
                "user_id": str(user_id),
                "days": str(days)
            }
        }
        order = client.order.create(data=order_data)
        logger.info(f"Order created: {order['id']} for user {user_id}")
        return order
    except Exception as e:
        logger.error(f"Order create error: {e}")
        return None

def verify_payment(order_id: str) -> bool:
    """Check karo ki order paid hai ya nahi"""
    try:
        payments = client.order.payments(order_id)
        
        if not payments or 'items' not in payments:
            return False
        
        for payment in payments['items']:
            if payment['status'] == 'captured':
                logger.info(f"Payment verified for order: {order_id}")
                return True
        
        return False
    except Exception as e:
        logger.error(f"Payment verify error: {e}")
        return False
