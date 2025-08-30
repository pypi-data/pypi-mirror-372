# 🚀 Django Auto DRF

Automated API registration for Django Rest Framework.

Django Auto DRF automatically registers ViewSets, Serializers, and Filters for your Django models so you can skip boilerplate and focus on your logic.

[Docs](./docs/index.md) · [Getting started](./docs/getting-started.md) · [Configuration](./docs/configuration.md) · [Versioning](./docs/versioning.md) · [TS generator](./docs/generate-ts-models.md) · [API Reference](./docs/api-reference.md) · [FAQ](./docs/faq.md)

---

## Quick install

```bash
pip install django-auto-drf
```

Minimal setup (urls.py):
```python
from django.urls import include, path
from django_auto_drf.urls import get_urlpatterns

urlpatterns = [
    path('', include(get_urlpatterns())),
]
```


---

## Compatibility

| Python | Django | DRF |
|-------:|-------:|----:|
| 3.10+  | 4.2+   | 3.14+ |

---

## Why

- Save time: automatic endpoints per model
- Stay flexible: override serializers, viewsets, filters, permissions, pagination
- Great DX: automatic OpenAPI docs; optional numeric API versioning

---

## More

- Changelog: [CHANGELOG.md](./CHANGELOG.md)
- Contributing: [CONTRIBUTING.md](./CONTRIBUTING.md)
- Source: https://github.com/wolfmc3/django-auto-drf

<details>
<summary>Optional: Notes about schema endpoints and auth</summary>

- Schema endpoints (Swagger/Redoc) can be disabled via `DJANGO_AUTO_DRF_DISABLE_SCHEMA_GENERATION`.
- Auth endpoints are provided unversioned at `/api/auth/login|logout|me/`.

</details>

For full examples and advanced usage, see the documentation:
- Getting started: ./docs/getting-started.md
- API Reference: ./docs/api-reference.md
