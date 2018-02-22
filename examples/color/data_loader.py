
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import matplotlib.pyplot as plt
import math
import cairo

WIDTH = 32
HEIGHT = 32
CHANNELS = 3

class DataGenerator:

    def __init__(self):
        self.size = 100
        self.ratio = 0.8
        self.generate();

    def generate_image(self):
        ''' Randomly generates an image with random boxes '''
        data = np.zeros( (HEIGHT,WIDTH, 4), dtype=np.uint8 ) 
        surface = cairo.ImageSurface.create_for_data( data, cairo.FORMAT_ARGB32, WIDTH, HEIGHT )
        ctx = cairo.Context( surface )

        ctx.scale (WIDTH, HEIGHT) # Normalizing the canvas
        ctx.set_source_rgb(0, 0, 0)
        ctx.rectangle (0, 0, 1, 1)  # Rectangle(x0, y0, x1, y1) 
        ctx.fill()

        ctx.set_source_rgb(0, 0, 1)
        for _ in range(50):
            r = np.random.rand(2)
            ctx.translate (r[0], r[1])      # Changing the current transformation matrix
            ctx.rectangle (0, 0, 0.1, 0.1)  # Rectangle(x0, y0, x1, y1)
            ctx.fill()
            ctx.translate (-r[0], -r[1])    # Changing the current transformation matrix

        img = data[:,:,0:3]
        return img;

    def whiten_data(self, features):
        """ whiten our data - zero mean and unit standard deviation """
        features = (features - np.mean(features, axis=0)) / np.std(features, axis=0)
        return features

    def generate(self):
        ''' Generates a randomly generated dataset '''
        img = self.generate_image()
        self.data = np.stack( (img, self.generate_image()))
        for _ in range(self.size - 2):
            img = self.generate_image()
            self.data = np.concatenate( (self.data, img[None,:]), axis=0)

        # Generate truth data
        threshold = [200, 0, 0]
        self.label = np.all(np.greater_equal(self.data, threshold), axis=3) * 1.0;
        self.label = np.reshape(self.label, (self.size, WIDTH, HEIGHT, 1))
        self.label = np.concatenate( (self.label, 1 - self.label), axis=3)

        # Reshape 
        self.data = np.reshape(self.data, (self.size, WIDTH * HEIGHT * CHANNELS))
        self.label = np.reshape(self.label, (self.size, WIDTH * HEIGHT * 2))

        print(self.label.shape)  

        # Setup data
        self.data = self.whiten_data(self.data)

        # Split data into test/training sets
        index = int(self.ratio * len(self.data)) # Split index
        self.x_train = self.data[0:index, :]
        self.y_train = self.label[0:index]
        self.x_test = self.data[index:,:]
        self.y_test = self.label[index:]

    def show(self, index):
        ''' Show a data slice at index'''
        img = np.reshape(self.data[index], (WIDTH, HEIGHT, CHANNELS))
        plt.imshow(img)
        plt.show()

    def show_label(self, index):
        ''' Show a truth data slice at index'''
        img = np.reshape(self.label[index], (WIDTH, HEIGHT, 2))
        plt.imshow(img[:,:,0], cmap='gray')
        plt.show()  
        plt.imshow(img[:,:,1], cmap='gray')
        plt.show()  

    def print(self):
        print("Data Split: ", self.ratio)
        print("Train => x:", self.x_train.shape, " y:", self.y_train.shape)
        print("Test  => x:", self.x_test.shape, " y:", self.y_test.shape)

    def next_batch(self, batch_size):
        ''' Retrieves the next batch for a given batch size '''
        length = self.x_train.shape[0]
        indices = np.random.randint(0, length, batch_size) # Grab batch_size values randomly
        return [self.x_train[indices], self.y_train[indices]]

if __name__ == '__main__':
    data = DataGenerator()
    data.print()
    data.show(2)
    data.show_label(2)