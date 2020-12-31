import json, os, itertools
from tqdm import tqdm

annotation_dir = 'data'
annotation_files = os.listdir(annotation_dir)
data_dir = 'data'

annotations = []
for annotation_file in tqdm(annotation_files):
    if not annotation_file.endswith('.json'): continue

    with open(os.path.join(annotation_dir, annotation_file), 'r') as f:
        annotations.append(json.loads(f.read()))

from PIL import Image, ImageOps

def load_image(filename):
    image = Image.open(filename).convert('RGB')
    image = ImageOps.exif_transpose(image)
    return image

def is_overlap(one_shape, other_shape):
    # one-left >= other-right or otherleft >= one-right (x축에서 겹치지 않을 때)
    if one_shape[0][0] >= other_shape[1][0] or other_shape[0][0] >= one_shape[1][0]:
        return False

    # one-top >= other-bottom or other-top >= one-bottom
    if one_shape[0][1] >= other_shape[1][1] or other_shape[0][1] >= one_shape[1][1]:
        return False

    return True

def get_merged_shape(one_shape, other_shape):
    return [
        [min(one_shape[0][0], other_shape[0][0]), min(one_shape[0][1], other_shape[0][1])],
        [max(one_shape[1][0], other_shape[1][0]), max(one_shape[1][1], other_shape[1][1])],
    ]

def crop(image, box, margin_pct=0.0):
    width, height = box[1][0] - box[0][0], box[1][1] - box[0][1]
    margin = margin_pct * max(width, height)
    margined_box = [
        box[0][0] - margin, box[0][1] - margin,
        box[1][0] + margin, box[1][1] + margin,
    ]

    return image.crop(margined_box)


import random
margin_pct = 0.02
box_annotations = []
def get_objects(annotation):
    objects = []
    used = set()
    for idx, i_shape in enumerate(annotation['shapes']):
        if idx in used: continue

        overlap_labels = [i_shape['label']]
        overlap_box = i_shape['points']

        used.add(idx)
        for jdx, j_shape in enumerate(annotation['shapes'][idx+1:], idx+1):
            if is_overlap(overlap_box, j_shape['points']):
                overlap_labels.append(j_shape['label'])
                overlap_box = get_merged_shape(overlap_box, j_shape['points'])
                used.add(jdx)

        objects.append({
            'labels': overlap_labels,
            'box': overlap_box,
            'original_image': annotation['imagePath']
        })


    return objects

import multiprocessing

with multiprocessing.Pool(70) as p:
    objects = p.map(get_objects, annotations)
