from rest_framework import status, viewsets
from rest_framework.response import Response

from api.company.services.ServicesCompany import ServicesCompany
from api.company.serializers.SerializerCompany import SerializerCompany
class ControllerCompany(viewsets.ViewSet):
    """
    Controller for managing Company entities.

    Provides endpoints for:
    - Creating a company.
    - Updating a company.
    - Deleting a company.
    - Retrieving all companies.
    - Retrieving a company by ID.
    - Retrieving a company by name.
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.company_service = ServicesCompany()
        
    def create(self, request):
        """
        Create a new company.

        Expects:
        - A JSON body with company details.

        Returns:
        - 201 Created: If the company is successfully created.
        - 400 Bad Request: If the request contains invalid data.
        """
        serializer = SerializerCompany(data=request.data)
        if serializer.is_valid():
            company = self.company_service.create(serializer.validated_data)  
            return Response(SerializerCompany(company).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, pk=None):
        """
        Update an existing company.

        Expects:
        - A JSON body with updated company details.

        Returns:
        - 200 OK: If the company is successfully updated.
        - 400 Bad Request: If the request contains invalid data.
        - 404 Not Found: If the company does not exist.
        """
        serializer = SerializerCompany(data=request.data)
        if serializer.is_valid():
            try:
                company = self.company_service.update_company(pk, serializer.validated_data)  
                return Response(SerializerCompany(company).data, status=status.HTTP_200_OK)
            except ValueError:
                return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk=None):
        """
        Delete a company.

        Expects:
        - A company ID in the URL.

        Returns:
        - 204 No Content: If the company is successfully deleted.
        - 404 Not Found: If the company does not exist.
        """
        try:
            self.company_service.delete_company(pk)  
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValueError:
            return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)
        
    def list(self, request):
        """
        Retrieve all companies.

        Returns:
        - 200 OK: A list of all companies.
        """
        companies = self.company_service.get_all_companies()  
        return Response(SerializerCompany(companies, many=True).data, status=status.HTTP_200_OK)
    
    def retrieve(self, request, pk=None):
        """
        Retrieve a company by ID.

        Expects:
        - A company ID in the URL.

        Returns:
        - 200 OK: The requested company.
        - 404 Not Found: If the company does not exist.
        """
        try:
            company = self.company_service.get_company_by_id(pk)  
            return Response(SerializerCompany(company).data, status=status.HTTP_200_OK)
        except ValueError:
            return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)
        
    def retrieve_by_name(self, request, name=None):
        """
        Retrieve a company by name.

        Expects:
        - A company name in the URL.

        Returns:
        - 200 OK: The requested company.
        - 404 Not Found: If the company does not exist.
        """
        try:
            company = self.company_service.get_company_by_name(name)  
            return Response(SerializerCompany(company).data, status=status.HTTP_200_OK)
        except ValueError:
            return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)