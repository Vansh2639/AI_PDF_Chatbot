from google import genai
import os
import re


def format_code_blocks(text):

    lines = text.splitlines()

    formatted = []

    inside_code = False

    for line in lines:

        if line.strip() == "js":

            if inside_code:
                formatted.append("```")

            formatted.append("```javascript")
            inside_code = True
            continue

        if inside_code and (
            line.startswith("28/")
            or line.startswith("29/")
            or line.startswith("30/")
            or line.startswith("31/")
            or line.startswith("32/")
            or line.startswith("33/")
            or line.startswith("34/")
            or line.startswith("35/")
            or line.startswith("36/")
            or line.startswith("📍")
            or line.startswith("🏗️")
            or line.startswith("✂️")
            or line.startswith("🔁")
            or line.startswith("📦")
            or line.startswith("❓")
            or line.startswith("🧠")
            or line.startswith("⚠️")
            or line.startswith("🧪")
        ):

            formatted.append("```")
            inside_code = False

        formatted.append(line)

    if inside_code:
        formatted.append("```")

    return "\n".join(formatted)


def rewrite_question(question, history):

    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    prompt = f"""
You are a query rewriting assistant.

Your ONLY job is to rewrite follow-up questions into complete standalone questions.

Conversation History:
{history}

Current User Question:
{question}

Rules:

1. If the current question is already complete, return it unchanged.
2. If it refers to previous questions using words like:
- it
- this
- that
- these
- those
- more
- another example
- explain further
- why
- how
- when
- where

replace those references with the latest relevant topic.

Return ONLY the rewritten question.

Do NOT answer the question.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    return response.text.strip()


def get_answer(question, docs):

    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    context = ""

    for doc in docs:
        content = format_code_blocks(doc.page_content)

        context += f"""
    
    File: {doc.metadata["source"]}
    
    Page: {doc.metadata["page"]}
    
    {content}

----------------------------------------

"""

    prompt = f"""
You are an expert AI tutor helping users understand concepts from uploaded PDF documents.

IMPORTANT RULES

- Answer ONLY using the provided context.
- Never use outside knowledge.
- Carefully read ALL retrieved context before answering.
- If the answer is not found in the context, reply exactly:

I couldn't find that information in the uploaded PDFs.

--------------------------------------------------

Structure your answer as follows whenever applicable.

## Definition

Start with a short and clear definition (2-4 lines).

---

## Detailed Explanation

Explain the concept thoroughly.

- If the user asks "explain in detail", "deeply", "teach me", or "elaborate", provide a comprehensive explanation using ALL relevant information from the retrieved context.
- Explain the concept step by step.
- Keep paragraphs short (2-4 lines).
- Leave one blank line between paragraphs.

---

## Key Points

Provide important points as a numbered list.

---

## Code (Only if present in the context)

If the retrieved context contains any syntax or code examples:

- Copy the COMPLETE code exactly as it appears.
- Put every example in its own Markdown code block.
- Preserve the original formatting and variable names.
- Never replace code with only a textual explanation.

After each code block, explain:

- What the code does.
- The important lines.
- The expected output (if applicable).

---

## Important Notes

List important notes from the context as numbered points.

---

## Common Use Cases

If available in the context, list practical use cases as numbered points.

---

## Summary

Finish with a short summary (2-3 lines).

--------------------------------------------------

Formatting Rules

- Use Markdown.
- Use ## headings.
- Leave a blank line between sections.
- Leave a blank line between numbered points.
- Use numbered lists where appropriate.
- Use bullet points where appropriate.
- Never make the entire response bold.
- Use **bold** only for important keywords.
- Never invent information or code that is not present in the retrieved context.

--------------------------------------------------

Context

{context}

--------------------------------------------------

Question

{question}

--------------------------------------------------

Answer
"""

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        return response.text, docs

    except Exception as e:

        return f"⚠️ Gemini API Error:\n\n{str(e)}", docs
