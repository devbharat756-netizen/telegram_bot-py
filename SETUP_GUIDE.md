# 📖 Bot Setup Guide — Step by Step (Hindi)

---

## ✅ Step 1 — Dono Bots Banao (Telegram pe)

1. Telegram kholो aur **@BotFather** search karo
2. `/newbot` bhejo
3. Bot ka naam do (e.g. "My Premium Content")
4. Bot ka username do (e.g. "MyPremiumPayBot") — **ye copy kar lo**
5. BotFather ek **TOKEN** dega — isko copy karo (bahut zaroori hai)
6. Ye process dobara karo **doosre bot ke liye bhi** (File Bot)

---

## ✅ Step 2 — Apna Telegram User ID Nikalo

1. Telegram pe **@userinfobot** search karo
2. `/start` bhejo
3. Wo aapka **ID number** batayega (e.g. 987654321)
4. Ye number `config.py` me `ADMIN_IDS` me daalna hai

---

## ✅ Step 3 — Razorpay Account Banao

1. **razorpay.com** pe jaao → Sign Up karo (free hai)
2. Dashboard → **Settings → API Keys**
3. **"Generate Key"** click karo
4. `Key ID` aur `Key Secret` copy karo
5. **Payment Links** section me jaao → ek payment link banao
   - Amount: variable rakhna (user khud choose kare)
   - Ya teen alag links banao (₹50, ₹299, ₹399)
6. Us link ko `RAZORPAY_PAYMENT_LINK` me daalo

---

## ✅ Step 4 — config.py Fill Karo

`config.py` file kholो aur ye saari cheezein bharo:

```python
PAYMENT_BOT_TOKEN = "1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ"  # BotFather se
FILE_BOT_TOKEN    = "0987654321:ZYXwvuTSRqpoNMLkjiHGFedcBA"  # BotFather se

PAYMENT_BOT_USERNAME = "MyPremiumPayBot"   # @ ke bina
FILE_BOT_USERNAME    = "MyPremiumFileBot"  # @ ke bina

ADMIN_IDS = [987654321]  # Aapka Telegram ID

RAZORPAY_KEY_ID     = "rzp_live_abcXYZ123"
RAZORPAY_KEY_SECRET = "secretkey123abc"
RAZORPAY_PAYMENT_LINK = "https://rzp.io/l/yourlink"
```

---

## ✅ Step 5 — Railway.app pe Free Deploy Karo

1. **railway.app** pe jaao → GitHub se Sign Up karo
2. **"New Project"** → **"Deploy from GitHub repo"**
3. Ye folder GitHub pe upload karo (GitHub Desktop use karo — free & easy)
4. Railway automatically detect karega aur deploy karega
5. **Environment Variables** me jaao aur saare config values daalo
   (config.py ki jagah environment variables use karna zyada safe hai)

---

## ✅ Step 6 — Files Add Karo (Bahut Asaan!)

File Bot me files add karne ka tarika:

1. **File Bot** pe jaao (admin hoke)
2. Ye command do:
   ```
   /addfile Meri PDF Book | Ye ek bahut achhi book hai | pdf
   ```
3. Bot bolega "ab file bhejo"
4. Apni PDF / Video / Image bhejo
5. **Done!** ✅ Ab ye file saare premium users ko dikhegi

### Saari Files Dekhne ke Liye:
```
/listfiles
```

### File Delete Karne ke Liye:
```
/deletefile FILE_ID
```

---

## 🔄 System Kaise Kaam Karta Hai

```
User → Payment Bot → Plan Choose Kare
     → Razorpay pe Payment Kare
     → Auto Verify Ho
     → File Bot ka Access Mile
     → Files Dekhe / Download Kare / Forward Kare
     → Plan Expire → Access Khatam
```

---

## ❓ Common Problems

**Q: Bot respond nahi kar raha**
→ Token sahi se copy kiya? Extra space to nahi?

**Q: Payment verify nahi ho rahi**
→ Razorpay Test Mode OFF karo, Live Mode ON karo

**Q: Files nahi dikh rahi**
→ Pehle /addfile command se file add karo

**Q: Railway pe deploy kaise karein**
→ YouTube pe "Railway app deploy Python bot" search karo

---

## 📞 Kuch Problem Ho To

config.py me `ADMIN_IDS` me apna ID daala hai na?
Wo sahi se daala hai tabhi /addfile kaam karega!
