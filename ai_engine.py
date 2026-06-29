import os
import json
import logging
import re
import hashlib
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

from google import genai
from google.genai import types

# =========================
# CONFIG
# =========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    http_options={"api_version": "v1"}
)

# =========================
# SIMPLE CACHE (RAM)
# =========================
CACHE = {}

def hash_text(text: str):
    return hashlib.md5(text.encode("utf-8")).hexdigest()

# =========================
# SAFE JSON PARSER
# =========================
def safe_json_parse(text: str):
    try:
        return json.loads(text)
    except Exception:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise

# =========================
# GEMINI CALL (RETRY)
# =========================
def call_gemini(prompt: str):
    key = hash_text(prompt)

    # cache hit
    if key in CACHE:
        return CACHE[key]

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2
                )
            )

            result = safe_json_parse(response.text)
            CACHE[key] = result
            return result

        except Exception as e:
            logging.warning(f"Retry {attempt + 1}/3 failed: {e}")

    return None

# =========================
# BUILD PROMPT
# =========================
def build_prompt(p):
    return f"""
Bạn là AI chuyên ngành Cơ điện tử và Tự động hóa.

QUY TẮC BẮT BUỘC:
- Chỉ trả về JSON
- Không markdown
- Không giải thích

OUTPUT FORMAT:
{{
  "summary": "...",
  "technical_keywords": ["..."],
  "suggested_reply": "..."
}}

DATA:

Author: {p['author']}
Content: {p['content']}

Comments:
{json.dumps(p.get('comments', []), ensure_ascii=False)}
"""

# =========================
# PROCESS SINGLE POST
# =========================
def process_post(p):
    try:
        logging.info(f"🔍 Processing {p['post_id']} - {p['author']}")

        prompt = build_prompt(p)
        result = call_gemini(prompt)

        if not result:
            logging.error(f"❌ Failed post {p['post_id']}")
            return None

        p.update(result)
        return p

    except Exception as e:
        logging.error(f"💥 Error post {p['post_id']}: {e}")
        return None

# =========================
# PARALLEL WORKER
# =========================
def run_parallel(posts, max_workers=5):
    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_post, p) for p in posts]

        for f in as_completed(futures):
            r = f.result()
            if r:
                results.append(r)

    return results

# =========================
# LOAD DATA
# =========================
def load_posts():
    file = "posts_data.json"

    if not os.path.exists(file):
        logging.error("❌ posts_data.json not found!")
        return []

    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)

# =========================
# SAVE OUTPUT
# =========================
def save_output(data):
    os.makedirs("logs", exist_ok=True)

    output_file = "logs/analyzed_posts.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    logging.info(f"✨ Saved to {output_file}")

# =========================
# MAIN
# =========================
def main():
    posts = load_posts()

    if not posts:
        return

    logging.info(f"🧠 Starting AI processing: {len(posts)} posts")

    results = run_parallel(posts, max_workers=5)

    save_output(results)

    logging.info("✅ DONE - Production pipeline completed")

# =========================
# RUN
# =========================
if __name__ == "__main__":
    main()