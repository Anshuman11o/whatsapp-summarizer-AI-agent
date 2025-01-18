from openai import OpenAI
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# OpenAI API Key
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=OPENAI_API_KEY)

# Configure the logger
logging.basicConfig(
    filename="media_processing.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger()

def generate_summary(content,media_type="text"):
    try:
        logger.info(f"Generating summary for media type: {media_type}")

        prompt = f"The following is text extracted from a {media_type} file. Summarize it appropriately:\n\n{content}"

        # Call OpenAI API to generate a summary
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Ensure this is set to an accessible GPT model, gpt-4o-mini, gpt-3.5-turbo, gpt-4
            messages=[
                {"role": "system", "content": "You are an expert summarizer."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.5,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )

        logger.info("Summary generated successfully.")
        # Extract and return the summary from the response
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating summary: {e}"