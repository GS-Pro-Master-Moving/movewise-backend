import uuid
from django.db import models
from api.operator.models.Operator import Operator
from api.person.models import Person 

from api.job.models.Job import Job
from api.tool.models.Tool import Tool
from api.company.models.Company import Company

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
    key = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # Unique ID for DB
    key_ref = models.CharField(max_length=50,null=True, blank=True)
    date = models.DateField(null=True, blank=True)  # Order date
    distance = models.PositiveIntegerField(null=True, blank=True) # Order income
    expense = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)
    income = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True) 
    weight = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)  # Weight of charge
    # states of the order
    # It has 3 possible values: "pending", "finished", "inactive"
    # "pending" means that the order is still active and can be modified
    # "finished" means that the order is completed and cannot be modified
    # "inactive" means that the order is no longer active and cannot be modified
    # "en transito?"
    status = models.CharField(max_length=50,null=True, blank=True, default="pending")
    payStatus = models.SmallIntegerField(null=True, blank=True) 
    evidence = models.URLField(null=True, blank=True)  # URL of evidence
    state_usa = models.CharField(
        max_length=2, 
        choices=StatesUSA.choices,
        null=True, blank=True
    )
    # By the moment person its created everytime there is a register
    # even when the email its registered
    id_company = models.ForeignKey(
        Company,
        related_name='orders',
        on_delete=models.CASCADE,
        db_column='id_company',
        null=True,
        blank=True
    )
    person = models.ForeignKey( # Person realtion
        Person, 
        related_name='orders', 
        on_delete=models.CASCADE,
        db_column="id_person"  
    )

    job = models.ForeignKey(  # Job realtion
        Job, 
        related_name="orders", 
        on_delete=models.CASCADE,
        db_column="id_job"
    )

    assign = models.ManyToManyField(
        Operator, 
        through="Assign", 
        related_name="assigned_operators",
        db_column="id_assign")

    tool = models.ManyToManyField(
        Tool, 
        through="AssignTool", 
        related_name="order_tools",
        db_column="id_tool"
    )
    
    def __str__(self):
        return f"Order {self.key} - {self.person.id_person if self.person else 'No Person Assigned'}"

