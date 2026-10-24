import tensorflow as tf
import numpy as np
from sklearn.metrics import confusion_matrix, accuracy_score

IMG_SIZE = 64

model = tf.keras.models.load_model("blink_model.h5")

test_data = tf.keras.preprocessing.image_dataset_from_directory(
    "dataset/test",
    image_size=(64,64),
    batch_size=32,
    shuffle=False
)

X = []
y_true = []

for images, labels in test_data:
    X.append(images / 255.0)
    y_true.extend(labels.numpy())

X = np.concatenate(X)

pred = model.predict(X)
y_pred = (pred > 0.5).astype(int).flatten()

acc = accuracy_score(y_true, y_pred)

cm = confusion_matrix(y_true, y_pred)

TN, FP, FN, TP = cm.ravel()

FAR = FP / (FP + TN)
FRR = FN / (FN + TP)

print("Accuracy :", round(acc*100,2), "%")
print("FAR      :", round(FAR*100,2), "%")
print("FRR      :", round(FRR*100,2), "%")
print("Confusion Matrix:")
print(cm)