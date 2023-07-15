import os
import time
import cv2
from cv2 import matchTemplate
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from browser import take_dice_screenshot, click_element, Location, click_slot, roll, click_dice, click_row
from log import logger
from detection import display_dice, Dice
import socket
from strat import get_best_option


def check_port(port: str):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', int(port)))
    return result == 0

slots = [None, None, None, None, None]
keep = [False, False, False, False, False]

def add_dice_to_slot(driver, dice, index):
    # Click on the dice to add it to a slot
    click_dice(driver, dice.x, dice.y)
    # Add the dice to the slots list
    slots[index] = dice

def remove_dice_from_slot(driver, slot):
    # Click on the dice to remove it from a slot
    click_slot(driver, slot)
    # Remove the dice from the slots list
    slots[slot] = None
    
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

if __name__ == "__main__":
    display_dice("data/cropped_screenshot.png")
    
    

if __name__ == "__main_":
    port = "9222"
    
    if not check_port(port):
        logger.error(f"No instance is running on port {port}. Please launch Brave with remote debugging on port {port}: \"\\path\\to\\brave.exe --remote-debugging-port={port}\"")
        exit(1)
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")

    webdriver_service = Service(ChromeDriverManager().install())
    
    logger.info(f"Connecting to Brave instance on port: {port}")

    # Connect to the existing instance of Brave
    driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)
    
    logger.info("Successfully connected to the existing instance of Brave")
    
    # calc_driver = webdriver.Chrome(service=webdriver_service)
    # calc_driver.get('http://www-set.win.tue.nl/~wstomv/misc/yahtzee/osyp.php')

    # Go to a website
    # driver.get('https://www.gamepoint.com/nl/roomlist.php?game=partydice&port=0')

    score_card = {
        'Aces': None,
        'Twos': None,
        'Threes': None,
        'Fours': None,
        'Fives': None,
        'Sixes': None,
        'Three of a Kind': None,
        'Four of a Kind': None,
        'Full House': None,
        'Small Straight': None,
        'Large Straight': None,
        'Yahtzee': None,
        'Chance': None,
    }

    while any(value is None for value in score_card.values()):
        
        keep = [False, False, False, False, False]
        slots = [None, None, None, None, None]
        for rollIndex in range(4):
            for i in range(len(slots)):
                if keep[i] == False:
                    slots[i] = None
            
            dicesIsFull = len(list(filter(lambda x: x == True, keep))) >= 5
            
            if not dicesIsFull:
                roll(driver)
                time.sleep(2.5)
                take_dice_screenshot(driver)
        
                logger.info("Screenshot taken")
                
            if not dicesIsFull:
                board_dices = display_dice("data/cropped_screenshot.png")
                
                # Create a list of indices where slots are None
                empty_slot_indices = [i for i, x in enumerate(slots) if x is None]
                
                for i in range(len(empty_slot_indices)):
                    dice = board_dices[i][1]
                    
                    if dice.dots <= 6:
                        slots[empty_slot_indices[i]] = dice
                        print(dice.dots, 'added to slot', empty_slot_indices[i])
            
            print('slots:\t', list(map(lambda s: s.dots, slots)))
            print('keep:\t', keep)
            
            keptDices = []
            notKeptDices = []
            
            for i in range(len(keep)):
                if keep[i] == False:
                    keptDices.append(None)
                    notKeptDices.append(slots[i].dots)
                else:
                    keptDices.append(slots[i].dots)
                    notKeptDices.append(None)
                
            res = get_best_option(
                score_card=score_card,
                d1=notKeptDices[0],
                d2=notKeptDices[1],
                d3=notKeptDices[2],
                d4=notKeptDices[3],
                d5=notKeptDices[4],
                kd1=keptDices[0],
                kd2=keptDices[1],
                kd3=keptDices[2],
                kd4=keptDices[3],
                kd5=keptDices[4],
                rollIndex=min(rollIndex + 1, 3)
            )
            
            if str(res).startswith('Keep'):
                best_option_text = str(res)[5:10]
                print(res)
                result = [None if char == '_' else int(char) for char in list(best_option_text)]
                print('result', result)
                
                for i in range(len(notKeptDices)):
                    if result[i] is not None and int(result[i]) == notKeptDices[i]:
                        click_dice(driver, slots[i].x, slots[i].y)
                        slots[keep.index(False)] = slots[i]
                        keep[keep.index(False)] = True
                        
                for i in range(len(keptDices)):
                    if result[i] is None and keptDices[i] is not None:
                        click_slot(driver, i)
                        keep[i] = False

            else:
                print(str(res))
                for index, key in enumerate(score_card.keys()):
                    if key in str(res):
                        score_card[key] = int(str(res).split(" ")[1])
                        print(score_card[key])
                        click_row(driver, index)
                        break
        
            cv2.waitKey(1000)
            cv2.destroyAllWindows()