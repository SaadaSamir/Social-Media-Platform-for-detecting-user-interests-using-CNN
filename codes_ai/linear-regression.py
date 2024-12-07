import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from google.colab import drive 
from sklearn.linear_model import LogisticRegression

drive.mount('/content/drive')
df = pd.read_csv("/content/drive/MyDrive/reddit_data.csv")
le = LabelEncoder()
df['username'] = le.fit_transform(df['username'])
df['subreddit'] = le.fit_transform(df['subreddit'])
scaler = StandardScaler()
cols_to_scale = ['username', 'subreddit', 'num_interactions','avrg']
scaler.fit(df[cols_to_scale])
df[cols_to_scale] = scaler.transform(df[cols_to_scale])
X = df[['username', 'subreddit', 'num_interactions','avrg']].to_numpy()
y = df['binary_value'].to_numpy()
train_X, test_X, train_y, test_y = train_test_split(X, y, test_size=0.2, random_state=42)
model_logit = LogisticRegression(penalty='none',solver='newton-cg')
model_logit.fit(train_X, train_y)
y_pred = model_logit.predict(test_X)
accuracy = accuracy_score(test_y, y_pred)
precision = precision_score(test_y, y_pred)
recall = recall_score(test_y, y_pred)
f1 = f1_score(test_y, y_pred)
print("Accuracy: ", accuracy)
print("Precision: ", precision)
print("Recall: ", recall)
print("F1-score: ", f1)
