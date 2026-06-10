#!/usr/bin/env python3
"""
Dono bots ko ek saath ek hi process me chalata hai.
Railway/Render pe deploy karne ke liye YE FILE use karo.
"""
import subprocess
import sys
import os

def main():
    base = os.path.dirname(os.path.abspath(__file__))
    
    procs = [
        subprocess.Popen([sys.executable, os.path.join(base, "payment_bot", "bot.py")]),
        subprocess.Popen([sys.executable, os.path.join(base, "file_bot", "bot.py")]),
    ]
    
    print("✅ Payment Bot + File Bot — dono chal rahe hain!")
    
    try:
        for p in procs:
            p.wait()
    except KeyboardInterrupt:
        print("\n🛑 Bots band ho rahe hain...")
        for p in procs:
            p.terminate()

if __name__ == "__main__":
    main()
