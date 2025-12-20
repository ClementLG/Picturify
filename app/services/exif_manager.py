from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import piexif
import os

class ExifManager:
    @staticmethod
    def get_exif_data(image_path):
        """
        Extracts and converts EXIF data into a readable dictionary.
        """
        exif_data = {}
        try:
            image = Image.open(image_path)
            info = image._getexif()
            if info:
                for tag, value in info.items():
                    decoded = TAGS.get(tag, tag)
                    if decoded == "GPSInfo":
                        gps_data = {}
                        for t in value:
                            sub_decoded = GPSTAGS.get(t, t)
                            gps_data[sub_decoded] = value[t]
                        exif_data[decoded] = gps_data
                    else:
                        # Convert bytes to string if needed for JSON serialization
                        if isinstance(value, bytes):
                            try:
                                value = value.decode()
                            except:
                                value = str(value)
                        exif_data[decoded] = value
        except Exception as e:
            print(f"Error extracting EXIF: {e}")
            pass
        return exif_data

    @staticmethod
    def remove_exif(source_path, dest_path=None):
        """
        Removes EXIF data and saves the image.
        If dest_path is None, overwrites source_path (or saves to a temporary location).
        Actually for typical web usage, we probably want to create a new 'purified' version.
        """
        if dest_path is None:
            # Create a prefixed filename
            dir_name, file_name = os.path.split(source_path)
            dest_path = os.path.join(dir_name, f"purified_{file_name}")

        try:
            image = Image.open(source_path)
            data = list(image.getdata())
            image_without_exif = Image.new(image.mode, image.size)
            image_without_exif.putdata(data)
            
            # Save without metadata
            image_without_exif.save(dest_path)
            return dest_path
        except Exception as e:
            print(f"Error purifying image: {e}")
            return None
    
    @staticmethod
    def modify_exif(source_path, changes, dest_path=None):
        """
        Modifies specific EXIF tags.
        'changes' is a dict of tag names (str) and new values (str).
        Now supports arbitrary tags if they are valid EXIF names.
        """
        if dest_path is None:
            dir_name, file_name = os.path.split(source_path)
            if not file_name.startswith("formatted_"):
                 dest_path = os.path.join(dir_name, f"formatted_{file_name}")
            else:
                 dest_path = source_path

        try:
            image = Image.open(source_path)
            
            # Load existing EXIF or create new if missing
            if "exif" in image.info:
                exif_dict = piexif.load(image.info["exif"])
            else:
                exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}

            # Helper to find tag ID and Group from Name
            # We iterate piexif's own mappings to be sure it's supported
            def find_tag_info(tag_name):
                # Check 0th IFD (Image)
                for tag_id, name in piexif.TAGS["Image"].items():
                    if name["name"] == tag_name:
                        return "0th", tag_id
                # Check Exif IFD
                for tag_id, name in piexif.TAGS["Exif"].items():
                    if name["name"] == tag_name:
                        return "Exif", tag_id
                # Check GPS IFD - ignoring for now as it requires complex value formatting (tuple of rationals)
                return None, None

            for key, value in changes.items():
                if not value: continue
                
                group, tag_id = find_tag_info(key)
                
                if group and tag_id:
                    # Encoding logic
                    if key == 'UserComment':
                         # UserComment: 8 bytes header + value. 
                         # ASCII\x00\x00\x00 is standard.
                         encoded_val = b'ASCII\x00\x00\x00' + value.encode('ascii', 'ignore')
                         exif_dict[group][tag_id] = encoded_val
                    else:
                        # Attempt to determine type. piexif.TAGS[group][tag_id]["type"] gives the type ID.
                        # Type 2 (Ascii) -> needs bytes ending with null.
                        # Type 7 (Undefined) -> bytes.
                        tag_type = piexif.TAGS["Image" if group == "0th" else group][tag_id]["type"]
                        
                        if tag_type == piexif.TYPES.Ascii:
                            # Ensure utf-8/ascii bytes
                            exif_dict[group][tag_id] = value.encode('utf-8')
                        elif tag_type == piexif.TYPES.Undefined:
                             exif_dict[group][tag_id] = value.encode('utf-8')
                        else:
                            # For other types (Short, Rational), writing string might fail or need conversion.
                            # For this MVP we act on a best-effort basis for text-compatible tags.
                            # If user tries to write "ISO" (Short), passing a string might crash piexif dump.
                            try:
                                if tag_type in [piexif.TYPES.Short, piexif.TYPES.Long]:
                                    exif_dict[group][tag_id] = int(value)
                                else:
                                    print(f"Skipping complex tag {key} (Type {tag_type})")
                            except:
                                pass

            exif_bytes = piexif.dump(exif_dict)
            image.save(dest_path, exif=exif_bytes)
            return dest_path
        except Exception as e:
            print(f"Error modifying EXIF: {e}")
            try:
                image.save(dest_path)
            except:
                pass
            return None
