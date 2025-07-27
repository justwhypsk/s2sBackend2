import cloudinary
import cloudinary.uploader
from app.core.config import settings
import os
import base64


# Configure Cloudinary
cloudinary.config(
    cloud_name="dgzv3nira",
    api_key="621634815674283",
    api_secret=settings.CLOUDINARY_SECRET
)

def base64_to_image(base64_string):
    # Remove the data URI prefix if present
    if "data:image" in base64_string:
        base64_string = base64_string.split(",")[1]

    # Decode the Base64 string into bytes
    image_bytes = base64.b64decode(base64_string)
    return image_bytes

def upload_to_cloudinary(file_path, resource_type="image"):
    """
    Upload a file to Cloudinary with a resize transformation to 1000x1000 without cropping (stretching the image).
    """
    try:
        #check if file is base64 if it is then upload to cloudinary and replace with image link
        if file_path.startswith("data:image"):
            response = cloudinary.uploader.upload(
                base64_to_image(file_path),
                resource_type=resource_type,
                transformation=[
                    {"width": 1000, "height": 1000, "crop": "fill"}  # Stretch to 1000x1000
                ]
            )

            return response.get('secure_url')
        
        # Resize the image to 1000x1000 pixels without cropping (stretching the image)
        response = cloudinary.uploader.upload(
            file_path,
            resource_type=resource_type,
            transformation=[
                {"width": 1000, "height": 1000, "crop": "fill"}  # Stretch to 1000x1000
            ]
        )

        # Delete file after successful upload
        os.remove(file_path)

        return response.get('secure_url')
    
    except Exception as e:
        print(f"Error uploading to Cloudinary: {e}")
        return None
