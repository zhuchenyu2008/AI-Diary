import os
import uuid
from typing import Optional
from fastapi import UploadFile, HTTPException, status
import boto3
import oss2
from PIL import Image
import io

from app.core.config import settings


class StorageService:
    def __init__(self):
        self.storage_type = settings.storage_type
        
        # 初始化S3客户端
        if self.storage_type == "s3" and settings.aws_access_key_id:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
                region_name=settings.aws_region
            )
            self.bucket_name = settings.aws_s3_bucket
        else:
            self.s3_client = None
        
        # 初始化OSS客户端
        if self.storage_type == "oss" and settings.oss_access_key_id:
            self.oss_auth = oss2.Auth(settings.oss_access_key_id, settings.oss_access_key_secret)
            self.oss_bucket = oss2.Bucket(self.oss_auth, settings.oss_endpoint, settings.oss_bucket_name)
        else:
            self.oss_bucket = None
    
    async def upload_image(self, file: UploadFile) -> str:
        """上传图片到对象存储"""
        # 验证文件类型
        if file.content_type not in settings.allowed_image_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: {file.content_type}"
            )
        
        # 验证文件大小
        if file.size > settings.max_file_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large: {file.size} bytes"
            )
        
        # 读取并处理图片
        image_data = await file.read()
        
        # 压缩和优化图片
        optimized_image_data = await self._optimize_image(image_data)
        
        # 生成唯一文件名
        file_extension = self._get_file_extension(file.filename)
        file_name = f"images/{uuid.uuid4()}{file_extension}"
        
        # 上传到存储服务
        if self.storage_type == "s3":
            return await self._upload_to_s3(file_name, optimized_image_data, file.content_type)
        elif self.storage_type == "oss":
            return await self._upload_to_oss(file_name, optimized_image_data, file.content_type)
        else:
            return await self._upload_to_local(file_name, optimized_image_data)
    
    async def _optimize_image(self, image_data: bytes) -> bytes:
        """优化图片大小和质量"""
        try:
            # 打开图片
            image = Image.open(io.BytesIO(image_data))
            
            # 转换为RGB模式（如果是RGBA）
            if image.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            
            # 如果图片太大，进行压缩
            max_size = (1920, 1920)
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # 保存优化后的图片
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=85, optimize=True)
            return output.getvalue()
        except Exception as e:
            # 如果处理失败，返回原始数据
            return image_data
    
    def _get_file_extension(self, filename: str) -> str:
        """获取文件扩展名"""
        if not filename:
            return ".jpg"
        
        name, ext = os.path.splitext(filename.lower())
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            return ext
        return ".jpg"
    
    async def _upload_to_s3(self, file_name: str, image_data: bytes, content_type: str) -> str:
        """上传到S3"""
        if not self.s3_client:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="S3 client not configured"
            )
        
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_name,
                Body=image_data,
                ContentType=content_type,
                ACL='public-read'
            )
            
            # 返回公开访问的URL
            return f"https://{self.bucket_name}.s3.{settings.aws_region}.amazonaws.com/{file_name}"
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload to S3: {str(e)}"
            )
    
    async def _upload_to_oss(self, file_name: str, image_data: bytes, content_type: str) -> str:
        """上传到阿里云OSS"""
        if not self.oss_bucket:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="OSS client not configured"
            )
        
        try:
            self.oss_bucket.put_object(file_name, image_data, headers={'Content-Type': content_type})
            
            # 返回公开访问的URL
            return f"https://{settings.oss_bucket_name}.{settings.oss_endpoint}/{file_name}"
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload to OSS: {str(e)}"
            )
    
    async def _upload_to_local(self, file_name: str, image_data: bytes) -> str:
        """上传到本地存储"""
        try:
            # 创建本地存储目录
            local_storage_dir = "uploads/images"
            os.makedirs(local_storage_dir, exist_ok=True)
            
            # 保存文件
            file_path = os.path.join(local_storage_dir, os.path.basename(file_name))
            with open(file_path, "wb") as f:
                f.write(image_data)
            
            # 返回本地URL（开发环境）
            return f"/uploads/images/{os.path.basename(file_name)}"
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload to local storage: {str(e)}"
            )
    
    def generate_presigned_url(self, file_name: str, expiration: int = 3600) -> str:
        """生成预签名URL"""
        if self.storage_type == "s3" and self.s3_client:
            try:
                url = self.s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': self.bucket_name, 'Key': file_name},
                    ExpiresIn=expiration
                )
                return url
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to generate presigned URL: {str(e)}"
                )
        elif self.storage_type == "oss" and self.oss_bucket:
            try:
                url = self.oss_bucket.sign_url('GET', file_name, expiration)
                return url
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to generate presigned URL: {str(e)}"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Storage service not configured for presigned URLs"
            ) 