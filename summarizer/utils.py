from openai import OpenAI
import os
from dotenv import load_dotenv
import logging
from openai import AuthenticationError, RateLimitError, OpenAIError

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

def handle_error(e, user_message="Looks like we have encountered some issue..."):
    """
    Log the detailed error for backend debugging and return a generic message for the user.
    """
    logger.error(f"Error encountered: {str(e)}")
    return user_message

def generate_summary(content, media_type="text"):
    """
    Generate a two-level summary when the content contains detailed data or statistics.
    The first summary provides analytical insights, and the second offers detailed data points.
    """
    try:
        logger.info(f"Generating summary for media type: {media_type}")

        # Define the analytical and detailed prompts
        analytical_prompt = (
            f"The following is text extracted from a {media_type} file. Generate an analytical summary that:\n"
            f"- Highlights the overall context and main themes.\n"
            f"- Identifies and analyzes significant trends, patterns, or sentiments.\n"
            f"- Provides evidence and reasoning behind key observations.\n\n{content}"
        )

        detailed_prompt = (
            f"The following is text extracted from a {media_type} file. Generate a detailed summary that:\n"
            f"- Extracts key data points, statistics, and indicators.\n"
            f"- Provides actionable insights or recommendations based on the data.\n"
            f"- Focuses on facts that help in decision-making.\n\n{content}"
        )

        # Check if two-level summary is needed
        if len(content.split()) > 1000 or any(keyword in content.lower() for keyword in ["data", "statistics", "figures", "analysis"]):
            logger.info("Detected detailed content; generating analytical and detailed summaries.")

            # Generate the analytical summary
            analytical_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert summarizer."},
                    {"role": "user", "content": analytical_prompt}
                ],
                max_tokens=450,
                temperature=0.5,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            if not analytical_response or 'error' in analytical_response:
                logger.error(f"OpenAI error response: {analytical_response}")

            analytical_summary = analytical_response.choices[0].message.content.strip()

            # Generate the detailed summary
            detailed_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert summarizer."},
                    {"role": "user", "content": detailed_prompt}
                ],
                max_tokens=350,
                temperature=0.5,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            if not detailed_summary or 'error' in detailed_summary:
                logger.error(f"OpenAI error response: {detailed_summary}")

            detailed_summary = detailed_response.choices[0].message.content.strip()

            logger.info("Two-level summary generated successfully.")
            return f"**Analytical Summary:**\n{analytical_summary}\n\n**Detailed Summary:**\n{detailed_summary}"
        else:
            logger.info("Generating a single analytical summary.")

            # Generate a single analytical summary for shorter or less complex content
            analytical_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert summarizer."},
                    {"role": "user", "content": analytical_prompt}
                ],
                max_tokens=400,
                temperature=0.5,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            if not analytical_response or 'error' in analytical_response:
                logger.error(f"OpenAI error response: {analytical_response}")

            analytical_summary = analytical_response.choices[0].message.content.strip()

            logger.info("Single analytical summary generated successfully.")
            return f"**Analytical Summary:**\n{analytical_summary}"

    except AuthenticationError as auth_err:
        logger.error(f"Authentication failed: {auth_err}")
        return "Error: Authentication failed. Please check your API key."
    except RateLimitError as rate_err:
        logger.error(f"Rate limit exceeded: {rate_err}")
        return "Error: Rate limit exceeded. Please try again later."
    except OpenAIError as openai_err:
        logger.error(f"OpenAI API error: {openai_err}")
        return "Error: Something went wrong with OpenAI API. Please try again later."
    except Exception as e:
        return handle_error(e)