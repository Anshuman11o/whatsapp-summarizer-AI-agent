import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI API Key
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY

def generate_summary(text):
    try:
        # Call OpenAI API to generate a summary
        response = openai.Completion.create(
            engine="text-davinci-003",  # Adjust engine as needed
            prompt=f"Summarize the following text:\n{text}",
            max_tokens=100,
            temperature=0.7,
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Error generating summary: {e}"