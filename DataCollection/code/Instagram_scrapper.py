import instaloader
import csv
import re
import os
import time
import random
import logging

# Set up logging
logging.basicConfig(filename='scraping_log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Instaloader with custom User-Agent
L = instaloader.Instaloader()

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.110 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
]

# Rotate User-Agent before making requests
L.context._session.headers.update({'User-Agent': random.choice(USER_AGENTS)})

# Function to log in and handle login issues
def login_instagram(username, password):
    global L  # Ensure L is globally accessible
    try:
        L.login(username, password)
        print(f"Logged in as {username}")
        logging.info(f"Logged in as {username}")
    except Exception as e:
        logging.error(f"Login failed: {e}")
        print(f"Login failed: {e}")
        time.sleep(300)  # Wait for 5 minutes before retrying login
        login_instagram(username, password)

# Function to handle redirection and re-login if necessary
def handle_redirect():
    print("Redirected to login page. You've been logged out.")
    logging.info("Redirected to login page. Reattempting login.")
    time.sleep(600)  # Wait for 10 minutes to avoid further rate-limiting
    login_instagram(USERNAME, PASSWORD)

# Auto-login credentials
USERNAME = 'x_sejal.x'   # Replace with your Instagram username
PASSWORD = '9625212054'  # Replace with your Instagram password

# Attempt login
login_instagram(USERNAME, PASSWORD)

# Load or save session
def load_session(username):
    session_file = f"{username}.session"
    if os.path.exists(session_file):
        print(f"Loading session from {session_file}")
        L.load_session_from_file(username, session_file)
    else:
        print(f"Creating a new session for {username}")
        L.login(username, PASSWORD)
        L.save_session_to_file(session_file)

# Use the session handling function
load_session(USERNAME)

# Create directory to save profile pictures
if not os.path.exists('profile_pictures'):
    os.makedirs('profile_pictures')

# Function to safely download the profile picture
def safe_download_pic(profile, profile_username):
    profile_pic_path = ''
    if profile.profile_pic_url:
        try:
            profile_pic_path = f"profile_pictures/{profile_username}_profile_pic.jpg"
            L.download_pic(profile_pic_path, profile.profile_pic_url, int(time.time()))  # Unix timestamp as int
        except Exception as e:
            logging.error(f"Error downloading profile picture for {profile_username}: {e}")
            print(f"Error downloading profile picture for {profile_username}: {e}")
    return profile_pic_path

# Function to extract profile data
def extract_profile_data(profile_username):
    try:
        print(f"Fetching profile: {profile_username}")
        profile = instaloader.Profile.from_username(L.context, profile_username)

        # Username-related features
        username = profile.username
        username_length = len(username)
        username_digits = sum(c.isdigit() for c in username)
        username_special_chars = len(re.findall(r'\W', username))

        # Full name-related features
        full_name = profile.full_name
        full_name_length = len(full_name)
        full_name_words = len(full_name.split())
        username_similarity = 1 if full_name.lower() in username.lower() else 0

        # Profile picture
        has_profile_pic = 1 if profile.profile_pic_url else 0
        profile_pic_path = safe_download_pic(profile, profile_username)

        # Bio-related features
        bio = profile.biography
        bio_length = len(bio)
        bio_words = len(bio.split())
        suspicious_words = ["money", "giveaway", "free", "bitcoin", "forex", "investment","buy followers","buy likes","viral","click here","trading","win","free trial","coupon","voucher","discount","exclusive deal","paytm","profits"]
        bio_has_suspicious = 1 if any(word in bio.lower() for word in suspicious_words) else 0

        # External URL
        external_url = profile.external_url
        has_external_url = 1 if external_url else 0

        # Privacy setting
        is_private = profile.is_private

        # Posts, followers, following counts
        num_posts = profile.mediacount
        num_followers = profile.followers
        num_following = profile.followees

        print(f"Successfully fetched data for {profile_username}")

        # Return the extracted data as a list
        return [
            username, username_length, username_digits, username_special_chars,
            full_name, full_name_length, full_name_words, username_similarity,
            has_profile_pic, profile_pic_path, bio, bio_length, bio_words, bio_has_suspicious,
            external_url, has_external_url, is_private, num_posts, num_followers, num_following
        ]

    except instaloader.exceptions.ProfileNotExistsException:
        print(f"Profile {profile_username} does not exist.")
        logging.error(f"Profile {profile_username} does not exist.")
        return None
    except instaloader.exceptions.PrivateProfileNotFollowedException:
        print(f"Profile {profile_username} is private, and you do not follow it.")
        logging.error(f"Profile {profile_username} is private, and you do not follow it.")
        return None
    except instaloader.exceptions.ConnectionException as e:
        logging.error(f"Connection issue while fetching {profile_username}: {str(e)}")
        print(f"Connection issue while fetching {profile_username}: {str(e)}")
        return None
    except Exception as e:
        if "redirected to login" in str(e).lower():
            handle_redirect()  # Handle login redirects
        else:
            logging.error(f"An error occurred while fetching {profile_username}: {str(e)}")
            print(f"An error occurred while fetching {profile_username}: {str(e)}")
        return None

