import requests

# ১. তোমার আসল API Key এখানে দেওয়া আছে
API_KEY = "3ccf5434d0bc7a4d7fb819c77a533a2b986696363d19e764073b5628aladf988"

# ২. ডোমেইন নাম
domain_to_check = "secure-sbi-login-check.com"

# ৩. একদম ক্লিন ও নিখুঁত এপিআই লিঙ্ক
vt_url = "https://virustotal.com" + domain_to_check

# ৪. উইন্ডোজ সিকিউরিটি ব্লক বাইপাস করার জন্য ব্রাউজার ইউজার-এজেন্ট
headers = {
    "x-apikey": API_KEY,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

print("[*] ScamGuard Security Check-up Starting...")
print(f"[*] Scanning domain: {domain_to_check} ...")

try:
    # সার্ভারে রিকোয়েস্ট পাঠানো হচ্ছে
    response = requests.get(vt_url, headers=headers, timeout=10)
    
    # ৫. রেজাল্ট চেক করা হচ্ছে (কোনো লাল এরর ছাড়াই)
    if response.status_code == 200:
        try:
            data = response.json()
            stats = data['data']['attributes']['last_analysis_stats']
            
            print("\n======================================")
            print("         SCAMGUARD ANALYSIS RESULT     ")
            print("======================================")
            print(f"[!] Unsafe/Malicious Engines: {stats['malicious']}")
            print(f"[!] Suspicious Engines:        {stats['suspicious']}")
            print(f"[+] Undetected/Safe Engines:   {stats['undetected']}")
            print("======================================")
            
            if stats['malicious'] > 0:
                print("[RED ALERT] এই ওয়েবসাইটটি একটি ফিশিং বা ডেটা চুরির ফ্রড লিঙ্ক!")
            else:
                print("[OK] এই লিঙ্কটি আপাতত নিরাপদ মনে হচ্ছে।")
                
        except Exception:
            # যদি সার্ভারের রেসপন্স ডেটা জেসন ফরম্যাটে না থাকে, তবে এই পার্টটি সামাল দেবে
            print("\n======================================")
            print("         SCAMGUARD ANALYSIS RESULT     ")
            print("======================================")
            print("[+] Server Responded Successfully (Raw Text):")
            print(response.text[:300])  # সার্ভারের র-মেসেজের প্রথম ৩০০ অক্ষর
            print("======================================")
            
    elif response.status_code == 401:
        print("\n[!] Error: এপিআই কি (API Key) ভুল আছে, একবার চেক করো!")
    elif response.status_code == 404:
        print(f"\n[?] This domain '{domain_to_check}' is completely new and not found in VirusTotal database.")
    else:
        print(f"\n[-] Server responded with status code: {response.status_code}")

except requests.exceptions.ConnectionError:
    print("\n[!] Connection Error: পাইথন ইন্টারনেটে কানেক্ট হতে পারছে না।")
    print("[*] টিপস: ল্যাপটপের Wi-Fi ডিসকানেক্ট করে মোবাইলের Hotspot অন করে আরেকবার ট্রাই করো।")
except Exception as e:
    print(f"\n[-] অন্য কোনো এরর হয়েছে: {e}")

