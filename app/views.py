from django.shortcuts import render
from .utils import *
# Create your views here.
def fnIndex(request):
    return render(request=request, template_name="home.html")

def fnSendEmail(request):
    if request.method == "POST":
            recipentEmail = request.POST['recipentEmail']
            topic = request.POST['topic']
            emimage_prompt = request.POST['emimage_prompt']

            headlines = fetch_ai_news()
            summarized_headlines = summarize_headlines(headlines)
            # # Save the summarized headlines to a text file
            ainews = save_headlines_to_file(summarized_headlines)
            print(ainews)
            prompt1 = topic.replace("<<AINEWS>>", ainews).replace("\n", "\n\n")
            conversation1 = []
            email_content = chatgpt_auto(conversation1, prompt1, prompt1)
            # Add HTML line breaks
            email_content = email_content.replace("\n", "<br>")
            # Get today's date
            date =datetime.today().strftime("%B %d, %Y")
            # Add the date to the email subject
            email_subject = "Today's AI News 🤖🔥 " + date
            # Get the email body
            email_body = email_content
            image_prompt_response = chatgpt_auto(conversation1, prompt1, emimage_prompt)
            if emimage_prompt != "":
                try:
                    image_path = generate_image(image_prompt_response)
                    sent_result = send_email(recipentEmail, email_subject, email_body, image_path)
                except:
                    return render(request=request, template_name="response.html", context={"response": "Failed generate image"})
            else:
                sent_result = send_email(recipentEmail, email_subject, email_body)
            if sent_result == True:
                return render(request=request, template_name="response.html", context={"response": "Your email has been sent successfully."})
            else:
                return render(request=request, template_name="response.html", context={"response": "Failed send email"})
            # return render(request=request, template_name="response.html", context={"response": "Failed send email"})
    return render(request=request, template_name="home.html")