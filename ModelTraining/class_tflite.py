from numpy import random
import tensorflow as tf

from tensorflow import keras
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math

from tensorflow.keras.models import Sequential
from keras.layers import Input, Dense, Dropout
from keras.wrappers.scikit_learn import KerasClassifier
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

# Set seed for experiment reproducibility
seed = 2
tf.random.set_seed(seed)
tf.compat.v1.set_random_seed(seed)
random.seed(seed)
np.random.seed(seed)
import os
MODELS_DIR = 'models/'
if not os.path.exists(MODELS_DIR):
    os.mkdir(MODELS_DIR)
MODEL_TF = MODELS_DIR + 'model'
MODEL_NO_QUANT_TFLITE = MODELS_DIR + 'model_no_quant.tflite'
MODEL_TFLITE = MODELS_DIR + 'model.tflite'
MODEL_TFLITE_MICRO = MODELS_DIR + 'model.cc'

features = pd.read_csv(os.path.join("Features_2sec.csv"), index_col=0)

def select_three_classes(df, class1, class2, class3):
    df = df[(df['Label'] == class1)|(df['Label'] == class2)|(df['Label'] == class3)]
    df['Label'] = df['Label'].replace(class1,0) 
    df['Label'] = df['Label'].replace(class2,1)
    df['Label'] = df['Label'].replace(class3,2)
    return df
    
def select_four_classes(df, class_to_drop):
    df = df[df['Label']!=class_to_drop]
    new_label = 0
    for label in df['Label'].unique():
        df['Label'] = df['Label'].replace(label, new_label)
        new_label += 1
    return df

features.dropna(inplace=True)
features['Label'] = features['Label'].map(int)
#features = select_three_classes(features,1,2,3)
features = select_four_classes(features,4)
features = features.sample(frac=1)
features = features.to_numpy()

y_values = keras.utils.to_categorical(features[:,0])
x_values = features[:,1:].astype('float32')

TRAIN_SPLIT =  int(0.6 * features.shape[0])
TEST_SPLIT = int(0.2 * features.shape[0] + TRAIN_SPLIT)

x_train, x_test, x_validate = np.split(x_values, [TRAIN_SPLIT, TEST_SPLIT])
y_train, y_test, y_validate = np.split(y_values, [TRAIN_SPLIT, TEST_SPLIT])

assert(x_train.shape[0] + x_test.shape[0] + x_validate.shape[0] == features.shape[0])

model = Sequential()
model.add(Dense(30, input_shape = (x_train.shape[1],), activation='relu'))
#model.add(Dropout(0.2))
#model.add(Dense(15, activation='relu'))
#model.add(Dropout(0.2))
#model.add(Dense(10, activation='relu'))
#model.add(Dropout(0.2))
model.add(Dense(10,activation='relu'))
#model.add(Dropout(0.1))
#model.add(Dense(5,activation='relu'))
#model.add(Dropout(0.1))
model.add(Dense(4,activation='softmax'))


optimizer = tf.keras.optimizers.Adam(0.001)
model.compile(optimizer=optimizer, loss='categorical_crossentropy', metrics=['accuracy'])
history_1 = model.fit(x_train, y_train, epochs=400, batch_size=64,
                        validation_data=(x_validate, y_validate))

test_results = model.evaluate(x_test, y_test, verbose=1)
print(f'Test results - Loss: {test_results[0]} - Accuracy: {test_results[1]*100}%')

model.save(MODEL_TF)

# Convert the model to the TensorFlow Lite format without quantization
converter = tf.lite.TFLiteConverter.from_saved_model(MODEL_TF)
model_no_quant_tflite = converter.convert()

# Save the model to disk
open(MODEL_NO_QUANT_TFLITE, "wb").write(model_no_quant_tflite)
#print(model.predict(x_test))
# Convert to a C source file, i.e, a TensorFlow Lite for Microcontrollers model
#xxd -i {MODEL_NO_QUANT_TFLITE} > {MODEL_TFLITE_MICRO}
# Update variable names
#REPLACE_TEXT = MODEL_TFLITE.replace('/', '_').replace('.', '_')
#sed -i 's/'{REPLACE_TEXT}'/g_model/g' {MODEL_TFLITE_MICRO}
