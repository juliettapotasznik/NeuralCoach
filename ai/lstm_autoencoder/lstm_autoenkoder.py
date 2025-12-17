import numpy as np
import pandas as pd
from tensorflow.keras.utils import Sequence
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, RepeatVector, TimeDistributed
import os
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from tensorflow.keras.callbacks import EarlyStopping

class ExerciseSequence(Sequence):
    def __init__(self, file_paths, mean, std, batch_size=16, seq_len=30, step=5):
        self.file_paths = file_paths
        self.mean = mean
        self.std = std
        self.batch_size = batch_size
        self.seq_len = seq_len
        self.step = step

    def __len__(self):
        return int(np.ceil(len(self.file_paths) / self.batch_size))

    def __getitem__(self, idx):
        batch_paths = self.file_paths[idx * self.batch_size:(idx + 1) * self.batch_size]
        batch_windows = []

        for file_path in batch_paths:
            df = pd.read_csv(file_path).drop(columns=["frame_id"])

            if df.isnull().values.any():
                continue

            arr = df.values
    
            #normalizacja danych wzgledem joint_0
            joint_0_cols = [col for col in df.columns if 'joint_0' in col]
            joint_0 = df[joint_0_cols].values
            joint_0_repeated = np.repeat(joint_0, repeats=57//3, axis=1)
            centered = arr - joint_0_repeated
            centered = (centered - self.mean) / self.std

            #standaryzacja dlugosci sekwencji
            for j in range(0, len(centered) - self.seq_len + 1, self.step):
                window = centered[j:j + self.seq_len]
                batch_windows.append(window)

        if len(batch_windows) == 0:
            return np.zeros((0, self.seq_len, 57)), np.zeros((0, self.seq_len, 57))

        batch_windows = np.array(batch_windows)
        return batch_windows, batch_windows  
    
csv_files = [f'../dataset_csv/{file}' for file in os.listdir('../dataset_csv') if file.endswith('.csv')]

#enkoder
autoencoder = Sequential()
autoencoder.add(LSTM(128, activation='tanh', return_sequences=True, input_shape=(30, 57)))
autoencoder.add(LSTM(64, activation='tanh', return_sequences=True))
autoencoder.add(LSTM(32, activation='tanh'))

#dekoder
autoencoder.add(RepeatVector(30))
autoencoder.add(LSTM(32, activation='tanh', return_sequences=True))
autoencoder.add(LSTM(64, activation='tanh', return_sequences=True))
autoencoder.add(LSTM(128, activation='tanh', return_sequences=True))
autoencoder.add(TimeDistributed(Dense(57)))

autoencoder.compile(optimizer='adam', loss='mean_squared_error')
autoencoder.summary()

train_files, val_files = train_test_split(csv_files, test_size=0.3, random_state=42)

all_data = []
for file_path in train_files:
    df = pd.read_csv(file_path).drop(columns=["frame_id"])
    arr = df.values
    joint_0_cols = [col for col in df.columns if 'joint_0' in col]
    joint_0 = df[joint_0_cols].values
    joint_0_repeated = np.repeat(joint_0, repeats=57//3, axis=1)
    centered = arr - joint_0_repeated
    all_data.append(centered)
all_data = np.concatenate(all_data, axis=0)
mean = np.mean(all_data, axis=0)
std = np.std(all_data, axis=0) + 1e-6

np.save("mean.npy", mean)
np.save("std.npy", std)


train_generator = ExerciseSequence(train_files, mean, std)
val_generator = ExerciseSequence(val_files, mean, std)

early_stop = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)
history = autoencoder.fit(
    train_generator,
    validation_data=val_generator,
    epochs=50,
    callbacks=[early_stop]
)

plt.plot(history.history['loss'], label='Train loss')
plt.plot(history.history.get('val_loss', []), label='Val loss')
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.legend()
plt.title("LSTM Autoencoder training")
plt.show()

autoencoder.save_weights("lstm_weights.weights.h5")
with open("lstm_architecture.json", "w") as f:
    f.write(autoencoder.to_json())

sample, _ = train_generator[0]
reconstructed = autoencoder.predict(sample)
mse = np.mean((sample - reconstructed)**2)
print(f"Average reconstruction MSE: {mse:.5f}")


