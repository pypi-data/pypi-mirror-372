def get_queryset(qs):
    if hasattr(qs, "_default_manager"):
        return qs._default_manager
    return qs