from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.instagram import (
    get_instagram_post,
    analyze_image_with_mistral,
)
from app.services.moderation import check_product_moderation

router = APIRouter(prefix="/social", tags=["social"])


class InstagramPostRequest(BaseModel):
    url: str


@router.post("/analyze-instagram-post/")
async def analyze_instagram_post(data: InstagramPostRequest):
    """
    Endpoint to analyze an Instagram post by URL.
    """
    try:
        # Process the Instagram post to get Cloudinary URLs
        download_dir = "media"
        analysis_result = get_instagram_post(data.url, download_dir=download_dir)

        if not analysis_result:
            raise HTTPException(
                status_code=400,
                detail="Could not process Instagram post. Please check the URL.",
            )

        # Extract media URLs
        media_urls = analysis_result.get("media_urls", [])
        caption = analysis_result.get("caption", "Caption not found for this post.")
        if not media_urls:
            raise HTTPException(
                status_code=400, detail="No media URLs found for analysis."
            )

        # Use the Mistral API to analyze the image and generate attributes
        mistral_analysis = analyze_image_with_mistral(media_urls, caption)

        if not mistral_analysis:
            raise HTTPException(
                status_code=500, detail="Failed to analyze image using Mistral API."
            )

        if mistral_analysis == "Inappropriate image":
            return {"message": "Inappropriate image"}

        # Parse the attributes content
        raw_attributes = mistral_analysis.get("attributes", {})
        choices = raw_attributes.get("choices", [])
        parsed_content = {}

        if choices and "content" in choices[0]["message"]:
            # Parse the JSON content from the Mistral response
            import json

            try:
                parsed_content = json.loads(choices[0]["message"]["content"])
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=500, detail="Failed to parse attributes content."
                )

        # Prepare the cleaned response
        cleaned_response = {"image": media_urls, "attributes": parsed_content}

        # Check the moderation status of the product details
        moderation_result = check_product_moderation(parsed_content)

        if moderation_result.get("inappropriate_content"):
            raise HTTPException(
                status_code=400,
                detail=f"Product validation failed. Reason: {moderation_result.get('error', 'Inappropriate Content')}",
            )

        return cleaned_response

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )
