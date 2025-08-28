from django_auto_drf.registry import api_register_model, load_class_from_module


def discovery_api_models(app, exclude_models=None, **kwargs):
    """
    Iterates through the app's models and registers them with `api_register_model`,
    attempting to load Default<ModelName>Serializer and Default<ModelName>FilterSet
    for each model and register them if they exist.
    """
    # Normalizza le etichette dei modelli da escludere in lowercase
    exclude_models = [model.lower() for model in (exclude_models or [])]

    # Cicla sui modelli registrati nell'app (self.get_models include solo quelli dell'app corrente)
    for model in app.get_models():
        model_label = model._meta.label_lower
        if model_label in exclude_models:
            continue

        # Registra il modello
        api_register_model(model, **kwargs)

        # Ottieni il nome del modello
        model_name = model.__name__

        # Tenta di caricare e registrare il serializer e il filterset
        serializer_class_name = f"Default{model_name}Serializer"
        filterset_class_name = f"Default{model_name}FilterSet"

        # Usa la funzione generica per caricare classi dai moduli
        serializer_class = load_class_from_module(f"{app.name}.serializers", serializer_class_name)
        filterset_class = load_class_from_module(f"{app.name}.filters", filterset_class_name)

        # Registra il serializer se esiste
        if serializer_class:
            api_register_model(model)(serializer_class)

        # Registra il filterset se esiste
        if filterset_class:
            api_register_model(model)(filterset_class)
