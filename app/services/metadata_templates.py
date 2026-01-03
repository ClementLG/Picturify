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
            
            # GPS
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
