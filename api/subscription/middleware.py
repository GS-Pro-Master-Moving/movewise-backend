# api/subscription/middleware.py
from django.utils import timezone
from django.http import JsonResponse
from api.company.models.Company import Company
from api.subscription.models import Subscription
import jwt
from django.conf import settings

SAFE_METHODS = ("HEAD", "OPTIONS")
EXEMPT_PATHS = ["/login/", "/register/", "/api/schema/", "/api/docs/"]

class SubscriptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Initial log with request details
        print(f"\n🔔 [{timezone.now()}] Incoming {request.method} request to {request.path}")

        if self._should_exempt_request(request):
            print("🟡 Exempt request - skipping validation")
            return self.get_response(request)

        company_id = self._get_company_id(request)
        if not company_id:
            print("🔴 No company ID found in request")
            return JsonResponse({"detail": "Company not found in token"}, status=401)

        try:
            # Get company with related subscription and plan
            company = Company.objects.select_related(
                'subscription',
                'subscription__id_plan'
            ).get(pk=company_id)
            
            # Log company details
            print(f"\n🏢 COMPANY DETAILS")
            print(f"ID: {company.id}")
            print(f"Name: {company.name}")
            print(f"License: {company.license_number}")
            print(f"Created: {company.created_at.date()}")

            subscription = company.subscription
            if subscription:
                # Log subscription details
                print(f"\n📅 SUBSCRIPTION STATUS")
                print(f"ID: {subscription.id_subscription}")
                print(f"Status: {subscription.status.upper()}")
                print(f"Period: {subscription.start_date} to {subscription.end_date}")
                
                # Log plan details
                if subscription.id_plan:
                    plan = subscription.id_plan
                    print(f"\n📋 ASSOCIATED PLAN")
                    print(f"ID: {plan.id_plan}")
                    print(f"Name: {plan.name}")
                    print(f"Price: ${plan.price}")
                    # print(f"Features: {', '.join(plan.features)}")
                else:
                    print("\n⚠️ No associated plan found")
            else:
                print("\n⚠️ No active subscription found")

        except Company.DoesNotExist:
            print(f"🔴 Company ID {company_id} not found in database")
            return JsonResponse({"detail": "Company not found"}, status=401)

        # Validate subscription
        is_valid = self._validate_subscription(company)
        validation_result = "🟢 Valid subscription" if is_valid else "🔴 Invalid subscription"
        print(f"\n{validation_result} - {'Allowing' if is_valid else 'Blocking'} {request.method} request")

        if not is_valid:
            return JsonResponse(
                {"detail": "Subscription inactive - write operations blocked"}, 
                status=403
            )

        return self.get_response(request)

    def _should_exempt_request(self, request):
        return (
            request.method in SAFE_METHODS or 
            any(request.path.startswith(p) for p in EXEMPT_PATHS)
        )

    def _get_company_id(self, request):
        """Get company ID in priority order"""
        # 1. Check request context (set by authentication)
        if hasattr(request, 'company_id'):
            print(f"🔑 Company ID from request context: {request.company_id}")
            return request.company_id
        
        # 2. Fallback to user/person object
        if hasattr(request.user, 'company_id'):
            print(f"👤 Company ID from user object: {request.user.company_id}")
            return request.user.company_id
        
        # 3. Last resort: Check auth header directly
        token = request.headers.get('Authorization', '').split()[-1]
        if token:
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                print(f"🔍 Company ID from token payload: {payload.get('company_id')}")
                return payload.get('company_id')
            except jwt.PyJWTError:
                print("⚠️ Failed to decode token for company ID")
        
        return None

    def _validate_subscription(self, company):
        today = timezone.now().date()
        
        try:
            subscription = company.subscription
            return (
                subscription and
                subscription.status.lower() == "active" and
                subscription.start_date <= today <= subscription.end_date
            )
        except Subscription.DoesNotExist:
            return False