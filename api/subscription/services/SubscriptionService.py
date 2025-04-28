from api.subscription.repositories.SubscriptionRepository import SubscriptionRepository

class SubscriptionService:
    @staticmethod
    def list_subscriptions():
        return SubscriptionRepository.get_all()

    @staticmethod
    def retrieve_subscription(subscription_id):
        return SubscriptionRepository.get_by_id(subscription_id)

    @staticmethod
    def create_subscription(data):
        return SubscriptionRepository.create(data)

    @staticmethod
    def update_subscription(instance, data):
        return SubscriptionRepository.update(instance, data)

    @staticmethod
    def delete_subscription(instance):
        return SubscriptionRepository.delete(instance)
