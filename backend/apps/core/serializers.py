from rest_framework import serializers
from .models import Technology, ProjectTemplate

class TechnologySerializer(serializers.ModelSerializer):
    class Meta:
        model = Technology
        fields = ['id', 'name', 'description', 'type']

class ProjectTemplateSerializer(serializers.ModelSerializer):
    backend_technology = TechnologySerializer(read_only=True)
    frontend_technology = TechnologySerializer(read_only=True)

    class Meta:
        model = ProjectTemplate
        fields = ['id', 'name', 'description', 'backend_technology', 'frontend_technology']