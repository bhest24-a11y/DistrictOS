import re
from PIL import Image, ImageDraw, ImageFilter
import pytesseract

SENSITIVE_PATTERNS = [
    r"password\\s*[:=]?\\s*\\S+",
    r"passcode\\s*[:=]?\\s*\\S+",
    r"ssn\\s*[:=]?\\s*\\d{3}-?\\d{2}-?\\d{4}",
    r"\\b\\d{3}-\\d{2}-\\d{4}\\b",
    r"\\b(?:\\d[ -]*?){13,16}\\b",
    r"token\\s*[:=]?\\s*\\S+",
    r"api[_ -]?key\\s*[:=]?\\s*\\S+",
]

def contains_sensitive_text(text: str) -> bool:
    low = text.lower()
    return any(re.search(p, low, re.IGNORECASE) for p in SENSITIVE_PATTERNS)

def redact_image_text_regions(image_path: str, output_path: str) -> str:
    \"\"\"
    Local redaction pass.
    Uses OCR bounding boxes and blacks out regions matching sensitive patterns.
    If OCR is unavailable, it returns the original image copied to output.
    \"\"\"
    img = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(img)

    try:
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        n = len(data.get("text", []))
        for i in range(n):
            word = data["text"][i] or ""
            context = word.lower()
            if contains_sensitive_text(context) or context in {"password", "passcode", "token"}:
                x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
                pad = 8
                draw.rectangle([x-pad, y-pad, x+w+pad+180, y+h+pad], fill="black")
    except Exception:
        pass

    img.save(output_path)
    return output_path
