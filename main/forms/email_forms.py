from django import forms

class SendCVEmailForm(forms.Form):
    recipient_email = forms.EmailField(
        label='Recipient Email',
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter recipient email address',
            'required': True
        })
    )

    sender_name = forms.CharField(
        label='Your Name (Optional)',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your name (optional)'
        })
    )

    message = forms.CharField(
        label='Additional Message (Optional)',
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Add a personal message (optional)'
        })
    )

    def clean_recipient_email(self):
        email = self.cleaned_data.get('recipient_email')
        if not email:
            raise forms.ValidationError('Email address is required.')
        return email.lower()

    def clean_sender_name(self):
        name = self.cleaned_data.get('sender_name', '').strip()
        return name
