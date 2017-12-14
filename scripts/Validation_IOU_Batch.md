

```python
import json
import time
import operator
import matplotlib.pyplot as plt

W = int(input('Image width: ') or 1242)
H = int(input('Image height: ') or 375)
DEBUG = bool(input('Debug mode? [y/N]:'))
MATCH_CLASS = bool(input('Match classes mode? [y/N]:'))
OLD_S = bool(input('Old style bounding box notation? [y/N]:'))
IOU = float(input('IOU Treshold [0.0-1.0]: ') or 0.20)
YOLO_JSON = '/data/urbinn/darknet/output/batch/0712_{}/objects.json'
KITTI_GT = '/data/urbinn/darknet/gtconverted/{}'
CLASSES = '/data/urbinn/darknet/own_cfg/final_selftrained.names'
false_pos = ops = bbs = gt_bbs = 0
detected_classes = []


''' Decorator method for timing a method '''
def timing(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        print('%s took %0.3f ms' % (f.__name__, (time2-time1)*1000.0))
        return ret
    return wrap


''' prints the config '''
def print_cfg():
    print('YOLO_JSON: {}\nKITTI_GT: {}\nIOU Treshold: {}\n'.format(YOLO_JSON,KITTI_GT,IOU))

''' Returns the available classes '''
def get_classes():
    with open(CLASSES) as classes:
        return [c.replace('\n', '').lower() for c in classes.readlines()]

''' Calculates the  intersection over union '''
def iou(boxA, boxB):
    # determine the (x, y)-coordinates of the intersection rectangle
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])
    # compute the area of intersection rectangle
    interArea = (xB - xA + 1) * (yB - yA + 1)
    # compute the area of both the prediction and ground-truth rectangles
    boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
    boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)
    # compute the intersection over union
    iou = interArea / float(boxAArea + boxBArea - interArea)
    return iou


# class Counter:
    
#     classes = {}
    
#     def __init__(cl):
#         self.classes = {el:0 for el in cl}
        
#     def add(c):
#         self.classes[c] += 1
        
#     def sub(c):
#         self.classes[c] -= 1
    


''' Datamodel for handeling boundingboxes '''
class BoundingBox:
    name = None
    x1 = y1 = x2 = y2 = 0

    def __init__(self, x1, y1, x2, y2, name=None, centre_point=False):
        self.x1 = float(x1)        # X coordinate of BB (lower-left)
        self.y1 = float(y1)       # Y coordinate of BB (lower-left)
        self.x2 = float(x2)       # X coordinate of BB (upper-right)
        self.y2 = float(y2)        # Y coordinate of BB (upper-right)
        self.set_class(name)
            
    def get_list(self):
        return [self.x1, self.y1, self.x2, self.y2]
    
    def get_class(self):
        return self.name
    
    def set_class(self, name):
        if isinstance(name, int):
            self.name = int(name)
        else:
            try:
                self.name = CLASSES.index(name.replace(' ', '').lower())
            except:
                print('No matching id found for: ', name.replace(' ', '').lower())

    def __str__(self):
        return '{}: x1:{}, y1:{}, x2:{}, y2:{}'.format(self.name, self.x1, self.y1, self.x2, self.y2)
    
class BoundingBoxKitti(BoundingBox):
        
    def __init__(self, x, y, w, h, name='0', centre_point=False):
        self.x1 = int((x - .5 * w) * W) # Top left of Bounding-box
        self.y1 = int((y - .5 * h) * H) # Top left of Bounding-box
        self.x2 = int((x + .5 * w) * W) # Bottom right of Bounding-box
        self.y2 = int((y + .5 * h) * H) # Bottom right of Bounding-box
        self.name = int(name)  # id of recoognized class in BB
        gt_classes[self.name] += 1
    
class BoundingBoxYolo(BoundingBox):
    
    translation_x = -12
    translation_y = -12
        
    def __init__(self, x, y, w, h, name='0', centre_point=False):
        self.x1 = int(x - .5 * w) + self.translation_x # Top left of Bounding-box
        self.y1 = int(y - .5 * h) + self.translation_y # Top left of Bounding-box
        self.x2 = int(x + .5 * w) + self.translation_x # Bottom right of Bounding-box
        self.y2 = int(y + .5 * h) + self.translation_y # Bottom right of Bounding-box
        self.set_class(name)  # id of recoognized class in BB
        detected_classes[self.name] += 1



''' GroundTruth object '''
class GroundTruth:
    
    bounding_boxes = []
    
    def __init__(self, gt):
        self.bounding_boxes = []
        global gt_bbs
        for line in gt:
            split = [float(x) for x in line.split()]
            gt_bbs += 1
            ''' convert the x1 x2 params to a bounding box '''
            if OLD_S:
                boundingbox = BoundingBox(split[4], split[5], split[6], split[7], name=split[0])
            else:
                boundingbox = BoundingBoxKitti(split[1], split[2], split[3], split[4], name=split[0])
            self.bounding_boxes.append(boundingbox)
            if DEBUG:
                print(boundingbox)

    def check_boundingbox_iou(self, bb):
        ''' functionality to compare BB to the set of bb's in the Ground Truth'''
        global bbs
        bbs += 1
        max_result = 0.0
        for index, gt_bb in enumerate(self.bounding_boxes):
            global ops
            ops += 1
            if bb.get_class() == gt_bb.get_class() or not MATCH_CLASS:
                result = iou(bb.get_list(), gt_bb.get_list())
                if 1 >= result > max_result:
                    max_result = result
        if DEBUG:        
            print(max_result)
        if max_result < IOU:
            global false_pos
            false_pos += 1
            if DEBUG:
                print('MAX RESULT {}\n-----------\n{}'.format(max_result, bb))
                for bbbb in self.bounding_boxes:
                    print('       ', bbbb)


@timing
def evaluate(batch):
    global CLASSES
    with open(YOLO_JSON.format(batch)) as results:
        results = json.loads(results.read())
        print(batch)
        print('Checking {} images...'.format(len(results)))
        for result in results:
            image = result.pop(0).replace('png', 'txt')
            current_gt = KITTI_GT.format(image)
            try:
                with open(current_gt) as gt_results:
                    # creates new gt object with info from .txt
                    ground_truth = GroundTruth(gt_results)
                    for bb in result:
                        bb = BoundingBoxYolo(bb[2][0], bb[2][1], bb[2][2], bb[2][3], bb[0])
                        if DEBUG:
                            print('Detected BB: ', bb)
                        ground_truth.check_boundingbox_iou(bb)
            except Exception as e:
                print(e)
                    
        # OUTPUT THE EVALUTATION
        print('------------------------------------')
        print('Compares:           {} '.format(ops))
        print('Detected BB\'s:      {}'.format(bbs))
        print('GroundTruth BB\'s:   {}'.format(gt_bbs))
        print('False positives:    {}'.format(false_pos))
        print('percentage of boundingboxes that where detected:             % {:.2f}'.format(bbs/gt_bbs*100))
        print('percentage of boundingboxes that where falsely detected:     % {:.2f}'.format(false_pos/bbs*100))
        print('net percentage of boundingboxes that where detected correct: % {:.2f}'.format((bbs/gt_bbs-false_pos/bbs)*100))
        print('------------------------------------')

print_cfg()
CLASSES = get_classes()
batches = []
false_poss = []
opss = []
bbss = []
gt_bbss = []
total_detected_classes = []
total_gt_classes = []
batch = 10000
while batch < 340000:
    false_pos = ops = bbs = gt_bbs = 0
    detected_classes = []
    gt_classes = []
    for i in range(len(CLASSES)):
        detected_classes.append(0)
        gt_classes.append(0)
    evaluate(batch)
    batches.append(batch)
    false_poss.append(false_pos)
    opss.append(ops)
    bbss.append(bbs)
    gt_bbss.append(gt_bbs)
    total_detected_classes.append(detected_classes)
    total_gt_classes.append(gt_classes)
    batch += 10000
    

```

    Image width: 
    Image height: 
    Debug mode? [y/N]:
    Match classes mode? [y/N]:
    Old style bounding box notation? [y/N]:
    IOU Treshold [0.0-1.0]: 
    YOLO_JSON: /data/urbinn/darknet/output/batch/0712_{}/objects.json
    KITTI_GT: /data/urbinn/darknet/gtconverted/{}
    IOU Treshold: 0.2
    
    10000
    Checking 180 images...
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007333.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007334.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007335.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007336.txt'
    ------------------------------------
    Compares:           4431 
    Detected BB's:      367
    GroundTruth BB's:   2126
    False positives:    55
    percentage of boundingboxes that where detected:             % 17.26
    percentage of boundingboxes that where falsely detected:     % 14.99
    net percentage of boundingboxes that where detected correct: % 2.28
    ------------------------------------
    evaluate took 31.764 ms
    20000
    Checking 180 images...
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007333.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007334.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007335.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007336.txt'
    ------------------------------------
    Compares:           4990 
    Detected BB's:      415
    GroundTruth BB's:   2126
    False positives:    36
    percentage of boundingboxes that where detected:             % 19.52
    percentage of boundingboxes that where falsely detected:     % 8.67
    net percentage of boundingboxes that where detected correct: % 10.85
    ------------------------------------
    evaluate took 33.145 ms
    30000
    Checking 180 images...
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007333.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007334.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007335.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007336.txt'
    ------------------------------------
    Compares:           8043 
    Detected BB's:      655
    GroundTruth BB's:   2126
    False positives:    64
    percentage of boundingboxes that where detected:             % 30.81
    percentage of boundingboxes that where falsely detected:     % 9.77
    net percentage of boundingboxes that where detected correct: % 21.04
    ------------------------------------
    evaluate took 42.585 ms
    40000
    Checking 180 images...
    float division by zero
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007333.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007334.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007335.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007336.txt'
    ------------------------------------
    Compares:           9107 
    Detected BB's:      732
    GroundTruth BB's:   2126
    False positives:    118
    percentage of boundingboxes that where detected:             % 34.43
    percentage of boundingboxes that where falsely detected:     % 16.12
    net percentage of boundingboxes that where detected correct: % 18.31
    ------------------------------------
    evaluate took 45.245 ms
    50000
    Checking 180 images...
    float division by zero
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007333.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007334.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007335.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007336.txt'
    ------------------------------------
    Compares:           8629 
    Detected BB's:      684
    GroundTruth BB's:   2126
    False positives:    93
    percentage of boundingboxes that where detected:             % 32.17
    percentage of boundingboxes that where falsely detected:     % 13.60
    net percentage of boundingboxes that where detected correct: % 18.58
    ------------------------------------
    evaluate took 44.157 ms
    60000
    Checking 180 images...
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007333.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007334.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007335.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007336.txt'
    ------------------------------------
    Compares:           6860 
    Detected BB's:      568
    GroundTruth BB's:   2126
    False positives:    70
    percentage of boundingboxes that where detected:             % 26.72
    percentage of boundingboxes that where falsely detected:     % 12.32
    net percentage of boundingboxes that where detected correct: % 14.39
    ------------------------------------
    evaluate took 39.633 ms
    70000
    Checking 180 images...
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007333.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007334.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007335.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007336.txt'
    ------------------------------------
    Compares:           10740 
    Detected BB's:      837
    GroundTruth BB's:   2126
    False positives:    125
    percentage of boundingboxes that where detected:             % 39.37
    percentage of boundingboxes that where falsely detected:     % 14.93
    net percentage of boundingboxes that where detected correct: % 24.44
    ------------------------------------
    evaluate took 50.358 ms
    80000
    Checking 180 images...
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007333.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007334.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007335.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007336.txt'
    ------------------------------------
    Compares:           4341 
    Detected BB's:      386
    GroundTruth BB's:   2126
    False positives:    41
    percentage of boundingboxes that where detected:             % 18.16
    percentage of boundingboxes that where falsely detected:     % 10.62
    net percentage of boundingboxes that where detected correct: % 7.53
    ------------------------------------
    evaluate took 30.127 ms
    90000
    Checking 180 images...
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007333.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007334.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007335.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007336.txt'
    ------------------------------------
    Compares:           5861 
    Detected BB's:      558
    GroundTruth BB's:   2126
    False positives:    92
    percentage of boundingboxes that where detected:             % 26.25
    percentage of boundingboxes that where falsely detected:     % 16.49
    net percentage of boundingboxes that where detected correct: % 9.76
    ------------------------------------
    evaluate took 35.362 ms
    100000
    Checking 180 images...
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007333.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007334.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007335.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007336.txt'
    ------------------------------------
    Compares:           3702 
    Detected BB's:      348
    GroundTruth BB's:   2126
    False positives:    31
    percentage of boundingboxes that where detected:             % 16.37
    percentage of boundingboxes that where falsely detected:     % 8.91
    net percentage of boundingboxes that where detected correct: % 7.46
    ------------------------------------
    evaluate took 27.955 ms
    110000
    Checking 180 images...
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007333.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007334.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007335.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007336.txt'
    ------------------------------------
    Compares:           4605 
    Detected BB's:      403
    GroundTruth BB's:   2126
    False positives:    54
    percentage of boundingboxes that where detected:             % 18.96
    percentage of boundingboxes that where falsely detected:     % 13.40
    net percentage of boundingboxes that where detected correct: % 5.56
    ------------------------------------
    evaluate took 30.685 ms
    120000
    Checking 180 images...
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007333.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007334.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007335.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007336.txt'
    ------------------------------------
    Compares:           6364 
    Detected BB's:      562
    GroundTruth BB's:   2126
    False positives:    75
    percentage of boundingboxes that where detected:             % 26.43
    percentage of boundingboxes that where falsely detected:     % 13.35
    net percentage of boundingboxes that where detected correct: % 13.09
    ------------------------------------
    evaluate took 34.733 ms
    130000
    Checking 180 images...
    float division by zero
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007333.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007334.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007335.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007336.txt'
    float division by zero
    ------------------------------------
    Compares:           8669 
    Detected BB's:      709
    GroundTruth BB's:   2126
    False positives:    98
    percentage of boundingboxes that where detected:             % 33.35
    percentage of boundingboxes that where falsely detected:     % 13.82
    net percentage of boundingboxes that where detected correct: % 19.53
    ------------------------------------
    evaluate took 41.744 ms
    140000
    Checking 180 images...
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007333.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007334.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007335.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007336.txt'
    ------------------------------------
    Compares:           9761 
    Detected BB's:      779
    GroundTruth BB's:   2126
    False positives:    100
    percentage of boundingboxes that where detected:             % 36.64
    percentage of boundingboxes that where falsely detected:     % 12.84
    net percentage of boundingboxes that where detected correct: % 23.80
    ------------------------------------
    evaluate took 44.759 ms
    150000
    Checking 180 images...
    float division by zero
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007333.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007334.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007335.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007336.txt'
    ------------------------------------
    Compares:           5051 
    Detected BB's:      469
    GroundTruth BB's:   2126
    False positives:    64
    percentage of boundingboxes that where detected:             % 22.06
    percentage of boundingboxes that where falsely detected:     % 13.65
    net percentage of boundingboxes that where detected correct: % 8.41
    ------------------------------------
    evaluate took 30.973 ms
    160000
    Checking 180 images...
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007333.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007334.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007335.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007336.txt'
    ------------------------------------
    Compares:           7218 
    Detected BB's:      597
    GroundTruth BB's:   2126
    False positives:    56
    percentage of boundingboxes that where detected:             % 28.08
    percentage of boundingboxes that where falsely detected:     % 9.38
    net percentage of boundingboxes that where detected correct: % 18.70
    ------------------------------------
    evaluate took 37.292 ms
    170000
    Checking 180 images...
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007333.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007334.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007335.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007336.txt'
    ------------------------------------
    Compares:           6931 
    Detected BB's:      598
    GroundTruth BB's:   2126
    False positives:    60
    percentage of boundingboxes that where detected:             % 28.13
    percentage of boundingboxes that where falsely detected:     % 10.03
    net percentage of boundingboxes that where detected correct: % 18.09
    ------------------------------------
    evaluate took 37.252 ms
    180000
    Checking 180 images...
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007333.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007334.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007335.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007336.txt'
    ------------------------------------
    Compares:           6790 
    Detected BB's:      564
    GroundTruth BB's:   2126
    False positives:    60
    percentage of boundingboxes that where detected:             % 26.53
    percentage of boundingboxes that where falsely detected:     % 10.64
    net percentage of boundingboxes that where detected correct: % 15.89
    ------------------------------------
    evaluate took 36.354 ms
    190000
    Checking 180 images...
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007333.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007334.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007335.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007336.txt'
    ------------------------------------
    Compares:           7711 
    Detected BB's:      660
    GroundTruth BB's:   2126
    False positives:    82
    percentage of boundingboxes that where detected:             % 31.04
    percentage of boundingboxes that where falsely detected:     % 12.42
    net percentage of boundingboxes that where detected correct: % 18.62
    ------------------------------------
    evaluate took 38.685 ms
    200000
    Checking 180 images...
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007333.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007334.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007335.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007336.txt'
    ------------------------------------
    Compares:           7509 
    Detected BB's:      638
    GroundTruth BB's:   2126
    False positives:    77
    percentage of boundingboxes that where detected:             % 30.01
    percentage of boundingboxes that where falsely detected:     % 12.07
    net percentage of boundingboxes that where detected correct: % 17.94
    ------------------------------------
    evaluate took 37.828 ms
    210000
    Checking 180 images...
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007333.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007334.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007335.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007336.txt'
    ------------------------------------
    Compares:           7036 
    Detected BB's:      617
    GroundTruth BB's:   2126
    False positives:    83
    percentage of boundingboxes that where detected:             % 29.02
    percentage of boundingboxes that where falsely detected:     % 13.45
    net percentage of boundingboxes that where detected correct: % 15.57
    ------------------------------------
    evaluate took 38.301 ms
    220000
    Checking 180 images...
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007333.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007334.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007335.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007336.txt'
    ------------------------------------
    Compares:           7705 
    Detected BB's:      648
    GroundTruth BB's:   2126
    False positives:    62
    percentage of boundingboxes that where detected:             % 30.48
    percentage of boundingboxes that where falsely detected:     % 9.57
    net percentage of boundingboxes that where detected correct: % 20.91
    ------------------------------------
    evaluate took 40.558 ms
    230000
    Checking 180 images...
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007333.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007334.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007335.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007336.txt'
    ------------------------------------
    Compares:           7948 
    Detected BB's:      678
    GroundTruth BB's:   2126
    False positives:    105
    percentage of boundingboxes that where detected:             % 31.89
    percentage of boundingboxes that where falsely detected:     % 15.49
    net percentage of boundingboxes that where detected correct: % 16.40
    ------------------------------------
    evaluate took 42.709 ms
    240000
    Checking 180 images...
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007333.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007334.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007335.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007336.txt'
    ------------------------------------
    Compares:           5018 
    Detected BB's:      459
    GroundTruth BB's:   2126
    False positives:    67
    percentage of boundingboxes that where detected:             % 21.59
    percentage of boundingboxes that where falsely detected:     % 14.60
    net percentage of boundingboxes that where detected correct: % 6.99
    ------------------------------------
    evaluate took 31.699 ms
    250000
    Checking 180 images...
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007333.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007334.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007335.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007336.txt'
    ------------------------------------
    Compares:           13174 
    Detected BB's:      955
    GroundTruth BB's:   2126
    False positives:    118
    percentage of boundingboxes that where detected:             % 44.92
    percentage of boundingboxes that where falsely detected:     % 12.36
    net percentage of boundingboxes that where detected correct: % 32.56
    ------------------------------------
    evaluate took 56.532 ms
    260000
    Checking 180 images...
    float division by zero
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007333.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007334.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007335.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007336.txt'
    ------------------------------------
    Compares:           7082 
    Detected BB's:      587
    GroundTruth BB's:   2126
    False positives:    85
    percentage of boundingboxes that where detected:             % 27.61
    percentage of boundingboxes that where falsely detected:     % 14.48
    net percentage of boundingboxes that where detected correct: % 13.13
    ------------------------------------
    evaluate took 38.182 ms
    270000
    Checking 180 images...
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007333.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007334.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007335.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007336.txt'
    ------------------------------------
    Compares:           6453 
    Detected BB's:      578
    GroundTruth BB's:   2126
    False positives:    71
    percentage of boundingboxes that where detected:             % 27.19
    percentage of boundingboxes that where falsely detected:     % 12.28
    net percentage of boundingboxes that where detected correct: % 14.90
    ------------------------------------
    evaluate took 37.485 ms
    280000
    Checking 180 images...
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007333.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007334.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007335.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007336.txt'
    ------------------------------------
    Compares:           5365 
    Detected BB's:      501
    GroundTruth BB's:   2126
    False positives:    55
    percentage of boundingboxes that where detected:             % 23.57
    percentage of boundingboxes that where falsely detected:     % 10.98
    net percentage of boundingboxes that where detected correct: % 12.59
    ------------------------------------
    evaluate took 34.915 ms
    290000
    Checking 180 images...
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007333.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007334.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007335.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007336.txt'
    ------------------------------------
    Compares:           7471 
    Detected BB's:      636
    GroundTruth BB's:   2126
    False positives:    78
    percentage of boundingboxes that where detected:             % 29.92
    percentage of boundingboxes that where falsely detected:     % 12.26
    net percentage of boundingboxes that where detected correct: % 17.65
    ------------------------------------
    evaluate took 40.022 ms
    300000
    Checking 180 images...
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007333.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007334.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007335.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007336.txt'
    ------------------------------------
    Compares:           2961 
    Detected BB's:      313
    GroundTruth BB's:   2126
    False positives:    37
    percentage of boundingboxes that where detected:             % 14.72
    percentage of boundingboxes that where falsely detected:     % 11.82
    net percentage of boundingboxes that where detected correct: % 2.90
    ------------------------------------
    evaluate took 25.979 ms
    310000
    Checking 180 images...
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007333.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007334.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007335.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007336.txt'
    ------------------------------------
    Compares:           6361 
    Detected BB's:      574
    GroundTruth BB's:   2126
    False positives:    64
    percentage of boundingboxes that where detected:             % 27.00
    percentage of boundingboxes that where falsely detected:     % 11.15
    net percentage of boundingboxes that where detected correct: % 15.85
    ------------------------------------
    evaluate took 36.595 ms
    320000
    Checking 180 images...
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007333.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007334.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007335.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007336.txt'
    ------------------------------------
    Compares:           4072 
    Detected BB's:      409
    GroundTruth BB's:   2126
    False positives:    46
    percentage of boundingboxes that where detected:             % 19.24
    percentage of boundingboxes that where falsely detected:     % 11.25
    net percentage of boundingboxes that where detected correct: % 7.99
    ------------------------------------
    evaluate took 29.761 ms
    330000
    Checking 180 images...
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007333.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007334.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007335.txt'
    [Errno 2] No such file or directory: '/data/urbinn/darknet/gtconverted/007336.txt'
    float division by zero
    ------------------------------------
    Compares:           7475 
    Detected BB's:      637
    GroundTruth BB's:   2126
    False positives:    65
    percentage of boundingboxes that where detected:             % 29.96
    percentage of boundingboxes that where falsely detected:     % 10.20
    net percentage of boundingboxes that where detected correct: % 19.76
    ------------------------------------
    evaluate took 40.634 ms



