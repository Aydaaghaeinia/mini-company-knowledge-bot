import streamlit as st
import requests

st.set_page_config(page_title="Company Bot", layout="centered")
st.title("🤖 Mini Company Knowledge Bot")
st.markdown("این سیستم فایل‌های شما را می‌خواند و به سؤالات پاسخ می‌دهد.")

if "messages" not in st.session_state:
    st.session_state.messages = []

# نمایش تاریخچه چت
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("سؤال خود را بپرسید..."):
    # نمایش پیام کاربر
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # دریافت پاسخ از دستیار (بک‌اند)
    with st.chat_message("assistant"):
        with st.spinner("در حال جستجو در اسناد..."):
            try:
                res = requests.post("http://127.0.0.1:8000/ask", json={"question": prompt})
                
                if res.status_code == 200:
                    data = res.json()
                    answer = data.get("answer", "خطای نامشخص.")
                    sources = data.get("sources", [])
                    
                    # اگر منبعی پیدا شد، به انتهای جواب اضافه کن
                    if sources:
                        answer += f"\n\n**📄 منابع:** {', '.join(sources)}"
                else:
                    answer = f"❌ خطا از سمت بک‌اند: {res.text}"
                
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
            except requests.exceptions.ConnectionError:
                st.error("ارتباط با بک‌اند قطع است. لطفاً ابتدا فایل backend.py را اجرا کنید.")