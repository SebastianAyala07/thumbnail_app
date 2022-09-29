import boto3
import json
from datetime import datetime
from io import BytesIO
from PIL import Image, ImageOps
import uuid
import os

s3 = boto3.client("s3")
size = int(os.environ["THUMBNAIL_SIZE"])


def s3_thumbnail_generator(event, context):
    s3_record = event["Records"][0]["s3"]
    bucket = s3_record["bucket"]["name"]
    key = s3_record["object"]["key"]
    img_size = s3_record["object"]["size"]

    if not key.endsWith("_thumbnail.png"):
        image = get_s3_image(bucket, key)
        thumbnail = image_to_thumbnail(image)

        thumbnail_key = new_filename(key)
        url = upload_to_s3(bucket, thumbnail_key, thumbnail, img_size)
        return None

    body = {
        "message": "Go Serverless v3.0! Your function executed successfully!",
        "input": event,
    }

    return {"statusCode": 200, "body": json.dumps(body)}


def get_s3_image(bucket, key):
    response = s3.get_object(Bucket=bucket, Key=key)
    image_content = response["Body"].read()

    img_file = BytesIO(image_content)
    img = Image.open(img_file)
    return img

def image_to_thumbnail(image):
    return ImageOps.fit(image, (size, size), Image.ANTIALIAS)

def new_filename(key):
    key_split = key.rsplit('.', 1)
    return key_split[0] + "_thumbnail.png"

def upload_to_s3(bucket, key, image, img_size):
    out_thumbnail = BytesIO()

    image.save(out_thumbnail, "PNG")
    out_thumbnail.seek(0)

    s3.put_object(
        ACL="public-read",
        Body=out_thumbnail,
        Bucket=bucket,
        ContentType="image/png",
        Key=key
    )

    url = "{}/{}/{}".format(s3.meta.endpoint_url, bucket, key)

    return url