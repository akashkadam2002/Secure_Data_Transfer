from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import EncodeImageForm, RegistrationForm, LoginForm
from .models import steganography, UserRegistration
from django.conf import settings

# from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.http import Http404 

# Required libraries for image processing
import os
from PIL import Image
import numpy as np
from django.core.files import File
import logging
from django.contrib.auth import logout


# ----------Authentication and authorization views---------------
# register view
def registerUser(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            profile_picture = form.cleaned_data.get('profile_picture')
            email = form.cleaned_data.get('email')
            user_registration = UserRegistration(user=user, profile_picture=profile_picture, email=email)
            user_registration.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegistrationForm()
    return render(request, 'base/SignUp.html', {'form': form})


# login view
def loginUser(request):
    error_message = None
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('landing')
            else:
                error_message = "Invalid username or password."

    else:
        form = LoginForm()

    return render(request, 'base/SignIn.html', {'form': form, 'error_message': error_message})

# logout view
def logout_view(request):
    try:
        logout(request)
    except Exception as e:
        return Http404('Page not found', e)

    return render(request, 'base/home.html')

# Landing Page view
def home(request):
    return render(request, 'base/home.html')


def about(request):
    return render(request, 'base/about.html')


# ----------Image Steganography--------------------
# Rail Fence Enc
def encrypt_rail_fence(text, key):
    rail = [['\n' for _ in range(len(text))] for _ in range(key)]
    dir_down = False
    row, col = 0, 0

    for char in text:
        if row == 0 or row == key - 1:
            dir_down = not dir_down
        rail[row][col] = char
        col += 1
        row = row + 1 if dir_down else row - 1

    result = ''.join(char for row in rail for char in row if char != '\n')
    return result


# Encoding Image
logger = logging.getLogger('base')

def encode_image(request):
    media_root = settings.MEDIA_ROOT
    success_message = ""
    error_message = ""

    if request.method == 'POST':
        form = EncodeImageForm(request.POST, request.FILES)
        if form.is_valid():
            # Get the form data
            image = request.FILES['image']
            message = form.cleaned_data['message']
            password = form.cleaned_data['password']
            dest = form.cleaned_data['dest']
            receiver = form.cleaned_data['receiver']
            sender = request.user

            # --ASCII Encryption - Level 1
            encmsg = "".join(chr(ord(ch) + 3) for ch in message)
            
            # Rail Fence encryption - Level 2
            encrypted = encrypt_rail_fence(encmsg, 3)

            # Prepare paths
            image_path = os.path.join(media_root, 'originalImages', image.name)
            encoded_image_path = os.path.join(media_root, 'stegoImages', dest)

            try:
                # Attempt to open the image
                img = Image.open(image_path)
                width, height = img.size
                array = np.array(list(img.getdata()))

                n = 3 if img.mode == 'RGB' else 4
                total_pixels = array.size // n

                # Append password to encrypted message
                encrypted += password
                b_message = ''.join(format(ord(i), "08b") for i in encrypted)
                req_pixels = len(b_message)

                if req_pixels > (total_pixels * 3):
                    error_message = 'ERROR: Need larger file size'
                    raise Exception(error_message)

                index = 0
                for p in range(total_pixels):
                    for q in range(n):
                        if index < req_pixels:
                            array[p][q] = int(bin(array[p][q])[2:9] + b_message[index], 2)
                            index += 1

                array = array.reshape(height, width, n)
                enc_img = Image.fromarray(array.astype('uint8'), img.mode)
                enc_img.save(encoded_image_path)

                # Only save the instance if encoding was successful
                encoded_image = steganography(image=image, message=encrypted, dest=dest, receiver=receiver, sender=sender)
                encoded_image.save()

                # Reset form after successful encoding
                form = EncodeImageForm()
                success_message = "Image encoding was successful."
                
            except Exception as e:
                error_message = str(e)

    else:
        form = EncodeImageForm()

    return render(request, 'base/encodeImg.html', {
        'form': form,
        'success_message': success_message,
        'error_message': error_message
    })


# success view
def success(request):
    return render(request, 'base/success.html')

# try - login_register
def login_register(request):
    return render(request, 'base/login_register.html')

def userLanding(request):
    user = request.user
    sent_records = steganography.objects.filter(sender=user).order_by('-created')
    records_found_s = any(request.user == record.sender for record in sent_records)

    receiver_records = steganography.objects.filter(receiver=user).order_by('-created')
    records_found_r = any(request.user == record.receiver for record in receiver_records)
    
    for record in sent_records:
        record.image_name = record.image.url.split("/")[-1] 

    for record in receiver_records:
        record.image_name = record.image.url.split("/")[-1]
    return render(request, 'base/userLanding.html', {'sent_records': sent_records, 'receiver_records': receiver_records, 'records_found_r': records_found_r, 'records_found_s': records_found_s })

