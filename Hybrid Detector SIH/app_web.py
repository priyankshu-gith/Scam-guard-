import streamlit as st
import requests
import io
import time
from PIL import Image

# ১. প্রফেশনাল পেজ সেটআপ ও থিম
st.set_page_config(page_title="ScamGuard AI - Hybrid Shield", page_icon="🛡️", layout="wide")

# ২. 🌟 কাস্টম CSS, অ্যানিমেশন এবং গ্লোয়িং বর্ডার এফেক্ট (UI/UX কাস্টমাইজেশন)
st.markdown("""
    <style>
    /* মেইন ব্যাকগ্রাউন্ড ও টেক্সট স্মুথ অ্যানিমেশন */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .stApp {
        background-color: #0f0f1a;
        animation: fadeIn 0.8s ease-out;
    }
    /* টাইটেল স্টাইলিং ও গ্লো এফেক্ট */
    .main-title {
        font-size: 42px !important;
        font-weight: 800 !important;
        color: #f38ba8 !important;
        text-align: center;
        text-shadow: 0 0 15px rgba(243, 139, 168, 0.4);
        margin-bottom: 5px;
    }
    .sub-title {
        font-size: 16px;
        color: #a6adc8;
        text-align: center;
        margin-bottom: 30px;
    }
    /* প্রফেশনাল গ্লোয়িং কার্ডের ডিজাইন */
    .custom-card-red {
        background: rgba(243, 139, 168, 0.1);
        border: 2px solid #f38ba8;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 0 20px rgba(243, 139, 168, 0.2);
        animation: fadeIn 0.5s ease-in-out;
    }
    .custom-card-green {
        background: rgba(166, 227, 161, 0.1);
        border: 2px solid #a6e3a1;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 0 20px rgba(166, 227, 161, 0.2);
        animation: fadeIn 0.5s ease-in-out;
    }
    /* চ্যাট হিস্টোরি স্টাইলিং */
    .user-msg {
        background-color: #89b4fa;
        color: #11111b;
        padding: 10px 15px;
        border-radius: 15px 15px 0px 15px;
        margin: 5px 0;
        max-width: 75%;
        float: right;
        clear: both;
    }
    .bot-msg {
        background-color: #313244;
        color: #cdd6f4;
        padding: 10px 15px;
        border-radius: 15px 15px 15px 0px;
        margin: 5px 0;
        max-width: 75%;
        float: left;
        clear: both;
    }
    </style>
""", unsafe_allow_allowed_html=True)

# হেডার সেকশন রেন্ডার
st.markdown('<p class="main-title">🛡️ SCAMGUARD AI ULTRA HYBRID</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Next-Gen Phishing & Financial Fraud Detection Shield (SIH Exclusive Build)</p>', unsafe_allow_html=True)

# লেআউটকে দুটি সুন্দর কলামে ভাগ করা (বামপাশে স্ক্যানার, ডানপাশে লাইভ বট)
col1, col2 = st.columns([1.1, 0.9], gap="large")

