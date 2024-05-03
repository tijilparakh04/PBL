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
from django.http import FileResponse


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
                
                # Redirect to the preview page with the MongoDB document ID
                return redirect('preview_ppt', ppt_id=str(ppt_doc['_id']))
            except Exception as e:
                return HttpResponse(f"An error occurred: {str(e)}", status=500)
    return render(request, 'page.html')

def entry(request: HttpRequest):
    return render(request, 'entry.html')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Account created successfully.')
                return redirect('entry')  # Redirect to entry page after sign-up
            else:
                messages.error(request, 'Error creating account. Please try again.')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('userid')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful.')
            return redirect('entry')  # Redirect to the entry page after successful login
        else:
            messages.error(request, 'Invalid credentials. Please try again.')
    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    messages.info(request, 'Logged out successfully.')
    return redirect('login')  # Redirect to login page after logout


def preview_ppt(request, ppt_id):
    try:
        # Find the MongoDB document by ID
        ppt_doc = collection.find_one({'_id': ObjectId(ppt_id)})
        if ppt_doc:
            ppt_data = ppt_doc['data']
            return FileResponse(ppt_data, content_type='application/vnd.openxmlformats-officedocument.presentationml.presentation')
        else:
            return HttpResponse("Presentation not found.", status=404)
    except Exception as e:
        return HttpResponse(f"An error occurred: {str(e)}", status=500)
