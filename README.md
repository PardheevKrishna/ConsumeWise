# ConsumeWise

ConsumeWise is an AI-powered smart label reader designed to help consumers understand the health impact of packaged food products and make better dietary decisions. This project leverages OCR, NLP, and machine learning to extract product information from images, analyze it, and provide health insights. It offers a multi-platform experience, including mobile apps for convenient access.

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [File Structure](#file-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Tech Stack](#tech-stack)
- [Future Enhancements](#future-enhancements)
- [License](#license)

## Project Overview

ConsumeWise uses advanced AI techniques to extract information from product labels and analyze the health impact of the food. It offers personalized recommendations based on user preferences and product nutritional data. The mobile app is user-friendly, supporting multiple platforms like Android and iOS.

Key features include:
- **Image capture** and **OCR** for reading product labels.
- **Nutritional analysis** and **health scoring** based on label data.
- **User-specific recommendations** for better food choices.
- **Barcode and QR code scanning** for easy product lookup.
- Support for **multi-language** and **speech-to-text** functionality.

## Features

- **OCR and Label Recognition**: Extract text from product labels using Google Cloud Vision API.
- **Data Structuring & Enrichment**: Process and normalize extracted data, utilizing Google Cloud Natural Language API for entity extraction.
- **Health Analysis**: Score the healthiness of food items using a machine learning model.
- **Recommendations**: Provide personalized food recommendations based on user preferences.
- **Multi-Platform Support**: Available on Android and iOS through a mobile app developed using Flutter or React Native.
- **Additional Functionalities**:
  - Barcode and QR code scanning.
  - Speech-to-text and text-to-speech integration.
  - Community reviews and personal analytics.

## File Structure

```bash
consumewise/
├── app.py
├── requirements.txt
├── README.md
├── config/
│   └── config.py
├── data_processing/
│   ├── __init__.py
│   ├── image_capture.py
│   ├── ocr_processing.py
│   ├── data_normalization.py
│   └── entity_extraction.py
├── database/
│   ├── __init__.py
│   ├── firestore_db.py
│   └── product_scraper.py
├── models/
│   ├── __init__.py
│   ├── health_analysis_model.py
│   ├── recommendation_engine.py
│   └── processed_food_score.py
├── ui/
│   ├── mobile_app/  # Flutter or React Native code
│   └── web_app/     # Optional web interface
├── utils/
│   ├── __init__.py
│   └── helpers.py
└── logs/
    └── app.log
```

## Installation

### Prerequisites

- Python 3.x
- Google Cloud SDK
- Firebase project and credentials (serviceAccountKey.json)
- Mobile development setup (Flutter or React Native)

### Step 1: Clone the repository

```bash
git clone https://github.com/your-username/consumewise.git
cd consumewise
```

### Step 2: Set up the environment

Install the necessary Python packages:

```bash
pip install -r requirements.txt
```

Install and configure Google Cloud SDK:

- Download and install the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install).
- Set up authentication:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-file.json"
```

### Step 3: Firebase Setup

- Create a Firebase project and download the `serviceAccountKey.json`.
- Initialize Firebase in your project:

```bash
firebase login
firebase init
```

Add your `serviceAccountKey.json` to the project and reference it in the configuration.

### Step 4: Mobile App Setup

If using Flutter:

```bash
cd ui/mobile_app
flutter pub get
flutter run
```

For React Native:

```bash
cd ui/mobile_app
npm install
npx react-native run-android  # or run-ios
```

## Usage

### Running the App

1. **Mobile App**: Use Flutter or React Native to run the mobile app on a device or emulator. Capture images or scan barcodes to extract product information.
2. **Backend Services**: The Python backend handles OCR, data processing, and machine learning tasks. Run the Flask/Django server with:

```bash
python app.py
```

### Example Use Case

- Open the mobile app, capture a product label, and the image will be processed via Google Cloud Vision API.
- The app will extract product information, process nutritional data, and display a health score.
- Users can view recommendations or scan additional items for comparison.

## Tech Stack

- **Backend**: Python, Google Cloud Vision API, Google Cloud Natural Language API, Firebase Firestore
- **Mobile App**: Flutter or React Native
- **Machine Learning**: TensorFlow, AutoML, custom models
- **OCR and NLP**: Google Cloud Vision and Natural Language APIs
- **Data Storage**: Firebase Firestore for user and product data

## Future Enhancements

- **Model Training**: Implement custom models for health scoring and recommendations using more diverse datasets.
- **UI/UX Enhancements**: Improve the user experience with more intuitive features.
- **API Integration**: Integrate with external APIs to enrich product information and health analysis.
- **Security**: Ensure best practices for data security, especially for user data and analytics.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
