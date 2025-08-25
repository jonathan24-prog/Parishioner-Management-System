from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import SignUpForm, LoginForm


def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        accept_privacy = request.POST.get('accept_privacy')

        if not accept_privacy:
            form.add_error(None, "You must accept the Privacy Policy to register.")

        if form.is_valid() and accept_privacy:
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = SignUpForm()

    return render(request, 'faithlink/signup.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = LoginForm()
    return render(request, 'faithlink/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


# from rest_framework.generics import ListAPIView
# from .models import CustomUser

# from rest_framework import viewsets
# from rest_framework.decorators import api_view,authentication_classes,permission_classes
# from rest_framework.response import Response
# from rest_framework.authentication import SessionAuthentication, BasicAuthentication
# from rest_framework.permissions import IsAuthenticated
# from rest_framework import viewsets
# from rest_framework import filters

