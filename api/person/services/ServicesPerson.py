from api.person.services.IServicesPerson import IServicesPerson
from api.person.repositories.RepositoryPerson import RepositoryPerson
from api.person.models.Person import Person
from typing import List, Optional

class ServicesPerson(IServicesPerson):
    def __init__(self):
        self.repository = RepositoryPerson()
        
    def create(self, person: Person) -> Person:
        return self.repository.create(person)
    
    def delete(self, person_id: str) -> bool:
        return self.repository.delete(person_id)
    
    def list(self) -> List[Person]:
        return self.repository.list() 
    def get(self, person_id: str) -> Optional[Person]:
        return self.repository.get(person_id)
    
    def getByEmail(self, email):
        return self.repository.getByEmail(email)