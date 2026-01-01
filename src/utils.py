import base64
from io import BytesIO
from PIL import Image

def encode_image(image_path):
    """Encodes an image to a base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def load_image_from_path(image_path):
    """Loads an image from a path."""
    return Image.open(image_path)
