import click
from glob import glob
import zipfile
import random
import math
from pathlib import Path
import shutil
import os

random.seed(23)


def get_labels(directory):
    items = list(glob('{}/*.txt'.format(directory)))
    items.remove('{}/classes.txt'.format(directory))
    return items


def split_dataset_files(labels, images):
    dataset_labels, dataset_images = {}, {}
    for directory, label in labels.items():
        dataset_labels[directory] = {}
        dataset_images[directory] = {}
        idxs = list(range(len(label)))
        random.shuffle(idxs)
        train = round(len(idxs) * 0.75)
        val = train + round(len(idxs) * 0.15)
        train_idxs = idxs[:train]
        val_idxs = idxs[train:val]
        test_idxs = idxs[val:]
        dataset_labels[directory]['train'] = [label[idx] for idx in train_idxs]
        dataset_labels[directory]['val'] = [label[idx] for idx in val_idxs]
        dataset_labels[directory]['test'] = [label[idx] for idx in test_idxs]
        dataset_images[directory]['train'] = [images[directory][idx] for idx in train_idxs]
        dataset_images[directory]['val'] = [images[directory][idx] for idx in val_idxs]
        dataset_images[directory]['test'] = [images[directory][idx] for idx in test_idxs]
    return dataset_labels, dataset_images


def copy_files(labels, images, base_directory):
    for name in ['train', 'val', 'test']:
        image_base = (base_directory / 'images' / name)
        image_base.mkdir(exist_ok=True)
        label_base = (base_directory / 'labels' / name)
        label_base.mkdir(exist_ok=True)

        for directory, dir_labels in labels.items():
            print('copying {} files in {}'.format(name, directory))
            for label in dir_labels[name]:
                shutil.copy(label, label_base)

        for directory, dir_images in images.items():
            print('copying {} files in {}'.format(name, directory))
            for image in dir_images[name]:
                shutil.copy(image, image_base)


def create_metadata(directory):
    for name in ['train', 'val', 'test']:
        image_base = (directory / 'images' / name)
        print('Creating {}.txt in {}'.format(name, directory))
        with open('{}/{}.txt'.format(directory, name), 'w') as fp:
            for filename in image_base.iterdir():
                fp.write('{}\n'.format(filename))

    coco_names = 'coco1.names'
    print('Creating {} file'.format(coco_names))
    with open('{}/{}'.format(directory, coco_names), 'w') as fp:
        fp.write('facetouch\n')

    coco_data = 'coco1.data'
    print('Creating {} file'.format(coco_data))
    with open('{}/{}'.format(directory, coco_data), 'w') as fp:
        fp.write('classes=1\n')
        fp.write('train={}/train.txt\n'.format(directory))
        fp.write('valid={}/val.txt\n'.format(directory))
        fp.write('names={}/{}\n'.format(directory, coco_names))


def create_archive(filename, directory):
    print('Creating zip file {}'.format(filename))
    zipf = zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(directory):
        for filename in files:
            zipf.write(os.path.join(root, filename))
    zipf.close()


@click.command()
@click.option('--directories', type=str, multiple=True)
@click.option('--dataset_name', type=str, required=True)
def run(directories, dataset_name):
    # 0. Create directory
    dataset_name = Path(dataset_name)
    dataset_name.mkdir(exist_ok=True)
    (dataset_name / 'images').mkdir(exist_ok=True)
    (dataset_name / 'labels').mkdir(exist_ok=True)
    # 1. Collect all the labels
    labels = {directory: get_labels(directory) for directory in directories}
    images = {directory: [label.replace('txt', 'jpg') for label in labels]
              for directory, labels in labels.items()}
    # 2. Create train/val/test sets
    dataset_labels, dataset_images = split_dataset_files(labels, images)
    # 3. Copy files
    print('copying files')
    copy_files(dataset_labels, dataset_images, dataset_name)
    # 4. Create train/val.txt
    create_metadata(dataset_name)
    # 5. Create zip file
    create_archive('{}.zip'.format(dataset_name), dataset_name)


if __name__ == "__main__":
    run()
