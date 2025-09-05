import os
from flask import Flask, request, jsonify
from transformers import pipeline
import requests

app = Flask(__name__)

# Load API keys from environment variables for security
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")

# Load Hugging Face model
try:
    classifier = pipeline(
        "text-classification",
        model="jy46604790/Fake-News-Bert-Detect",
    )
except Exception as e:
    print(f"Error loading model: {e}")
    classifier = None


def google_custom_search(query):
    """Call Google Custom Search API and return list of result titles and snippets."""
    if not GOOGLE_API_KEY or not SEARCH_ENGINE_ID:
        return []

    url = (
        "https://www.googleapis.com/customsearch/v1"
        f"?key={GOOGLE_API_KEY}&cx={SEARCH_ENGINE_ID}&q={query}"
    )
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        items = data.get("items", [])
        results = []
        for item in items:
            title = item.get("title", "")
            snippet = item.get("snippet", "")
            results.append(f"{title} {snippet}")
        return results
    except Exception as e:
        print(f"Google Search API error: {e}")
        return []


def newsapi_search(query):
    """Call NewsAPI and return list of article titles and descriptions."""
    if not NEWSAPI_KEY:
        return []

    url = (
        "https://newsapi.org/v2/everything"
        f"?q={query}&apiKey={NEWSAPI_KEY}&language=en&pageSize=5"
    )
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        articles = data.get("articles", [])
        results = []
        for article in articles:
            title = article.get("title", "")
            description = article.get("description", "")
            results.append(f"{title} {description}")
        return results
    except Exception as e:
        print(f"NewsAPI error: {e}")
        return []


@app.route("/check_text", methods=["POST"])
def check_text():
    """
    Handles POST requests to check a piece of text for misinformation.
    Combines model prediction with external news verification.
    """
    if not classifier:
        return jsonify({"error": "Model could not be loaded."}), 500

    data = request.json
    if not data or "text" not in data:
        return jsonify({"error": "Invalid input. 'text' field is required."}), 400

    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "Empty text provided."}), 400

    try:
        # 1. Model prediction
        result = classifier(text)[0]
        label = result["label"].upper()
        score = round(result["score"], 3)

        # 2. External verification
        google_results = google_custom_search(text)
        news_results = newsapi_search(text)

        credible_sources_count = len(google_results) + len(news_results)

        # 3. Combine model and external signals
        if score < 0.7:
            verdict = "Suspicious"
        elif label in ["REAL", "LABEL_1"]:
            if credible_sources_count == 0:
                verdict = "Suspicious (no credible sources found)"
            else:
                verdict = "True"
        elif label in ["FAKE", "LABEL_0"]:
            if credible_sources_count > 3:
                verdict = "Suspicious (credible sources found)"
            else:
                verdict = "Fake"
        else:
            verdict = "Suspicious"

        return jsonify(
            {
                "verdict": verdict,
                "confidence": score,
                "external_sources_found": credible_sources_count,
                "model_label": label,
            }
        )

    except Exception as e:
        return jsonify({"error": f"An error occurred during classification: {e}"}), 500


@app.route("/", methods=["GET"])
def home():
    return "SmartAssist Backend is running. Use the /check_text endpoint with a POST request."


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
