import os
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from googletrans import Translator  # অথবা আপনি Bhashini AI API ব্যবহার করতে পারেন
from gtts import gTTS  # ভারতের আঞ্চলিক ভাষার টেক্সট-টু-স্পিচের জন্য

app = FastAPI(
    title="AI-Powered Hybrid SMS Scam Detector",
    description="Multilingual Support for 64 Indian Languages with Automated Voice-Over",
    version="2.0.0"
)

# ১. ইউজার যে ভাষা সিলেক্ট করবেন তার জন্য ল্যাঙ্গুয়েজ ম্যাপ (আইএসও কোড)
# উদাহরণ হিসেবে প্রধান কয়েকটি দেওয়া হলো, আপনি মোট ৬৪টি ভাষা এভাবে ম্যাপ করতে পারবেন
LANGUAGE_MAP = {
    "bengali": "bn",
    "hindi": "hi",
    "marathi": "mr",
    "tamil": "ta",
    "telugu": "te",
    "assamese": "as",
    "gujarati": "gu",
    "kannada": "kn",
    "malayalam": "ml",
    "punjabi": "pa",
    "odia": "or",
    "english": "en"
}

# ২. ইনপুট ডেটা স্ট্রাকচার (FastAPI Pydantic Model)
class SMSInput(BaseModel):
    sms_text: str
    selected_language: str  # যেমন: "bengali", "marathi"

# ৩. মক হাইব্রিড এআই ডিটেক্টর (এখানে আপনার বর্তমান এআই মডেলের লজিক বসবে)
def run_hybrid_ai_analysis(text: str):
    """
    আপনার আসল হাইব্রিড এআই মডেলের আউটপুট এখানে জেনারেট হবে।
    এটি মেসেজ টেক্সট, সেন্ডার আইডি এবং লিঙ্কের ব্যাকএন্ড মেটাডেটা চেক করবে।
    """
    text_lower = text.lower()
    
    # উদাহরণস্বরূপ একটি হাই-রিস্ক স্ক্যাম মেসেজের কন্ডিশন
    if "block" in text_lower or "lottery" in text_lower or "click here" in text_lower or "bkash" in text_lower:
        return {
            "risk_status": "High",
            "reason_1": "The sender is an unknown 11-digit personal mobile number, not an official channel.",
            "reason_2": "The text creates artificial urgency by threatening account suspension or offering fake rewards.",
            "advice": "Do not click any link, do not call this number, and never share your PIN or OTP."
        }
    
    # সেফ মেসেজের কন্ডিশন
    return {
        "risk_status": "Low",
        "reason_1": "The sender matches verified official organizational database systems.",
        "reason_2": "No suspicious redirection links or urgent text manipulation detected.",
        "advice": "This message appears safe to read and process."
    }

# ৪. মেইন এপিআই এন্ডপয়েন্ট (FastAPI Route)
@app.post("/api/v1/analyze-sms", status_code=status.HTTP_200_OK)
async def analyze_and_localize_sms(data: SMSInput):
    # ক) ইউজারের ভাষা চেক করা
    target_lang = data.selected_language.lower().strip()
    if target_lang not in LANGUAGE_MAP:
        raise HTTPException(
            status_code=400, 
            detail=f"Language '{target_lang}' is not supported yet. Choose from: {list(LANGUAGE_MAP.keys())}"
        )
    
    lang_code = LANGUAGE_MAP[target_lang]
    
    # খ) আপনার হাইব্রিড এআই মডেল রান করা (ইংরেজি আউটপুট)
    ai_result = run_hybrid_ai_analysis(data.sms_text)
    
    # গ) ট্রান্সলেশন লেয়ার (ইংরেজি থেকে ইউজারের মাতৃভাষায় রূপান্তর)
    translator = Translator()
    try:
        translated_reason_1 = translator.translate(ai_result["reason_1"], src="en", dest=lang_code).text
        translated_reason_2 = translator.translate(ai_result["reason_2"], src="en", dest=lang_code).text
        translated_advice = translator.translate(ai_result["advice"], src="en", dest=lang_code).text
        
        # রিস্ক স্ট্যাটাস অনুবাদ
        status_text = "ঝুঁকি অনেক বেশি" if ai_result["risk_status"] == "High" else "ঝুঁকি নেই, নিরাপদ"
        if lang_code != "bn":  # বাংলা বাদে অন্য ভাষার জন্য গ্লোবাল ট্রান্সলেশন
            status_text = translator.translate(ai_result["risk_status"] + " Risk", src="en", dest=lang_code).text
            
    except Exception as e:
        # ট্রান্সলেশন ফেইল করলে ব্যাকআপ হিসেবে ইংরেজি টেক্সট পাঠাবে
        translated_reason_1 = ai_result["reason_1"]
        translated_reason_2 = ai_result["reason_2"]
        translated_advice = ai_result["advice"]
        status_text = ai_result["risk_status"]

    # ঘ) টেক্সট-টু-স্পিচ (TTS) অডিও ফাইল জেনারেশন লেয়ার
    # পুরো স্ক্রিপ্টটি একটি অডিও লাইনে সাজানো হচ্ছে
    full_audio_text = f"{status_text}. {translated_reason_1} {translated_reason_2} {translated_advice}"
    
    audio_filename = f"static/audio_{target_lang}_output.mp3"
    os.makedirs("static", exist_ok=True)
    
    try:
        # ইউজারের সিলেক্ট করা ভাষায় অডিও ফাইল জেনারেট হবে
        tts = gTTS(text=full_audio_text, lang=lang_code, slow=False)
        tts.save(audio_filename)
        audio_url = f"/static/{os.path.basename(audio_filename)}"
    except Exception:
        audio_url = None  # অডিও জেনারেট না হতে পারলে নাল রিটার্ন করবে

    # ঙ) ফাইনাল লোকাল রেসপন্স (যা ফ্রন্টএন্ডে লাল/সবুজ কালার মিটার ও অটো-প্লে অডিও ট্রিগার করবে)
    return {
        "success": True,
        "selected_language": target_lang,
        "risk_level": ai_result["risk_status"],  # "High" বা "Low" (ফ্রন্টএন্ডে লাল/সবুজ করার জন্য)
        "localized_output": {
            "status_headline": status_text,
            "point_1": translated_reason_1,
            "point_2": translated_reason_2,
            "final_advice": translated_advice
        },
        "audio_playback_url": audio_url
    }
