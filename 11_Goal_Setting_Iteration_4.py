# MIT License
# Copyright (c) 2025 Mahtab Syed
# https://www.linkedin.com/in/mahtabsyed/
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so.

"""
Hands-On Code Example - Iteration 4
- To illustrate the Goal Setting and Monitoring pattern, we have an example using LangChain and OpenAI APIs:

Objective: Build an AI Agent which can write code for a specified use case based on specified goals:
- Accepts a coding problem (use case) in code or can be as input.
- Accepts a list of goals (e.g., "simple", "tested", "handles edge cases")  in code or can be input.
- Uses an LLM (like GPT-4o) to generate and refine Python code until the goals are met. (I am using max 5 iterations, this could be based on a set goal as well)
- To check if we have met our goals I am asking the LLM to judge this and answer with a confidence score 1-10, which makes it easier to stop the iterations.
- Saves the final code in a .py file with a clean filename and a header comment.
"""

import os
import random
import re
import time
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
from langchain_openai import ChatOpenAI
from openai import OpenAIError
import requests

# 🔐 Load environment variables
_ = load_dotenv(find_dotenv())
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise EnvironmentError("❌ Please set the OPENAI_API_KEY environment variable.")

# ✅ Initialize LLM
print("📡 Initializing OpenAI LLM (gpt-4o)...")
llm = ChatOpenAI(model="gpt-4o", temperature=0.3, openai_api_key=OPENAI_API_KEY)

# --- Utility: Safe LLM Call ---
def safe_llm_invoke(prompt: str, max_retries: int = 3, delay: float = 1.0):
    for attempt in range(max_retries):
        try:
            return llm.invoke(prompt)
        except (OpenAIError, requests.exceptions.RequestException) as e:
            print(f"⚠️ LLM call failed (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(delay)
                delay *= 2
            else:
                print("❌ Maximum retries reached. Skipping this step.")
                return None

# --- Prompt Builders ---
def generate_prompt(use_case: str, goals: list[str], previous_code: str = "", feedback: str = "") -> str:
    print("📝 Constructing prompt for code generation...")
    base_prompt = f"""
    You are an AI coding agent. Your job is to write Python code based on the following use case:

    Use Case: {use_case}

    Your goals are:
    {chr(10).join(f"- {g.strip()}" for g in goals)}
    """
    if previous_code:
        print("🔄 Adding previous code to the prompt for refinement.")
        base_prompt += f"\nPreviously generated code:\n{previous_code}"
    if feedback:
        print("📋 Including feedback for revision.")
        base_prompt += f"\nFeedback on previous version:\n{feedback}\n"

    base_prompt += "\nPlease return only the revised Python code. Do not include comments or explanations outside the code."
    return base_prompt

def get_code_feedback(code: str, goals: list[str]) -> str:
    print("🔍 Evaluating code against the goals...")
    feedback_prompt = f"""
    You are a Python code reviewer. A code snippet is shown below. Based on the following goals:

    {chr(10).join(f"- {g.strip()}" for g in goals)}

    Please critique this code and identify if the goals are met. Mention if improvements are needed for clarity, simplicity, correctness, edge case handling, or test coverage.

    Code:
    {code}
    """
    response = safe_llm_invoke(feedback_prompt)
    return response if response else None

def goals_met(feedback_text: str, goals: list[str]) -> tuple[bool, int]:
    """
    Uses the LLM to evaluate whether the goals have been met based on the feedback text.
    Returns a tuple: (bool, confidence_score)
    """
    review_prompt = f"""
    You are an AI reviewer.

    Here are the goals:
    {chr(10).join(f"- {g.strip()}" for g in goals)}

    Here is the feedback on the code:
    \"\"\"
    {feedback_text}
    \"\"\"

    Evaluate how well the goals have been met on a confidence scale from 1 to 10,
    where 1 means "not met at all" and 10 means "fully met with no changes needed".

    Respond ONLY with the confidence number, nothing else.
    """
    response_obj = safe_llm_invoke(review_prompt)
    if not response_obj:
        return (False, 0)

    response = response_obj.content.strip()
    try:
        score = int(re.search(r"\d+", response).group())
        print(f"📊 Confidence score returned by LLM: {score}/10")
        return (score >= 8, score)
    except Exception:
        print(f"⚠️ Could not parse score from: '{response}'")
        return (False, 0)

# --- Helpers ---
def clean_code_block(code: str) -> str:
    lines = code.strip().splitlines()
    if lines and lines[0].strip().startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines).strip()

