"""
Usage:
  # From tensorflow/models/
  # Create train data:
  python generate_tfrecord.py --csv_input=data/train_labels.csv  --output_path=train.record
  # Create test data:
  python generate_tfrecord.py --csv_input=data/test_labels.csv  --output_path=test.record
"""
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os
import io
import pandas as pd
import tensorflow as tf

from PIL import Image
from object_detection.utils import dataset_util
from collections import namedtuple, OrderedDict

flags = tf.app.flags
flags.DEFINE_string('csv_input', '', 'Path to the CSV input')
flags.DEFINE_string('output_path', '', 'Path to output TFRecord')
FLAGS = flags.FLAGS


# TO-DO replace this with label map
def class_text_to_int(row_label):
    if row_label == 'adidas':
        return 1
    elif row_label == 'apple':
        return 2
    elif row_label == 'bmw':
        return 3
    elif row_label == 'citroen':
        return 4
    elif row_label == 'cocacola':
        return 5
    elif row_label == 'fedex':
        return 6
    elif row_label == 'ferrari':
        return 7
    elif row_label == 'ford':
        return 8
    elif row_label == 'google':
        return 9
    elif row_label == 'heineken':
        return 10
    elif row_label == 'hp':
        return 11
    elif row_label == 'mcdonalds':
        return 12
    elif row_label == 'mini':
        return 13
    elif row_label == 'nbc':
        return 14
    elif row_label == 'nike':
        return 15
    elif row_label == 'pepsi':
        return 16
    elif row_label == 'porsche':
        return 17
    elif row_label == 'puma':
        return 18
    elif row_label == 'redbull':
        return 19
    elif row_label == 'sprite':
        return 20
    elif row_label == 'starbucks':
        return 21
    elif row_label == 'intel':
        return 22
    elif row_label == 'texaco':
        return 23
    elif row_label == 'unicef':
        return 24
    elif row_label == 'vodafone':
        return 25
    elif row_label == 'yahoo':
        return 26
    elif row_label == 'dhl':
        return 27
    elif row_label == 'chanel':
        return 28
    elif row_label == 'gucci':
        return 29
    elif row_label == 'hh':
        return 30
    elif row_label == 'lacoste':
        return 31
    elif row_label == 'mk':
        return 32
    elif row_label == 'prada':
        return 33
    elif row_label == 'supreme':
        return 34
    else:
        0


def split(df, group):
    data = namedtuple('data', ['filename', 'object'])
    gb = df.groupby(group)
    return [data(filename, gb.get_group(x)) for filename, x in zip(gb.groups.keys(), gb.groups)]


def create_tf_example(group, path):
    with tf.gfile.GFile(os.path.join(path, '{}'.format(group.filename)), 'rb') as fid:
        encoded_jpg = fid.read()
    encoded_jpg_io = io.BytesIO(encoded_jpg)
    image = Image.open(encoded_jpg_io)
    width, height = image.size

    filename = group.filename.encode('utf8')
    image_format = b'jpg'
    xmins = []
    xmaxs = []
    ymins = []
    ymaxs = []
    classes_text = []
    classes = []

    for index, row in group.object.iterrows():
        xmins.append(row['xmin'] / width)
        xmaxs.append(row['xmax'] / width)
        ymins.append(row['ymin'] / height)
        ymaxs.append(row['ymax'] / height)
        classes_text.append(row['class'].encode('utf8'))
        classes.append(class_text_to_int(row['class']))

    tf_example = tf.train.Example(features=tf.train.Features(feature={
        'image/height': dataset_util.int64_feature(height),
        'image/width': dataset_util.int64_feature(width),
        'image/filename': dataset_util.bytes_feature(filename),
        'image/source_id': dataset_util.bytes_feature(filename),
        'image/encoded': dataset_util.bytes_feature(encoded_jpg),
        'image/format': dataset_util.bytes_feature(image_format),
        'image/object/bbox/xmin': dataset_util.float_list_feature(xmins),
        'image/object/bbox/xmax': dataset_util.float_list_feature(xmaxs),
        'image/object/bbox/ymin': dataset_util.float_list_feature(ymins),
        'image/object/bbox/ymax': dataset_util.float_list_feature(ymaxs),
        'image/object/class/text': dataset_util.bytes_list_feature(classes_text),
        'image/object/class/label': dataset_util.int64_list_feature(classes),
    }))
    return tf_example


def main(_):
    writer = tf.python_io.TFRecordWriter(FLAGS.output_path)
    path = os.path.join(os.getcwd(), 'object_detection', 'Logos', 'images')
    examples = pd.read_csv(FLAGS.csv_input)
    grouped = split(examples, 'filename')
    for group in grouped:
        tf_example = create_tf_example(group, path)
        writer.write(tf_example.SerializeToString())

    writer.close()
    output_path = os.path.join(os.getcwd(), FLAGS.output_path)
    print('Successfully created the TFRecords: {}'.format(output_path))


if __name__ == '__main__':
    tf.app.run()