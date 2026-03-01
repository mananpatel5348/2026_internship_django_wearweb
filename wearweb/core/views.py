from django.shortcuts import render,redirect
from django.http import HttpResponse
from .forms import usersignupform, userloginform
from django.contrib.auth import authenticate, login
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from email.mime.image import MIMEImage
import os


# Create your views here.
def usersignupview(request):

    if request.method == 'POST':
        form = usersignupform(request.POST or None)

        if form.is_valid():

            # -------- GET EMAIL --------
            email = form.cleaned_data['email']

            # -------- PREMIUM EMAIL --------
            subject = "Welcome to WearWeb "
            from_email = settings.EMAIL_HOST_USER
            to = [email]

            html_content = """
            <div style="background-color:#0f0f0f; padding:40px 0; font-family:Arial, sans-serif;">
                <div style="max-width:600px; margin:auto; background:#1a1a1a; padding:30px; border-radius:12px; text-align:center;">

                    <h3 style="color:#c5a047; letter-spacing:3px; margin-bottom:5px;">
                        “Step Into Style with WearWeb”
                    </h3>

                    <h1 style="color:#d4af37; font-size:40px; margin:10px 0;">
                        WEARWEB
                    </h1>

                    <p style="color:#cccccc; font-size:16px; margin-bottom:25px;">
                        Your Premium Fashion Destination
                    </p>

                    <img src="cid:poster_image" width="100%" style="border-radius:10px; margin-bottom:25px;">

                    <p style="color:#bbbbbb; font-size:15px; line-height:1.6;">
                        Welcome to the world of luxury fashion.<br>
                        We are excited to have you on board.
                    </p>

                    <a href="http://127.0.0.1:8000/"
                       style="display:inline-block; margin-top:25px; padding:12px 30px;
                              background:#d4af37; color:black; text-decoration:none;
                              border-radius:30px; font-weight:bold;">
                       Explore Now
                    </a>

                </div>
            </div>
            """

            email_message = EmailMultiAlternatives(subject, "", from_email, to)
            email_message.attach_alternative(html_content, "text/html")

            poster_path = os.path.join(settings.BASE_DIR, 'static/images/welcome_poster.png')

            with open(poster_path, 'rb') as f:
                img = MIMEImage(f.read())
                img.add_header('Content-ID', '<poster_image>')
                img.add_header('Content-Disposition', 'inline', filename="welcome_poster.png")
                email_message.attach(img)

            email_message.send()

            # -------- SAVE USER --------
            form.save()

            return redirect('login')

    else:
        form = usersignupform()

    return render(request, 'core/signup.html', {'form': form})




def userloginview(request):
    if request.method == "POST":
        form = userloginform(request.POST or None)
        if form.is_valid():
            print(form.cleaned_data)
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user:
                login(request, user)
                if user.role == "customer":
                    return redirect("customer_dashboard")
                if user.role == "seller":
                    return redirect("seller_dashboard")
                if user.role == "admin":
                    return redirect("admin_dashboard")
            else:
                return render(request, 'core/login.html', {'form': form,})
        
    else:
        form = userloginform()
        return render(request, 'core/login.html',{'form': form})   
