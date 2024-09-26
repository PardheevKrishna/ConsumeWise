# consume-wise-backend/main.py

import os
import io
import re
import json
import base64
from typing import List, Dict

import cv2
import numpy as np
from PIL import Image
from paddleocr import PaddleOCR
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Configure CORS to allow requests from the frontend
origins = [
    "http://localhost:3000",  # Next.js default port
    # Add your production frontend URL here, e.g., "https://yourdomain.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Adjust as needed for security
    allow_headers=["*"],  # Adjust as needed for security
)

# Initialize PaddleOCR with GPU support
ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=True)

# Configure the AI API client with the API key from environment variables
genai.configure(api_key=os.getenv('GENAI_API_KEY'))  # Ensure GENAI_API_KEY is set in .env

# Define the generation settings for the Gemini model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Create the generative model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config
)

# Start a chat session with the model
chat_session = model.start_chat(history=[])

# Function to normalize text
def normalize_text(text: str) -> str:
    return ' '.join(text.lower().split())

# Function to extract text with coordinates using PaddleOCR
def extract_text_with_coords(image_bytes: bytes) -> List[Dict]:
    try:
        # Convert bytes to NumPy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        # Decode image from NumPy array
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            raise ValueError("Image decoding failed.")

        # Perform OCR on the image
        result = ocr.ocr(image, cls=True)

        # Extract text and coordinates
        detected_items = []
        for res in result:
            for line in res:
                text = line[1][0]  # Extract the text content
                coords = line[0]    # Coordinates of the bounding box
                detected_items.append({'text': text, 'coords': coords})

        return detected_items
    except Exception as e:
        print(f"Error during OCR: {e}")
        return []

# Function to analyze detected items using Gemini AI
def analyze_detected_items(extracted_text: str) -> str:
    analysis_prompt = f"""
You are a nutrition expert. Analyze the following product details extracted from a food label:

{extracted_text}

Provide the analysis split into the following sections, using JSON format:

{{
  "NutritionalAnalysis": {{
    "Macronutrients": {{
      "Carbohydrates": {{
        "Good": ["List of healthy carbohydrate sources with reasons"],
        "Bad": ["List of unhealthy carbohydrates like added sugars with reasons"]
      }},
      "Proteins": {{
        "Good": ["List of high-quality proteins with reasons"],
        "Bad": ["List of low-quality or harmful proteins with reasons"]
      }},
      "Fats": {{
        "Good": ["List of healthy fats (e.g., omega-3, unsaturated fats) with reasons"],
        "Bad": ["List of unhealthy fats (e.g., trans fats, saturated fats) with reasons"]
      }},
      "Fiber": {{
        "Good": ["List of good fiber sources and their benefits"]
      }}
    }},
    "Micronutrients": {{
      "Vitamins": {{
        "Good": ["List of vitamins that are beneficial and in appropriate amounts"],
        "Deficient": ["Vitamins that are lacking or insufficient in the product"]
      }},
      "Minerals": {{
        "Good": ["List of minerals that are beneficial and in appropriate amounts"],
        "Deficient": ["Minerals that are lacking or insufficient in the product"]
      }}
    }},
    "HealthRisks": ["Summarize potential health risks from overconsumption of specific nutrients or ingredients"],
    "HealthBenefits": ["Summarize potential health benefits of the product based on its composition"]
  }},
  "ProcessingLevel": {{
    "Description": "Describe how processed this product is and any nutrient deficiencies.",
    "Level": "Low/Medium/High",
    "Good": ["Positive aspects of processing, if any (e.g., fortified with vitamins)"],
    "Bad": ["Negative aspects of processing (e.g., artificial additives, preservatives)"]
  }},
  "HarmfulIngredients": [
    {{
      "Ingredient": "Name of the harmful ingredient",
      "Reason": "Why it is harmful"
    }},
    ...
  ],
  "DietCompliance": {{
    "CompliantDiets": ["List of diets the product complies with (e.g., vegan, keto, paleo)"],
    "NonCompliantDiets": ["List of diets the product does not comply with"],
    "Reasons": "Explanation for compliance or non-compliance with specific diets"
  }},
  "DiabetesAllergenFriendly": {{
    "IsSuitable": true/false,
    "Reasons": "Why it is or isn't suitable",
    "Allergens": ["List of allergens present"]
  }},
  "SustainabilityAndEthics": {{
    "Sustainability": "Describe whether the ingredients are sustainably sourced (e.g., palm oil, fish)",
    "EthicalConcerns": "Highlight any ethical concerns with the product ingredients (e.g., animal products, labor conditions)"
  }},
  "RecommendedAlternatives": ["Suggest healthier or more sustainable alternatives to harmful ingredients"],
  "RegulatoryCompliance": {{
    "FSSAI": "Is this product compliant with India FSSAI regulations? true/false",
    "FDA": "Is this product compliant with US FDA regulations? true/false",
    "EFSA": "Is this product compliant with EU EFSA regulations? true/false",
    "OtherRegions": "Mention any other regional compliance issues"
  }},
  "MisleadingClaims": ["List any potentially misleading claims made by the brand and explain why they may be misleading."],
  "AlternativeHomeMadeProcedure": {{
    "Ingredients": ["List of required ingredients with measurements"],
    "Steps": ["Detailed step-by-step procedure to make the homemade product"]
  }}
}}

**Important Instructions:**

- Provide the result in **JSON format only**.
- Do **not** include any explanations, code snippets, disclaimers, or additional text.
- Do **not** include code fences (e.g., ```).
- Ensure the JSON is properly formatted and valid.
- For the "MisleadingClaims" section, provide each claim as an object with "Claim" and "Reason" keys.
"""

    # Send the message to the AI
    response = chat_session.send_message(analysis_prompt)

    # Return the AI's response
    return response.text

