from django.core.files.base import ContentFile

# Import your function

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from django.core.files.base import ContentFile
import base64

def generate_aadhaar_card_image(data, profile_image_b64=None):
    """
    Generate Aadhaar card-like image with dummy data.
    """

    # Card size
    img = Image.new("RGB", (800, 500), color="white")
    draw = ImageDraw.Draw(img)

    # Fonts
    try:
        font = ImageFont.truetype("arial.ttf", 20)
        bold_font = ImageFont.truetype("arialbd.ttf", 28)
    except:
        font = ImageFont.load_default()
        bold_font = ImageFont.load_default()

    # Top Tricolor Strip
    draw.rectangle([0, 0, 800, 40], fill=(255, 153, 51))  # Orange
    draw.rectangle([0, 40, 800, 80], fill=(255, 255, 255))  # White
    draw.rectangle([0, 80, 800, 120], fill=(19, 136, 8))   # Green

    draw.text((250, 45), "Government of India", fill="black", font=bold_font)

    # Aadhaar Number
    draw.text((280, 130), f"{data.get('masked_aadhaar')}", fill="black", font=bold_font)

    # Insert Profile Photo (if given)
    if profile_image_b64:
        try:
            profile_data = base64.b64decode(profile_image_b64)
            profile_img = Image.open(BytesIO(profile_data)).resize((150, 180))
            img.paste(profile_img, (50, 180))
        except Exception as e:
            print("Profile photo error:", e)

    # Personal Details
    x_offset = 250
    y_offset = 180
    line_gap = 40

    draw.text((x_offset, y_offset), f"Name: {data.get('name')}", fill="black", font=font)
    draw.text((x_offset, y_offset + line_gap), f"Father's Name: {data.get('father_name')}", fill="black", font=font)
    draw.text((x_offset, y_offset + 2*line_gap), f"DOB: {data.get('dob')}", fill="black", font=font)
    draw.text((x_offset, y_offset + 3*line_gap), f"Gender: {data.get('gender')}", fill="black", font=font)
    draw.text((x_offset, y_offset + 4*line_gap), f"Address: {data.get('full_address')}", fill="black", font=font)
    draw.text((x_offset, y_offset + 5*line_gap), f"Pincode: {data.get('zip_code')}", fill="black", font=font)

    # Fake QR Box (right side bottom)
  
    # Footer
    draw.text((250, 460), "Demo - Aadhaar ", fill="red", font=bold_font)

    # Save to buffer
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return ContentFile(buffer.getvalue(), "aadhaar_card.png")



# Dummy Aadhaar data
dummy_data = {
    "name": "Sid Malhotra",
    "gender": "Female",
    "dob": "2000-05-28",
    "yob": "2000",
    "zip_code": "400001",
    "masked_aadhaar": "3425 0653 1151",
    "full_address": "123 MG Road, Andheri East, Mumbai, Maharashtra",
    "father_name": "Rajesh Malhotra",
}

# Call function (without real Aadhaar profile image, so just leave profile_image_b64=None)
aadhaar_img_file = generate_aadhaar_card_image(dummy_data)

# Save to disk (to verify output manually)
with open("test_aadhaar.png", "wb") as f:
    f.write(aadhaar_img_file.read())

print("✅ Aadhaar test image generated: test_aadhaar.png")
