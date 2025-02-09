import os
import logging
from libxmp import XMPFiles, XMPMeta, consts
from iptcinfo3 import IPTCInfo

class MetadataProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.ERROR)

    def convert_description(self, input_desc):
        """Convert MSUK description format to clean text"""
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

    def process_image(self, input_path, output_path):
        """Process a single image's metadata"""
        try:
            info = IPTCInfo(input_path)
            description = info['caption/abstract'].decode('utf-8', errors='replace')

            if not description:
                return False, "No description found"

            converted_description = self.convert_description(description)
            info['caption/abstract'] = converted_description.encode('utf-8')
            
            # Save IPTC changes
            info.save_as(output_path)
            
            # Update XMP
            try:
                xmpfile = XMPFiles(file_path=output_path, open_forupdate=True)
                xmp = xmpfile.get_xmp()
                if xmp is None:
                    xmp = XMPMeta()
                
                xmp.set_property(consts.XMP_NS_DC, 'description[1]', converted_description)
                
                if xmpfile.can_put_xmp(xmp):
                    xmpfile.put_xmp(xmp)
                    xmpfile.close_file()
                    self.logger.info("XMP data successfully saved")
                    return True, "Success"
            finally:
                xmpfile.close_file()

        except Exception as e:
            self.logger.error(f"Error processing {os.path.basename(input_path)}: {str(e)}")
            return False, str(e)