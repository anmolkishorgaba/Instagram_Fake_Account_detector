# Fake Instagram Account Detector

A machine learning-powered tool that leverages computer vision and meta-ensemble techniques to detect fake Instagram accounts. This project uses a combination of a Convolutional Neural Network (CNN) for profile picture classification, a Random Forest model for extracting Instagram profile features, and a meta-model to combine these predictions for a final verdict.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Usage](#usage)

## Overview

Instagram is a prime target for fake accounts that can spread misinformation or manipulate social interactions. This project aims to classify Instagram accounts as "fake" or "real" by:
- Scraping profile pictures and Instagram metadata.
- Processing profile pictures using a pre-trained CNN model.
- Analyzing Instagram features (number of posts, followers, following, and follower-following ratio) using a Random Forest classifier.
- Combining both predictions with a meta-model (stacking) for a robust final prediction.
<table style="border-collapse: collapse; border: none;">
  <tr>
    <td style="border: none;"><img width="646" height="496" alt="image" src="https://github.com/user-attachments/assets/b592b949-50e3-4be7-8522-963c857a365b" />
</td>
    <td style="border: none;"><img width="612" height="858" alt="image" src="https://github.com/user-attachments/assets/41582a4f-1208-44f8-8c7d-8e3334473c26" />
</td>
  </tr>
</table>

## Features

- **Instagram Scraping:**  
  - Downloads the profile picture using the [Instaloader](https://instaloader.github.io/) library.
  - Extracts Instagram metadata such as followers, following, number of posts, and bio.

- **Image Preprocessing & CNN Prediction:**  
  - Preprocesses profile images (resize and normalization) for the CNN.
  - Uses a TensorFlow-based CNN model to classify the profile picture as indicative of a fake or real account.

- **Random Forest Prediction:**  
  - Extracts key Instagram features.
  - Uses a scikit-learn Random Forest model to classify account authenticity based on numerical features.

- **Meta-Model Stacking:**  
  - Combines predictions from the CNN and Random Forest models.
  - Uses a pre-trained meta-model (also built with scikit-learn) to produce a final classification ("fake" or "real") after scaling the combined predictions.

- **API Service with FastAPI:**  
  - Provides an API endpoint (`/predict/`) to input an Instagram username and receive:
    - Final prediction ("fake" or "real")
    - Instagram profile details (followers, following, number of posts, bio)
    - URL for the downloaded profile picture
  - Serves static files and a basic index page for potential front-end integration.

## Technologies Used

- **Programming Language:** Python
- **Machine Learning & Deep Learning:**  
  - TensorFlow (for CNN model)
  - scikit-learn (for Random Forest and meta-model)
- **Web Framework:** FastAPI (for API endpoints)
- **Web Scraping:** Instaloader (for downloading Instagram profile data)
- **Image Processing:** Pillow (PIL)
- **Data Handling:** NumPy
- **Model Serialization:** joblib
- **HTTP Requests:** requests
## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/fake-instagram-account-detector.git
   cd fake-instagram-account-detector

2. **Set Up a Virtual Environment:**

  ```bash
  python -m venv venv
  source venv/bin/activate  # For Windows: venv\Scripts\activate
```
3.**Install Dependencies:**
Make sure you have all required packages installed. You can install them using:
  ```bash
  pip install -r requirements.txt
  ```
4.**Model Files:**

Ensure that the following model files are available in your project directory:

- **profile_pic_classifier.h5 (TensorFlow CNN model)**
- **random_forest_model.pkl (scikit-learn Random Forest model)**
- **meta_model.pkl (scikit-learn meta-model for stacking)**
- **scaler.pkl (scaling model for meta-model input)**

5.**Static Files:**

Create a directory structure for static files if not already present:
   ```bash
   mkdir -p static/profile_pics
   ```
##Usage
1.**Run the FastAPI Server:**

Start the server using Uvicorn:

```bash
uvicorn main:app --reload
The server will run at http://127.0.0.1:8000.
```
2.**Access the API:**

- **Index Page:**
  Open http://127.0.0.1:8000/ in your browser to view the index page.

- **Prediction Endpoint:**
  Make a GET request to /predict/?username=<instagram_username> to get the prediction for an Instagram account.
  Example:

```bash
http://127.0.0.1:8000/predict/?username=example_user
```
The endpoint returns a JSON object with the following keys:
- **username**
- **prediction ("fake" or "real")**
- **profile_pic_url (path to the downloaded profile picture)**
- **followers**
- **following**
- **num_posts**
- **bio**
