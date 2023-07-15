import time
import cv2
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyautogui
import pygetwindow as gw
from enum import Enum

size_fraction = .48
center_x_fraction = .49
center_y_fraction = 0.40
factor = 1.6

def relative_to_absolute(driver, element_id, x_ratio, y_ratio):
    # Find the element
    element = driver.find_element(By.ID, element_id)

    # Get the size of the element
    element_size = element.size

    # Calculate the absolute coordinates
    absolute_x = element_size['width'] * x_ratio
    absolute_y = element_size['height'] * y_ratio

    return absolute_x, absolute_y

def calculate_click_coordinates(driver, element_id, x_ratio, y_ratio):
    # Find the element
    element = driver.find_element(By.ID, element_id)

    # Get current width and height
    original_width = driver.execute_script("return arguments[0].offsetWidth", element)
    original_height = driver.execute_script("return arguments[0].offsetHeight", element)

    # Calculate the size of the box
    box_size = int(min(original_width, original_height) * size_fraction)

    # Calculate the center of the box
    center_x = int(original_width * center_x_fraction)
    center_y = int(original_height * center_y_fraction)

    # Calculate the start and end points of the box
    start_x = center_x - box_size // 2
    end_x = start_x + box_size
    start_y = center_y - box_size // 2
    end_y = start_y + box_size

    # Ensure the box is within the image
    start_x = max(0, start_x)
    start_y = max(0, start_y)
    end_x = min(original_width, end_x)
    end_y = min(original_height, end_y)

    # Calculate click coordinates based on the box dimensions
    click_x = start_x + (end_x - start_x) * x_ratio
    click_y = start_y + (end_y - start_y) * y_ratio

    return click_x, click_y

def click_element(driver, element_id, click_x, click_y):
    # Get the position of the element
    element_location = driver.find_element(By.ID, element_id).location

    # Get the position of the browser window
    window = gw.getWindowsWithTitle(driver.title)[0]

    # Get the scroll position
    scroll_x = driver.execute_script('return window.pageXOffset')
    scroll_y = driver.execute_script('return window.pageYOffset')

    # Get the size of the browser window's border and title bar
    border_width = window.width - driver.execute_script('return window.innerWidth')
    title_bar_height = window.height - driver.execute_script('return window.outerHeight')

    # Calculate the absolute coordinates of the click
    absolute_x = window.left + border_width + element_location['x'] + click_x - scroll_x
    absolute_y = window.top + title_bar_height + element_location['y'] + click_y - scroll_y

    # Perform the click using pyautogui
    pyautogui.moveTo(absolute_x, absolute_y)
    pyautogui.click()
    
def click_dice(driver, x, y):
    click_x, click_y = calculate_click_coordinates(driver, 'appletContainer', x, y)
    click_element(driver, 'appletContainer', click_x, click_y)
    
def click_slot(driver, slot: int = 0):
    click_x, click_y = calculate_click_coordinates(driver, 'appletContainer', 0.16 * (slot + 1), 1.09)
    click_element(driver, 'appletContainer', click_x, click_y)
    
def roll(driver):
    x, y = relative_to_absolute(driver, 'appletContainer', 0.48, 0.92)
    click_element(driver, 'appletContainer', x, y)
    
def click_row(driver, idx: int = 0):
    if idx >= 6:
        idx += 1
    x, y = relative_to_absolute(driver, 'appletContainer', 0.22, 0.15 + 0.055 * (idx + 1))
    if idx > 6:
        y = y * 0.97
    click_element(driver, 'appletContainer', x, y)

def take_dice_screenshot(driver: WebDriver):
    element_id = "#canvas"
    appletcontainer_id = "appletContainer"
    
    # Find elements
    element = driver.find_element(By.ID, element_id)
    appletcontainer = driver.find_element(By.ID, appletcontainer_id)

    # Get current width and height
    original_width = driver.execute_script("return arguments[0].offsetWidth", element)
    original_height = driver.execute_script("return arguments[0].offsetHeight", element)
    original_appletcontainer_width = driver.execute_script("return arguments[0].offsetWidth", appletcontainer)
    original_appletcontainer_height = driver.execute_script("return arguments[0].offsetHeight", appletcontainer)

    # Resize elements
    driver.execute_script("arguments[0].style.width = '{}px'; arguments[0].style.height = '{}px';".format(original_width*factor, original_height*factor), element)
    driver.execute_script("arguments[0].style.width = '{}px'; arguments[0].style.height = '{}px';".format(original_appletcontainer_width*factor, original_appletcontainer_height*factor), appletcontainer)

    # Take screenshot
    element.screenshot(f'data/{element_id}_screenshot.png')

    # Reset the width and height
    driver.execute_script("arguments[0].style.width = '{}px'; arguments[0].style.height = '{}px';".format(original_width, original_height), element)
    driver.execute_script("arguments[0].style.width = '{}px'; arguments[0].style.height = '{}px';".format(original_appletcontainer_width, original_appletcontainer_height), appletcontainer)

    # Load the image
    img = cv2.imread(f'data/{element_id}_screenshot.png')

    # Get the dimensions of the image
    height, width, _ = img.shape

    # Calculate the size of the box
    box_size = int(min(height, width) * size_fraction)

    # Calculate the center of the box
    center_x = int(width * center_x_fraction)
    center_y = int(height * center_y_fraction)

    # Calculate the start and end points of the box
    start_x = center_x - box_size // 2
    end_x = start_x + box_size
    start_y = center_y - box_size // 2
    end_y = start_y + box_size

    # Ensure the box is within the image
    start_x = max(0, start_x)
    start_y = max(0, start_y)
    end_x = min(width, end_x)
    end_y = min(height, end_y)

    # Crop the image
    crop_img = img[start_y:end_y, start_x:end_x]

    # Save the cropped image
    cv2.imwrite('data/cropped_screenshot.png', crop_img)

class Location(Enum):
    CENTER = 'center'
    TOP = 'top'
    LEFT = 'left'
    RIGHT = 'right'
    BOTTOM = 'bottom'
    BOTTOM_LEFT = 'bottom_left'
    BOTTOM_RIGHT = 'bottom_right'
    TOP_LEFT = 'top_left'
    TOP_RIGHT = 'top_right'