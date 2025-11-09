"""Fine-tune DistilBERT for ingredient token classification."""
from __future__ import annotations

import json
from dataclasses import dataclass
import argparse
from pathlib import Path
from typing import Dict, List, Sequence

import numpy as np
import torch
from datasets import Dataset, DatasetDict, load_from_disk
from rich.console import Console
from rich.table import Table
from seqeval.metrics import classification_report, f1_score, precision_score, recall_score
from transformers import (
    AutoModelForTokenClassification,
    AutoTokenizer,
    DataCollatorForTokenClassification,
    EarlyStoppingCallback,
    Trainer,
    TrainerCallback,
    TrainingArguments,
)

from scripts.common import BASE_MODEL, save_json, set_seed

console = Console()


def parse_cli_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train token classification model.")
    parser.add_argument(
        "--resume_from_checkpoint",
        type=str,
        default=None,
        help="Path to a checkpoint directory to resume training from.",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Automatically resume from the latest checkpoint under the model directory.",
    )
    return parser.parse_args()

ROOT_DIR = Path(__file__).resolve().parent
CACHE_DIR = ROOT_DIR / "cache"
NER_DATASET_DIR = CACHE_DIR / "ner"
META_DIR = CACHE_DIR / "meta"
OUTPUTS_DIR = ROOT_DIR / "outputs"
MODEL_DIR = ROOT_DIR / "model" / "token_classification"
MODEL_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

TEST_METRICS_PATH = OUTPUTS_DIR / "ner_test_metrics.json"

EPOCHS = 6
TRAIN_BATCH_SIZE = 16
EVAL_BATCH_SIZE = 16
LEARNING_RATE = 3e-5
WEIGHT_DECAY = 0.01
WARMUP_RATIO = 0.1
PATIENCE = 2


@dataclass
class MetricsTracker:
    id2label: Dict[int, str]
    last_report: Dict[str, Dict[str, float]] | None = None
    last_overall: Dict[str, float] | None = None
    last_sequences: tuple[list[list[str]], list[list[str]]] | None = None

    def update(self, refs: Sequence[Sequence[str]], preds: Sequence[Sequence[str]]) -> Dict[str, float]:
        report = classification_report(refs, preds, output_dict=True, zero_division=0)
        overall = {
            "precision": precision_score(refs, preds),
            "recall": recall_score(refs, preds),
            "f1": f1_score(refs, preds),
        }
        self.last_report = report
        self.last_overall = overall
        self.last_sequences = (list(refs), list(preds))
        return overall

    def render_confusion_summary(self) -> None:
        if not self.last_report or not self.last_sequences:
            return
        refs, preds = self.last_sequences
        entity_counts = _compute_entity_counts(refs, preds)
        table = Table(title="Entity Summary", show_header=True, header_style="bold magenta")
        table.add_column("Entity")
        table.add_column("True Count", justify="right")
        table.add_column("Pred Count", justify="right")
        table.add_column("Correct", justify="right")
        table.add_column("Precision", justify="right")
        table.add_column("Recall", justify="right")
        table.add_column("F1", justify="right")

        for entity, stats in entity_counts.items():
            metrics = self.last_report.get(entity, {})
            table.add_row(
                entity,
                str(stats["true"]),
                str(stats["pred"]),
                str(stats["correct"]),
                f"{metrics.get('precision', 0.0):.3f}",
                f"{metrics.get('recall', 0.0):.3f}",
                f"{metrics.get('f1-score', 0.0):.3f}",
            )
        console.print(table)


def _compute_entity_counts(
    refs: Sequence[Sequence[str]], preds: Sequence[Sequence[str]]
) -> Dict[str, Dict[str, int]]:
    entity_names = sorted({label.split("-")[-1] for seq in refs for label in seq if label != "O"})
    if not entity_names:
        return {}
    counts = {
        name: {"true": 0, "pred": 0, "correct": 0} for name in entity_names
    }

    for ref_seq in refs:
        for label in ref_seq:
            if label.startswith("B-"):
                counts[label.split("-", 1)[1]]["true"] += 1
    for pred_seq in preds:
        for label in pred_seq:
            if label.startswith("B-"):
                counts[label.split("-", 1)[1]]["pred"] += 1

    for ref_seq, pred_seq in zip(refs, preds):
        ref_entities = _extract_entities(ref_seq)
        pred_entities = _extract_entities(pred_seq)
        for ent in ref_entities:
            if ent in pred_entities:
                counts[ent[0]]["correct"] += 1
    return counts


def _extract_entities(labels: Sequence[str]) -> List[tuple[str, int, int]]:
    entities: List[tuple[str, int, int]] = []
    active_label: str | None = None
    start = 0
    for idx, tag in enumerate(labels + ["O"]):
        if tag.startswith("B-"):
            if active_label is not None:
                entities.append((active_label, start, idx))
            active_label = tag.split("-", 1)[1]
            start = idx
        elif tag.startswith("I-"):
            continue
        else:
            if active_label is not None:
                entities.append((active_label, start, idx))
                active_label = None
    return entities


class MetricsCallback(TrainerCallback):
    def __init__(self, tracker: MetricsTracker) -> None:
        self.tracker = tracker

    def on_evaluate(self, args, state, control, metrics, **kwargs):  # noqa: D401
        if self.tracker.last_overall:
            console.rule(f"Evaluation step {state.global_step}")
            console.log(
                "Overall precision={precision:.3f} recall={recall:.3f} f1={f1:.3f}".format(
                    **self.tracker.last_overall
                )
            )
            self.tracker.render_confusion_summary()
        return control


