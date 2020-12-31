import csv
import pickle
import os
import collections
from tqdm import tqdm

download_dir = './data/'

image_label_dict = collections.defaultdict(list) # image_id: list of (label, confidence)

selected_labels = {
    '/m/02b389': 'Bottle cap',
}

with open('image-labels.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')

    next(reader)
    for image_id, _, label, confidence in tqdm(reader):
        if label in selected_labels and confidence == '1':
            image_label_dict[image_id].append((label, selected_labels[label]))

with open('image_label_dict.pickle', 'wb') as f:
    pickle.dump(image_label_dict, f)


download_image_list = []
with open('image-metadata.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')

    next(reader)
    for image_id, _, url, _, _, _, _, _, _, _, _, rotation in tqdm(reader):
        if image_id in image_label_dict:
            download_image_list.append((image_id, url, rotation))

with open('download_image_list.pickle', 'wb') as f:
    pickle.dump(download_image_list, f)

try:
    os.makedirs(download_dir)
except FileExistsError as e:
    pass

