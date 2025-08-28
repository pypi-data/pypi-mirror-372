🤖 llm_toolchain

A simple, powerful, and model-agnostic Python library for building robust LLM agents with tools.

The era of LLMs that just talk is over. The future is agents that act. While modern LLMs have native function-calling, building a truly robust and scalable agent requires a thoughtful framework. llm_toolchain is designed to be that framework.

It's not another bloated, all-encompassing library. It's a lightweight, developer-first toolchain focused on one thing: making it incredibly simple to give your LLM a set of powerful tools and have it reliably execute complex, multi-step tasks.
哲学 (Philosophy)

    Simplicity First: Creating a new tool should be as easy as writing a Python function. The @tool decorator handles all the complex schema generation for you.

    Model-Agnostic: Don't get locked into a single provider. With a powerful adapter system, you can seamlessly switch between different LLMs (like OpenAI, Gemini, or any generic model) without changing your core logic.

    Developer Experience: The library is designed to be intuitive. The Toolchain object abstracts away the entire multi-turn ReAct (Reason-Act) loop into a single, clean .run() method.

✨ Key Features

    Effortless Tool Creation: Define complex tools with a simple @tool decorator. No manual JSON schemas needed.

    Model-Agnostic Adapters: Comes with pre-built, optimized adapters for OpenAI and Google Gemini.

    Universal PromptAdapter: A powerful, catch-all adapter that uses prompt engineering to make almost any chat-based LLM capable of tool use, even if it doesn't have a native function-calling API.

    Automatic ReAct Loop: The .run() method automatically handles the entire conversation: calling the LLM, executing tools, and sending results back until the task is complete.

    Parallel Tool Calling: The agent can intelligently call multiple tools in a single turn to solve complex, multi-part prompts efficiently.

    Rich Library of Pre-built Tools: Get started immediately with a powerful suite of tools for file system operations, web browsing, code execution, and more.

🚀 Installation

Install the core library from PyPI:

pip install llm_toolchain

To use specific LLM clients, install them as "extras." This keeps the core library lightweight.

# To use with OpenAI models
pip install llm_toolchain[openai]

# To use with Google Gemini models
pip install llm_toolchain[gemini]

# To install everything for development
pip install llm_toolchain[openai,gemini]

⚡ Quickstart

This example uses the OpenAIAdapter to answer a question that requires calling two different tools in parallel.

import os
from openai import OpenAI
from dotenv import load_dotenv

# 1. Import the Toolchain and the tools you need
from llm_toolchain.core import Toolchain
from llm_toolchain.tools import get_weather, calculate_compound_interest

# 2. Load your API key (from a .env file)
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 3. Initialize the Toolchain with your LLM client and tools
chain = Toolchain(llm=client, tools=[get_weather, calculate_compound_interest])

# 4. Define a complex prompt
prompt = (
    "I have $17,000. How much will I have in 10 years if I invest it at an "
    "annual interest rate of 5%? Also, what's the weather like in New York City today?"
)

# 5. Run it!
# The Toolchain will automatically call both tools and synthesize a final answer.
final_response = chain.run(prompt=prompt, model="gpt-4o")

print(final_response)
# Expected Output:
# "In 10 years, your $17,000 investment will grow to $27,691.21.
#  The weather in New York City today is currently [Real-time weather data]."

🔌 Using Different Adapters

Switching models is as simple as changing the client and the adapter.
Google Gemini

import google.generativeai as genai
from llm_toolchain.adapters import GeminiAdapter

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
gemini_client = genai.GenerativeModel('gemini-1.5-flash')

# Just pass the new client and adapter!
chain = Toolchain(
    llm=gemini_client,
    tools=[...],
    adapter=GeminiAdapter()
)
chain.run(prompt="...")

Any Other Chat Model (with the PromptAdapter)

The PromptAdapter will intelligently discover how to interact with almost any LLM client.

from some_other_llm_library import SomeClient
from llm_toolchain.adapters import PromptAdapter

# The adapter will figure out how to call this client automatically
unknown_client = SomeClient(api_key="...")

chain = Toolchain(
    llm=unknown_client,
    tools=[...],
    adapter=PromptAdapter() # The catch-all adapter
)
chain.run(prompt="...")

🛠️ Creating Your Own Tools

Creating a new tool is incredibly simple. Just write a standard Python function with type hints and a clear docstring, then add the @tool decorator.

from llm_toolchain.core import tool

@tool
def create_meeting_summary(attendees: list[str], topic: str, key_decisions: str):
    """
    Formats meeting notes into a clean summary.

    Args:
        attendees: A list of names of people who attended.
        topic: The main topic of the meeting.
        key_decisions: A summary of the key decisions made.
    """
    summary = f"## Meeting Summary: {topic}\n\n"
    summary += f"**Attendees:** {', '.join(attendees)}\n\n"
    summary += f"**Key Decisions:**\n- {key_decisions.replace('. ', '.\\n- ')}"
    return {"meeting_summary": summary}

🧰 Available Tools

llm_toolchain comes with a powerful set of pre-built tools, ready to use out of the box.

    File System: list_files, read_file, write_file, append_to_file, delete_file, change_directory

    Web Access: get_weather, open_and_read_website

    Data & Logic: run_python_code, calculate_compound_interest, test_regex_pattern, convert_units

    create_calendar_event, visualize_graph

    Geolocation: get_address_from_coordinates

🤝 Contributing

Contributions are welcome! If you have an idea for a new tool, an improvement to an adapter, or a bug fix, please open an issue or submit a pull request.
📜 License

This project is licensed under the MIT License. See the LICENSE file for details.