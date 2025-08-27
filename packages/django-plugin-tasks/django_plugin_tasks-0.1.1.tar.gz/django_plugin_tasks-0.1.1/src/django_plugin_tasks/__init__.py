import djp


@djp.hookimpl
def installed_apps():
    return [
        "django_tasks",
        "django_tasks.backends.database",
    ]


@djp.hookimpl
def settings(current_settings: dict):
    current_settings.setdefault("TASKS", {})["default"] = {
        "BACKEND": "django_tasks.backends.database.DatabaseBackend"
    }
