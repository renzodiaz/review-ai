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

def ask_structured(
    prompt: str,
    schema,
):
    """
    Ask OpenAI to return a structured object
    matching the supplied Pydantic schema.
    """

    response = client.responses.parse(
        model=OPENAI_MODEL,
        input=prompt,
        text_format=schema,
    )

    return response.output_parsed