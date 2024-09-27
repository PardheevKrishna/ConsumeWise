# consume-wise-backend/main.py

import os
import io
import re
import json
import base64
from typing import List, Dict, Optional

import cv2
import numpy as np
from PIL import Image
from paddleocr import PaddleOCR
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field, validator

import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Configure CORS to allow requests from the frontend
origins = [
    "http://localhost:3000",  # Next.js default port
    "http://127.0.0.1:5500",  # Live Server port (if used)
    "https://consume-wise-smoky.vercel.app/",
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
GENAI_API_KEY = os.getenv('GENAI_API_KEY')
if not GENAI_API_KEY:
    raise ValueError("GENAI_API_KEY is not set in the environment variables.")
genai.configure(api_key=GENAI_API_KEY)

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

# MongoDB Configuration
MONGODB_URI = os.getenv("MONGODB_URI")
if not MONGODB_URI:
    raise ValueError("MONGODB_URI is not set in the environment variables.")

client = AsyncIOMotorClient(MONGODB_URI)
db = client["consume_wise_db"]
products_collection = db["products"]

# Pydantic Models

class ProprietaryClaim(BaseModel):
    claim: str
    reason: Optional[str] = None

class NutritionalInfo(BaseModel):
    serving_size: Optional[str] = None
    calories: Optional[float] = None
    carbohydrates: Optional[float] = None
    proteins: Optional[float] = None
    fats: Optional[float] = None
    fiber: Optional[float] = None
    # Add other nutritional fields as needed

class HealthScore(BaseModel):
    score: int
    review: str

class Product(BaseModel):
    product_name: str = Field(..., example="Organic Almond Milk")
    product_qty: str = Field(..., example="1 Liter")
    brand_name: str = Field(..., example="Nature's Best")
    weightage: float = Field(..., example=1000)
    weight_unit: str = Field(..., example="ml")  # "g" or "ml"

    product_category: str = Field(..., example="Beverages")
    ingredients: List[str] = Field(..., example=["Water", "Almonds", "Sea Salt"])
    nutritional_info: Optional[NutritionalInfo] = None
    proprietary_claims: Optional[List[ProprietaryClaim]] = None
    analysis: Optional[Dict] = None  # Stores the full analysis JSON
    health_score: Optional[HealthScore] = None
    image_url: Optional[str] = None  # URL to the uploaded image
    purpose: Optional[str] = Field(None, example="Nutritional")  # New Field
    frequency: Optional[str] = Field(None, example="Daily")  # New Field

    @validator('weight_unit')
    def validate_weight_unit(cls, v):
        if v not in ["g", "ml"]:
            raise ValueError("weight_unit must be either 'g' or 'ml'")
        return v

# Utility Functions

def normalize_text(text: str) -> str:
    return ' '.join(text.lower().split())

def extract_text_with_coords(image_bytes: bytes) -> List[Dict]:
    try:
        if not image_bytes:
            print("No image data provided.")
            return []
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

def analyze_detected_items(extracted_text: str) -> str:
    analysis_prompt = f"""
You are a nutrition expert. Analyze the following product details extracted from a food label:

{extracted_text}

Provide the analysis split into the following sections, using JSON format:

{{
  "NutritionalAnalysis": {{
    "serving_size": "Specify the serving size here",
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
  "MisleadingClaims": [
    {{
      "Claim": "Name of the misleading claim",
      "Reason": "Why it is misleading"
    }},
    ...
  ],
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
- **Always include the "serving_size" field under "NutritionalAnalysis".**
"""

    # Send the message to the AI
    response = chat_session.send_message(analysis_prompt)

    # Return the AI's response
    return response.text

def parse_analysis_response(analysis_response: str) -> Dict:
    try:
        # Use regex to extract the JSON object
        match = re.search(r'\{.*\}', analysis_response, re.DOTALL)
        if match:
            json_str = match.group(0)
            # Parse the JSON
            analysis = json.loads(json_str)
            # Ensure 'serving_size' is present
            if 'NutritionalAnalysis' in analysis:
                if 'serving_size' not in analysis['NutritionalAnalysis']:
                    analysis['NutritionalAnalysis']['serving_size'] = None
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

def highlight_image(image_bytes: bytes, detected_items: List[Dict], analysis: Dict) -> bytes:
    try:
        if not image_bytes:
            raise ValueError("No image data provided for highlighting.")
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

# API Endpoints

@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    try:
        # Read image bytes
        image_bytes = await file.read()

        if not image_bytes:
            raise HTTPException(status_code=400, detail="Uploaded image is empty.")

        # Extract text with coordinates
        detected_items = extract_text_with_coords(image_bytes)

        if not detected_items:
            raise HTTPException(status_code=400, detail="No text detected in the image.")

        # Prepare extracted text for analysis
        extracted_texts = [item['text'] for item in detected_items]
        extracted_text = '\n'.join(extracted_texts)

        # Analyze the extracted text using AI
        analysis_response = analyze_detected_items(extracted_text)

        # Parse the analysis response
        analysis = parse_analysis_response(analysis_response)

        if not analysis:
            raise HTTPException(status_code=500, detail="Analysis failed.")

        # Highlight the image based on analysis
        highlighted_image_bytes = highlight_image(image_bytes, detected_items, analysis)

        # Encode highlighted image to base64 for frontend
        highlighted_image_base64 = base64.b64encode(highlighted_image_bytes).decode('utf-8')

        return {
            "analysis": analysis,
            "highlighted_image": highlighted_image_base64
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error in /analyze endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error.")

@app.post("/add_product")
async def add_product(
    product_name: str = Form(...),
    product_qty: str = Form(...),
    brand_name: str = Form(...),
    weightage: float = Form(...),
    weight_unit: str = Form(...),  # "g" or "ml"
    product_category: str = Form(...),
    ingredients: Optional[str] = Form(None),  # If manual input
    ingredients_image: Optional[UploadFile] = File(None),  # If image upload
    purpose: Optional[str] = Form(None),  # New Field
    frequency: Optional[str] = Form(None)  # New Field
):
    try:
        # Log received data
        print(f"Received product_name: {product_name}")
        print(f"Received product_qty: {product_qty}")
        print(f"Received brand_name: {brand_name}")
        print(f"Received weightage: {weightage}")
        print(f"Received weight_unit: {weight_unit}")
        print(f"Received product_category: {product_category}")
        print(f"Received ingredients: {ingredients}")
        print(f"Received ingredients_image: {ingredients_image.filename if ingredients_image else 'None'}")
        print(f"Received purpose: {purpose}")
        print(f"Received frequency: {frequency}")

        # Handle ingredients
        if ingredients_image and ingredients_image.filename:
            # Validate file type
            if not ingredients_image.content_type.startswith('image/'):
                raise HTTPException(status_code=400, detail="Uploaded file is not an image.")

            # Optionally, validate file size (e.g., max 5MB)
            contents = await ingredients_image.read()
            if len(contents) > 5 * 1024 * 1024:
                raise HTTPException(status_code=400, detail="Uploaded image is too large. Max size is 5MB.")

            # Reset the file pointer after reading
            ingredients_image.file.seek(0)

            # Read image bytes
            image_bytes = await ingredients_image.read()
            if not image_bytes:
                raise HTTPException(status_code=400, detail="Uploaded ingredients image is empty.")
            detected_items = extract_text_with_coords(image_bytes)
            if not detected_items:
                raise HTTPException(status_code=400, detail="No text detected in the ingredients image.")
            ingredients_list = [item['text'] for item in detected_items]
        elif ingredients:
            # Split ingredients by comma and strip whitespace
            ingredients_list = [ing.strip() for ing in ingredients.split(",")]
        else:
            raise HTTPException(status_code=400, detail="Ingredients are required either via manual input or image upload.")

        # Prepare extracted text for Gemini API
        extracted_text = ', '.join(ingredients_list)

        # Analyze with Gemini API
        analysis_response = analyze_detected_items(extracted_text)

        # Parse the analysis response
        analysis = parse_analysis_response(analysis_response)

        if not analysis:
            raise HTTPException(status_code=500, detail="Failed to analyze ingredients with Gemini API.")

        # Calculate health score
        health_score_value = calculate_health_score(analysis)
        overall_review = generate_overall_review(analysis, health_score_value)

        health_score = HealthScore(
            score=health_score_value,
            review=overall_review
        )

        # Extract proprietary claims from analysis
        misleading_claims = analysis.get("MisleadingClaims", [])
        proprietary_claims = [ProprietaryClaim(claim=item['Claim'], reason=item.get('Reason')) for item in misleading_claims]

        # Handle image storage (Optional)
        # For simplicity, we're not storing images. If needed, implement image storage and set image_url accordingly.

        # Create Product instance
        product = Product(
            product_name=product_name,
            product_qty=product_qty,
            brand_name=brand_name,
            weightage=weightage,
            weight_unit=weight_unit,
            product_category=product_category,
            ingredients=ingredients_list,
            nutritional_info=analysis.get("NutritionalAnalysis"),
            proprietary_claims=proprietary_claims if proprietary_claims else None,
            analysis=analysis,  # Store the full analysis
            health_score=health_score,
            image_url=None,  # Placeholder, can be updated if storing images
            purpose=purpose,  # New Field
            frequency=frequency  # New Field
        )

        # Insert into MongoDB
        result = await products_collection.insert_one(product.dict())

        return {"message": "Product added successfully", "product_id": str(result.inserted_id)}
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error in /add_product endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error.")

@app.get("/get_products")
async def get_products(
    product_name: Optional[str] = None,
    brand_name: Optional[str] = None,
    product_category: Optional[str] = None,
    purpose: Optional[str] = None,  # New Filter
    frequency: Optional[str] = None,  # New Filter
    page: int = 1,
    limit: int = 10
):
    try:
        query = {}
        if product_name:
            # Case-insensitive search for product name
            query["product_name"] = {"$regex": product_name, "$options": "i"}
        if brand_name:
            # Case-insensitive search for brand name
            query["brand_name"] = {"$regex": brand_name, "$options": "i"}
        if product_category:
            # Exact match for category
            query["product_category"] = product_category
        if purpose:
            # Exact match for purpose
            query["purpose"] = purpose
        if frequency:
            # Exact match for frequency
            query["frequency"] = frequency

        # Pagination
        skips = limit * (page - 1)
        cursor = products_collection.find(query).skip(skips).limit(limit)
        results = []
        async for document in cursor:
            document["_id"] = str(document["_id"])  # Convert ObjectId to string
            results.append(document)

        # Get total count for pagination
        total_count = await products_collection.count_documents(query)

        return {
            "page": page,
            "limit": limit,
            "total_pages": (total_count + limit - 1) // limit,
            "total_products": total_count,
            "products": results
        }
    except Exception as e:
        print(f"Error in /get_products endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error.")

# Optional: Serve Static Files (e.g., images)
# Uncomment and configure if you decide to store images locally

# from fastapi.staticfiles import StaticFiles
# app.mount("/images", StaticFiles(directory="images"), name="images")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
