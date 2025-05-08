"""
Centralized image processing utilities for handling image uploads
Compatible with both local and cloud storage backends (S3, DO Spaces, etc.)
"""
import uuid
import logging
from io import BytesIO
from PIL import Image, ImageOps
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)

class ImageProcessor:
    """
    Utility class for processing images before storage
    Works with both local file systems and cloud storage backends
    """
    
    @staticmethod
    def compress_image(image_field, quality=60, max_size=(1200, 1200), format='JPEG', prefix=None):
        """
        Compress an image to optimize storage and loading speed
        Compatible with S3 and other storage backends that don't support path()
        
        Args:
            image_field: Django ImageField or InMemoryUploadedFile
            quality: Compression quality (1-100)
            max_size: Maximum dimensions (width, height)
            format: Output format (JPEG, PNG, etc)
            prefix: Optional prefix for filename
            
        Returns:
            ContentFile of compressed image or original if compression failed
        """
        if not image_field:
            logger.debug("No image field provided for compression")
            return image_field
            
        try:
            # Safely handle all types of image fields without relying on path
            # which may not be supported by S3/cloud storage backends
            try:
                # Try reading directly, which works for both InMemoryUploadedFile 
                # and files from remote storage
                image = Image.open(image_field)
                logger.debug(f"Processing image: {getattr(image_field, 'name', 'unnamed')}")
            except Exception as e:
                logger.warning(f"Error opening image directly: {str(e)}")
                # If direct opening fails, we have no other options
                logger.error("Could not process image")
                return image_field
            
            # Record original dimensions
            original_width, original_height = image.size
            logger.debug(f"Original image dimensions: {original_width}x{original_height}")
            
            # Convert to RGB if necessary (excluding formats that support transparency)
            if format.upper() != 'PNG' and image.mode not in ('RGB', 'L'):
                image = image.convert('RGB')
                logger.debug(f"Converted image from {image.mode} to RGB")
            
            # Resize if larger than max_size
            if original_width > max_size[0] or original_height > max_size[1]:
                image = ImageOps.contain(image, max_size, method=Image.LANCZOS)
                new_width, new_height = image.size
                logger.debug(f"Resized image to {new_width}x{new_height}")
            
            # Process in memory
            buffer = BytesIO()
            
            # Save with appropriate format and compression
            save_kwargs = {'optimize': True, 'quality': quality}
            
            # Remove quality parameter for PNG as it's not supported
            if format.upper() == 'PNG':
                save_kwargs.pop('quality', None)
                save_kwargs['optimize'] = True
                save_kwargs['compress_level'] = 6  # For PNG compression
            
            image.save(
                buffer, 
                format=format,
                **save_kwargs
            )
            
            # Create unique filename to avoid cache issues
            extension = format.lower()
            timestamp = uuid.uuid4().hex[:8]
            
            if prefix:
                new_name = f"{prefix}_{timestamp}.{extension}"
            else:
                # Try to preserve original filename but add timestamp
                if hasattr(image_field, 'name') and image_field.name:
                    original_name = image_field.name.split('/')[-1]  # Use only filename part
                    name_parts = original_name.split('.')
                    if len(name_parts) > 1:
                        base_name = '.'.join(name_parts[:-1])
                        new_name = f"{base_name}_{timestamp}.{extension}"
                    else:
                        new_name = f"{original_name}_{timestamp}.{extension}"
                else:
                    new_name = f"image_{timestamp}.{extension}"
            
            logger.debug(f"Created compressed image with name: {new_name}")
            buffer_size = len(buffer.getvalue())
            logger.debug(f"Compressed size: {buffer_size} bytes")
            
            buffer.seek(0)  # Reset buffer position to beginning
            return ContentFile(buffer.getvalue(), name=new_name)
            
        except Exception as e:
            logger.error(f"Error compressing image: {str(e)}", exc_info=True)
            return image_field  # Return original if compression fails
            
    @staticmethod
    def compress_image_with_metadata(image_field, quality=60, max_size=(1200, 1200), format='JPEG', prefix=None, metadata=None):
        """
        Extended version that preserves important metadata while compressing
        
        Args:
            image_field: Django ImageField
            quality: Compression quality (1-100)
            max_size: Maximum dimensions (width, height)
            format: Output format (JPEG, PNG, etc)
            prefix: Optional prefix for filename
            metadata: Dict of metadata to preserve (e.g. EXIF data)
            
        Returns:
            ContentFile of compressed image with metadata or original if compression failed
        """
        # Call basic compression first
        compressed = ImageProcessor.compress_image(image_field, quality, max_size, format, prefix)
        
        # If metadata provided and compression successful, try to add metadata
        if metadata and compressed != image_field:
            try:
                # Create a new buffer with the compressed image
                img_buffer = BytesIO()
                img_buffer.write(compressed.read())
                img_buffer.seek(0)
                
                # Open the compressed image
                img = Image.open(img_buffer)
                
                # Create a new buffer for the metadata-enhanced version
                meta_buffer = BytesIO()
                
                # Save with metadata
                save_kwargs = {'optimize': True, 'quality': quality}
                save_kwargs.update(metadata)
                
                # Remove quality parameter for PNG as it's not supported
                if format.upper() == 'PNG':
                    save_kwargs.pop('quality', None)
                
                img.save(
                    meta_buffer,
                    format=format,
                    **save_kwargs
                )
                
                # Return the image with metadata
                return ContentFile(meta_buffer.getvalue(), name=compressed.name)
                
            except Exception as e:
                logger.error(f"Error adding metadata to image: {str(e)}", exc_info=True)
                return compressed  # Return compressed version without metadata if this fails
        
        return compressed