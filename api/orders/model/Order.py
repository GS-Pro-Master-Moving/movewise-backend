import uuid
from django.db import models

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

# Possible jobs taken in an order
class Job(models.TextChoices):
    CHARGING = "C", "Charge"
    PACKING = "P", "Packing"
    DISCHARGING = "D", "Discharging"
    LOADING = "L", "Loading"
    COMERCIAL = "Com", "Comercial"
    DEBRIS = "Deb", "Debris"

# Class model Order
class Order(models.Model):
    key = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # Unique ID for DB
    key_ref = models.CharField(max_length=50)
    date = models.DateField()  # Order date
    distance = models.PositiveIntegerField() # Order income
    expense = models.DecimalField()
    income = models.DecimalField() 
    weight = models.DecimalField(max_digits=10, decimal_places=2)  # Weight of charge
    status = models.CharField(max_length=50);
    payStatus = models.SmallIntegerField()
    state_usa = models.CharField(
        max_length=2, 
        choices=StatesUSA.choices
    )
    
    job_assigned = models.CharField(
        max_length=3,
        choices=Job.choices
    )

    def __str__(self):
        return f"Order {self.key} - {self.client_name} {self.client_last_name}"
