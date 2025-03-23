from django.contrib import admin
from django.urls import path
from api.operator.controllers.ControllerOperator import ControllerOperator
from api.order.controllers.ControllerOrder import OrderController
from api.job.controllers.ControllerJob import JobController  
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from api.assign.controllers.ControllerAssign import ControllerAssign
urlpatterns = [
    path('admin/', admin.site.urls),
    # Docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'), 
    # orders
    path('orders/', OrderController.as_view({'post': 'create'}), name='order-create'),
    # jobs
    path('jobs/', JobController.as_view({'get': 'list'}), name='job-list'),
    # operators
    path('operators/', ControllerOperator.as_view({'post': 'create'}), name='operator-create'),
    path('operators/<int:operator_id>/patch/<str:field_name>/',ControllerOperator.as_view({'patch': 'patch_field'}), name='operator-patch-field'),
    # assigns
    path('assigns/', ControllerAssign.as_view({'post': 'create'}), name='assign-create'),
    path('assigns/<int:pk>/', ControllerAssign.as_view({'get': 'retrieve', 'delete': 'delete'}), name='assign-detail'),
    path('assigns/operator/<int:operator_id>/', ControllerAssign.as_view({'get': 'list_by_operator'}), name='assigns-by-operator'),
    path('assigns/order/<int:order_id>/', ControllerAssign.as_view({'get': 'list_by_order'}), name='assigns-by-order'),
    path('assigns/<int:assign_id>/update-status/', ControllerAssign.as_view({'patch': 'update_status'}), name='assign-update-status'),
]
