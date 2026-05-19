from PIL import Image

def contains_sensitive_text(text: str) -> bool:
    sensitive_words = ["password", "passcode", "token", "api_key", "ssn"]
    return any(word in text.lower() for word in sensitive_words)

def redact_image_text_regions(image_path: str, output_path: str) -> str:
    image = Image.open(image_path).convert("RGB")
    image.save(output_path)
    return output_path
