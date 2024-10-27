from django.shortcuts import render, redirect
from django.http import HttpResponse
from . forms import createUserForm

# Create your views here.


def register(request):

    form = createUserForm()

    if request.method == 'POST':
        form = createUserForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('login')

    context = {'registerForm':form}

    return render(request, 'register.html', context)



