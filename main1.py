import os
import pathlib

import pandas as pd
from colorama import init
from pandas._libs.internals import defaultdict
from transformers import BertTokenizer

from model import BertForMultiLabelClassification
from multilabel_pipeline import MultiLabelPipeline

init(autoreset=True)  # Ensure colors reset automatically

tokenizer = BertTokenizer.from_pretrained("monologg/bert-base-cased-goemotions-original")
model = BertForMultiLabelClassification.from_pretrained("monologg/bert-base-cased-goemotions-original")

go_emotions_pipe = MultiLabelPipeline(model=model, tokenizer=tokenizer, threshold=0.3)
chuck_length = 32


def chunk_text(text, max_length=511):
    tokens = tokenizer.tokenize(text)
    token_ids = tokenizer.convert_tokens_to_ids(tokens)

    chunks = []
    current_chunk = []
    current_length = 0

    for word, word_id in zip(tokens, token_ids):
        current_chunk.append(word)
        current_length += 1

        if current_length == max_length:
            chunks.append(tokenizer.convert_tokens_to_string(current_chunk))
            current_chunk = []
            current_length = 0

    if len(current_chunk) != 0:
        chunks.append(tokenizer.convert_tokens_to_string(current_chunk))
    return chunks


# Process each text
def getScores(text):
    # print(f"Processing text: "+Fore.GREEN+f"{text[:50]}")
    chunks = chunk_text(text, max_length=chuck_length)

    aggregated_outputs = []
    for chunk in chunks:
        outputs = go_emotions_pipe([chunk])
        outputs[0]["scores"] = [float(score) for score in outputs[0]["scores"]]

        outputs = [{label: score for label, score in zip(item['labels'], item['scores'])} for item in outputs]

        aggregated_outputs.append(outputs)

    emotion_counts = defaultdict(int)
    num_chunks = len(aggregated_outputs)

    for chunk in aggregated_outputs:
        for emotion_dict in chunk:
            for emotion in emotion_dict:
                emotion_counts[emotion] += 1
    return {emotion: counts / num_chunks for (emotion, counts) in zip(emotion_counts.keys(), emotion_counts.values())}


def score(name="US_foreign_policy_in_the_Middle_East1974-2024by3months"):
    table = pd.read_csv(name + ".csv")
    print(name)
    print(table.head(1))
    for i, row in table.iterrows():
        emotion_counts = getScores(row["content"])
        print(emotion_counts)
        for emotion in emotion_counts.keys():
            table.loc[i, emotion] = emotion_counts[emotion]  # print(row)
    table.fillna(0.0, inplace=True)
    table.to_csv(pathlib.Path("./data/" + name + "_scored.csv"))
    print("saved, next")


directory = os.fsencode(".")
files = os.listdir(directory)
for file in files:
    filename = os.fsdecode(file)
    if filename.endswith(".csv"):
        score(filename[:-4])
