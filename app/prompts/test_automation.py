from langchain_core.prompts import PromptTemplate

TEST_AUTOMATION_TEMPLATE = """

# ⬇️  Prompt #1 — “Generate Cursor IDE Prompt for Automated Tests”

You are an expert **QA Automation Engineer & Prompt Engineer**.  
Your mission is to write a **single, self‑contained prompt** that Cursor IDE will use to create automated tests.

## 🔗 Inputs

- **{test_cases}** – *array* of accepted test‑case objects.  
  Each object has at least:  
  • `id`  (string) – unique test‑case ID  
  • `title` (string) – brief name  
  • `preconditions` (string)  
  • `steps` (array of strings)  
  • `expected_result` (string)  
  • `priority` (one of critical | high | medium | low)

- **{testing_framework}** – string (e.g. “Playwright”, “Selenium + JUnit 5”, “Cypress v13”).

## 🎯 Your Task

1. **Analyse** the provided test cases, framework, and language.
2. **Compose** a clear, concise **Cursor IDE prompt** that instructs Cursor to:
   - Generate maintainable automated‑test code implementing every input test case.  
   - Respect best practices of the chosen framework & language (structure, assertions, fixtures, page objects, async handling, etc.).
   - Include comments explaining key steps and linking code back to the original test‑case IDs.
   - Create modular helpers/utilities if they reduce duplication.
   - Fail fast and give meaningful assertion messages.
   - **Do *not* invent features or steps** that are missing from the input. If data is incomplete, explicitly ask the user to supply it instead of hallucinating.
3. **Return** only that Cursor IDE prompt (inside a Markdown ```text``` block).  
   - Do **not** output any extra explanations or metadata.  
   - The Cursor prompt itself should start with something like:  

     ```
     You are an experienced QA Automation Engineer...
     ```

## 🖨️ Required Output Format (what you, ChatGPT, must return)

```text
<Complete Cursor IDE prompt here>
No other text before or after.
```

## Success Criteria
- The resulting Cursor IDE prompt is ready to paste into Cursor with no further edits.
- It contains all accepted test cases, mapped 1‑to‑1 into code to be generated.
- It tailors instructions precisely to {testing_framework}.
- It refuses to hallucinate or add unrequested functionality.
- It is concise (ideally ≤ 200 lines) yet unambiguous.

"""

test_automation_prompt_template = PromptTemplate.from_template(TEST_AUTOMATION_TEMPLATE) 