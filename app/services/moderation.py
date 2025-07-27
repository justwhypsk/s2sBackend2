import requests
from app.core.config import settings

mistral_api_key = settings.MISTRAL_API_KEY
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {mistral_api_key}",
}


def check_product_moderation(product_json):
    """
    Use the Mistral Moderation API to check if the product details are appropriate.

    Parameters:
        product_json (dict): JSON object containing product details.

    Returns:
        dict: A dictionary containing moderation results with validated status.
              Example:
              {
                  "validated": True,
                  "categories": {
                      "sexual": False,
                      "hate_and_discrimination": False,
                      ...
                  },
                  "category_scores": {
                      "sexual": 0.0001,
                      "hate_and_discrimination": 0.0002,
                      ...
                  }
              }
    """
    # Prepare the moderation payload
    payload = {
        "model": "mistral-moderation-latest",
        "input": [
            {
                "role": "user",
                "content": f"""Product details: {product_json}.
                Check if the product details comply with platform guidelines and moderation standards.""",
            }
        ],
    }

    try:
        # Make the API request
        response = requests.post(
            "https://api.mistral.ai/v1/chat/moderations",
            headers=headers,
            json=payload,
            timeout=10,  # Timeout for the request
        )
        response.raise_for_status()  # Raise an exception for non-2xx responses
    except requests.RequestException as e:
        print(f"Error during moderation: {e}")
        return {"error": "API request failed"}

    try:
        # Parse the API response
        response_json = response.json()

        # Extract categories and scores
        results = response_json.get("results", [])
        if not results:
            return {
                "inappropriate_content": False,
                "error": "Invalid API response format",
            }

        categories = results[0].get("categories", {})

        print(categories)  # Debug: Log the categories

        # Relevant categories to check
        relevant_categories = [
            "sexual",
            "hate_and_discrimination",
            "violence_and_threats",
            "dangerous_and_criminal_content",
            "selfharm",
        ]

        # Determine if the content is inappropriate
        inappropriate_content = any(
            categories.get(category, False) for category in relevant_categories
        )

        moderation_result = {
            "inappropriate_content": inappropriate_content,
        }

        print(moderation_result)  # Debug: Log the result
        return moderation_result
    except (KeyError, TypeError) as e:
        print(f"Error parsing moderation response: {e}")
        return {"validated": False, "error": "Failed to parse API response"}
