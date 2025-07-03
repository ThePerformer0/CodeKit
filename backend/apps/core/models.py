from django.db import models

class Technology(models.Model):
    class TypeChoices(models.TextChoices):
        FRONTEND = 'frontend', 'Frontend'
        BACKEND = 'backend', 'Backend'
        DATABASE = 'database', 'Database'
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    type = models.CharField(
        max_length=10,
        choices=TypeChoices.choices,
        default=TypeChoices.BACKEND # valeur par défaut
    )

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"
    

class ProjectTemplate(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    backend_technology = models.ForeignKey(
        Technology,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='backend_templates',
        limit_choices_to={'type': Technology.TypeChoices.BACKEND}
    )

    frontend_technology = models.ForeignKey(
        Technology,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='frontend_templates',
        limit_choices_to={'type': Technology.TypeChoices.FRONTEND}
    )

    def __str__(self):
        return self.name
