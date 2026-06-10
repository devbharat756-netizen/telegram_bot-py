import os

# ============================================================
#   Render pe Environment Variables se values aayengi
# ============================================================

PAYMENT_BOT_TOKEN     = os.environ.get("PAYMENT_BOT_TOKEN", "")
FILE_BOT_TOKEN        = os.environ.get("FILE_BOT_TOKEN", "")

PAYMENT_BOT_USERNAME  = os.environ.get("PAYMENT_BOT_USERNAME", "YourPaymentBot")
FILE_BOT_USERNAME     = os.environ.get("FILE_BOT_USERNAME", "YourFileBot")

# ADMIN_IDS — comma separated: "123456,789012"
_admin_raw = os.environ.get("ADMIN_IDS", "123456789")
ADMIN_IDS = [int(x.strip()) for x in _admin_raw.split(",")]

RAZORPAY_KEY_ID       = os.environ.get("RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET   = os.environ.get("RAZORPAY_KEY_SECRET", "")
RAZORPAY_PAYMENT_LINK = os.environ.get("RAZORPAY_PAYMENT_LINK", "")

# Supabase / PostgreSQL
DATABASE_URL          = os.environ.get("DATABASE_URL", "")


if not DATABASE_URL:
    raise Exception('DATABASE_URL missing')
