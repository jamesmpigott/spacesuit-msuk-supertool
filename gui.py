import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from iptcinfo3 import IPTCInfo
import logging
import multiprocessing
import queue
from libxmp import XMPFiles, XMPMeta, consts
from PIL import Image, ImageTk

def convert_description(input_desc):
    """Standalone function for description conversion"""
    parts = input_desc.strip('|').split('|')
    cleaned_parts = []
    for part in parts:
        if not part.strip():
            continue
        if ':' in part:
            key, value = part.split(':', 1)
            value = value.strip()
            cleaned_parts.append(value)
    return ', '.join(cleaned_parts)

def process_image_batch(input_folder, output_folder, batch, results_queue):
    """Process a batch of images in a separate process"""
    batch_results = []
    for filename in batch:
        try:
            img_path = os.path.join(input_folder, filename)
            new_img_path = os.path.join(output_folder, filename)
            
            info = IPTCInfo(img_path)
            # Force utf-8 encoding when reading
            description = info['caption/abstract'].decode('utf-8', errors='replace')

            if description:
                converted_description = convert_description(description)
                # Ensure clean UTF-8 encoding when writing
                info['caption/abstract'] = converted_description.encode('utf-8')
                
                # Save IPTC changes
                info.save_as(new_img_path)
                
                # Add XMP update
                try:
                    xmpfile = XMPFiles(file_path=new_img_path, open_forupdate=True)
                    xmp = xmpfile.get_xmp()
                    if xmp is None:
                        xmp = XMPMeta()
                    
                    # Use the correct XMP namespace and property
                    xmp.set_property(consts.XMP_NS_DC, 'description[1]', converted_description)
                    # Alternative namespace you might need:
                    # xmp.set_property(consts.XMP_NS_PHOTOSHOP, 'Caption', converted_description)
                    
                    if xmpfile.can_put_xmp(xmp):
                        xmpfile.put_xmp(xmp)
                        xmpfile.close_file()
                        logging.info("XMP data successfully saved to the image.")
                finally:
                    xmpfile.close_file()

            batch_results.append(f"Processed: {filename}")
        except Exception as e:
            batch_results.append(f"Error processing {filename}: {str(e)}")
    
    results_queue.put(batch_results)

