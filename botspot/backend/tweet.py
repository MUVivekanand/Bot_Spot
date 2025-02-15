from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()

import tweepy
import pandas as pd
import re

# Replace with your API v2 Bearer Token
bearer_token = os.getenv("TWEET")

client = tweepy.Client(bearer_token=bearer_token)

username = "22z23144138"

# Fetch user details with verified_type
user = client.get_user(username=username, user_fields=["public_metrics", "verified_type"])

# Extract required details
user_id = user.data.id
follower_count = user.data.public_metrics["followers_count"]
verified_type = user.data.verified_type  # Can be "blue", "business", etc.

# Convert to a boolean
is_verified = verified_type is not None

# Fetch latest 10 tweets with public metrics
elonmusk_tweets = client.get_users_tweets(id=user_id, max_results=10, tweet_fields=["public_metrics"])

# Prepare tweet list
tweet_list = []
for tweet in elonmusk_tweets.data:
    clean_text = re.sub(r"https://t\.co/\S+", "", tweet.text)  # Remove links

    # Extract retweet count
    retweet_count = tweet.public_metrics["retweet_count"]

    # Count mentions (@username) in the tweet
    mention_count = len(re.findall(r"@\w+", tweet.text))

    tweet_list.append({
        "username": username,
        "follower_count": follower_count,
        "is_verified": is_verified,
        "verified_type": verified_type,
        "tweet_text": clean_text.strip(),
        "retweet_count": retweet_count,
        "mention_count": mention_count
    })

# Convert to DataFrame
df = pd.DataFrame(tweet_list)

# Save as CSV file
csv_filename = "karthi_bot.csv"
df.to_csv(csv_filename, index=False)

print(f"✅ Data saved to {csv_filename}")
print(df.head(10))  # Print first 10 rows
# df = pd.read_csv("elonmusk_tweets.csv")
# tweet_list = df.values.tolist()

print(tweet_list)


llm = AzureChatOpenAI(
    api_key=os.getenv("AZURE_KEY"),
    api_version="2023-03-15-preview",
    temperature=0,
    max_tokens=None,
    azure_endpoint=os.getenv("AZURE_ENDPOINT"),
    azure_deployment="gpt-4o",
)

prompt = (
    """
    You are an expert in detecting Twitter bots based on tweet content and metadata.
    
    Given the following tweet data:
    {tweet_list}
    
    Your task:
    - Analyze the tweet and user features.
    - Detect if the tweet is likely from a bot.
    - Provide a probability score (0-1) where 0 = definitely human and 1 = definitely bot.
    - Justify your reasoning based on retweet count, follower count, verification status, and spam-like words.
    
    Return the result with how much do you think for bot probability and explained reasoning .

    """
)

prompt_template = ChatPromptTemplate.from_template(prompt)

response = llm.invoke(prompt_template.format(tweet_list=tweet_list))

# Print the output
print(response.content)
