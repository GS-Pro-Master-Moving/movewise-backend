from django.contrib import admin
from django.urls import path
from api.company.controllers.ControllerCompany import ControllerCompany
from api.operator.controllers.ControllerOperator import ControllerOperator
from api.order.controllers.ControllerOrder import ControllerOrder
from api.job.controllers.ControllerJob import JobController  
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from api.assign.controllers.ControllerAssign import ControllerAssign
from api.truck.controllers.ControllerTruck import ControllerTruck  
from api.assign_tool.controllers.ControllerAssignTool import ControllerAssignTool
from api.user.controllers.UserController import UserRegister, UserLogin
urlpatterns = [
    #login
    path('register/', UserRegister.as_view(), name='user-register'),
    path('login/', UserLogin.as_view(), name='user-login'),

    path('admin/', admin.site.urls),
    # Docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'), 
    # orders
    path('orders/', ControllerOrder.as_view({'post': 'create'}), name='order-create'),
    path('orders/<str:pk>/', ControllerOrder.as_view({'patch': 'partial_update'}), name='order-update'),
    # jobs
    path('jobs/', JobController.as_view({'get': 'list'}), name='job-list'),
    # operators
    path('operators/', ControllerOperator.as_view({'post': 'create', 'get': 'list'}), name='operator-list-create'),
    path('operators/<int:operator_id>/patch/<str:field_name>/',ControllerOperator.as_view({'patch': 'patch_field'}), name='operator-patch-field'),
    # assigns
    path('assigns/', ControllerAssign.as_view({'post': 'create'}), name='assign-create'),
    path('assigns/<int:pk>/', ControllerAssign.as_view({'get': 'retrieve', 'delete': 'delete'}), name='assign-detail'),
    path('assigns/operator/<int:operator_id>/', ControllerAssign.as_view({'get': 'list_by_operator'}), name='assigns-by-operator'),
    path('assigns/order/<int:order_id>/', ControllerAssign.as_view({'get': 'list_by_order'}), name='assigns-by-order'),
    path('assigns/<int:assign_id>/update-status/', ControllerAssign.as_view({'patch': 'update_status'}), name='assign-update-status'),
    # assignTools
    path('assignTool/', ControllerAssignTool.as_view({'post': 'assign_tool'}), name='assign-tool'),
    path('assignTools/', ControllerAssignTool.as_view({'post': 'bulk_create'}), name='assign-tool'),
    path('unassignTool/', ControllerAssignTool.as_view({'delete': 'unassign_tool'}), name='unassign-tool'),
    path('assignedTools/', ControllerAssignTool.as_view({'get': 'get_assigned_tools'}), name='assigned-tools'),
    # Trucks
    path('trucks/', ControllerTruck.as_view({'get': 'get_avaliable', 'post': 'create'}), name='truck-list-create'),
    path('trucks/<int:pk>/', ControllerTruck.as_view({'patch': 'update_status'}), name='truck-update-status'),
    # Company
    path('companies/', ControllerCompany.as_view({'post': 'create', 'get': 'list'}), name='company-list-create'),
    path('companies/<int:pk>/', ControllerCompany.as_view({'patch': 'update', 'delete': 'delete'}), name='company-update-delete'),
    path('companies/<str:name>/', ControllerCompany.as_view({'get': 'retrieve_by_name'}), name='company-retrieve-by-name'),
    path('companies/<int:pk>/patch/<str:field_name>/', ControllerCompany.as_view({'patch': 'patch_field'}), name='company-patch-field'),
]
