from openai import OpenAI
from dotenv import load_dotenv
from src.config import OPENAI_MODEL


load_dotenv()

client = OpenAI()

def ask(prompt):
    """
    Send a prompt to OpenAI and return the text response.
    """

    response = client.responses.create(
        model=OPENAI_MODEL,
        input=prompt
    )

    return response.output_text