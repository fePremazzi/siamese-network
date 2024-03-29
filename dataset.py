from __future__ import generators, division, absolute_import, with_statement, print_function, unicode_literals

import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.datasets import mnist
import os
import cv2
import sys
import h5py
import pandas as pd
import matplotlib.pyplot as plt
import time
import os
from tqdm import tqdm_notebook
from load_data import *

class Dataset(object):
	images_train = np.array([])
	images_test = np.array([])
	labels_train = np.array([])
	labels_test = np.array([])
	unique_train_label = np.array([])
	map_train_label_indices = dict()

	def _get_siamese_similar_pair(self):
		label =np.random.choice(self.unique_train_label)
		l, r = np.random.choice(self.map_train_label_indices[label], 2, replace=False)
		return l, r, 1

	def _get_siamese_dissimilar_pair(self):
		label_l, label_r = np.random.choice(self.unique_train_label, 2, replace=False)
		l = np.random.choice(self.map_train_label_indices[label_l])
		r = np.random.choice(self.map_train_label_indices[label_r])
		return l, r, 0

	def _get_siamese_pair(self):
		if np.random.random() < 0.5:
			return self._get_siamese_similar_pair()
		else:
			return self._get_siamese_dissimilar_pair()

	def get_siamese_batch(self, n):
		idxs_left, idxs_right, labels = [], [], []
		for _ in range(n):
			l, r, x = self._get_siamese_pair()
			idxs_left.append(l)
			idxs_right.append(r)
			labels.append(x)
		return self.images_train[idxs_left,:], self.images_train[idxs_right, :], np.expand_dims(labels, axis=1)

class MNISTDataset(Dataset):
	def __init__(self):
	

		data_path = os.path.join('dataset/omniglot')
		train_folder = os.path.join(data_path,'images_train')
		valpath = os.path.join(data_path,'images_test')
		
		with open(os.path.join(data_path, "pickle/train.pickle"), "rb") as f:
			(X, classes) = pickle.load(f)

		with open(os.path.join(data_path, "pickle/val.pickle"), "rb") as f:
			(Xval, val_classes) = pickle.load(f)
			
		print("Training alphabets: \n")
		print(list(classes.keys()))
		print("Validation alphabets:", end="\n\n")
		print(list(val_classes.keys()))
		
		x_train = []
		y_train = []
		x_test = []
		y_test = []

		target = 0
		for classe in X:    
			for img in classe:
				x_train.append(255 - img)
				y_train.append(target)
			target += 1

		target = 0
		for classe in Xval:    
			for img in classe:
				x_test.append(255 - img)
				y_test.append(target)
			target += 1    
			
		x_imgs = np.asarray([np.asarray(x_train), np.asarray(x_test)])
		y_lbls = np.asarray([np.asarray(y_train), np.asarray(y_test)])
	
	
	
		print("===Loading ひらがな　Dataset===")
		#(self.images_train, self.labels_train), (self.images_test, self.labels_test) = mnist.load_data()
		self.images_train = np.expand_dims(x_train, axis=3) / 255.0
		self.images_test = np.expand_dims(x_test, axis=3) / 255.0
		self.labels_train = np.expand_dims(y_train, axis=1)
		self.unique_train_label = np.unique(self.labels_train)
		self.map_train_label_indices = {label: np.flatnonzero(self.labels_train == label) for label in self.unique_train_label}
		print("Images train :", self.images_train.shape)
		print("Labels train :", self.labels_train.shape)
		print("Images test  :", self.images_test.shape)
		print("Labels test  :", self.labels_test.shape)
		print("Unique label :", self.unique_train_label)
		# print("Map label indices:", self.map_train_label_indices)
		
if __name__ == "__main__":
	# Test if it can load the dataset properly or not. use the train.py to run the training
	a = MNISTDataset()
	batch_size = 4
	ls, rs, xs = a.get_siamese_batch(batch_size)
	f, axarr = plt.subplots(batch_size, 2)
	for idx, (l, r, x) in enumerate(zip(ls, rs, xs)):
		print("Row", idx, "Label:", "similar" if x else "dissimilar")
		print("max:", np.squeeze(l, axis=2).max())
		axarr[idx, 0].imshow(np.squeeze(l, axis=2))
		axarr[idx, 1].imshow(np.squeeze(r, axis=2))
	plt.show()