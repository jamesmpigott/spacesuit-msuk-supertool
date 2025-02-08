import os
from iptcinfo3 import IPTCInfo
import logging
from progress.bar import ChargingBar
from libxmp import XMPFiles, XMPMeta, consts

iptcinfo_logger = logging.getLogger('iptcinfo')
iptcinfo_logger.setLevel(logging.ERROR)

logging.basicConfig(level=logging.DEBUG)

def convert_description(input):
    parts = input.strip('|').split('|')
    
    # Filter and clean the parts
    cleaned_parts = []

    for part in parts:
        # Skip empty parts
        if not part.strip():
            continue
        
        # Split into key and value
        if ':' in part:
            key, value = part.split(':', 1)
            # Trim whitespace from the value
            value = value.strip()
            cleaned_parts.append(value)

    return ', '.join(cleaned_parts)


def process_images(input_folder):
    included_extensions = ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif']
    files = [fn for fn in os.listdir(input_folder)
        if any(fn.endswith(ext) for ext in included_extensions)]
    
    
    if len(files) > 0:
        output_folder = os.path.join(input_folder, "MSUK")
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        with ChargingBar('Processing...') as bar:
            for filename in files:
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
                    img_path = os.path.join(input_folder, filename)
                    new_img_path = os.path.join(output_folder, filename)
                    
                    try:
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

                    except Exception as e:
                        print(f"Error processing {filename}: {str(e)}")

                
                bar.next()
    else:
        raise Exception(f"Directory '{input_folder}' contains no images.")
        

# input_folder = input("Enter the folder path containing images: ").strip()
input_folder = "/Users/jmp/Python/Images"

if os.path.isdir(input_folder):
    print(f"Processing images in: {input_folder}")
    process_images(input_folder)
    print(f"Processing complete. Check the '{os.path.join(input_folder, 'MSUK')}' folder for updated images.")
else:
    print("Invalid folder path. Please try again.")