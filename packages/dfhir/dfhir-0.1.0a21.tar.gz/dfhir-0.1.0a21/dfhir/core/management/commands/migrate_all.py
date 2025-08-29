"""custom migrate command to reload all models."""

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db.migrations.state import ProjectState

# Save original methods in case you need fallback
original_reload_model = ProjectState.reload_model
original_reload_models = ProjectState.reload_models


def custom_reload_model(self, app_label, model_name, delay=False):
    """Custom reload model method to reload a single model."""
    if "apps" in self.__dict__:  # hasattr would cache the property
        self._reload(set([(app_label, model_name)]))


def custom_reload_models(self, models, delay=True):
    """Custom reload models method to reload multiple models."""
    if "apps" in self.__dict__:  # hasattr would cache the property
        related_models = set(self.models.keys()) if models is None else set()
        for app_label, model_name in models:
            related_models.update(self._find_reload_model(app_label, model_name, delay))
        self._reload(related_models)


# Apply monkey patches
ProjectState.reload_model = custom_reload_model
ProjectState.reload_models = custom_reload_models


class Command(BaseCommand):
    """Custom command to reload all models in the project."""

    help = "Prints 'hi' to the console"

    def handle(self, *args, **kwargs):
        """Handle method to execute the command."""
        # Call the custom command
        call_command("migrate", *args, **kwargs)
