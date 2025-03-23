from django.contrib import admin
from django.urls import path
from api.operator.controllers.ControllerOperator import ControllerOperator
from api.order.controllers.ControllerOrder import OrderController
from api.job.controllers.ControllerJob import JobController  

urlpatterns = [
    path('admin/', admin.site.urls),
    path('orders/', OrderController.as_view({'post': 'create'}), name='order-create'),
    path('jobs/', JobController.as_view({'get': 'list'}), name='job-list'),
    path('operators/', ControllerOperator.as_view({'post': 'create'}), name='operator-create'),
    path('operators/<int:operator_id>/patch/<str:field_name>/',ControllerOperator.as_view({'patch': 'patch_field'}), name='operator-patch-field'),
]