# List of Instagram usernames to scrape based on seed account followers
seed_account = 'allure.4u'  # Replace with your seed account username

# Fetch seed account profile with retry logic in case of rate limiting
attempts = 1
while attempts <= 5:
    try:
        profile = instaloader.Profile.from_username(L.context, seed_account)
        break  # Exit the loop if successful
    except instaloader.exceptions.ConnectionException as e:
        logging.error(f"Failed to fetch seed account profile: {e}")
        handle_redirect()
        attempts += 1

# Get a list of followers
try:
    followers = profile.get_followers()
    followers_usernames = [follower.username for follower in followers]
    print(f"Fetched {len(followers_usernames)} followers from {seed_account}")
except Exception as e:
    logging.error(f"Failed to fetch followers: {e}")
    print(f"Failed to fetch followers: {e}")
    exit()

# Check if followers list is empty
if not followers_usernames:
    print("No followers found for scraping.")
    exit()

# CSV file to store the scraped data
csv_file = 'instagram_profile_data.csv'

# CSV header
header = [
    'Username', 'Username Length', 'Username Digits', 'Username Special Chars',
    'Full Name', 'Full Name Length', 'Full Name Words', 'Username Similarity',
    'Has Profile Pic', 'Profile Pic Path', 'Bio', 'Bio Length', 'Bio Words', 'Bio Has Suspicious',
    'External URL', 'Has External URL', 'Is Private', 'Number of Posts', 'Followers', 'Following'
]

def get_existing_usernames(csv_file):
    existing_usernames = set()  # Use a set for fast lookups
    if os.path.exists(csv_file):
        with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header
            for row in reader:
                if row:  # Ensure it's not an empty row
                    existing_usernames.add(row[0])  # Add the username (first column)
    return existing_usernames

# Open the CSV file and write the header
with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    
    if os.stat(csv_file).st_size == 0:
        writer.writerow(header)
    
    # Batch process followers in sets of 50
    batch_size = 50
    total_followers = len(followers_usernames)
    existing_usernames = get_existing_usernames(csv_file)

    for start_idx in range(0, total_followers, batch_size):
        batch = followers_usernames[start_idx:start_idx + batch_size]

        for follower_username in batch:
            if follower_username in existing_usernames:
                print(f"skipping{follower_username} , already in csv")
                continue

            profile_data = extract_profile_data(follower_username)
            if profile_data:
                writer.writerow(profile_data)
                print(f"Data written for {follower_username}")
                delay = random.randint(10, 90)  # Random delay between 30 seconds and 3 minutes
                print(f"Sleeping for {delay} seconds to avoid rate limiting...")
                time.sleep(delay)
        file.flush()
        os.fsync(file.fileno())  # Ensures data is written to disk
        # Sleep between batches to avoid rate limiting (adjust delay as needed)
        print(f"Finished processing batch {start_idx//batch_size + 1}, sleeping between batches...")
        time.sleep(random.randint(300, 350))  # Sleep for 5 mins
print(f"Data collection complete. Saved to {csv_file}.")
