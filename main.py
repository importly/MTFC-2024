from transformers import BertTokenizer
from model import BertForMultiLabelClassification
from multilabel_pipeline import MultiLabelPipeline
from pprint import pprint
from colorama import init, Fore, Back, Style
init(autoreset=True)  # Ensure colors reset automatically

tokenizer = BertTokenizer.from_pretrained("monologg/bert-base-cased-goemotions-original")
model = BertForMultiLabelClassification.from_pretrained("monologg/bert-base-cased-goemotions-original")

go_emotions_pipe = MultiLabelPipeline(
    model=model,
    tokenizer=tokenizer,
    threshold=0.3
)

texts = [
    "I can remember a time when the borders were secure, the world was at peace, gas was cheap and plentiful, groceries were affordable, mortgage interest rates were 2.5%, and the economic outlook was optimistic. I sure do miss those good old days from three years ago.",
    'All you have to ask is this: "Are you better off now than you were three years ago?" Forget the personalities, the irrational lawfare, the stupidity of the political parties... simply ask the question.  Ask the question. '
]


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

chuck_length = 25
# Process each text
for text in texts:
    print(f"Processing text: "+Fore.BLUE+f"{text[:50]}...")
    chunks = chunk_text(text, max_length=chuck_length)

    aggregated_outputs = []
    for chunk in chunks:
        print(f"    Processing chunk: "+Fore.GREEN+f"{chunk[:50]}...")
        outputs = go_emotions_pipe([chunk])
        print("    Outputs:", end=" ")
        pprint(outputs)
        print(Style.RESET_ALL, end=" ")
        aggregated_outputs.append(outputs)