def _load_label_maps() -> tuple[Dict[str, int], Dict[int, str]]:
    ner_label_path = META_DIR / "ner_label2id.json"
    ner_id_path = META_DIR / "ner_id2label.json"
    if not ner_label_path.exists() or not ner_id_path.exists():
        raise FileNotFoundError(
            f"Missing label maps in {META_DIR}. Run `python scripts/convert_to_hf.py` first."
        )
    with ner_label_path.open("r", encoding="utf-8") as f:
        label2id = {label: int(idx) for label, idx in json.load(f).items()}
    with ner_id_path.open("r", encoding="utf-8") as f:
        id2label = {int(idx): label for idx, label in json.load(f).items()}
    return label2id, id2label


def prepare_datasets() -> DatasetDict:
    if not NER_DATASET_DIR.exists():
        raise FileNotFoundError(
            f"Token classification dataset not found at {NER_DATASET_DIR}. "
            "Run `python scripts/convert_to_hf.py` first."
        )
    dataset = load_from_disk(str(NER_DATASET_DIR))
    if isinstance(dataset, DatasetDict):
        required = {"train", "val", "test"}
        if not required.issubset(dataset.keys()):
            raise ValueError(f"Dataset at {NER_DATASET_DIR} missing splits: {sorted(required - set(dataset.keys()))}")
        return dataset
    if not isinstance(dataset, Dataset):
        raise TypeError(f"Unexpected dataset type {type(dataset)} loaded from {NER_DATASET_DIR}")
    train_val = dataset.train_test_split(test_size=0.2, seed=42)
    val_test = train_val["test"].train_test_split(test_size=0.5, seed=42)
    return DatasetDict(
        {
            "train": train_val["train"],
            "val": val_test["train"],
            "test": val_test["test"],
        }
    )


def compute_metrics_builder(tracker: MetricsTracker):
    def compute_metrics(eval_preds):
        logits, labels = eval_preds
        predictions = np.argmax(logits, axis=-1)
        refs: list[list[str]] = []
        preds: list[list[str]] = []
        for pred_seq, label_seq in zip(predictions, labels):
            ref_tags: list[str] = []
            pred_tags: list[str] = []
            for pred_id, label_id in zip(pred_seq, label_seq):
                if label_id == -100:
                    continue
                ref_tags.append(tracker.id2label[int(label_id)])
                pred_tags.append(tracker.id2label[int(pred_id)])
            refs.append(ref_tags)
            preds.append(pred_tags)
        overall = tracker.update(refs, preds)
        metrics = {
            "precision": overall["precision"],
            "recall": overall["recall"],
            "f1": overall["f1"],
        }
        if tracker.last_report:
            for entity, stats in tracker.last_report.items():
                if entity in {"micro avg", "macro avg", "weighted avg"}:
                    continue
                metrics[f"{entity}_precision"] = stats.get("precision", 0.0)
                metrics[f"{entity}_recall"] = stats.get("recall", 0.0)
                metrics[f"{entity}_f1"] = stats.get("f1-score", 0.0)
        return metrics

    return compute_metrics


def main() -> None:
    args = parse_cli_args()
    set_seed(42)
    ds = prepare_datasets()

    ner_label2id, id2label = _load_label_maps()

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    model = AutoModelForTokenClassification.from_pretrained(
        BASE_MODEL,
        num_labels=len(ner_label2id),
        id2label=id2label,
        label2id=ner_label2id,
    )

    data_collator = DataCollatorForTokenClassification(tokenizer)

    tracker = MetricsTracker(id2label=id2label)
    compute_metrics = compute_metrics_builder(tracker)

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
        metric_for_best_model="f1",
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
        data_collator=data_collator,
        compute_metrics=compute_metrics,
        callbacks=[
            EarlyStoppingCallback(early_stopping_patience=PATIENCE),
            MetricsCallback(tracker),
        ],
    )

    resume_path: str | bool | None = None
    if args.resume_from_checkpoint:
        resume_path = args.resume_from_checkpoint
    elif args.resume:
        checkpoints = sorted(
            MODEL_DIR.glob("checkpoint-*"),
            key=lambda path: int(path.name.split("-")[-1]) if path.name.split("-")[-1].isdigit() else -1,
        )
        if checkpoints:
            resume_path = str(checkpoints[-1])
    if resume_path:
        console.rule(f"Resuming training from {resume_path}")
        trainer.train(resume_from_checkpoint=resume_path)
    else:
        console.rule("Starting training")
        trainer.train()

    console.rule("Evaluation on validation set")
    best_metrics = trainer.evaluate(ds["val"])  # ensures compute_metrics runs for best model

    console.rule("Evaluation on test set")
    test_metrics = trainer.evaluate(ds["test"])

    console.rule("Saving artifacts")
    trainer.save_model(str(MODEL_DIR))
    tokenizer.save_pretrained(str(MODEL_DIR))
    save_json({label: int(idx) for label, idx in ner_label2id.items()}, MODEL_DIR / "label2id.json")
    save_json({int(idx): label for idx, label in id2label.items()}, MODEL_DIR / "id2label.json")
    save_json({"best_val": best_metrics, "test": test_metrics}, MODEL_DIR / "metrics.json")
    save_json(test_metrics, TEST_METRICS_PATH)

    tracker.render_confusion_summary()
    console.log(f"Training complete. Best model saved to {MODEL_DIR}")


if __name__ == "__main__":
    if not NER_DATASET_DIR.exists():
        raise FileNotFoundError(
            f"Cache directory not found at {NER_DATASET_DIR}. Run `python scripts/convert_to_hf.py` first."
        )
    main()
