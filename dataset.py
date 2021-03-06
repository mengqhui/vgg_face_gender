import numpy as np
from scipy import misc
import tensorflow as tf
import cv2

wiki_Path = './wiki_crop/lfw_wiki_imdb_temp.txt'

class Dataset:
	def __init__(self, data_path):
		# Load training images (path) and labels
		with open(data_path) as f:
			lines = f.readlines()
			self.train_image = []
			self.train_label = []
			self.test_image = []
			self.test_label = []
			for l in lines:
				items = l.split()
				if(items[0].split('/',1) != '00'):
					self.train_image.append('./wiki_crop/' + items[0])
					if(items[1] == '0.0'):
						self.train_label.append(1)
					else:
						self.train_label.append(2)
				else:
					self.test_image.append('./wiki_crop/' + items[0])
					if items[1] == '0.0':
						self.test_label.append(1)
					else:
						self.test_label.append(2)


		# Init params
		self.train_ptr = 0
		self.test_ptr = 0
		self.train_size = len(self.train_label)
		self.test_size = len(self.test_label)
		self.crop_size = 224
		self.n_classes = 2
	
	def next_batch(self, batch_size, phase):
		# Get next batch of image (path) and labels

		if phase == 'train':
			if self.train_ptr + batch_size < self.train_size:
				paths = self.train_image[self.train_ptr:self.train_ptr + batch_size]
				labels = self.train_label[self.train_ptr:self.train_ptr + batch_size]
				self.train_ptr += batch_size
			else:
				new_ptr = (self.train_ptr + batch_size)%self.train_size
				paths = self.train_image[self.train_ptr:] + self.train_image[:new_ptr]
				labels = self.train_label[self.train_ptr:] + self.train_label[:new_ptr]
				self.train_ptr = new_ptr
		elif phase == 'test':
			if self.test_ptr + batch_size < self.test_size:
				paths = self.test_image[self.test_ptr:self.test_ptr + batch_size]
				labels = self.test_label[self.test_ptr:self.test_ptr + batch_size]
				self.test_ptr += batch_size
			else:
				new_ptr = (self.test_ptr + batch_size)%self.test_size
				paths = self.test_image[self.test_ptr:] + self.test_image[:new_ptr]
				labels = self.test_label[self.test_ptr:] + self.test_label[:new_ptr]
				self.test_ptr = new_ptr
		else:
			return None, None
		
		images = np.ndarray([batch_size, self.crop_size, self.crop_size, 3])
		for i in xrange(len(paths)):
			img = misc.imread(paths[i])
			try:
				h, w, c = img.shape
				if h!=224 or w!=224 :
					img = misc.imresize(img, (self.crop_size, self.crop_size))
				assert c==3
				images[i] = img
			except ValueError:
				img_3channel = cv2.merge([img,img,img])
				misc.imsave(paths[i], img_3channel)
				images[i] = img_3channel

		# Expand labels
		one_hot_labels = np.zeros((batch_size, self.n_classes))
		for i in xrange(len(labels)):
			one_hot_labels[i][labels[i]-1] = 1
		
		return images, one_hot_labels
			
class Testset:
	# Load testing images (path)
	def __init__(self, data_path):
		with open(data_path) as f:
			lines = f.readlines()
			self.test_image = []
			for l in lines:
				item = l.split()[0]
				self.test_image.append('./face/'+item)

			self.test_size = len(lines)

		self.test_ptr = 0
		self.crop_size = 224

	def next_batch(self, batch_size = 1):
		if self.test_ptr + batch_size < self.test_size:
			paths = self.test_image[self.test_ptr:self.test_ptr + batch_size]
			self.test_ptr += batch_size
		else:
			new_ptr = (self.test_ptr + batch_size)%self.test_size
			paths = self.test_image[self.test_ptr:] + self.test_image[:new_ptr]
			self.test_ptr = new_ptr

		images = np.ndarray([batch_size, self.crop_size, self.crop_size, 3])
		for i in xrange(len(paths)):
			img = misc.imread(paths[i])
			h, w, c = img.shape
			assert c==3

			if h!=224 or w!=224 :
				img = misc.imresize(img, (self.crop_size, self.crop_size))
			
			images[i] = img

		return images, self.test_image[self.test_ptr]

#if __name__ == '__main__':
#	data = Dataset(wiki_Path)
#	for i in range(1000):
#		data.next_batch(50,'train')