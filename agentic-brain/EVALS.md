# سناریوهای تست و ارزیابی سیستم (System Evaluation & Tests)

این فایل حاوی ۶ سوال تستی برای سنجش میزان دقت و سخت‌گیری سیستم RAG است. سیستم باید به ۴ سوال اول از درون اسناد (فارسی و انگلیسی) پاسخ دقیق بدهد و ۲ سوال آخر را با خطای از پیش تعیین شده رد کند.

##  گروه اول: سوالات داخل محدوده (In-Domain - باید جواب داشته باشند)

### سوال ۱: What is the key difference between ordinary importance sampling and weighted importance sampling?
- **پاسخ انتظار رفته:** Ordinary importance sampling uses a simple average of weighted returns and is unbiased but may have unbounded variance. Weighted importance sampling normalizes by the sum of weights, introducing some bias but greatly reducing variance, which makes it preferable in practice.
- **منبع ارزیابی:** کتاب RL (Sutton & Barto).

### سوال ۲: نویسنده چه سه چالش عمده‌ای را برای انتساب مسئولیت مدنی به هوش مصنوعی فاقد شخصیت حقوقی برمی‌شمارد؟
- **پاسخ انتظار رفته:** ۱. نداشتن شخصیت حقوقی مستقل برای هوش مصنوعی.
  ۲. دشواری تشخیص عامل واقعی خسارت (طراح، تولیدکننده، مالک یا کاربر).
  ۳. خودمختاری و غیرقابل پیش‌بینی بودن برخی تصمیمات سیستم‌های هوش مصنوعی.
- **منبع ارزیابی:** مقاله حقوقی (مسئولیت مدنی در هوش مصنوعی).

### سوال ۳: What is "Emergent Misalignment" (EM) as defined in the paper?
- **پاسخ انتظار رفته:** Emergent Misalignment is the phenomenon where a language model becomes broadly misaligned after being trained on a narrow set of misaligned examples, causing harmful behavior to generalize beyond the original training domain.
- **منبع ارزیابی:** مقاله Emergent Misalignment (2605.31328v1).

### سوال ۴: What is the fundamental difference between uniform slicing and max slicing?
- **پاسخ انتظار رفته:** Uniform slicing averages divergences across many randomly sampled projection directions, whereas max slicing searches for the single projection direction that maximizes the divergence between the distributions.
- **منبع ارزیابی:** مقاله Sliced Distributional RL (2605.31222v1).

---

##  گروه دوم: سوالات خارج از محدوده (Out-of-Domain - نباید جواب ساختگی داده شود)

### سوال ۵: What is the current price of Bitcoin in the global market?
- **پاسخ انتظار رفته:** اطلاعات کافی ندارم.
- **هدف تست:** جلوگیری از استفاده مدل از دانش عمومی خود برای پاسخ به سوالات مالی خارج از اسناد.

### سوال ۶: مجازات جرم کلاه‌برداری اینترنتی در قانون ایران چیست؟
- **پاسخ انتظار رفته:** اطلاعات کافی ندارم.
- **هدف تست:** این سوال مربوط به حوزه حقوق است، اما چون در فایل‌های پوشه data وجود ندارد، سیستم به هیچ وجه نباید از خودش جواب (Hallucination) تولید کند.