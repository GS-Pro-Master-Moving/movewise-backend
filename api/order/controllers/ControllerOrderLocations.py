import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

class OrderLocationController(APIView):
    authentication_classes = []  # null 
    permission_classes = [AllowAny]  # no token
    
    # URLs de la API CountryNow
    COUNTRIES_URL = "https://countriesnow.space/api/v0.1/countries"
    STATES_URL = "https://countriesnow.space/api/v0.1/countries/states"
    CITIES_URL = "https://countriesnow.space/api/v0.1/countries/state/cities"
    
    def get(self, request, *args, **kwargs):
        """
        Endpoint para obtener países, estados o ciudades
        Parámetros de consulta:
        - type: 'countries', 'states', 'cities'
        - country: nombre del país (requerido para states y cities)
        - state: nombre del estado (requerido para cities)
        """
        try:
            request_type = request.GET.get('type', 'countries')
            country = request.GET.get('country')
            state = request.GET.get('state')
            
            if request_type == 'countries':
                return self._get_countries()
            elif request_type == 'states':
                if not country:
                    return Response({
                        "status": "error",
                        "messDev": "Country parameter is required for states",
                        "messUser": "País requerido para obtener estados",
                        "data": None
                    }, status=400)
                return self._get_states(country)
            elif request_type == 'cities':
                if not country or not state:
                    return Response({
                        "status": "error",
                        "messDev": "Country and state parameters are required for cities",
                        "messUser": "País y estado requeridos para obtener ciudades",
                        "data": None
                    }, status=400)
                return self._get_cities(country, state)
            else:
                return Response({
                    "status": "error",
                    "messDev": f"Invalid type parameter: {request_type}",
                    "messUser": "Tipo de consulta inválido",
                    "data": None
                }, status=400)
                
        except Exception as e:
            logger.error(f"Error in OrderLocationController: {str(e)}")
            return Response({
                "status": "error",
                "messDev": f"Unexpected error: {str(e)}",
                "messUser": "Error interno del servidor",
                "data": None
            }, status=500)
    
    def _get_countries(self):
        """Obtiene la lista de países"""
        cache_key = "countries_list"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response({
                "status": "success",
                "data": cached_data,
                "message": "Countries retrieved successfully"
            })
        
        try:
            response = requests.get(self.COUNTRIES_URL, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('error'):
                raise Exception(data.get('msg', 'API Error'))
            
            countries = [
                {
                    'code': country.get('iso2', ''),
                    'name': country.get('country', ''),
                    'iso3': country.get('iso3', '')
                }
                for country in data.get('data', [])
            ]
            
            # Ordenar por nombre
            countries.sort(key=lambda x: x['name'])
            
            # Cache por 24 horas
            cache.set(cache_key, countries, 86400)
            
            return Response({
                "status": "success",
                "data": countries,
                "message": "Countries retrieved successfully"
            })
            
        except requests.RequestException as e:
            logger.error(f"Request error getting countries: {str(e)}")
            return Response({
                "status": "error",
                "messDev": f"API request failed: {str(e)}",
                "messUser": "Error al conectar con el servicio de países",
                "data": None
            }, status=503)
    
    def _get_states(self, country):
        """Obtiene los estados de un país específico"""
        cache_key = f"states_{country.lower()}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response({
                "status": "success",
                "data": cached_data,
                "message": f"States for {country} retrieved successfully"
            })
        
        try:
            payload = {"country": country}
            response = requests.post(self.STATES_URL, json=payload, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('error'):
                raise Exception(data.get('msg', 'API Error'))
            
            states_data = data.get('data', {})
            states = [
                {
                    'name': state.get('name', ''),
                    'state_code': state.get('state_code', '')
                }
                for state in states_data.get('states', [])
            ]
            
            # Ordenar por nombre
            states.sort(key=lambda x: x['name'])
            
            # Cache por 12 horas
            cache.set(cache_key, states, 43200)
            
            return Response({
                "status": "success",
                "data": states,
                "message": f"States for {country} retrieved successfully"
            })
            
        except requests.RequestException as e:
            logger.error(f"Request error getting states for {country}: {str(e)}")
            return Response({
                "status": "error",
                "messDev": f"API request failed: {str(e)}",
                "messUser": f"Error al obtener estados de {country}",
                "data": None
            }, status=503)
    
    def _get_cities(self, country, state):
        """Obtiene las ciudades de un estado específico"""
        cache_key = f"cities_{country.lower()}_{state.lower()}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response({
                "status": "success",
                "data": cached_data,
                "message": f"Cities for {state}, {country} retrieved successfully"
            })
        
        try:
            payload = {"country": country, "state": state}
            response = requests.post(self.CITIES_URL, json=payload, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('error'):
                raise Exception(data.get('msg', 'API Error'))
            
            cities = [
                {"name": city}
                for city in data.get('data', [])
            ]
            
            # Ordenar por nombre
            cities.sort(key=lambda x: x['name'])
            
            # Cache por 6 horas
            cache.set(cache_key, cities, 21600)
            
            return Response({
                "status": "success",
                "data": cities,
                "message": f"Cities for {state}, {country} retrieved successfully"
            })
            
        except requests.RequestException as e:
            logger.error(f"Request error getting cities for {state}, {country}: {str(e)}")
            return Response({
                "status": "error",
                "messDev": f"API request failed: {str(e)}",
                "messUser": f"Error al obtener ciudades de {state}, {country}",
                "data": None
            }, status=503)