```python
import matplotlib.pyplot as plt
import numpy as np

def make_plot():
    corrected_bbss = np.array(bbss) - np.array(false_poss)
    avg_fal_pos = sum(false_poss)/len(false_poss)
    avg_dect = sum(corrected_bbss)/len(corrected_bbss)

    ''' Baseline '''
    plt.plot(batches, gt_bbss, 'y-')

    plt.plot(batches, bbss, 'g-', label='Detected Boundingboxes')
    plt.plot(batches, false_poss, 'r-', label='False positives')
    plt.plot(batches, corrected_bbss, 'b-', label='Real Detected Boundingboxes')
    plt.plot(batches, corrected_bbss, 'bo')
    plt.plot((batches[-1], batches[0]), (avg_fal_pos, avg_fal_pos), label='Avg. False positives')
    plt.plot((batches[-1], batches[0]), (avg_dect, avg_dect), label='Avg. real Detections')


    ''' Set size of plot '''

    plt.rcParams["figure.figsize"] = [30, 12]

    ''' Add some legend'''
    plt.xlabel("# of trained batches")
    plt.ylabel("# of detected bounding boxes")
    plt.legend()
    plt.show()
```


```python
make_plot()
```


```python
make_plot()
```


![png](output_3_0.png)



```python
plt.rcParams["figure.figsize"] = [30, 12]

for detected_classes in total_classes:
    plt.plot(CLASSES, detected_classes, 'bo')
    plt.show()
```


