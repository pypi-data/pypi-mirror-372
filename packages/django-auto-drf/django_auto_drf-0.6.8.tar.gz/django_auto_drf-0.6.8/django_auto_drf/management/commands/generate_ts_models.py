import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from django.core.management.base import BaseCommand, CommandError
from django.utils.text import capfirst
from django.apps import apps

from django_auto_drf.registry import get_versioned_registry
from django_auto_drf.core import EndpointConfig


DJANGO_TO_TS_TYPE = {
    'CharField': 'string',
    'TextField': 'string',
    'EmailField': 'string',
    'SlugField': 'string',
    'URLField': 'string',
    'UUIDField': 'string',
    'BooleanField': 'boolean',
    'NullBooleanField': 'boolean',
    'IntegerField': 'number',
    'BigIntegerField': 'number',
    'SmallIntegerField': 'number',
    'PositiveIntegerField': 'number',
    'PositiveSmallIntegerField': 'number',
    'FloatField': 'number',
    'DecimalField': 'number',
    'DurationField': 'number',  # seconds
    'DateField': 'string',  # ISO date
    'DateTimeField': 'string',  # ISO datetime
    'TimeField': 'string',
    'JSONField': 'any',
}

DJANGO_TO_FIELD_UI = {
    'EmailField': 'email',
    'BooleanField': 'boolean',
    'NullBooleanField': 'boolean',
    'IntegerField': 'number',
    'BigIntegerField': 'number',
    'SmallIntegerField': 'number',
    'PositiveIntegerField': 'number',
    'PositiveSmallIntegerField': 'number',
    'FloatField': 'number',
    'DecimalField': 'number',
    'DateField': 'date',
    'DateTimeField': 'datetime',
    'TimeField': 'time',
    'JSONField': 'json',
}


