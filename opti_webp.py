import os
import sys
from PIL import Image

def get_icon_path():
    """Get the path to the application icon file."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, 'opti_webp.ico')
    else:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'opti_webp.ico')

def count_images(directory, include_subdirs=False):
    image_count = 0
    
    if include_subdirs:
        for root, dirs, files in os.walk(directory):
            for filename in files:
                if filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp", ".heic", ".tiff", ".tif")):
                    image_count += 1
    else:
        image_count = sum([filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp", ".heic", ".tiff", ".tif")) 
                          for filename in os.listdir(directory)])
    
    print(f"Optimizable Images found: {image_count}")
    return image_count

def process_image(img_path, max_width, max_height, delete_original=False, custom_output_dir=None, preserve_structure=True, progress_callback=None, base_directory=None):
    try:
        filename = os.path.basename(img_path)
        directory = os.path.dirname(img_path)
        
        print(f"Processing image: {filename}")
        
        # Step 1: Loading
        img = Image.open(img_path)
        if progress_callback:
            progress_callback(0.2)  # 20% progress for loading
        
        # Calculate aspect ratio
        width, height = img.size
        aspect_ratio = width / height
        
        # Initialize scaling ratios
        width_ratio = float('inf')
        height_ratio = float('inf')
        
        # Calculate ratios only for enabled dimensions
        if max_width:
            width_ratio = max_width / width
        if max_height:
            height_ratio = max_height / height
        
        # Only resize if we have at least one limit and the image exceeds it
        if (max_width and width > max_width) or (max_height and height > max_height):
            # Use the smaller ratio to ensure both dimensions fit within limits
            ratio = min(width_ratio, height_ratio)
            
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            
            # Step 2: Resize the image
            img = img.resize((new_width, new_height), Image.LANCZOS)
            print(f"Resized image from {width}x{height} to {new_width}x{new_height}")
        
        if progress_callback:
            progress_callback(0.4)  # 40% progress after potential resize

        # Determine where to save the files
        temp_dir = directory  # For temporary resized PNG
        
        # If custom output directory is specified, use it for WebP output
        if custom_output_dir:
            # Default output directory is the custom output directory
            output_dir = custom_output_dir
            
            # If preserving structure and we're not in the base directory
            if preserve_structure and base_directory is not None and directory != base_directory:
                # Get the path relative to the base directory
                rel_path = os.path.relpath(directory, base_directory)
                output_dir = os.path.join(custom_output_dir, rel_path)
                os.makedirs(output_dir, exist_ok=True)
        else:
            output_dir = directory

        # Step 3: Save as PNG (temporary)
        new_filename = os.path.splitext(filename)[0] + "_resized.png"
        new_path = os.path.join(temp_dir, new_filename)
        img.save(new_path, "PNG", optimize=True)
        print(f"Saved resized image as: {new_filename}")
        
        if progress_callback:
            progress_callback(0.6)  # 60% progress after saving PNG

        # Step 4: Convert to WebP
        webp_filename = os.path.splitext(filename)[0] + ".webp"
        webp_path = os.path.join(output_dir, webp_filename)
        img.save(webp_path, "WEBP")
        print(f"Converted image to WebP: {webp_filename}")
        
        if progress_callback:
            progress_callback(0.8)  # 80% progress after WebP conversion

        # Step 5: Cleanup - Delete resized PNG file
        os.remove(new_path)
        print(f"Deleted resized image: {new_filename}")
        
        # Delete original file if option is selected
        if delete_original:
            os.remove(img_path)
            print(f"Deleted original image: {filename}")
        
        if progress_callback:
            progress_callback(1.0)  # 100% progress after cleanup
            
        return True
    
    except Exception as e:
        print(f"An error occurred while processing image {filename}: {e}")
        return False

def resize_and_convert(directory, max_width, max_height, delete_original=False, process_subdirs=False, use_custom_output=False, custom_output_dir=None, preserve_structure=True, progress_callback=None):
    image_count = count_images(directory, process_subdirs)
    if image_count == 0:
        print("No optimizable images found.")
        return

    print(f"Processing images in directory: {directory}")
    print(f"Using max width: {max_width}, max height: {max_height}")
    print(f"Processing subdirectories: {'Yes' if process_subdirs else 'No'}")
    
    if use_custom_output and custom_output_dir:
        print(f"Saving all WebP images to: {custom_output_dir}")
        print(f"Preserving folder structure: {'Yes' if preserve_structure else 'No'}")
        # Create output directory if it doesn't exist
        os.makedirs(custom_output_dir, exist_ok=True)
    
    processed_count = 0
    
    # Use the input directory as the base for relative paths
    base_directory = directory
    
    if process_subdirs:
        # Process all subdirectories
        for root, dirs, files in os.walk(directory):
            for filename in files:
                if filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp", ".heic", ".tiff", ".tif")):
                    img_path = os.path.join(root, filename)
                    if process_image(img_path, max_width, max_height, delete_original, 
                                     custom_output_dir if use_custom_output else None, 
                                     preserve_structure, progress_callback, base_directory):
                        processed_count += 1
    else:
        # Process only the selected directory
        for filename in os.listdir(directory):
            if filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp", ".heic", ".tiff", ".tif")):
                img_path = os.path.join(directory, filename)
                if process_image(img_path, max_width, max_height, delete_original, 
                                 custom_output_dir if use_custom_output else None, 
                                 preserve_structure, progress_callback, base_directory):
                    processed_count += 1
    
    print(f"Successfully processed {processed_count} out of {image_count} images.")
