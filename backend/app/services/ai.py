import os
from dotenv import load_dotenv
from openai import OpenAI

# ================================
# 🔑 LOAD ENV
# ================================
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

# ================================
# 🧠 MAIN AI ANALYSIS
# ================================
def generate_ai_insights(text: str):
    if not text:
        return "No report text provided."

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an elite retail operations analyst. "
                        "You analyze messy district/store reports and produce executive-level insights."
                    )
                },
                {
                    "role": "user",
                    "content": f"""
Analyze this retail report:

{text}

Return:
- Executive summary
- Key risks
- Store-level insights
- Recommended actions

Be concise, structured, and business-focused.
"""
                }
            ],
            temperature=0.3
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"AI error: {str(e)}"


# ================================
# 💬 AI CHAT WITH CONTEXT
# ================================
def chat_with_context(question: str, history: str):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a retail intelligence assistant. "
                        "You answer questions about store performance, risks, and actions."
                    )
                },
                {
                    "role": "user",
                    "content": f"""
Conversation History:
{history}

User Question:
{question}

Answer clearly and directly using the context.
"""
                }
            ],
            temperature=0.4
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"AI error: {str(e)}"