class IPTCProcessorApp:
    def __init__(self, master):
        # Logging setup
        logging.basicConfig(level=logging.ERROR)
        iptcinfo_logger = logging.getLogger('iptcinfo')
        iptcinfo_logger.setLevel(logging.ERROR)

        # UI Setup
        self.master = master
        master.title("Spacesuit Media - MSUK Description Fixer")
        master.geometry("600x500")

        # Logo frame
        self.logo_frame = tk.Frame(master)
        self.logo_frame.pack(pady=20)

        try:
            logo_path = os.path.join(os.path.dirname(__file__), "assets", "spacesuit-full.png")
            original_img = Image.open(logo_path)
            aspect_ratio = original_img.height / original_img.width
            new_height = int(150 * aspect_ratio)
            resized_img = original_img.resize((150, new_height), Image.Resampling.LANCZOS)
            logo = ImageTk.PhotoImage(resized_img)
            logo_label = tk.Label(self.logo_frame, image=logo)
            logo_label.image = logo  # Keep reference!
            logo_label.pack(side=tk.LEFT, padx=10)
        except Exception as e:
            logging.error(f"Failed to load logo: {e}")

        try:
            msuk_logo_path = os.path.join(os.path.dirname(__file__), "assets", "msuk.png")
            original_img = Image.open(msuk_logo_path)
            aspect_ratio = original_img.height / original_img.width
            new_height = int(150 * aspect_ratio)
            resized_img = original_img.resize((150, new_height), Image.Resampling.LANCZOS)
            msuk_logo = ImageTk.PhotoImage(resized_img)
            msuk_logo_label = tk.Label(self.logo_frame, image=msuk_logo)
            msuk_logo_label.image = msuk_logo  # Keep reference!
            msuk_logo_label.pack(side=tk.RIGHT, padx=10)
        except Exception as e:
            logging.error(f"Failed to load logo: {e}")

        # Input folder selection
        self.input_folder_frame = tk.Frame(master)
        self.input_folder_frame.pack(pady=10)

        self.input_folder_label = tk.Label(
            self.input_folder_frame, 
            text="Input Folder: Not Selected", 
        )
        self.input_folder_label.pack(side=tk.LEFT)

        self.select_folder_button = tk.Button(
            self.input_folder_frame, 
            text="Select Input Folder", 
            command=self.select_input_folder
        )
        self.select_folder_button.pack(side=tk.LEFT)

        self.batch_var = 50

        self.cores_var = max(1, multiprocessing.cpu_count() - 1)

        # Output folder selection
        self.output_folder_frame = tk.Frame(master)
        self.output_folder_frame.pack(pady=10)

        self.use_default_var = tk.BooleanVar(value=True)
        self.use_default_checkbox = tk.Checkbutton(
            self.output_folder_frame, 
            text="Use default output folder (MSUK)", 
            variable=self.use_default_var,
            command=self.toggle_output_folder
        )
        self.use_default_checkbox.pack(side=tk.LEFT)

        self.select_output_button = tk.Button(
            self.output_folder_frame, 
            text="Select Output Folder", 
            command=self.select_output_folder,
            state=tk.DISABLED
        )
        self.select_output_button.pack(side=tk.LEFT, padx=10)

        self.output_folder_label = tk.Label(master, text="Output Folder: MSUK (default)")
        self.output_folder_label.pack(pady=5)

        # Progress indicators
        self.progress_frame = tk.Frame(master)
        self.progress_frame.pack(pady=10)

        self.total_progress_label = tk.Label(self.progress_frame, text="Total Progress:")
        self.total_progress_label.pack()
        self.total_progress_bar = ttk.Progressbar(
            self.progress_frame, 
            orient="horizontal", 
            length=500, 
            mode="determinate"
        )
        self.total_progress_bar.pack()

        # Status text
        self.status_text = tk.Text(
            master, 
            height=10, 
            width=70, 
            state='disabled'
        )
        self.status_text.pack(pady=10)

        # Process button
        self.process_button = tk.Button(
            master, 
            text="Process Images", 
            command=self.start_processing,
            state=tk.DISABLED
        )
        self.process_button.pack(pady=10)

        # State variables
        self.input_folder = None
        self.output_folder = None

    def toggle_output_folder(self):
        if self.use_default_var.get():
            self.select_output_button.config(state=tk.DISABLED)
            self.output_folder_label.config(text="Output Folder: MSUK (default)")
            self.output_folder = None
        else:
            self.select_output_button.config(state=tk.NORMAL)
            self.output_folder_label.config(text="Output Folder: Not Selected")

    def select_output_folder(self):
        selected_folder = filedialog.askdirectory()
        if selected_folder:
            self.output_folder = selected_folder
            self.output_folder_label.config(
                text=f"Output Folder: {self.output_folder}"
            )

    def select_input_folder(self):
        self.input_folder = filedialog.askdirectory()
        if self.input_folder:
            self.input_folder_label.config(
                text=f"Input Folder: {self.input_folder}"
            )
            self.process_button.config(state=tk.NORMAL)

    def start_processing(self):
        # Validate and prepare processing
        if not self.input_folder or not os.path.isdir(self.input_folder):
            messagebox.showerror("Error", "Invalid input folder")
            return

        # Get batch and core settings
        try:
            batch_size = int(self.batch_var)
            num_cores = int(self.cores_var)
        except ValueError:
            messagebox.showerror("Error", "Invalid batch size or core count")
            return

        # Determine output folder
        if self.use_default_var.get():
            output_folder = os.path.join(self.input_folder, "MSUK")
        else:
            if not self.output_folder:
                messagebox.showerror("Error", "Please select an output folder")
                return
            output_folder = self.output_folder

        # Create output folder
        os.makedirs(output_folder, exist_ok=True)

        # Find image files
        included_extensions = ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif']
        files = [
            fn for fn in os.listdir(self.input_folder)
            if any(fn.lower().endswith(ext) for ext in included_extensions)
        ]

        if not files:
            messagebox.showinfo("Info", "No images found in the selected folder")
            return

        # Prepare UI for processing
        self.process_button.config(state=tk.DISABLED)
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete(1.0, tk.END)
        
        # Setup progress bars
        self.total_progress_bar['maximum'] = len(files)
        self.total_progress_bar['value'] = 0

        # Start processing
        self.process_images_multiprocess(files, output_folder, batch_size, num_cores)

    def process_images_multiprocess(self, files, output_folder, batch_size, num_cores):
        # Create results queue for inter-process communication
        results_queue = multiprocessing.Queue()

        # Batch the files
        batches = [files[i:i+batch_size] for i in range(0, len(files), batch_size)]

        # Track overall progress
        processed_count = 0
        total_files = len(files)

        # Process batches
        def process_next_batch(batch_index):
            if batch_index >= len(batches):
                # All batches processed
                self.status_text.insert(tk.END, f"\nProcessed {processed_count} images\n")
                self.process_button.config(state=tk.NORMAL)
                response = messagebox.askquestion(
                    "Complete",
                    f"Processed {processed_count} images.\nOutput folder: {output_folder}",
                    type='yesno',
                    icon='info',
                    detail='Would you like to open the output folder?'
                )
                if response == 'yes':
                    open_output_folder(output_folder)
                return

            # Current batch
            batch = batches[batch_index]
            
            # Create a new process for this batch
            p = multiprocessing.Process(
                target=process_image_batch, 
                args=(self.input_folder, output_folder, batch, results_queue)
            )
            p.start()

            # Wait for results
            def check_results():
                nonlocal processed_count
                try:
                    # Non-blocking check for results
                    batch_results = results_queue.get_nowait()
                    
                    # Update UI with results
                    for result in batch_results:
                        self.status_text.config(state=tk.NORMAL)
                        self.status_text.insert(tk.END, result + "\n")
                        self.status_text.see(tk.END)
                    
                    # Update progress
                    processed_count += len(batch)
                    self.total_progress_bar['value'] = processed_count

                    # Process next batch
                    p.join()
                    process_next_batch(batch_index + 1)

                except queue.Empty:
                    # No results yet, check again soon
                    self.master.after(100, check_results)
                except Exception as e:
                    # Error handling
                    self.status_text.insert(tk.END, f"Error: {str(e)}\n")
                    p.join()
                    process_next_batch(batch_index + 1)

            # Start checking for results
            self.master.after(100, check_results)

        # Start processing first batch
        process_next_batch(0)

def open_output_folder(output_folder):
    os.system(f'open "{output_folder}"')

def main():
    root = tk.Tk()
    app = IPTCProcessorApp(root)
    root.mainloop()

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()