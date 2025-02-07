import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from iptcinfo3 import IPTCInfo
import logging
import multiprocessing
import queue

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
            description = info['caption/abstract'].decode('utf-8', errors='ignore')

            if description:
                info['caption/abstract'] = convert_description(description).encode('utf-8')

            info.save_as(new_img_path)
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
        master.title("IPTC Processor")
        master.geometry("600x500")

        # Input folder selection
        self.input_folder_frame = tk.Frame(master)
        self.input_folder_frame.pack(pady=10)

        self.input_folder_label = tk.Label(
            self.input_folder_frame, 
            text="Input Folder: Not Selected", 
            width=50
        )
        self.input_folder_label.pack(side=tk.LEFT, padx=10)

        self.select_folder_button = tk.Button(
            self.input_folder_frame, 
            text="Select Input Folder", 
            command=self.select_input_folder
        )
        self.select_folder_button.pack(side=tk.LEFT)

        # Batch size selection
        self.batch_frame = tk.Frame(master)
        self.batch_frame.pack(pady=10)

        tk.Label(self.batch_frame, text="Batch Size:").pack(side=tk.LEFT, padx=10)
        self.batch_var = tk.StringVar(value="100")
        self.batch_entry = tk.Entry(
            self.batch_frame, 
            textvariable=self.batch_var, 
            width=10
        )
        self.batch_entry.pack(side=tk.LEFT, padx=10)

        # CPU Core selection
        tk.Label(self.batch_frame, text="CPU Cores:").pack(side=tk.LEFT, padx=10)
        self.cores_var = tk.StringVar(value=str(max(1, multiprocessing.cpu_count() - 1)))
        self.cores_entry = tk.Entry(
            self.batch_frame, 
            textvariable=self.cores_var, 
            width=10
        )
        self.cores_entry.pack(side=tk.LEFT, padx=10)

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
            batch_size = int(self.batch_var.get())
            num_cores = int(self.cores_var.get())
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
                messagebox.showinfo(
                    "Complete", 
                    f"Processed {processed_count} images. Output folder: {output_folder}"
                )
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

def main():
    root = tk.Tk()
    app = IPTCProcessorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()