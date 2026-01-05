import numpy as np
import tensorflow as tf
import json
import os
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

# Load data
DATA_PATH = 'processed_data'
X_val = np.load(os.path.join(DATA_PATH, 'X_val.npy'))
y_val = np.load(os.path.join(DATA_PATH, 'y_val.npy'))

# Load class names
with open(os.path.join(DATA_PATH, 'yoga_pose_model_labels.json')) as f:
    class_names = json.load(f)['classes']

# Load trained model
model = tf.keras.models.load_model('yoga_pose_model.h5')

# Predict
y_pred_probs = model.predict(X_val)
y_pred = np.argmax(y_pred_probs, axis=1)

# Evaluation metrics
print("\nClassification Report:\n")
print(classification_report(y_val, y_pred, target_names=class_names))

# Confusion matrix
cm = confusion_matrix(y_val, y_pred)

plt.figure(figsize=(10, 8))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=class_names,
            yticklabels=class_names)
plt.xlabel('Predicted')
plt.ylabel('True')
plt.title('Confusion Matrix')
plt.tight_layout()
plt.show()
