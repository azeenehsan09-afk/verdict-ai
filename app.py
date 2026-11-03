
import os
import json
from pathlib import Path

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from google import genai


# 1. Load API key
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

api_key = os.getenv("GEMINI_API_KEY")


# 2. Create Flask app
app = Flask(__name__)
CORS(app)


# 3. Connect to Gemini
client = genai.Client(api_key=api_key) if api_key else None

MODEL_NAME = "gemini-3.5-flash-lite"


# 4. Home route
@app.route("/")
def home():
    return "Verdict AI Backend is running!"


# ===================================
# 5. ANALYZE DECISION
# ===================================

@app.route("/analyze", methods=["POST"])
def analyze():

    if client is None:
        return jsonify({
            "error": "Gemini API key is missing. Check your .env file."
        }), 500

    data = request.get_json(silent=True) or {}
    decision = data.get("decision", "")

    if not isinstance(decision, str) or not decision.strip():
        return jsonify({
            "error": "Please enter a valid decision."
        }), 400

    decision = decision.strip()

    if len(decision) > 2000:
        return jsonify({
            "error": "Please keep your decision under 2000 characters."
        }), 400

    prompt = """
You are the AI engine of Verdict, an AI decision courtroom.

The user's decision is:

{decision}

Generate four distinct perspectives.

1. OPTIMIST:
Make the strongest reasonable argument IN FAVOUR.
Explain benefits and opportunities.

2. SKEPTIC:
Challenge the decision.
Identify risks, weak assumptions and disadvantages.

3. REALIST:
Examine practical factors such as money, time,
responsibilities, resources and alternatives.
Do not invent facts about the user.

4. JUDGE:
Act as an impartial decision judge.

VERDICT:
Choose exactly one:
PROCEED,
PROCEED WITH CAUTION,
or RECONSIDER.

REASONING:
Explain your verdict using all three perspectives.

OVERLOOKED QUESTION:
Ask one important question the user has not considered.

CONFIDENCE:
Provide an integer from 0 to 100.

WHAT WOULD CHANGE THIS VERDICT:
Provide 2 or 3 specific conditions that could change
your verdict.

RULES:
- Keep the first three perspectives around 80-120 words.
- Give every persona a distinct voice.
- Do not invent personal information.
- If important details are missing, prefer
  PROCEED WITH CAUTION.
- Never present the verdict as unquestionable truth.
- Confidence must reflect the available information.
- Encourage professional advice for medical, legal
  or financial decisions.
""".replace("{decision}", decision)

    response_schema = {
        "type": "OBJECT",
        "properties": {
            "optimist": {"type": "STRING"},
            "skeptic": {"type": "STRING"},
            "realist": {"type": "STRING"},
            "judge": {
                "type": "OBJECT",
                "properties": {
                    "verdict": {
                        "type": "STRING",
                        "enum": [
                            "PROCEED",
                            "PROCEED WITH CAUTION",
                            "RECONSIDER"
                        ]
                    },
                    "reasoning": {"type": "STRING"},
                    "overlooked_question": {"type": "STRING"},
                    "confidence": {"type": "INTEGER"},
                    "what_would_change": {
                        "type": "ARRAY",
                        "items": {"type": "STRING"}
                    }
                },
                "required": [
                    "verdict",
                    "reasoning",
                    "overlooked_question",
                    "confidence",
                    "what_would_change"
                ]
            }
        },
        "required": [
            "optimist",
            "skeptic",
            "realist",
            "judge"
        ]
    }

    try:

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_json_schema": response_schema
            }
        )

        if not response.text:
            raise ValueError("Gemini returned an empty response.")

        result = json.loads(response.text)

        for persona in ["optimist", "skeptic", "realist"]:
            if not isinstance(result.get(persona), str):
                raise ValueError(f"Invalid response from {persona}.")

        judge = result.get("judge")

        if not isinstance(judge, dict):
            raise ValueError("Invalid Judge response.")

        valid_verdicts = [
            "PROCEED",
            "PROCEED WITH CAUTION",
            "RECONSIDER"
        ]

        if judge.get("verdict") not in valid_verdicts:
            raise ValueError("Invalid verdict.")

        if not isinstance(judge.get("reasoning"), str):
            raise ValueError("Invalid Judge reasoning.")

        if not isinstance(judge.get("overlooked_question"), str):
            raise ValueError("Invalid overlooked question.")

        confidence = judge.get("confidence")

        if (
            isinstance(confidence, bool)
            or not isinstance(confidence, int)
            or not 0 <= confidence <= 100
        ):
            raise ValueError("Invalid confidence score.")

        conditions = judge.get("what_would_change")

        if (
            not isinstance(conditions, list)
            or not 2 <= len(conditions) <= 3
            or not all(isinstance(item, str) for item in conditions)
        ):
            raise ValueError("Invalid verdict conditions.")

        return jsonify(result)

    except Exception as error:

        print("Gemini Error:", error)

        error_message = str(error)

        if "503" in error_message or "UNAVAILABLE" in error_message:
            message = (
                "Gemini is temporarily busy. "
                "Please try again in a little while."
            )

        elif "429" in error_message or "RESOURCE_EXHAUSTED" in error_message:
            message = (
                "Gemini's request limit may have been reached. "
                "Please wait and try again."
            )

        else:
            message = "AI analysis failed. Please try again."

        return jsonify({"error": message}), 500


