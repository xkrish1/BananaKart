"""Fine-tune DistilBERT for urgency text classification."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

import numpy as np
import torch
from datasets import Dataset, DatasetDict, load_from_disk
from evaluate import load as load_metric
from rich.console import Console
from rich.table import Table
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    EarlyStoppingCallback,
    Trainer,
    TrainingArguments,
)
from transformers.data.data_collator import default_data_collator

from scripts.common import BASE_MODEL, save_json, set_seed

console = Console()

ROOT_DIR = Path(__file__).resolve().parent
CACHE_DIR = ROOT_DIR / "cache"
CLS_DATASET_DIR = CACHE_DIR / "cls"
META_DIR = CACHE_DIR / "meta"
OUTPUTS_DIR = ROOT_DIR / "outputs"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
MODEL_DIR = ROOT_DIR / "model" / "text_classification"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

TEST_METRICS_PATH = OUTPUTS_DIR / "cls_test_metrics.json"

EPOCHS = 4
TRAIN_BATCH_SIZE = 32
EVAL_BATCH_SIZE = 32
LEARNING_RATE = 3e-5
WEIGHT_DECAY = 0.01
WARMUP_RATIO = 0.1
PATIENCE = 2


def prepare_datasets() -> DatasetDict:
    if not CLS_DATASET_DIR.exists():
        raise FileNotFoundError(
            f"Text classification dataset not found at {CLS_DATASET_DIR}. "
            "Run `python scripts/convert_to_hf.py` first."
        )
    dataset = load_from_disk(str(CLS_DATASET_DIR))
    if isinstance(dataset, DatasetDict):
        required = {"train", "val", "test"}
        if not required.issubset(dataset.keys()):
            raise ValueError(f"Dataset at {CLS_DATASET_DIR} missing splits: {sorted(required - set(dataset.keys()))}")
        return dataset
    if not isinstance(dataset, Dataset):
        raise TypeError(f"Unexpected dataset type {type(dataset)} loaded from {CLS_DATASET_DIR}")
    train_val = dataset.train_test_split(test_size=0.2, seed=42)
    val_test = train_val["test"].train_test_split(test_size=0.5, seed=42)
    return DatasetDict(
        {
            "train": train_val["train"],
            "val": val_test["train"],
            "test": val_test["test"],
        }
    )


def _load_label_maps() -> tuple[Dict[str, int], Dict[int, str]]:
    cls_label_path = META_DIR / "cls_label2id.json"
    if not cls_label_path.exists():
        raise FileNotFoundError(
            f"Missing classification label map at {cls_label_path}. Run `python scripts/convert_to_hf.py` first."
        )
    with cls_label_path.open("r", encoding="utf-8") as f:
        cls_label2id = {label: int(idx) for label, idx in json.load(f).items()}
    id2label = {idx: label for label, idx in cls_label2id.items()}
    return cls_label2id, id2label


def compute_confusion_counts(preds: List[int], refs: List[int], id2label: Dict[int, str]) -> Dict[str, Dict[str, int]]:
    matrix: Dict[str, Dict[str, int]] = {
        id2label[i]: {id2label[j]: 0 for j in range(len(id2label))} for i in range(len(id2label))
    }
    for pred, ref in zip(preds, refs):
        matrix[id2label[ref]][id2label[pred]] += 1
    return matrix


def render_confusion(matrix: Dict[str, Dict[str, int]]) -> None:
    table = Table(title="Confusion Matrix", show_header=True, header_style="bold cyan")
    headers = ["True\\Pred"] + list(matrix.keys())
    for header in headers:
        table.add_column(header, justify="center")
    for true_label, row in matrix.items():
        table.add_row(true_label, *[str(row[pred_label]) for pred_label in matrix.keys()])
    console.print(table)


def main() -> None:
    set_seed(42)
    ds = prepare_datasets()

    cls_label2id, id2label = _load_label_maps()

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    model = AutoModelForSequenceClassification.from_pretrained(
        BASE_MODEL,
        num_labels=len(cls_label2id),
        id2label=id2label,
        label2id=cls_label2id,
    )

    accuracy_metric = load_metric("accuracy")
    f1_metric = load_metric("f1")

    def compute_metrics(eval_preds):
        logits, labels = eval_preds
        predictions = np.argmax(logits, axis=-1)
        accuracy = accuracy_metric.compute(predictions=predictions, references=labels)["accuracy"]
        macro_f1 = f1_metric.compute(
            predictions=predictions, references=labels, average="macro"
        )["f1"]
        per_class_result = f1_metric.compute(
            predictions=predictions, references=labels, average=None
        )["f1"]
        if isinstance(per_class_result, (int, float)):
            per_class = [float(per_class_result)]
        else:
            per_class = list(per_class_result)
        metrics = {
            "accuracy": accuracy,
            "macro_f1": macro_f1,
        }
        for idx, score in enumerate(per_class):
            label = id2label[idx]
            metrics[f"f1_{label}"] = score
        metrics["confusion"] = compute_confusion_counts(predictions.tolist(), labels.tolist(), id2label)
        render_confusion(metrics["confusion"])
        return metrics

    training_args = TrainingArguments(
        output_dir=str(MODEL_DIR),
        overwrite_output_dir=True,
        num_train_epochs=EPOCHS,
        per_device_train_batch_size=TRAIN_BATCH_SIZE,
        per_device_eval_batch_size=EVAL_BATCH_SIZE,
        learning_rate=LEARNING_RATE,
        weight_decay=WEIGHT_DECAY,
        warmup_ratio=WARMUP_RATIO,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="macro_f1",
        greater_is_better=True,
        logging_strategy="epoch",
        report_to=[],
        fp16=torch.cuda.is_available(),
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=ds["train"],
        eval_dataset=ds["val"],
        tokenizer=tokenizer,
        data_collator=default_data_collator,
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=PATIENCE)],
    )

    console.rule("Starting training")
    trainer.train()

    console.rule("Evaluation on validation set")
    best_metrics = trainer.evaluate(ds["val"])

    console.rule("Evaluation on test set")
    test_metrics = trainer.evaluate(ds["test"])

    console.rule("Saving artifacts")
    trainer.save_model(str(MODEL_DIR))
    tokenizer.save_pretrained(str(MODEL_DIR))
    save_json({label: int(idx) for label, idx in cls_label2id.items()}, MODEL_DIR / "label2id.json")
    save_json({int(idx): label for idx, label in id2label.items()}, MODEL_DIR / "id2label.json")
    save_json({"best_val": best_metrics, "test": test_metrics}, MODEL_DIR / "metrics.json")
    save_json(test_metrics, TEST_METRICS_PATH)

    console.log(f"Training complete. Best model saved to {MODEL_DIR}")


if __name__ == "__main__":
    if not CLS_DATASET_DIR.exists():
        raise FileNotFoundError(
            f"Cache directory not found at {CLS_DATASET_DIR}. Run `python scripts/convert_to_hf.py` first."
        )
    main()
