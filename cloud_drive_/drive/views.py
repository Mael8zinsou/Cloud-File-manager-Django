'''User Authentification Views'''

# drive/views.py
from .forms import SignUpForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # redirection vers la page d'accueil
        else:
            messages.error(request, "Invalid credentials.")
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def signup_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            try:
                user = User.objects.create_user(username=username, password=password1)
                user.save()
                login(request, user)
                return redirect('home')
            except:
                messages.error(request, "Username already exists.")
        else:
            messages.error(request, "Passwords do not match.")
    
    return render(request, 'accounts/signup.html')

@login_required
def home_view(request):
    return render(request, 'home.html')
