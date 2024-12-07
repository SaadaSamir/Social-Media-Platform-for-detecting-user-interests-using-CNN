import pandas as pd
from google.colab import drive
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split

drive.mount("/content/drive")
df = pd.read_csv("/content/drive/MyDrive/reddit_data.csv") 
le = LabelEncoder()
df['username'] = le.fit_transform(df['username'])
df['subreddit'] = le.fit_transform(df['subreddit'])
scaler = StandardScaler()
cols_to_scale = ['username', 'subreddit', 'num_interactions', 'avrg']
scaler.fit(df[cols_to_scale])
df[cols_to_scale] = scaler.transform(df[cols_to_scale])
X = df[['username', 'subreddit', 'num_interactions', 'avrg']].to_numpy()
y = df['binary_value'].to_numpy()
train_X, test_X, train_y, test_y = train_test_split(X, y, test_size=0.2, random_state=42)

model = SVC(kernel='rbf', C=1.0, random_state=42)
model.fit(train_X, train_y)

y_pred = model.predict(test_X)

print('True values: ', test_y)
print('Predicted values: ', y_pred)
print('--------------------------------')
precision = precision_score(test_y, y_pred)
recall = recall_score(test_y, y_pred)
f1 = f1_score(test_y, y_pred)
print('Test metrics:')
print(f'Test precision: {precision:.17f}')
print(f'Test recall: {recall:.17f}')
print(f'Test F1 score: {f1:.17f}')
