from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import instaloader
import requests
import pickle
from io import BytesIO
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os
import tweepy
import pandas as pd
import re

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enables CORS for all routes

# Initialize Instaloader
loader = instaloader.Instaloader()
bearer_token = os.getenv("TWEET")

client = tweepy.Client(bearer_token=bearer_token)

# Load the pre-trained model
with open("fake_account_model.pkl", "rb") as model_file:
    model = pickle.load(model_file)

@app.route("/check", methods=["POST"])
def check_account():
    try:
        data = request.get_json()
        username = data.get("username")

        if not username:
            return jsonify({"error": "Username is required"}), 400

        # Fetch Instagram profile
        profile = instaloader.Profile.from_username(loader.context, username)

        # Prepare the feature data
        user_data = {
            "userFollowerCount": profile.followers,
            "userFollowingCount": profile.followees,
            "userMediaCount": profile.mediacount,
            "userHasProfilPic": bool(profile.profile_pic_url),  # Convert to boolean
            "userIsPrivate": profile.is_private,
            "usernameLength": len(profile.username)  # Calculate username length
        }

        # Convert to model input format
        feature_values = [
            user_data["userFollowerCount"],
            user_data["userFollowingCount"],
            user_data["userMediaCount"],
            int(user_data["userHasProfilPic"]),  # Convert boolean to int
            int(user_data["userIsPrivate"]),  # Convert boolean to int
            user_data["usernameLength"]
        ]

        def analyze_instagram_account(model, follower_count, following_count, media_count, 
                                    has_profile_pic, is_private, username_length, verbose=True):
            """
            Analyze an Instagram account with detailed explanation of risk factors.
            """
            import pandas as pd
            import numpy as np
            
            # Create sample data
            sample = pd.DataFrame({
                'userFollowerCount': [follower_count],
                'userFollowingCount': [following_count],
                'userMediaCount': [media_count],
                'userHasProfilPic': [has_profile_pic],
                'userIsPrivate': [is_private],
                'usernameLength': [username_length]
            })
            
            # Make prediction
            prediction = model.predict(sample)[0]
            probability = model.predict_proba(sample)[0]
            fake_probability = probability[1]
            
            # Analyze risk factors
            risk_factors = []
            
            # Following to follower ratio
            if following_count / max(follower_count, 1) > 10:
                risk_factors.append(f"High following/follower ratio: {following_count}/{follower_count}")
            
            # Low follower count
            if follower_count < 50:
                risk_factors.append(f"Very low follower count: {follower_count}")
            
            # No profile picture
            if not has_profile_pic:
                risk_factors.append("No profile picture")
            
            # Unusual username length
            if username_length > 15:
                risk_factors.append(f"Unusually long username: {username_length} characters")
            
            # Unusual media to follower ratio
            if media_count > follower_count:
                risk_factors.append(f"High media count ({media_count}) compared to followers ({follower_count})")
            
            if verbose:
                print("\nAccount Analysis Results:")
                print("-" * 50)
                print(f"Prediction: {'FAKE' if prediction == 1 else 'REAL'}")
                print(f"Confidence: {max(probability) * 100:.2f}%")
                print(f"Probability of being fake: {fake_probability * 100:.2f}%")
                print("\nAccount Features:")
                print(f"- Followers: {follower_count}")
                print(f"- Following: {following_count}")
                print(f"- Media Count: {media_count}")
                print(f"- Has Profile Picture: {'Yes' if has_profile_pic else 'No'}")
                print(f"- Private Account: {'Yes' if is_private else 'No'}")
                print(f"- Username Length: {username_length}")
                
                if risk_factors:
                    print("\nPotential Risk Factors:")
                    for factor in risk_factors:
                        print(f"- {factor}")
                else:
                    print("\nNo significant risk factors identified")
            
            return prediction, fake_probability, risk_factors


        # Get prediction
        follower_count = profile.followers
        following_count = profile.followees
        media_count = profile.mediacount
        has_profile_pic = bool(profile.profile_pic_url)  # Convert to boolean
        is_private = profile.is_private
        username_length = len(profile.username)  # Calculate username length

        # Call analyze_instagram_account function
        prediction, prob, risks = analyze_instagram_account(
            model, follower_count, following_count, media_count, 
            has_profile_pic, is_private, username_length, verbose=True
        )

        return jsonify({
            "username": profile.username,
            "user_id": profile.userid,
            "followers": profile.followers,
            "following": profile.followees,
            "bio": profile.biography,
            "profile_pic": profile.profile_pic_url,
            "is_private": profile.is_private,
            "post_count": profile.mediacount,
            "prediction": str(prediction),
            "prob": f"{prob * 100:.2f}%",
            "risks": "\n".join(risks) if risks else "No significant risk factors identified"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/proxy-image")
def proxy_image():
    image_url = request.args.get("url")
    if not image_url:
        return jsonify({"error": "Image URL is required"}), 400

    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        return send_file(BytesIO(response.content), mimetype="image/jpeg")

    except requests.RequestException:
        return jsonify({"error": "Failed to load image"}), 500
    
llm = AzureChatOpenAI(
    api_key=os.getenv("AZURE_KEY"),
    api_version="2023-03-15-preview",
    temperature=0,
    max_tokens=None,
    azure_endpoint=os.getenv("AZURE_ENDPOINT"),
    azure_deployment="gpt-4o",
)

@app.route("/analyze_twitter_bot", methods=["POST"])
def analyze_twitter_bot():
    try:
        data = request.get_json()
        username = data.get("username")

        if not username:
            return jsonify({"error": "Username is required"}), 400

        # Fetch user details
        user = client.get_user(username=username, user_fields=["public_metrics", "verified_type"])
        user_id = user.data.id
        follower_count = user.data.public_metrics["followers_count"]
        verified_type = user.data.verified_type  # "blue", "business", etc.
        is_verified = verified_type is not None  # Convert to boolean

        # Fetch latest tweets
        user_tweets = client.get_users_tweets(id=user_id, max_results=10, tweet_fields=["public_metrics"])

        # Process tweets
        tweet_list = []
        for tweet in user_tweets.data:
            clean_text = re.sub(r"https://t\.co/\S+", "", tweet.text)  # Remove links
            retweet_count = tweet.public_metrics["retweet_count"]
            mention_count = len(re.findall(r"@\w+", tweet.text))  # Count @mentions

            tweet_list.append({
                "username": username,
                "follower_count": follower_count,
                "is_verified": is_verified,
                "verified_type": verified_type,
                "tweet_text": clean_text.strip(),
                "retweet_count": retweet_count,
                "mention_count": mention_count
            })

        # Convert to DataFrame and save as CSV
        df = pd.DataFrame(tweet_list)
        df.to_csv(f"tweet_csvs\\{username}_analysis.csv", index=False)

        # Format prompt for GPT-4o
        prompt_template = ChatPromptTemplate.from_template("""
            You are an expert in detecting Twitter bots based on tweet content and metadata.

            Given the following tweet data:
            {tweet_list}

            Your task:
            - Analyze the tweet and user features.
            - Detect if the tweet is likely from a bot.
            - Provide a probability score (0-1) where 0 = definitely human and 1 = definitely bot.
            - Justify your reasoning based on retweet count, follower count, verification status, and spam-like words.

            Return the result with the bot probability and tell the model from which probability is taken is from BERT model and an explanation.
        """)

        # Invoke GPT-4o
        response = llm.invoke(prompt_template.format(tweet_list=tweet_list))
        return jsonify({
            "username": username,
            "follower_count": follower_count,
            "is_verified": is_verified,
            "verified_type": verified_type,
            "analysis": response.content
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
