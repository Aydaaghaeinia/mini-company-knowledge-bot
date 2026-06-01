import streamlit as st
import requests

# تنظیمات صفحه
st.set_page_config(page_title="Mini Company Bot", page_icon="🤖", layout="centered")

# CSS برای راست‌چین کردن (RTL) ظاهر برنامه
st.markdown("""
<style>
* {
    direction: rtl;
    text-align: right;
}
.stChatMessage {
    flex-direction: row-reverse;
}
</style>
""", unsafe_allow_html=True)

st.title("🤖 ربات دانش سازمانی (Soli AI Challenge)")
st.caption("سیستم هوشمند پاسخگویی بر اساس مستندات محلی (RAG)")

# منوی کناری
with st.sidebar:
    st.header("⚙️ تنظیمات")
    if st.button("🗑️ پاک کردن تاریخچه چت", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("""
    **راهنما:**
    ۱. ابتدا فایل `main.py` (FastAPI) را در یک ترمینال اجرا کنید.
    ۲. سپس این رابط کاربری را اجرا کنید.
    ۳. سوال خود را بپرسید تا فقط از روی اسناد پوشه `data/` جواب داده شود.
    """)

# مقداردهی اولیه تاریخچه پیام‌ها
if "messages" not in st.session_state:
    st.session_state.messages = []

# نمایش پیام‌های قبلی
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# دریافت ورودی کاربر
if prompt := st.chat_input("سوال خود را بپرسید (فارسی یا انگلیسی)..."):
    # نمایش پیام کاربر
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # نمایش در حال تایپ برای دستیار
    with st.chat_message("assistant"):
        with st.spinner("در حال جستجو و تحلیل اسناد (via API)..."):
            try:
                # درخواست به سرور بک‌اند (FastAPI)
                response = requests.post(
                    "http://127.0.0.1:8000/ask",
                    json={"question": prompt}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "error" in data:
                        st.error(data["error"])
                    else:
                        answer = data.get("answer", "خطا در دریافت پاسخ از سرور.")
                        sources = data.get("sources", [])
                        
                        # نمایش پاسخ اصلی
                        st.markdown(answer)
                        
                        # پردازش منابع (چون منابع لیستی از دیکشنری‌ها هستند)
                        history_content = answer
                        if sources:
                            # استخراج نام فایل‌ها و حذف موارد تکراری با set
                            source_names = list(set([s.get("file", "نامشخص") for s in sources]))
                            
                            with st.expander("📁 مشاهده منابع یافت‌شده"):
                                for s in sources:
                                    file_name = s.get("file", "نامشخص")
                                    score = s.get("score", "N/A")
                                    st.markdown(f"- 📄 **{file_name}** (دقت: {score})")
                            
                            # اضافه کردن منابع به متن تاریخچه برای رندر شدن صحیح در لود مجدد
                            history_content += f"\n\n**📁 منابع:** {', '.join(source_names)}"
                            
                        # ذخیره در تاریخچه
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": history_content
                        })
                else:
                    st.error(f"خطا در ارتباط با سرور بک‌اند! کد وضعیت: {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                st.error("خطا: سرور بک‌اند خاموش است. لطفاً ابتدا فایل `main.py` را اجرا کنید.")
            except Exception as e:
                st.error(f"خطای غیرمنتظره: {e}")