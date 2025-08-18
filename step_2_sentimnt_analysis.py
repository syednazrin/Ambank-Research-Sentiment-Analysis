from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json
import time
import re
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Function to parse JSON from LLM response
def parse_json_response(response_text, tweet_data):
    """
    Parse JSON from the LLM response, with fallback handling for confidence scores
    """
    try:
        # Try to find JSON in the response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            parsed = json.loads(json_str)
            # Add timestamp information to the parsed result
            parsed["timestamp"] = tweet_data["timestamp"]
            parsed["rawTimestamp"] = tweet_data["rawTimestamp"]
            
            # Ensure confidence_score is within valid range
            if "confidence_score" in parsed:
                score = parsed["confidence_score"]
                if not isinstance(score, (int, float)) or score < 0 or score > 1:
                    parsed["confidence_score"] = 0.5  # Default neutral score
            else:
                parsed["confidence_score"] = 0.5  # Default if missing
                
            return parsed
        else:
            # Fallback: try to estimate confidence from text patterns
            confidence_score = 0.5  # Default neutral
            reasoning = "Unable to parse structured response"
            
            # Basic pattern matching for fallback scoring
            text_lower = response_text.lower()
            if "strongly" in text_lower or "definitely" in text_lower or "clear" in text_lower:
                if "boycott" in text_lower or "negative" in text_lower:
                    confidence_score = 0.8
                elif "positive" in text_lower or "support" in text_lower:
                    confidence_score = 0.2
            elif "boycott" in text_lower or "against" in text_lower:
                confidence_score = 0.7
            elif "support" in text_lower or "positive" in text_lower:
                confidence_score = 0.3
            
            return {
                "tweet": tweet_data["text"],
                "confidence_score": confidence_score,
                "reasoning": reasoning,
                "timestamp": tweet_data["timestamp"],
                "rawTimestamp": tweet_data["rawTimestamp"]
            }
    except json.JSONDecodeError:
        # Fallback scoring based on keywords
        text_lower = response_text.lower()
        confidence_score = 0.5  # Default neutral
        
        # Simple keyword-based scoring
        if "boycott" in text_lower or "against" in text_lower or "negative" in text_lower:
            confidence_score = 0.7
        elif "support" in text_lower or "positive" in text_lower or "good" in text_lower:
            confidence_score = 0.3
        
        return {
            "tweet": tweet_data["text"],
            "confidence_score": confidence_score,
            "reasoning": "Fallback parsing due to JSON decode error",
            "timestamp": tweet_data["timestamp"],
            "rawTimestamp": tweet_data["rawTimestamp"]
        }

# Load real tweets from the scraped data
def load_tweets_from_json(filename):
    """
    Load tweets with timestamps from the threads scraper JSON file
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract text and timestamp from posts
        tweets_data = []
        for post in data['posts']:
            if post.get('text'):
                tweets_data.append({
                    'text': post['text'],
                    'timestamp': post.get('timestamp', ''),
                    'rawTimestamp': post.get('rawTimestamp', '')
                })
        
        print(f"Loaded {len(tweets_data)} tweets from {filename}")
        return tweets_data
    except FileNotFoundError:
        print(f"Error: File {filename} not found!")
        return []
    except Exception as e:
        print(f"Error loading tweets: {e}")
        return []

# Load tweets from the scraped data
tweets_data = load_tweets_from_json(r"C:\Users\Syed Nazrin\Downloads\Nestle Sentiment Analysis\threads_posts_2025-08-12_23-30.json")

# Check if we have tweets to process
if not tweets_data:
    print("No tweets found! Please check the JSON file.")
    exit(1)

# Initialize GPT-4o-mini model
llm = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    temperature=float(os.getenv("OPENAI_TEMPERATURE", "0")),
    api_key=os.getenv("OPENAI_API_KEY"),
    max_tokens=150,
)

# Set up the string output parser
parser = StrOutputParser()

# System prompt for detailed confidence-based sentiment analysis
system_prompt = """
You are an advanced sentiment analysis model specialized in detecting attitudes toward Nestle, particularly regarding boycotts and brand sentiment.

Your task is to analyze each post and assign a confidence score from 0 to 1 that represents how negative or positive the sentiment is toward Nestle:

CONFIDENCE SCORE SCALE:
• 0.0 - 0.1: Extremely negative toward Nestle, strongly pro-boycott, aggressive anti-Nestle sentiment
• 0.1 - 0.3: Clearly negative toward Nestle, supports boycott, critical of company practices
• 0.3 - 0.4: Somewhat negative, mild criticism, questioning Nestle's actions
• 0.4 - 0.6: Neutral, balanced, or unclear sentiment toward Nestle
• 0.6 - 0.7: Somewhat positive, mild support, or defensive of Nestle
• 0.7 - 0.9: Clearly positive toward Nestle, opposes boycotts, supports the company
• 0.9 - 1.0: Extremely positive toward Nestle, strong brand advocacy, actively promotes Nestle

ANALYSIS CRITERIA:
1. BOYCOTT LANGUAGE: Look for explicit calls to boycott, avoid, or protest Nestle products
2. CRITICISM INTENSITY: Assess how harsh or mild any criticism is
3. EMOTIONAL TONE: Consider anger, frustration, disappointment vs. support, praise, defense
4. ACTION ORIENTATION: Does the post encourage action against or for Nestle?
5. CONTEXT AWARENESS: Consider sarcasm, irony, or indirect references
6. BRAND MENTIONS: How Nestle products/brands are discussed (negative, neutral, positive)

