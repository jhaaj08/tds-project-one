import requests

# Replace with your actual AI Proxy token from https://aiproxy.sanand.workers.dev/
AIPROXY_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIxZjEwMDU3NDVAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.QIzF-en4LaXJxOYQgwh9W1dgvn1QvLJL6_40g98vZU0"

API_URL = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
MODEL_NAME = "gpt-4o-mini"  # Change if model availability differs


def query_llm(prompt: str) -> str:
    """Query the AI Proxy LLM and return the response."""
    headers = {
        "Authorization": f"Bearer {AIPROXY_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500,
        "temperature": 0.7
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        response.raise_for_status()  # Raise error for non-200 responses

        result = response.json()
        return result["choices"][0]["message"]["content"].strip()

    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
        raise

    except KeyError:
        print(f"Unexpected response format: {response.json()}")
        raise Exception("Failed to extract LLM response")


def list_available_models():
    """Fetch and print available models from AI Proxy."""
    headers = {"Authorization": f"Bearer {AIPROXY_TOKEN}"}
    models_url = "https://aiproxy.sanand.workers.dev/openai/v1/models"

    try:
        response = requests.get(models_url, headers=headers)
        response.raise_for_status()
        models = response.json()["data"]
        available_models = [model["id"] for model in models]

        print("Available models:", available_models)
        return available_models

    except requests.exceptions.RequestException as e:
        print(f"Error fetching models: {e}")
        return []


if __name__ == "__main__":
    # Uncomment to check available models before running queries
    # list_available_models()

    prompt = "Extract the sender's email address from this email:\n\nFrom: John Doe <john.doe@example.com>\nSubject: Meeting Reminder"
    print(query_llm(prompt))