class Command(BaseCommand):
    help = (
        "Generate minimal TypeScript types (Read, CreatePayload, UpdatePayload) and API metadata strictly from DRF "
        "(Serializer + ViewSet/Router + DRF settings) for resources registered in django-auto-drf registry."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--output', '-o',
            dest='output',
            required=True,
            help='Base output directory where model folders will be created.'
        )
        parser.add_argument(
            '--json',
            dest='dump_json',
            action='store_true',
            help='Also write a JSON file with the generated schema per model.'
        )
        parser.add_argument(
            '--api-version', '-V',
            dest='version',
            type=int,
            help='When API versioning is enabled (AUTO_DRF_VERSIONS), you MUST provide the target API version to generate for.'
        )

    def handle(self, *args, **options):
        output_dir = Path(options['output']).resolve()
        dump_json = options['dump_json']
        from django_auto_drf.settings import AUTO_DRF_VERSIONS
        version_opt = options.get('version')
        # If versioning is enabled, require --version and validate it
        if AUTO_DRF_VERSIONS is not None:
            if version_opt is None:
                raise CommandError('When AUTO_DRF_VERSIONS is enabled, you must pass --api-version to generate_ts_models')
            if version_opt not in AUTO_DRF_VERSIONS:
                raise CommandError(f"Invalid --api-version={version_opt}. Must be one of AUTO_DRF_VERSIONS={AUTO_DRF_VERSIONS}")
        else:
            # When versioning is OFF, ignore any provided version (allowed but unused)
            version_opt = None

        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        # Ensure registry is populated (apps are ready). In most setups, importing apps that
        # call api_register_model occurs during app import time. Here we just ensure Django apps are ready.
        _ = apps.get_app_configs()

        reg = get_versioned_registry()
        if not reg:
            raise CommandError(
                'django-auto-drf registry is empty. Make sure your apps call api_register_model() '
                'and that they are loaded (e.g., via AppConfig.ready or module import).'
            )

        # Clean per-app output subfolders once before generating files
        cleaned_apps = set()
        # Keep track of app -> [ModelName, ...] for registrar generation
        self._app_models: Dict[str, List[str]] = {}

        for endpoint, ve in reg.items():
            config = ve.segments[0] if getattr(ve, 'segments', None) else None
            if not isinstance(config, EndpointConfig):
                continue
            model = config.get_model_object()
            app_label = model._meta.app_label
            if app_label not in cleaned_apps:
                app_dir = output_dir / app_label
                self._prepare_app_dirs(app_dir)
                cleaned_apps.add(app_label)
            # generate per-model artifacts
            self._generate_for_model(config, endpoint, output_dir, dump_json)
            # collect for app registrars
            self._app_models.setdefault(app_label, []).append(model.__name__)

        # After all models processed, write per-app registrar index and global aggregator
        for app_label, model_names in sorted(self._app_models.items()):
            self._write_app_registrar_index(output_dir / app_label, app_label, model_names)
        # Global aggregator file (optional)
        if cleaned_apps:
            self._write_apps_aggregator(output_dir, sorted(cleaned_apps))

        self.stdout.write(self.style.SUCCESS('TypeScript models generated successfully.'))
        # Also print the absolute output directory used (per requirement)
        self.stdout.write(f"Output directory: {str(output_dir)}")

    # === generation helpers ===

    def _generate_for_model(self, config: EndpointConfig, endpoint: str, base_dir: Path, dump_json: bool):
        # Get DRF ViewSet and Serializer from config (auto-provided if missing)
        viewset_cls = config.get_viewset()
        serializer_cls = viewset_cls.serializer_class

        model = config.get_model_object()
        model_name = model.__name__
        app_label = model._meta.app_label
        file_stem = model_name.lower()

        # Create application folder and sub-folders (types, meta)
        app_dir = base_dir / app_label
        types_dir = app_dir / 'types'
        meta_dir = app_dir / 'meta'
        types_dir.mkdir(parents=True, exist_ok=True)
        meta_dir.mkdir(parents=True, exist_ok=True)

        types_path = types_dir / f'{file_stem}.ts'
        meta_ts_path = meta_dir / f'{file_stem}.ts'
        meta_json_path = meta_dir / f'{file_stem}.json'

        resource = self._build_resource(serializer_cls, viewset_cls, endpoint, app_label, model_name)

        # Write types file (Read/CreatePayload/UpdatePayload)
        types_code = self._render_ts_types(resource)
        types_path.write_text(types_code, encoding='utf-8')

        # Write metadata files
        meta_ts_code = self._render_meta_ts(resource)
        meta_ts_path.write_text(meta_ts_code, encoding='utf-8')
        if dump_json:
            meta_payload = self._make_meta_payload(resource)
            meta_json_path.write_text(json.dumps(meta_payload, indent=2, ensure_ascii=False), encoding='utf-8')

        # Write per-model registrar file (index.<model>.ts)
        registrar_code = self._render_model_registrar_ts(resource)
        (app_dir / f"index.{file_stem}.ts").write_text(registrar_code, encoding='utf-8')

    def _build_resource(self, serializer_cls, viewset_cls, endpoint: str, app_label: str, model_name: str) -> Dict[str, Any]:
        from rest_framework import serializers as drf
        from django.conf import settings as dj_settings
        from django.utils.module_loading import import_string

        # Instantiate serializer (no data, only for field metadata)
        try:
            serializer = serializer_cls()
        except Exception:
            # Fallback with empty context
            serializer = serializer_cls(context={})

        fields_od = serializer.get_fields()

        # Helpers for types and metadata
        def map_field(f: drf.Field) -> Dict[str, Any]:
            meta: Dict[str, Any] = {}
            meta['readOnly'] = bool(getattr(f, 'read_only', False))
            meta['writeOnly'] = bool(getattr(f, 'write_only', False))
            meta['required'] = bool(getattr(f, 'required', False)) and not meta['readOnly']
            meta['allowNull'] = bool(getattr(f, 'allow_null', False))
            # Defaults
            default = getattr(f, 'default', drf.empty)
            if default is drf.empty:
                meta['hasDefault'] = False
            else:
                if callable(default):
                    meta['hasDefault'] = True
                    meta['default'] = None
                else:
                    meta['hasDefault'] = True
                    meta['default'] = default
            # label/help_text/source
            if getattr(f, 'label', None):
                meta['label'] = str(getattr(f, 'label'))
            if getattr(f, 'help_text', None):
                meta['help_text'] = str(getattr(f, 'help_text'))
            if getattr(f, 'source', None):
                meta['source'] = str(getattr(f, 'source'))

            # validators
            validators = []
            # min_length/max_length
            if hasattr(f, 'min_length') and f.min_length is not None:
                validators.append({'type': 'min_length', 'value': int(f.min_length)})
            if hasattr(f, 'max_length') and f.max_length is not None:
                validators.append({'type': 'max_length', 'value': int(f.max_length)})
            if hasattr(f, 'min_value') and f.min_value is not None:
                validators.append({'type': 'min_value', 'value': float(f.min_value)})
            if hasattr(f, 'max_value') and f.max_value is not None:
                validators.append({'type': 'max_value', 'value': float(f.max_value)})
            # Regex
            try:
                from django.core.validators import RegexValidator
                for v in getattr(f, 'validators', []) or []:
                    if isinstance(v, RegexValidator):
                        validators.append({'type': 'pattern', 'value': v.regex.pattern})
            except Exception:
                pass
            if validators:
                meta['validators'] = validators

            # choices (only for explicit ChoiceField-like, not for relational fields)
            choices = getattr(f, 'choices', None)
            try:
                is_choicefield = isinstance(f, drf.ChoiceField)
            except Exception:
                is_choicefield = False
            if choices and is_choicefield:
                meta['choices'] = [{'value': val, 'label': str(lab)} for val, lab in list(choices.items())]

            # type mapping
            meta['many'] = False
            meta['kind'] = 'primitive'
            meta['type'] = 'any'
            subtype: Optional[str] = None

            # ListSerializer (many nested), ListField, ManyRelatedField
            if isinstance(f, drf.ListSerializer):
                meta['kind'] = 'array'
                meta['many'] = True
                child = f.child
                child_meta = map_field(child)
                meta['items'] = child_meta
                meta['type'] = 'array'
            elif isinstance(f, getattr(drf, 'ManyRelatedField', tuple())):
                meta['kind'] = 'array'
                meta['many'] = True
                child = getattr(f, 'child_relation', None)
                # Default array type and relation inference for many relations
                meta['type'] = 'array'
                try:
                    rel_model = None
                    if child is not None:
                        # Map child as a PK field when possible
                        child_meta = map_field(child)
                        # Force items.type to number for IDs
                        if child_meta.get('type') == 'number|string':
                            child_meta['type'] = 'number'
                        meta['items'] = child_meta
                        qs = getattr(child, 'queryset', None)
                        if qs is not None:
                            rel_model = getattr(qs, 'model', None)
                        if rel_model is None and callable(getattr(child, 'get_queryset', None)):
                            try:
                                qs2 = child.get_queryset()
                                rel_model = getattr(qs2, 'model', None)
                            except Exception:
                                rel_model = None
                    if rel_model is not None:
                        app_label = rel_model._meta.app_label
                        model_name = rel_model._meta.model_name
                        # Determine target field (pk by default, slug if SlugRelatedField)
                        to_field = None
                        try:
                            if isinstance(child, drf.SlugRelatedField):
                                to_field = getattr(child, 'slug_field', None) or None
                        except Exception:
                            to_field = None
                        if not to_field:
                            try:
                                to_field = rel_model._meta.pk.name
                            except Exception:
                                to_field = 'id'
                        meta['relation'] = { 'kind': 'many', 'resource': f"{app_label}.{model_name}", 'toField': to_field }
                    # Ensure items present even if we couldn't introspect
                    if 'items' not in meta:
                        meta['items'] = { 'type': 'number' }
                except Exception:
                    # Fallback items
                    if 'items' not in meta:
                        meta['items'] = { 'type': 'number' }
            elif isinstance(f, drf.ListField):
                meta['kind'] = 'array'
                meta['many'] = True
                child = f.child
                child_meta = map_field(child)
                meta['items'] = child_meta
                meta['type'] = 'array'
            # Nested serializer
            elif isinstance(f, drf.Serializer):
                meta['kind'] = 'object'
                meta['type'] = 'object'
                nested_fields = f.get_fields()
                meta['properties'] = {n: map_field(sf) for n, sf in nested_fields.items()}
            # Related fields by key
            elif isinstance(f, (drf.PrimaryKeyRelatedField,)):
                # Represent related PKs as numeric IDs on the client
                meta['type'] = 'number'
                # Attach relation info if we can infer target model
                try:
                    rel_model = None
                    qs = getattr(f, 'queryset', None)
                    if qs is not None:
                        rel_model = getattr(qs, 'model', None)
                    if rel_model is None and callable(getattr(f, 'get_queryset', None)):
                        try:
                            qs2 = f.get_queryset()
                            rel_model = getattr(qs2, 'model', None)
                        except Exception:
                            rel_model = None
                    if rel_model is not None:
                        app_label = rel_model._meta.app_label
                        model_name = rel_model._meta.model_name
                        # Determine target field (pk by default)
                        try:
                            to_field = rel_model._meta.pk.name
                        except Exception:
                            to_field = 'id'
                        meta['relation'] = { 'kind': 'one', 'resource': f"{app_label}.{model_name}", 'toField': to_field }
                except Exception:
                    pass
            elif isinstance(f, (drf.SlugRelatedField, drf.StringRelatedField, drf.HyperlinkedRelatedField)):
                meta['type'] = 'string'
            else:
                # Primitive and special mappings
                if isinstance(f, drf.ChoiceField):
                    # Determine base type from choices values
                    ch = getattr(f, 'choices', None) or {}
                    values = [val for val, _ in list(ch.items())]
                    if values and all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in values):
                        meta['type'] = 'number'
                    elif values and all(isinstance(v, str) for v in values):
                        meta['type'] = 'string'
                    elif values:
                        # Mixed values, be explicit union
                        meta['type'] = 'number|string'
                    else:
                        # No values? fallback to any
                        meta['type'] = 'any'
                elif isinstance(f, (drf.IntegerField, drf.FloatField)):
                    meta['type'] = 'number'
                elif isinstance(f, drf.DecimalField):
                    # Represent decimals as strings by default to preserve precision
                    # Keep subtype and numeric constraints
                    # Edge-case: if serializer explicitly disables string coercion, use number but keep subtype
                    coerce_to_string = getattr(f, 'coerce_to_string', True)
                    meta['type'] = 'number' if (coerce_to_string is False) else 'string'
                    subtype = 'decimal'
                    # Include DRF decimal constraints if available
                    if hasattr(f, 'max_digits') and f.max_digits is not None:
                        meta['max_digits'] = int(f.max_digits)
                    if hasattr(f, 'decimal_places') and f.decimal_places is not None:
                        meta['decimal_places'] = int(f.decimal_places)
                elif isinstance(f, drf.BooleanField):
                    meta['type'] = 'boolean'
                elif isinstance(f, (drf.UUIDField,)):
                    meta['type'] = 'string'
                    subtype = 'uuid'
                elif isinstance(f, drf.DateField):
                    meta['type'] = 'string'
                    subtype = 'date'
                elif isinstance(f, drf.DateTimeField):
                    meta['type'] = 'string'
                    subtype = 'datetime'
                elif isinstance(f, drf.TimeField):
                    meta['type'] = 'string'
                    subtype = 'time'
                elif isinstance(f, (drf.JSONField, drf.DictField)):
                    meta['type'] = 'json'
                elif isinstance(f, drf.CharField):
                    meta['type'] = 'string'
                else:
                    meta['type'] = 'any'
            if subtype:
                meta['subtype'] = subtype
            return meta

        fields_meta: Dict[str, Any] = {}
        for name, f in fields_od.items():
            fields_meta[name] = map_field(f)

        # Heuristic corrections for known server-managed/sensitive fields
        try:
            # Force password-like fields to writeOnly
            for fname, fmeta in fields_meta.items():
                low = fname.lower()
                if low in ('password',) or low.endswith('_password') or low.startswith('password_'):
                    fmeta['writeOnly'] = True
            # Force readOnly for well-known server-managed timestamps
            for fname in ('last_login', 'date_joined'):
                if fname in fields_meta:
                    fields_meta[fname]['readOnly'] = True
                    # readOnly fields should not be required
                    fields_meta[fname]['required'] = False
        except Exception:
            pass

        # Warn on potentially sensitive fields not marked write_only
        try:
            sensitive_keywords = (
                'password', 'pass', 'token', 'secret', 'api_key', 'apikey', 'auth', 'reset_code', 'otp', 'pin'
            )
            for fname, fmeta in fields_meta.items():
                lower = fname.lower()
                if any(kw in lower for kw in sensitive_keywords) and not fmeta.get('writeOnly', False):
                    self.stdout.write(self.style.WARNING(
                        f"Field '{fname}' appears sensitive but is not write_only=True in serializer."
                    ))
        except Exception:
            pass

        # Action support
        std_actions = ['list', 'retrieve', 'create', 'update', 'partial_update', 'destroy']
        actions_avail = {a: bool(getattr(viewset_cls, a, None)) for a in std_actions}

        # Pagination
        pagination = None
        try:
            pag_cls = getattr(viewset_cls, 'pagination_class', None)
            if pag_cls is not None:
                page_size = getattr(pag_cls, 'page_size', None)
                pagination = {'class': pag_cls.__name__, 'page_size': page_size}
            else:
                # fallback to REST_FRAMEWORK settings
                try:
                    from django.conf import settings as dj_settings
                    rf = getattr(dj_settings, 'REST_FRAMEWORK', {}) or {}
                    dpc = rf.get('DEFAULT_PAGINATION_CLASS')
                    if dpc:
                        # class path string -> take last part as name
                        cls_name = str(dpc).split('.')[-1]
                        page_size = rf.get('PAGE_SIZE')
                        pagination = {'class': cls_name, 'page_size': page_size}
                except Exception:
                    pass
        except Exception:
            pass

        # Filters/search/ordering
        search_list = None
        ordering_obj = None
        filters_obj = None
        try:
            fbs = getattr(viewset_cls, 'filter_backends', []) or []
            from rest_framework.filters import SearchFilter, OrderingFilter
            try:
                from django_filters.rest_framework import DjangoFilterBackend
            except Exception:
                DjangoFilterBackend = None  # type: ignore

            # search
            if any((fb is SearchFilter) or (isinstance(fb, type) and issubclass(fb, SearchFilter)) for fb in fbs):
                sf = getattr(viewset_cls, 'search_fields', None)
                if sf:
                    search_list = list(sf)

            # ordering
            if any((fb is OrderingFilter) or (isinstance(fb, type) and issubclass(fb, OrderingFilter)) for fb in fbs):
                of = getattr(viewset_cls, 'ordering_fields', None)
                default_ord = getattr(viewset_cls, 'ordering', None)
                ord_fields = list(of) if of else None
                if default_ord is not None:
                    if isinstance(default_ord, (list, tuple)):
                        default_val = list(default_ord) if len(default_ord) != 1 else default_ord[0]
                    else:
                        default_val = default_ord
                else:
                    default_val = None
                if ord_fields is not None or default_val is not None:
                    ordering_obj = {
                        'fields': ord_fields,
                        'default': default_val,
                    }

            # filters via DjangoFilterBackend
            if DjangoFilterBackend and any((fb is DjangoFilterBackend) or (isinstance(fb, type) and issubclass(fb, DjangoFilterBackend)) for fb in fbs):
                backend_path = f"{DjangoFilterBackend.__module__}.{DjangoFilterBackend.__name__}"
                ff = getattr(viewset_cls, 'filterset_fields', None)
                fsc = getattr(viewset_cls, 'filterset_class', None)
                payload: Dict[str, Any] = {'backend': backend_path}
                if isinstance(ff, dict):
                    payload['fields'] = ff
                elif isinstance(ff, (list, tuple, set)):
                    payload['fields'] = list(ff)
                elif fsc is not None:
                    # Try to expand from filterset class Meta.fields if present; else expose class path
                    fields_from_meta = None
                    if hasattr(fsc, 'Meta') and hasattr(fsc.Meta, 'fields'):
                        fields_from_meta = getattr(fsc.Meta, 'fields')
                    if isinstance(fields_from_meta, dict):
                        payload['fields'] = fields_from_meta
                    elif isinstance(fields_from_meta, (list, tuple, set)):
                        payload['fields'] = list(fields_from_meta)
                    else:
                        payload['filtersetClass'] = f"{fsc.__module__}.{fsc.__name__}"
                if len(payload.keys()) >= 2:
                    filters_obj = payload
        except Exception:
            pass

        resource: Dict[str, Any] = {
            'metadataVersion': 1,
            'resource': {
                'name': model_name.lower(),
                'typeName': model_name,
                'appLabel': app_label,
                'endpoint': f"/api/{endpoint}/",  # Note: versioned base path determination is left to router; TS paths are unprefixed by version
                'actions': actions_avail,
                'pagination': pagination,
                'search': search_list,
                'ordering': ordering_obj,
                'filters': filters_obj,
            },
            'fields': fields_meta,
        }

        # Derive TS type maps for Read/Create/Update
        def ts_type_for_meta(m: Dict[str, Any], for_write: bool, is_update: bool) -> str:
            # Determine base TS type
            if m.get('kind') == 'array':
                inner = ts_type_for_meta(m.get('items', {}), for_write, is_update)
                t = f"{inner}[]"
            elif m.get('kind') == 'object':
                # Inline nested object type
                props = m.get('properties', {})
                parts = []
                for pn, pm in props.items():
                    optional = False
                    if for_write:
                        # create: required if required and not readOnly and no default; update: optional
                        if is_update:
                            optional = True
                        else:
                            optional = not (pm.get('required') and not pm.get('readOnly') and not pm.get('hasDefault'))
                    tprop = ts_type_for_meta(pm, for_write, is_update)
                    q = '?' if optional else ''
                    null_union = ' | null' if pm.get('allowNull') and not pm.get('kind') == 'array' else ''
                    parts.append(f"{pn}{q}: {tprop}{null_union};")
                t = '{ ' + ' '.join(parts) + ' }'
            else:
                tname = m.get('type', 'any')
                if tname == 'number|string':
                    t = '(number | string)'
                elif tname == 'json':
                    t = 'any'
                else:
                    t = tname
            return t

        # Build TS type properties dicts
        read_props: Dict[str, str] = {}
        create_props: Dict[str, str] = {}
        update_props: Dict[str, str] = {}

        for fname, fmeta in fields_meta.items():
            # Read type excludes writeOnly fields
            if not fmeta.get('writeOnly'):
                read_t = ts_type_for_meta(fmeta, for_write=False, is_update=False)
                if fmeta.get('allowNull') and fmeta.get('kind') != 'array' and fmeta.get('kind') != 'object':
                    read_t = f"{read_t} | null"
                read_props[fname] = read_t

            # Write payloads exclude readOnly
            if fmeta.get('readOnly'):
                continue
            # Create required/opcional according to DRF rules
            create_t = ts_type_for_meta(fmeta, for_write=True, is_update=False)
            if fmeta.get('allowNull') and fmeta.get('kind') not in ('array', 'object'):
                create_t = f"{create_t} | null"
            # Required?
            is_required = bool(fmeta.get('required')) and not fmeta.get('hasDefault')
            create_props[(fname, is_required)] = create_t

            # Update: all optional
            update_t = ts_type_for_meta(fmeta, for_write=True, is_update=True)
            if fmeta.get('allowNull') and fmeta.get('kind') not in ('array', 'object'):
                update_t = f"{update_t} | null"
            update_props[fname] = update_t

        resource['tsTypes'] = {
            'read': read_props,
            'create': create_props,  # keys are tuples for required flag; handled during rendering
            'update': update_props,
        }

        return resource

    def _introspect_field(self, field) -> Optional[Dict[str, Any]]:
        from django.db import models as djm

        # Primary keys: treat as number/string depending on type, but usually id number
        if getattr(field, 'primary_key', False):
            name = field.name
            label = capfirst(getattr(field, 'verbose_name', name))
            base_ts = 'number' if field.get_internal_type() not in ('UUIDField',) else 'string'
            yup = 'Yup.number()' if base_ts == 'number' else 'Yup.string()'
            return {
                'name': name,
                'label': label,
                'ts_type': base_ts,
                'ui_type': 'number' if base_ts == 'number' else 'text',
                'required': True,
                'yup': yup,
            }

        # ManyToMany
        if isinstance(field, djm.ManyToManyField):
            name = field.name
            label = capfirst(getattr(field, 'verbose_name', name))
            required = not field.blank
            ts_type = 'number[]'
            yup = 'Yup.array().of(Yup.number())' + ('.required()' if required else '')
            return {
                'name': name,
                'label': label,
                'ts_type': ts_type,
                'ui_type': 'relation',
                'required': required,
                'many': True,
                'relatedModel': field.related_model.__name__,
                'yup': yup,
            }

        # ForeignKey and OneToOne
        if isinstance(field, (djm.ForeignKey, djm.OneToOneField)):
            name = field.name
            label = capfirst(getattr(field, 'verbose_name', name))
            nullable = field.null
            required = not field.blank and not field.null
            ts_type = 'number' + (' | null' if nullable else '')
            yup = 'Yup.number()' + ('.nullable()' if nullable else '') + ('.required()' if required else '')
            return {
                'name': name,
                'label': label,
                'ts_type': ts_type,
                'ui_type': 'relation',
                'required': required,
                'many': False,
                'relatedModel': field.related_model.__name__,
                'yup': yup,
            }

        # Regular fields
        internal = field.get_internal_type()
        name = field.name
        label = capfirst(getattr(field, 'verbose_name', name))
        nullable = getattr(field, 'null', False)
        required = not getattr(field, 'blank', False) and not nullable

        # Base TS type
        ts_type = DJANGO_TO_TS_TYPE.get(internal, 'any')
        # UI type heuristic
        ui_type = DJANGO_TO_FIELD_UI.get(internal, 'text')

        # Choices (if any)
        choices_list: Optional[List[Dict[str, Any]]] = None
        if getattr(field, 'choices', None):
            # Normalize choices to a list of {value, label}
            choices_list = []
            for val, lab in field.choices:
                choices_list.append({'value': val, 'label': str(lab)})

        # Yup mapping
        yup = self._yup_for_field(internal, nullable, required)

        return {
            'name': name,
            'label': label,
            'ts_type': ts_type if not nullable else f'{ts_type} | null' if ts_type in ('string', 'number', 'boolean') else ts_type,
            'ui_type': ui_type,
            'required': required,
            'choices': choices_list,
            'yup': yup,
        }

    def _yup_for_field(self, internal: str, nullable: bool, required: bool) -> str:
        # Base constructors
        if internal in ('IntegerField', 'BigIntegerField', 'SmallIntegerField', 'PositiveIntegerField', 'PositiveSmallIntegerField'):
            base = 'Yup.number().integer()'
        elif internal in ('FloatField', 'DecimalField'):
            base = 'Yup.number()'
        elif internal == 'BooleanField' or internal == 'NullBooleanField':
            base = 'Yup.boolean()'
        elif internal in ('DateField', 'DateTimeField', 'TimeField'):
            base = 'Yup.date()'
        elif internal == 'EmailField':
            base = 'Yup.string().email()'
        elif internal == 'JSONField':
            base = 'Yup.mixed()'
        else:
            base = 'Yup.string()'

        if nullable:
            base += '.nullable()'
        if required and internal not in ('BooleanField', 'NullBooleanField'):
            base += '.required()'
        return base

    def _prepare_app_dirs(self, app_dir: Path) -> None:
        """Ensure app subfolders exist and clean their contents (types, meta) and old registrar files.
        """
        for sub in ['types', 'meta']:
            subdir = app_dir / sub
            subdir.mkdir(parents=True, exist_ok=True)
            for item in list(subdir.iterdir()):
                try:
                    if item.is_file():
                        item.unlink()
                except Exception:
                    # Silently continue on files that can't be removed
                    pass
        # Remove old registrar files like index.<model>.ts and previous index.ts
        try:
            for item in app_dir.glob('index.*.ts'):
                if item.is_file():
                    item.unlink()
        except Exception:
            pass

    def _write_app_index(self, app_dir: Path) -> None:
        """(Deprecated) Previously exported all generated items. Kept for backward compatibility, unused now."""
        lines: List[str] = []
        header = self._ts_autogen_header()
        for sub in ['types', 'meta']:
            subdir = app_dir / sub
            if not subdir.exists():
                continue
            for f in sorted(subdir.glob('*.ts')):
                if f.name == 'index.ts':
                    continue
                stem = f.stem
                lines.append(f"export * from './{sub}/{stem}';")
        content = header + ("\n".join(lines) + ("\n" if lines else ""))
        (app_dir / 'index.ts').write_text(content, encoding='utf-8')

    def _render_model_registrar_ts(self, resource: Dict[str, Any]) -> str:
        """Render the per-model registrar file content (index.<model>.ts)."""
        header = self._ts_autogen_header()
        tn = resource['resource']['typeName']
        name_lower = resource['resource']['name']
        lines: List[str] = []
        lines.append("import { createModelRegistrar, type DRFMetaRaw } from 'django-auto-drf-react';")
        lines.append(f"import {{ {tn}Meta }} from './meta/{name_lower}';")
        lines.append("")
        lines.append(f"export const register{tn} = createModelRegistrar({tn}Meta as unknown as DRFMetaRaw);")
        lines.append("")
        return header + "\n".join(lines)

    def _write_app_registrar_index(self, app_dir: Path, app_label: str, model_names: List[str]) -> None:
        """Generate the app-level registrar index.ts as specified."""
        header = self._ts_autogen_header()
        app_pascal = self._to_pascal_identifier(app_label)
        # Build imports
        lines: List[str] = []
        lines.append("import { createAppRegistrar, type DRFMetaRaw } from 'django-auto-drf-react';")
        for mn in sorted(model_names, key=lambda s: s.lower()):
            lines.append(f"import {{ {mn}Meta }} from './meta/{mn.lower()}';")
        lines.append("")
        # Registrar creation
        lines.append(f"export const register{app_pascal}App = createAppRegistrar([")
        for mn in sorted(model_names, key=lambda s: s.lower()):
            lines.append(f"  {mn}Meta as unknown as DRFMetaRaw,")
        lines.append("]);")
        lines.append("")
        # Optional: re-export per-model registrars for granular use
        for mn in sorted(model_names, key=lambda s: s.lower()):
            lines.append(f"export {{ register{mn} }} from './index.{mn.lower()}';")
        lines.append("")
        (app_dir / 'index.ts').write_text(header + "\n".join(lines), encoding='utf-8')

    def _write_apps_aggregator(self, base_dir: Path, app_labels: List[str]) -> None:
        """Generate optional frontend/apps.ts aggregator that merges all app registrars."""
        header = self._ts_autogen_header()
        lines: List[str] = []
        lines.append("import { mergeRegistrars } from 'django-auto-drf-react';")
        for app_label in app_labels:
            app_pascal = self._to_pascal_identifier(app_label)
            lines.append(f"import {{ register{app_pascal}App }} from './{app_label}';")
        lines.append("")
        lines.append("export const registerAllApps = mergeRegistrars(")
        for app_label in app_labels:
            app_pascal = self._to_pascal_identifier(app_label)
            lines.append(f"  register{app_pascal}App,")
        lines.append(");")
        lines.append("")
        (base_dir / 'apps.ts').write_text(header + "\n".join(lines), encoding='utf-8')

    def _render_ts_type(self, schema: Dict[str, Any]) -> str:
        lines: List[str] = []
        lines.append(f"export type {schema['typeName']} = {{")
        for name, ts_t in schema['tsProps'].items():
            lines.append(f"  {name}: {ts_t};")
        lines.append('};')
        lines.append('')
        return "\n".join(lines)

    def _render_ts_enums(self, schema: Dict[str, Any]) -> str:
        lines: List[str] = []
        for field_name, options in schema['enums'].items():
            const_name = f"{schema['typeName']}{self._camel_to_pascal(field_name)}Options"
            lines.append(f"export const {const_name} = [")
            for opt in options:
                value = opt['value']
                if isinstance(value, (int, float)):
                    val_repr = str(value)
                else:
                    s = str(value).replace('\\', '\\\\').replace('"', '\\"')
                    val_repr = f'"{s}"'
                label = str(opt['label']).replace('\\', '\\\\').replace('"', '\\"')
                lines.append(f"  {{ value: {val_repr}, label: \"{label}\" }},")
            lines.append("] as const;")
            lines.append('')
        return "\n".join(lines)

    def _render_ts_model(self, schema: Dict[str, Any], has_enums: bool) -> str:
        lines: List[str] = []
        # imports
        lines.append("import * as Yup from 'yup';")
        file_stem = schema['name']
        # Note: no need to import the TS type in model file; keeping model self-contained
        if has_enums:
            const_names: List[str] = []
            for field_name in schema['enums'].keys():
                const_names.append(f"{schema['typeName']}{self._camel_to_pascal(field_name)}Options")
            joined = ', '.join(const_names)
            lines.append(f"import {{ {joined} }} from '../enums/{file_stem}';")
        lines.append('')

        # Model object
        lines.append(f"export const {schema['typeName']}Model = {{")
        lines.append(f"  name: '{schema['name']}',")
        lines.append(f"  label: '{self._escape_js(schema['label'])}',")
        lines.append(f"  apiPath: '{schema['apiPath']}',")
        lines.append(f"  permissions: {{")
        for k, v in schema['permissions'].items():
            lines.append(f"    {k}: '{v}',")
        lines.append("  },")
        lines.append("  fields: [")
        for f in schema['fields']:
            line = (
                f"    {{ name: '{f['name']}', label: '{self._escape_js(f['label'])}', "
                f"type: '{f['type']}', required: {str(bool(f['required'])).lower()}"
            )
            if f.get('many'):
                line += ", many: true"
            if f.get('relatedModel'):
                line += f", relatedModel: '{f['relatedModel']}'"
            if f.get('choices'):
                const_name = f"{schema['typeName']}{self._camel_to_pascal(f['name'])}Options"
                line += f", options: {const_name}"
            line += " },"
            lines.append(line)
        lines.append("  ],")

        # validation schema
        lines.append("  validationSchema: Yup.object({")
        for name, rule in schema['yupRules'].items():
            lines.append(f"    {name}: {rule},")
        lines.append("  }),")
        lines.append("};")
        lines.append('')

        return "\n".join(lines)

    def _render_ts(self, schema: Dict[str, Any]) -> str:
        # Build TS type definition
        lines: List[str] = []
        lines.append("import * as Yup from 'yup';")
        lines.append('')
        # If any enums present, render them first as const arrays
        if schema['enums']:
            for field_name, options in schema['enums'].items():
                const_name = f"{schema['typeName']}{self._camel_to_pascal(field_name)}Options"
                lines.append(f"export const {const_name} = [")
                for opt in options:
                    value = opt['value']
                    if isinstance(value, (int, float)):
                        val_repr = str(value)
                    else:
                        s = str(value).replace('\\', '\\\\').replace('"', '\\"')
                        val_repr = f'"{s}"'
                    label = str(opt['label']).replace('\\', '\\\\').replace('"', '\\"')
                    lines.append(f"  {{{{ value: {val_repr}, label: \"{label}\" }}}},")
                lines.append("] as const;")
                lines.append('')

        # type
        lines.append(f"export type {schema['typeName']} = {{")
        for name, ts_t in schema['tsProps'].items():
            lines.append(f"  {name}: {ts_t};")
        lines.append('};')
        lines.append('')

        # Model object
        lines.append(f"export const {schema['typeName']}Model = {{")
        lines.append(f"  name: '{schema['name']}',")
        lines.append(f"  label: '{self._escape_js(schema['label'])}',")
        lines.append(f"  apiPath: '{schema['apiPath']}',")
        lines.append(f"  permissions: {{")
        for k, v in schema['permissions'].items():
            lines.append(f"    {k}: '{v}',")
        lines.append("  },")
        lines.append("  fields: [")
        for f in schema['fields']:
            line = (
                f"    {{{{ name: '{f['name']}', label: '{self._escape_js(f['label'])}', "
                f"type: '{f['type']}', required: {str(bool(f['required'])).lower()}"
            )
            if f.get('many'):
                line += ", many: true"
            if f.get('relatedModel'):
                line += f", relatedModel: '{f['relatedModel']}'"
            if f.get('choices'):
                const_name = f"{schema['typeName']}{self._camel_to_pascal(f['name'])}Options"
                line += f", options: {const_name}"
            line += " }},"
            lines.append(line)
        lines.append("  ],")

        # validation schema
        lines.append("  validationSchema: Yup.object({")
        for name, rule in schema['yupRules'].items():
            lines.append(f"    {name}: {rule},")
        lines.append("  }),")
        lines.append("};")
        lines.append('')

        return "\n".join(lines)

    def _render_ts_types(self, resource: Dict[str, Any]) -> str:
        tn = resource['resource']['typeName']
        read = resource['tsTypes']['read']
        create = resource['tsTypes']['create']
        update = resource['tsTypes']['update']
        header = self._ts_autogen_header()
        lines: List[str] = []
        # Read type
        lines.append(f"export type {tn} = {tn}Read;")
        lines.append(f"export type {tn}Read = {{")
        for name, t in read.items():
            lines.append(f"  {name}: {t};")
        lines.append("};")
        lines.append("")
        # Create payload
        lines.append(f"export type {tn}CreatePayload = {{")
        for key, t in create.items():
            if isinstance(key, tuple):
                name, req = key
            else:
                name, req = key, False
            q = '' if req else '?'
            lines.append(f"  {name}{q}: {t};")
        lines.append("};")
        lines.append("")
        # Update payload
        lines.append(f"export type {tn}UpdatePayload = {{")
        for name, t in update.items():
            lines.append(f"  {name}?: {t};")
        lines.append("};")
        lines.append("")
        return header + "\n".join(lines)

    def _render_meta_ts(self, resource: Dict[str, Any]) -> str:
        tn = resource['resource']['typeName']
        header = self._ts_autogen_header()
        # Serialize JSON into TS const (drop non-serializable helpers like tsTypes)
        safe_payload = self._make_meta_payload(resource)
        payload = json.dumps(safe_payload, indent=2, ensure_ascii=False)
        # Avoid unescaped backslashes or quotes issues
        return header + f"export const {tn}Meta = {payload} as const;\n"

    def _make_meta_payload(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """Return a JSON-serializable copy of resource for meta export (drops tsTypes)."""
        import copy
        data = copy.deepcopy(resource)
        # Drop non-serializable helpers
        if 'tsTypes' in data:
            try:
                del data['tsTypes']
            except Exception:
                pass
        return data

    def _ts_autogen_header(self) -> str:
        """Standard header for generated TypeScript files (Italian notice)."""
        return (
            "// ATTENZIONE: File generato automaticamente da django-auto-drf.\n"
            "// Non modificare direttamente questo file.\n"
            "// Rigenerare utilizzando il comando `generate_ts_models`.\n\n"
        )

    def _camel_to_pascal(self, s: str) -> str:
        if not s:
            return s
        return s[0].upper() + s[1:]

    def _to_pascal_identifier(self, s: str) -> str:
        """Convert strings like 'first_app' or 'second-app' to 'FirstApp'."""
        parts: List[str] = []
        curr = ''
        for ch in s:
            if ch.isalnum():
                curr += ch
            else:
                if curr:
                    parts.append(curr)
                    curr = ''
        if curr:
            parts.append(curr)
        return ''.join(p[:1].upper() + p[1:] for p in parts if p)

    def _escape_js(self, s: str) -> str:
        return str(s).replace('\\', '\\\\').replace('\n', ' ').replace("'", "\\'")
