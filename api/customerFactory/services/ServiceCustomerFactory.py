from api.customerFactory.repositories.RepositoryCustomerFactory import RepositoryCustomerFactory
class ServicesCustomerFactory:

    def __init__(self):
        self.repository = RepositoryCustomerFactory()

    def list(self):
        return self.repository.get_all()

    def get(self, id):
        return self.repository.get_by_id(id)

    def create(self, validated_data):
        return self.repository.create(validated_data)

    def update(self, id, validated_data):
        entity = self.get(id)
        return self.repository.update(entity, validated_data) if entity else None

    def delete(self, id):
        entity = self.get(id)
        if not entity:
            return None
        return self.repository.delete(entity)
    
    def setStateFalse(self, id):
        return self.repository.setStateFalse(id)
