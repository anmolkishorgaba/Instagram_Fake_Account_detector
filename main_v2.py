import tensorflow as tf
import os
import shutil
from PIL import Image
import numpy as np
import instaloader
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import requests
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

# Load the CNN model (assuming it's saved in 'profile_pic_classifier.h5')
cnn_model = tf.keras.models.load_model('profile_pic_classifier.h5')
rf_model = joblib.load('random_forest_model.pkl') 

meta_model = joblib.load('meta_model.pkl')
scaler = joblib.load('scaler.pkl')

L = instaloader.Instaloader()
L.login('sai_abinav','Saiabhinav123')

# Directory to store profile pictures
PROFILE_PICS_DIR = "static/profile_pics"

# Function to scrape Instagram profile and download profile picture
def scrape_instagram_data(username: str):
    try:
        profile = instaloader.Profile.from_username(L.context, username)
        profile_pic_url = profile.profile_pic_url
        profile_picture_path = os.path.join(PROFILE_PICS_DIR, f"{username}_profile_pic.jpg")

        response = requests.get(profile_pic_url)
        if response.status_code == 200:
            with open(profile_picture_path, 'wb') as f:
                f.write(response.content)
            return profile_picture_path
        else:
            raise ValueError("Failed to download profile picture")

    except instaloader.exceptions.ProfileNotExistsException:
        raise ValueError(f"Profile with username '{username}' does not exist.")
    except Exception as e:
        raise ValueError(f"Error downloading profile picture: {str(e)}")

# Function to get Instagram profile details
def get_instagram_profile_details(username: str):
    try:
        profile = instaloader.Profile.from_username(L.context, username)
        followers = profile.followers
        following = profile.followees
        num_posts = profile.mediacount
        bio = profile.biography
        return {
            "followers": followers,
            "following": following,
            "num_posts": num_posts,
            "bio": bio
        }

    except instaloader.exceptions.ProfileNotExistsException:
        raise ValueError(f"Profile with username '{username}' does not exist.")
    except Exception as e:
        raise ValueError(f"Error fetching profile details: {str(e)}")

# Function to scrape Instagram features for Random Forest
def scrape_instagram_rf(username: str):
    try:
        profile = instaloader.Profile.from_username(L.context, username)
        number_of_posts = profile.mediacount
        
        # Feature 2: Followers
        followers = profile.followers
        
        # Feature 3: Following
        following = profile.followees

        follower_following_ratio = followers / following if following != 0 else 0
        
        # Combine all features into a list
        features = np.array([number_of_posts, followers, following, follower_following_ratio])
        
        return features.reshape(1,-1)

    except instaloader.exceptions.ProfileNotExistsException:
        raise HTTPException(status_code=404, detail=f"Profile '{username}' does not exist.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Preprocessing for CNN
def preprocess_profile_pic_for_cnn(image_path: str):
    try:
        image = Image.open(image_path)
        image = image.resize((224, 224))
        image_array = np.array(image)
        image_array = image_array / 255.0
        image_array = np.expand_dims(image_array, axis=0)
        return image_array
    except Exception as e:
        raise ValueError(f"Error in preprocessing image: {str(e)}")

# CNN Prediction
def predict_with_cnn(image_array):
    try:
        prediction = cnn_model.predict(image_array)
        predicted_class = np.argmax(prediction, axis=1)
        return 1 if predicted_class[0] == 1 else 0  # 1 for fake, 0 for real
    except Exception as e:
        raise ValueError(f"Error in CNN prediction: {str(e)}")

# Random Forest Prediction
def predict_with_random_forest(rf_model,features):
    try:
        prediction = rf_model.predict(features)
        return 1 if prediction[0] == 1 else 0  # 1 for fake, 0 for real
    except Exception as e:
        raise ValueError(f"Error in Random Forest prediction: {str(e)}")



# Define a function to stack the CNN and Random Forest predictions
def stack_models(cnn_pred, rf_pred):
    #Combine CNN and Random Forest predictions
    combined_features = np.array([cnn_pred, rf_pred]).reshape(1, -1)
    
    # Scale the features (if you used scaling during training)
    combined_features = scaler.transform(combined_features)
    
    # Meta-model prediction
    stacked_prediction = meta_model.predict(combined_features)
    
    return "fake" if stacked_prediction[0] == 1 else "real"

#FastAPI app setup
app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/profile_pics", StaticFiles(directory=PROFILE_PICS_DIR), name="profile_pics")

# Serve index.html
@app.get("/")
def read_index():
    return FileResponse('static/index.html')

# Prediction API endpoint
@app.get("/predict/")
def predict_profile(username: str):
    try:
        profile_pic_path = scrape_instagram_data(username)
        profile_details = get_instagram_profile_details(username)
        profile_rf = scrape_instagram_rf(username)

        profile_pic_array = preprocess_profile_pic_for_cnn(profile_pic_path)

        cnn_result = predict_with_cnn(profile_pic_array)
        rf_result = predict_with_random_forest(rf_model,profile_rf)
        print(cnn_result)
        print(rf_result)
        final_result = stack_models(cnn_result, rf_result)

        profile_pic_url = f"/profile_pics/{username}_profile_pic.jpg"
        return {
            "username": username,
            "prediction": final_result,
            "profile_pic_url": profile_pic_url,
            "followers": profile_details["followers"],
            "following": profile_details["following"],
            "num_posts": profile_details["num_posts"],
            "bio": profile_details["bio"]
        }

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
