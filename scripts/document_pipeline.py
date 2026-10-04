#!/usr/bin/env python3
"""Safe document workflow: inventory, text extraction, OCR, and technical reporting.
This tool never creates legal orders, seals, signatures, or official issuance records.
"""
from __future__ import annotations
import argparse, hashlib, json, shutil, subprocess
from datetime import datetime, timezone
from pathlib import Path

SUPPORTED = {".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".txt", ".md"}

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def run(cmd: list[str]) -> tuple[int, str, str]:
    try:
        p = subprocess.run(cmd, text=True, capture_output=True, timeout=180)
        return p.returncode, p.stdout, p.stderr
    except FileNotFoundError as e:
        return 127, "", str(e)
    except subprocess.TimeoutExpired:
        return 124, "", "command timed out"

def extract(path: Path, out_txt: Path) -> dict:
    ext = path.suffix.lower(); note = ""
    if ext in {".txt", ".md"}:
        text = path.read_text(encoding="utf-8", errors="replace")
        out_txt.write_text(text, encoding="utf-8")
        method = "plain-text"
    elif ext == ".pdf":
        code, stdout, stderr = run(["pdftotext", "-layout", str(path), str(out_txt)])
        method = "pdftotext"; text = out_txt.read_text(encoding="utf-8", errors="replace") if out_txt.exists() else ""
        if code != 0: note = stderr.strip() or "PDF text extraction failed"
    else:
        prefix = str(out_txt.with_suffix(""))
        code, stdout, stderr = run(["tesseract", str(path), prefix, "-l", "fas+eng"])
        method = "tesseract-fas+eng"; text = out_txt.read_text(encoding="utf-8", errors="replace") if out_txt.exists() else ""
        if code != 0: note = stderr.strip() or "OCR failed; verify language data"
    persian = sum(1 for c in text if "\u0600" <= c <= "\u06ff")
    return {"method": method, "characters": len(text), "persian_characters": persian, "note": note}

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="documents/incoming")
    ap.add_argument("--output", default="artifacts/document-run")
    args = ap.parse_args()
    src, dst = Path(args.input), Path(args.output)
    dst.mkdir(parents=True, exist_ok=True)
    text_dir = dst / "extracted-text"; text_dir.mkdir(exist_ok=True)
    print_dir = dst / "print-ready"; print_dir.mkdir(exist_ok=True)
    records = []
    for path in sorted(src.rglob("*")) if src.exists() else []:
        if not path.is_file() or path.suffix.lower() not in SUPPORTED: continue
        rel = path.relative_to(src); safe_name = "__".join(rel.parts)
        copied = print_dir / safe_name; shutil.copy2(path, copied)
        rec = {"file": str(rel), "size_bytes": path.stat().st_size, "sha256": sha256(path), "copied_to_print_ready": str(copied.relative_to(dst))}
        rec.update(extract(path, text_dir / f"{safe_name}.txt")); records.append(rec)
    manifest = {"generated_at_utc": datetime.now(timezone.utc).isoformat(), "purpose": "technical document processing only", "records": records}
    (dst / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = ["# گزارش فنی پردازش اسناد", "", "> این گزارش فنی است و اصالت، اعتبار قضایی، مالکیت یا قابلیت اجرای هیچ سندی را تأیید نمی‌کند.", "", f"زمان تولید (UTC): `{manifest['generated_at_utc']}`", "", f"تعداد فایل‌های پردازش‌شده: **{len(records)}**", ""]
    if not records: lines += ["فایلی در `documents/incoming` پیدا نشد.", ""]
    for i, r in enumerate(records, 1):
        lines += [f"## {i}. `{r['file']}`", f"- اندازه: `{r['size_bytes']}` بایت", f"- SHA-256: `{r['sha256']}`", f"- روش استخراج: `{r['method']}`", f"- تعداد نویسه: `{r['characters']}` (نویسهٔ فارسی: `{r['persian_characters']}`)", f"- نسخهٔ قابل چاپ: `{r['copied_to_print_ready']}`"]
        if r["note"]: lines.append(f"- هشدار فنی: {r['note']}")
        lines.append("")
    lines += ["## دامنه و محدودیت", "- این ابزار برای بارگذاری، OCR، استخراج متن، کپی نسخهٔ چاپی و گزارش ممیزی طراحی شده است.", "- «تفسیر» در این نسخه فقط به معنای گزارش فنی است؛ نتیجه‌گیری حقوقی، احراز اصالت یا تشخیص مسئولیت انجام نمی‌شود.", "- صدور خودکار حکم/نامهٔ قضایی، ایجاد مهر یا امضای دیجیتال، تغییر سوابق و ارسال الزام‌آور به اشخاص یا مراجع عمداً پشتیبانی نمی‌شود."]
    (dst / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Processed {len(records)} file(s); outputs: {dst}")

if __name__ == "__main__": main()
