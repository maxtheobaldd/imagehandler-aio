import os
import time
import shutil
import re
from PIL import Image
from tkinter import Tk, filedialog
from tqdm import tqdm

ascii_art = r"""
  _____                                _    _                 _ _                      _____ ____  
 |_   _|                              | |  | |               | | |               /\   |_   _/ __ \ 
   | |  _ __ ___   __ _  __ _  ___    | |__| | __ _ _ __   __| | | ___ _ __     /  \    | || |  | |
   | | | '_ ` _ \ / _` |/ _` |/ _ \   |  __  |/ _` | '_ \ / _` | |/ _ \ '__|   / /\ \   | || |  | |
  _| |_| | | | | | (_| | (_| |  __/   | |  | | (_| | | | | (_| | |  __/ |     / ____ \ _| || |__| |
 |_____|_| |_| |_|\__,_|\__, |\___|   |_|  |_|\__,_|_| |_|\__,_|_|\___|_|    /_/    \_\_____\____/ 
                         __/ |                                                                     
                        |___/                                                                      

Image Handler All-in-One V1.2 by Max

This script will:
 - Accept a folder containing images (.jpg, .jpeg, .png, .bmp, .gif, .tiff, .webp are suppported)
 - Crop them slightly when requested to enlarge the product itself (12% from each side)
 - Replace transparency in PNG images with white background
 - Resize images to a specified width and height
 - Save the processed images as .JPG files in a new folder named "Processed" in the input folder
"""
print(ascii_art)

while True:
    if input("Press Enter to continue...") == "":
        break

def select_folder():
    """Open a dialog to select a folder and return its path."""
    root = Tk()
    root.withdraw()  # Hide the main Tkinter window
    folder_selected = filedialog.askdirectory(title="Select a folder")
    return folder_selected

def sanitize_filename(filename):
    """Remove invalid characters from a filename."""
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def crop_image_by_12_percent(image_path, output_path):
    """Crop the image by 12% and save as a new file."""
    img = Image.open(image_path).convert("RGBA")
    white_background = Image.new("RGB", img.size, (255, 255, 255))
    if img.mode == "RGBA":
        white_background.paste(img, mask=img.split()[3])  # Use alpha channel as mask
    else:
        white_background.paste(img)  # No transparency, paste directly
    width, height = white_background.size
    square_size = min(width, height) * 0.88  # Ensure square crop
    left = (width - square_size) / 2
    top = (height - square_size) / 2
    right = (width + square_size) / 2
    bottom = (height + square_size) / 2
    cropped_img = white_background.crop((left, top, right, bottom))
    cropped_img.save(output_path, "JPEG")  # Save as JPEG format

def batch_crop_images(input_dir, output_dir, total_images):
    """Batch crop images in a directory with tqdm progress bar."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Get list of valid image files
    image_files = [f for f in os.listdir(input_dir) if f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp"))]
    
    # Use tqdm for progress visualization
    with tqdm(total=len(image_files), desc="Cropping", unit="image") as pbar:
        for filename in image_files:
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, sanitize_filename(os.path.splitext(filename)[0]) + ".JPG")  # Enforce .JPG
            crop_image_by_12_percent(input_path, output_path)
            pbar.update(1)  # Update progress bar
    
    print("Cropping completed!")

def resize_images(input_dir, output_dir, width, height, total_images):
    """Resize images and save them as .JPG with tqdm progress bar."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Get list of valid image files
    image_files = [f for f in os.listdir(input_dir) if f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp"))]
    
    # Use tqdm for progress visualization
    with tqdm(total=len(image_files), desc="Resizing", unit="image") as pbar:
        for filename in image_files:
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, sanitize_filename(os.path.splitext(filename)[0]) + ".JPG")  # Enforce .JPG

            try:
                with Image.open(input_path) as img:
                    # Ensure RGB mode for .JPG
                    if img.mode == "RGBA":
                        img = img.convert("RGB")  # Convert RGBA to RGB
                    elif img.mode != "RGB":
                        img = img.convert("RGB")  # Convert other modes (e.g., grayscale) to RGB

                    # Resize the image
                    img_resized = img.resize((width, height), Image.Resampling.LANCZOS)
                    img_resized.save(output_path, "JPEG")  # Save as JPEG format
            except Exception as e:
                print(f"Error processing {input_path}: {e}")
                with open("error_log.txt", "a") as log_file:
                    log_file.write(f"Error processing {input_path}: {e}\n")
            finally:
                pbar.update(1)  # Update progress bar
    
    print("Resizing completed!")

if __name__ == "__main__":
    print("Please begin by selecting a folder containing images to process.")
    input_directory = select_folder()
    if not input_directory:
        print("No folder selected. Exiting.")
        exit()

    output_directory = os.path.join(input_directory, "Processed")
    cropped_directory = None

    # Count total images to process
    total_images = len([f for f in os.listdir(input_directory) if f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp"))])
    if total_images == 0:
        print("No valid images found in the selected folder. Exiting.")
        exit()

    while True:
        crop_choice = input("Do you want to crop images before resizing? (yes/no): ").strip().lower()
        if crop_choice in ("yes", "no"):
            break
        print("Invalid input. Please enter 'yes' or 'no'.")

    if crop_choice == "yes":
        cropped_directory = os.path.join(input_directory, "Cropped")
        batch_crop_images(input_directory, cropped_directory, total_images)
        input_directory = cropped_directory  # Update input directory for resizing

    try:
        width = int(input("Enter width: "))
        height = int(input("Enter height: "))
        if width <= 0 or height <= 0:
            raise ValueError("Dimensions must be positive integers.")
        if width > 10000 or height > 10000:  # Arbitrary limit to prevent excessive memory usage
            raise ValueError("Dimensions are too large. Maximum allowed is 10000x10000.")
    except ValueError as e:
        print(f"Invalid input: {e}. Exiting.")
        exit()

    resize_images(input_directory, output_directory, width, height, total_images)

    if cropped_directory:
        shutil.rmtree(cropped_directory)

    print(f"Processing completed! Processed images are saved in: {output_directory}")
    time.sleep(1)