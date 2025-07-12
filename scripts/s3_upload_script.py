import os
from PIL import Image
import boto3
from botocore.exceptions import ClientError

# ---------- CONFIG ----------
INPUT_DIR = "./s3_images"
CROP_SIZE = (300, 300)  # width, height
BUCKET_NAME = "zeamigo-main"
S3_FOLDER = "image_assets/"
AWS_REGION = "ap-south-1"  # change if needed
TEMP_PATH = "/tmp"
# ----------------------------

# Initialize S3 client
s3 = boto3.client("s3", region_name=AWS_REGION)

def crop_center(input_path, size):
    with Image.open(input_path) as image:
        w, h = image.size
        new_w, new_h = size
        left = (w - new_w) / 2
        top = (h - new_h) / 2
        right = (w + new_w) / 2
        bottom = (h + new_h) / 2
        return image.crop((left, top, right, bottom))

def upload_to_s3(file_path, s3_key):
    try:
        s3.upload_file(file_path, BUCKET_NAME, s3_key)
        print(f"Uploaded: {s3_key}")
    except ClientError as e:
        print(f"Failed to upload {s3_key}: {e}")
        return False
    return True

def verify_s3_upload(s3_key):
    try:
        s3.head_object(Bucket=BUCKET_NAME, Key=s3_key)
        return True
    except ClientError:
        return False

def process_image(file_path,s3_key):

    uploaded = upload_to_s3(file_path, s3_key)
    if uploaded and verify_s3_upload(s3_key):
        print(f"✅ Verified upload: {s3_key}")
    else:
        print(f"❌ Upload verification failed: {s3_key}")

if __name__ == "__main__":
    hotel_path = os.path.join(INPUT_DIR,"hotels")
    for hotel_image in os.listdir(hotel_path):
        resized_image = crop_center(os.path.join(hotel_path,hotel_image),CROP_SIZE)
        new_path=os.path.join(TEMP_PATH,hotel_image)
        resized_image.save(new_path)
        s3_key = os.path.join("hotels",hotel_image)
        process_image(new_path,s3_key)
    for city_image in os.listdir(os.path.join(INPUT_DIR,"cities")):
        full_path = os.path.join(INPUT_DIR,"cities",city_image)
        s3_key = os.path.join("cities",city_image)
        process_image(full_path,s3_key)

