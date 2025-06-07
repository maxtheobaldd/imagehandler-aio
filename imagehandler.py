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
 - Save the processed images as .jpg files in a new folder named "Processed" in the input folder
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
            output_path = os.path.join(output_dir, sanitize_filename(os.path.splitext(filename)[0]) + ".jpg")  # Enforce .jpg
            crop_image_by_12_percent(input_path, output_path)
            pbar.update(1)  # Update progress bar
    
    print("Cropping completed!")

def resize_images(input_dir, output_dir, width, height, total_images):
    """Resize images and save them as .jpg with tqdm progress bar."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Get list of valid image files
    image_files = [f for f in os.listdir(input_dir) if f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp"))]
    
    # Use tqdm for progress visualization
    with tqdm(total=len(image_files), desc="Resizing", unit="image") as pbar:
        for filename in image_files:
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, sanitize_filename(os.path.splitext(filename)[0]) + ".jpg")  # Enforce .jpg

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

    # This variable will store the original input directory to correctly place the "Processed" folder
    # and to serve as the source for cropping if enabled.
    original_input_directory_for_paths = input_directory
    cropped_directory = None # Initialize cropped_directory

    # Count total images to process from the original selected directory
    total_images_in_source = len([
        f for f in os.listdir(original_input_directory_for_paths) 
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp"))
    ])
    if total_images_in_source == 0:
        print("No valid images found in the selected folder. Exiting.")
        exit()

    while True:
        # Updated prompt for clarity on cropping
        crop_choice = input("Do you want to crop images (12% from each side, square aspect) before resizing? (yes/no): ").strip().lower()
        if crop_choice in ("yes", "no"):
            break
        print("Invalid input. Please enter 'yes' or 'no'.")

    # This is the directory that will be used as input for resizing operations.
    # It's either the original input_directory or the cropped_directory.
    current_source_dir_for_resize = original_input_directory_for_paths

    if crop_choice == "yes":
        # Using a more descriptive temporary folder name
        cropped_directory = os.path.join(original_input_directory_for_paths, "Cropped_Temp_Images") 
        print(f"Cropping images from '{original_input_directory_for_paths}' into temporary folder: '{cropped_directory}'")
        # Pass total_images_in_source for progress bar consistency if functions were to use it
        batch_crop_images(original_input_directory_for_paths, cropped_directory, total_images_in_source)
        current_source_dir_for_resize = cropped_directory  # Update input directory for resizing

    # Define the base directory where "Processed" subfolders will be created
    base_processed_dir = os.path.join(original_input_directory_for_paths, "Processed")
    processed_paths_list = [] # To store paths of successfully processed batches

    while True:
        two_batches_choice = input("Do you want to create two batches of images with different dimensions? (yes/no): ").strip().lower()
        if two_batches_choice in ("yes", "no"):
            break
        print("Invalid input. Please enter 'yes' or 'no'.")

    if two_batches_choice == "yes":
        # Batch 1
        print("\n--- Configuring First Batch ---")
        try:
            width1 = int(input("Enter target width for the first batch: "))
            height1 = int(input("Enter target height for the first batch: "))
            if width1 <= 0 or height1 <= 0: raise ValueError("Dimensions must be positive integers.")
            if width1 > 10000 or height1 > 10000: raise ValueError("Dimensions too large (max 10000x10000).")
        except ValueError as e:
            print(f"Invalid input for first batch: {e}. Exiting.")
            if cropped_directory and os.path.exists(cropped_directory): shutil.rmtree(cropped_directory)
            exit()
        
        output_directory1 = os.path.join(base_processed_dir, f"{width1}x") # Folder name based on width
        print(f"First batch: Resizing images from '{current_source_dir_for_resize}' to {width1}x{height1}, saving to '{output_directory1}'")
        resize_images(current_source_dir_for_resize, output_directory1, width1, height1, total_images_in_source)
        processed_paths_list.append(output_directory1)

        # Batch 2
        print("\n--- Configuring Second Batch ---")
        try:
            width2 = int(input("Enter target width for the second batch: "))
            height2 = int(input("Enter target height for the second batch: "))
            if width2 <= 0 or height2 <= 0: raise ValueError("Dimensions must be positive integers.")
            if width2 > 10000 or height2 > 10000: raise ValueError("Dimensions too large (max 10000x10000).")
        except ValueError as e:
            print(f"Invalid input for second batch: {e}. Exiting.")
            if cropped_directory and os.path.exists(cropped_directory): shutil.rmtree(cropped_directory)
            exit()

        output_directory2 = os.path.join(base_processed_dir, f"{width2}x") # Folder name based on width
        print(f"Second batch: Resizing images from '{current_source_dir_for_resize}' to {width2}x{height2}, saving to '{output_directory2}'")
        resize_images(current_source_dir_for_resize, output_directory2, width2, height2, total_images_in_source)
        processed_paths_list.append(output_directory2)
        
    else:  # Single batch
        print("\n--- Configuring Single Batch ---")
        try:
            width = int(input("Enter target width: "))
            height = int(input("Enter target height: "))
            if width <= 0 or height <= 0: raise ValueError("Dimensions must be positive integers.")
            if width > 10000 or height > 10000: raise ValueError("Dimensions too large (max 10000x10000).")
        except ValueError as e:
            print(f"Invalid input: {e}. Exiting.")
            if cropped_directory and os.path.exists(cropped_directory): shutil.rmtree(cropped_directory)
            exit()

        output_directory_single = os.path.join(base_processed_dir, f"{width}x") # Folder name based on width
        print(f"Single batch: Resizing images from '{current_source_dir_for_resize}' to {width}x{height}, saving to '{output_directory_single}'")
        resize_images(current_source_dir_for_resize, output_directory_single, width, height, total_images_in_source)
        processed_paths_list.append(output_directory_single)

    if cropped_directory and os.path.exists(cropped_directory): # Check existence before attempting to remove
        print(f"\nCleaning up temporary cropped directory: {cropped_directory}")
        shutil.rmtree(cropped_directory)

    if processed_paths_list:
        print("\nProcessing completed!")
        print("Processed images are saved in the following location(s):")
        for path in processed_paths_list:
            print(f" - {path}")
    else:
        # This case should ideally not be reached if there were images and no errors leading to exit.
        print("\nNo images were processed or processing was interrupted.") 
    
    print("\nScript finished. Press Enter to exit.") # Changed from time.sleep(1)
    input() # Waits for user to press Enter before closing