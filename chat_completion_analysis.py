"""
Assignment: Python Script Calling Chat Completion API
with Automated Token & Cost Analysis

Requirements:
    pip install openai

Set your API key before running:
    Windows PowerShell:
        $env:OPENAI_API_KEY="your_new_api_key"
    macOS/Linux:
        export OPENAI_API_KEY="your_new_api_key"

Optional: Set the model's official prices (USD per 1 million tokens).
Do not guess these values; check the pricing supplied by your course/API provider.
    Windows PowerShell:
        $env:INPUT_PRICE_PER_1M="..."
        $env:OUTPUT_PRICE_PER_1M="..."
    macOS/Linux:
        export INPUT_PRICE_PER_1M="..."
        export OUTPUT_PRICE_PER_1M="..."

Run:
    python chat_completion_analysis.py
"""

import os
from decimal import Decimal, InvalidOperation
from openai import OpenAI

MODEL_NAME = "gpt-6-luna"


def read_price_from_environment(variable_name):
    """Return a non-negative price, or None if no valid price was supplied."""
    raw_value = os.getenv(variable_name)

    if raw_value is None or raw_value.strip() == "":
        return None

    try:
        price = Decimal(raw_value)
        if price < 0:
            raise ValueError
        return price
    except (InvalidOperation, ValueError):
        raise ValueError(
            f"{variable_name} must contain a non-negative number."
        )


def calculate_cost(input_tokens, output_tokens, input_price, output_price):
    """
    Calculate USD cost from token counts and prices per 1,000,000 tokens.
    Returns None if either price has not been configured.
    """
    if input_price is None or output_price is None:
        return None

    one_million = Decimal("1000000")
    input_cost = Decimal(input_tokens) * input_price / one_million
    output_cost = Decimal(output_tokens) * output_price / one_million
    return input_cost + output_cost


def main():
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("Error: OPENAI_API_KEY is not set.")
        print("Set your API key as an environment variable, then run again.")
        return

    input_price = read_price_from_environment("INPUT_PRICE_PER_1M")
    output_price = read_price_from_environment("OUTPUT_PRICE_PER_1M")

    # The SDK reads the secret key from this variable.
    client = OpenAI(api_key=api_key)

    total_input_tokens = 0
    total_output_tokens = 0
    total_cost = Decimal("0")
    request_count = 0
    cost_is_configured = input_price is not None and output_price is not None

    print(f"Chat Completion API - Model: {MODEL_NAME}")
    print("Enter a prompt and press Enter. Type 'exit' to finish.\n")

    while True:
        user_prompt = input("You: ").strip()

        if user_prompt.lower() in {"exit", "quit"}:
            break

        if not user_prompt:
            print("Please enter a prompt.\n")
            continue

        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant. Answer clearly."
                    },
                    {"role": "user", "content": user_prompt}
                ]
            )

            answer = response.choices[0].message.content
            usage = response.usage

            # Chat Completions reports usage for the completed request.
            input_tokens = usage.prompt_tokens
            output_tokens = usage.completion_tokens
            total_tokens = usage.total_tokens

            request_cost = calculate_cost(
                input_tokens,
                output_tokens,
                input_price,
                output_price
            )

            total_input_tokens += input_tokens
            total_output_tokens += output_tokens
            request_count += 1

            print("\nAssistant:")
            print(answer or "(The model returned an empty response.)")
            print("\nRequest usage:")
            print(f"Input tokens:  {input_tokens}")
            print(f"Output tokens: {output_tokens}")
            print(f"Total tokens:  {total_tokens}")

            if request_cost is not None:
                total_cost += request_cost
                print(f"Estimated request cost: ${request_cost:.8f} USD")
            else:
                print("Request cost: Not calculated.")
                print(
                    "Set INPUT_PRICE_PER_1M and OUTPUT_PRICE_PER_1M "
                    "using the official model prices."
                )

            print("-" * 50)

        except Exception as error:
            print(f"\nAPI request failed: {error}")
            print(
                "Check your API key, internet connection, account access, "
                "and whether the model name is enabled for your account.\n"
            )

    print("\n========== FINAL USAGE SUMMARY ==========")
    print(f"Successful requests: {request_count}")
    print(f"Total input tokens:  {total_input_tokens}")
    print(f"Total output tokens: {total_output_tokens}")
    print(f"Total tokens:        {total_input_tokens + total_output_tokens}")

    if cost_is_configured:
        print(f"Estimated total cost: ${total_cost:.8f} USD")
    else:
        print("Total cost: Not calculated (model prices were not configured).")

    print("===========================================")


if __name__ == "__main__":
    main()
