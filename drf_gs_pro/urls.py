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
from api.company.controllers.company_controller import CompanyViewSet
from api.payment.controllers.ControllerPayment import ControllerPayment

urlpatterns = [
    #login
    path('register/', UserRegister.as_view(), name='user-register'),
    path('login/', UserLogin.as_view(), name='user-login'),

    path('admin/', admin.site.urls),
    # Docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'), 
    # orders
    path('orders-states/', ControllerOrder.as_view({'get': 'get_states'}), name='order-get-states'),
    path('orders/', ControllerOrder.as_view({'post': 'create','get':'list_all' }), name='order-create'),
    path('orders/<str:pk>/', ControllerOrder.as_view({'patch': 'partial_update'}), name='order-update'),
    path('orders/status/<str:pk>/', ControllerOrder.as_view({'patch': 'update_status'}), name='order-update-status'),
    # jobs
    path('jobs/', JobController.as_view({'get': 'list'}), name='job-list'),
    # operators
    path('operators/<int:operator_id>/', ControllerOperator.as_view({'get': 'getOperatorByNumberId'}), name='operator-get-by-id'),
    path('operators-by-id/<int:operator_id>/', ControllerOperator.as_view({'get': 'getOperatorById'}), name='operator-get-by-number-id'),
    path('operators/', ControllerOperator.as_view({'post': 'create', 'get': 'list'}), name='operator-list-create'),
    path('operators/<int:operator_id>/patch/<str:field_name>/',ControllerOperator.as_view({'patch': 'patch_field'}), name='operator-patch-field'),

    path('operators/create/',ControllerOperator.as_view({'post': 'create_operator_person'}), name='operator-create-person'),

    # assigns
    path('assigns/', ControllerAssign.as_view({'post': 'create'}), name='assign-create'),
    path('assigns/bulk/', ControllerAssign.as_view({'post': 'bulk_create'}), name='assign-bulk-create'),
    path('assigns/<int:pk>/', ControllerAssign.as_view({'get': 'retrieve', 'delete': 'delete'}), name='assign-detail'),
    path('assigns/operator/<int:operator_id>/', ControllerAssign.as_view({'get': 'list_by_operator'}), name='assigns-by-operator'),
    path('assigns/order/<str:order_id>/', ControllerAssign.as_view({'get': 'list_by_order'}), name='assigns-by-order'),
    path('assigns/<int:pk>/update/', ControllerAssign.as_view({'patch': 'update'}), name='assign-update'),
    path('assigns/<int:assign_id>/update-status/', ControllerAssign.as_view({'patch': 'update_status'}), name='assign-update-status'),
    path('assigns/<int:pk>/audit-history/', ControllerAssign.as_view({'get': 'audit_history'}), name='assign-audit-history'),
    path('assigns/order/<str:order_key>/operators/', ControllerAssign.as_view({'get': 'get_assigned_operators'}), name='assign-get-operators'),
    # assignTools
    path('assignTool/', ControllerAssignTool.as_view({'post': 'assign_tool'}), name='assign-tool'),
    path('assignTools/', ControllerAssignTool.as_view({'post': 'bulk_create'}), name='assign-tool'),
    path('unassignTool/', ControllerAssignTool.as_view({'delete': 'unassign_tool'}), name='unassign-tool'),
    path('assignedTools/', ControllerAssignTool.as_view({'get': 'get_assigned_tools'}), name='assigned-tools'),
    # Trucks
    path('truck-by-id/<int:id_truck>/', ControllerTruck.as_view({'get': 'get_truck_by_id'}), name='truck-get-by-id'),    
    path('trucks/', ControllerTruck.as_view({'get': 'get_avaliable', 'post': 'create'}), name='truck-list-create'),
    path('trucks/<int:pk>/', ControllerTruck.as_view({'patch': 'update_status'}), name='truck-update-status'),

    # Companies
    path('companies/', CompanyViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='company-list-create'),
    path('companies/<int:pk>/', CompanyViewSet.as_view({
        'get': 'retrieve',
        #'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='company-detail'),

    # Payments
    path('payments/', ControllerPayment.as_view({
        'get': 'list',
        'post': 'create'
    }), name='payment-list-create'),
    path('payments/<int:pk>/', ControllerPayment.as_view({
        'get': 'retrieve',
        'patch': 'update',
        'delete': 'destroy'
    }), name='payment-detail'),
   
]
