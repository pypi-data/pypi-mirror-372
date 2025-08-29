import asyncio
import logging
import os
import base64
import uuid
import json
import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
import google.generativeai as genai
import requests

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- MCP Server Setup ---
# Create a FastMCP server instance
mcp = FastMCP(
    name="image_generator_mcp_server",
)
logger.info(f"MCP server '{mcp.name}' created.")


# --- Tool Definition ---
@mcp.tool(
    name="generate_image",
    description="Generates an image based on a text prompt using the Gemini API and returns the image as a base64 encoded string.",
)
async def generate_image(prompt: str) -> str:
    """
    Generates an image from a text prompt and returns the base64 encoded PNG data.
    """
    try:
        try:
            logger.info(f"Tool 'generate_image' called with prompt: '{prompt}'")

            model = genai.GenerativeModel('gemini-2.5-flash-image-preview')

            response = await model.generate_content_async([f"Generate a high-quality, detailed image of: {prompt}"])
            response = response.to_dict()

            image_data_base64 = response["candidates"][0]["content"]["parts"][-1]["inline_data"]["data"]
        except Exception as e:
            logger.exception(f"An error occurred during image generation: {e}")
            return json.dumps({"error": f"An error occurred: {str(e)}"})

        try:
            # Upload image to imgbb
            IMGBB_API_KEY = os.getenv("IMGBB_API_KEY")
            if not IMGBB_API_KEY:
                raise ValueError("IMGBB_API_KEY environment variable not set or .env file is missing.")

            upload_url = "https://api.imgbb.com/1/upload"

            # All parameters go into the 'data' payload for the POST request
            payload = {
                "key": IMGBB_API_KEY,
                "image": image_data_base64,  # The Base64 string is the 'image' field
                "name": f"{uuid.uuid4()}"   # Optional: specify a name for the file
            }
            resp = requests.post(upload_url, data=payload, timeout=60) # Increased timeout for larger files
            resp.raise_for_status() # Raise an error for bad status codes (4xx or 5xx)
            resp_json = resp.json()
            # ImgBB's success indicator is the 'data' key in the response
            if "data" not in resp_json:
                raise Exception(f"Imgbb upload failed. Response: {resp_json}")

            uploaded_url = resp_json["data"]["url"]
            logger.info(f"Image uploaded to {uploaded_url}")

        except Exception as e:
            logger.exception(f"An error occurred during image upload: {e}")
            return json.dumps({"error": f"An error occurred: {str(e)}"})
        return uploaded_url

    except Exception as e:
        logger.exception(f"An error occurred during image generation: {e}")
        return json.dumps({"error": f"An error occurred: {str(e)}"})
    

def main():
    # Get the API key from environment variables
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set or .env file is missing.")
    # Configure the Gemini API client
    genai.configure(api_key=api_key)
    logger.info("Gemini API configured successfully.")

    IMGBB_API_KEY = os.getenv("IMGBB_API_KEY")
    if not IMGBB_API_KEY:
        raise ValueError("IMGBB_API_KEY environment variable not set or .env file is missing.")
    logger.info("IMGBB_API_KEY API configured successfully.")

    logger.info("Starting MCP server via mcp.run()...")
    asyncio.run(mcp.run())

if __name__ == "__main__":
    main()
