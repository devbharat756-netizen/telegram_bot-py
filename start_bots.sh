#!/bin/bash
# Dono bots ek saath chalao

echo "🤖 Bot System Start Ho Raha Hai..."

# Install karo agar pehli baar hai
pip install -r requirements.txt -q

# Payment Bot background me chalao
echo "💳 Payment Bot chal raha hai..."
cd payment_bot && python bot.py &
PAYMENT_PID=$!

# File Bot background me chalao
echo "📁 File Bot chal raha hai..."
cd ../file_bot && python bot.py &
FILE_PID=$!

echo "✅ Dono Bots Chal Rahe Hain!"
echo "Payment Bot PID: $PAYMENT_PID"
echo "File Bot PID: $FILE_PID"
echo ""
echo "Bots band karne ke liye: Ctrl+C"

# Wait karo
wait
