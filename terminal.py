import os
import logging
import sys
from progress.bar import ChargingBar
from metadata_processor import MetadataProcessor, DependencyError

iptcinfo_logger = logging.getLogger('iptcinfo')
iptcinfo_logger.setLevel(logging.ERROR)

logging.basicConfig(level=logging.DEBUG)

def process_images(input_folder):
    try:
        processor = MetadataProcessor()
    except DependencyError as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

    included_extensions = ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif']
    files = [fn for fn in os.listdir(input_folder)
        if any(fn.endswith(ext) for ext in included_extensions)]
    
    
    if len(files) > 0:
        print(f"Processing images in: {input_folder}")
        output_folder = os.path.join(input_folder, "MSUK")
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        with ChargingBar('Processing...') as bar:
            for filename in files:
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
                    img_path = os.path.join(input_folder, filename)
                    new_img_path = os.path.join(output_folder, filename)
                    
                    success, message = processor.process_image(img_path, new_img_path)
                    if not success:
                        print(f"Error processing {filename}: {message}")                

                bar.next()
    else:
        raise Exception(f"Directory '{input_folder}' contains no images.")
        

# input_folder = input("Enter the folder path containing images: ").strip()
input_folder = "/Users/jmp/Python/Images"

if os.path.isdir(input_folder):
    try: 
        process_images(input_folder)
        print(f"Processing complete. Check the '{os.path.join(input_folder, 'MSUK')}' folder for updated images.")
    except DependencyError as e: 
        print("=" * 50)
        print(f"Error: {str(e)}")
        print("=" * 50)
        sys.exit(1)
else:
    print("Invalid folder path. Please try again.")