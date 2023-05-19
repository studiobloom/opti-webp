import os
import tkinter as tk
from tkinter import filedialog, simpledialog
from PIL import Image

def display_initial_message():
    print("Opti-WebP - Image Optimization Tool")
    print("Opti-WebP will bulk resize, compress and convert non WebP images to an optimized WebP final version.")
    print("Created by John Large aka bloom")
    print("Website: https://studiobloom.xyz")
    print("If this tool helps you, please consider donating:\n$studiobloomxyz on cash app, paypal.me/studiobloomxyz\nBTC @ 33bhGfzcKekYh8oB31Jzv5FYUkdahyC3eA\nETH @ 0xD974b9ab6e897d1128F2aFe98Aa172dE8180D27E")
    print("\n\n")
    print("Choose the directory of the image(s) to be optimized.\nProceed through the following window prompts.")

def select_directory():
    root = tk.Tk()
    root.withdraw()
    directory = filedialog.askdirectory()
    return directory

class MaxDimensionSizeDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Max Dimension Size")
        self.geometry("300x250")
        self.resizable(False, False)

        self.max_dimension_size = None
        self.create_widgets()

    def create_widgets(self):
        label = tk.Label(self, text="Limit max width/height of image(s).\nAspect Ratio will remain locked.\n(between 500px-4000px is suggested)\nEnter the maximum dimension size:")
        label.pack(pady=10)

        self.entry = tk.Entry(self)
        self.entry.pack()

        button = tk.Button(self, text="OK", command=self.set_max_dimension_size)
        button.pack(pady=10)
        
    def set_max_dimension_size(self):
        try:
            self.max_dimension_size = int(self.entry.get())
        except ValueError:
            pass
        self.destroy()
        
def get_max_dimension_size():
    root = tk.Tk()
    root.withdraw()
    dialog = MaxDimensionSizeDialog(root)
    root.wait_window(dialog)
    return dialog.max_dimension_size

def count_images(directory):
    image_count = sum([filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp", ".heic", ".tiff", ".tif")) for filename in os.listdir(directory)])
    print(f"Optimizable Images found in directory: {image_count}")
    return image_count

def resize_and_convert(directory, max_dimension_size):
    image_count = count_images(directory)
    if image_count == 0:
        print("No optimizable images found.")
        return

    print(f"Processing images in directory: {directory}")
    for filename in os.listdir(directory):
        try:
            if filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp", ".heic", ".tiff", ".tif")):
                print(f"Processing image: {filename}")
                img = Image.open(os.path.join(directory, filename))
                img.thumbnail((max_dimension_size, max_dimension_size))

                # Save as PNG
                new_filename = os.path.splitext(filename)[0] + "_resized.png"
                img.save(os.path.join(directory, new_filename), "PNG", optimize=True)
                print(f"Saved resized image as: {new_filename}")

                # Convert to WebP
                webp_filename = os.path.splitext(filename)[0] + ".webp"
                img.save(os.path.join(directory, webp_filename), "WEBP")
                print(f"Converted image to WebP: {webp_filename}")

                # Delete resized PNG file
                os.remove(os.path.join(directory, new_filename))
                print(f"Deleted resized image: {new_filename}")

        except Exception as e:
            print(f"An error occurred while processing image {filename}: {e}")

if __name__ == "__main__":
    display_initial_message()
    directory = select_directory()
    if directory:
        max_dimension_size = get_max_dimension_size()
        if max_dimension_size:
            resize_and_convert(directory, max_dimension_size)
    
    # Keep the command window open and prompt the user to restart
    while True:
        user_input = input("Your conversion is now complete, thank you for using Opti-WebP:)\nType 'r' to run the script again, or press enter to exit:")
        if user_input.lower() == "r":
            display_initial_message()
            directory = select_directory()
            if directory:
                max_dimension_size = get_max_dimension_size()
                if max_dimension_size:
                    resize_and_convert(directory, max_dimension_size)
        else:
            break
