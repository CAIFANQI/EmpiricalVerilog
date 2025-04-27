from openai import OpenAI
from typing import List, Dict
from dotenv import load_dotenv 
import os

load_dotenv()
API_KEY = os.getenv("DEEPSEEK_API_KEY")
client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")
def generate(messages: List[Dict[str, str]], max_tokens=50, n=1) -> List[str]:
    for message in messages:
        assert ("role" in message and "content" in message), "Invalid message format. Each message must contain 'role' and 'content' keys."
        assert (message["role"] in ["user", "system"]), "Role must be either 'user' or 'system'."

    """Use DeepSeek v3 API to generate something given prompt
    Args:
        prompt (str)
        max_tokens (int): The maximum number of tokens to generate.
        n (int): The number of completions to generate for each prompt.
    
    Returns:
        str: generated text
    """
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        max_tokens=max_tokens,
        n=n,
    )
    return [choice.message.content for choice in message.choices]

    
    
def generate_docstring(code_snippet, max_tokens, n) -> List[str]:
    """Call DeepSeek v3 API to generate a docstring for a given code snippet.

    Args:
        code_snippet (str): The code snippet for which the docstring is to be generated.
        max_tokens (int): The maximum number of tokens to generate.
        n (int): The number of completions to generate for each prompt.

    Returns:
        str: The generated docstring, or an error message if the API call fails.
    """
    messages = [
        {
            "role": "system",
            "content": """
            You are a docstring generation machine.
            Given a Verilog code module,
            you generate a docstring containing as much detail as possible.
            Begin each docstring with "DOCSTRING_START" and a newline 
            and end with a newline and "DOCSTRING_END".
            """
        },
        {
        "role": "user",
        "content": f"{code_snippet},"
        }
    ]
    return generate(messages, max_tokens=max_tokens, n=n)

def generate_module_from_docstring(docstring: str, max_tokens, n) -> List[str]:
    """Call DeepSeek v3 API to generate code snippet from a given docstring.

    Args:
        docstring (str);
        max_tokens (int): The maximum number of tokens to generate.
        n (int): The number of completions to generate for each prompt.

    Returns:
        str: The generated code snippet, or an error message if the API call fails.
    """
    messages = [
        {
            "role": "system",
            "content": """
            You are a Verilog code generation machine.
            Given a docstring describing a Verilog module,
            you generate a module that implements the docstring as accurately as possible,
            Begin each module with "MODULE_GEN_START" and a newline 
            and end with a newline and "MODULE_GEN_END".
            """
        },
        {
        "role": "user",
        "content": f"{docstring},"
        }
    ]
    return generate(messages, max_tokens=max_tokens, n=n)