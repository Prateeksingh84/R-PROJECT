# -*- coding: utf-8 -*-
"""CANCER CELL DETECTION.py

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1vDmCqwWzjwK8LBh4YijG3n9cezrVk9oe
"""

!pip install tensorflow==2.9.1

# import system libs
import os
import time
import shutil
import pathlib
import itertools
from PIL import Image

# import data handling tools
import cv2
import numpy as np
import pandas as pd
import seaborn as sns
sns.set_style('darkgrid')
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report

# import Deep learning Libraries
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam, Adamax
from tensorflow.keras.metrics import categorical_crossentropy
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Activation, Dropout, Flatten, Dense, BatchNormalization
from tensorflow.keras import regularizers

# Ignore Warnings
import warnings
warnings.filterwarnings("ignore")

print ('modules loaded')

# Generate data paths with labels
# Check if the original path exists
import os

original_data_dir = ''
if not os.path.exists(original_data_dir):
    # If not, try an alternative path
    # (this assumes the dataset is in '../input/blood-cells')
    data_dir = '/content/blood cancer cell dataset'
else:
    data_dir = original_data_dir

filepaths = []
labels = []

folds = os.listdir(data_dir)
for fold in folds:
    foldpath = os.path.join(data_dir, fold)
    # Check if foldpath is a directory before proceeding
    if os.path.isdir(foldpath):
        filelist = os.listdir(foldpath)
        if fold in ['ig', 'neutrophil']:
            continue
        for file in filelist:
            fpath = os.path.join(foldpath, file)

            filepaths.append(fpath)
            labels.append(fold)

# Concatenate data paths with labels into one dataframe
Fseries = pd.Series(filepaths, name= 'filepaths')
Lseries = pd.Series(labels, name='labels')
df = pd.concat([Fseries, Lseries], axis= 1)

df

# train dataframe
train_df, dummy_df = train_test_split(df,  train_size= 0.8, shuffle= True, random_state= 123)

# valid and test dataframe
valid_df, test_df = train_test_split(dummy_df,  train_size= 0.6, shuffle= True, random_state= 123)

# crobed image size
batch_size = 16
img_size = (224, 224)
channels = 3
img_shape = (img_size[0], img_size[1], channels)

tr_gen = ImageDataGenerator()
ts_gen = ImageDataGenerator()

train_gen = tr_gen.flow_from_dataframe( train_df, x_col= 'filepaths', y_col= 'labels', target_size= img_size, class_mode= 'categorical',
                                    color_mode= 'rgb', shuffle= True, batch_size= batch_size)

valid_gen = ts_gen.flow_from_dataframe( valid_df, x_col= 'filepaths', y_col= 'labels', target_size= img_size, class_mode= 'categorical',
                                    color_mode= 'rgb', shuffle= True, batch_size= batch_size)

test_gen = ts_gen.flow_from_dataframe( test_df, x_col= 'filepaths', y_col= 'labels', target_size= img_size, class_mode= 'categorical',
                                    color_mode= 'rgb', shuffle= False, batch_size= batch_size)


# Check if train_gen has any samples
if train_gen.samples > 0:
    g_dict = train_gen.class_indices      # defines dictionary {'class': index}
    classes = list(g_dict.keys())       # defines list of dictionary's kays (classes), classes names : string
    images, labels = next(train_gen)      # get a batch size samples from the generator

    plt.figure(figsize= (20, 20))

    num_images_to_display = min(16, len(images))  # Display up to 16 images or the number of images available, whichever is smaller

    for i in range(num_images_to_display):
        plt.subplot(4, 4, i + 1)
        image = images[i] / 255.0     # scales data to range (0 - 1)
        plt.imshow(image)
        index = np.argmax(labels[i])  # get image index

        # Check if index is within bounds of classes before accessing
        if 0 <= index < len(classes):
            class_name = classes[index]   # get class of image
            plt.title(class_name, color= 'blue', fontsize= 12)
        else:
            plt.title("Unknown Class", color='red', fontsize=12)  # Handle case where index is out of bounds

        plt.axis('off')
    plt.show()
else:
    print("train_gen has no samples. Check filepaths and dataframe.")

