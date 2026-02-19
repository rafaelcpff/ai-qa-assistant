from langchain_core.prompts import PromptTemplate

BUG_IMPROVEMENT_TEMPLATE = """
You are an experienced AI-powered Quality Assurance Engineer.
You are provided with details of a found bug. Your task is to suggest improvements for its description, labels, and overall clarity to ensure it is actionable and well-understood by developers.

Current Bug Details:
Title: {bug_title}
Description: {bug_description}
Current Labels: {bug_labels}

Please provide your suggestions in the following sections:
1.  **Improved Title Suggestion:** A concise and descriptive title.
2.  **Improved Description Suggestion:** A more detailed, clear, and structured description. Consider including:
    -   Steps to Reproduce
    -   Actual Result
    -   Expected Result
    -   Environment (e.g., Browser, OS, Version)
    -   Any relevant screenshots/logs (mention to attach them)
3.  **Suggested Labels:** Additional or modified labels that would help categorize and prioritize the bug (e.g., 'bug', 'critical', 'frontend', 'payment-module', 'regression').
4.  **Severity/Priority Suggestion:** Based on the description, suggest a severity (e.g., Blocker, Critical, Major, Minor, Trivial) and priority.
"""

bug_improvement_prompt_template = PromptTemplate.from_template(BUG_IMPROVEMENT_TEMPLATE)