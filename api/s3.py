import uuid
import boto3
from fastapi import APIRouter, File, HTTPException, UploadFile

from config.config import AWS_S3_BUCKET
from config.config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION



router = APIRouter()

s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

@router.post("/upload")
async def upload_logo(
    file: UploadFile = File(...)
):
    try:
        file_key = f"uploads/{uuid.uuid4().hex}_{file.filename}"
        
        s3.upload_fileobj(
            file.file,
            AWS_S3_BUCKET,
            file_key,
            ExtraArgs={"ContentType": file.content_type}
        )
        
        file_url = f"https://{AWS_S3_BUCKET}.s3.amazonaws.com/{file_key}"
        return {"url": file_url}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        