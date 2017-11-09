

```python
import json
import time
import operator

''' CONFIG 
YOLO_JSON = location of the json output by the run_yolo.py script
KITTI_GT = Location of folder containing the kitty GroundTruth .txt filed
ERROR = minimal IOU for an boject to be valid 'recognized' 
     ------ '''

YOLO_JSON = '/data/urbinn/yolo-chris/darknet/output/1507719473/objects.json'
KITTI_GT = '/data/urbinn/datasets/kitti/KITTI_Training_Labels/training/label_2/{}'
IOU = 0.95
errors = ops = bbs = 0


''' prints the config '''
def print_cfg():
    print('YOLO_JSON: {}\nKITTI_GT: {}\nERROR: {}\n'.format(YOLO_JSON,KITTI_GT,IOU))

''' Decorator method for timing a method '''
def timing(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        print('%s took %0.3f ms' % (f.__name__, (time2-time1)*1000.0))
        return ret
    return wrap

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


''' Datamodel for handeling boundingboxes '''
class BoundingBox:
    name = ''
    x1 = y1 = x2 = y2 = 0

    def __init__(self, x1, y1, x2, y2, name='-', centre_point=False):
        self.x1 = float(x1)        # X coordinate of BB (lower-left)
        self.y1 = float(y1)       # Y coordinate of BB (lower-left)
        self.x2 = float(x2)       # X coordinate of BB (upper-right)
        self.y2 = float(y2)        # Y coordinate of BB (upper-right)
        self.name = name  # Name (id) of BB

    def get_list(self):
        return [self.x1, self.y1, self.x2, self.y2]

    def __str__(self):
        return '{}: x1:{}, y1:{}, x2:{}, y2:{}'.format(self.name, self.x1, self.y1, self.x2, self.y2)


''' GroundTruth object '''
class GroundTruth:
    bounding_boxes = []

    def __init__(self, gt):
        for line in gt:
            split = line.split(' ')
            ''' convert the x1 x2 params to a bounding box '''
            boundingbox = BoundingBox(split[4], split[5], split[6], split[7], name=split[0])
            self.bounding_boxes.append(boundingbox)

    def check_boundingbox_iou(self, bb):
        ''' functionality to compare BB tot he set of bb's in the Ground Truth'''
        global bbs
        bbs += 1
        max_result = 0.0
        bb = bb.get_list()

        for index, gt_bb in enumerate(self.bounding_boxes):
            global ops
            ops += 1
            result = iou( bb, gt_bb.get_list())
            if result > max_result:
                max_result = result

        if max_result < IOU:
            global errors
            errors += 1


@timing
def evaluate():
    with open(YOLO_JSON) as results:
        results = json.loads(results.read())
        print('Checking {} images...'.format(len(results)))
        for result in results:
            image = result.pop(0).replace('png', 'txt')
            current_gt = KITTI_GT.format(image)
            with open(current_gt) as gt_results:
                # creates new gt object with info from .txt
                ground_truth = GroundTruth(gt_results)
                for bb in result:
                    bb = BoundingBox(bb[2][0], bb[2][1], bb[2][2], bb[2][3], bb[0])
                    ground_truth.check_boundingbox_iou(bb)

print_cfg()
evaluate()
print(' Errors: {} \n Compares: {} \n Checked bounding boxes: {}'.format(errors, ops, bbs))
print('percentage of boundingboxes that where not found:   % {:.2f}'.format(errors/bbs*100))

```


```python

```
