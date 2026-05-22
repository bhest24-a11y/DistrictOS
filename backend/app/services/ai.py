import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ================================
# 🧠 DISTRICT-LEVEL ANALYSIS
# ================================
def generate_ai_insights(text: str):

    if not text:
        return "No report provided."

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an elite retail operations analyst. You turn messy reports into clear executive decisions."
                },
                {
                    "role": "user",
                    "content": f"""
Analyze this district report:

{text}

Return structured output:

## Executive Summary
## Key Risks
## Store-Level Issues
## Recommended Actions

Be concise and actionable.
"""
                }
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"AI error: {str(e)}"


# ================================
# 🏪 STORE-LEVEL ANALYSIS (NEW)
# ================================
def analyze_store(store_id: str, context: str):

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You analyze store-level retail performance and identify root causes."
                },
                {
                    "role": "user",
                    "content": f"""
Context:
{context}

Analyze store {store_id}.

Return:
- Why this store is at risk
- What is driving the score
- What action should be taken
"""
                }
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"AI error: {str(e)}"


# ================================
# 💬 CHAT WITH CONTEXT
# ================================
def chat_with_context(question: str, history: str):

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a retail intelligence assistant helping analyze district performance."
                },
                {
                    "role": "user",
                    "content": f"""
Conversation:
{history}

Question:
{question}
"""
                }
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"AI error: {str(e)}"