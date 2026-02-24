from django.shortcuts import render, redirect
from .forms import usersignupform


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
