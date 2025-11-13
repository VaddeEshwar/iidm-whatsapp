from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.contrib.auth import authenticate, login, logout


def user_login(request):
    if request.method == 'POST':
        print("POST token:", request.POST.get('csrfmiddlewaretoken'))
        print("Cookie token:", request.COOKIES.get('csrftoken'))
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        print(f'username:{username} and pass:{password} to login...')
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # Redirect to a success page
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')


def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')  # Redirect to your login page