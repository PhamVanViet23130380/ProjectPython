from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import os

# Path tới model local
MODEL_NAME = "wonrax/phobert-base-vietnamese-sentiment"


_tokenizer = None
_model = None

LABELS = ["negative", "neutral", "positive"]


def load_model():
    global _tokenizer, _model
    if _tokenizer is None or _model is None:
        print("Loading ViSoBERT from HuggingFace...")
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        _model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
        _model.eval()


def analyze_sentiment(text: str):
    if not text or not text.strip():
        return "neutral", 0.0

    load_model()

    inputs = _tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=256
    )

    with torch.no_grad():
        outputs = _model(**inputs)

    probs = torch.nn.functional.softmax(outputs.logits, dim=1)[0]
    confidence, label_id = torch.max(probs, dim=0)

    sentiment = LABELS[label_id.item()]

    text_lower = text.lower()

    # Rule-based boost (rất tốt cho tiếng Việt)
    strong_positive = [
        "rất đẹp", "cực đẹp", "đẹp lắm", "tuyệt vời",
        "xuất sắc", "sạch sẽ", "rất sạch", "hài lòng",
        "tuyệt", "trải nghiệm tốt", "quá tốt",
        "đáng tiền", "giá tốt", "siêu đẹp"
    ]

    strong_negative = [
        "dơ", "bẩn", "rất tệ", "kinh",
        "xấu", "không hài lòng", "quá tệ", "bừa bộn"
    ]

    neutral_keywords = [
    "bình thường", "tạm ổn", "tàm tạm", "ổn",
    "không có gì đặc biệt", "được"
    ]

    # Nếu chứa từ mạnh → ép thành positive
    if any(k in text_lower for k in strong_positive):
        return "positive", round(confidence.item(), 4)

    # Nếu chứa từ tiêu cực mạnh → ép negative
    if any(k in text_lower for k in strong_negative):
        return "negative", round(confidence.item(), 4)
    
    if any(k in text_lower for k in neutral_keywords):
        return "neutral", round(confidence.item(), 4)

    return sentiment, round(confidence.item(), 4)
