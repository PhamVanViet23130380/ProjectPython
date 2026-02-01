# from transformers import AutoTokenizer, AutoModelForSequenceClassification
# import torch
# import os

# MODEL_PATH = os.path.join("app", "models", "visobert")

# _tokenizer = None
# _model = None
# MODEL_AVAILABLE = False


# def load_model():
#     global _tokenizer, _model, MODEL_AVAILABLE
#     if _tokenizer is None or _model is None:
#         try:
#             print("Loading local ViSoBERT model...")
#             _tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
#             _model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
#             _model.eval()
#             MODEL_AVAILABLE = True

#             # DEBUG: in ra mapping nhãn (rất quan trọng)
#             print("Model labels:", _model.config.id2label)

#         except Exception as e:
#             print("Failed to load ViSoBERT model:", e)
#             _tokenizer = None
#             _model = None
#             MODEL_AVAILABLE = False


# def analyze_sentiment(text: str):
#     if not text or not text.strip():
#         return "neutral", 0.0

#     load_model()

#     if not MODEL_AVAILABLE:
#         return "neutral", 0.0

#     try:
#         inputs = _tokenizer(
#             text,
#             return_tensors="pt",
#             truncation=True,
#             padding=True,
#             max_length=256
#         )

#         with torch.no_grad():
#             outputs = _model(**inputs)

#         probs = torch.nn.functional.softmax(outputs.logits, dim=1)[0]
#         confidence, label_id = torch.max(probs, dim=0)

#         # ✅ LẤY LABEL ĐÚNG TỪ MODEL
#         sentiment = _model.config.id2label[label_id.item()].lower()

#         return sentiment, round(confidence.item(), 4)

#     except Exception as e:
#         print("Sentiment analysis error:", e)
#         return "neutral", 0.0
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

    sentiment = _model.config.id2label[label_id.item()].lower()

    if sentiment.startswith("pos"):
        sentiment = "pos"
    elif sentiment.startswith("neg"):
        sentiment = "neg"
    else:
        sentiment = "neu"

    return sentiment, round(confidence.item(), 4)
