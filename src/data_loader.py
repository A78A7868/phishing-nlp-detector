import os
import random
import requests
import pandas as pd

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
os.makedirs(RAW_DATA_DIR, exist_ok=True)
RAW_FILE_PATH = os.path.join(RAW_DATA_DIR, "Phishing_Email.csv")

# Constants for Kaggle phishing email dataset format
EMAIL_TEXT_COL = "Email Text"
EMAIL_TYPE_COL = "Email Type"
PHISHING_LABEL = "Phishing Email"
SAFE_LABEL = "Safe Email"

# Direct raw dataset link from github replica of Kaggle dataset
DATASET_URL = "https://raw.githubusercontent.com/uzmabb182/Data_622/main/final_project_data_622/Phishing_Email.csv"

def download_dataset():
    """
    Attempts to download the phishing emails dataset from a public raw GitHub URL.
    Falls back to generating a high-quality synthetic dataset if the network is down or URL fails.
    """
    print(f"Attempting to download dataset from: {DATASET_URL}")
    try:
        response = requests.get(DATASET_URL, timeout=15)
        if response.status_code == 200:
            with open(RAW_FILE_PATH, "wb") as f:
                f.write(response.content)
            print(f"Successfully downloaded and saved raw dataset to {RAW_FILE_PATH}")
            # Verify CSV file is valid
            df = pd.read_csv(RAW_FILE_PATH)
            if EMAIL_TEXT_COL in df.columns and EMAIL_TYPE_COL in df.columns:
                print(f"Dataset verified successfully. Shape: {df.shape}")
                return RAW_FILE_PATH
            else:
                print("Downloaded file does not have the expected columns. Falling back to synthetic data.")
        else:
            print(f"Download failed with status code {response.status_code}. Falling back to synthetic data.")
    except Exception as e:
        print(f"Network error or timeout occurred during download: {e}")
        print("Falling back to synthetic data generation.")
    
    # Fallback: Generate high-quality synthetic dataset
    return generate_synthetic_dataset()

def generate_synthetic_dataset(num_samples=250):
    """
    Generates a high-quality synthetic dataset of phishing and safe emails.
    Includes rich structural characteristics: urgency words, URLs, sender patterns, etc.
    """
    print("Generating a realistic synthetic phishing/legitimate email dataset...")
    
    phishing_templates = [
        "Dear customer, your online bank account has been suspended due to suspicious login attempts. Please click the link to verify your identity immediately: http://secure-banking-verify-{id}.com/login. Failure to do so within 24 hours will result in permanent suspension of services. Urgent action required!",
        "Urgent Notice: We detected an unauthorized attempt to access your account from an unknown IP address. Please confirm your credentials by visiting our security portal: http://account-update-portal-{id}.org. Thank you for helping us protect your account.",
        "Congratulations! You have won a $1,000 Amazon Gift Card! Click here to claim your prize now: http://free-rewards-{id}.net/giftcard. Hurry, this offer expires in 12 hours! No purchase necessary.",
        "Your Netflix subscription payment has failed. To avoid service disruption, please update your billing information at http://netflix-billing-support-{id}.com. If you do not update your payment details, your account will be suspended.",
        "ATTENTION: Internal Revenue Service (IRS) Refund Notice. You are eligible to receive a tax refund of $450.50. Please submit the tax refund request form: http://irs-tax-refund-{id}.gov-portal.net. Note: Do not reply to this email.",
        "Dear customer, your PayPal account has been limited. We noticed some unusual activity on your card associated with this account. To lift the restriction, please verify your details here: http://paypal-resolution-center-{id}.com. Thank you for your cooperation.",
        "Hey! Check out this awesome video of you at the party last night! You look so funny lol. Watch it here: http://social-media-video-{id}.com/view-profile. Make sure to log in to see it.",
        "Important Security Update: Your email account password expires today. Please click http://mail-server-security-renew-{id}.net to keep your current password. If you do not renew, your mail account will be deactivated."
    ]
    
    safe_templates = [
        "Hi Team, please find attached the minutes of our project sync meeting from today. Let me know if you have any questions or additions. We need to finalize the design by Friday afternoon.",
        "Hi, are we still on for lunch tomorrow at 12:30 PM? Let me know if that works for you or if we should reschedule for later in the week.",
        "Your weekly subscription receipt for Spotify Premium is ready. The amount of $9.99 has been charged to your card ending in 4321. Thank you for choosing Spotify. If you have questions, visit our help section.",
        "Hi everyone, just a reminder that the office will be closed on Monday for the national holiday. Have a wonderful long weekend, and see you all on Tuesday morning!",
        "Dear student, your final grade for CS101: Introduction to Computer Science has been posted on the student portal. You can view your grades and feedback online. If you have questions, please reach out during office hours.",
        "Thanks for signing up for our weekly tech newsletter. In this issue, we explore the rise of machine learning, NLP in cybersecurity, and best practices for writing clean code in Python. Read the full article on our blog.",
        "Hi John, I took a look at the pull request you submitted. The changes look great, but I left a couple of minor comments about variable naming. Please review and merge once updated.",
        "Dear Valued Customer, your order #7890123 has been shipped and is on its way. You can track your package details using the link provided by the carrier. Thank you for shopping with us!"
    ]
    
    data = []
    # Mix of phishing and safe emails
    for i in range(num_samples):
        # 45% phishing, 55% safe split
        is_phishing = random.random() < 0.45
        email_id = random.randint(1000, 9999)
        
        if is_phishing:
            template = random.choice(phishing_templates)
            text = template.format(id=email_id)
            label = PHISHING_LABEL
        else:
            template = random.choice(safe_templates)
            text = template.format(id=email_id)
            label = SAFE_LABEL
            
        data.append({
            "Email Text": text,
            "Email Type": label
        })
        
    df = pd.DataFrame(data)
    df.to_csv(RAW_FILE_PATH, index=False)
    print(f"Successfully generated and saved {num_samples} synthetic email samples to {RAW_FILE_PATH}")
    return RAW_FILE_PATH

if __name__ == "__main__":
    download_dataset()
