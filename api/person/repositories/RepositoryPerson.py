from typing import List, Optional
from api.person.models.Person import Person
from api.person.repositories.IRepositoryPerson import IRepositoryPerson

class RepositoryPerson(IRepositoryPerson):

    def create(self, person: Person) -> Person:
        person.save()
        return person

    def delete(self, person_id: str) -> bool:
        deleted_count, _ = Person.objects.filter(id_person=person_id).delete()
        return deleted_count > 0

    def list(self) -> List[Person]:
        return list(Person.objects.all())

    def get(self, person_id: str) -> Optional[Person]:
        try:
            return Person.objects.get(id_person=person_id)
        except Person.DoesNotExist:
            return None

    def getByEmail(self, email: str) -> Optional[Person]:
        try:
            return Person.objects.get(email=email)
        except Person.DoesNotExist:
            return None