import os
import sys
import glob
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import threading
import importlib.util

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Import functions from opti_webp.py
opti_webp_path = resource_path("opti_webp.py")
spec = importlib.util.spec_from_file_location("opti_webp", opti_webp_path)
opti_webp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(opti_webp)

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue") 
HIGHLIGHT_COLOR = "#763ece"

class CustomMessageBox(ctk.CTkToplevel):
    def __init__(self, master, title, message, ask=False):
        super().__init__(master)
        self.overrideredirect(True)
        self.result = None
        
        # Set consistent size and dark background
        self.geometry("400x200")
        self.configure(fg_color="#2B2B2B")
        
        # Create main container with rounded corners and border
        self.container = ctk.CTkFrame(
            self,
            fg_color="#2B2B2B",
            border_color=HIGHLIGHT_COLOR,
            border_width=2,
            corner_radius=10
        )
        self.container.pack(fill="both", expand=True)
        
        # Title Bar with close button
        self.title_bar = ctk.CTkFrame(
            self.container,
            fg_color=HIGHLIGHT_COLOR,
            height=30,
            corner_radius=0
        )
        self.title_bar.pack(fill="x", padx=2, pady=(2, 0))
        
        # Title text
        self.title_label = ctk.CTkLabel(
            self.title_bar, 
            text=title, 
            text_color="white", 
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.title_label.pack(side="left", padx=10, pady=5)
        
        # Close button
        self.close_button = ctk.CTkButton(
            self.title_bar,
            text="×",
            width=40,
            height=20,
            command=self.destroy,
            fg_color="transparent",
            hover_color=self.adjust_color_brightness(HIGHLIGHT_COLOR, -20),
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        )
        self.close_button.pack(side="right", padx=5, pady=2)
        
        # Bindings to allow dragging the window
        self.title_bar.bind("<ButtonPress-1>", self.start_move)
        self.title_bar.bind("<B1-Motion>", self.on_move)
        self.title_label.bind("<ButtonPress-1>", self.start_move)
        self.title_label.bind("<B1-Motion>", self.on_move)
        
        # Message text
        self.message_label = ctk.CTkLabel(
            self.container, 
            text=message, 
            text_color="white", 
            wraplength=360,
            justify="center"
        )
        self.message_label.pack(expand=True, padx=20)
        
        # Button Area
        if ask:
            self.button_frame = ctk.CTkFrame(self.container, fg_color="transparent")
            self.button_frame.pack(fill="x", padx=20, pady=20)
            
            self.yes_button = ctk.CTkButton(
                self.button_frame, 
                text="Yes", 
                width=120,
                fg_color=HIGHLIGHT_COLOR, 
                hover_color=self.adjust_color_brightness(HIGHLIGHT_COLOR, -20),
                command=self.on_yes
            )
            self.yes_button.pack(side="left", expand=True, padx=10)
            
            self.no_button = ctk.CTkButton(
                self.button_frame, 
                text="No", 
                width=120,
                fg_color=HIGHLIGHT_COLOR, 
                hover_color=self.adjust_color_brightness(HIGHLIGHT_COLOR, -20),
                command=self.on_no
            )
            self.no_button.pack(side="right", expand=True, padx=10)
        else:
            self.ok_button = ctk.CTkButton(
                self.container, 
                text="OK", 
                width=120,
                fg_color=HIGHLIGHT_COLOR, 
                hover_color=self.adjust_color_brightness(HIGHLIGHT_COLOR, -20),
                command=self.destroy
            )
            self.ok_button.pack(pady=20)
        
        # Center the popup relative to the master window
        self.update_idletasks()
        x = master.winfo_rootx() + (master.winfo_width() // 2) - (self.winfo_width() // 2)
        y = master.winfo_rooty() + (master.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
        
        self.grab_set()
        self.focus_force()
        self.wait_window()
    
    def adjust_color_brightness(self, color_hex, brightness_offset=0):
        """Adjust the brightness of a hex color"""
        # Convert hex to RGB
        h = color_hex.lstrip('#')
        rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
        
        # Adjust brightness
        rgb_adjusted = [max(0, min(255, val + brightness_offset)) for val in rgb]
        
        # Convert back to hex
        return '#{:02x}{:02x}{:02x}'.format(*rgb_adjusted)

    def start_move(self, event):
        self._offset_x = event.x
        self._offset_y = event.y

    def on_move(self, event):
        x = self.winfo_x() + event.x - self._offset_x
        y = self.winfo_y() + event.y - self._offset_y
        self.geometry(f"+{x}+{y}")

    def on_yes(self):
        self.result = True
        self.destroy()

    def on_no(self):
        self.result = False
        self.destroy()

# Helper functions for custom popups
def custom_showerror(master, title, message):
    CustomMessageBox(master, title, message)
    
def custom_showinfo(master, title, message):
    CustomMessageBox(master, title, message)
    
def custom_askyesno(master, title, message):
    msg_box = CustomMessageBox(master, title, message, ask=True)
    return msg_box.result

class OptiWebpGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("Opti_WebP")
        self.geometry("800x600")
        self.minsize(700, 500)
        
        # Try to set icon
        try:
            icon_path = opti_webp.get_icon_path()
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except Exception:
            pass  # Ignore if icon setting fails
        
        # Variables
        self.selected_directory = ctk.StringVar(value="")
        self.output_directory = ctk.StringVar(value="")
        self.custom_output = ctk.BooleanVar(value=False)
        
        # Link selected_directory to output_directory when custom_output is False
        self.selected_directory.trace_add("write", self._update_output_directory)
        
        self.use_max_width = ctk.BooleanVar(value=True)
        self.use_max_height = ctk.BooleanVar(value=True)
        self.max_width = ctk.IntVar(value=2000)
        self.max_height = ctk.IntVar(value=2000)
        self.delete_original = ctk.BooleanVar(value=False)
        self.include_subdirectories = ctk.BooleanVar(value=True)
        self.preserve_structure = ctk.BooleanVar(value=True)  # Add preserve structure variable
        self.processing = False
        self.progress_value = ctk.DoubleVar(value=0.0)
        self.total_images = 0
        self.processed_images = 0
        self.preview_images = []  # Store image references
        self.thumbnail_size = 150  # Size for preview thumbnails
        
        # Configure main window grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)  # Give weight to preview area
        
        # Create UI elements
        self.create_ui()
    
    def create_ui(self):
        # Settings frame
        settings_frame = ctk.CTkFrame(self)
        settings_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        settings_frame.grid_columnconfigure(1, weight=1)
        
        # Directory selection
        dir_label = ctk.CTkLabel(settings_frame, text="Input Folder:", anchor="w")
        dir_label.grid(row=0, column=0, padx=(20, 10), pady=(20, 10), sticky="w")
        
        dir_entry = ctk.CTkEntry(settings_frame, textvariable=self.selected_directory)
        dir_entry.grid(row=0, column=1, padx=(0, 10), pady=(20, 10), sticky="ew")
        
        browse_button = ctk.CTkButton(
            settings_frame, 
            text="Browse", 
            command=self.browse_directory,
            fg_color=HIGHLIGHT_COLOR,
            hover_color=self.adjust_color_brightness(HIGHLIGHT_COLOR, -20)
        )
        browse_button.grid(row=0, column=2, padx=(0, 20), pady=(20, 10))
        
        # Frame for dimension controls (removed the Size Limits label)
        dim_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        dim_frame.grid(row=1, column=0, columnspan=3, padx=20, pady=(0, 10), sticky="ew")
        dim_frame.grid_columnconfigure(1, weight=1)
        
        # Width controls
        width_toggle = ctk.CTkCheckBox(
            dim_frame,
            text="Max Width:",
            variable=self.use_max_width,
            command=lambda: self.toggle_dimension("width"),
            checkbox_width=20,
            checkbox_height=20,
            corner_radius=4,
            border_width=2,
            hover=True,
            fg_color=HIGHLIGHT_COLOR,
            hover_color=self.adjust_color_brightness(HIGHLIGHT_COLOR, -20)
        )
        width_toggle.grid(row=0, column=0, padx=(0, 10))
        
        width_controls_frame = ctk.CTkFrame(dim_frame, fg_color="transparent")
        width_controls_frame.grid(row=0, column=1, sticky="ew")
        width_controls_frame.grid_columnconfigure(0, weight=1)
        
        self.width_slider = ctk.CTkSlider(
            width_controls_frame,
            from_=500,
            to=4000,
            number_of_steps=70,
            variable=self.max_width,
            command=lambda v: self.update_dimension_label("width"),
            progress_color=HIGHLIGHT_COLOR,
            button_color=HIGHLIGHT_COLOR,
            button_hover_color=self.adjust_color_brightness(HIGHLIGHT_COLOR, -20)
        )
        self.width_slider.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        width_entry_frame = ctk.CTkFrame(width_controls_frame, fg_color="transparent")
        width_entry_frame.grid(row=0, column=1)
        
        self.width_entry = ctk.CTkEntry(width_entry_frame, width=60)
        self.width_entry.grid(row=0, column=0)
        self.width_entry.insert(0, str(self.max_width.get()))
        self.width_entry.bind("<FocusOut>", lambda e: self.update_dimension_from_entry("width"))
        self.width_entry.bind("<Return>", lambda e: self.update_dimension_from_entry("width"))
        
        width_px = ctk.CTkLabel(width_entry_frame, text="px", width=20)
        width_px.grid(row=0, column=1)
        
        # Height controls
        height_toggle = ctk.CTkCheckBox(
            dim_frame,
            text="Max Height:",
            variable=self.use_max_height,
            command=lambda: self.toggle_dimension("height"),
            checkbox_width=20,
            checkbox_height=20,
            corner_radius=4,
            border_width=2,
            hover=True,
            fg_color=HIGHLIGHT_COLOR,
            hover_color=self.adjust_color_brightness(HIGHLIGHT_COLOR, -20)
        )
        height_toggle.grid(row=1, column=0, padx=(0, 10), pady=(10, 0))
        
        height_controls_frame = ctk.CTkFrame(dim_frame, fg_color="transparent")
        height_controls_frame.grid(row=1, column=1, sticky="ew", pady=(10, 0))
        height_controls_frame.grid_columnconfigure(0, weight=1)
        
        self.height_slider = ctk.CTkSlider(
            height_controls_frame,
            from_=500,
            to=4000,
            number_of_steps=70,
            variable=self.max_height,
            command=lambda v: self.update_dimension_label("height"),
            progress_color=HIGHLIGHT_COLOR,
            button_color=HIGHLIGHT_COLOR,
            button_hover_color=self.adjust_color_brightness(HIGHLIGHT_COLOR, -20)
        )
        self.height_slider.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        height_entry_frame = ctk.CTkFrame(height_controls_frame, fg_color="transparent")
        height_entry_frame.grid(row=0, column=1)
        
        self.height_entry = ctk.CTkEntry(height_entry_frame, width=60)
        self.height_entry.grid(row=0, column=0)
        self.height_entry.insert(0, str(self.max_height.get()))
        self.height_entry.bind("<FocusOut>", lambda e: self.update_dimension_from_entry("height"))
        self.height_entry.bind("<Return>", lambda e: self.update_dimension_from_entry("height"))
        
        height_px = ctk.CTkLabel(height_entry_frame, text="px", width=20)
        height_px.grid(row=0, column=1)
        
        # Create a frame for the checkbox options
        checkbox_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        checkbox_frame.grid(row=2, column=0, columnspan=3, padx=20, pady=(0, 20), sticky="ew")
        checkbox_frame.grid_columnconfigure(0, weight=1)
        checkbox_frame.grid_columnconfigure(1, weight=1)
        
        # Include subdirectories option (now alone in the checkbox frame)
        subdirectories_checkbox = ctk.CTkCheckBox(
            checkbox_frame,
            text="Include Subdirectories",
            variable=self.include_subdirectories,
            command=self.on_subdirectories_toggle,
            checkbox_width=20,
            checkbox_height=20,
            corner_radius=4,
            border_width=2,
            hover=True,
            fg_color=HIGHLIGHT_COLOR,
            hover_color=self.adjust_color_brightness(HIGHLIGHT_COLOR, -20)
        )
        subdirectories_checkbox.grid(row=0, column=0, columnspan=2, padx=0, pady=(0, 0), sticky="w")
        
        # Output directory selection (moved down)
        output_checkbox = ctk.CTkCheckBox(
            settings_frame,
            text="Custom Output Folder",
            variable=self.custom_output,
            command=self.toggle_output_directory,
            checkbox_width=20,
            checkbox_height=20,
            corner_radius=4,
            border_width=2,
            hover=True,
            fg_color=HIGHLIGHT_COLOR,
            hover_color=self.adjust_color_brightness(HIGHLIGHT_COLOR, -20)
        )
        output_checkbox.grid(row=3, column=0, columnspan=3, padx=20, pady=(0, 10), sticky="w")
        
        # Output directory row
        self.output_dir_label = ctk.CTkLabel(settings_frame, text="Output Folder:", anchor="w", text_color="gray")
        self.output_dir_label.grid(row=4, column=0, padx=(20, 10), pady=(0, 10), sticky="w")
        
        self.output_dir_entry = ctk.CTkEntry(
            settings_frame, 
            textvariable=self.output_directory, 
            state="disabled",
            fg_color=("#E5E5E5", "#2B2B2B"),  # Darker background for disabled state
            border_color=("#D3D3D3", "#3E3E3E"),  # Lighter border for disabled state
            text_color=("gray50", "gray60")  # Grayed out text for disabled state
        )
        self.output_dir_entry.grid(row=4, column=1, padx=(0, 10), pady=(0, 10), sticky="ew")
        
        self.output_browse_button = ctk.CTkButton(
            settings_frame, 
            text="Browse", 
            command=self.browse_output_directory,
            fg_color=HIGHLIGHT_COLOR,
            hover_color=self.adjust_color_brightness(HIGHLIGHT_COLOR, -20),
            state="disabled"
        )
        self.output_browse_button.grid(row=4, column=2, padx=(0, 20), pady=(0, 10))

        # Preserve folder structure checkbox (add this new checkbox)
        self.preserve_structure_checkbox = ctk.CTkCheckBox(
            settings_frame,
            text="Preserve Folder Structure in Output",
            variable=self.preserve_structure,
            checkbox_width=20,
            checkbox_height=20,
            corner_radius=4,
            border_width=2,
            hover=True,
            fg_color=HIGHLIGHT_COLOR,
            hover_color=self.adjust_color_brightness(HIGHLIGHT_COLOR, -20),
            state="disabled"  # Disabled by default until both custom output and subdirectories are enabled
        )
        self.preserve_structure_checkbox.grid(row=5, column=0, columnspan=3, padx=20, pady=(0, 10), sticky="w")

        # Create preview frame with scrollbar
        preview_container = ctk.CTkFrame(self, fg_color="transparent")
        preview_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        preview_container.grid_columnconfigure(0, weight=1)
        preview_container.grid_rowconfigure(0, weight=1)

        # Create canvas and scrollbar for image preview
        self.preview_canvas = ctk.CTkCanvas(
            preview_container,
            bg=self._apply_appearance_mode(self._fg_color),
            highlightthickness=0,
            borderwidth=0
        )
        self.preview_canvas.grid(row=0, column=0, sticky="nsew")

        scrollbar = ctk.CTkScrollbar(
            preview_container,
            orientation="vertical",
            command=self.preview_canvas.yview,
            button_color=HIGHLIGHT_COLOR,
            button_hover_color=self.adjust_color_brightness(HIGHLIGHT_COLOR, -20)
        )
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.preview_canvas.configure(yscrollcommand=scrollbar.set)

        # Create frame inside canvas for image previews
        self.preview_frame = ctk.CTkFrame(self.preview_canvas, fg_color="transparent")
        self.preview_canvas_window = self.preview_canvas.create_window(
            (0, 0),
            window=self.preview_frame,
            anchor="nw",
            width=self.preview_canvas.winfo_width()
        )

        # Create placeholder with true vertical centering
        self.create_placeholder()

        # Progress frame
        self.progress_frame = ctk.CTkFrame(self)
        self.progress_frame.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")
        self.progress_frame.grid_columnconfigure(0, weight=1)
        
        self.progress_label = ctk.CTkLabel(self.progress_frame, text="Progress: 0%", anchor="w")
        self.progress_label.grid(row=0, column=0, padx=20, pady=(10, 0), sticky="w")
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_bar.grid(row=1, column=0, padx=20, pady=(5, 10), sticky="ew")
        self.progress_bar.set(0)
        self.progress_bar.configure(progress_color=HIGHLIGHT_COLOR)
        
        # Delete original files option (moved to bottom)
        delete_frame = ctk.CTkFrame(self, fg_color="transparent")
        delete_frame.grid(row=3, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        delete_checkbox = ctk.CTkCheckBox(
            delete_frame,
            text="Delete Original Files After Conversion (Cannot Be Undone)",
            variable=self.delete_original,
            checkbox_width=20,
            checkbox_height=20,
            corner_radius=4,
            border_width=2,
            hover=True,
            fg_color=HIGHLIGHT_COLOR,
            hover_color=self.adjust_color_brightness(HIGHLIGHT_COLOR, -20)
        )
        delete_checkbox.pack(pady=5)
        
        # Process button
        self.process_button = ctk.CTkButton(
            self, 
            text="Opti-Mize", 
            font=ctk.CTkFont(size=16, weight="bold"),
            height=40,
            command=self.process_images,
            fg_color=HIGHLIGHT_COLOR,
            hover_color=self.adjust_color_brightness(HIGHLIGHT_COLOR, -20)
        )
        self.process_button.grid(row=4, column=0, padx=20, pady=(0, 20), sticky="ew")

        # Configure preview frame grid and scrolling
        self.preview_frame.bind("<Configure>", self.on_frame_configure)
        self.preview_canvas.bind("<Configure>", self.on_canvas_configure)
        
        # Add mouse wheel scrolling
        self.preview_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.preview_canvas.bind("<Enter>", self._bind_mousewheel)
        self.preview_canvas.bind("<Leave>", self._unbind_mousewheel)
    
    def adjust_color_brightness(self, color_hex, brightness_offset=0):
        """Adjust the brightness of a hex color"""
        # Convert hex to RGB
        h = color_hex.lstrip('#')
        rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
        
        # Adjust brightness
        rgb_adjusted = [max(0, min(255, val + brightness_offset)) for val in rgb]
        
        # Convert back to hex
        return '#{:02x}{:02x}{:02x}'.format(*rgb_adjusted)
    
    def update_dimension_label(self, dim_type):
        """Update the entry field when slider changes"""
        if dim_type == "width":
            self.width_entry.delete(0, "end")
            self.width_entry.insert(0, str(self.max_width.get()))
        else:
            self.height_entry.delete(0, "end")
            self.height_entry.insert(0, str(self.max_height.get()))
    
    def update_dimension_from_entry(self, dim_type):
        """Update the slider when entry field changes"""
        try:
            if dim_type == "width":
                value = int(self.width_entry.get())
                value = max(500, min(4000, value))
                self.max_width.set(value)
                self.width_entry.delete(0, "end")
                self.width_entry.insert(0, str(value))
            else:
                value = int(self.height_entry.get())
                value = max(500, min(4000, value))
                self.max_height.set(value)
                self.height_entry.delete(0, "end")
                self.height_entry.insert(0, str(value))
        except ValueError:
            # Restore the previous value if invalid input
            if dim_type == "width":
                self.width_entry.delete(0, "end")
                self.width_entry.insert(0, str(self.max_width.get()))
            else:
                self.height_entry.delete(0, "end")
                self.height_entry.insert(0, str(self.max_height.get()))
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        self.preview_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def _bind_mousewheel(self, event):
        """Bind mouse wheel to canvas when mouse enters"""
        self.preview_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
    
    def _unbind_mousewheel(self, event):
        """Unbind mouse wheel from canvas when mouse leaves"""
        self.preview_canvas.unbind_all("<MouseWheel>")

    def on_frame_configure(self, event=None):
        """Reset the scroll region to encompass the inner frame"""
        self.preview_canvas.configure(scrollregion=self.preview_canvas.bbox("all"))
        # Ensure the preview frame is the same width as the canvas
        self.preview_canvas.itemconfig(
            self.preview_canvas_window,
            width=self.preview_canvas.winfo_width()
        )

    def on_canvas_configure(self, event):
        """When the canvas is resized, adjust the preview grid"""
        # Update the preview frame width to match canvas
        self.preview_canvas.itemconfig(
            self.preview_canvas_window,
            width=event.width
        )
        
        # If showing placeholder, recreate it with new dimensions
        if not self.preview_images:
            self.create_placeholder()
        else:
            self.update_preview_grid(event.width)

    def create_placeholder(self):
        """Create a centered placeholder when no images are available"""
        # Clear any existing content
        for widget in self.preview_frame.winfo_children():
            widget.destroy()
            
        # Configure the preview frame for centering
        self.preview_frame.grid_columnconfigure(0, weight=1)
        self.preview_frame.grid_rowconfigure(0, weight=1)
        
        # Create a simple centered frame
        center_frame = ctk.CTkFrame(self.preview_frame, fg_color="transparent")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Create the placeholder content
        placeholder_image = self.create_placeholder_image()
        
        if placeholder_image:
            image_label = ctk.CTkLabel(center_frame, image=placeholder_image, text="")
            image_label.pack(pady=(0, 10))
            # Store reference to prevent garbage collection
            self.placeholder_image = placeholder_image
            
        text_label = ctk.CTkLabel(
            center_frame,
            text="No images to display\nClick 'Browse' to select a folder with images",
            font=ctk.CTkFont(size=14),
            text_color="gray",
            justify="center"
        )
        text_label.pack(pady=(0, 0))
        
        # Update the canvas scroll region
        self.preview_canvas.update_idletasks()
        self.preview_canvas.configure(scrollregion=self.preview_canvas.bbox("all"))

    def create_placeholder_image(self):
        """Create a placeholder image icon"""
        try:
            # Create a simple image icon
            size = 64
            img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            
            # Draw image shape
            from PIL import ImageDraw
            draw = ImageDraw.Draw(img)
            
            # Image frame color
            frame_color = self.adjust_color_brightness(HIGHLIGHT_COLOR, -20)
            
            # Draw image frame
            margin = 4
            draw.rectangle([margin, margin, size-margin, size-margin], outline=frame_color, width=2)
            
            # Draw mountain landscape
            mountain_color = self.adjust_color_brightness(HIGHLIGHT_COLOR, 20)
            
            # Main mountain
            draw.polygon([
                (16, 48),  # Left base
                (32, 24),  # Peak
                (48, 48),  # Right base
            ], fill=mountain_color)
            
            # Smaller mountain
            draw.polygon([
                (24, 48),  # Left base
                (40, 32),  # Peak
                (56, 48),  # Right base
            ], fill=self.adjust_color_brightness(HIGHLIGHT_COLOR, 40))
            
            # Sun
            draw.ellipse([44, 12, 52, 20], fill=self.adjust_color_brightness(HIGHLIGHT_COLOR, 60))
            
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error creating placeholder image: {e}")
            return None

    def clear_preview_images(self):
        """Clear all preview images"""
        for widget in self.preview_frame.winfo_children():
            widget.destroy()
        self.preview_images.clear()
        
        # Show placeholder
        self.create_placeholder()

    def create_thumbnail(self, image_path):
        """Create a thumbnail from an image file"""
        try:
            with Image.open(image_path) as img:
                # Convert RGBA to RGB if necessary
                if img.mode == 'RGBA':
                    img = img.convert('RGB')
                
                # Calculate thumbnail size maintaining aspect ratio
                width, height = img.size
                aspect_ratio = width / height
                
                if aspect_ratio > 1:
                    new_width = self.thumbnail_size
                    new_height = int(self.thumbnail_size / aspect_ratio)
                else:
                    new_height = self.thumbnail_size
                    new_width = int(self.thumbnail_size * aspect_ratio)
                
                # Resize with high-quality resampling
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                return photo
        except Exception as e:
            print(f"Error creating thumbnail for {image_path}: {e}")
            return None

    def update_preview_grid(self, container_width):
        """Update the preview grid layout"""
        if not self.preview_images:
            return

        # Calculate optimal thumbnail size based on container width
        padding = 10
        min_columns = 3  # Minimum number of columns
        max_columns = 6  # Maximum number of columns
        
        # Calculate the optimal number of columns
        available_width = container_width - (padding * 2)
        optimal_columns = min(max_columns, max(min_columns, available_width // (self.thumbnail_size + padding)))
        
        # Calculate the actual thumbnail size to use
        actual_thumbnail_size = (available_width // optimal_columns) - padding
        
        # Reconfigure grid
        for i in range(optimal_columns):
            self.preview_frame.grid_columnconfigure(i, weight=1)
        
        # Rearrange images
        for idx, (label, _) in enumerate(self.preview_images):
            row = idx // optimal_columns
            col = idx % optimal_columns
            label.grid(row=row, column=col, padx=padding//2, pady=padding//2)

    def update_preview_for_directory(self, directory=None):
        """Update the preview images for the given or currently selected directory"""
        if directory is None:
            directory = self.selected_directory.get()
        
        if not directory:
            return
            
        self.clear_preview_images()
        
        # Get list of image files
        image_files = []
        extensions = ('*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp')
        
        if self.include_subdirectories.get():
            # Include all subdirectories
            for ext in extensions:
                image_files.extend(glob.glob(os.path.join(directory, "**", ext), recursive=True))
        else:
            # Only include files in the top directory
            for ext in extensions:
                image_files.extend(glob.glob(os.path.join(directory, ext)))
        
        # Count total images
        self.total_images = len(image_files)
        
        if self.total_images > 0:
            # Clear placeholder if it exists
            for widget in self.preview_frame.winfo_children():
                widget.destroy()
            
            # Create thumbnails for preview
            for image_path in image_files:
                photo = self.create_thumbnail(image_path)
                if photo:
                    label = ctk.CTkLabel(self.preview_frame, image=photo, text="")
                    self.preview_images.append((label, photo))
            
            # Update grid layout
            if self.preview_images:
                self.update_preview_grid(self.preview_canvas.winfo_width())

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.selected_directory.set(directory)
            self.update_preview_for_directory(directory)

    def on_subdirectories_toggle(self):
        """Handle subdirectories checkbox toggle"""
        if self.selected_directory.get():
            self.update_preview_for_directory()
        
        # Enable/disable preserve structure checkbox based on subdirectories toggle
        if self.include_subdirectories.get() and self.custom_output.get():
            self.preserve_structure_checkbox.configure(state="normal")
        else:
            self.preserve_structure_checkbox.configure(state="disabled")

    def log(self, message):
        self.log_text += message + "\n"
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.insert("1.0", self.log_text)
        self.log_textbox.configure(state="disabled")
        self.log_textbox.see("end")
        self.update_idletasks()
    
    def update_progress(self, increment=1):
        self.processed_images += increment
        if self.total_images > 0:
            progress = self.processed_images / self.total_images
            self.progress_bar.set(progress)
            self.progress_label.configure(text=f"Progress: {int(progress * 100)}%")
    
    def process_images(self):
        if not self.selected_directory.get():
            custom_showerror(self, "Error", "Please select a directory first.")
            return
        
        if self.processing:
            return
        
        directory = self.selected_directory.get()
        
        # Get max dimensions based on toggle states
        max_width = self.max_width.get() if self.use_max_width.get() else None
        max_height = self.max_height.get() if self.use_max_height.get() else None
        
        # Check if at least one dimension is enabled
        if not (self.use_max_width.get() or self.use_max_height.get()):
            custom_showerror(self, "Error", "Please enable at least one dimension limit.")
            return
        
        delete_original = self.delete_original.get()
        
        # Get output directory if custom output is enabled
        output_path = None
        if self.custom_output.get():
            output_path = self.output_directory.get()
            if not output_path:
                custom_showerror(self, "Error", "Please select an output directory.")
                return
        
        # Check if directory exists and has images
        if not os.path.isdir(directory):
            custom_showerror(self, "Error", "Selected directory does not exist.")
            return
        
        include_subdirectories = self.include_subdirectories.get()
        image_count = opti_webp.count_images(directory, include_subdirectories)
        if image_count == 0:
            custom_showinfo(self, "Info", "No optimizable images found in the selected directory.")
            return
        
        # Confirm deletion if enabled
        if delete_original:
            confirm = custom_askyesno(self, "Confirm Deletion", "You have chosen to delete original files after conversion.\n\nThis action cannot be undone. Are you sure you want to continue?")
            if not confirm:
                return
        
        # Reset progress
        self.total_images = image_count
        self.processed_images = 0
        self.progress_bar.set(0)
        self.progress_label.configure(text="Progress: 0%")
        
        # Start processing in a separate thread
        self.processing = True
        self.process_button.configure(state="disabled", text="Processing...")
        
        def process_thread():
            try:
                def update_progress(step_progress=1.0):
                    # If this is the final step (1.0), increment the completed images counter
                    if step_progress == 1.0:
                        self.processed_images += 1
                        
                    # Calculate overall progress
                    # For incomplete images, add the step progress
                    # step_progress is between 0-1 for the current image
                    total_progress = (self.processed_images + (0 if step_progress == 1.0 else step_progress)) / self.total_images
                    self.progress_bar.set(total_progress)
                    self.progress_label.configure(text=f"Progress: {int(total_progress * 100)}%")
                    # Force the GUI to update
                    self.update_idletasks()

                # Get preserve structure value for passing to resize_and_convert
                preserve_structure = self.preserve_structure.get()
                # Only use preserve_structure if both custom output and subdirectories are enabled
                if not (self.custom_output.get() and include_subdirectories):
                    preserve_structure = True  # Default to True in other cases

                opti_webp.resize_and_convert(
                    directory, 
                    max_width,
                    max_height,
                    delete_original,
                    include_subdirectories,  # process_subdirs parameter
                    self.custom_output.get(),  # use_custom_output parameter
                    output_path,  # custom_output_dir parameter
                    preserve_structure,  # preserve_structure parameter
                    update_progress  # progress_callback parameter
                )
                
                # Ensure progress is at 100% when done
                self.progress_bar.set(1.0)
                self.progress_label.configure(text="Progress: 100%")
                
                custom_showinfo(self, "Success", "Processing completed successfully!")
            except Exception as e:
                custom_showerror(self, "Error", f"Error during processing: {str(e)}")
            finally:
                self.processing = False
                self.process_button.configure(state="normal", text="Opti-Mize")
        
        threading.Thread(target=process_thread, daemon=True).start()

    def toggle_output_directory(self):
        """Show or hide the output directory selection based on checkbox state"""
        if self.custom_output.get():
            # Enable custom output directory
            self.output_dir_label.configure(text_color=("black", "white"))  # Default colors for light/dark mode
            self.output_dir_entry.configure(
                state="normal",
                fg_color=("white", "#343638"),  # Default colors for light/dark mode
                border_color=("#979DA2", "#565B5E"),  # Default colors for light/dark mode
                text_color=("black", "white")  # Default text colors for light/dark mode
            )
            self.output_browse_button.configure(state="normal")
            
            # Enable preserve structure checkbox only if subdirectories are also enabled
            if self.include_subdirectories.get():
                self.preserve_structure_checkbox.configure(state="normal")
            else:
                self.preserve_structure_checkbox.configure(state="disabled")
        else:
            # Disable custom output directory and show input directory
            self.output_dir_label.configure(text_color="gray")
            self.output_directory.set(self.selected_directory.get())
            self.output_dir_entry.configure(
                state="disabled",
                fg_color=("#E5E5E5", "#2B2B2B"),  # Darker background for disabled state
                border_color=("#D3D3D3", "#3E3E3E"),  # Lighter border for disabled state
                text_color=("gray50", "gray60")  # Grayed out text for disabled state
            )
            self.output_browse_button.configure(state="disabled")
            
            # Disable preserve structure checkbox
            self.preserve_structure_checkbox.configure(state="disabled")

    def browse_output_directory(self):
        """Open a dialog to select the output directory"""
        directory = filedialog.askdirectory()
        if directory:
            self.output_directory.set(directory)

    def toggle_dimension(self, dim_type):
        """Enable/disable dimension controls based on toggle state"""
        disabled_fg_color = ("#E5E5E5", "#2B2B2B")  # Darker background for disabled state
        disabled_border_color = ("#D3D3D3", "#3E3E3E")  # Lighter border for disabled state
        disabled_text_color = ("gray50", "gray60")  # Grayed out text for disabled state
        
        enabled_fg_color = ("white", "#343638")  # Default colors for light/dark mode
        enabled_border_color = ("#979DA2", "#565B5E")  # Default colors for light/dark mode
        enabled_text_color = ("black", "white")  # Default text colors for light/dark mode
        
        if dim_type == "width":
            enabled = self.use_max_width.get()
            self.width_slider.configure(
                state="normal" if enabled else "disabled",
                button_color=HIGHLIGHT_COLOR if enabled else disabled_border_color[1],
                progress_color=HIGHLIGHT_COLOR if enabled else disabled_border_color[1]
            )
            self.width_entry.configure(
                state="normal" if enabled else "disabled",
                fg_color=enabled_fg_color if enabled else disabled_fg_color,
                border_color=enabled_border_color if enabled else disabled_border_color,
                text_color=enabled_text_color if enabled else disabled_text_color
            )
        else:
            enabled = self.use_max_height.get()
            self.height_slider.configure(
                state="normal" if enabled else "disabled",
                button_color=HIGHLIGHT_COLOR if enabled else disabled_border_color[1],
                progress_color=HIGHLIGHT_COLOR if enabled else disabled_border_color[1]
            )
            self.height_entry.configure(
                state="normal" if enabled else "disabled",
                fg_color=enabled_fg_color if enabled else disabled_fg_color,
                border_color=enabled_border_color if enabled else disabled_border_color,
                text_color=enabled_text_color if enabled else disabled_text_color
            )

    def _update_output_directory(self, *args):
        """Update the output directory when the selected directory changes"""
        if not self.custom_output.get():
            self.output_directory.set(self.selected_directory.get())

if __name__ == "__main__":
    app = OptiWebpGUI()
    app.mainloop() 