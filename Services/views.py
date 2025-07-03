import os
import io
import json
import base64
from PIL import Image
from .models import WasteReport
from config.models import APIKey
from django.conf import settings
import google.generativeai as genai
from Accounts.models import Profile
from django.contrib import auth,messages
from Accounts.models import RewardTransaction
from django.shortcuts import render, redirect
from google.generativeai import GenerativeModel
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.storage import FileSystemStorage

GEMINI_KEY = APIKey.objects.get(name="GEMINI_API").key
# genai.configure(api_key=GEMINI_KEY)
# model = genai.GenerativeModel("gemini-1.5-turbo")

PROMPT = """
You are an expert in waste management and recycling. Analyze this image and provide:
1. The type of waste (e.g., plastic, paper, glass, metal, organic)
2. An estimate of the quantity or amount (in kg or liters)

Respond in plain text. Do NOT use any JSON, markdown, or formatting like triple backticks.
Just answer in a simple sentence like:
"Waste Type: Plastic 
Quantity: 2 kg "for the Quantity note dont include other thing like approxialty give the quantity in this format only" " 
"""
filename = None
def report(request):
    global GEMINI_KEY
    global filename
    if request.method == "POST" and "image" in request.FILES:
        image_file = request.FILES["image"]

        # Convert RGBA to RGB if needed
        image = Image.open(image_file)
        if image.mode == "RGBA":
            image = image.convert("RGB")

        # Convert image to bytes
        image_io = io.BytesIO()
        image.save(image_io, format="JPEG")
        image_bytes = image_io.getvalue()   
    # Define custom storage location (media/proof_image)
        fs = FileSystemStorage(location="media/proof_images", base_url="/media/proof_images/")

        # Generate a unique filename (optional)
        filename = fs.save(image_file.name, image_io)

        try:
            genai.configure(api_key=GEMINI_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")  
            response = model.generate_content([
                PROMPT,
                {
                    "mime_type": "image/jpeg",
                    "data": image_bytes
                }
            ])
            
            generated_text = response.text.strip()
            print("Generated Text:", generated_text)
            lines = generated_text.splitlines()
 
            for line in lines:
                if "Waste Type:" in line:
                    waste_type = line.split("Waste Type:")[1].strip()
                elif "Quantity:" in line:
                    quantity = line.split("Quantity:")[1].strip()

        except Exception as e:
            print("Gemini Error:", e)
            waste_type = "Unknown"
            quantity = "N/A"
 
        return render(request, "report.html", {
            "wasteType": waste_type,
            "quantity": quantity,
        })

    
    else:
        import re
        estimate_amt = request.POST.get("estimate_amt", "")
        location = request.POST.get("location")
        waste_type = request.POST.get("waste_type")
        # Ensure that waste_type is provided
        if not waste_type:
            # Handle the case where waste_type is missing (e.g., show an error message)
            return render(request, "report.html", {
                "error": "Waste type is required."
            })
        from decimal import Decimal
        # Process estimate_amt (if provided)
        if estimate_amt:
            estimate_amt = re.sub(r'[^0-9.]', '', estimate_amt)
            estimate_amt = Decimal(estimate_amt)
        else:
            estimate_amt = Decimal('0.00')  # Default value if estimate_amt is missing
        try:
            relative_file_path = f"proof_images/{filename}"
            WasteReport.objects.create(
                user=request.user,
                waste_type=waste_type,
                estimate_amt=estimate_amt,
                location=location,
                proof_image=relative_file_path  # ✅ correct
            )
            messages.success(request, "Report submitted successfully!")
            return redirect("dashboard")
        
        except Exception as e:
            return render(request, "report.html", {
                "error": f"Error saving the report: {str(e)}"
            })
    return render(request, "report.html")

from django.shortcuts import render
from .models import WasteReport

def collect(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            # Retrieve all WasteReports if the user is a superuser
            waste_reports = WasteReport.objects.all()
        else:
            # Retrieve WasteReports for the logged-in user if they are not a superuser
            waste_reports = WasteReport.objects.filter(user=request.user)
    else:
        # If the user is not authenticated, you can either redirect them or show an error
        waste_reports = []

    return render(request, "collect.html", {
        "waste_reports": waste_reports
    })

from django.shortcuts import render, redirect, get_object_or_404
from .models import WasteReport
from django.contrib.auth.decorators import login_required

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from PIL import Image, ImageChops
import os
from django.conf import settings
from PIL import Image
from skimage.metrics import structural_similarity as ssim
import numpy as np

def are_images_equal(img1_path, img2_path, threshold=0.95):
    img1 = Image.open(img1_path).convert('L')  # convert to grayscale
    img2 = Image.open(img2_path).convert('L')

    # Resize to the same size if they are different
    if img1.size != img2.size:
        img2 = img2.resize(img1.size)

    img1_np = np.array(img1)
    img2_np = np.array(img2)

    score, _ = ssim(img1_np, img2_np, full=True)
    return score >= threshold  # Threshold 0.95 means 95% similarity

from django.shortcuts import render, get_object_or_404, redirect
from .models import WasteReport
import os
from django.conf import settings
from PIL import Image
 # Assuming this is a custom function

def mark_collected(request, report_id):
    report = get_object_or_404(WasteReport, id=report_id)
    
    if request.method == 'POST':
        if 'proof' in request.FILES:
            uploaded_image = request.FILES['proof']
            uploaded_image_path = os.path.join(settings.MEDIA_ROOT, 'temp', uploaded_image.name)

            # Save the uploaded image temporarily
            with open(uploaded_image_path, 'wb') as f:
                for chunk in uploaded_image.chunks():
                    f.write(chunk)

            # Get the proof image stored in the database
            proof_image_path = os.path.join(settings.MEDIA_ROOT, report.proof_image.name)
            print(proof_image_path,uploaded_image_path)
            from decimal import Decimal
            from Accounts.models import RewardTransaction
            if are_images_equal(uploaded_image_path, proof_image_path):
                report.collected = True

                # ✅ Reward logic
                reward_amount = report.estimate_amt * Decimal('0.5')
                report.reward_given = reward_amount
                report.save()
                ## Step 3: Update user's profile
                profile = report.user.profile
                profile.reward += reward_amount
                profile.save()

                # Record the reward transaction
                RewardTransaction.objects.create(
                    user=report.user,
                    amount=reward_amount,
                    transaction_type='add',
                    reason=f"Reward for collecting {report.waste_type} waste"
                )
                messages.success(request, f"Waste marked as collected. {reward_amount} reward points added.")
            else:
                messages.warning(request, "Uploaded image does not match the proof image.")

            os.remove(uploaded_image_path)
        else:
            messages.error(request,"No proof image uploaded.")

        return redirect('collect')  # Redirect to your collection page or show the message

    return redirect('collect')  # Redirect if GET request or no form submission


def rewards(request):
    transactions = RewardTransaction.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'rewards.html', {'transactions': transactions})


def leaderboard(request):
    leaderboard = Profile.objects.filter(user__is_superuser=False).order_by('-reward')
    return render(request, 'leaderboard.html', {'leaderboard': leaderboard})