EXAMPLES OF SCORING:
• "Nestle is evil, boycott all their products!" → 0.1 (strongly pro-boycott)
• "I'm disappointed in Nestle's water practices" → 0.3 (critical but measured)
• "Just saw news about Nestle, not sure what to think" → 0.5 (neutral/uncertain)
• "Nestle makes good chocolate though" → 0.7 (mildly positive)
• "Love my Nestle coffee every morning!" → 0.9 (brand advocacy)

SPECIAL CONSIDERATIONS:
- Posts mentioning boycotts should generally score 0.4 or lower unless defending Nestle
- Neutral brand mentions (just naming products) should score around 0.5
- Consider the overall message intent, not just individual words
- Factor in the strength of language used (mild vs. strong expressions)
- Account for implicit vs. explicit sentiment

You must respond with valid JSON in exactly this format:
{{
  "tweet": "<original post text>",
  "confidence_score": <number between 0 and 1 with up to 2 decimal places>,
  "reasoning": "<detailed explanation of why you assigned this score, mentioning specific words/phrases that influenced your decision>"
}}

Be precise with your scoring and provide clear reasoning for your confidence assessment.
"""

# Prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("user", "Classify this tweet: {tweet}")
])

# Build the chain
chain = prompt | llm | parser

before = time.time()

results = []
# Run classification on each tweet
for i, tweet_data in enumerate(tweets_data, 1):
    try:
        print(f"Processing tweet {i}/{len(tweets_data)}...")
        
        # Get the raw response from the chain
        raw_response = chain.invoke({"tweet": tweet_data["text"]})
        print(f"Raw response: {raw_response}")
        
        # Parse the JSON from the response
        result = parse_json_response(raw_response, tweet_data)
        
        # Ensure timestamps and required fields are always included
        if "timestamp" not in result:
            result["timestamp"] = tweet_data["timestamp"]
        if "rawTimestamp" not in result:
            result["rawTimestamp"] = tweet_data["rawTimestamp"]
        if "confidence_score" not in result:
            result["confidence_score"] = 0.5
        if "reasoning" not in result:
            result["reasoning"] = "No reasoning provided"
            
        print(f"Parsed result: {result}")
        
        results.append(result)
        print("-" * 50)
        
    except Exception as e:
        print(f"Error processing tweet: {tweet_data['text']}")
        print(f"Error: {e}")
        # Fallback: create manual JSON structure with neutral score
        fallback_result = {
            "tweet": tweet_data["text"],
            "confidence_score": 0.5,
            "reasoning": f"Error during processing: {str(e)}",
            "timestamp": tweet_data["timestamp"],
            "rawTimestamp": tweet_data["rawTimestamp"]
        }
        results.append(fallback_result)
        print("-" * 50)

after = time.time()

print(f"Time taken: {after - before:.2f} seconds")

# Save results to JSON file
output_filename = "nestle_threads_sentiment_analysis_2025-08-12.json"
with open(output_filename, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"Saved results to {output_filename}")

# Print detailed summary with confidence score analysis
print(f"\nDetailed Summary:")
print(f"Total posts processed: {len(results)}")

# Calculate confidence score statistics
confidence_scores = [r.get('confidence_score', 0.5) for r in results]
avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5

# Categorize by confidence ranges
extremely_negative = sum(1 for score in confidence_scores if 0.0 <= score <= 0.1)
clearly_negative = sum(1 for score in confidence_scores if 0.1 < score <= 0.3)
somewhat_negative = sum(1 for score in confidence_scores if 0.3 < score <= 0.4)
neutral = sum(1 for score in confidence_scores if 0.4 < score <= 0.6)
somewhat_positive = sum(1 for score in confidence_scores if 0.6 < score <= 0.7)
clearly_positive = sum(1 for score in confidence_scores if 0.7 < score <= 0.9)
extremely_positive = sum(1 for score in confidence_scores if 0.9 < score <= 1.0)

# Count errors (posts with reasoning containing "Error")
errors = sum(1 for r in results if 'Error' in r.get('reasoning', ''))

print(f"\nAverage confidence score: {avg_confidence:.3f}")
print(f"(Lower scores = more negative toward Nestle/pro-boycott)")
print(f"(Higher scores = more positive toward Nestle)")

print(f"\nConfidence Score Distribution:")
print(f"Extremely Negative (0.0-0.1): {extremely_negative} posts")
print(f"Clearly Negative (0.1-0.3): {clearly_negative} posts")  
print(f"Somewhat Negative (0.3-0.4): {somewhat_negative} posts")
print(f"Neutral (0.4-0.6): {neutral} posts")
print(f"Somewhat Positive (0.6-0.7): {somewhat_positive} posts")
print(f"Clearly Positive (0.7-0.9): {clearly_positive} posts")
print(f"Extremely Positive (0.9-1.0): {extremely_positive} posts")
print(f"Processing Errors: {errors} posts")

# Summary categories
total_negative = extremely_negative + clearly_negative + somewhat_negative
total_positive = somewhat_positive + clearly_positive + extremely_positive

print(f"\nOverall Sentiment Summary:")
print(f"Negative toward Nestle: {total_negative} posts ({total_negative/len(results)*100:.1f}%)")
print(f"Neutral: {neutral} posts ({neutral/len(results)*100:.1f}%)")
print(f"Positive toward Nestle: {total_positive} posts ({total_positive/len(results)*100:.1f}%)")