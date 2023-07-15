import cv2
import numpy as np
from scipy import ndimage
from PIL import ImageFont, ImageDraw, Image, ImageTk
from color import Color
import tkinter as tk
import threading
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as viz_utils
import tensorflow as tf

colormap = cv2.COLORMAP_BONE
model = tf.saved_model.load("../Tensorflow/workspace/models/efficient_dice/export/saved_model")
label_map_path = '../Tensorflow/workspace/annotations/label_map.pbtxt'
label_map = label_map_util.load_labelmap(label_map_path)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=6)
category_index = label_map_util.create_category_index(categories)

class Dice:
    x: int
    y: int
    dots: int
    
    def __init__(self, dots: int, x: int, y: int):
        self.x = x
        self.y = y
        self.dots = dots

def display(n: str, k: any):
    # Apply a color map to the image before displaying it
    pil_image = Image.fromarray(k)
    
    root = tk.Tk()
    
    root.attributes('-topmost', 1)
    
    tk_image = ImageTk.PhotoImage(pil_image)
    label = tk.Label(root, image=tk_image, name=n.lower())
    label.image = tk_image  # Keep a reference to the image
    label.pack()
    
    root.after(2000, root.destroy)
    
    root.mainloop()
    
def run_inference_for_single_image(model, image):
    image = np.asarray(image)
    # The input needs to be a tensor.
    input_tensor = tf.convert_to_tensor(image)
    # The model expects a batch of images, so add an axis with `tf.newaxis`.
    input_tensor = input_tensor[tf.newaxis,...]

    # Run inference
    output_dict = model(input_tensor)

    # All outputs are batches tensors.
    # Convert to numpy arrays, and take index [0] to remove the batch dimension.
    # We're only interested in the first num_detections.
    num_detections = int(output_dict.pop('num_detections'))
    output_dict = {key:value[0, :num_detections].numpy() 
                   for key,value in output_dict.items()}
    output_dict['num_detections'] = num_detections

    # detection_classes should be ints.
    output_dict['detection_classes'] = output_dict['detection_classes'].astype(np.int64)
   
    return output_dict

def display_dice(image_path):
    image_np = cv2.imread(image_path)
    image_np = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
    output_dict = run_inference_for_single_image(model, image_np)
    
    viz_utils.visualize_boxes_and_labels_on_image_array(
        image_np,
        output_dict['detection_boxes'],
        output_dict['detection_classes'],
        output_dict['detection_scores'],
        category_index,
        instance_masks=output_dict.get('detection_masks_reframed', None),
        use_normalized_coordinates=True,
        line_thickness=2)

    # Create a list to store the Dice objects
    dice_list = []

    # Iterate over the detected boxes and classes
    for i in range(output_dict['num_detections']):
        # Get the coordinates of the box
        ymin, xmin, ymax, xmax = output_dict['detection_boxes'][i]

        # Calculate the center of the box
        x = (xmin + xmax) / 2
        y = (ymin + ymax) / 2

        # Get the number of dots on the dice from the class
        dots = output_dict['detection_classes'][i]

        # Create a Dice object and add it to the list
        dice = Dice(dots, x, y)
        dice_list.append(dice)

    # Convert the image back to BGR color space
    image_np = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)

    # Display the image with detections
    threading.Thread(target=display, args=("Detections", image_np)).start()

    return dice_list