def add_comment_header(code: str, use_case: str) -> str:
    comment = f"# This Python program implements the following use case:\n# {use_case.strip()}\n"
    return comment + "\n" + code

def save_code_to_file(code: str, use_case: str) -> str:
    print("💾 Saving final code to file...")

    summary_prompt = (
        f"Summarize the following use case into a single lowercase word or phrase, "
        f"no more than 10 characters, suitable for a Python filename:\n\n{use_case}"
    )
    response_obj = safe_llm_invoke(summary_prompt)
    if not response_obj:
        print("❌ Failed to summarize use case. Using fallback name.")
        short_name = "autogen"
    else:
        raw_summary = response_obj.content.strip()
        short_name = re.sub(r"[^a-zA-Z0-9_]", "", raw_summary.replace(" ", "_").lower())[:10]

    random_suffix = str(random.randint(1000, 9999))
    filename = f"{short_name}_{random_suffix}.py"
    filepath = Path.cwd() / filename

    with open(filepath, "w") as f:
        f.write(code)

    print(f"✅ Code saved to: {filepath}")
    return str(filepath)

# --- Main Loop ---
def run_code_agent(use_case: str, goals_input: str, max_iterations: int = 5) -> str:
    goals = [g.strip() for g in goals_input.split(",")]

    print(f"\n🎯 Use Case: {use_case}")
    print("🎯 Goals:")
    for g in goals:
        print(f"  - {g}")

    previous_code = ""
    feedback = ""

    for i in range(max_iterations):
        print(f"\n=== 🔁 Iteration {i + 1} of {max_iterations} ===")
        prompt = generate_prompt(use_case, goals, previous_code, feedback if isinstance(feedback, str) else feedback.content)

        print("🚧 Generating code...")
        response_obj = safe_llm_invoke(prompt)
        if not response_obj:
            print("❌ Code generation failed. Skipping iteration.")
            continue

        raw_code = response_obj.content.strip()
        code = clean_code_block(raw_code)
        print("\n🧾 Generated Code:\n" + "-" * 50 + f"\n{code}\n" + "-" * 50)

        print("\n📤 Submitting code for feedback review...")
        feedback = get_code_feedback(code, goals)
        if not feedback:
            print("❌ Feedback failed. Skipping iteration.")
            continue

        feedback_text = feedback.content.strip()
        print("\n📥 Feedback Received:\n" + "-" * 50 + f"\n{feedback_text}\n" + "-" * 50)

        met, score = goals_met(feedback_text, goals)
        print(f"📈 Confidence Score: {score}/10")
        if met:
            print("✅ LLM confirms goals are met. Stopping iteration.")
            break

        print("🛠️ Goals not fully met. Preparing for next iteration...")
        previous_code = code

    final_code = add_comment_header(code, use_case)
    return save_code_to_file(final_code, use_case)

# --- CLI Test Run ---
if __name__ == "__main__":
    print("\n🧠 Welcome to the AI Code Generation Agent")

    # Example 1
    # use_case_input = "Write code to find BinaryGap of a given positive integer"
    # goals_input = "Code simple to understand, Functionally correct, Handles comprehensive edge cases, Takes positive integer input only, prints the results with few examples"
    # run_code_agent(use_case_input, goals_input)


    # Example 2
    use_case_input = "Write code to count the number of files in current directory and all its nested sub directories, and print the total count"
    goals_input = (
        "Code simple to understand, Functionally correct, Handles comprehensive edge cases, Ignore recommendations for performance, Ignore recommendations for test suite use like unittest or pytest"
    )
    run_code_agent(use_case_input, goals_input)


    # Example 3
    # use_case_input = "Write code which takes a command line input of a word doc or docx file and opens it and counts the number of words, and characters in it and prints all"
    # goals_input = "Code simple to understand, Functionally correct, Handles edge cases"
    # run_code_agent(use_case_input, goals_input)

    # Example 4
    # use_case_input = "Write code to create a simple car race game with my car and many other moving cars on different lanes like a real race. Use Pygame library for this. The game should have a simple GUI, a scoreboard with time remaining and lives remaining, and should handle edge cases like collisions and out of bounds. The road should be a simple straight road with lanes, and the player car should be controlled by arrow keys. The game should end when the player runs out of lives or time."
    # goals_input = "Code simple to understand, Functionally correct, Handles edge cases, Uses Pygame library, Has a simple GUI, Has a scoreboard with time remaining and lives remaining"
    # run_code_agent(use_case_input, goals_input)


