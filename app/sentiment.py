from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import os

# Path tới model local
MODEL_PATH = os.path.join("app", "models", "visobert")

_tokenizer = None
_model = None
MODEL_AVAILABLE = False

LABELS = ["negative", "neutral", "positive"]


def load_model():
    global _tokenizer, _model
    if _tokenizer is None or _model is None:
        try:
            print("Loading local ViSoBERT model...")
            _tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
            _model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
            _model.eval()
            global MODEL_AVAILABLE
            MODEL_AVAILABLE = True
        except Exception as e:
            # If the model or weights are missing/corrupt, fall back to rule-based
            print("Failed to load ViSoBERT model, falling back to rule-based sentiment. Error:", e)
            _tokenizer = None
            _model = None
            MODEL_AVAILABLE = False


def analyze_sentiment(text: str):
    if not text or not text.strip():
        return "neutral", 0.0
    # Attempt to use the transformer model if available; otherwise use rules
    text_lower = text.lower()
    try:
        load_model()
        if MODEL_AVAILABLE and _tokenizer is not None and _model is not None:
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
        else:
            # Model not available; set defaults and fall through to rule-based checks
            sentiment = None
            confidence = 0.0
    except Exception as e:
        print('Error during transformer sentiment analysis, falling back to rules:', e)
        sentiment = None
        confidence = 0.0

    # Rule-based boost (rất tốt cho tiếng Việt)
    strong_positive = [
        "rất đẹp", "cực đẹp", "đẹp lắm", "tuyệt vời",
        "xuất sắc", "sạch sẽ", "rất sạch", "hài lòng",
        "tuyệt", "trải nghiệm tốt", "quá tốt",
        "đáng tiền", "giá tốt", "siêu đẹp",
        "ấn tượng", "hết ý", "quá tuyệt", "miễn chê", "số một", "hàng đầu", "tuyệt hảo", "đáng ngưỡng mộ",
        "đỉnh cao", "vượt trội", "đáng khen", "xuất sắc nhất", "hoàn hảo", "tuyệt diệu", "đáng giá", "đáng đồng tiền bát gạo",
        "đáng đồng tiền", "tuyệt vời nhất", "đáng đồng tiền nhất", "đáng đồng tiền bát gạo nhất",
"chất lượng cao", "cao cấp", "sang trọng", "hoàn hảo", "đỉnh của chóp", "đỉnh của đỉnh",
        "nhiệt tình", "chu đáo", "thân thiện", "hỗ trợ tốt", "tận tâm"
    ]

    strong_negative = [
        "dơ", "bẩn", "rất tệ", "kinh",
        "xấu", "không hài lòng", "quá tệ", "bừa bộn",
        
        # Bổ sung
        "tồi tệ", "kém chất lượng", "hỏng", "cũ kỹ", "xuống cấp", "rách nát", 
        "thất vọng", "bực mình", "quá dở", "không chấp nhận được", "không tốt", 
        "mùi", "ẩm mốc", "cáu bẩn", "chuột", "gián", "bụi bẩn", "lộn xộn", 
        "chật chội", "thờ ơ", "không chuyên nghiệp", "thái độ tệ",
        "hư hỏng", "lỗi thời", "đắt đỏ", "quá đắt", "đắt quá", "không đáng tiền",
        "không xứng đáng", "kém xa", "thua kém", "tệ hại", "khủng khiếp", "kinh khủng",
        "khó chịu", "bất tiện", "phiền toái", "rắc rối",
    ]

    neutral_keywords = [
    "bình thường", "tạm ổn", "tàm tạm", "ổn",
    "không có gì đặc biệt", "được",
    "chấp nhận được", "không quá tệ", "đúng như mô tả", "đúng ý", "đúng giá", 
    "chỉ vậy thôi", "không hơn không kém",
    "vừa đủ", "hài lòng ở mức độ vừa phải", "không tốt lắm", "không quá xuất sắc",
    "trung bình", "bình thường thôi", "tạm được", "không có gì nổi bật",
    ]

    # Nếu chứa từ mạnh → ép thành positive
    if any(k in text_lower for k in strong_positive):
        return "positive", round(float(confidence) if not hasattr(confidence, 'item') else confidence.item(), 4)

    # Nếu chứa từ tiêu cực mạnh → ép negative
    if any(k in text_lower for k in strong_negative):
        return "negative", round(float(confidence) if not hasattr(confidence, 'item') else confidence.item(), 4)
    
    if any(k in text_lower for k in neutral_keywords):
        return "neutral", round(float(confidence) if not hasattr(confidence, 'item') else confidence.item(), 4)

    # If transformer produced a sentiment, prefer it; otherwise derive from rules
    if sentiment:
        return sentiment, round(float(confidence) if not hasattr(confidence, 'item') else confidence.item(), 4)

    # Fallback: basic heuristic using star keywords
    # If none matched above, return neutral with low confidence
    return "neutral", round(float(confidence) if not hasattr(confidence, 'item') else confidence.item(), 4)
