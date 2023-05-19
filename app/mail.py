import openai
import os
import requests
import re
from colorama import Fore, Style, init
import base64
import datetime

# Import emfetch and execute the main function
# import summarize
from django.conf import settings
recipients = "ms@afterflea.com"

# Initialize colorama
init()

# Define a function to open a file and return its contents as a string
def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()

# Define a function to save content to a file
def save_file(filepath, content):
    with open(filepath, 'a', encoding='utf-8') as outfile:
        outfile.write(content)

# Set the OpenAI API keys by reading them from files
api_key = os.environ.get('OPENAI_APIKEY')
sd_api_key = os.environ.get('SDAPI_KEY')
mailgun_api_key = os.environ.get('MAILGUN_API')
mailgun_link = os.environ.get('MAILGUN_LINK')
domain = os.environ.get('DOMAIN')

# Initialize an empty list to store the conversations
conversation1 = []

# Define a function to make an API call to the OpenAI ChatCompletion endpoint
def chatgpt(api_key, conversation, chatbot, user_input, temperature=0.7, frequency_penalty=0.2,
presence_penalty=0):

    # Set the API key
    openai.api_key = api_key

    # Update conversation by appending the user's input
    conversation.append({"role": "user","content": user_input})
    

    # Insert prompt into message history
    messages_input = conversation.copy()
    prompt = [{"role": "system", "content": chatbot}]
    messages_input.insert(0, prompt[0])

    # Make an API call to the ChatCompletion endpoint with the updated messages
    completion = openai.ChatCompletion.create(
        model="gpt-4",
        temperature=temperature,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        messages=messages_input)

    # Extract the chatbot's response from the API response
    chat_response = completion['choices'][0]['message']['content']

    # Update conversation by appending the chatbot's response
    conversation.append({"role": "assistant", "content": chat_response})
    print("conversations :", conversation)

    # Return the chatbot's response
    return chat_response

# TODO: remember to change the recipient email address
def send_email(mailgun_api_key, subject, body, attachment=None):
    data = {
        "from":f"Shafik - Afterflea <{domain}>",
        "to": f"{recipients}",
        "subject": subject,
        "html": body,
    }

    if attachment:
        with open(attachment, 'rb') as f:
            files = {'attachment': (os.path.basename(attachment), f)}
            response = requests.post(
                f"{mailgun_link}",
                auth=("api", mailgun_api_key),
                data=data,
                files=files
            )
    else:
        response = requests.post(
                f"{mailgun_link}",
            auth=("api", mailgun_api_key),
            data=data
        )

    if response.status_code != 200:
        raise Exception("Failed to send email: " + str(response.text))

    print("Email sent successfully.")


def generate_image(api_key, text_prompt, height=512, width=512, cfg_scale=7, clip_guidance_preset="FAST_BLUE", steps=50, samples=1):
    api_host = 'https://api.stability.ai'
    engine_id = "stable-diffusion-xl-beta-v2-2-2"

    response = requests.post(
        f"{api_host}/v1/generation/{engine_id}/text-to-image",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        json={
            "text_prompts": [
                {
                    "text": text_prompt
                }
            ],
            "cfg_scale": cfg_scale,
            "clip_guidance_preset": clip_guidance_preset,
            "height": height,
            "width": width,
            "samples": samples,
            "steps": steps,
        },
    )

    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))

    data = response.json()
    image_data = data["artifacts"][0]["base64"]

    # Save the generated image to a file with a unique name in the "SDimages" folder
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    image_filename = os.path.join(settings.GENERATED_IMAGES_DIR, f"generated_image_{timestamp}.png")

    with open(image_filename, "wb") as f:
        f.write(base64.b64decode(image_data))

    return image_filename