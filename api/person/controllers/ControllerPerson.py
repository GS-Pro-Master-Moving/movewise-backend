from api.person.services.ServicesPerson import ServicesPerson
from api.person.serializers.PersonSerializer import PersonSerializer
from rest_framework import viewsets, status
from rest_framework.response import Response

class ControllerPerson(viewsets.ViewSet):
    """
    Controller for managing Person entities.

    Provides endpoints for:
    - Creating a person.
    - Deleting a person.
    - Listing all persons.
    - Retrieving a person by ID.
    - Retrieving a person by email.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.person_service = ServicesPerson()  

    def create(self, request):
        """
        Create a new person.

        Expects:
        - A JSON body with person details.

        Returns:
        - 201 Created: If the person is successfully created.
        - 400 Bad Request: If the request contains invalid data.
        """
        serializer = PersonSerializer(data=request.data)
        if serializer.is_valid():
            person = self.person_service.create(serializer.validated_data) 
            return Response(PersonSerializer(person).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, person_id):
        """
        Delete a person by ID.

        Path Parameters:
        - `person_id`: The ID of the person to delete.

        Returns:
        - 204 No Content: If the person is successfully deleted.
        - 404 Not Found: If the person does not exist.
        """
        success = self.person_service.delete(person_id)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"error": "Person not found"}, status=status.HTTP_404_NOT_FOUND)
    
    def list(self, request):
        """
        List all persons.

        Returns:
        - 200 OK: A list of all persons.
        """
        persons = self.person_service.list()
        return Response(PersonSerializer(persons, many=True).data, status=status.HTTP_200_OK)
    
    def retrieve(self, request, person_id):
        """
        Retrieve a person by ID.

        Path Parameters:
        - `person_id`: The ID of the person to retrieve.

        Returns:
        - 200 OK: The details of the person.
        - 404 Not Found: If the person does not exist.
        """
        person = self.person_service.get(person_id)
        if person:
            return Response(PersonSerializer(person).data, status=status.HTTP_200_OK)
        return Response({"error": "Person not found"}, status=status.HTTP_404_NOT_FOUND)
    
    def retrieve_by_email(self, request, email):
        """
        Retrieve a person by email.

        Path Parameters:
        - `email`: The email of the person to retrieve.

        Returns:
        - 200 OK: The details of the person.
        - 404 Not Found: If the person does not exist.
        """
        person = self.person_service.getByEmail(email)
        if person:
            return Response(PersonSerializer(person).data, status=status.HTTP_200_OK)
        return Response({"error": "Person not found"}, status=status.HTTP_404_NOT_FOUND)