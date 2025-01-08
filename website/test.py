import openai

# Set your OpenAI API key
openai.api_key = "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"

def check_company_in_industry_gpt3(company, industry):
    """Check if a company belongs to a specified industry using GPT-3."""
    prompt = f"Is {company} a {industry} company? Please respond with 'Yes' or 'No' only."

    # Request GPT-3 to generate a completion based on the prompt
    response = openai.Completion.create(
        engine="gpt-3.5-turbo",  # GPT-3 engine, you can replace with other models if needed
        prompt=prompt,
        max_tokens=2,  # Short answer, enough to say Yes or No
        n=1,  # Number of responses to return
        stop=None,  # No stopping token, let the model decide when to stop
        temperature=0  # Lower temperature means more deterministic responses
    )

    # Extract the model's answer
    answer = response.choices[0].text.strip().lower()

    # Return a boolean based on the answer
    if "yes" in answer:
        return True
    elif "no" in answer:
        return False
    else:
        return None  # If the model's response is unclear or does not contain Yes/No
    

if(check_company_in_industry_gpt3("Apple","Tech")):
    print("yeaaa")