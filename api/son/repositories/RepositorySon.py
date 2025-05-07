from api.son.models.Son import Son

class SonRepository:
    
    @staticmethod
    def get_all():
        return Son.objects.all()
    
    @staticmethod
    def get_by_id(son_id):
        return Son.objects.filter(id_son=son_id).first()

    @staticmethod
    def get_by_operator(operator_id):
        return Son.objects.filter(operator_id=operator_id)
    
    @staticmethod
    def create(**kwargs):
        return Son.objects.create(**kwargs)
    
    @staticmethod
    def update(instance, **kwargs):
        for attr, value in kwargs.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
    @staticmethod
    def delete(instance):
        instance.delete()
