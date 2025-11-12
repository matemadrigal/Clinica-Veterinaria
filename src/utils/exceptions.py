"""
Excepciones personalizadas para la aplicación.
"""


class ClinicaVeterinariaException(Exception):
    """Excepción base para la aplicación"""
    pass


class ValidationError(ClinicaVeterinariaException):
    """Error de validación de datos"""
    pass


class NotFoundError(ClinicaVeterinariaException):
    """Entidad no encontrada"""
    pass


class DuplicateError(ClinicaVeterinariaException):
    """Entidad duplicada"""
    pass


class BusinessRuleError(ClinicaVeterinariaException):
    """Violación de regla de negocio"""
    pass


class CitaSolapeError(BusinessRuleError):
    """Error de solape de citas"""
    pass
