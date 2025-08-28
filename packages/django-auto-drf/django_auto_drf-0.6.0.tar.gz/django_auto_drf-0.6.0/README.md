# 🚀 Django Auto DRF

**Automated API registration for Django Rest Framework**

Django Auto DRF is a powerful utility that **automatically registers ViewSets, Serializers, and Filters** for your
Django models. Skip the boilerplate and focus on your logic.

---

## 🌟 Features

- ✅ **Automatic API Registration**: No need to manually create ViewSets, Serializers, or Filters.
- ✅ **Multiple Endpoints per Model**: Register multiple APIs for the same model easily.
- ✅ **Custom Permissions & Pagination**: Customize permissions and pagination on each endpoint.
- ✅ **Django Admin-style Registration**: Just like `admin.site.register()` but for DRF.
- ✅ **Automatic OpenAPI Docs**: Swagger and Redoc supported out of the box.
- ✅ **Custom Extra Actions**: Add custom actions to your endpoints with decorators.
- ✅ **Autodiscovery**: Automatically imports `views.py`, `serializers.py`, and `filters.py` in each installed app.
- ✅ **Smart Defaults**: Auto-generates serializers and filtersets if not defined.
- ✅ **Config Inspection**: Retrieve registered configuration with `get_endpoint_config()`.

---

## 🚀 Installation

Install via pip:

```bash
pip install django-auto-drf
```

---

## ⚡ API Registration

### Registering Models

Use the `api_register_model()` function to register a model. You can optionally provide a custom endpoint, permissions,
pagination, and other parameters from EndpointConfig.

```python
from django_auto_drf.registry import api_register_model
from .models import Product

api_register_model(Product)
```

#### Parameters for api_register_model

The `api_register_model()` function accepts the following parameters:

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| model | Model class | The Django model to register | Required |
| endpoint | string | Custom API endpoint path | "{app_label}/{model_name}" |
| viewset_class | ViewSet class | Custom ViewSet class | Auto-generated ModelViewSet |
| serializer_class | Serializer class | Custom Serializer class | Auto-generated ModelSerializer |
| filterset_class | FilterSet class | Custom FilterSet class | Auto-generated FilterSet |
| permissions | list | List of permission classes | [] |
| paginate_by | int | Number of items per page | None |

Example with additional parameters:

```python
from rest_framework.permissions import IsAuthenticated
from django_auto_drf.registry import api_register_model
from .models import Product

api_register_model(
    Product,
    endpoint="shop/products",
    permissions=[IsAuthenticated],
    paginate_by=25
)
```

### Registering Serializers or Filters

You can register a custom serializer or filterset using the same function as a decorator:

```python
@api_register_model(Product)
class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
```

### Adding Extra Actions

Use `api_register_action()` to add custom actions to your endpoints:

```python
from django_auto_drf.registry import api_register_action


@api_register_action(Product, methods=["post"])
def publish(request, pk=None):
    ...
```

### Access Configuration

You can inspect the registered configuration with:

```python
from django_auto_drf.registry import get_endpoint_config

config = get_endpoint_config(Product)
print(config)
```

---

## 📌 Quick Start

### 1. Add to `INSTALLED_APPS`

```python
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "rest_framework",
    "django_auto_drf",
]
```

### 2. Include URLs in your project's urls.py

```python
from django.urls import include, path
from django_auto_drf.urls import get_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(get_urlpatterns())),  # Include auto-generated API URLs
]
```

You can customize the base URL for your API endpoints by:

1. Setting `DJANGO_AUTO_DRF_DEFAULT_BASE_URL` in your settings.py (defaults to "api/")
2. Passing a custom base_url to the get_urlpatterns function:

```python
# Custom base URL example
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(get_urlpatterns(base_url="custom-api/"))),
]
```

### 3. Register Models

You can register models individually:

```python
from django_auto_drf.registry import api_register_model
from .models import Product

api_register_model(Product)
```

Or automatically discover and register all models from an app:

