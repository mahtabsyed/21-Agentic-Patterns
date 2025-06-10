import os
import requests
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
import json

# Use updated imports as per LangChain deprecation warning
from langchain_openai import ChatOpenAI

# Load .env variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

if not OPENAI_API_KEY or not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
    raise ValueError("Please set OPENAI_API_KEY, GOOGLE_API_KEY, and GOOGLE_CSE_ID in your .env file.")

# Prompt template for classification
classification_prompt = ChatPromptTemplate.from_template("""
Classify the following user prompt into one of the following categories:

1. Simple
2. Needs Reasoning Model
3. Needs Google Search + Info Aggregation using Simple or Reasoning Model

Also explain why.

User Prompt:
"{user_prompt}"

Return as JSON:
{{
  "classification": "...",
  "reasoning": "..."
}}
""")

# LangChain setup for classifier using RunnableSequence (prompt | llm)
classifier_llm = ChatOpenAI(
    model_name="gpt-4o-mini",
    temperature=0,
    openai_api_key=OPENAI_API_KEY
)
classification_chain = classification_prompt | classifier_llm

# Google search using Custom Search API
def google_search(query, api_key, cse_id, num_results=5):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": cse_id,
        "q": query,
        "num": num_results
    }
    response = requests.get(url, params=params)
    results = response.json()
    return [item['snippet'] for item in results.get("items", [])]

# Generate final response based on classification
def generate_response(user_prompt, classification, google_results=None):
    if classification == "Simple":
        model_name = "gpt-4o-mini"
    elif classification == "Needs Reasoning Model":
        model_name = "o4-mini"
    else:  # Needs Google
        model_name = "o4-mini" if "Reasoning" in classification else "gpt-4o-mini"

    model = ChatOpenAI(model_name=model_name, temperature=0, openai_api_key=OPENAI_API_KEY)

    if google_results:
        search_context = "\n".join(google_results)
        prompt = f"""
Use the following search results to answer the prompt:
{search_context}

Prompt: {user_prompt}
"""
    else:
        prompt = user_prompt

    # Use RunnableSequence for response_chain
    response_chain = ChatPromptTemplate.from_template("{prompt}") | model
    return response_chain.invoke({"prompt": prompt})

# Entry point
def main(user_prompt):
    classification_result = classification_chain.invoke({"user_prompt": user_prompt})
    try:
        # If result is an object with 'content', extract it
        if hasattr(classification_result, "content"):
            classification_result = classification_result.content
        # Remove code block markers and leading/trailing whitespace
        if classification_result.strip().startswith("```") and classification_result.strip().endswith("```"):
            classification_result = classification_result.strip()[3:-3].strip()
        elif classification_result.strip().startswith("```"):
            classification_result = classification_result.strip()[3:].strip()
        elif classification_result.strip().endswith("```"):
            classification_result = classification_result.strip()[:-3].strip()

        # Find the first and last curly braces to extract the JSON substring
        start = classification_result.find('{')
        end = classification_result.rfind('}') + 1
        json_str = classification_result[start:end]
        result = json.loads(json_str)
        classification = result["classification"]
        reasoning = result["reasoning"]
    except Exception as e:
        return {"error": f"Failed to parse classifier output: {e}\nRaw output: {classification_result}"}

    google_results = None
    if classification.startswith("Needs Google"):
        google_results = google_search(user_prompt, GOOGLE_API_KEY, GOOGLE_CSE_ID)

    final_response = generate_response(user_prompt, classification, google_results)

    return {
        "classification": classification,
        "reasoning": reasoning,
        "response": final_response
    }

# Example usage
if __name__ == "__main__":
    user_prompt = input("Enter a prompt: ")
    result = main(user_prompt)
    if "error" in result:
        print("\n=== Error ===")
        print(result["error"])
    else:
        print("\n=== Classification ===")
        print(result["classification"])
        print("\n=== Reasoning ===")
        print(result["reasoning"])
        print(result["response"])