# ===================================
# 6. APPEAL ROUND
# ===================================

@app.route("/appeal", methods=["POST"])
def appeal():

    if client is None:
        return jsonify({"error": "Gemini API key is missing."}), 500

    data = request.get_json(silent=True) or {}

    decision = data.get("decision", "")
    original_verdict = data.get("original_verdict", "")
    original_reasoning = data.get("original_reasoning", "")
    appeal_text = data.get("appeal", "")

    if not all(
        isinstance(value, str)
        for value in [
            decision,
            original_verdict,
            original_reasoning,
            appeal_text
        ]
    ):
        return jsonify({"error": "Invalid appeal information."}), 400

    decision = decision.strip()
    original_verdict = original_verdict.strip()
    original_reasoning = original_reasoning.strip()
    appeal_text = appeal_text.strip()

    if not decision or not original_verdict or not appeal_text:
        return jsonify({
            "error": "Please provide the original decision and your appeal."
        }), 400

    if len(appeal_text) < 10:
        return jsonify({
            "error": "Please explain your appeal in a little more detail."
        }), 400

    if len(appeal_text) > 2000:
        return jsonify({
            "error": "Your appeal must be under 2000 characters."
        }), 400

    prompt = """
You are the Judge in Verdict, an AI decision courtroom.

The user's original decision:
""" + decision + """

Original verdict:
""" + original_verdict + """

Original reasoning:
""" + original_reasoning + """

The user's appeal:
""" + appeal_text + """

Reassess the original decision fairly.

Instructions:
1. Consider the appeal as additional evidence, not automatically as truth.
2. Evaluate whether it genuinely changes the original reasoning.
3. You may keep or change the original verdict.
4. Explain why the verdict changed or stayed the same.
5. Do not simply agree with the user.
6. Do not make the decision for the user.

Return:
- verdict: PROCEED, PROCEED WITH CAUTION, or RECONSIDER
- reasoning: explain your reassessment
- verdict_changed: true or false
- overlooked_question: one important question the user should still consider
"""

    appeal_schema = {
        "type": "OBJECT",
        "properties": {
            "verdict": {
                "type": "STRING",
                "enum": [
                    "PROCEED",
                    "PROCEED WITH CAUTION",
                    "RECONSIDER"
                ]
            },
            "reasoning": {"type": "STRING"},
            "verdict_changed": {"type": "BOOLEAN"},
            "overlooked_question": {"type": "STRING"}
        },
        "required": [
            "verdict",
            "reasoning",
            "verdict_changed",
            "overlooked_question"
        ]
    }

    try:

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_json_schema": appeal_schema
            }
        )

        if not response.text:
            raise ValueError("Gemini returned an empty appeal response.")

        result = json.loads(response.text)

        return jsonify(result)

    except Exception as error:

        print("Appeal Error:", str(error))

        return jsonify({
            "error": "The Judge could not reassess your appeal. Please try again."
        }), 500


