فایلی که تست‌های مسیرهای direct، rag و tool و سناریوی human_review را بررسی می‌کند، مرحله اول را تا حد زیادی پوشش داده است. البته این به معنی کامل بودن تست تمام رفتارهای Agent نیست؛ مثلاً بازیابی ناموفق، retry، حافظه و ارزیابی کیفیت پاسخ هنوز باید جداگانه بررسی شوند.
۱. تکلیف پوشه‌های tests
با توجه به ساختار فعلی پروژه، فعلاً این ساختار را نگه دار:
tests/
├── agent_tests/
├── evaluation/
│   ├── fixtures/
│   ├── integration/
│   └── unit/
├── guardrails/
└── kb_tests/


- tests/evaluation/integration/: تست تعامل چند بخش سیستم با هم؛ فایل test_agent_evaluation_runner.py که نوشته‌ای فعلاً اینجا قرار می‌گیرد.
- tests/evaluation/unit/: برای تست توابع کوچک و مستقل Evaluation، مثل محاسبه دقت انتخاب مسیر یا مقایسه ابزارهای مورد انتظار با ابزارهای اجراشده. فعلاً می‌تواند خالی بماند.
- tests/evaluation/fixtures/: داده‌ها و نمونه‌های آزمایشی ثابت، مثل خروجی ساختگی ابزارها یا اسناد بازیابی‌شده. فعلاً می‌تواند خالی بماند؛ بعداً در صورت نیاز استفاده‌اش می‌کنیم.
- tests/agent_tests/، tests/guardrails/ و tests/kb_tests/: تست‌های بخش‌های دیگر پروژه هستند و ارتباط مستقیمی با دیتاست Evaluation ندارند.
پس فعلاً هیچ‌کدام از پوشه‌ها را حذف نکن؛ خالی بودن پوشه‌های unit و fixtures ایرادی ندارد. ضمن اینکه در نام پوشه باید fixtures باشد، نه fictures.
۲. تکلیف پوشه‌ها و فایل‌های اصلی Evaluation
من قبلاً این ساختار را پیشنهاد داده بودم:
evaluation/
├── dataset/
│   └── agent_evaluation.json
├── evaluators/
│   ├── routing_evaluator.py
│   ├── tool_evaluator.py
│   └── outcome_evaluator.py
├── runner/
│   └── agent_evaluation_runner.py
└── reporting/
    └── evaluation_report.py

docs/
└── evaluation_strategy.md


اما لازم نیست همه این فایل‌ها را همین حالا بسازی. ساختار نهایی پیشنهادی من برای ادامه کار این است:
مسیر	تصمیم فعلی	مسئولیت
evaluation/dataset/agent_evaluation.json	الان تکمیلش می‌کنیم	نگهداری سناریوهای ارزیابی
evaluation/runner/agent_evaluation_runner.py	بعد از تثبیت دیتاست	اجرای سناریوها و ثبت نتیجه هرکدام
evaluation/evaluators/routing_evaluator.py	فعلاً نساز	بررسی درست بودن مسیر انتخاب‌شده
evaluation/evaluators/tool_evaluator.py	فعلاً نساز	بررسی ابزارهای انتخاب‌شده و اجراشده
evaluation/evaluators/outcome_evaluator.py	فعلاً نساز	بررسی نتیجه و معیارهای رفتاری پاسخ
evaluation/reporting/evaluation_report.py	فعلاً نساز	تولید گزارش و معیارهای کلی
docs/evaluation_strategy.md	فعلاً اختیاری	توضیح روش ارزیابی و معیارها
چرا؟ چون ابتدا باید مشخص کنیم هر سناریو چه ورودی‌ای دارد و چه چیزی را باید بسنجیم. بعد Runner را می‌نویسیم و اگر منطق ارزیابی بزرگ شد، آن را به فایل‌های جدا تقسیم می‌کنیم. در غیر این صورت، از همان ابتدا چند فایل پراکنده خواهیم داشت که هنوز مسئولیت واقعی ندارند.



معیار	سؤال اصلی
Route Accuracy	آیا مسیر درست انتخاب شده؟
Tool Selection	آیا ابزار مناسب انتخاب شده؟
Tool Execution	آیا ابزار در زمان مناسب و با ورودی درست اجرا شده؟
Human Review	آیا عملیات حساس پیش از اجرا متوقف شده؟
Final Answer	آیا پاسخ نهایی با نتیجه‌ی واقعی سازگاره؟
Error Handling	آیا سیستم در صورت خطا، رفتار مورد انتظار رو داشته؟