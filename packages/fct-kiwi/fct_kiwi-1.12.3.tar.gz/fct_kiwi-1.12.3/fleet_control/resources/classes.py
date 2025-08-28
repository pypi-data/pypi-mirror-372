# type: ignore
import balena.types.models
import fleet_control.logging_config # Ensure logging is configured
from fleet_control.utils.utils import get_device_variables, get_fleet_variables, handle_request_error, balena_sdk

def create_target(target_obj):
    """Factory function to create the appropriate target class."""
    if target_obj.get("device_name"):
        return Device(target_obj)
    else:
        return Application(target_obj)


class Device:
    """Class for handling operations on a device target."""

    def __init__(self, device: balena.types.models.TypeDevice):
        for k, v in device.items():
            setattr(self, k, v)
        self.device = device

    @handle_request_error()
    def get_variables(self, custom=False):
        """Get environment and service variables for the device."""
        return get_device_variables(self.device, custom_only=custom)

    @handle_request_error()
    def set_env_var(self, var_name: str, value: str) -> None:
        """Set an environment variable on the device."""
        balena_sdk.models.device.env_var.set(self.id, var_name, str(value))

    @handle_request_error()
    def set_service_var(self, service: int, var_name: str, value: str) -> None:
        """Set a service variable on the device."""
        balena_sdk.models.device.service_var.set(self.id, service, var_name, str(value))

    @handle_request_error()
    def remove_env_var(self, var_name: str) -> None:
        """Remove an environment variable from the device."""
        balena_sdk.models.device.env_var.remove(self.id, var_name)

    @handle_request_error()
    def remove_service_var(self, service: int, var_name: str) -> None:
        """Remove a service variable from the device."""
        balena_sdk.models.device.service_var.remove(self.id, service, var_name)

    def get_identifier(self) -> str:
        """Get a string identifier for the device."""
        return f"device {self.device_name}"


class Application:
    """Class for handling operations on an application target."""

    def __init__(self, application: balena.types.models.TypeApplication):
        for k, v in application.items():
            setattr(self, k, v)

    @handle_request_error()
    def get_variables(self, custom=False):
        """Get environment and service variables for the application."""
        return get_fleet_variables(self.id)

    @handle_request_error()
    def set_env_var(self, var_name: str, value: str) -> None:
        """Set an environment variable on the application."""
        balena_sdk.models.application.env_var.set(self.id, var_name, str(value))

    @handle_request_error()
    def set_service_var(self, service: int, var_name: str, value: str) -> None:
        """Set a service variable on the application."""
        balena_sdk.models.service.var.set(service, var_name, str(value))

    @handle_request_error()
    def remove_env_var(self, var_name: str) -> None:
        """Remove an environment variable from the application."""
        balena_sdk.models.application.env_var.remove(self.id, var_name)

    @handle_request_error()
    def remove_service_var(self, service: int, var_name: str) -> None:
        """Remove a service variable from the application."""
        balena_sdk.models.service.var.remove(service, var_name)

    def get_identifier(self) -> str:
        """Get a string identifier for the application."""
        return f"application {self.app_name}"


class Service:
    pass
