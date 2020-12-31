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



from torchvision.transforms import functional as F

import numpy as np
def get_noise_image():
    base = np.random.randn(720, 720, 3)
    mean = np.array((0.485, 0.456, 0.406))
    std = np.array((0.229, 0.224, 0.225))

    image = (((base * std) + mean).clip(0, 1) * 255).astype(np.uint8)

    return Image.fromarray(image)

def rotate_and_resize(base_image, image):
    width, height = base_image.size

    mask = Image.new('L', image.size, 255)

    p = random.randint(0, 360)

    rotated_image = F.rotate(image, angle=p, resample=Image.BICUBIC, expand=True)
    rotated_mask = F.rotate(mask, angle=p, resample=Image.BICUBIC, expand=True)

    p = random.uniform(0.4, 0.6)

    im_width, im_height = rotated_image.size

    longer_edge = int(min(width, height, max(im_width, im_height) * 2) * p)

    if im_width > im_height:
        resized_im_width = longer_edge
        resized_im_height = longer_edge * im_height // im_width
    else:
        resized_im_width = longer_edge * im_width // im_height
        resized_im_height = longer_edge


    resized_image = F.resize(rotated_image, (resized_im_height, resized_im_width), Image.BICUBIC)
    resized_mask = F.resize(rotated_mask, (resized_im_height, resized_im_width), Image.BICUBIC)

    return resized_image, resized_mask

def paste(base_image, image, pos, mask=None):
    Image.Image.paste(base_image, image, tuple(map(int, pos)), mask=mask)
