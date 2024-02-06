# utils.py
import secrets
from django.core.mail import send_mail
from django.utils import timezone

def generate_activation_code():
    # Implement your activation code generation logic here
    # This can be a random string, a hash, or any other method of your choice
    return secrets.token_urlsafe(32)

def send_activation_email(user):
    activation_code = generate_activation_code()

    # Save the activation code and creation time to the author
    user.activation_code = activation_code
    user.activation_code_created_at = timezone.now()
    user.save()

    # Send activation code via email
    subject = 'Account Activation Code'
    message = f'Your activation code is: {activation_code}'
    from_email = 'ashishsunuwar914@gmail.com'  # Update with your email address or use a configured email backend
    to_email = user.author.email

    send_mail(subject, message, from_email, [to_email])
