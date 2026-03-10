from django.core.mail import EmailMessage
from django.conf import settings
from django.shortcuts import redirect, render
from .models import Account
from .forms import RegistrationForm
from django.contrib import messages
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse

def register(request):
    form = RegistrationForm(request.POST)
    if request.method == 'POST':     
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            username = email.split('@')[0]
            user = Account.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password
            )
            user.phone_number = phone_number
            user.save()

            #User Activation
            current_site = get_current_site(request)
            mail_subject = 'Activate your account.'
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = form.cleaned_data.get('email')

            email = EmailMessage(
                subject=mail_subject,
                body=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[to_email]
            )
            email.send()
            messages.success(request, 'Thank you for registering with us. We have sent you a verification email to your email address. Please verify to activate your account.')
            redirect_url = reverse('login') + '?command=verification&email=' + form.cleaned_data.get('email')
            return redirect(redirect_url)
    context = {
        'form': form,
    }
    
    return render(request, 'accounts/register.html', context)

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your account has been activated successfully. You can now log in.')
        return redirect('login')
    else:
        messages.error(request, 'Activation link is invalid!')
        return redirect('register')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = auth.authenticate(request, email=email, password=password)
        if user is not None:
            auth.login(request, user)
            messages.success(request, 'You have successfully logged in.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid email or password.')
            return redirect('login')
    return render(request, 'accounts/login.html')

@login_required (login_url='login')
def logout_view(request):
    auth.logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')


@login_required (login_url='login')
def dashboard(request):
    return render(request, 'accounts/dashboard.html')


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            # Reset Password Email
            current_site = get_current_site(request)
            mail_subject = 'Reset Your Password'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            email = EmailMessage(
                subject=mail_subject,
                body=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[to_email]
            )
            email.send()

            messages.success(request, 'Password reset email has been sent to your email address.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist')
            return redirect('forgot_password')
    return render(request, 'accounts/forgot-password.html')

def reset_password_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.info(request, 'Please enter your new password.')
        return redirect('reset_password')
    else:
        messages.error(request, 'The reset password link is invalid.')
        return redirect('forgot_password')



def reset_password(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):  
        if request.method == 'POST':
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            if password == confirm_password:
                user.set_password(password)
                user.save()
                messages.success(request, 'Password reset successful. You can now log in with your new password.')
                return redirect('login')
            else:
                messages.error(request, 'Passwords do not match.')
                return redirect(request.path)
        else:
            return render(request, 'accounts/reset-password.html')
    else:
        messages.error(request, 'The reset password link is invalid.')
        return redirect('forgot_password')



def reset_password(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):  
        if request.method == 'POST':
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            if password == confirm_password:
                user.set_password(password)
                user.save()
                messages.success(request, 'Password reset successful. You can now log in with your new password.')
                return redirect('login')
            else:
                messages.error(request, 'Passwords do not match.')
                return redirect(request.path)
        else:
            context = {
                'uidb64': uidb64,
                'token': token,
            }
            return render(request, 'accounts/reset-password.html', context)
    else:
        messages.error(request, 'The reset password link is invalid.')
        return redirect('forgot_password')
    
   
    
    