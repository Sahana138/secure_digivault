import os
import shutil
import random

SOURCE = "dataset_raw"
DEST = "dataset"

TRAIN_SPLIT = 0.8

classes = {
    "Open-Eyes": "open",
    "Close-Eyes": "closed"
}

for folder_name, label in classes.items():

    source_folder = os.path.join(SOURCE, folder_name)

    files = os.listdir(source_folder)
    random.shuffle(files)

    split_index = int(len(files) * TRAIN_SPLIT)

    train_files = files[:split_index]
    test_files = files[split_index:]

    for file in train_files:
        src = os.path.join(source_folder, file)
        dst = os.path.join(DEST, "train", label)
        os.makedirs(dst, exist_ok=True)
        shutil.copy(src, dst)

    for file in test_files:
        src = os.path.join(source_folder, file)
        dst = os.path.join(DEST, "test", label)
        os.makedirs(dst, exist_ok=True)
        shutil.copy(src, dst)

print("Dataset Ready Successfully")