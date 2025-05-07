from rest_framework import serializers
from api.job.models.Job import Job

class SerializerJob(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ['id', 'name']
