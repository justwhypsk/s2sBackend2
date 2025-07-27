import instaloader
from backend.app.services.cloudinary import upload_to_cloudinary
from backend.app.core.config import settings
import os
import shutil
import requests
from urllib.parse import urlparse


# Initialize Instaloader
L = instaloader.Instaloader()


def analyze_image_with_mistral(media_urls, caption):
    """
    Use the Mistral API to analyze the image and generate attributes.
    """
    try:
        mistral_api_key = settings.MISTRAL_API_KEY
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {mistral_api_key}",
        }

        # Prepare payload for Mistral API request
        payload = {
            "model": "pixtral-12b-2409",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Describe the product in this image such that a customer would understand it. Also tell the products color, brand, and any other details you can see.",
                        },
                        {
                            "type": "image_url",
                            "image_url": media_urls[0],
                        },  # Use the first image
                    ],
                }
            ],
            "max_tokens": 300,
        }

        response = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers=headers,
            json=payload,
        )

        if response.status_code != 200:
            print(f"Mistral API error: {response.status_code}, {response.text}")
            return None

        # Extract description from the response
        analysis_result = response.json()
        description = (
            analysis_result.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )

        # Prepare attributes with another Mistral request
        payload_attributes = {
            "model": "mistral-large-latest",
            "messages": [
                {
                    "role": "user",
                    "content": f"""Image description: {description},
                    Post caption: {caption}
                    Ignore the hashtags and emojis in the caption do not include those in any response.
                    Based on the above details generate the following attributes (whichever are possible) for this product.

                    product_name: str
                    product_description: str
                    category: str
                    brand: str
                    color: str
                    dyanmic_attributes: {{str : str}} (any other details)

                    Respond the attributes in a json format
""",
                }
            ],
            "response_format": {"type": "json_object"},
        }

        attributes_response = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers=headers,
            json=payload_attributes,
        )

        if attributes_response.status_code != 200:
            print(
                f"Mistral attributes error: {attributes_response.status_code}, {attributes_response.text}"
            )
            return None

        attributes = attributes_response.json()
        return {
            "description": description,
            "attributes": attributes,
            "image": media_urls,
        }
    except Exception as e:
        print(f"Error in analyze_image_with_mistral: {e}")
        return None


def clean_up_folder(folder_path):
    """
    Delete the specified folder and all its contents.
    """
    try:
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
    except Exception as e:
        print(f"Error deleting folder {folder_path}: {e}")

def get_instagram_post_shortcode(url):
    """
    Extracts the shortcode from various Instagram post URL formats.
    """
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip("/").split("/")
    
    # Handle URLs like "https://www.instagram.com/p/C6dV6ujNa1a/" and "https://www.instagram.com/username/p/C6dV6ujNa1a/"
    if len(path_parts) >= 2 and path_parts[-2] == "p":
        return path_parts[-1]
    else:
        raise ValueError("Invalid Instagram post URL format.")

def get_instagram_post(url: str, download_dir: str = "media"):
    """
    Get and analyze a post from Instagram by its URL.
    """
    try:
        # Post url can also be like: https://www.instagram.com/username/p/C6dV6ujNa1a/?hl=en&img_index=1

        # Extract the shortcode from the URL
        shortcode = get_instagram_post_shortcode(url)

        if shortcode:

            post = instaloader.Post.from_shortcode(L.context, shortcode)

            # Ensure directory exists
            os.makedirs(download_dir, exist_ok=True)

            # Default caption
            caption = post.caption if post.caption else ""

            # Initialize post data
            post_data = {"caption": caption, "media_urls": []}

            # Download post to the specified directory
            L.dirname_pattern = download_dir
            L.download_post(post, target=download_dir)

            # Analyze files in the directory
            for file_name in os.listdir(download_dir):
                file_path = os.path.join(download_dir, file_name)
                if file_name.endswith((".jpg", ".jpeg", ".png")):
                    # Upload image to Cloudinary
                    image_url = upload_to_cloudinary(file_path, resource_type="image")
                    post_data["media_urls"].append(image_url)

            return post_data

        else:
            print("Invalid Instagram post URL.")
            return None
    except Exception as e:
        print(f"An error occurred while processing Instagram post: {e}")
        return None
    finally:
        # Clean up the media directory after processing
        clean_up_folder(download_dir)