# Function to parse the AI's analysis response
def parse_analysis_response(analysis_response: str) -> Dict:
    try:
        # Use regex to extract the JSON object
        match = re.search(r'\{.*\}', analysis_response, re.DOTALL)
        if match:
            json_str = match.group(0)
            # Parse the JSON
            analysis = json.loads(json_str)
            return analysis
        else:
            print("No valid JSON object found in the response.")
            print("Raw Analysis Response:\n", analysis_response)
            return {}
    except json.JSONDecodeError as e:
        print("Failed to parse the analysis response as JSON.")
        print(f"Error: {e}")
        print("Raw Analysis Response:\n", analysis_response)
        return {}

# Function to highlight the image based on analysis
def highlight_image(image_bytes: bytes, detected_items: List[Dict], analysis: Dict) -> bytes:
    try:
        # Convert bytes data to a NumPy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        # Decode image from NumPy array
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise ValueError("Image decoding failed.")

        # Get list of harmful ingredients from analysis
        harmful_ingredients = analysis.get("HarmfulIngredients", [])
        harmful_texts = [normalize_text(item['Ingredient']) for item in harmful_ingredients]

        # Define colors (BGR format for OpenCV)
        colors = {
            'harmful': (0, 0, 255),        # Red
            'neutral': (0, 165, 255),      # Orange
            'beneficial': (0, 255, 0)      # Green
        }

        # Draw bounding boxes
        for item in detected_items:
            text = normalize_text(item['text'])
            coords = item['coords']

            if text in harmful_texts:
                color = colors['harmful']
            else:
                color = colors['neutral']  # You can enhance this logic as needed

            # Coordinates are in the format [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
            pts = np.array(coords, np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(image, [pts], isClosed=True, color=color, thickness=2)

        # Optionally, highlight beneficial ingredients in green
        # Implement similar logic if needed

        # Encode the image back to bytes
        _, buffer = cv2.imencode('.jpg', image)
        highlighted_image_bytes = buffer.tobytes()

        return highlighted_image_bytes

    except Exception as e:
        print(f"Error in highlight_image: {e}")
        raise e

# Function to calculate health score based on analysis
def calculate_health_score(analysis: Dict) -> int:
    # Start with a perfect health score of 100
    health_score = 100

    # Deduct points for bad macronutrients and micronutrients
    bad_macronutrients = analysis.get("NutritionalAnalysis", {}).get("Macronutrients", {})
    bad_nutrients_count = sum(len(bad_macronutrients.get(nutrient, {}).get("Bad", [])) for nutrient in ["Carbohydrates", "Proteins", "Fats", "Fiber"])
    health_score -= bad_nutrients_count * 5  # Deduct 5 points per bad nutrient

    # Deduct points for harmful ingredients
    harmful_ingredients = analysis.get("HarmfulIngredients", [])
    health_score -= len(harmful_ingredients) * 10  # Deduct 10 points per harmful ingredient

    # Deduct points for high processing level
    processing_level = analysis.get("ProcessingLevel", {}).get("Level", "Unknown").lower()
    if processing_level == "high":
        health_score -= 15
    elif processing_level == "medium":
        health_score -= 5

    # Deduct points for non-compliance with diets
    non_compliant_diets = analysis.get("DietCompliance", {}).get("NonCompliantDiets", [])
    health_score -= len(non_compliant_diets) * 5  # Deduct 5 points per non-compliant diet

    # Ensure the score doesn't go below 0
    health_score = max(health_score, 0)

    return health_score

# Function to generate an overall review based on analysis and health score
def generate_overall_review(analysis: Dict, health_score: int) -> str:
    review = []

    # Review based on health score
    if health_score > 80:
        review.append("This product is generally healthy and well-balanced.")
    elif health_score > 50:
        review.append("This product is moderately healthy but has some areas of concern.")
    else:
        review.append("This product is not healthy and contains many harmful ingredients or nutrients.")

    # Review based on processing level
    processing_level = analysis.get("ProcessingLevel", {}).get("Level", "Unknown").lower()
    if processing_level == "high":
        review.append("It is highly processed, which can negatively impact health.")
    elif processing_level == "medium":
        review.append("It is moderately processed.")
    elif processing_level == "low":
        review.append("It is minimally processed.")

    # Review based on harmful ingredients
    harmful_ingredients = analysis.get("HarmfulIngredients", [])
    if harmful_ingredients:
        review.append("Contains harmful ingredients that could pose health risks.")
    else:
        review.append("No harmful ingredients detected.")

    # Review based on diet compliance
    compliant_diets = analysis.get("DietCompliance", {}).get("CompliantDiets", [])
    non_compliant_diets = analysis.get("DietCompliance", {}).get("NonCompliantDiets", [])
    if compliant_diets:
        review.append(f"Complies with the following diets: {', '.join(compliant_diets)}.")
    if non_compliant_diets:
        review.append(f"Does not comply with the following diets: {', '.join(non_compliant_diets)}.")

    return " ".join(review)

# Function to display analysis as HTML (Optional: For backend rendering)
def display_analysis(analysis: Dict, highlighted_image_bytes: bytes) -> str:
    # This function can be customized based on how you want to present the analysis
    # For now, it's a placeholder and not used in the endpoint response
    pass

# Endpoint to handle image upload and analysis
@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    try:
        # Read image bytes
        image_bytes = await file.read()

        # Extract text with coordinates
        detected_items = extract_text_with_coords(image_bytes)

        if not detected_items:
            return {"error": "No text detected in the image."}

        # Prepare extracted text for analysis
        extracted_texts = [item['text'] for item in detected_items]
        extracted_text = '\n'.join(extracted_texts)

        # Analyze the extracted text using AI
        analysis_response = analyze_detected_items(extracted_text)

        # Parse the analysis response
        analysis = parse_analysis_response(analysis_response)

        if not analysis:
            return {"error": "Analysis failed."}

        # Highlight the image based on analysis
        highlighted_image_bytes = highlight_image(image_bytes, detected_items, analysis)

        # Optionally, generate HTML for display (not used in this response)
        # analysis_html = display_analysis(analysis, highlighted_image_bytes)

        # Encode highlighted image to base64 for frontend
        highlighted_image_base64 = base64.b64encode(highlighted_image_bytes).decode('utf-8')

        return {
            "analysis": analysis,
            "highlighted_image": highlighted_image_base64
        }
    except Exception as e:
        print(f"Error in /analyze endpoint: {e}")
        return {"error": "Internal Server Error."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
