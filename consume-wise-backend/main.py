# consume-wise-backend/main.py

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from paddleocr import PaddleOCR
import google.generativeai as genai
import re
import json
import os

from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Configure CORS to allow requests from the frontend
origins = [
    "http://localhost:3000",  # Next.js default port
    # Add your production frontend URL here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=True)

# Configure the API client with the API key (ensure you store your API key securely)
genai.configure(api_key=os.getenv('GENAI_API_KEY'))  # Use environment variables

# Define the generation settings for the Gemini model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Create the model for generation
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config
)

# Start a chat session
chat_session = model.start_chat(history=[])

# Function to normalize text
def normalize_text(text):
    return ' '.join(text.lower().split())

# Function to extract text with coordinates
def extract_text_with_coords(image_bytes):
    try:
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        image_np = np.array(image)

        # Perform OCR on the image
        result = ocr.ocr(image_np, cls=True)

        # Extract text and coordinates
        detected_items = []
        for res in result:
            for line in res:
                text = line[1][0]  # Extract the text content
                coords = line[0]   # Coordinates of the bounding box
                detected_items.append({'text': text, 'coords': coords})

        return detected_items
    except Exception as e:
        print(f"Error during OCR: {e}")
        return []

# Function to analyze detected items
def analyze_detected_items(extracted_text):
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
    "FSSAI": "Is this product compliant with India FSSAI India regulations? true/false",
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

# Function to parse the analysis response
def parse_analysis_response(analysis_response):
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

import io
from PIL import Image
import numpy as np

