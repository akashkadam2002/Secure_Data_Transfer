from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class EncodeImageForm(forms.Form):
    image = forms.ImageField()
    message = forms.CharField(widget=forms.Textarea, help_text="Enter the message to be encoded.")
    password = forms.CharField(
        max_length=128, 
        widget=forms.PasswordInput, 
        help_text="Enter a password (at least 6 characters long)."
    )
    dest = forms.CharField(initial="encoded_image.png")
    receiver = forms.ModelChoiceField(queryset=User.objects.all(), label="Receiver")

    def __init__(self, *args, **kwargs):
        super(EncodeImageForm, self).__init__(*args, **kwargs)
        self.fields["message"].widget.attrs.update({"class": "custom-message"})
        self.fields["password"].widget.attrs.update({"class": "custom-password"})
        self.fields["dest"].widget.attrs.update({"class": "custom-dest"})
        self.fields["receiver"].widget.attrs.update({"class": "custom-receiver"})

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 6:
            raise forms.ValidationError("Password must be at least 6 characters long.")
        return password
    

class DecodeImageForm(forms.Form):
    encoded_image = forms.ImageField(label="Select the image to decode: ")
    password = forms.CharField(max_length=128, widget=forms.PasswordInput)


class RegistrationForm(UserCreationForm):
    profile_picture = forms.ImageField(required=False, label="Choose Profile Image")
    email = forms.CharField(
        label="Email",
        widget=forms.TextInput(attrs={"placeholder": "akash@gmail.com"}),
    )

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {"class": "custom-username", "placeholder": "Username"}
        )
        self.fields["password1"].widget.attrs.update(
            {"class": "custom-password1", "placeholder": "Enter Password"}
        )
        self.fields["password2"].widget.attrs.update(
            {"class": "custom-password2", "placeholder": "Confirm Password"}
        )
        self.fields["email"].widget.attrs.update({"class": "custom-email"})

    class Meta:
        model = User
        fields = ["username", "password1", "password2", "profile_picture"]


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, label="Enter Username")
    password = forms.CharField(widget=forms.PasswordInput, label="Enter Password")

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"class": "custom-username"})
        self.fields["password"].widget.attrs.update({"class": "custom-password1"})


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Enter your email'}))
