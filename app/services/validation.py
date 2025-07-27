import requests
from app.core.config import settings
import json

# Load the Mistral API key from settings
mistral_api_key = settings.MISTRAL_API_KEY
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {mistral_api_key}",
}

def check_product_details(product_json):
    """
    Validates product details using the Mistral API.
    
    Parameters:
        product_json (dict): The product details in JSON format.
        
    Returns:
        dict: A dictionary containing the validation result.
              Example: {"validated": True} or {"validated": False}.
    """
    # Prepare the request payload
    payload_attributes = {
        "model": "mistral-large-latest",
        "messages": [
            {
                "role": "user",
                "content": f"""
                Product description: {product_json}
                Check if the product details are correct and not fraudulent.
                Respond with the attributes in JSON format:
                {{
                    "validated": bool
                }}
                """,
            }
        ],
        "response_format": {"type": "json_object"}
    }

    try:
        # Make the API request to Mistral
        response = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers=headers,
            json=payload_attributes,
            timeout=10  # Add a timeout to avoid hanging requests
        )
        response.raise_for_status()  # Raise an HTTPError for non-200 status codes
    except requests.RequestException as e:
        # Log and handle any request exceptions
        print(f"Error validating product details: {e}")
        return {"validated": False, "error": "API request failed"}

    try:
        # Parse the API response
        response_json = response.json()
        print(response_json)  # Debug: Log the full API response
        
        # Extract the `content` field
        content = (
            response_json
            .get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )
        
        # Parse `content` as JSON to extract `validated`
        parsed_content = json.loads(content)  # Convert string to dictionary
        validated = parsed_content.get("validated", False)
        
        ret_json = {"validated": validated}
        print(ret_json)  # Debug: Log the result
        return ret_json
    except (ValueError, KeyError, TypeError) as e:
        # Handle JSON parsing errors or missing data
        print(f"Error parsing response: {e}, Response content: {response.text}")
        return {"validated": False, "error": "Invalid API response format"}

