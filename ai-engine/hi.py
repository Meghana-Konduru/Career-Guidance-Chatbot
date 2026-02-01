import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"

response = requests.get(url)
if response.status_code == 200:
    models = response.json()
    for model in models['models']:
        print(f"Model: {model['name']}")
        print(f"Supported methods: {model['supportedGenerationMethods']}")
        print("---")
else:
    print(f"Error: {response.status_code} - {response.text}")