#Verify Dataframe
print(len(train_df))
print(train_df.head())
print(train_df['filepaths'].iloc[0])
#Verify train_gen setup
print(train_gen.samples)
if train_gen.samples > 0:  # Check if train_gen has any samples
    print(train_gen.filenames[0])
else:
    print("train_gen has no samples. Check filepaths and dataframe.")

# Check if images are loaded in your IPython-input-5-fc389b07c2db script
# Create a new list to store the labels
updated_labels = []
folds = os.listdir(data_dir)
for fold in folds:
    foldpath = os.path.join(data_dir, fold)
    # Check if foldpath is a directory before proceeding
    if os.path.isdir(foldpath):
        filelist = os.listdir(foldpath)
        if fold in ['ig', 'neutrophil']:
            continue
        for file in filelist:
            fpath = os.path.join(foldpath, file)
            print("Loading image:", fpath) # Check if the loaded image paths are correct
            filepaths.append(fpath)
            # Append to the new list
            updated_labels.append(fold)

train_df['filepaths'] = train_df['filepaths'].astype(str)

#Check train_df content
print(train_df.head())  # Print the first few rows of train_df to inspect the data
print(train_df['filepaths'].dtype)  # Check data type of 'filepaths' column

#Check train_gen setup
print(train_gen.samples)  # Number of samples in the generator
print(train_gen.filepaths[:5])  # Print the first 5 filepaths

#Check if images exist at those locations
import os
for filepath in train_gen.filepaths[:5]:
    if not os.path.exists(filepath):
        print(f"Image not found: {filepath}")
# If images are not found, adjust the filepaths in your DataFrame or ensure the files exist in those locations.



# If everything looks correct and you still get the error, consider adding these lines:
# Reset generator
train_gen.reset()
images, labels = next(train_gen)

# Try to get data if available
try:
    images, labels = next(train_gen)
except StopIteration:
    print("The generator is empty. Check filepaths and dataframe.")
    images, labels = None, None

g_dict = train_gen.class_indices      # defines dictionary {'class': index}
classes = list(g_dict.keys())       # defines list of dictionary's kays (classes), classes names : string
images, labels = next(train_gen)      # get a batch size samples from the generator

plt.figure(figsize= (20, 20))

for i in range(16):
    plt.subplot(4, 4, i + 1)
    image = images[i] / 100       # scales data to range (0 - 100)
    plt.imshow(image)
    index = np.argmax(labels[i])  # get image index
    class_name = classes[index]   # get class of image
    plt.title(class_name, color= 'blue', fontsize= 12)
    plt.axis('off')
plt.show()

# Create Model Structure
img_size = (224, 224)
channels = 3
img_shape = (img_size[0], img_size[1], channels)
class_count = len(list(train_gen.class_indices.keys())) # to define number of classes in dense layer

# create pre-trained model (you can built on pretrained model such as :  efficientnet, VGG , Resnet )
# we will use efficientnetb3 from EfficientNet family.
base_model = tf.keras.applications.efficientnet.EfficientNetB3(include_top= False, weights= "imagenet", input_shape= img_shape, pooling= 'max')
# base_model.trainable = False

model = Sequential([
    base_model,
    BatchNormalization(axis= -1, momentum= 0.99, epsilon= 0.001),
    Dense(256, kernel_regularizer= regularizers.l2(l= 0.016), activity_regularizer= regularizers.l1(0.006),
                bias_regularizer= regularizers.l1(0.006), activation= 'relu'),
    Dropout(rate= 0.45, seed= 123),
    Dense(class_count, activation= 'softmax')
])
model.compile(Adamax(learning_rate= 0.001), loss= 'categorical_crossentropy', metrics= ['accuracy'])

model.summary()

epochs = 10   # number of all epochs in training

history = model.fit(x= train_gen, epochs= epochs, verbose= 1, validation_data= valid_gen,
                    validation_steps= None, shuffle= False)

# Define needed variables
tr_acc = history.history['accuracy']
tr_loss = history.history['loss']
val_acc = history.history['val_accuracy']
val_loss = history.history['val_loss']
index_loss = np.argmin(val_loss)
val_lowest = val_loss[index_loss]
index_acc = np.argmax(val_acc)
acc_highest = val_acc[index_acc]
Epochs = [i+1 for i in range(len(tr_acc))]
loss_label = f'best epoch= {str(index_loss + 1)}'
acc_label = f'best epoch= {str(index_acc + 1)}'

