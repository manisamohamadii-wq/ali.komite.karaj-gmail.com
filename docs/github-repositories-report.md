# گزارش مخزن‌های متن‌باز برای اسناد، مکاتبات و چاپ

> این گزارش فنی است. هیچ‌یک از ابزارها اصالت سند قضایی، اعتبار حقوقی، مهر یا امضا را تضمین نمی‌کنند. جعل مهر/امضای تصویری و صدور خودکار سند رسمی خارج از دامنهٔ پروژه است.

## پشتهٔ پیشنهادی

| حوزه | انتخاب اصلی | جایگزین/مکمل | کاربرد |
|---|---|---|---|
| OCR فارسی و فرم پیچیده | [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) | [EasyOCR](https://github.com/JaidedAI/EasyOCR)، [Tesseract](https://github.com/tesseract-ocr/tesseract) | استخراج متن، جدول و چیدمان |
| اسکن و PDF قابل جست‌وجو | [OCRmyPDF](https://github.com/ocrmypdf/OCRmyPDF) + Tesseract `fas` | [unpaper](https://github.com/unpaper/unpaper) | deskew، پاک‌سازی و OCR محلی |
| آرشیو و جست‌وجو | [Paperless-ngx](https://github.com/paperless-ngx/paperless-ngx) | [Docspell](https://github.com/eikek/docspell)، [Teedy](https://github.com/sismics/docs) | نگهداری، برچسب‌گذاری و جست‌وجوی اسناد |
| امضای دیجیتال معتبر | [DSS](https://github.com/esig/dss) | [pyHanko](https://github.com/MatthiasValvekens/pyHanko)، [pdfsign](https://github.com/digitorus/pdfsign) | PAdES/CAdES/XAdES، اعتبارسنجی زنجیره و revocation |
| گردش تأیید | [LibreSign](https://github.com/LibreSign/libresign) | [Documenso](https://github.com/documenso/documenso)، [DocuSeal](https://github.com/docusealco/docuseal) | نقش‌ها، تأیید انسانی و audit trail |
| کنترل خروجی چاپی | [veraPDF](https://github.com/veraPDF/veraPDF-library) | [pdfcpu](https://github.com/pdfcpu/pdfcpu) | کنترل PDF/A/PDF/UA و صحت عمومی PDF |

## نصب محلی پیشنهادی

```bash
sudo apt-get update
sudo apt-get install -y poppler-utils tesseract-ocr tesseract-ocr-fas ocrmypdf
```

برای PDF پیچیده، پس از آزمون نسخهٔ سبک، PaddleOCR را در محیط مجازی جداگانه نصب کنید و مدل فارسی/راست‌به‌چپ را با نمونه‌های واقعی ارزیابی کنید:

```bash
python3 -m venv .venv-ocr
. .venv-ocr/bin/activate
python -m pip install --upgrade pip
python -m pip install paddleocr
```

## ترتیب امن پردازش

۱. قرنطینه و بدافزارسنجی فایل ورودی؛ ۲. ثبت SHA-256 نسخهٔ اصلی؛ ۳. پاک‌سازی و OCR؛ ۴. بازبینی انسانی متن و فیلدهای حساس؛ ۵. آرشیو رمزنگاری‌شده؛ ۶. تأیید نقش‌محور؛ ۷. در صورت وجود اختیار قانونی، امضای PDF با کلید محافظت‌شده، گواهی معتبر، timestamp و بررسی OCSP/CRL؛ ۸. کنترل PDF/A و ثبت گزارش ممیزی.

**نکتهٔ مهم:** پس از امضای دیجیتال، روی PDF عملیات OCR، بهینه‌سازی، stamp یا تغییر محتوا انجام نشود؛ هر تغییر می‌تواند امضا را نامعتبر کند. تصویر مهر یا امضا، امضای دیجیتال معتبر نیست.

## معماری GitHub Actions

- اجرای pipeline روی `pull_request` و شاخهٔ محافظت‌شده؛
- `permissions: contents: read` و حداقل مجوز برای هر job؛
- pin کردن Actionها با SHA کامل؛
- اجرای OCR در runner/کانتینر غیرممتاز و بدون دسترسی تولید؛
- تولید manifest، هش، SBOM و گزارش فنی؛
- نگهداری Artifact محدود و رمزنگاری‌شده؛
- امضای نهایی فقط در سرویس جداگانهٔ PKI/HSM پس از تأیید انسانی، نه در CI عادی؛
- عدم استفاده از فایل‌ها و اطلاعات قضایی حساس در مخزن عمومی.

## وضعیت اجرای این پروژه

گردش‌کار موجود در `.github/workflows/document-pipeline.yml` از Tesseract فارسی، Poppler و گزارش‌گیری استفاده می‌کند. خروجی «قابل چاپ» به معنی تولید فایل برای چاپ است و چاپ فیزیکی خودکار انجام نمی‌شود.
