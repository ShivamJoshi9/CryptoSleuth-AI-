import os
import pandas as pd
from datasets import Dataset
from transformers import (
    DistilBertTokenizerFast,
    DistilBertForSequenceClassification,
    Trainer,
    TrainingArguments
)

# ---------------- CONFIG ---------------- #

LABEL_MAP = {
    "trace_transactions": 0,
    "trace_to_exchange": 1,
    "expand_wallet": 2,
    "trace_path": 3,
    "time_filter": 4
}

NUM_LABELS = len(LABEL_MAP)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_PATH = os.path.join(BASE_DIR, "data", "nlp_intents.csv")
MODEL_OUT = os.path.join(BASE_DIR, "models", "intent_classifier")

# ---------------- TRAINING ---------------- #

def main():
    # Load dataset
    df = pd.read_csv(DATA_PATH)

    # Encode labels
    df["label"] = df["label"].map(LABEL_MAP)

    if df["label"].isnull().any():
        raise ValueError("❌ Unknown label found in CSV")

    dataset = Dataset.from_pandas(df)

    tokenizer = DistilBertTokenizerFast.from_pretrained(
        "distilbert-base-uncased"
    )

    def tokenize(batch):
        return tokenizer(
            batch["text"],
            padding="max_length",
            truncation=True
        )

    dataset = dataset.map(tokenize, batched=True)

    dataset = dataset.train_test_split(test_size=0.2)

    model = DistilBertForSequenceClassification.from_pretrained(
        "distilbert-base-uncased",
        num_labels=NUM_LABELS
    )

    training_args = TrainingArguments(
        output_dir=MODEL_OUT,
        evaluation_strategy="epoch",
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        num_train_epochs=5,
        logging_dir="./logs",
        save_strategy="epoch",
        load_best_model_at_end=True
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset["train"],
        eval_dataset=dataset["test"],
        tokenizer=tokenizer
    )

    trainer.train()

    model.save_pretrained(MODEL_OUT)
    tokenizer.save_pretrained(MODEL_OUT)

    print("✅ Intent classifier trained and saved successfully")

if __name__ == "__main__":
    main()
