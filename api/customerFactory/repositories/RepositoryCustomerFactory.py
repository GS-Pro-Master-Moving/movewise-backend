from api.customerFactory.models.CustomerFactory import CustomerFactory

class RepositoryCustomerFactory:

    def get_all(self):
        return CustomerFactory.objects.filter(state=True).all()

    def get_by_id(self, id):
        return CustomerFactory.objects.filter(pk=id).first()

    def create(self, data):
        return CustomerFactory.objects.create(**data)

    def update(self, instance, data):
        for k, v in data.items():
            setattr(instance, k, v)
        instance.save(update_fields=list(data.keys()))
        return instance

    def delete(self, instance):
        instance.delete()
        return True

    def setStateFalse(self, pk):
        print(pk)
        cf = CustomerFactory.objects.filter(id_factory=pk).first()
        print(cf)
        if(cf.state==False):
            return None
        if(cf==None):
            return None
        cf.state = False
        cf.save(update_fields=['state'])
        return cf