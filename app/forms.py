from django import forms

class EmailForm(forms.Form):
    # recipients = forms.CharField(label='Recipient', widget=forms.Textarea)
    topic = forms.CharField(label='Topic')
    imagine = forms.CharField(label='Describe the image you want to see')
    # attachment = forms.FileField(label='Attachment', required=False)


# class news(forms.Form):
#     topic = forms.CharField(label='Topic')


# class imagine(forms.Form):
#     topic = forms.CharField(label="Describe the image you want to see")