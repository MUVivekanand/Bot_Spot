## BotSpot

We built this BotSpot for a 24-hr Hackathon. This webapp detects the bot accounts in Instagram and Twitter and  has a minimalistic UI. the app asks for a username and scrapes the user details and pass into the models which we built and classify the user as bot or human.<br/>

### Models

1.For Instagram, we used XGBoost. <br/>
2.For Twitter, we used BERT model with a perceptron DL layer and passed into LLM for a structured output. <br />

### Tech Stack

1.Frontend - React.js
2.Backend - Python AI/ML frameworks, Flask