with col1:
    st.markdown("### 📸 Image & QR AI Scanner")
    
    # ড্রপডাউন মেনু
    language_options = {
        "English": "english", "Bengali (বাংলা)": "bengali", "Hindi (हिंदी)": "hindi",
        "Marathi (मराठी)": "marathi", "Tamil (தமிழ்)": "tamil", "Telugu (తెలుగు)": "telugu"
    }
    selected_lang_name = st.selectbox("🌐 Select Threat Response Language:", list(language_options.keys()))
    selected_lang_value = language_options[selected_lang_name]

    uploaded_file = st.file_uploader("Upload suspicious screenshot or QR asset:", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded File Preview", use_container_width=True)
        
        if st.button("🚀 RUN HYBRID DETECTOR", use_container_width=True):
            # লোডিং অ্যানিমেশন (সহজ ও মডার্ন লোডার)
            with st.spinner("🧠 Scanning layers with Computer Vision & NLP..."):
                try:
                    img_byte_arr = io.BytesIO()
                    image.save(img_byte_arr, format='PNG')
                    img_byte_arr = img_byte_arr.getvalue()
                    
                    files = {"file": ("screenshot.png", img_byte_arr, "image/png")}
                    data = {"selected_language": selected_lang_value}
                    
                    # ⚠️ আপনার আসল Localtunnel বা Ngrok ব্যাকএন্ড URL টি এখানে বসাবেন
                    BACKEND_URL = "http://127.0.0.1:8000" 
                    
                    response = requests.post(f"{BACKEND_URL}/predict", files=files, data=data)
                    
                    if response.status_code == 200:
                        result_data = response.json()
                        risk = result_data.get("risk_score", "LOW")
                        headline = result_data.get("localized_output", {}).get("headline", result_data.get("result", ""))
                        message = result_data.get("localized_output", {}).get("translated_message", result_data.get("message", ""))
                        
                        st.write("### 🔍 Security Analysis Output")
                        
                        # অ্যানিমেটেড কার্ড ও গ্লোয়িং বর্ডার এফেক্ট রেন্ডার
                        if risk == "HIGH":
                            st.markdown(f"""
                                <div class="custom-card-red">
                                    <h2 style='color:#f38ba8; margin:0;'>🚨 {headline}</h2>
                                    <p style='color:#cdd6f4; font-size:15px; margin-top:10px;'>{message}</p>
                                </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                                <div class="custom-card-green">
                                    <h2 style='color:#a6e3a1; margin:0;'>✅ {headline}</h2>
                                    <p style='color:#cdd6f4; font-size:15px; margin-top:10px;'>{message}</p>
                                </div>
                            """, unsafe_allow_html=True)
                        
                        # 🌟 ৩. কোনো ক্লিক ছাড়াই অটোমেটিক ভয়েস অ্যালার্ট প্লে হওয়ার ম্যাজিক হ্যাক (HTML5 Audio Autoplay)
                        audio_url = result_data.get("audio_url")
                        if audio_url:
                            full_audio_url = f"{BACKEND_URL}{audio_url}"
                            # এই কাস্টম এইচটিএমএল স্ক্রিপ্টটি ব্যাকগ্রাউন্ডে লুকিয়ে থেকে অডিও নিজে থেকেই প্লে করে দেবে
                            st.markdown(f"""
                                <audio autoplay style="display:none;">
                                    <source src="{full_audio_url}" type="audio/mp3">
                                </audio>
                            """, unsafe_allow_html=True)
                            st.caption("🔊 Voice alert triggered automatically in selected language.")

                    else:
                        st.error(f"Backend Returned Error Code: {response.status_code}")
                except Exception as e:
                    st.error(f"Failed to fetch AI server layers: {str(e)}")

# ৪. 🌟 লাইভ থ্রেট ডিটেকশন চ্যাটবট উইন্ডো (ডান কলামে)
with col2:
    st.markdown("### 💬 Live Threat Chatbot")
    st.write("Paste suspicious text or query links directly to interact with ScamGuard AI.")
    
    # চ্যাট হিস্টোরি স্টেট তৈরি
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"sender": "bot", "text": "হ্যালো! আমি স্ক্যামগার্ড বট। কোনো মেসেজ বা ইউআরএল সন্দেহজনক মনে হলে এখানে সাবমিট করুন।"}
        ]
        
    # চ্যাটবক্স কন্টেইনার স্ক্রোলিং মেকানিজম
    chat_container = st.container(height=350)
    with chat_container:
        for chat in st.session_state.chat_history:
            if chat["sender"] == "user":
                st.markdown(f'<div class="user-msg">{chat["text"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="bot-msg">{chat["text"]}</div>', unsafe_allow_html=True)

    # চ্যাট ইনপুট ও বাটন লজিক
    user_input = st.text_input("Analyze links, numbers or context:", key="chat_input_field", placeholder="Type here...")
    
    if st.button("💬 Send to Bot", use_container_width=True):
        if user_input.strip():
            # ইউজারের মেসেজ অ্যাড করা
            st.session_state.chat_history.append({"sender": "user", "text": user_input})
            
            try:
                # ব্যাকএন্ডের চ্যাট এপিআই-তে ডেটা পাঠানো
                BACKEND_URL = "http://127.0.0.1:8000"
                chat_response = requests.post(f"{BACKEND_URL}/chat", json={"message": user_input})
                
                if chat_response.status_code == 200:
                    bot_data = chat_response.json()
                    bot_reply = bot_data.get("reply", bot_data.get("message", "দুঃখিত, আমি বুঝতে পারিনি।"))
                    st.session_state.chat_history.append({"sender": "bot", "text": bot_reply})
                else:
                    st.session_state.chat_history.append({"sender": "bot", "text": "Error communicating with intelligence layers."})
            except Exception:
                st.session_state.chat_history.append({"sender": "bot", "text": "Chatbot server offline or host failed."})
                
            # স্ক্রিন রিফ্রেশ করে নতুন চ্যাট মেসেজ দেখানো
            st.rerun()
