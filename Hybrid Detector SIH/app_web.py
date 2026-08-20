import streamlit as st
import requests
import io
from PIL import Image

# ১. ওয়েবসাইটের পেজ টাইটেল ও থিম সেটিংস
st.set_page_config(page_title="ScamGuard AI - Hybrid Detector", page_icon="🛡️", layout="centered")

st.title("🛡️ SCAMGUARD AI HYBRID")
st.subheader("Smart India Hackathon (SIH) Live Demo")
st.write("Upload a screenshot or scan a QR code to detect phishing links and financial fraud indicators instantly.")

# ২. 🌟 স্ক্রোলিং ড্রপডাউন মেনু (ভাষা সিলেক্ট করার জন্য)
language_options = {
    "English": "english",
    "Bengali (বাংলা)": "bengali",
    "Hindi (हिंदी)": "hindi",
    "Marathi (मराठी)": "marathi",
    "Tamil (தமிழ்)": "tamil",
    "Telugu (తెలుగు)": "telugu",
    "Gujarati (ગુજરાતી)": "gujarati"
}
selected_lang_name = st.selectbox("🌐 Choose Response Language:", list(language_options.keys()))
selected_lang_value = language_options[selected_lang_name]

# ৩. ফাইল আপলোডার জোন
uploaded_file = st.file_uploader("📸 Upload Screenshot or QR Image...", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # স্ক্রিনে আপলোড করা ছবিটা দেখানো
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image Preview", use_container_width=True)
    
    # স্ক্যান বাটন
    if st.button("🚀 ANALYZE SCREENSHOT"):
        with st.spinner("AI Scanner is running... Please wait."):
            try:
                # আপলোড করা ফাইলটিকে বাইটসে রূপান্তর
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='PNG')
                img_byte_arr = img_byte_arr.getvalue()
                
                # আপনার FastAPI লোকাল ব্যাকএন্ড পোর্টে ডেটা পাঠানো
                files = {"file": ("screenshot.png", img_byte_arr, "image/png")}
                data = {"selected_language": selected_lang_value}
                
                # আপনার ব্যাকএন্ড এপিআই হিট করা
                response = requests.post("http://127.0.0.1:8000/predict", files=files, data=data)
                
                if response.status_code == 200:
                    result_data = response.json()
                    
                    st.success("Analysis Complete!")
                    st.write("---")
                    
                    # ৪. 🌟 রিস্ক অনুযায়ী চমৎকার কালার বক্স ডেমো
                    risk = result_data.get("risk_score", "LOW")
                    
                    # স্থানীয় ভাষার ডেটা নেওয়া (যদি থাকে)
                    headline = result_data.get("localized_output", {}).get("headline", result_data.get("result", ""))
                    message = result_data.get("localized_output", {}).get("translated_message", result_data.get("message", ""))
                    
                    if risk == "HIGH":
                        st.error(f"🚨 **Result:** {headline}")
                        st.warning(f"⚠️ **Alert:** {message}")
                    else:
                        st.success(f"✅ **Result:** {headline}")
                        st.info(f"ℹ️ **Message:** {message}")
                        
                    # ৫. 🌟 ভয়েস অ্যালার্ট অডিও প্লেয়ার (যদি ব্যাকএন্ড থেকে জেনারেট হয়)
                    audio_url = result_data.get("audio_url")
                    if audio_url:
                        # লোকাল স্ট্যাটিক পাথ থেকে অডিও লোড করা
                        full_audio_url = f"http://127.0.0.1:8000{audio_url}"
                        st.write("🔊 **Voice Alert Playback:**")
                        st.audio(full_audio_url, format="audio/mp3")
                        
                    # এপিআই এর ডিটেইলড রেসপন্স (জুরিদের টেকনিক্যাল ব্যাকগ্রাউন্ড দেখানোর জন্য)
                    with st.expander("🔍 View Technical JSON Response"):
                        st.json(result_data)
                        
                else:
                    st.error(f"Backend Server Error: Status Code {response.status_code}")
            except Exception as e:
                st.error(f"Cannot connect to FastAPI backend: {str(e)}")
