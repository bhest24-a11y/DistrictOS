import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def ask_ai(question, context):

    prompt = f"""
You are a district operations expert.

Data:
{context}

Question:
{question}

Answer clearly with priorities, risks, and actions.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content
