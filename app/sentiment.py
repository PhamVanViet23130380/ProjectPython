from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import os

MODEL_PATH = os.path.join("app", "models", "visobert")

_tokenizer = None
_model = None

def load_model():
    global _tokenizer, _model

    if _tokenizer is None or _model is None:
        print("Loading local ViEmotion model...")
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
        _model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)

def analyze_sentiment(text: str):
    load_model()

    inputs = _tokenizer(text, return_tensors="pt", truncation=True)

    with torch.no_grad():
        outputs = _model(**inputs)

    logits = outputs.logits
    label = logits.argmax(dim=1).item()

    # Mapping theo mô hình local
    mapping = ["negative", "neutral", "positive"]

    text_lower = text.lower()

    # BOOST RULE: ép các câu cực tích cực => positive
    strong_positive = [
        "rất đẹp", "cực đẹp", "đẹp lắm", "tuyệt vời",
        "xuất sắc", "sạch sẽ", "rất sạch", "hài lòng",
        "tuyệt", "trải nghiệm tốt", "quá tốt",
        "đáng tiền", "giá tốt", "siêu đẹp"
    ]

    strong_negative = [
        "dơ", "bẩn", "rất tệ", "kinh", "xấu",
        "không hài lòng", "quá tệ", "bừa bộn"
    ]

    # Nếu chứa từ mạnh → ép thành positive
    if any(k in text_lower for k in strong_positive):
        return "positive"

    # Nếu chứa từ tiêu cực mạnh → ép negative
    if any(k in text_lower for k in strong_negative):
        return "negative"

    return mapping[label]
