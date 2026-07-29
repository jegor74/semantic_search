import re
import csv
import json
import random


with open("data/metadata/chunks.json", "r", encoding="utf-8") as file:                        # loading .json file with chunks
    chunks = json.load(file)


with open("data/finetune/train_data.csv", "w", encoding="utf-8", newline="") as csv_file:     # opening .csv file for training data
   
    writer = csv.writer(csv_file)                                                             # making writer
    writer.writerow(["anchor", "positive", "negative"])                                       # header of .csv file

    for chunk in chunks:

        anchor_match = re.search(r"^#.+", chunk["text"], re.MULTILINE)                        # finding anchor in chunk (###...)
        if not anchor_match:                                                                  # skipping anchor if there is no in chunk
            continue
        anchor = anchor_match.group(0)                                                        # taking text of anchor
    
        text = chunk["text"]
        pos = text.find(anchor) + len(anchor)
        positive = text[pos:].strip()                                                         # finding positive text for anchor (all text after the anchor)
        
        other_chunks = [other for other in chunks if other["source"] != chunk["source"]]      # taking all other chunks for random choosing
        if other_chunks:
            negative = random.choice(other_chunks)["text"]                                    # taking negative text for anchor from other chunks
        else:
            continue                                                                          # skipping if there is no negative text in chunk

        writer.writerow([anchor, positive, negative])                                         # writing (anchor, positive, negative) to .csv file
