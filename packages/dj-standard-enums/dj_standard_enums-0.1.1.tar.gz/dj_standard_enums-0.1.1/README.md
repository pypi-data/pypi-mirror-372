# dj_standard_enums

A standard way to define, register, and expose enums in Django. This package provides:

- A simple, consistent pattern to define enums once in your Django backend.
- A registry to look them up by name.
- A REST API endpoint to expose enum values to your Front End (React, Vue, etc.), reducing duplication of constants between BE and FE.

In short, this package aims to establish a standard way to use enums in Django and expose them via API so that they can be used in the Front End, thereby reducing code duplication.

## Installation

This package is published as `dj_standard_enums` on PyPI.

- One-time install with pip:

```bash
pip install dj_standard_enums
```

- Pin it in your project's requirements.txt:

```
dj_standard_enums>=0.0.2
```

The package depends on Django and Django REST Framework, which will be installed automatically if not already present.

## Quickstart

1. Add the app to INSTALLED_APPS

In your Django settings (e.g., `settings.py`):

```python
INSTALLED_APPS = [
    # ... your apps ...
    "rest_framework",  # if not already included
    "enums",           # provided by dj_standard_enums
]
```

2. Include the enums URLs

In your project-level `urls.py`:

```python
from django.urls import include, re_path

urlpatterns = [
    # ... other urls ...
    re_path(r"", include("enums.urls")),
]
```

This will make the enums API available at the route defined by the package, for example:

- GET `/api/v1/enums/<EnumClassName>`

Where `<EnumClassName>` is the name used to register your enum in the registry.

## How it works

- The package defines an API view and URL pattern in `enums/urls.py` that serves enums by class name.
- The endpoint: `^api/v1/enums/(?P<enum_class_name>[0-9a-zA-Z\-]+)$` maps to a view that queries the internal registry and returns the enum representation as JSON.
- You can then fetch enums in your Front End and avoid duplicating constant lists.

## Defining and exposing your enums

At a high level, you define enums using the package's framework and register them so they can be retrieved by the API. A typical flow is:

- Create an enum subclass using the provided base classes in `enums.framework`.
- Ensure your enum is registered with the `SystemEnumRegistry` so it can be fetched by name.
- In order to register your enum, add your Enum class's dotted path in your django settings.py file in the STANDARD_ENUMS_REGISTRY setting.
- Access it in FE via the API endpoint: `/api/v1/enums/<EnumClassName>`.

Example response shape (simplified):

```json
[
  {"value": "ACTIVE", "label": "Active"},
  {"value": "INACTIVE", "label": "Inactive"}
]
```

Notes:
- The package ships a `RetrieveEnumAPIView` that returns a full representation via `get_full_representation()` defined on your enum classes.
- Authentication is disabled by default on this view; you can wrap it with your own project-level auth or gate it via URL configuration if needed.

## Why use this package?

- Single source of truth for enums shared across BE/FE.
- Standardized registry and retrieval pattern.
- Fewer bugs and less drift between backend choices and frontend constants.

## Requirements

- Python 3.8+
- Django 3.2+ (tested up to Django 5.x)
- Django REST Framework
