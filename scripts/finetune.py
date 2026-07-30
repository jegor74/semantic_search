import csv
from datasets import Dataset
from sentence_transformers import SentenceTransformer, SentenceTransformerTrainer, SentenceTransformerTrainingArguments
from sentence_transformers.sentence_transformer.losses import MultipleNegativesRankingLoss


train_data = []                                                                  # loading data
with open("data/finetune/train_data.csv", "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        train_data.append({"anchor": row["anchor"],
                           "positive": row["positive"],
                           "negative": row["negative"]})
dataset = Dataset.from_list(train_data)

model = SentenceTransformer("intfloat/multilingual-e5-small")                    # loading model

args = SentenceTransformerTrainingArguments(                                     # setting arguments
    output_dir="models/finetuned",
    num_train_epochs=3,
    per_device_train_batch_size=8,
    learning_rate=1e-5,
    warmup_steps=100
)


loss = MultipleNegativesRankingLoss(model)                                       # training model
trainer = SentenceTransformerTrainer(
    model=model,
    args=args,
    train_dataset=dataset,
    loss=loss
)
trainer.train()

model.save_pretrained("models/finetuned")                                         # saving new model
