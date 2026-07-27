import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Initialize client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Make request
response = client.responses.create(
    model="gpt-5-mini",
    max_output_tokens=100-200,
    reasoning={"effort": "low"},
    input="Give one creative use for AI."
)

print(response.output_text)

# Print result
# print(response.output[0].content[0].text)
#print(response.status)
#print(response.output)
#print(response.output_text)