# Function to highlight the image based on analysis
def highlight_image(image_path, detected_items, analysis):
    import cv2
    import matplotlib.pyplot as plt

    # Load the image
    image = cv2.imread(image_path)

    # Get list of harmful ingredients from analysis
    harmful_ingredients = analysis.get("HarmfulIngredients", [])
    harmful_texts = [normalize_text(item['Ingredient']) for item in harmful_ingredients]

    # Define colors
    colors = {
        'harmful': (255, 0, 0),      # Red
        'neutral': (255, 165, 0),    # Orange
        'beneficial': (0, 255, 0)    # Green
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

    # Convert BGR to RGB for displaying
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Save the highlighted image to bytes
    _, buffer = cv2.imencode('.jpg', image_rgb)
    image_bytes = buffer.tobytes()

    return image_bytes

# Function to calculate health score
def calculate_health_score(analysis):
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

# Function to generate overall review
def generate_overall_review(analysis, health_score):
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

# Function to display analysis
def display_analysis(analysis, highlighted_image_bytes):
    import base64

    # Calculate health score and generate overall review
    health_score = calculate_health_score(analysis)
    overall_review = generate_overall_review(analysis, health_score)

    # Prepare the highlighted image for display
    highlighted_image_base64 = base64.b64encode(highlighted_image_bytes).decode('utf-8')
    img_tag = f'<img src="data:image/jpeg;base64,{highlighted_image_base64}" alt="Highlighted Image" />'

    # Prepare the HTML content
    html_content = "<h2>Nutritional and Product Analysis</h2>"

    # Health Score
    color = 'green' if health_score > 80 else 'orange' if health_score > 50 else 'red'
    html_content += f"<h3>Health Score: <span style='color:{color};'>{health_score}/100</span></h3>"

    # Overall Review
    html_content += f"<h4>Overall Review:</h4><p>{overall_review}</p>"

    # Nutritional Analysis
    nutritional_analysis = analysis.get("NutritionalAnalysis", {})
    html_content += "<h3>Nutritional Analysis:</h3>"

    # Macronutrients
    macronutrients = nutritional_analysis.get("Macronutrients", {})
    if macronutrients:
        html_content += "<h4>Macronutrients:</h4>"
        for macro in ["Carbohydrates", "Proteins", "Fats", "Fiber"]:
            macro_data = macronutrients.get(macro, {})
            good = macro_data.get("Good", [])
            bad = macro_data.get("Bad", [])
            if good:
                html_content += f"<p style='color:green;'><strong>Good {macro}:</strong></p><ul>"
                for item in good:
                    html_content += f"<li>{item}</li>"
                html_content += "</ul>"
            if bad:
                html_content += f"<p style='color:red;'><strong>Bad {macro}:</strong></p><ul>"
                for item in bad:
                    html_content += f"<li>{item}</li>"
                html_content += "</ul>"

    # Micronutrients
    micronutrients = nutritional_analysis.get("Micronutrients", {})
    if micronutrients:
        html_content += "<h4>Micronutrients:</h4>"
        for micro in ["Vitamins", "Minerals"]:
            micro_data = micronutrients.get(micro, {})
            good = micro_data.get("Good", [])
            deficient = micro_data.get("Deficient", [])
            if good:
                html_content += f"<p style='color:green;'><strong>Good {micro}:</strong></p><ul>"
                for item in good:
                    html_content += f"<li>{item}</li>"
                html_content += "</ul>"
            if deficient:
                html_content += f"<p style='color:red;'><strong>Deficient {micro}:</strong></p><ul>"
                for item in deficient:
                    html_content += f"<li>{item}</li>"
                html_content += "</ul>"

    # Health Risks and Benefits
    health_risks = nutritional_analysis.get("HealthRisks", [])
    health_benefits = nutritional_analysis.get("HealthBenefits", [])
    if health_risks:
        html_content += "<h4>Health Risks:</h4><ul>"
        for risk in health_risks:
            html_content += f"<li style='color:red;'>{risk}</li>"
        html_content += "</ul>"
    if health_benefits:
        html_content += "<h4>Health Benefits:</h4><ul>"
        for benefit in health_benefits:
            html_content += f"<li style='color:green;'>{benefit}</li>"
        html_content += "</ul>"

    # Processing Level
    processing_level = analysis.get("ProcessingLevel", {})
    html_content += "<h3>Processing Level:</h3>"
    level = processing_level.get("Level", "Unknown")
    description = processing_level.get("Description", "")
    good_processing = processing_level.get("Good", [])
    bad_processing = processing_level.get("Bad", [])
    color = 'green' if level.lower() == 'low' else 'orange' if level.lower() == 'medium' else 'red'
    html_content += f"<p style='color:{color};'><strong>Level:</strong> {level}</p>"
    html_content += f"<p>{description}</p>"
    if good_processing:
        html_content += "<p style='color:green;'><strong>Good Processing Aspects:</strong></p><ul>"
        for item in good_processing:
            html_content += f"<li>{item}</li>"
        html_content += "</ul>"
    if bad_processing:
        html_content += "<p style='color:red;'><strong>Bad Processing Aspects:</strong></p><ul>"
        for item in bad_processing:
            html_content += f"<li>{item}</li>"
        html_content += "</ul>"

    # Harmful Ingredients
    harmful_ingredients = analysis.get("HarmfulIngredients", [])
    html_content += "<h3>Harmful Ingredients:</h3>"
    if harmful_ingredients:
        html_content += "<ul>"
        for ingredient in harmful_ingredients:
            name = ingredient.get('Ingredient', '')
            reason = ingredient.get('Reason', '')
            html_content += f"<li style='color:red;'><strong>{name}</strong>: {reason}</li>"
        html_content += "</ul>"
    else:
        html_content += "<p style='color:green;'>No harmful ingredients detected.</p>"

    # Diet Compliance
    diet_compliance = analysis.get("DietCompliance", {})
    html_content += "<h3>Diet Compliance:</h3>"
    compliant_diets = diet_compliance.get("CompliantDiets", [])
    non_compliant_diets = diet_compliance.get("NonCompliantDiets", [])
    reasons = diet_compliance.get("Reasons", "")

    if compliant_diets:
        html_content += "<p style='color:green;'><strong>Compliant Diets:</strong> " + ', '.join(compliant_diets) + "</p>"
    if non_compliant_diets:
        html_content += "<p style='color:red;'><strong>Non-Compliant Diets:</strong> " + ', '.join(non_compliant_diets) + "</p>"
    if reasons:
        html_content += f"<p>{reasons}</p>"

    # Diabetes/Allergen Friendly
    daf = analysis.get("DiabetesAllergenFriendly", {})
    html_content += "<h3>Diabetes/Allergen Friendly:</h3>"
    is_suitable = daf.get("IsSuitable", False)
    reasons = daf.get("Reasons", "")
    allergens = daf.get("Allergens", [])

    color = 'green' if is_suitable else 'red'
    suitability = "Suitable" if is_suitable else "Not Suitable"
    html_content += f"<p style='color:{color};'><strong>{suitability} for people with diabetes or allergies.</strong></p>"
    if reasons:
        html_content += f"<p>{reasons}</p>"
    if allergens:
        html_content += f"<p><strong>Allergens:</strong> {', '.join(allergens)}</p>"

    # Sustainability and Ethics
    sustainability_ethics = analysis.get("SustainabilityAndEthics", {})
    sustainability = sustainability_ethics.get("Sustainability", "")
    ethical_concerns = sustainability_ethics.get("EthicalConcerns", "")
    html_content += "<h3>Sustainability and Ethics:</h3>"
    if sustainability:
        html_content += f"<p><strong>Sustainability:</strong> {sustainability}</p>"
    if ethical_concerns:
        html_content += f"<p><strong>Ethical Concerns:</strong> {ethical_concerns}</p>"

    # Recommended Alternatives
    recommended_alternatives = analysis.get("RecommendedAlternatives", [])
    html_content += "<h3>Recommended Alternatives:</h3>"
    if recommended_alternatives:
        html_content += "<ul>"
        for alternative in recommended_alternatives:
            html_content += f"<li style='color:green;'>{alternative}</li>"
        html_content += "</ul>"
    else:
        html_content += "<p>No alternatives recommended.</p>"

    # Regulatory Compliance
    regulatory_compliance = analysis.get("RegulatoryCompliance", {})
    html_content += "<h3>Regulatory Compliance:</h3>"
    fssai_compliance = regulatory_compliance.get("FSSAI", "Unknown")
    fda_compliance = regulatory_compliance.get("FDA", "Unknown")
    efsa_compliance = regulatory_compliance.get("EFSA", "Unknown")
    other_regions = regulatory_compliance.get("OtherRegions", "")

    html_content += f"<p><strong>FSSAI Compliant:</strong> {fssai_compliance}</p>"
    html_content += f"<p><strong>FDA Compliant:</strong> {fda_compliance}</p>"
    html_content += f"<p><strong>EFSA Compliant:</strong> {efsa_compliance}</p>"
    if other_regions:
        html_content += f"<p><strong>Other Region Compliance Issues:</strong> {other_regions}</p>"

    # Misleading Claims
    misleading_claims = analysis.get("MisleadingClaims", [])
    html_content += "<h3>Misleading Claims:</h3>"
    if misleading_claims:
        html_content += "<ul>"
        for claim in misleading_claims:
            if isinstance(claim, dict):
                claim_text = claim.get('Claim', 'Unknown Claim')
                reason = claim.get('Reason', 'No reason provided')
                html_content += f"<li style='color:red;'><strong>{claim_text}</strong>: {reason}</li>"
            elif isinstance(claim, str):
                html_content += f"<li style='color:red;'>{claim}</li>"
            else:
                html_content += f"<li style='color:red;'>Unknown format</li>"
        html_content += "</ul>"
    else:
        html_content += "<p style='color:green;'>No misleading claims detected.</p>"

    # Alternative Homemade Procedure
    alternative_procedure = analysis.get("AlternativeHomeMadeProcedure", {})
    ingredients = alternative_procedure.get("Ingredients", [])
    steps = alternative_procedure.get("Steps", [])

    if health_score <= 50 and (ingredients or steps):
        html_content += "<h3>Alternative Homemade Procedure:</h3>"
        if ingredients:
            html_content += "<p><strong>Ingredients Required:</strong></p><ul>"
            for ingredient in ingredients:
                html_content += f"<li>{ingredient}</li>"
            html_content += "</ul>"
        if steps:
            html_content += "<p><strong>Step-by-Step Procedure:</strong></p><ol>"
            for step in steps:
                html_content += f"<li>{step}</li>"
            html_content += "</ol>"

    # Display the HTML content along with the highlighted image
    combined_html = f"{img_tag}<br/>{html_content}"
    return combined_html

import io
import base64

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

        # Analyze the extracted text
        analysis_response = analyze_detected_items(extracted_text)

        # Parse the analysis response
        analysis = parse_analysis_response(analysis_response)

        if not analysis:
            return {"error": "Analysis failed."}

        # Highlight the image
        highlighted_image_bytes = highlight_image(io.BytesIO(image_bytes), detected_items, analysis)

        # Generate HTML for display
        analysis_html = display_analysis(analysis, highlighted_image_bytes)

        return {"analysis": analysis, "highlighted_image": base64.b64encode(highlighted_image_bytes).decode('utf-8')}
    except Exception as e:
        print(f"Error in /analyze endpoint: {e}")
        return {"error": "Internal Server Error."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
