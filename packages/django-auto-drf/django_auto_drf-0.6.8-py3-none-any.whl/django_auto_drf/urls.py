def get_urlpatterns(base_url=None):
    from django.urls import include, path

    from django_auto_drf.auto_register import api_router_urls
    from django_auto_drf.settings import DJANGO_AUTO_DRF_DEFAULT_BASE_URL, DJANGO_AUTO_DRF_DISABLE_SCHEMA_GENERATION, \
        AUTO_DRF_VERSIONS
    from django_auto_drf.views import MeView, LoginView, LogoutView

    # small wrapper to normalize kwargs keys for Spectacular schema views
    def _norm_schema_view(as_view_callable):
        view = as_view_callable
        def wrapper(request, *args, **kwargs):
            # normalize incoming kwargs from URL resolver
            try:
                kwargs = {str(k): v for k, v in (kwargs or {}).items()}
            except Exception:
                kwargs = {}
            # also normalize request.resolver_match.kwargs if present
            try:
                rm = getattr(request, 'resolver_match', None)
                if rm is not None and isinstance(getattr(rm, 'kwargs', None), dict):
                    rm.kwargs = {str(k): v for k, v in rm.kwargs.items()}
            except Exception:
                pass
            # normalize the underlying view.kwargs as well (Spectacular stores api_version here)
            try:
                if hasattr(view, 'kwargs') and isinstance(view.kwargs, dict):
                    view.kwargs = {str(k): v for k, v in view.kwargs.items()}
            except Exception:
                pass
            return view(request, *args, **kwargs)
        return wrapper

    baseurl = base_url or DJANGO_AUTO_DRF_DEFAULT_BASE_URL
    # normalize base url like "api/" (no leading slash, with trailing)
    if not baseurl.endswith("/"):
        baseurl += "/"
    if baseurl.startswith("/"):
        baseurl = baseurl[1:]

    # Build nested patterns under baseurl using include, avoiding full concatenated paths
    base_patterns = []

    # REST auth endpoints (not versioned)
    base_patterns += [
        path("auth/login/", LoginView.as_view(), name="auth-login"),
        path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
        path("auth/me/", MeView.as_view(), name="auth-me"),
    ]

    # API router endpoints
    if AUTO_DRF_VERSIONS is None:
        base_patterns.append(path("", include(api_router_urls())))
    else:
        # Versioned URLs: /<base>/v{k}/<endpoint>/
        for k in AUTO_DRF_VERSIONS:
            base_patterns.append(path(f"v{k}/", include(api_router_urls(version=k))))

    # Schema/docs endpoints
    if not DJANGO_AUTO_DRF_DISABLE_SCHEMA_GENERATION:
        from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
        from drf_spectacular.renderers import OpenApiJsonRenderer

        if AUTO_DRF_VERSIONS is None:
            base_patterns += [
                path("schema/", _norm_schema_view(SpectacularAPIView.as_view()), name="schema"),
                path("schema.json", _norm_schema_view(SpectacularAPIView.as_view(renderer_classes=[OpenApiJsonRenderer])),
                     name="schema-json"),
                path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
                path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
            ]
        else:
            # Versioned schema endpoints nested under base
            for k in AUTO_DRF_VERSIONS:
                name_prefix = f"schema-v{k}"
                base_patterns += [
                    path(f"schema/v{k}/", _norm_schema_view(SpectacularAPIView.as_view(api_version=str(k))), name=name_prefix),
                    path(f"schema/v{k}.json",
                         _norm_schema_view(SpectacularAPIView.as_view(api_version=str(k), renderer_classes=[OpenApiJsonRenderer])),
                         name=f"{name_prefix}-json"),
                    path(f"docs/v{k}/",
                         SpectacularSwaggerView.as_view(url_name=name_prefix),
                         name=f"swagger-ui-v{k}"),
                    path(f"redoc/v{k}/",
                         SpectacularRedocView.as_view(url_name=name_prefix),
                         name=f"redoc-v{k}"),
                ]

    # Finally, mount everything under the baseurl via include to avoid full paths
    urlpatterns = [path(baseurl, include((base_patterns, 'django_auto_drf'), namespace=None))]

    return urlpatterns