![png](output_4_0.png)



    ---------------------------------------------------------------------------

    KeyboardInterrupt                         Traceback (most recent call last)

    <ipython-input-3-7e9b63adfa18> in <module>()
          3 for detected_classes in total_classes:
          4     plt.plot(CLASSES, detected_classes, 'bo')
    ----> 5     plt.show()
    

    /opt/jupyterhub/anaconda/lib/python3.6/site-packages/matplotlib/pyplot.py in show(*args, **kw)
        249     """
        250     global _show
    --> 251     return _show(*args, **kw)
        252 
        253 


    /opt/jupyterhub/anaconda/lib/python3.6/site-packages/ipykernel/pylab/backend_inline.py in show(close, block)
         34     try:
         35         for figure_manager in Gcf.get_all_fig_managers():
    ---> 36             display(figure_manager.canvas.figure)
         37     finally:
         38         show._to_draw = []


    /opt/jupyterhub/anaconda/lib/python3.6/site-packages/IPython/core/display.py in display(*objs, **kwargs)
        162             publish_display_data(data=obj, metadata=metadata)
        163         else:
    --> 164             format_dict, md_dict = format(obj, include=include, exclude=exclude)
        165             if not format_dict:
        166                 # nothing to display (e.g. _ipython_display_ took over)


    /opt/jupyterhub/anaconda/lib/python3.6/site-packages/IPython/core/formatters.py in format(self, obj, include, exclude)
        143             md = None
        144             try:
    --> 145                 data = formatter(obj)
        146             except:
        147                 # FIXME: log the exception


    <decorator-gen-9> in __call__(self, obj)


    /opt/jupyterhub/anaconda/lib/python3.6/site-packages/IPython/core/formatters.py in catch_format_error(method, self, *args, **kwargs)
        188     """show traceback on failed format call"""
        189     try:
    --> 190         r = method(self, *args, **kwargs)
        191     except NotImplementedError:
        192         # don't warn on NotImplementedErrors


    /opt/jupyterhub/anaconda/lib/python3.6/site-packages/IPython/core/formatters.py in __call__(self, obj)
        305                 pass
        306             else:
    --> 307                 return printer(obj)
        308             # Finally look for special method names
        309             method = get_real_method(obj, self.print_method)


    /opt/jupyterhub/anaconda/lib/python3.6/site-packages/IPython/core/pylabtools.py in <lambda>(fig)
        238 
        239     if 'png' in formats:
    --> 240         png_formatter.for_type(Figure, lambda fig: print_figure(fig, 'png', **kwargs))
        241     if 'retina' in formats or 'png2x' in formats:
        242         png_formatter.for_type(Figure, lambda fig: retina_figure(fig, **kwargs))


    /opt/jupyterhub/anaconda/lib/python3.6/site-packages/IPython/core/pylabtools.py in print_figure(fig, fmt, bbox_inches, **kwargs)
        122 
        123     bytes_io = BytesIO()
    --> 124     fig.canvas.print_figure(bytes_io, **kw)
        125     data = bytes_io.getvalue()
        126     if fmt == 'svg':


    /opt/jupyterhub/anaconda/lib/python3.6/site-packages/matplotlib/backend_bases.py in print_figure(self, filename, dpi, facecolor, edgecolor, orientation, format, **kwargs)
       2206                     orientation=orientation,
       2207                     dryrun=True,
    -> 2208                     **kwargs)
       2209                 renderer = self.figure._cachedRenderer
       2210                 bbox_inches = self.figure.get_tightbbox(renderer)


    /opt/jupyterhub/anaconda/lib/python3.6/site-packages/matplotlib/backends/backend_agg.py in print_png(self, filename_or_obj, *args, **kwargs)
        524         try:
        525             _png.write_png(renderer._renderer, filename_or_obj,
    --> 526                            self.figure.dpi, metadata=metadata)
        527         finally:
        528             if close:


    KeyboardInterrupt: 



```python
plt.rcParams["figure.figsize"] = [30, 6]
plt.xticks(rotation='vertical')
corrected_bbss = np.array(total_gt_classes[25]) - np.array(total_detected_classes[25])
avg_dect = sum(total_detected_classes[25]) / len(total_detected_classes[25])
avg_gt = sum(total_gt_classes[25]) / len(total_gt_classes[25])

plt.ylim(0,50)
plt.plot(CLASSES, total_gt_classes[25], 'ro')
plt.plot(CLASSES, total_detected_classes[25], 'bo')
plt.plot(CLASSES, corrected_bbss, 'yo')
plt.plot((0, 133), (avg_dect, avg_dect))
plt.plot((0, 133), (avg_gt, avg_gt))
plt.show()
```


![png](output_5_0.png)



```python

```
