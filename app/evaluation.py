from langchain.evaluation import ExactMatchStringEvaluator, CriteriaEvalChain
from langchain_ollama import ChatOllama
import os

# Assuming llm is initialized as in main.py
# llm = ChatOllama(model="llama3", base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))

def evaluate_user_story_analysis(llm_chain, test_data_entry, llm_model_for_eval):
    """
    Evaluates the user story analysis output.
    Uses a combination of ExactMatch for specific phrases and LLM-as-a-judge for overall quality.
    """
    context_str = "\n\n".join([f"Key: {s['key']}\nTitle: {s['title']}\nDescription: {s['description']}" for s in test_data_entry['context_stories']])
    inputs = {
        "context_user_stories": context_str,
        "new_story_title": test_data_entry['new_story_title'],
        "new_story_description": test_data_entry['new_story_description']
    }

    # Generate AI response
    ai_response = llm_chain.invoke(inputs)

    # 1. Evaluate specific sections (e.g., presence of keywords, direct matches)
    exact_match_evaluator = ExactMatchStringEvaluator()
    insights_match = exact_match_evaluator.evaluate_strings(
        prediction=ai_response,
        reference=test_data_entry['expected_response_insights']
    )
    risks_match = exact_match_evaluator.evaluate_strings(
        prediction=ai_response,
        reference=test_data_entry['expected_response_risks']
    )

    # 2. LLM-as-a-judge for overall quality/relevance/completeness
    # This requires an LLM to act as the evaluator.
    criteria_evaluator = CriteriaEvalChain.from_llm(
        llm=llm_model_for_eval,
        criteria={
            "relevance": "The generated response must be relevant to the new user story and context.",
            "completeness": "The response must cover insights, impacts, and quality risks.",
            "accuracy": "The identified impacts and risks must be logically sound and accurate based on the provided context."
        }
    )
    llm_eval_result = criteria_evaluator.evaluate_strings(
        prediction=ai_response,
        input=str(inputs), # Pass the original input for context
        reference=f"Insights: {test_data_entry['expected_response_insights']}\nRisks: {test_data_entry['expected_response_risks']}"
    )

    return {
        "ai_response": ai_response,
        "insights_exact_match": insights_match['score'],
        "risks_exact_match": risks_match['score'],
        "llm_eval_score": llm_eval_result['score'],
        "llm_eval_reasoning": llm_eval_result['reasoning']
    }

# Example for bug improvement evaluation (similar structure)
def evaluate_bug_improvement(llm_chain, test_data_entry, llm_model_for_eval):
    inputs = {
        "bug_title": test_data_entry['bug_title'],
        "bug_description": test_data_entry['bug_description'],
        "bug_labels": test_data_entry['bug_labels']
    }
    ai_response = llm_chain.invoke(inputs)

    criteria_evaluator = CriteriaEvalChain.from_llm(
        llm=llm_model_for_eval,
        criteria={
            "clarity": "The improved description must be clear and easy to understand.",
            "completeness": "The improved description should suggest all relevant sections (steps, actual, expected, env).",
            "actionability": "The suggestions should make the bug report more actionable for developers.",
            "labels_relevance": "The suggested labels should be relevant and useful for categorization."
        }
    )
    llm_eval_result = criteria_evaluator.evaluate_strings(
        prediction=ai_response,
        input=str(inputs),
        reference=test_data_entry['expected_improved_description']
    )
    return {
        "ai_response": ai_response,
        "llm_eval_score": llm_eval_result['score'],
        "llm_eval_reasoning": llm_eval_result['reasoning']
    }