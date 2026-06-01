import streamlit as st
import requests

# تنظیمات ظاهر صفحه
st.set_page_config(page_title="Mini Company Bot", page_icon="🤖", layout="centered")

st.title("🤖 ربات دانش سازمانی (Mini Company)")
st.markdown("سوال خود را بپرسید تا ربات بر اساس فایل‌های PDF پاسخ دهد.")
st.divider()

# ساخت حافظه برای نگه داشتن تاریخچه چت‌ها روی صفحه
if "messages" not in st.session_state:
    st.session_state.messages = []

# نمایش پیام‌های قبلی در صفحه
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# کادر دریافت سوال از کاربر
if prompt := st.chat_input("سوال خود را از اسناد بپرسید..."):
    
    # ۱. نمایش سوال کاربر روی صفحه
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # ۲. ارتباط با بک‌اند (main.py) و نمایش جواب
    with st.chat_message("assistant"):
        with st.spinner("در حال جستجو در اسناد شرکت... 🔍"):
            try:
                # فرستادن سوال به سرور فست‌ای‌پی‌آی
                response = requests.post("http://127.0.0.1:8000/ask", json={"question": prompt})
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "")
                    sources = data.get("sources_used", [])
                    
                    # زیباتر کردن خروجی و اضافه کردن منابع
                    if sources:
                        sources_text = f"\n\n---\n**📁 منابع استفاده شده:** {', '.join(sources)}"
                    else:
                        sources_text = ""
                        
                    full_response = answer + sources_text
                    
                    st.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                else:
                    st.error("خطا: سرور بک‌اند پاسخ نمی‌دهد!")
            except Exception as e:
                st.error("ارتباط با سرور قطع است. مطمئن شوید فایل main.py در یک ترمینال دیگر در حال اجراست.")