# ===================================
# 7. FINAL VERDICT
# ===================================

@app.route("/finalize", methods=["POST"])
def finalize():

    if client is None:
        return jsonify({
            "error": "Gemini API key is missing."
        }), 500

    data = request.get_json(silent=True) or {}

    decision = data.get("decision", "")
    revised_verdict = data.get("revised_verdict", "")
    revised_reasoning = data.get("revised_reasoning", "")
    overlooked_question = data.get("overlooked_question", "")
    user_answer = data.get("user_answer", "")

    values = [
        decision,
        revised_verdict,
        revised_reasoning,
        overlooked_question,
        user_answer
    ]

    if not all(isinstance(value, str) for value in values):
        return jsonify({
            "error": "Invalid final reflection information."
        }), 400

    decision = decision.strip()
    revised_verdict = revised_verdict.strip()
    revised_reasoning = revised_reasoning.strip()
    overlooked_question = overlooked_question.strip()
    user_answer = user_answer.strip()

    if not all([
        decision,
        revised_verdict,
        revised_reasoning,
        overlooked_question,
        user_answer
    ]):
        return jsonify({
            "error": "Please answer the overlooked question before finalizing."
        }), 400

    if len(user_answer) < 5:
        return jsonify({
            "error": "Please provide a little more detail in your answer."
        }), 400

    if len(user_answer) > 2000:
        return jsonify({
            "error": "Your answer must be under 2000 characters."
        }), 400

    prompt = """
You are the Final Judge in Verdict, an AI decision courtroom.

The user's original decision:
""" + decision + """

The revised verdict after the appeal:
""" + revised_verdict + """

The Judge's reassessment:
""" + revised_reasoning + """

The overlooked question:
""" + overlooked_question + """

The user's answer to that question:
""" + user_answer + """

Your task is to deliver the FINAL conclusion of this decision trial.

Consider the entire discussion, including the user's latest answer.

1. FINAL VERDICT:
Choose exactly one:
PROCEED,
PROCEED WITH CAUTION,
or RECONSIDER.

2. FINAL REASONING:
Explain why this is the most reasonable conclusion,
taking the user's answer into account.

3. PRACTICAL NEXT STEP:
Give one specific, realistic action the user can take next.

RULES:
- Do not automatically agree with the user.
- Be fair, balanced and thoughtful.
- Do not invent personal information.
- Acknowledge uncertainty when important information is missing.
- Do not present your verdict as an unquestionable truth.
- Do not ask another question. This is the end of the trial.
- Encourage professional advice for medical, legal or financial decisions.
- End with a concise, memorable closing message.
"""

    final_schema = {
        "type": "OBJECT",
        "properties": {
            "final_verdict": {
                "type": "STRING",
                "enum": [
                    "PROCEED",
                    "PROCEED WITH CAUTION",
                    "RECONSIDER"
                ]
            },
            "final_reasoning": {
                "type": "STRING"
            },
            "next_step": {
                "type": "STRING"
            },
            "closing_message": {
                "type": "STRING"
            }
        },
        "required": [
            "final_verdict",
            "final_reasoning",
            "next_step",
            "closing_message"
        ]
    }

    try:

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_json_schema": final_schema
            }
        )

        if not response.text:
            raise ValueError("Gemini returned an empty final response.")

        result = json.loads(response.text)

        if result.get("final_verdict") not in [
            "PROCEED",
            "PROCEED WITH CAUTION",
            "RECONSIDER"
        ]:
            raise ValueError("Invalid final verdict.")

        for field in [
            "final_reasoning",
            "next_step",
            "closing_message"
        ]:
            if not isinstance(result.get(field), str) or not result[field].strip():
                raise ValueError("Invalid final response.")

        return jsonify(result)

    except Exception as error:

        print("Final Verdict Error:", str(error))

        return jsonify({
            "error": "The Judge could not prepare the final verdict. Please try again."
        }), 500


# ===================================
# 8. START SERVER
# ===================================

if __name__ == "__main__":
    app.run(debug=True)
