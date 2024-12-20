from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from .models import SecureData, UserProfile
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
import logging
import datetime


def home_view(request):
    return render(request, 'eternalvault_app/home.html')

logger = logging.getLogger(__name__)

@login_required
def download_file_view(reques, secure_data_id):
    #get the secure data object
    secure_data = get_object_or_404(SecureData, id=secure_data_id, user=request.user)

    #get the associated user profile to retrieve the encrypted key
    try:
        user_profile = request.user.userprofile
    except:
        logger.error(f"UserProfile not found for user: {request.user}")
        raise Http404("UserProfile not found")
    
    #chek if the file can be accessed based on target_date
    if now().date() < user_profile.target_date:
        logger.warning(f"access attempt before target date for file: {secure_data.title} by user: {request.user}")
        raise Http404("this file can not be accessed before the target date")

    #decryopt the file using the user's encryption key
    try:
        decrypt_content = secure_data.get_decrypted_file(user_profile.encrypted_key)
    except:
        logger.error(f"error decrypting file: {secure_data.title} for user: {request.user}, error: {e}")
        raise Http404("error decrypting file")
    
    #create a response with the decrypted content
    response = HttpResponse(decrypted_content, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{secure_data.title}"'
    return response


@login_required
def upload_file_view(request):
    if request.method == 'POST':
        uploaded_file = request.FILES['file']

        #ensure the user has a UserProfile
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)

        logger.info(f"user: {request.user}, type: {type(request.user)}")

        #create secureData instance and save encrypted file
        secure_data = SecureData(user=request.user, title=uploaded_file.name)
        secure_data.save_encrypted_file(uploaded_file, user_profile.encrypted_key)
        secure_data.save()

        messages.success(request, "File uplaoded successfully")
        return redirect('home') #redirect after successful upload
    
    return render(request, 'eternalvault_app/upload_file.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        target_date = request.POST.get('target_date')
        home_address = request.POST['home_address']
        receipt_name = request.POST['receipt_name']
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(username=username, password=password)
            user.save()

            if not target_date:
                target_date = now().date() + datetime.timedelta(days=365*10)
            else:
                target_date = datetime.datetime.strptime(target_date, '%Y-%m-%d').date()
                if target_date < now().date() + datetime.timedelta(days=365*10):
                    messages.error(request, "Target date must be at least 10 years from now")
                    return redirect('register')

            #create a UserProfile for the new user
            UserProfile.objects.create(
                user=user,
                target_date = target_date,
                home_address = home_address,
                receipt_name = receipt_name,
            )

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