from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database URL from .env file
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),  # This is the default and can be omitted
)

def generate_company_description(company_name):
    """
    Generates an AI-written description for a given company using OpenAI's GPT-4o-mini model.
    """
    try:
        # Define the prompt
        prompt = f"Write a detailed but concise description of the company {company_name}. Use max 150 words"

        # Call the OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a sustainable financial analyst specialized in biodiversity loss. You never use markdowns."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,  # Adjust creativity level
            max_tokens=250    # Limit response length
        )
        # Extract and return the generated description
        return response.choices[0].message.content
    
    except Exception as e:
        # Handle errors gracefully
        return f"An error occurred: {str(e)}"

def calculate_score_color(score):
    """
    Calculate a color for the score gauge based on the score.
    Red for low scores, orange for medium, and green for high scores.

    Args:
        score (float): The score (0-100).

    Returns:
        str: Hexadecimal color code.
    """
    if score <= 50:
        # Red to orange gradient
        r = 255
        g = int(255 * (score / 50))  # Increase green as score approaches 50
        b = 0
    else:
        # Orange to green gradient
        r = int(255 * ((100 - score) / 50))  # Decrease red as score approaches 100
        g = 255
        b = 0

    return f"rgb({r},{g},{b})"