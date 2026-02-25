from django.shortcuts import render,redirect
from django.http import HttpResponse
from .forms import usersignupform, userloginform
from django.contrib.auth import authenticate, login


# Create your views here.
def usersignupview(request):
    if request.method == 'POST':
        form = usersignupform(request.POST or None)
        if form.is_valid():
            form.save()
            return redirect('login')
        else:
            return render(request, 'core/signup.html', {'form': form})
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
