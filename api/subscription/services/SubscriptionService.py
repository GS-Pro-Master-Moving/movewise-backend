from api.subscription.repositories.SubscriptionRepository import SubscriptionRepository

class SubscriptionService:
    def list_subscriptions(self):
        return SubscriptionRepository.get_all()

    def get_subscription(self, subscription_id):
        return SubscriptionRepository.get_by_id(subscription_id)

    def create_subscription(self, data):
        return SubscriptionRepository.create(data)
