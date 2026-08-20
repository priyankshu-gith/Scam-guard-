import cv2
import numpy as np
import easyocr
import os
from enum import Enum
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from deep_translator import GoogleTranslator
from gtts import gTTS

class LanguageOptions(str, Enum):
    bengali = "bengali"
    hindi = "hindi"
    marathi = "marathi"
    tamil = "tamil"
    telugu = "telugu"
    assamese = "assamese"
    gujarati = "gujarati"
    kannada = "kannada"
    malayalam = "malayalam"
    punjabi = "punjabi"
    odia = "odia"
    english = "english"

# Initialize FastAPI App and EasyOCR Reader
app = FastAPI(title="ScamGuard Ultimate Hybrid API", version="2.5")
reader = easyocr.Reader(['en'], gpu=False)

# --- ২. অডিও ফোল্ডার তৈরি ও ৬৪ ভাষার কোড ম্যাপ ---
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS Middleware যুক্ত করা হলো যাতে মোবাইল অ্যাপ থেকে কোনো বাধা ছাড়াই রিকোয়েস্ট আসে
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LANGUAGE_MAP = {
    "bengali": "bn", "hindi": "hi", "marathi": "mr", "tamil": "ta",
    "telugu": "te", "assamese": "as", "gujarati": "gu", "kannada": "kn",
    "malayalam": "ml", "punjabi": "pa", "odia": "or", "english": "en"
}

@app.get("/")
def home():
    return {"message": "ScamGuard Ultimate Hybrid API is live and running successfully!"}

@app.post("/predict")
async def scan_screenshot(
    file: UploadFile = File(...),
    selected_language: str = Form("english")  # এটিকে সাধারণ স্ট্রিং ও অপশনাল করা হলো যাতে মোবাইল থেকে ল্যাঙ্গুয়েজ না পাঠালেও ক্র্যাশ না করে
):
    try:
        # ১. Read the uploaded image bytes safely
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return {"status": "error", "message": "Invalid image file format uploaded"}
            
        # ২. Try QR Code Detection First
        detector = cv2.QRCodeDetector()
        secret_link, bbox, straight_qrcode = detector.detectAndDecode(img)
        
        suspicious_keywords = ['free', 'gift', 'card', 'sbi', 'secure', 'login']
        
        # # NEW PERFECT HACK: Trusted Official Brands (To avoid False Positives)
        trusted_keywords = ['scapia', 'federalbank', 'bobcard', 'hdfcbank', 'icicibank', 'axisbank']
        
        if secret_link:
            is_phishing = any(kw in secret_link.lower() for kw in suspicious_keywords)
            # Check if it belongs to a trusted official brand
            is_trusted = any(brand in secret_link.lower() for brand in trusted_keywords)
            
            if is_phishing and not is_trusted:
                return {
                    "status": "success",
                    "mode_detected": "QR_CODE",
                    "extracted_text_or_link": secret_link,
                    "result": "RED ALERT",
                    "risk_score": "HIGH",
                    "message": "Dangerous Phishing link found inside QR!"
                }
            else:
                return {
                    "status": "success",
                    "mode_detected": "QR_CODE",
                    "extracted_text_or_link": secret_link,
                    "result": "CLEAN",
                    "risk_score": "LOW",
                    "message": "QR link looks normal or belongs to a trusted brand."
                }
                
        # ৩. If NO QR Code is found, trigger EasyOCR to read text from normal screenshot
        print("[*] No QR Code found. Triggering EasyOCR Scanner...")
        ocr_results = reader.readtext(img, detail=0)
        extracted_text = " ".join(ocr_results).lower()
        
        if not extracted_text.strip():
            return {
                "status": "success",
                "mode_detected": "NO_TEXT_FOUND",
                "message": "The uploaded image is blank or contains no readable text."
            }
            
        # Analyze extracted text for phishing indicators
        is_scam_text = any(kw in extracted_text for kw in suspicious_keywords)
        # Check if the extracted text mentions any of our trusted official brands
        is_trusted_text = any(brand in extracted_text for brand in trusted_keywords)
        
        risk_level = "LOW"
        result_flag = "CLEAN"
        alert_message = "No clear phishing patterns or malicious links detected in the screenshot text."
        
        # THE MASTER UPDATE: Flag as RED ALERT ONLY IF it has bad keywords AND is NOT trusted
        if (is_scam_text or "@" in extracted_text) and not is_trusted_text:
            risk_level = "HIGH"
            result_flag = "RED ALERT"
            alert_message = "Suspicious financial scam keywords or malicious links detected in the screenshot text!"
        elif is_trusted_text:
            alert_message = "Contains keywords but verified as a promotion from an official trusted partner."
            
        # --- Store your original backend response format in a variable ---
        # --- original backend response dictionary ---
        response_data = {
            "status": "success",
            "mode_detected": "SCREENSHOT_OCR",
            "extracted_text_or_link": extracted_text,
            "result": result_flag,
            "risk_score": risk_level,
            "message": alert_message
        }
        
        # ৪. ড্রপডাউন থেকে সিলেক্ট করা ভাষা রিড করা
        target_lang = selected_language.lower().strip() # .value এরর ফিক্স করা হয়েছে
        lang_code = LANGUAGE_MAP.get(target_lang, "en")
        
        english_msg = response_data["message"]
        translated_msg = english_msg
        
        # ৫. ইংরেজি অ্যালার্ট মেসেজটাকে সম্পূর্ণভবে সিলেক্ট করা ভাষায় অনুবাদ
        if lang_code != "en":
            try:
                translated_msg = GoogleTranslator(source='en', target=lang_code).translate(english_msg)
            except Exception:
                pass
                
        # ৬. হেডলাইন বা স্ট্যাটাস ফিক্স করা (সম্পূর্ণ খাঁটি মাতৃভাষায়)
        if response_data["risk_score"] == "HIGH":
            status_prefix = "ঝুঁকি অনেক বেশি।" if lang_code == "bn" else "High Risk."
        else:
            status_prefix = "কোনো ঝুঁকি নেই।" if lang_code == "bn" else "Low Risk."
            
        if lang_code != "bn" and lang_code != "en":
            try:
                status_prefix = GoogleTranslator(source='en', target=lang_code).translate(f"{response_data['risk_score']} Risk.")
            except Exception:
                pass
                
        # ৭. অডিও স্ক্রিপ্ট তৈরি (ইংরেজি শব্দ ছাড়া সম্পূর্ণ লোকাল ভয়েস)
        full_audio_script = f"{status_prefix} {translated_msg}"
        audio_filename = f"static/voice_{target_lang}.mp3"
        audio_url = None
        
        try:
            tts = gTTS(text=full_audio_script, lang=lang_code, slow=False)
            tts.save(audio_filename)
            audio_url = f"/static/voice_{target_lang}.mp3"
        except Exception:
            pass
            
        # ৮. রেসপন্স ডিকশনারিতে ডেটা পুশ করা
        response_data["localized_output"] = {
            "headline": status_prefix.replace(".", "").strip(),
            "translated_message": translated_msg
        }
        response_data["audio_url"] = audio_url
        
        return response_data

    except Exception as e: # এই মেইন এক্সেপ্ট ব্লকের ইন্ডেন্টেশন বা স্পেসিং নিখুঁত করা হলো
        return {"status": "error", "message": f"Server internal error: {str(e)}"}



    
