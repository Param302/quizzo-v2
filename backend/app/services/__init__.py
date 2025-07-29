# Services package
# Import functions only, not classes to avoid initialization issues

def get_report_generator():
    from .report_generator import get_report_generator
    return get_report_generator()


def get_email_service():
    from .email_service import get_email_service
    return get_email_service()


def get_certificate_generator():
    from .certificate_generator import get_certificate_generator
    return get_certificate_generator()


__all__ = [
    'get_report_generator',
    'get_email_service',
    'get_certificate_generator'
]
