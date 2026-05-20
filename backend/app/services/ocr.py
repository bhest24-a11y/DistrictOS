from pathlib import Path
from PIL import Image
import pytesseract


def extract_text_from_image(path: Path) -> dict:
    try:
        image = Image.open(path).convert("RGB")
        text = pytesseract.image_to_string(image)

        return {
            "success": True,
            "text": text.strip(),
            "confidence": 0.75 if text.strip() else 0.2,
            "source": str(path.name)
        }

    except Exception as e:
        return {
            "success": False,
            "text": "",
            "confidence": 0.0,
            "source": str(path.name),
            "error": str(e)
        }


def extract_text_from_images(paths: list[Path]) -> dict:
    all_text = []
    confidence_scores = []

    for path in paths:
        result = extract_text_from_image(path)
        if result.get("text"):
            all_text.append(result["text"])
        confidence_scores.append(result.get("confidence", 0.0))

    avg_confidence = (
        sum(confidence_scores) / len(confidence_scores)
        if confidence_scores else 0.0
    )

    return {
        "text": "\n\n".join(all_text),
        "confidence": round(avg_confidence, 2),
        "frames_processed": len(paths)
    }
