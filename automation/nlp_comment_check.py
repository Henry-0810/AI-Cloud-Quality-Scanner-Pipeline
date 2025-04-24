import os
from openai import OpenAI
import json

# File paths
TARGET_FILE = "data/3-comments-nlp/benchmark_comments.py"
OUTPUT_FILE = "nlp-results.json"
OPENAI_TOKEN = os.getenv("OPENAI_TOKEN")

client = OpenAI(api_key=OPENAI_TOKEN)


def build_prompt(comment, code_context):
    return f"""
            You are a senior code reviewer focused on comment clarity and effectiveness.
            Given the following Python comment and its surrounding code, evaluate the comment quality.

            Code:
            {code_context}

            Comment:
            {comment}

            Tasks:
            1. Classify the comment as 'good' or 'bad'
            2. Explain why it's good or bad
            3. Provide a minimalist suggestion (not the solution, just how to improve it)

            Return your answer in this format:
            classification: <good|bad>
            why: <reason>
            suggestion: <1-sentence minimalist improvement>
            """


def main():
    with open(TARGET_FILE, "r") as f:
        lines = f.readlines()

    comment_lines = []
    window_size = 5

    for idx, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("#") and not stripped.startswith("###"):
            comment = stripped
            start = max(0, idx - 2)
            end = min(len(lines), idx + 3)
            context = "".join(lines[start:end])
            comment_lines.append((idx + 1, comment, context))

    print(f"Found {len(comment_lines)} comments to analyze.")

    # Step 4: Send to OpenAI and Collect Results
    results = []

    for line_num, comment, context in comment_lines:
        prompt = build_prompt(comment, context)

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
            # use attribute access on the ChatCompletionMessage object
            content = response.choices[0].message.content
            lines_out = content.strip().splitlines()

            classification = lines_out[0].split(":", 1)[1].strip()
            reason = lines_out[1].split(":", 1)[1].strip()
            suggestion = lines_out[2].split(":", 1)[1].strip()

            if classification == "bad":
                results.append({
                    "file": TARGET_FILE,
                    "line": line_num,
                    "comment": comment,
                    "why": reason,
                    "suggestion": suggestion
                })
                print(f"✅ Line {line_num}: {classification} → {suggestion}")
            else:
                print(f"ℹ️  Line {line_num}: classified as good, skipping.")

        except Exception as e:
            print(f"❌ Error on line {line_num}: {e}")

    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)

    print(f"📄 NLP results saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
