# user/views.py
from django.shortcuts import render, redirect
from .forms import createUserForm
from django.contrib.auth.decorators import login_required

# user/views.py
def welcome(request):
    return render(request, 'welcome.html')

def register(request):
    form = createUserForm()

    if request.method == 'POST':
        form = createUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')

    context = {'registerForm': form}
    return render(request, 'registration/register.html', context)  # Update path here

@login_required
def profile(request):
    return render(request, 'profile.html')