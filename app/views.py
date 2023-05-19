from django.shortcuts import render
import os
from django.conf import settings
from .forms import EmailForm
from .mail import send_email, generate_image, open_file, save_file
from .mail import chatgpt as chat
from .summarize import *
import datetime
import base64

conversation1 = []

api_key = os.environ.get('OPENAI_APIKEY')
sd_api_key = os.environ.get('SDAPI_KEY')
mailgun_api_key = os.environ.get('MAILGUN_API')


prompt = os.path.join(settings.PROMPT)
chatbot = os.path.join(settings.CHATBOT)

# Create your views here.
def fnIndex(request):
    return render(request=request, template_name="home.html")

def fnSendEmail(request):
    if request.method == "POST":
        # form = EmailForm(request.POST, request.FILES)
        # recipients = form.cleaned_data['recipients']
        topic = request.POST['topic']
        imagine = request.POST['emimage_prompt']
        # attachment = request.FILES.get('attachment')

        # Perform chatgpt and generate_image operations as needed
        # ...
        headlines = fetch_ai_news(topic)
        summarized_headlines = summarize_headlines(headlines)
        save_headlines_to_file("news_summaries.txt", summarized_headlines)
        news_file = open_file("news_summaries.txt")
        print(news_file)
        prompt1 = open_file(prompt).replace("<<Agent PathFinder>>", news_file).replace("\n", "\n\n")
        shorten = prompt1[:2000]
        # Send the email with the generated image attached all emails
        """For the news"""

        news_content = chat(api_key, conversation1, prompt1, prompt1)
        print("conversations :", conversation1)
        news_content = news_content.replace("\n", "<br>")
        image_prompt = chat(api_key, conversation1, shorten, imagine)
        # get today's date
        today = datetime.date.today().strftime("%B %d, %Y")

        # Add the date to the email subject
        news_subject = f"Today's {topic} News " + today
        # get the email body
        news_body = news_content
        if imagine != "":
            try:
                image_path = generate_image(sd_api_key, image_prompt)
                sent_result = send_email(mailgun_api_key, news_subject, news_body, image_path)
            except:
                return render(request=request, template_name="response.html", context={"response": "Failed generate image"})
        else:
            sent_result = send_email(mailgun_api_key, news_subject, news_body, image_path)
            print("sent_result :", sent_result)
        if sent_result != True:
            return render(request=request, template_name="response.html", context={"response": "Failed send email"})
        else:
            return render(request=request, template_name="response.html", context={"response": "Your email has been sent successfully."})
        # return render(request=request, template_name="response.html", context={"response": "Failed send email"})
    return render(request=request, template_name="home.html")