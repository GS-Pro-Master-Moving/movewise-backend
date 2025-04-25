from django.conf import settings
from django.conf.urls.static import static #image managment

from django.contrib import admin
from django.urls import path
from api.company.controllers.ControllerCompany import ControllerCompany
from api.operator.controllers.ControllerOperator import ControllerOperator
from api.order.controllers.ControllerOrder import ControllerOrder
from api.job.controllers.ControllerJob import JobController  
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from api.assign.controllers.ControllerAssign import ControllerAssign
from api.tool.controllers.ControllerTool import ControllerTool
from api.truck.controllers.ControllerTruck import ControllerTruck  
from api.assign_tool.controllers.ControllerAssignTool import ControllerAssignTool

from api.user.controllers.UserController import UserRegister, UserLogin
from api.company.controllers.company_controller import CompanyViewSet
from api.payment.controllers.ControllerPayment import ControllerPayment
from api.workCost.controllers.ControllerWorkCost import ControllerWorkCost
from api.costFuel.controllers.CostFuelController import ControllerCostFuel
from api.son.controllers.ControllerSon import SonController

urlpatterns = [
    #login
    path('register/', UserRegister.as_view(), name='user-register'),
    path('login/', UserLogin.as_view(), name='user-login'),

    path('admin/', admin.site.urls),
    # Docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'), 
    # orders
    path('orders-with-costFuel/', ControllerOrder.as_view({'get':'list_with_fuel'}), name="orders-with-costFuel"),
    path('orders-states/', ControllerOrder.as_view({'get': 'get_states'}), name='order-get-states'),
    path('orders/', ControllerOrder.as_view({'post': 'create','get':'list_all' }), name='order-create'),
    path('orders/<str:pk>/', ControllerOrder.as_view({'patch': 'partial_update'}), name='order-update'),
    path('orders/status/<str:pk>/', ControllerOrder.as_view({'patch': 'update_status'}), name='order-update-status'),
    path('orders/<str:pk>/summary-cost/', ControllerOrder.as_view({'get': 'SumaryCost'}), name='order-summary-cost'),
    path('order_details/<str:pk>/', ControllerOrder.as_view({'get': 'get_order_details'}), name='order-details'),
    path('summary-list/', ControllerOrder.as_view({'get': 'summary_orders_list'}), name='order-summary-list'),
    # jobs
    path('jobs/', JobController.as_view({'get': 'list'}), name='job-list'),
    # operators
    path('operators/<int:operator_id>/', ControllerOperator.as_view({'get': 'getOperatorByNumberId'}), name='operator-get-by-id'),
    path('operators-by-id/<int:operator_id>/', ControllerOperator.as_view({'get': 'getOperatorById'}), name='operator-get-by-number-id'),
    path('operators/', ControllerOperator.as_view({'post': 'create', 'get': 'list'}), name='operator-list-create'),
    path('operators/<int:operator_id>/patch/<str:field_name>/',ControllerOperator.as_view({'patch': 'patch_field'}), name='operator-patch-field'),

    path('operators/create/',ControllerOperator.as_view({'post': 'create_operator_person'}), name='operator-create-person'),
    path('operators/update/<int:id_operator>/', ControllerOperator.as_view({'patch': 'update_operator_person'}), name='operator-update-person'),
    # assigns
    path('list-assign-operator/', ControllerAssign.as_view({'get': 'list_assign_operator'}), name='assign-operator'),
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
    path('assignTool/order/<str:key>/', ControllerAssignTool.as_view({'get': 'get_assigned_tools'}), name='assigned-tools-by-order'),
    # Trucks
    path('truck-by-id/<int:id_truck>/', ControllerTruck.as_view({'get': 'get_truck_by_id'}), name='truck-get-by-id'),    
    path('trucks/', ControllerTruck.as_view({'get': 'get_avaliable', 'post': 'create'}), name='truck-list-create'),
    path('trucks/<int:pk>/', ControllerTruck.as_view({'patch': 'update_status'}), name='truck-update-status'),
    path('trucks/<int:pk>/update/', ControllerTruck.as_view({'put': 'update_truck'}), name='truck-update'),
    path('trucks/<int:pk>/delete/', ControllerTruck.as_view({'delete': 'delete_truck'}), name='truck-delete'),
    # Cost Fuel
    path('costfuel-by-id/<int:pk>/', ControllerCostFuel.as_view({'get': 'retrieve'}), name='costfuel-get-by-id'),    
    path('costfuels/', ControllerCostFuel.as_view({'get': 'list', 'post': 'create'}), name='costfuel-list-create'),
    path('costfuels/<int:pk>/', ControllerCostFuel.as_view({'put': 'update', 'patch': 'update'}), name='costfuel-update'),
    path('costfuels/<int:pk>/delete/', ControllerCostFuel.as_view({'delete': 'destroy'}), name='costfuel-delete'),
    path('costfuels/by-order/<str:order_key>/', ControllerCostFuel.as_view({'get': 'by_order'}), name='costfuel-by-order'),
    path('costfuels/by-truck/<int:truck_id>/', ControllerCostFuel.as_view({'get': 'by_truck'}), name='costfuel-by-truck'),
    #Son
    path('sons/', SonController.as_view({'get': 'get', 'post': 'post'}), name='son-list-create'),
    path('sons/<int:son_id>/', SonController.as_view({
        'get': 'get',
        'put': 'put',
        'delete': 'delete'
    }), name='son-detail'),
    #tools
    path('tools/', ControllerTool.as_view({'get': 'list'}), name='tool-list'),

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

    #WorkCost
    path('workcost/', ControllerWorkCost.as_view({
    'get': 'list',
    'post': 'create'
    }), name='workcost-list-create'),
    path('workcost/order/<str:order_id>/', 
        ControllerWorkCost.as_view({'get': 'listByOrderId'}), 
        name='workcost-list-by-order-id'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)