# --------------------------Cifar10 Image Classification Workshop--------------------#

#Import libraries
from __future__ import print_function, division
import keras
from keras.datasets import cifar10
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential, load_model
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Conv2D, MaxPooling2D
import numpy as np
import matplotlib.pyplot as plt

#----------------------------------Define Constants----------------------------------#

batch_size = 32
num_classes = 10
epochs = 3
data_augmentation = False
num_predictions = 20
train_new = False
model_name = 'keras_cifar10_trained_model.h5'

#-------------------------------Load and split the data------------------------------#

# The data, split between train and test sets:
(x_train, y_train), (x_test, y_test) = cifar10.load_data()
print('x_train shape:', x_train.shape)
print(x_train.shape[0], 'train samples')
print(x_test.shape[0], 'test samples')

# Convert class vectors to binary class matrices
y_train = keras.utils.to_categorical(y_train, num_classes)
y_test = keras.utils.to_categorical(y_test, num_classes)


#------------------------------------Create Model-----------------------------------#

model = Sequential()

# Add Convolutional Layer
model.add(Conv2D(32, # the number of output filters
                 (3, 3), #the height and width of the 2D convolution window
                 padding='same', #one of "valid" or "same"
                 input_shape=x_train.shape[1:]) # input shape
                )
model.add(Activation('relu')) # Add activation function - relu: rectifier linear unit
model.add(Conv2D(32, (3, 3)))
model.add(Activation('relu'))
# Add Poolling Layer - Max Pooling with window size 2x2
model.add(MaxPooling2D(pool_size=(2, 2)))
# Dropout Layer -  Used for regularization 
model.add(Dropout(0.25))

model.add(Conv2D(64,(3, 3), padding='same'))
model.add(Activation('relu'))
model.add(Conv2D(64, (3, 3)))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

# Flatten the CNN output
model.add(Flatten())

# Add Fully Connected Layers
model.add(Dense(512))
model.add(Activation('relu'))
model.add(Dropout(0.5))
model.add(Dense(num_classes))
model.add(Activation('softmax'))


# initiate RMSprop optimizer
opt = keras.optimizers.rmsprop(lr=0.0001, decay=1e-6)

# Compile the model using RMSprop
model.compile(loss='categorical_crossentropy',
              optimizer=opt,
              metrics=['accuracy'])

# Save the model summary
with open('summary.txt','w') as fh:
    # Pass the file handle in as a lambda function to make it callable
        model.summary(print_fn=lambda x: fh.write(x + '\n'))
        
# Data Normalization
x_train = x_train.astype('float32')
x_test = x_test.astype('float32')
x_train /= 255
x_test /= 255

#----------------------------------Train the Model----------------------------------#
if train_new:
    if not data_augmentation:
        print('Not using data augmentation.')
        # Start model training
        history = model.fit(x_train, # Images
                  y_train, # Ground truth
                  batch_size=batch_size, # Number of samples per gradient update
                  epochs=epochs, # Number of epochs to train the model
                  validation_data=(x_test, y_test), # Data used for evaluation purposes
                  verbose=1, # Verbosity mode. 0 = silent, 1 = progress bar, 2 = one line per epoch
                  shuffle=True # Whether to shuffle the training data before each epoch
                  )
    else:
        print('Using real-time data augmentation.')
        # This will do preprocessing and realtime data augmentation:
        #data augmentation
        datagen = ImageDataGenerator(
            rotation_range=15,
            width_shift_range=0.1,
            height_shift_range=0.1,
            horizontal_flip=True,
            )
     
        # Fit the model on the batches generated by datagen.flow().
        history = model.fit_generator(datagen.flow(x_train, y_train, batch_size=batch_size),
                        steps_per_epoch=int(x_train.shape[0]/batch_size),epochs=2,
                        verbose=1,validation_data=(x_test,y_test))
    # Save model and weights
    model.save(model_name)
    print('Saved trained model at %s ' % model_name)
    
    # Plot loss vs epochs
    fig1 = plt.figure(1)
    plt.plot(history.history['loss'], label = 'Training Loss')
    plt.legend()
    plt.show()
    plt.savefig('Accuracy_'+str(epochs)+'_'+str(data_augmentation)+'.png')
else:
    model = load_model(model_name)

#----------------------------Validate and visualize the results--------------------#

# Score trained model.
scores = model.evaluate(x_test, y_test, verbose=1)
print('Test loss:', scores[0])
print('Test accuracy:', scores[1])


def show_imgs(X):
    fig = plt.figure(2)
    
    k = 0
    for i in range(0,4):
        for j in range(0,4):
            plt.subplot2grid((4,4),(i,j))
            plt.imshow((X[k]))
            k = k+1
    # show the plot
    plt.show()
    fig.suptitle(str([labels[x] for x in indices]))
 

# Cifar10 Labels:
labels =  ['airplane','automobile','bird','cat','deer','dog','frog','horse','ship','truck']
indices = np.argmax(model.predict(x_test[:16]),1)
show_imgs(x_test[:16])
print([labels[x] for x in indices])
