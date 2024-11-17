from django.db import models
from django.contrib.auth.models import User
from cryptography.fernet import Fernet
from django.core.files.base import ContentFile
from django.utils.timezone import now
import datetime

#function to generate an encryption key
def generate_encryption_key():
    return Fernet.generate_key().decode()

def encrypt_file_content(file_content: bytes, key: str) -> bytes:
    fernet = Fernet(key.encode())
    return fernet.encrypt(file_content)

def decrypt_file_content(encrypted_content: bytes, key: str) -> bytes:
    fernet = Fernet(key.encode())
    return fernet.decrypt(encrypted_content)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    encrypted_key = models.CharField(max_length=100, default=generate_encryption_key)
    target_date = models.DateField() #date when the user can access their file
    home_address = models.CharField(max_length=225)
    receipt_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.created_at is None:
            self.created_at = now()
        #ensure target date is at least 10 years from account creating 
        if self.target_date < self.created_at.date() + datetime.timedelta(days=365*10):
            raise ValueError("Target date must be at least 10 years from the account creation date")
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.user.username

class SecureFolder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.title

class SecureData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    folder = models.ForeignKey(SecureFolder, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='secure_files/')
    created_at = models.DateTimeField(auto_now_add=True)

    def save_encrypted_file(self, file, key):
        encrypted_content = encrypt_file_content(file.read(), key)
        encrypted_file = ContentFile(encrypted_content)
        self.file.save(file.name, encrypted_file)

    def get_decrypted_file(self, key):
        with self.file.open('rb') as f:
            encrypted_content = f.read()
            return decrypt_file_content(encrypted_content, key)

    def __str__(self):
        return self.title

class AccessLog(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    attempted_access_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Access attempt by {self.user_profile.user.username} on {self.attempted_access_date}"