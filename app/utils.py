from googleapiclient.discovery import build
import openai
import os
import requests
from datetime import datetime
import base64

openai.api_key = os.getenv("OPENAI_APIKEY")
mailgun_api_key = os.getenv("MAILGUN_API")
sd_api_key = os.getenv("SDAPI_KEY")
developerKey=os.getenv("GOOGLE_SEARCH_API_KEY")
google_custome_search = os.getenv("GOOGLE_SEARCH_CX")
mailgun_link = os.getenv("MAILGUN_LINK")


def fetch_ai_news():
    print("34", os.getenv("SDAPI_KEY"))

    search_engine = build("customsearch", "v1", developerKey=developerKey)
    query = "AI site:news.google.com"
    results = search_engine.cse().list(q=query, cx=google_custome_search, num=6).execute()
    print("results", results)
    # Extract the titles, snippets, and URLs
    news_items = [{'title': result['title'], 'snippet': result['snippet'], 'url': result['link']} for result in results['items']]
    return news_items


def summarize_headlines(news_items):
    summarized_headlines = []
    for item in news_items:
        headline = item['title']
        snippet = item['snippet']
        url = item['url']
        summary, conversation = chatgpt([],f"Please summarize the following headline, snippet and include link(url) for each snippet: {headline} - {snippet} - {url}")
        summarized_headlines.append(summary)
    return summarized_headlines, conversation

def save_headlines_to_file(headlines):
    result = ""
    for headline in headlines:
        result += headline + "\n"
    return result

def chatgpt(conversation, user_input, temperature=1, frequency_penalty=0.2, presence_penalty=0):
    conversation.append({"role": "user", "content": user_input})
    messages_input = conversation.copy()

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=temperature,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        messages=messages_input)

    chat_response = completion['choices'][0]['message']['content']
    conversation.append({"role": "assistant", "content": chat_response})
    return chat_response, conversation

def chatgpt_auto(conversation, chatbot, user_input, temperature=0.7, frequency_penalty=0.2, presence_penalty=0):
    # Update conversation by appending the user's input
    conversation.append({"role": "user","content": user_input})
    # Insert prompt into message history
    messages_input = conversation.copy()
    prompt = [{"role": "system", "content": chatbot}]
    messages_input.insert(0, prompt[0])
    # Make an API call to the ChatCompletion endpoint with the updated messages
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=temperature,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        messages=messages_input)
    # Extract the chatbot's response from the API response
    chat_response = completion['choices'][0]['message']['content']
    # Update conversation by appending the chatbot's response
    conversation.append({"role": "assistant", "content": chat_response})
    # Return the chatbot's response
    return chat_response

def send_email(recipients, subject, body, attachment=None):
    data = {
        "from":"Mark - Afterflea <mohamed@sandboxd34a95b1834b4c658c64618856a6c38a.mailgun.org>",
        "to": recipients,
        "subject": subject,
        "html": body,
    }

    if attachment:
        with open(attachment, 'rb') as f:
            files = {'attachment': (os.path.basename(attachment), f)}
            response = requests.post(
                "https://api.mailgun.net/v3/sandboxd34a95b1834b4c658c64618856a6c38a.mailgun.org/messages",
                auth=("api", mailgun_api_key),
                data=data,
                files=files
            )
    else:
        response = requests.post(
            "https://api.mailgun.net/v3/sandboxd34a95b1834b4c658c64618856a6c38a.mailgun.org/messages",
            auth=("api", mailgun_api_key),
            data=data
        )

    if response.status_code != 200:
        print("Failed send email")
        return False
        # raise Exception("Failed to send email: " + str(response.text))

    print("Email sent successfully.")
    return True

def generate_image(text_prompt, height=512, width=512, cfg_scale=7, clip_guidance_preset="FAST_BLUE", steps=50, samples=1):
    api_host = 'https://api.stability.ai'
    engine_id = "stable-diffusion-xl-beta-v2-2-2"

    response = requests.post(
        f"{api_host}/v1/generation/{engine_id}/text-to-image",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {sd_api_key}"
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
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    image_filename = os.path.join("SDimages", f"generated_image_{timestamp}.png")

    with open(image_filename, "wb") as f:
        f.write(base64.b64decode(image_data))

    return image_filename

def fnGetNews():
    headlines = fetch_ai_news()
    summarized_headlines, _ = summarize_headlines(headlines)
    result = save_headlines_to_file(summarized_headlines)
    return result
