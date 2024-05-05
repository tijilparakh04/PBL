import base64
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import SignUpForm
from django.http import HttpRequest, HttpResponse
from .backend import process_ppt
from django.conf import settings
import os
from bson import ObjectId  
from django.template.response import TemplateResponse
import pymongo
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.core.mail import EmailMessage, send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from . tokens import generate_token
from pymongo import MongoClient
from django.contrib.auth.hashers import make_password

client = pymongo.MongoClient(settings.MONGODB_URI)
db = client[settings.MONGODB_NAME]
collection = db['enhanced_ppt']

def upload_ppt(request):
    if request.method == 'POST':
        ppt_file = request.FILES.get('ppt_file')
        if ppt_file:
            try:
                # Save the uploaded file to a temporary location
                with open('temp.pptx', 'wb') as f:
                    for chunk in ppt_file.chunks():
                        f.write(chunk)
                
                # Process the uploaded PowerPoint file
                enhanced_ppt_path = process_ppt('temp.pptx')
                
                # Save the enhanced PowerPoint presentation to MongoDB
                with open(enhanced_ppt_path, 'rb') as f:
                    enhanced_ppt_data = f.read()
                    ppt_doc = {'name': 'enhanced_presentation.pptx', 'data': enhanced_ppt_data}
                    collection.insert_one(ppt_doc)

                # Delete the temporary file
                os.remove('temp.pptx')
                
                ppt_id_str = str(ppt_doc['_id'])  # Convert ObjectId to string

                return redirect('preview_ppt', ppt_id=ppt_id_str)
            except Exception as e:
                return HttpResponse(f"An error occurred: {str(e)}", status=500)
    return render(request, 'page.html')

def entry(request: HttpRequest):
    return render(request, 'entry.html')

client = MongoClient(settings.MONGODB_URI)
db = client[settings.MONGODB_NAME]
user_collection = db['users']

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('signup')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('signup')

        
        user_data = {
            'username': username,
            'email': email,
            'password': password,
        }
        try:
            user_collection.insert_one(user_data)
            messages.success(request, 'Account created successfully. You can now login.')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Failed to create account: {str(e)}')
            return redirect('signup')

    return render(request, 'signup.html')

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check if user exists in MongoDB
        user_data = user_collection.find_one({'username': username, 'password': password})
        if user_data:
            # # Authenticate user in Django
            # user = authenticate(request, username=username, password=password)
            # if user is not None:
                # login(request, user)
                messages.success(request, 'You are now logged in.')
                print("hello")
                return redirect('upload_ppt')  # Replace 'home' with your desired redirect URL after login

        messages.error(request, 'Invalid username or password.')
        return redirect('login')

    return render(request, 'login.html')
