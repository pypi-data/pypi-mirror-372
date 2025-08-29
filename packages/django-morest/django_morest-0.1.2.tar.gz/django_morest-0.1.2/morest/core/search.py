import typing
from django.db import models
from django.db.models.query import QuerySet
from django.db.models.constants import LOOKUP_SEP
from django.core.exceptions import FieldDoesNotExist
from django.utils.text import (
    smart_split,
    unescape_string_literal,
)


T = typing.TypeVar("T")


def search_in_queryset(qs: QuerySet[T], search_term: str, search_fields: typing.List[str]):
    def construct_search(field_name):
        if field_name.startswith("^"):
            return "%s__istartswith" % field_name.removeprefix("^")
        elif field_name.startswith("="):
            return "%s__iexact" % field_name.removeprefix("=")
        elif field_name.startswith("@"):
            return "%s__search" % field_name.removeprefix("@")
        # Use field_name if it includes a lookup.
        opts = qs.model._meta
        lookup_fields = field_name.split(LOOKUP_SEP)
        # Go through the fields, following all relations.
        prev_field = None
        for path_part in lookup_fields:
            if path_part == "pk":
                path_part = opts.pk.name
            try:
                field = opts.get_field(path_part)
            except FieldDoesNotExist:
                # Use valid query lookups.
                if prev_field and prev_field.get_lookup(path_part):
                    return field_name
            else:
                prev_field = field
                if hasattr(field, "path_infos"):
                    # Update opts to follow the relation.
                    opts = field.path_infos[-1].to_opts
        # Otherwise, use the field with icontains.
        return "%s__icontains" % field_name

    if search_fields and search_term:
        orm_lookups = [
            construct_search(str(search_field)) for search_field in search_fields
        ]
        term_queries = []
        for bit in smart_split(search_term):
            if bit.startswith(('"', "'")) and bit[0] == bit[-1]:
                bit = unescape_string_literal(bit)
            or_queries = models.Q.create(
                [(orm_lookup, bit) for orm_lookup in orm_lookups],
                connector=models.Q.OR,
            )
            term_queries.append(or_queries)
        qs = qs.filter(models.Q.create(term_queries))
    return qs 
