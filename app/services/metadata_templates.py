class MetadataTemplates:
    """
    Defines templates for metadata filtering.
    Each template contains a list of tag names (strings) that should be PRESERVED.
    """
    
    TEMPLATES = {
        'flickr': [
            # Camera Info
            'Make', 'Model', 'LensModel', 'LensMake', 'LensSpecification',
            
            # Shooting Settings
            'ISOSpeedRatings', 'ISO', 'FNumber', 'ExposureTime', 'FocalLength', 'FocalLengthIn35mmFilm',
            'ExposureBiasValue', 'WhiteBalance', 'Flash', 'MeteringMode', 'ExposureProgram',
            
            # Dates
            'DateTimeOriginal', 'DateTimeDigitized', 'DateTime',
            
            # GPS - Note regarding piexif: GPS tags are in a separate IFD, 
            # but our keep_only_tags logic needs to handle knowing which names belong to GPS.
            # However, typically ExifManager._find_tag_info handles name lookup.
            # For simplicity in definitions, we list the NAMES here.
            'GPSVersionID', 'GPSLatitudeRef', 'GPSLatitude', 'GPSLongitudeRef', 'GPSLongitude',
            'GPSAltitudeRef', 'GPSAltitude', 'GPSTimeStamp', 'GPSSatellites', 'GPSStatus',
            'GPSMeasureMode', 'GPSDOP', 'GPSSpeedRef', 'GPSSpeed', 'GPSTrackRef', 'GPSTrack',
            'GPSImgDirectionRef', 'GPSImgDirection', 'GPSMapDatum', 'GPSDestLatitudeRef',
            'GPSDestLatitude', 'GPSDestLongitudeRef', 'GPSDestLongitude', 'GPSDestBearingRef',
            'GPSDestBearing', 'GPSDestDistanceRef', 'GPSDestDistance', 'GPSProcessingMethod',
            'GPSAreaInformation', 'GPSDateStamp', 'GPSDifferential',
            
            # Orientation
            'Orientation',
            
            # Software
            'Software',
            
            # Description/Artist (Optional but usually good for Flickr)
            'ImageDescription', 'Artist', 'Copyright'
        ]
    }

    @staticmethod
    def get_template(name):
        return MetadataTemplates.TEMPLATES.get(name)

    @staticmethod
    def list_templates():
        return list(MetadataTemplates.TEMPLATES.keys())
