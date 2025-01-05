import os
import openai
from django.http import JsonResponse


# Use environment variables for API key
openai.api_key = "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"


def generate_email_suggestions(description):
    # try:
    #     response = openai.ChatCompletion.create(
    #         model="gpt-3.5-turbo",
    #         messages=[
    #             {"role": "system", "content": "You are an expert marketing assistant."},
    #             {"role": "user", "content": f"Generate 3 marketing email suggestions. Campaign description: {description}"}
    #         ],
    #         max_tokens=150,
    #         temperature=0.7  # Creativity level
    #     )
    #     # Extract suggestions
    #     suggestions = response["choices"][0]["message"]["content"].split("\n")
    #     return [suggestion.strip() for suggestion in suggestions if suggestion.strip()]
    # except Exception as e:
    #     raise RuntimeError(f"OpenAI API error: {str(e)}")
     return [
        "Subject Line: 'Transform Your Inbox!'",
        "Body: 'Discover how our product can make your life easier today!'"
    ]