```python
from django.apps import apps
from django_auto_drf.discovery import discovery_api_models

# Register all models from the 'myapp' app
discovery_api_models(apps.get_app_config("myapp"))
```

You can also use `discovery_api_models` in your app's `AppConfig.ready()` method to automatically register all models when the app is loaded:

```python
# In your app's apps.py file
from django.apps import AppConfig
from django_auto_drf.discovery import discovery_api_models

class MyAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'

    def ready(self):
        # Register all models from this app
        discovery_api_models(self)
```

The `discovery_api_models` function also accepts additional parameters:
- `exclude_models`: A list of model names to exclude from registration
- Additional keyword arguments that will be passed to `api_register_model` for each model

Now your API is live at:

```
GET /api/app_name/product/
POST /api/app_name/product/
PUT /api/app_name/product/{id}/
DELETE /api/app_name/product/{id}/
```

---

## 📖 Advanced Usage

### Custom Endpoint

```python
api_register_model(Product, endpoint="shop/products")
```

### Multiple Endpoints for the Same Model
```python
from rest_framework.permissions import IsAuthenticated, AllowAny


@api_register_model(Product, permissions=[IsAuthenticated])
class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()


@api_register_model(Product, endpoint="shop/products", permissions=[AllowAny])
class PublicProductViewSet(ModelViewSet):
    queryset = Product.objects.filter(is_published=True)
```

### Registering a ViewSet via Decorator (Use Case)
```python
from rest_framework.viewsets import ModelViewSet
from django_auto_drf.registry import api_register_model
from .models import Supplier


@api_register_model(Supplier)
class SupplierViewSet(ModelViewSet):
    queryset = Supplier.objects.all()
```

### Post‑registration Configuration (Use Case)
```python
from rest_framework.permissions import DjangoModelPermissions
from django_auto_drf.registry import api_register_model
from .models import ProductCategory

# Register endpoint and then adjust configuration attributes
api_register_model(ProductCategory).permissions = [DjangoModelPermissions]
```

### Custom Pagination

```python
api_register_model(Product, paginate_by=50)
```

### Add Extra Actions

```python
@api_register_model(Product)
class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        ...
```

---

## 📜 Automatic Documentation

If `DEBUG=True` and schema generation is not disabled, visit:

- Swagger UI: `http://localhost:8000/api/docs/`
- Redoc UI: `http://localhost:8000/api/redoc/`

No need to configure, it's automatic!

---

## 🎯 Why Django Auto DRF?

- ⏳ Save development time
- 📈 Scale with multiple apps and endpoints
- ✅ DRY principle in action
- ⚙️ Fully customizable but easy to get started

---

## 🔒 StrictDjangoModelPermissions (django_auto_drf.permissions)

Django REST Framework’s built-in DjangoModelPermissions intentionally does not require any model permission for “safe” methods (GET/HEAD/OPTIONS). This means that, if you use it alone, authenticated users can read data without having the model’s "view" permission. StrictDjangoModelPermissions fixes this by enforcing the view permission for safe methods.

- What it enforces
  - GET/HEAD/OPTIONS → requires "%(app_label)s.view_%(model_name)s"
  - POST → requires "add"
  - PUT/PATCH → requires "change"
  - DELETE → requires "delete"

Why it exists
- By design, DRF maps safe methods to an empty permission list in DjangoModelPermissions. Many teams want to explicitly gate read access behind Django’s view permission (introduced in Django 2.1). StrictDjangoModelPermissions provides this stricter behavior out of the box.

How to use it
- Globally (recommended)
```python
# settings.py
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": (
        "django_auto_drf.permissions.StrictDjangoModelPermissions",
    ),
}
```

- Per endpoint with django-auto-drf
```python
from django_auto_drf.registry import api_register_model
from django_auto_drf.permissions import StrictDjangoModelPermissions
from .models import ProductCategory

api_register_model(ProductCategory).permissions = [StrictDjangoModelPermissions]
```

Notes
- Ensure your users/groups are granted the relevant view/add/change/delete permissions in Django Admin (or via migrations/fixtures).
- StrictDjangoModelPermissions requires authenticated users (like DjangoModelPermissions). Combine with your authentication setup as needed.

