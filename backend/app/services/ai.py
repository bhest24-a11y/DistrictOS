import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)


def generate_ai_insights(text: str):
    if not text:
        return "No report text provided."

    prompt = f"""
You are an elite retail operations analyst.

Analyze this report:

{text}

Return:
- Executive summary
- Key risks
- Store-level insights
- Recommended actions

Be concise and business-focused.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a high-level business intelligence system."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"AI error: {str(e)}"