# Plot training history
plt.figure(figsize= (20, 8))
plt.style.use('fivethirtyeight')

plt.subplot(1, 2, 1)
plt.plot(Epochs, tr_loss, 'r', label= 'Training loss')
plt.plot(Epochs, val_loss, 'g', label= 'Validation loss')
plt.scatter(index_loss + 1, val_lowest, s= 150, c= 'blue', label= loss_label)
plt.title('Training and Validation Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(Epochs, tr_acc, 'r', label= 'Training Accuracy')
plt.plot(Epochs, val_acc, 'g', label= 'Validation Accuracy')
plt.scatter(index_acc + 1 , acc_highest, s= 150, c= 'blue', label= acc_label)
plt.title('Training and Validation Accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()

plt.tight_layout
plt.show()

from tensorflow.keras.models import load_model
model.save('Bloods.h5')

ts_length = len(test_df)
test_batch_size = max(sorted([ts_length // n for n in range(1, ts_length + 1) if ts_length%n == 0 and ts_length/n <= 80]))
test_steps = ts_length // test_batch_size

train_score = model.evaluate(train_gen, steps= test_steps, verbose= 1)
valid_score = model.evaluate(valid_gen, steps= test_steps, verbose= 1)
test_score = model.evaluate(test_gen, steps= test_steps, verbose= 1)

print("Train Loss: ", train_score[0])
print("Train Accuracy: ", train_score[1])
print('-' * 20)
print("Validation Loss: ", valid_score[0])
print("Validation Accuracy: ", valid_score[1])
print('-' * 20)
print("Test Loss: ", test_score[0])
print("Test Accuracy: ", test_score[1])

preds = model.predict_generator(test_gen)
y_pred = np.argmax(preds, axis=1)

g_dict = test_gen.class_indices
classes = list(g_dict.keys())

# Confusion matrix
cm = confusion_matrix(test_gen.classes, y_pred)

plt.figure(figsize= (10, 10))
plt.imshow(cm, interpolation= 'nearest', cmap= plt.cm.Blues)
plt.title('Confusion Matrix')
plt.colorbar()

tick_marks = np.arange(len(classes))
plt.xticks(tick_marks, classes, rotation= 45)
plt.yticks(tick_marks, classes)


thresh = cm.max() / 2.
for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
    plt.text(j, i, cm[i, j], horizontalalignment= 'center', color= 'white' if cm[i, j] > thresh else 'black')
    plt.tight_layout()
plt.ylabel('True Label')
plt.xlabel('Predicted Label')

plt.show()

# Classification report
print(classification_report(test_gen.classes, y_pred, target_names= classes))

# Assuming the model was saved as an HDF5 file named 'Bloods.h5'
# in the '/content/blood cancer cell dataset' directory

loaded_model = tf.keras.models.load_model('Bloods.h5', compile=False)

# If the model was saved using model.save('path/to/your/model'),
# you should load it like this:
# loaded_model = tf.keras.models.load_model('/content/blood cancer cell dataset/model', compile=False)

loaded_model.compile(Adamax(learning_rate= 0.001), loss= 'categorical_crossentropy', metrics= ['accuracy'])

image_path = '/content/blood cancer cell dataset/eosinophil/EO_15801.jpg'
image = Image.open(image_path)
# Preprocess the image
img = image.resize((224, 224))
img_array = tf.keras.preprocessing.image.img_to_array(img)
img_array = tf.expand_dims(img_array, 0)
# Make predictions
predictions = loaded_model.predict(img_array)
class_labels = ['Basophil', 'Eosinophil', 'Erythroblast', 'IG', 'lymphocyte', 'Monocyte', 'Neutrophil', 'Platelet']
score = tf.nn.softmax(predictions[0])
print(f"{class_labels[tf.argmax(score)]}")

converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

print("model converted")

# Save the model.
with open('Bloods.tflite', 'wb') as f:
    f.write(tflite_model)