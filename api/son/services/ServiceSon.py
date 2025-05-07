from api.son.repositories.RepositorySon import SonRepository

class SonService:

    @staticmethod
    def list_son():
        return SonRepository.get_all()

    @staticmethod
    def get_son(id_son):
        return SonRepository.get_by_id(id_son)

    @staticmethod
    def son_by_operator(operator_id):
        return SonRepository.get_by_operator(operator_id)

    @staticmethod
    def create_son(data):
        return SonRepository.create(**data)

    @staticmethod
    def update_son(son, data):
        return SonRepository.update(son, **data)

    @staticmethod
    def delete_son(son):
        return SonRepository.delete(son)
