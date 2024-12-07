import pandas as pd
import numpy as np
from google.colab import drive
from sklearn.preprocessing import LabelEncoder,StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, SimpleRNN
from tensorflow.keras.optimizers import Adam
from sklearn.metrics import recall_score, f1_score

df = pd.read_csv('/content/reddit_data.csv')
le = LabelEncoder()
df['username'] = le.fit_transform(df['username'])
df['subreddit'] = le.fit_transform(df['subreddit'])
scaler = StandardScaler()
cols_to_scale = ['username', 'subreddit', 'num_interactions','avrg']
scaler.fit(df[cols_to_scale])
df[cols_to_scale] = scaler.transform(df[cols_to_scale])
X = df[['username', 'subreddit', 'num_interactions','avrg']].to_numpy()
y = df['binary_value'].to_numpy()



from sklearn.model_selection import train_test_split
train_X, test_X, train_y, test_y = train_test_split(X, y, test_size=0.2, random_state=42)

train_X = train_X.reshape(train_X.shape[0], train_X.shape[1], 1)
test_X = test_X.reshape(test_X.shape[0], test_X.shape[1], 1)

model = Sequential()
model.add(SimpleRNN(250, input_shape=(X.shape[1], 1), activation='relu', return_sequences=True))
model.add(Dropout(0.4))
model.add(SimpleRNN(180, activation='relu'))
model.add(Dropout(0.4))
model.add(Dense(120, activation='relu'))
model.add(Dropout(0.4))
model.add(Dense(1, activation='sigmoid'))
model.summary()
opt = Adam(learning_rate=0.001)
model.compile(loss='binary_crossentropy', optimizer=opt, metrics=['accuracy'])


history = model.fit(train_X, train_y, epochs=400, batch_size=400, verbose=1, validation_data=(test_X, test_y))
train_loss, train_accuracy = model.evaluate(train_X, train_y, verbose=1)
print(f'Train loss: {train_loss}')
print(f'Train accuracy: {train_accuracy}')
test_loss, test_accuracy = model.evaluate(test_X, test_y, verbose=1)
print(f'Test loss: {test_loss}')
print(f'Test accuracy: {test_accuracy}')

import matplotlib.pyplot as plt
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])  
plt.title('Model accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['Train', 'test'], loc='upper left')
plt.show()

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Model loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['Train', 'Test'], loc='upper left')
plt.show()

y_pred = model.predict(test_X)
y_pred_binary = (y_pred > 0.5).astype(int)
print('True values: ', test_y)
print('Predicted values: ', y_pred_binary)
print('--------------------------------')
print("Test-Accuracy:", np.mean(history.history["accuracy"]))
print("Test-loss:", np.mean(history.history["loss"]))
print('--------------------------------')
print("Validation-Accuracy:", np.mean(history.history["val_accuracy"]))
print("Validation-Loss:", np.mean(history.history["val_loss"]))


