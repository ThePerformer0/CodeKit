from django.shortcuts import render

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Technology, ProjectTemplate
from .serializers import TechnologySerializer, ProjectTemplateSerializer
import os
import shutil 
from django.conf import settings
import secrets
import string

class TechnologyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Technology.objects.all().order_by('name')
    serializer_class = TechnologySerializer

class ProjectTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProjectTemplate.objects.all().order_by('name')
    serializer_class = ProjectTemplateSerializer

def generate_django_secret_key():
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(chars) for i in range(50))

class ProjectGenerateAPIView(APIView):
    """
    API endpoint to generate a project based on a project template.
    """
    def post(self, request, *args, **kwargs):
        project_template_id = request.data.get('project_template_id')
        project_name = request.data.get('project_name', 'my-codekit-project')

        if not project_template_id:
            return Response(
                {"error": "project_template_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not project_name or not project_name.strip():
            return Response(
                {"error": "project_name cannot be empty."},
                status=status.HTTP_400_BAD_REQUEST
            )
        project_name = project_name.strip().replace(' ', '_').lower()

        try:
            project_template = ProjectTemplate.objects.get(id=project_template_id)
        except ProjectTemplate.DoesNotExist:
            return Response(
                {"error": "Project template not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        generated_projects_dir = settings.BASE_DIR.parent / 'generated_projects'
        if not generated_projects_dir.exists():
            generated_projects_dir.mkdir()

        final_project_path = generated_projects_dir / project_name

        if final_project_path.exists():
            return Response(
                {"error": f"Project directory '{project_name}' already exists. Please choose a different name or remove the existing one."},
                status=status.HTTP_409_CONFLICT
            )

        try:
            project_templates_root = settings.BASE_DIR.parent / 'project_templates_base'
            backend_base_path = project_templates_root / 'django_base'
            frontend_base_path = project_templates_root / 'react_base'

            if project_template.backend_technology and project_template.backend_technology.name == 'Django':
                shutil.copytree(backend_base_path, final_project_path)
                django_internal_project_path = final_project_path / 'project_name'
                if django_internal_project_path.exists():
                    os.rename(django_internal_project_path, final_project_path / project_name)

                # Mettre à jour manage.py pour qu'il pointe vers le bon dossier de settings
                manage_py_path = final_project_path / 'manage.py'
                with open(manage_py_path, 'r') as f:
                    content = f.read()
                content = content.replace("os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_name.settings')",
                                          f"os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{project_name}.settings')")
                with open(manage_py_path, 'w') as f:
                    f.write(content)

                # Création du fichier .env pour Django
                env_content_django = f"SECRET_KEY='{generate_django_secret_key()}'\n"
                env_content_django += "DEBUG=True\n"
                env_content_django += "ALLOWED_HOSTS='*'\n"
                env_content_django += "# DATABASE_URL=sqlite:///db.sqlite3\n" # Exemple pour une BDD externe plus tard
                env_content_django += "\n# Ajoutez vos variables d'environnement Django ici\n"

                with open(final_project_path / '.env', 'w') as f:
                    f.write(env_content_django)

            if project_template.frontend_technology and project_template.frontend_technology.name == 'React':
                frontend_target_path = final_project_path
                if project_template.backend_technology: # Si fullstack, copier dans un sous-dossier
                    frontend_target_path = final_project_path / 'frontend'
                    os.makedirs(frontend_target_path, exist_ok=True) # S'assurer que le dossier parent existe

                shutil.copytree(frontend_base_path, frontend_target_path, dirs_exist_ok=True)

                # Création du fichier .env pour React
                # Les variables React doivent commencer par REACT_APP_
                env_content_react = f"REACT_APP_PROJECT_NAME='{project_name}'\n"
                if project_template.backend_technology:
                    env_content_react += "REACT_APP_API_URL='http://localhost:8000/api/'\n" # Exemple pour fullstack
                env_content_react += "\n# Ajoutez vos variables d'environnement React ici\n"

                with open(frontend_target_path / '.env', 'w') as f:
                    f.write(env_content_react)

            if not project_template.backend_technology and not project_template.frontend_technology:
                 return Response(
                    {"error": "Project template must specify at least one technology (Backend or Frontend)."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            readme_path = final_project_path / 'README.md'
            if not readme_path.exists(): # Ne recrée pas si déjà copié avec le template React
                readme_content = f"# {project_name}\n\n"
                readme_content += "Ce projet a été généré par Codekit.\n\n"
                if project_template.backend_technology:
                    readme_content += f"**Backend:** {project_template.backend_technology.name}\n"
                if project_template.frontend_technology:
                    readme_content += f"**Frontend:** {project_template.frontend_technology.name}\n"
                with open(readme_path, 'w') as f:
                    f.write(readme_content)

            return Response(
                {"message": f"Project '{project_name}' generated successfully at {final_project_path}", "project_path": str(final_project_path)},
                status=status.HTTP_200_OK
            )
        except shutil.Error as e:
            if final_project_path.exists():
                shutil.rmtree(final_project_path)
            return Response(
                {"error": f"Failed to generate project due to file operations: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            if final_project_path.exists():
                shutil.rmtree(final_project_path)
            return Response(
                {"error": f"An unexpected error occurred during project generation: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )