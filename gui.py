import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import logging
import multiprocessing
import queue
from PIL import Image, ImageTk
from metadata_processor import MetadataProcessor, DependencyError
from rally_data import RallyData
import validators 

def process_image_batch(input_folder, output_folder, batch, results_queue):
    batch_results = []
    processor = MetadataProcessor()
        
    for filename in batch:
        try:
            img_path = os.path.join(input_folder, filename)
            new_img_path = os.path.join(output_folder, filename)
            
            success, message = processor.process_image(img_path, new_img_path)
            if success:
                batch_results.append(f"Processed: {filename}")
            else:
                batch_results.append(f"Error processing {filename}: {message}")
        
        except Exception as e:
            batch_results.append(f"Error processing {filename}: {str(e)}")
    
    results_queue.put(batch_results)

class IPTCProcessorApp:
    def __init__(self, master):
        # Base setup
        self.master = master
        master.title("Spacesuit Media - Tools")
        master.geometry("600x550")

        self.logo_frame = tk.Frame(self.master)
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

        # Create notebook
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(expand=True, fill='both')

        # Create tabs
        self.iptc_tab = ttk.Frame(self.notebook)
        self.csv_tab = ttk.Frame(self.notebook)
        
        # Add tabs to notebook
        self.notebook.add(self.iptc_tab, text='IPTC Tool')
        self.notebook.add(self.csv_tab, text='CSV Tool')

        # Initialize tab contents
        self.init_iptc_tab()

        self.init_csv_tab()

    def init_csv_tab(self):
        self.file_name = tk.StringVar(value="rally_entries.csv")
        self.url = tk.StringVar()
        self.csv_output_folder = None

        self.url.trace_add("write", self.check_csv_fields)
        self.file_name.trace_add("write", self.check_csv_fields)

        self.csv_output_folder_frame = tk.Frame(self.csv_tab)
        self.csv_output_folder_frame.pack(pady=10)

        self.csv_output_folder_label = tk.Label(
            self.csv_output_folder_frame, 
            text="Output Folder: Not Selected", 
        )

        self.csv_output_folder_label.pack(side=tk.LEFT)

        self.csv_select_folder_button = tk.Button(
            self.csv_output_folder_frame, 
            text="Select Output Folder", 
            command=self.select_csv_output_folder
        )
        self.csv_select_folder_button.pack(side=tk.LEFT)

        self.file_name_frame = tk.Frame(self.csv_tab)
        self.file_name_frame.pack(pady=10)
        self.file_name_label = tk.Label(
            self.file_name_frame,
            text="Output File name"
        )
        self.file_name_label.pack(side=tk.LEFT)


        self.file_name_field = tk.Entry(
            self.file_name_frame,
            textvariable=self.file_name
        )
        self.file_name_field.pack(side=tk.RIGHT)

        self.url_frame = tk.Frame(self.csv_tab)
        self.url_frame.pack(pady=10)

        self.url_label = tk.Label(
            self.url_frame,
            text="Url"
        )
        self.url_label.pack(side=tk.LEFT)

        self.url_field = tk.Entry(
            self.url_frame,
            textvariable=self.url
        )
        self.url_field.pack(side=tk.RIGHT)

        self.create_csv_button = tk.Button(
            self.csv_tab,
            text="Create CSV",
            command=self.create_csv,
            state=tk.DISABLED
        )
        self.create_csv_button.pack()

    def create_csv(self):
        if not validators.url(self.url.get()):
            messagebox.showerror("Invalid URL.", f"{self.url.get()} is not a valid url.")
            return

        rally_data = RallyData(self.url.get())
        rally_data.fetch_data()
        rally_data.transform_data()
        rally_data.export_to_csv(self.csv_output_folder, self.file_name.get())

    def check_csv_fields(self, *args):
        # Get the current values
        url_value = self.url.get()
        filename_value = self.file_name.get()
        
        # Check if all required fields have values
        if url_value and filename_value and self.csv_output_folder:
            self.create_csv_button.config(state=tk.NORMAL)
        else:
            self.create_csv_button.config(state=tk.DISABLED)

    def init_iptc_tab(self):
        # Input folder frame - update parent
        self.input_folder_frame = tk.Frame(self.iptc_tab)
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
        self.output_folder_frame = tk.Frame(self.iptc_tab)
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

        self.output_folder_label = tk.Label(self.iptc_tab, text="Output Folder: MSUK (default)")
        self.output_folder_label.pack(pady=5)

        # Progress indicators
        self.progress_frame = tk.Frame(self.iptc_tab)
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
            self.iptc_tab, 
            height=10, 
            width=70, 
            state='disabled'
        )
        self.status_text.pack(pady=10)

        # Process button - explicitly parented to iptc_tab
        self.process_button = tk.Button(
            self.iptc_tab,  # Changed from self.master
            text="Process Images",
            command=self.start_processing,
            state=tk.DISABLED
        )
        self.process_button.pack()

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

    def select_csv_output_folder(self):
        selected_folder = filedialog.askdirectory()
        if selected_folder:
            self.csv_output_folder = selected_folder
            self.csv_output_folder_label.config(
                text=f"Output Folder: {self.csv_output_folder}"
            )
            self.check_csv_fields()
    
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
    try: 
        MetadataProcessor()
        app = IPTCProcessorApp(root)
    except DependencyError as e:
        messagebox.showerror("Dependencies Missing", str(e))
        root.destroy()
        return
    
    root.mainloop()

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()