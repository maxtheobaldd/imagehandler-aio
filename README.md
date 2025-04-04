# Image Handler AIO
This is a tool I made to make my workflow more streamlined when working with images. This tool is designed to work on Windows and may not work correctly out-of-the-box on MacOS or Linux.
This tool will:
 - Accept a folder containing images (.jpg, .jpeg, .png, .bmp, .gif, .tiff are suppported)
 - Crop them slightly when requested to enlarge the product itself (12% from each side)
 - Replace transparency in PNG images with white background
 - Resize images to a specified width and height
 - Save the processed images as .JPG files in a new folder named "Processed" in the input folder

## Pre-compiled Binaries for Windows

Click releases on the right-hand side to find a standalone exe

## Running from Source on Windows

 1. Download and install Python (ensure that Python.exe is added to PATH during installation)
 2. Clone this repository into a folder using `git clone` or download as a zip by clicking the Code button at the top of this page.
 3. Open the repository folder in your Terminal (on Windows 11, you can right click inside the folder in Explorer and click open in terminal)
 4. Run `pip install -r requirements.txt` to install the dependencies
 5. You should now be able to run Image Handler with `python imagehandler.py`

## Running on Linux

For most distros, the intructions above for running from source will work fine. Ensure you have `python`, `pip` and `git` installed through your package manager.

For Arch-based distros, python packages are packaged by arch and can be installed using `pacman` instead:

`sudo pacman -S python-pillow python-tqdm`