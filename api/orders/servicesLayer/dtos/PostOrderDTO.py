from rest_framework import serializers
from api.orders.model.Order import Order, StatesUSA
from api.job.model.job import Job
from api.person.model.Person import Person
import uuid

def validate_job(job_value: str) -> uuid.UUID:
    """
    Transform a job value (like 'c' or 'p') into the corresponding id_job.
    """
    try:
        # Find the Job that matches the name value
        job = Job.objects.get(name=job_value)
        return job.id_job  # Return the id_job (UUID)
    except Job.DoesNotExist:
        raise serializers.ValidationError(f"Invalid job value: {job_value}")
    
class PostOrderDTO(serializers.Serializer):
    date = serializers.DateField()
    key_ref = serializers.CharField(max_length=50)
    name = serializers.CharField(max_length=100)  
    last_name = serializers.CharField(max_length=100)  
    address = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    weight = serializers.DecimalField(max_digits=10, decimal_places=2)
    state_usa = serializers.ChoiceField(choices=StatesUSA.choices)
    job = serializers.CharField()  # Changed to CharField to accept the value as a string

    def to_internal_value(self, data):
        """
        Transform the job value (like 'c' or 'p') into the corresponding id_job.
        """
        internal_data = super().to_internal_value(data)
        job_value = internal_data.get('job')

        # Validate and transform the job value
        internal_data['job'] = validate_job(job_value)

        return internal_data

    @classmethod
    def from_model(cls, order: Order):
        """ Convert a model instance to a DTO """
        return cls({
            "date": order.date,
            "key_ref": order.key_ref,
            "name": order.id_person.first_name,  
            "last_name": order.id_person.last_name,  
            "address": order.id_person.address,
            "email": order.id_person.email,
            "weight": order.weight,
            "state_usa": order.state_usa,
            "job": order.id_job.name,  # Use the job name (like 'c' or 'p')
        })