---

## 🧾 Audit – Missing Permissions

The audit feature automatically records, for each authenticated user who receives a 403 on a DRF endpoint, which permissions are missing for the involved model. Records are visible and manageable from the Django Admin.

Key features:
- Tracks 403 responses caused by missing permissions, with hit counting and deduplicated notes.
- Automatically infers the model/permission based on the HTTP method (view/change/add/delete).
- Admin actions to: grant the permission to the user (caution!), clear notes, or add the missing permissions to a selected Group.

### Setup
1. Add the app to INSTALLED_APPS and run migrations:
```python
INSTALLED_APPS = [
    # ...
    "django_auto_drf",
    "django_auto_drf.audit",
]
```
```bash
python manage.py migrate
```

2. Set DRF’s exception handler to enable auditing on 403 responses:
```python
REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "django_auto_drf.audit.handlers.audit_exception_handler",
    # Optional but recommended: use DRF's model permissions or the Strict variant
    # "DEFAULT_PERMISSION_CLASSES": (
    #     "rest_framework.permissions.DjangoModelPermissions",
    #     # or
    #     # "django_auto_drf.permissions.StrictDjangoModelPermissions",
    # ),
}
```

3. Protect an endpoint with permissions to generate audit events (example):
```python
from rest_framework.permissions import DjangoModelPermissions
from django_auto_drf.registry import api_register_model
from .models import ProductCategory

# Protected endpoint: users without view/add/change/delete on ProductCategory
# will generate audit records when they receive 403
api_register_model(ProductCategory).permissions = [DjangoModelPermissions]
```

### How it works
- When an AUTHENTICATED user receives 403, the audit tries to identify the model from the view (queryset/serializer) and computes the required permissions based on the method:
  - GET/HEAD/OPTIONS → view
  - POST → add
  - PUT/PATCH → change
  - DELETE → delete
- For each missing permission, a record is created/updated in Admin → Audit – Missing Permissions with:
  - hits: number of occurrences
  - note: deduplicated snippet with ip, method, url, user-agent

### Django Admin
- Go to Admin → Audit – Missing Permissions.
- Available actions in the changelist:
  - "Grant this permission to the user (CAUTION)": directly assigns the permission to the selected user.
  - "Clear note": empties the note for the selected records.
  - "Add this permission to a Group…": a guided page to add the missing permissions to a chosen group.

Note: the audit ignores anonymous (unauthenticated) users and only handles 403 responses.

---

## 🔧 Settings (Optional)

| Setting                                   | Description                           | Default           |
|-------------------------------------------|---------------------------------------|-------------------|
| DJANGO_AUTO_DRF_DEFAULT_VIEWSET           | Base class for ViewSets               | `ModelViewSet`    |
| DJANGO_AUTO_DRF_DEFAULT_SERIALIZER        | Base class for Serializers            | `ModelSerializer` |
| DJANGO_AUTO_DRF_DEFAULT_FILTERSET         | Base class for FilterSets             | `FilterSet`       |
| DJANGO_AUTO_DRF_DEFAULT_BASE_URL          | Root path for APIs                    | "api/"            |
| DJANGO_AUTO_DRF_DISABLE_SCHEMA_GENERATION | Disable Swagger/Redoc when DEBUG=True | `False`           |

---

## 🛠️ Development & Contribution

1. Clone:
   ```bash
   git clone https://github.com/wolfmc3/django-auto-drf.git
   cd django-auto-drf
   ```
2. Virtual env:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
3. Install:
   ```bash
   pip install -r requirements.txt
   ```
4. Run tests:
   ```bash
   python manage.py test
   ```

---

## 🔗 Links

- 📄 [Docs](https://github.com/wolfmc3/django-auto-drf/wiki)
- ✨ [Issues](https://github.com/wolfmc3/django-auto-drf/issues)
- 🌐 [Source](https://github.com/wolfmc3/django-auto-drf)
