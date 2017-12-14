from ctypes import *
from PIL import Image, ImageFont, ImageDraw, ImageEnhance

import sys
import math
import random
import time
import _thread
import json
import os
import optparse
import errno

print(" _   _____________ _____ _   _  _   _        _   ________  _________ ")
print("| | | | ___ \ ___ \_   _| \ | || \ | |      | | / /| ___ \|___  /   |")
print("| | | | |_/ / |_/ / | | |  \| ||  \| |______| |/ / | |_/ /   / / /| |")
print("| | | |    /| ___ \ | | | . ` || . ` |______|    \ | ___ \  / / /_| |")
print("| |_| | |\ \| |_/ /_| |_| |\  || |\  |      | |\  \| |_/ /./ /\___  |")
print(" \___/\_| \_\____/ \___/|_| \_/|_| \_/      \_| \_/|____/ /_/     |_|")
print("=====================================================================")
print("    __  ______  __    ____     _________________________________     ")
print("    \ \/ / __ \/ /   / __ \   /_  __/ ____/ ___/_  __/ ____/ __ \    ")
print("     \  / / / / /   / / / /    / / / __/  \__ \ / / / __/ / /_/ /    ")
print("     / / /_/ / /___/ /_/ /    / / / /___ ___/ // / / /___/ _, _/     ")	
print("    /_/\____/_____/\____/    /_/ /_____//____//_/ /_____/_/ |_|  \n\n")

''' CONFIG '''
START_IMG = 7300
END_IMG = 7480
FORMAT = 'png'
IMG_STRING = '%06d.' + FORMAT
IMG_LOCATION = '/data/urbinn/darknet/ownlabels/img/'
CONFIG = b"/data/urbinn/darknet/own_cfg/config-predict.cfg"
WEIGHTS = b"/data/urbinn/darknet/kitti_own_labels_0612/config_250000.weights"
DATA = b"/data/urbinn/darknet/own_cfg/data.data"
IMG_PRINT = True

OUTPUT_PATH = '/data/urbinn/darknet/output/batch/{}/'
FOLDER_NAME = input("Output folder name (leave empty for timestamp)") or int(time.time())
OUTPUT_FOLDER = OUTPUT_PATH.format(FOLDER_NAME)

GPU_ID = input("GPU ID to be used (default = 0)") or 0

if '-help' in sys.argv[1:]:
    print('-i            Interactive mode, the program will promt for the input parameters')
    print('-dataonly     No images will be rendered, only boundingboxes .json output will be generated')

if '-dataonly' in sys.argv[1:]:
    print('Used -dataonly flag: no images will be rendered.')
    IMG_PRINT = False

if '-i' in sys.argv[1:]:
    print('Used interactive flag: please enter desired config values, or leave empty to use default values')
    START_IMG = int(input('1/6  Start image #: ') or START_IMG)
    END_IMG = int(input('2/6  Ending image #: ') or END_IMG)
    IMG_LOCATION = input('3/6  Source image path: ') or IMG_LOCATION
    CONFIG = input('4/6  Config file path: ').encode('utf-8') or CONFIG
    WEIGHTS = input('5/6  Weights file path: ').encode('utf-8') or WEIGHTS
    DATA = input('6/6  Data file path: ').encode('utf-8') or DATA

'''Create output folder for current run'''
#try:
#     os.makedirs('{}data/'.format(OUTPUT_FOLDER))
#except OSError as e:
#    if e.errno != errno.EEXIST:
#        raise  # raises the error again
#print('\nData is saved to: {}\n'.format(OUTPUT_FOLDER))

