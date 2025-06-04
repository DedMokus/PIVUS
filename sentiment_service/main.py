import os
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import onnxruntime
import numpy as np

app = FastAPI(title="Sentiment Service")

# Задаем имя модели и путь для сохранения ONNX модели
MODEL_NAME = os.getenv("MODEL_NAME", "cointegrated/rubert-tiny-sentiment-balanced")
ONNX_MODEL_PATH = os.getenv("ONNX_MODEL_PATH", "model/model.onnx")

# Загружаем токенизатор и PyTorch модель
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

# Если ONNX-модель не существует, конвертируем PyTorch модель в ONNX
if not os.path.exists(ONNX_MODEL_PATH):
    print(
        "ONNX модель не найдена. Начинается конвертация PyTorch модели в формат ONNX..."
    )
    # Используем примерный текст для формирования dummy-входа
    dummy_text = "Это пример текста для конвертации модели в onnx."
    dummy_inputs = tokenizer(
        dummy_text, return_tensors="pt", max_length=512, truncation=True
    )
    # Экспортируем модель: передаем кортеж из (input_ids, attention_mask)
    torch.onnx.export(
        model,
        (dummy_inputs["input_ids"], dummy_inputs["attention_mask"]),
        ONNX_MODEL_PATH,
        input_names=["input_ids", "attention_mask"],
        output_names=["logits"],
        dynamic_axes={
            "input_ids": {0: "batch_size", 1: "sequence_length"},
            "attention_mask": {0: "batch_size", 1: "sequence_length"},
            "logits": {0: "batch_size"},
        },
        opset_version=17,
    )
    print(f"Модель успешно конвертирована и сохранена по пути: {ONNX_MODEL_PATH}")

# Загружаем ONNX модель для инференса
ort_session = onnxruntime.InferenceSession(ONNX_MODEL_PATH)


class TextData(BaseModel):
    text: str


@app.post("/sentiment-check")
def sentiment_check(data: TextData):
    # Подготавливаем входные данные с помощью токенизатора
    inputs = tokenizer(data.text, return_tensors="pt", max_length=512, truncation=True)
    # Конвертируем тензоры в numpy массивы
    input_ids = inputs["input_ids"].cpu().numpy()
    attention_mask = inputs["attention_mask"].cpu().numpy()

    # Подготавливаем словарь с входными данными для ONNX модели
    onnx_inputs = {"input_ids": input_ids, "attention_mask": attention_mask}
    # Получаем результаты инференса от ONNX модели
    ort_outputs = ort_session.run(None, onnx_inputs)
    logits = ort_outputs[0]  # ожидается форма [batch_size, num_classes]

    # Простейшая логика: считаем, что логит для "negative" находится в индексе 0
    negative_score = logits[0][0]
    sentiment = "negative" if negative_score > 0 else "positive"
    return {"sentiment": sentiment}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)
