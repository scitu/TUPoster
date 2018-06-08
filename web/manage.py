#!/usr/bin/env python
import os
import sys
_DEV_STATE = 'dev'
if __name__ == "__main__":
    state = os.environ.setdefault("STATE", _DEV_STATE)
    if state == _DEV_STATE:
        os.environ["DJANGO_SETTINGS_MODULE"] = "web.settings.dev"
    elif state == 'production':
        os.environ["DJANGO_SETTINGS_MODULE"] = "web.settings.production"

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