''' Decorator method for timing a method '''
def timing(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        print('%s took %0.3f ms' % (f.__name__, (time2-time1)*1000.0))
        return ret
    return wrap

def sample(probs):
    s = sum(probs)
    probs = [a/s for a in probs]
    r = random.uniform(0, 1)
    for i in range(len(probs)):
        r = r - probs[i]
        if r <= 0:
            return i
    return len(probs)-1

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
lib = CDLL("libdarknet.so", RTLD_GLOBAL)
lib.network_width.argtypes = [c_void_p]
lib.network_width.restype = c_int
lib.network_height.argtypes = [c_void_p]
lib.network_height.restype = c_int

predict = lib.network_predict
predict.argtypes = [c_void_p, POINTER(c_float)]
predict.restype = POINTER(c_float)

make_boxes = lib.make_boxes
make_boxes.argtypes = [c_void_p]
make_boxes.restype = POINTER(BOX)

set_gpu = lib.cuda_set_device
set_gpu.argtypes = [c_int]

free_ptrs = lib.free_ptrs
free_ptrs.argtypes = [POINTER(c_void_p), c_int]

num_boxes = lib.num_boxes
num_boxes.argtypes = [c_void_p]
num_boxes.restype = c_int

make_probs = lib.make_probs
make_probs.argtypes = [c_void_p]
make_probs.restype = POINTER(POINTER(c_float))

detect = lib.network_predict
detect.argtypes = [c_void_p, IMAGE, c_float, c_float, c_float, POINTER(BOX), POINTER(POINTER(c_float))]

reset_rnn = lib.reset_rnn
reset_rnn.argtypes = [c_void_p]

load_net = lib.load_network
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
network_detect.argtypes = [c_void_p, IMAGE, c_float, c_float, c_float, POINTER(BOX), POINTER(POINTER(c_float))]

def classify(net, meta, im):
    out = predict_image(net, im)
    res = []
    for i in range(meta.classes):
        res.append((meta.names[i], out[i]))
    res = sorted(res, key=lambda x: -x[1])
    return res

""" Detect using darknet """
@timing
def detect(net, meta, image, thresh=.4, hier_thresh=.4, nms=.45):
    im = load_image(image, 0, 0)
    boxes = make_boxes(net)
    probs = make_probs(net)
    num =   num_boxes(net)
    network_detect(net, im, thresh, hier_thresh, nms, boxes, probs)
    res = []
    for j in range(num):
        for i in range(meta.classes):
            if probs[j][i] > 0:
                res.append((meta.names[i], probs[j][i], (boxes[j].x, boxes[j].y, boxes[j].w, boxes[j].h)))
    res = sorted(res, key=lambda x: -x[1])
    free_image(im)
    free_ptrs(cast(probs, POINTER(c_void_p)), num)
    return res

''' Draws image on the source image using PIL '''
def draw_image(result, image):
    result = list(result)
    name = result.pop(0)
    source_img = Image.open(image).convert("RGBA")
    draw = ImageDraw.Draw(source_img)
    font = ImageFont.truetype("DejaVuSansMono.ttf", 12)
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
        draw.rectangle([x1, y1-y3, x1+x3, y1], fill='grey', outline="red")
        ''' Draws the text in the image '''
        draw.text((x1, y1-y3), tag, font=font)
    output_file = open('{}/data/{}'.format(OUTPUT_FOLDER, name), 'wb')
    source_img.save(output_file, FORMAT)

'''Converts the detect() result object to a list appendable to the final result'''
def results_to_list(name, result):
    result_list = []
    for r in result:
        r = list(r)
        r[0] = r[0].decode('utf8')
        result_list.append(r)
    return [name] + result_list

def create_output_folder(FOLDER_NAME): 
    global OUTPUT_FOLDER
    global OUTPUT_PATH
    OUTPUT_FOLDER = OUTPUT_PATH.format(FOLDER_NAME)
    try:
         os.makedirs('{}data/'.format(OUTPUT_FOLDER))
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise  # raises the error again
    print('\nData is saved to: {}\n'.format(OUTPUT_FOLDER))



if __name__ == "__main__":
    it = 10000
    while it < 340000:
        WEIGHTS = 'kitti_own_labels_0612/config_%i.weights' % it 
        folder_name = '0712_%i' % it
        set_gpu(GPU_ID)
        net = load_net(CONFIG, WEIGHTS.encode(), 0)
        meta = load_meta(DATA) 
        create_output_folder(folder_name)
        results = []
        for i in range(START_IMG, END_IMG):
            print('Detecting {}/{}'.format(i+1, END_IMG))
            name = IMG_STRING % i
            image = IMG_LOCATION + name
            try:
                result = detect(net, meta, image.encode())    
                result_list = results_to_list(name, result)
                results.append(result_list)
            except Exception as e:
                print(' FAILED to run yolo on: {}, reason: {}'.format(name, e))
            try:
                if IMG_PRINT:
                    t = _thread.start_new_thread(draw_image, (result_list, image,))
            except Exception as e:
                print('Could not save image: {}'.format(e))

        ''' Script is done, saving results '''
        JSON_NAME = '{}/objects.json'.format(OUTPUT_FOLDER)
        with open(JSON_NAME, 'w+', encoding="utf8") as outfile:
            json.dump(results, outfile, indent=2)
        # Some sleep to allow all threads to finish
        it += 10000
    time.sleep(15)
