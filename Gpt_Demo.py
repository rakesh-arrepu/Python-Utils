from openai import OpenAI
import os

client = OpenAI()
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
response = client.responses.create(
    model="gpt-4o-mini",  # or "gpt-3.5-turbo" if you don't have access to GPT-4
    input="Write a short bedtime story about a unicorn."
)

print(response.output_text)

# from openai import OpenAI
# import os
# # print("Make sure to set your OPENAI_API_KEY environment variable before running this script.")
# # print("API Key:", os.getenv("OPENAI_API_KEY"))

# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# response = client.chat.completions.create(
#     model="gpt-4.1",
#     messages=[{"role": "user", "content": "Hello, world!"}]
# )

# print(response.choices[0].message)
