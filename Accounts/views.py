import os
import csv
from django.core.files import File
from django.conf import settings
from django.contrib import auth,messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login

def user_login(request):
    if request.method == "POST":
        form_type = request.POST.get("form_type")  # Check which form was submitted

        if form_type == "login":
            # Handle login form submission
            username = request.POST.get("username")
            password = request.POST.get("password")
            if username and password:
                user = authenticate(username=username, password=password)
                if user is not None:
                    if user.is_superuser:
                        messages.warning(request, "Please Login Using Teacher Login!!")
                        return redirect("/auth/suser_login")
                    else:
                        auth_login(request, user)
                        messages.success(request, "Login successful")
                        return redirect('report')
                else:
                    messages.error(request, "User Doesn't Exist")
                    
            return render(request, "user_login.html", {"username": username})

        elif form_type == "signup":
            username = request.POST.get("username")
            password = request.POST.get("password")
            email = request.POST.get("email")
            try:
                user = User.objects.create_user(username = username , password = password)
                user.save()
                auth.login(request ,user)

            except:
                messages.error(request,"Username Already exists")
                return render(request,"user_login.html",{"username":username,"email":email}) 
                
            messages.success(request,"Success")
    return render(request, "user_login.html")

def suser_login(request):
    if request.method == "POST":
        form_type = request.POST.get("form_type")  # Check which form was submitted

        if form_type == "login":
            username = request.POST.get("username")
            password = request.POST.get("password")
            if username and password:
                user = authenticate(username=username, password=password)
                if user is not None:
                    if user.is_superuser:
                        # Handle superuser login
                        auth_login(request, user)
                        messages.success(request, "Superuser login successful")
                        return redirect('collect')  # Redirect to superuser dashboard or another page
                    else:
                        messages.warning(request, "Please Login Using Student Login!!")
                        return redirect('/auth/user_login')
                else:
                    messages.error(request, "Invalid credentials")
                    return render(request, "suser_login.html", {"username": username})

        elif form_type == "signup":
            # Handle signup form submission
            username = request.POST.get("username")
            password = request.POST.get("password")
            email = request.POST.get("email")
            try:
                user = User.objects.create_superuser(username = username , password = password,email = email)
                user.save()
                auth.login(request ,user)

            except:
                messages.error(request,"Username Already exists")
                return render(request,"suser_login.html",{"username":username,"email":email}) 
        messages.success(request,"Success")
    return render(request, "suser_login.html")

def logout(request):
    auth.logout(request)
    messages.success(request, "Logout successful")
    return redirect("user_login")

def profile(request):   
    return render(request, "profile.html") 