from abc import ABC, abstractmethod
from typing import List, Optional
from api.person.models.Person import Person

class IServicesPerson(ABC):
    """
    Interface for the Person service.
    This interface defines the standard operations (CRUD) for managing Person entities.
    Implementations should provide the actual business logic and data validation.
    """

    @abstractmethod
    def create(self, person: Person) -> Person:
        """
        Creates a new Person record.
        """
        pass

    @abstractmethod
    def delete(self, person_id: str) -> bool:
        """
        Deletes a Person by its ID.
        """
        pass

    @abstractmethod
    def list(self) -> List[Person]:
        """
        Retrieves all Person records.

        Returns:
            List[Person]: A list containing all registered Persons.
        """
        pass

    @abstractmethod
    def get(self, person_id: str) -> Optional[Person]:
        """
        Retrieves a Person by its ID.

        Returns:
            The Person object if found, None otherwise.
        """
        pass
    
    @abstractmethod
    def getByEmail(self, email: str) -> Optional[Person]:
        """
        Retrieves a Person by its email.

        Returns:
            The Person object if found, None otherwise.
        """
        pass