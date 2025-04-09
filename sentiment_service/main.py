import os
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import onnxruntime
import numpy as np

app = FastAPI(title="Sentiment Service")

MODEL_NAME = os.getenv("MODEL_NAME", "cointegrated/rubert-tiny-sentiment-balanced")
# Здесь можно загрузить onnx-модель, но в примере загрузим обычную PyTorch-модель
# Если используете onnxruntime, нужно сконвертировать модель в onnx заранее.
# Предположим, что у вас уже есть модель onnx. Для упрощения – PyTorch.

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

class TextData(BaseModel):
    text: str

@app.post("/sentiment-check")
def sentiment_check(data: TextData):
    inputs = tokenizer(data.text, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    # Допустим, последний слой – логиты для разных эмоций.
    # Для простоты берем вероятность "негативной" эмоции в неком индексе (пример).
    # Детали зависят от конкретной модели.
    logits = outputs.logits.squeeze().numpy()
    # Предположим, что индекс 0 – "negative"
    negative_score = logits[0]
    
    sentiment = "negative" if negative_score > 0 else "positive"
    return {"sentiment": sentiment}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)
