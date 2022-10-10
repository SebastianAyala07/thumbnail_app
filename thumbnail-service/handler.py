import boto3
import json
from datetime import datetime
from io import BytesIO
from PIL import Image, ImageOps
import uuid
import os
import logging

s3 = boto3.client("s3")
size = int(os.environ["THUMBNAIL_SIZE"])
dbtable = str(os.environ["DYNAMODB_TABLE"])
dynamodb = boto3.resource(
    'dynamodb', region_name=str(os.environ["REGION_NAME"])
)


logger = logging.getLogger("Thumbnail Service")
logger.setLevel(logging.INFO)


def s3_thumbnail_generator(event, context):
    try:
        s3_record = event["Records"][0]["s3"]
        bucket = s3_record["bucket"]["name"]
        key = s3_record["object"]["key"]
        img_size = s3_record["object"]["size"]

        if not key.endswith("_thumbnail.png"):
            image = get_s3_image(bucket, key)
            width, height = image.size
            thumbnail = image_to_thumbnail(image, width, height)

            thumbnail_key = new_filename(key)
            url = upload_to_s3(bucket, thumbnail_key, thumbnail, img_size)
            return None

        body = {
            "message": "Go Serverless v3.0! Your function executed successfully!",
            "input": event,
        }
    except Exception as e:
        logger.info(f"{e}")
        body = {}

    return {"statusCode": 200, "body": json.dumps(body)}


def get_s3_image(bucket, key):
    response = s3.get_object(Bucket=bucket, Key=key)
    image_content = response["Body"].read()

    img_file = BytesIO(image_content)
    img = Image.open(img_file)
    return img

def image_to_thumbnail(image, width, height):
    height_percent = int(height*(size))
    width_size = int(width*(size))
    return image.resize((width_size, height_percent))

def new_filename(key):
    key_split = key.rsplit('.', 1)
    return key_split[0] + "_thumbnail.png"

def s3_save_thumbnail_url_to_dynamo(url_path, img_size):
    toint = float(img_size*0.53)/1000
    table = dynamodb.Table(dbtable)
    response = table.put_item(
        Item={
            'id': str(uuid.uuid4()),
            'url': str(url_path),
            'approxReducedSize': str(toint) + ' KB',
            'createdAt': str(datetime.now()),
            'updatedAt': str(datetime.now())
        }
    )

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(response)
    }

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
    s3_save_thumbnail_url_to_dynamo(url, img_size)

    return url