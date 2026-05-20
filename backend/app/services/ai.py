import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_ai_insights(text):

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
