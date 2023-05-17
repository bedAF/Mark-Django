from django.shortcuts import render
from .utils import *
# Create your views here.
def fnSendEmail(request):
    if request.method == "POST":
        recipentEmail = request.POST['recipentEmail']
        topic = request.POST['topic']
        emimage_prompt = request.POST['emimage_prompt']
        summarized_headlines = fnGetNews()
        prompt1 = topic.replace("<<AINEWS>>", summarized_headlines).replace("\n", "\n\n")
        conversation1 = []
        email_content = chatgpt_auto(conversation1, prompt1, prompt1)
        # Add HTML line breaks
        email_content = email_content.replace("\n", "<br>")
        # Get today's date
        date = datetime.date.today().strftime("%B %d, %Y")
        # Add the date to the email subject
        email_subject = "Today's AI News 🤖🔥 " + date
        # Get the email body
        email_body = email_content
        image_prompt_response = chatgpt_auto(conversation1, prompt1, emimage_prompt)
        image_path = generate_image(sd_api_key, image_prompt_response)
        sent_result = send_email(mailgun_api_key, recipentEmail, email_subject, email_body, image_path)
        if sent_result == True:
            return render(request=request, template_name="response.html", context={"response": "Success sent email"})
        else:
            return render(request=request, template_name="response.html", context={"response": "Failed send email"})
    return render(request=request, template_name="home.html")