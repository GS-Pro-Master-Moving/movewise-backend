from django.contrib import admin
from django.urls import path
from api.order.controllers.ControllerOrder import OrderController
from api.job.controllers.ControllerJob import JobController  

urlpatterns = [
    path('admin/', admin.site.urls),
    path('orders/', OrderController.as_view({'post': 'create'}), name='order-create'),
    path('jobs/', JobController.as_view({'get': 'list'}), name='job-list'), 
]
