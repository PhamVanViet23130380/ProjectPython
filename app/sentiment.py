from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch, os, random, numpy as np

SEED = 42
torch.manual_seed(SEED)
random.seed(SEED)
np.random.seed(SEED)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False

MODEL_PATH = os.path.join("app", "models", "visobert")

_tokenizer = None
_model = None
_device = torch.device("cpu")

def load_model():
    global _tokenizer, _model
    if _tokenizer is None or _model is None:
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
        _model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
        _model.to(_device)
        _model.eval()

def analyze_sentiment(text: str):
    if not text or not text.strip():
        return "neu", 0.0

    load_model()

    inputs = _tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=256
    )

    inputs = {k: v.to(_device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = _model(**inputs)

    probs = torch.softmax(outputs.logits, dim=1)[0]
    confidence, label_id = torch.max(probs, dim=0)
    conf_value = confidence.item()

    sentiment = _model.config.id2label[label_id.item()].lower()

    # Lấy xác suất của từng nhãn (NEG=0, POS=1, NEU=2)
    neg_prob = probs[0].item()
    pos_prob = probs[1].item()
    

    # Nếu xác suất cao nhất là NEU hoặc confidence thấp -> neutral
    # Hoặc nếu khoảng cách giữa pos và neg quá nhỏ -> neutral
    CONFIDENCE_THRESHOLD = 0.6
    DIFF_THRESHOLD = 0.2

    if sentiment.startswith("neu"):
        sentiment = "neu"
    elif sentiment.startswith("pos"):
        # Nếu confidence thấp hoặc pos không vượt trội hơn neg nhiều -> neutral
        if conf_value < CONFIDENCE_THRESHOLD or (pos_prob - neg_prob) < DIFF_THRESHOLD:
            sentiment = "neu"
        else:
            sentiment = "pos"
    elif sentiment.startswith("neg"):
        # Nếu confidence thấp hoặc neg không vượt trội hơn pos nhiều -> neutral
        if conf_value < CONFIDENCE_THRESHOLD or (neg_prob - pos_prob) < DIFF_THRESHOLD:
            sentiment = "neu"
        else:
            sentiment = "neg"
    else:
        sentiment = "neu"

    return sentiment, round(conf_value, 4)
