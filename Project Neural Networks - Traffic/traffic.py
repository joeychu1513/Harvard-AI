import cv2
import numpy as np
import os
import sys
import tensorflow as tf

from sklearn.model_selection import train_test_split

EPOCHS = 128
IMG_WIDTH = 30
IMG_HEIGHT = 30
NUM_CATEGORIES = 43
TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) not in [2, 3]:
        sys.exit("Usage: python traffic.py data_directory [model.h5]")

    # Get image arrays and labels for all image files
    images, labels = load_data(sys.argv[1])

    # Split data into training and testing sets
    labels = tf.keras.utils.to_categorical(labels) # change to binary format
    x_train, x_test, y_train, y_test = train_test_split(
        np.array(images), np.array(labels), test_size=TEST_SIZE
    )

    # Get a compiled neural network
    model = get_model()

    # Fit model on training data
    model.fit(x_train, y_train, epochs=EPOCHS)

    # Evaluate neural network performance
    model.evaluate(x_test,  y_test, verbose=2)

    # Save model to file
    if len(sys.argv) == 3:
        filename = sys.argv[2]
        model.save(filename)
        print(f"Model saved to {filename}.")


def load_data(data_dir):
    """
    Load image data from directory `data_dir`.

    Assume `data_dir` has one directory named after each category, numbered
    0 through NUM_CATEGORIES - 1. Inside each category directory will be some
    number of image files.

    Return tuple `(images, labels)`. `images` should be a list of all
    of the images in the data directory, where each image is formatted as a
    numpy ndarray with dimensions IMG_WIDTH x IMG_HEIGHT x 3. `labels` should
    be a list of integer labels, representing the categories for each of the
    corresponding `images`.
    """
    
    images = []
    images_path = []
    labels = []

    # loop every file
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            file_path = os.path.join(root, file)
            separator = os.sep
            label = file_path.split(separator)[1]

            # add to images_path, label
            images_path.append(file_path)
            labels.append(label)

    # check for images, resize if needed, convert to np format and add to images
    for image_path in images_path:
        img = cv2.imread(image_path) # convert to numpy.ndarray

        # confirm image fit (30, 30, 3)
        img_shape = img.shape
        img_height = img_shape[0]
        img_width = img_shape[1]
        img_channel = img_shape[2]

        if img_channel != 3: # not RGB format
            print(image_path)
            raise Exception("image channel error")
        
        if img_height != IMG_HEIGHT or img_width != IMG_WIDTH:
            img = cv2.resize(img, (IMG_HEIGHT, IMG_WIDTH)) # convert to standard size

        images.append(img)
        
    return (images, labels)


def get_model():
    """
    Returns a compiled convolutional neural network model. Assume that the
    `input_shape` of the first layer is `(IMG_WIDTH, IMG_HEIGHT, 3)`.
    The output layer should have `NUM_CATEGORIES` units, one for each category.
    """

    # Create a convolutional neural network
    model = tf.keras.models.Sequential([

        # 1st Convolutional layer. Learn 64 filters using a 3x3 kernel
        tf.keras.layers.Conv2D(
            64, (3, 3), activation="relu", input_shape=(IMG_HEIGHT, IMG_WIDTH, 3)),

        # 1st Max-pooling layer, using 2x2 pool size
        tf.keras.layers.MaxPooling2D(pool_size=(2, 2)),

        # 2nd Convolutional layer. Learn 64 filters using a 3x3 kernel
        tf.keras.layers.Conv2D(64, (3, 3), activation="relu"),

        # 2nd Max-pooling layer, using 2x2 pool size
        tf.keras.layers.MaxPooling2D(pool_size=(2, 2)),

        # # 3rd Convolutional layer. Learn 64 filters using a 3x3 kernel
        # tf.keras.layers.Conv2D(64, (3, 3), activation="relu"),

        # # 3rd Max-pooling layer, using 2x2 pool size
        # tf.keras.layers.MaxPooling2D(pool_size=(2, 2)),

        # # 4th Convolutional layer. Learn 64 filters using a 3x3 kernel
        # tf.keras.layers.Conv2D(64, (3, 3), activation="relu"),

        # # 4th Max-pooling layer, using 2x2 pool size
        # tf.keras.layers.MaxPooling2D(pool_size=(2, 2)),

        # Flatten units
        tf.keras.layers.Flatten(),

        # Add 1st hidden layer with dropout
        tf.keras.layers.Dense(512, activation="relu"),
        tf.keras.layers.Dropout(0.2),

        # Add 2nd hidden layer with dropout
        tf.keras.layers.Dense(384, activation="relu"),
        tf.keras.layers.Dropout(0.2),

        # Add 3rd hidden layer with dropout
        tf.keras.layers.Dense(256, activation="relu"),
        tf.keras.layers.Dropout(0.2),

        # Add 4th hidden layer with dropout
        tf.keras.layers.Dense(128, activation="relu"),
        tf.keras.layers.Dropout(0.2),

        # # Add 5th hidden layer with dropout
        # tf.keras.layers.Dense(128, activation="relu"),
        # tf.keras.layers.Dropout(0.2),

        # Add an output layer with output units for all 43 output
        tf.keras.layers.Dense(NUM_CATEGORIES, activation="softmax")
    ])

    # Train neural network
    model.compile(
        optimizer="adam",
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )

    return model


if __name__ == "__main__":
    main()
