import sqlite3

# ১. ডেটাবেস ফাইল তৈরি করা (ScamGuard.db নামে একটি ফাইল তৈরি হবে)
conn = sqlite3.connect("ScamGuard.db")
cursor = conn.cursor()

# ২. ফ্রড UPI এবং ফোন নম্বর সেভ করার জন্য একটি টেবিল তৈরি করা
cursor.execute('''
    CREATE TABLE IF NOT EXISTS fraud_list (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scam_data TEXT UNIQUE,
        scam_type TEXT
    )
''')

# ৩. কিছু ডামি ফ্রড ডেটা আগে থেকেই টেবিলে ঢুকিয়ে রাখা (টেস্ট করার জন্য)
dummy_frauds = [
    ('win-prize@ybl', 'UPI_ID'),
    ('sbi-refund-fraud39@ybl', 'UPI_ID'),
    ('9876543210', 'PHONE_NUMBER')
]

try:
    cursor.executemany("INSERT OR IGNORE INTO fraud_list (scam_data, scam_type) VALUES (?, ?)", dummy_frauds)
    conn.commit()
    print("[+] ScamGuard Local Database successfully created and initialized!")
except Exception as e:
    print("[-] Error:", e)
finally:
    conn.close()
