from django.db import models
from django.contrib.auth.models import User


class AuditModel(models.Model):
    """
    Abstract base model for audit fields
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name="%(class)s_created"
    )
    updated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name="%(class)s_updated"
    )

    class Meta:
        abstract = True
