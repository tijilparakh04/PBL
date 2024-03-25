from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import SignUpForm
from django.http import HttpRequest, HttpResponse
from .backend import process_ppt
import os

def upload_ppt(request):
    if request.method == 'POST':
        ppt_file = request.FILES.get('ppt_file')
        if ppt_file:
            try:
                # Save the uploaded file to a temporary location
                with open('temp.pptx', 'wb') as f:
                    for chunk in ppt_file.chunks():
                        f.write(chunk)
                
                enhanced_ppt_path = process_ppt('temp.pptx')
                # Delete the temporary file
                os.remove('temp.pptx')
                # Provide the enhanced PowerPoint file for download or display
                with open(enhanced_ppt_path, 'rb') as f:
                    response = HttpResponse(f.read(), content_type='application/vnd.openxmlformats-officedocument.presentationml.presentation')
                    response['Content-Disposition'] = 'attachment; filename=enhanced_presentation.pptx'
                    return response
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
