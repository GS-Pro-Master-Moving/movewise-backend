import uuid
from django.db import models
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile

from api.operator.models.Operator import Operator
from api.person.models import Person
from api.job.models.Job import Job
from api.tool.models.Tool import Tool
from api.company.models.Company import Company
from api.utils import upload_evidence_file, _upload_dispatch_file

# Possible States from USA
class StatesUSA(models.TextChoices):
    ALABAMA = "AL", "Alabama"
    ALASKA = "AK", "Alaska"
    ARIZONA = "AZ", "Arizona"
    ARKANSAS = "AR", "Arkansas"
    CALIFORNIA = "CA", "California"
    COLORADO = "CO", "Colorado"
    CONNECTICUT = "CT", "Connecticut"
    DELAWARE = "DE", "Delaware"
    FLORIDA = "FL", "Florida"
    GEORGIA = "GA", "Georgia"
    HAWAII = "HI", "Hawaii"
    IDAHO = "ID", "Idaho"
    ILLINOIS = "IL", "Illinois"
    INDIANA = "IN", "Indiana"
    IOWA = "IA", "Iowa"
    KANSAS = "KS", "Kansas"
    KENTUCKY = "KY", "Kentucky"
    LOUISIANA = "LA", "Louisiana"
    MAINE = "ME", "Maine"
    MARYLAND = "MD", "Maryland"
    MASSACHUSETTS = "MA", "Massachusetts"
    MICHIGAN = "MI", "Michigan"
    MINNESOTA = "MN", "Minnesota"
    MISSISSIPPI = "MS", "Mississippi"
    MISSOURI = "MO", "Missouri"
    MONTANA = "MT", "Montana"
    NEBRASKA = "NE", "Nebraska"
    NEVADA = "NV", "Nevada"
    NEW_HAMPSHIRE = "NH", "New Hampshire"
    NEW_JERSEY = "NJ", "New Jersey"
    NEW_MEXICO = "NM", "New Mexico"
    NEW_YORK = "NY", "New York"
    NORTH_CAROLINA = "NC", "North Carolina"
    NORTH_DAKOTA = "ND", "North Dakota"
    OHIO = "OH", "Ohio"
    OKLAHOMA = "OK", "Oklahoma"
    OREGON = "OR", "Oregon"
    PENNSYLVANIA = "PA", "Pennsylvania"
    RHODE_ISLAND = "RI", "Rhode Island"
    SOUTH_CAROLINA = "SC", "South Carolina"
    SOUTH_DAKOTA = "SD", "South Dakota"
    TENNESSEE = "TN", "Tennessee"
    TEXAS = "TX", "Texas"
    UTAH = "UT", "Utah"
    VERMONT = "VT", "Vermont"
    VIRGINIA = "VA", "Virginia"
    WASHINGTON = "WA", "Washington"
    WEST_VIRGINIA = "WV", "West Virginia"
    WISCONSIN = "WI", "Wisconsin"
    WYOMING = "WY", "Wyoming"
    
class Order(models.Model):
    key = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key_ref = models.CharField(max_length=50, null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    distance = models.PositiveIntegerField(null=True, blank=True)
    expense = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    income = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True, default="pending")
    payStatus = models.SmallIntegerField(null=True, blank=True)

    # Image fields
    dispatch_ticket = models.ImageField(upload_to=_upload_dispatch_file,null=True,blank=True,max_length=255)
    evidence = models.ImageField(upload_to=upload_evidence_file,null=True, blank=True,max_length=255)

    state_usa = models.CharField(
        max_length=2,
        choices=StatesUSA.choices,
        null=True,
        blank=True
    )

    id_company = models.ForeignKey(
        Company,
        related_name='orders',
        on_delete=models.CASCADE,
        db_column='id_company'
    )
    person = models.ForeignKey(
        Person,
        related_name='orders',
        on_delete=models.CASCADE,
        db_column="id_person"
    )
    job = models.ForeignKey(
        Job,
        related_name="orders",
        on_delete=models.CASCADE,
        db_column="id_job"
    )
    assign = models.ManyToManyField(
        Operator,
        through="Assign",
        related_name="assigned_operators"
    )
    tool = models.ManyToManyField(
        Tool,
        through="AssignTool",
        related_name="order_tools"
    )

    def __str__(self):
        return f"Order {self.key} - {self.person.id_person if self.person else 'No Person Assigned'}"

    def compress_image(self, image_field):
        try:
            if not image_field or not hasattr(image_field, 'path'):
                return image_field
                
            image = Image.open(image_field)
            if image.mode != 'RGB':
                image = image.convert('RGB')
                
            max_size = (1200, 1200)
            if image.width > max_size[0] or image.height > max_size[1]:
                image.thumbnail(max_size, Image.LANCZOS)
                
            buffer = BytesIO()
            image.save(buffer, format='JPEG', optimize=True, quality=60)
            
            filename = image_field.name.split('/')[-1]
            return ContentFile(buffer.getvalue(), name=filename)
        except Exception as e:
            print(f"Error compressing image: {e}")
            return image_field

    def save(self, *args, **kwargs):
        # Handle update_fields parameter
        update_fields = kwargs.get('update_fields')
        
        # Check if it's an existing object (has a primary key) or a new one
        is_new = not self.pk
        
        # For new objects or complete saves, compress both images
        if is_new or not update_fields:
            if self.evidence:
                self.evidence = self.compress_image(self.evidence)
            if self.dispatch_ticket:
                self.dispatch_ticket = self.compress_image(self.dispatch_ticket)
        # For partial updates, only compress the specified fields
        elif update_fields:
            if 'evidence' in update_fields and self.evidence:
                self.evidence = self.compress_image(self.evidence)
            if 'dispatch_ticket' in update_fields and self.dispatch_ticket:
                self.dispatch_ticket = self.compress_image(self.dispatch_ticket)
        
        # Call parent save method
        super().save(*args, **kwargs)
