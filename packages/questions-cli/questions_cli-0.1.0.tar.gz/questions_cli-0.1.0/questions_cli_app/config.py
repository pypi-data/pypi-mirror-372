import os

# Model name
MODEL_NAME = os.getenv("LLM_MODEL", "gpt-4o-mini")

# Default number of questions
NUM_QUESTIONS = int(os.getenv("NUM_QUESTIONS", "3"))

# MCQ prompt for inputs that are already a complete question (DO NOT REWORD)
MCQ_PROMPT_FOR_COMPLETE_QUESTION = """
You are an expert teacher. You are given a complete question that may or may not be well formed.
Do not change or reword the question — keep the stem exactly as given - only make changes to grammatically correct it or a spellcheck.
For that question, produce a single multiple choice item and return ONLY valid JSON (no commentary).

Requirements:
- Provide exactly 4 options in the "options" array (order A,B,C,D).
- Indicate the correct option as a single letter in "correct_option" (A/B/C/D).
- "explanation": a short 1-2 sentence concise explanation (one or two sentences).
- "accepted_long_answer": a detailed long answer (3–6 sentences) that fully explains the concept and reasoning.
- "detailed_explanation": an object with an "options" map giving a short 1-2 sentence rationale for each option keyed by "A","B","C","D".
- Do NOT use "all of the above" / "none of the above".
- Keep JSON keys exactly as shown below.

Return this JSON object:

{
  "question": "<exact input question>",
  "options": ["Option A text", "Option B text", "Option C text", "Option D text"],
  "correct_option": "A",
  "explanation": "<short 1-2 sentence explanation>",
  "accepted_long_answer": "<detailed long answer, 3-6 sentences>",
  "detailed_explanation": {
    "options": {
      "A": "<why A is correct or incorrect — 1 sentence>",
      "B": "<...>",
      "C": "<...>",
      "D": "<...>"
    }
  }
}

Question: "{question}"
"""

# MCQ prompt for keyword / incomplete input (MODEL MAY EXPAND)
MCQ_PROMPT_FOR_KEYWORD = """
You are an expert teacher. You are given a keyword or short phrase which is a search query by a user on the app. Create a clear, exam-style question that tests the core concept of that keyword, then produce one MCQ for that question. 
Return ONLY valid JSON (no commentary).

Requirements (per MCQ):
- Create a concise question stem (self-contained).
- Provide exactly 4 options in the "options" array (A,B,C,D).
- Indicate correct option as "correct_option": "A" (letter).
- "explanation": a short 1-2 sentence explanation (concise).
- "accepted_long_answer": a detailed 3–6 sentence explanation.
- "detailed_explanation": per-option short rationales keyed by "A","B","C","D".

Return this JSON object:

{
  "question": "<generated question>",
  "options": ["Option A text", "Option B text", "Option C text", "Option D text"],
  "correct_option": "A",
  "explanation": "<short 1-2 sentence explanation>",
  "accepted_long_answer": "<detailed long answer, 3-6 sentences>",
  "detailed_explanation": {
    "options": {
      "A": "<...>",
      "B": "<...>",
      "C": "<...>",
      "D": "<...>"
    }
  }
}

Keyword: "{keyword}"
"""

# Topic-generation prompt (produce topic + definition + prerequisites etc.)
TOPIC_GENERATION_PROMPT = """
You are a smart teacher that maps a question to a precise topic and writes topic metadata to match our DB.
Given the question, return ONLY valid JSON with these fields:

{
  "topic": "<short topic name, max 5 words>",
  "definition": "<1-2 sentence clear definition>",
  "prerequisites": ["prereq1", "prereq2", "prereq3"],   # 2-5 key prior concepts
  "core_topic": "<broader subject area (e.g., 'General Psychology' or 'Economics')>",
}

Guidelines:
- Choose a concise topically-accurate 'topic' (no long phrases).
- 'definition' must be simple and directly explain the topic.
- 'prerequisites' should be concepts someone should already know (2–5 items).

- Return only JSON, no extra fields, no commentary.

Question: "{question}"
"""

CLASSIFICATION_PROMPT_TEMPLATE = """
You are a classifier.
Determine if the following input is:
- A complete question (well-formed question that can directly be answered), or
- A keyword / incomplete question (fragment, topic, or phrase that needs expansion).

Input: "{input_text}"

Respond with exactly one word: "question" or "keyword".
"""

# MongoDB config
MONGO_URI = os.getenv("MONGO_URI", "")
MONGO_DB = os.getenv("MONGO_DB", "seekh")
MONGO_QUESTIONS_COLLECTION = os.getenv("MONGO_QUESTIONS_COLLECTION", "questions")
MONGO_TOPICS_COLLECTION = os.getenv("MONGO_TOPICS_COLLECTION", "topics")
