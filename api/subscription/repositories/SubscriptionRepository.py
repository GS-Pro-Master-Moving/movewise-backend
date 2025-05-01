from api.subscription.models.Subscription import Subscription

class SubscriptionRepository:
    @staticmethod
    def get_all():
        return Subscription.objects.all()

    @staticmethod
    def get_by_id(subscription_id):
        return Subscription.objects.filter(id_subscription=subscription_id).first()

    @staticmethod
    def create(data):
        return Subscription.objects.create(**data)

    @staticmethod
    def update(instance, data):
        for attr, value in data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    @staticmethod
    def delete(instance):
        instance.delete()
