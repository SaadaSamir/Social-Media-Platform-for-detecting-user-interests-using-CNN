import pandas as pd
import numpy as np
from google.colab import drive
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score


df = pd.read_csv('/content/drive/MyDrive/reddit_data.csv') 
le = LabelEncoder()
df['username'] = le.fit_transform(df['username'])
df['subreddit'] = le.fit_transform(df['subreddit'])
scaler = StandardScaler()
cols_to_scale = ['username', 'subreddit', 'num_interactions','avrg']
df[cols_to_scale] = scaler.fit_transform(df[cols_to_scale])
X = df[['username', 'subreddit', 'num_interactions', 'avrg']].to_numpy()
y = df['binary_value'].to_numpy()
train_X, test_X, train_y, test_y = train_test_split(X, y, test_size=0.2, random_state=42)
model = DecisionTreeClassifier()
model.fit(train_X, train_y)
y_pred = model.predict(test_X)
test_accuracy = accuracy_score(test_y, y_pred)
print(f'Test accuracy: {test_accuracy}')
precision = precision_score(test_y, y_pred)
recall = recall_score(test_y, y_pred)
f1 = f1_score(test_y, y_pred)
print("Precision: ", precision)
print("Recall: ", recall)
print("F1-score: ", f1)

