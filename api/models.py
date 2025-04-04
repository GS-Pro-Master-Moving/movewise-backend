#Do not delete these imports, they are necessary for the code to work.
# These imports allows the framework to work with the models and serializers of the other apps.
from django.db import models
from api.operator.models.Operator import Operator
from api.job.models.Job import Job
from api.person.models.Person import Person
from api.tool.models.Tool import Tool
from api.order.models.Order import Order
from api.assign.models.Assign import Assign
from api.assign_tool.models.AssignTool import AssignTool
from api.truck.models.Truck import Truck
