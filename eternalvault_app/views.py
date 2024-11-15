from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from .models import SecureData, UserProfile
from django.contrib.auth.decorators import login_required


def home_view(request):
    return render(request, 'eternalvault_app/home.html')

@login_required
def upload_file_view(request):
    if request.method == 'POST':
        uploaded_file = request.FILES['file']
        user_profile = UserProfile.objects.get(user=request.user)

        #create secureData instance and save encrypted file
        secure_data = SecureData(user=request.user, title=uploaded_file.name)
        secure_data.save_encrypted_file(uploaded_file, user_profile.encrypted_key)
        secure_data.save()

        return redirect('home') #redirect after successful upload
    
    return render(request, 'eternalvault_app/upload_file.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(username=username, password=password)
            user.save()
            messages.success(request, "Account Created")
            return redirect('login')
        else:
            messages.error(request, "Username already exists")
    
    return render(request, 'eternalvault_app/register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('upload_file')
        else:
            messages.error(request, "Invalid username or password")
    
    return render(request, 'eternalvault_app/login.html')