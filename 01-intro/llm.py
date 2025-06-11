
import requests
import json
from openai import OpenAI
import os

def build_prompt(query, search_results):
    prompt_template = """
    You're a course teaching assistant. Answer the QUESTION based on the CONTEXT from the FAQ database.
    Use only the facts from the CONTEXT when answering the QUESTION.

    QUESTION: {question}

    CONTEXT:
    {context}
    """.strip()
    
    # prompt_template = """
    # Q: {question}
    # A: {context}
    # """.strip()
        
    
    context = ""
    for doc in search_results:
        context = context + f"section: {doc['section']}\nquestion: {doc['question']}\nanswer: {doc['text']}\n\n"
    
    prompt = prompt_template.format(question=query, context=context).strip()
    
    
    return prompt


def llm(prompt):
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY")
    )

    completion = client.chat.completions.create(
        model="deepseek/deepseek-r1-0528-qwen3-8b:free",
        extra_body={
                "models": ["anthropic/claude-3.5-sonnet", "gryphe/mythomax-l2-13b"]
            },
        messages=[
            {
            "role": "user",
            "content": prompt
            }
        ]
    )
    return completion.choices[0].message.content