

```python
from ctypes import *
from PIL import Image, ImageFont, ImageDraw, ImageEnhance

import math
import random
import time
import _thread
import json
import os

''' CONFIG '''
START_IMG = 0
END_IMG = 10
FORMAT = 'png'
IMG_STRING = '%06d.' + FORMAT
IMG_LOCATION = '/data/urbinn/datasets/kitti/KITTI_Left_Images/testing/image_2/'
CONFIG = b"/data/urbinn/yolo-kitti/tiny-yolo-kitti.cfg"
WEIGHTS = b"/data/urbinn/yolo-kitti/tiny-yolo-kitti_final.weights"
DATA = b"cfg/voc.data"

'''Create output folder for current run'''
OUTPUT_FOLDER = 'output/{}/'.format(int(time.time()))
os.makedirs('{}data/'.format(OUTPUT_FOLDER))
print('Data is saved to: {}'.format(OUTPUT_FOLDER))

''' Decorator method for timing a method '''
def timing(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        print('%s took %0.3f ms' % (f.__name__, (time2-time1)*1000.0))
        return ret
    return wrap

def c_array(ctype, values):
    return (ctype * len(values))(*values)

class BOX(Structure):
    _fields_ = [("x", c_float),
                ("y", c_float),
                ("w", c_float),
                ("h", c_float)]

class IMAGE(Structure):
    _fields_ = [("w", c_int),
                ("h", c_int),
                ("c", c_int),
                ("data", POINTER(c_float))]

class METADATA(Structure):
    _fields_ = [("classes", c_int),
                ("names", POINTER(c_char_p))]

#lib = CDLL("/home/pjreddie/documents/darknet/libdarknet.so", RTLD_GLOBAL)
lib = CDLL("./libdarknet.so", RTLD_GLOBAL)
lib.network_width.argtypes = [c_void_p]
lib.network_width.restype = c_int
lib.network_height.argtypes = [c_void_p]
lib.network_height.restype = c_int

predict = lib.network_predict_p
predict.argtypes = [c_void_p, POINTER(c_float)]
predict.restype = POINTER(c_float)

make_boxes = lib.make_boxes
make_boxes.argtypes = [c_void_p]
make_boxes.restype = POINTER(BOX)

free_ptrs = lib.free_ptrs
free_ptrs.argtypes = [POINTER(c_void_p), c_int]
num_boxes = lib.num_boxes
num_boxes.argtypes = [c_void_p]
num_boxes.restype = c_int

make_probs = lib.make_probs
make_probs.argtypes = [c_void_p]
make_probs.restype = POINTER(POINTER(c_float))

detect = lib.network_predict_p
detect.argtypes = [c_void_p, IMAGE, c_float, c_float, c_float, POINTER(BOX),
                   POINTER(POINTER(c_float))]

reset_rnn = lib.reset_rnn
reset_rnn.argtypes = [c_void_p]

load_net = lib.load_network_p
load_net.argtypes = [c_char_p, c_char_p, c_int]
load_net.restype = c_void_p

free_image = lib.free_image
free_image.argtypes = [IMAGE]

letterbox_image = lib.letterbox_image
letterbox_image.argtypes = [IMAGE, c_int, c_int]
letterbox_image.restype = IMAGE

load_meta = lib.get_metadata
lib.get_metadata.argtypes = [c_char_p]
lib.get_metadata.restype = METADATA

load_image = lib.load_image_color
load_image.argtypes = [c_char_p, c_int, c_int]
load_image.restype = IMAGE

predict_image = lib.network_predict_image
predict_image.argtypes = [c_void_p, IMAGE]
predict_image.restype = POINTER(c_float)

network_detect = lib.network_detect
network_detect.argtypes = [c_void_p, IMAGE, c_float, c_float, c_float,
                           POINTER(BOX), POINTER(POINTER(c_float))]

def sample(probs):
    s = sum(probs)
    probs = [a/s for a in probs]
    r = random.uniform(0, 1)
    for i in range(len(probs)):
        r = r - probs[i]
        if r <= 0:
            return i
    return len(probs)-1

def classify(net, meta, im):
    out = predict_image(net, im)
    res = []
    for i in range(meta.classes):
        res.append((meta.names[i], out[i]))
    res = sorted(res, key=lambda x: -x[1])
    return res

@timing
def detect(net, meta, image, thresh=.35, hier_thresh=.4, nms=.45):
    im = load_image(image, 0, 0)
    boxes = make_boxes(net)
    probs = make_probs(net)
    num =   num_boxes(net)
    network_detect(net, im, thresh, hier_thresh, nms, boxes, probs)
    res = []
    for j in range(num):
        for i in range(meta.classes):
            if probs[j][i] > 0:
                res.append((meta.names[i].decode(), probs[j][i], (boxes[j].x,
                boxes[j].y, boxes[j].w, boxes[j].h)))
    res = sorted(res, key=lambda x: -x[1])
    free_image(im)
    free_ptrs(cast(probs, POINTER(c_void_p)), num)
    return res

def draw_image(result, image):
    result = list(result)
    name = result.pop(0)
    source_img = Image.open(image).convert("RGBA")
    draw = ImageDraw.Draw(source_img)
    font = ImageFont.truetype("DejaVuSerif-Bold.ttf", 15)
    for cl in result:
        ''' calculates and draws the top left and bottom right coordinates based
            on the center coordinates and the dimensions of the bounding-box '''
        x1 = int(cl[2][0] - .5 * cl[2][2]) # Top left of Bounding-box
        y1 = int(cl[2][1] - .5 * cl[2][3]) # Top left of Bounding-box
        x2 = int(cl[2][0] + .5 * cl[2][2]) # Bottom right of Bounding-box
        y2 = int(cl[2][1] + .5 * cl[2][3]) # Bottom right of Bounding-box
        tag = str.upper("{} (%{:2.2f})".format(cl[0], cl[1]*100))
        draw.rectangle([x1, y1, x2, y2], outline="red")
        ''' calculates coordinates for text box, and draws it'''
        x3, y3 = font.getsize(tag)
        draw.rectangle([x1, y1, x1+x3, y1+y3], fill='grey', outline="red")
        ''' Draws the text in the image '''
        draw.text((x1, y1), tag, font=font)
    output_file = open('{}/data/{}'.format(OUTPUT_FOLDER, name), 'wb')
    source_img.save(output_file, FORMAT)


if __name__ == "__main__":
    net = load_net(CONFIG, WEIGHTS, 0)
    meta = load_meta(DATA)
    results = []
    for i in range(START_IMG, END_IMG):
        name = IMG_STRING % i
        image = IMG_LOCATION + name
        try:
            r = detect(net, meta, image.encode())
            r = [name] + r
            results.append(r)
        except:
            print('%s FAILED to run yolo on: ' % name)
        try:
            t = _thread.start_new_thread(draw_image, (r, image,))
        except Exception as e:
            print('Could not save image: {}'.format(e))
    JSON_NAME = '{}/objects.json'.format(OUTPUT_FOLDER)
    with open(JSON_NAME, 'w', encoding="utf8") as outfile:
        json.dump(results, outfile, indent=2)
    # Some sleep to allow all threads to finish
    time.sleep(5)

```


```python

```
