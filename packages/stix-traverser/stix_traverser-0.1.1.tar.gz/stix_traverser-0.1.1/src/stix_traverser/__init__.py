__version__ = "0.1.0"

import logging
from typing import Literal, Union, Any
import stix2
from stix2.properties import ReferenceProperty, ListProperty

logger = logging.getLogger(__name__)

class Traverser:
    pass

class EmptyTraverser:
    def __getattribute__(self, item) -> 'EmptyTraverser':
        return self

    def __bool__(self) -> Literal[False]:
        return False

    def __call__(self, *args, **kwargs) -> Literal[None]:
        return None

    def __getitem__(self, item) -> 'EmptyTraverser':
        return EmptyTraverser()


class ValueTraverser:
    def __init__(self, value):
        self._value = value

    def __call__(self, *args, **kwargs):
        return self._value

    def __str__(self):
        return str(self._value)

    def __getattr__(self, item):
        return ValueTraverser(self._value)

    def __getitem__(self, item):
        return ValueTraverser(self._value)


def _get_reverse_types():
    type_reg = {}

    for item in stix2.v21._Observable.__subclasses__():
        type_reg[item.__name__] = getattr(item, '_type')

    for item in stix2.v21._DomainObject.__subclasses__():
        type_reg[item.__name__] = getattr(item, '_type')


    return type_reg


class ObjectTraverser:
    def __init__(self, obj: stix2.base._STIXBase, env: stix2.Environment = None):
        self._object = obj

        if env:
            self._store = env
        else:
            self._store = stix2.Environment(
                store=stix2.MemoryStore()
            )

        self._refs, self._type_refs = self._get_reference_types()
        self._types = _get_reverse_types()

    def __str__(self):
        return str(self._object)

    def __call__(self, *args, **kwargs):
        return self._object

    def __getattr__(self, item) -> Union[Any, 'ListTraverser']:
        try:
            item, value = self._get_fuzzy_attr(item)

            if item in self._refs:
                return ListTraverser(*self._load_refs(value), store=self._store)

            return value
        except AttributeError:
            pass

        try:
            return self._get_extension(item)
        except AttributeError:
            pass

        if item in self._types:
            fields = self._get_fields(item)
            if fields:
                refs = self._gather_refs(fields)
                return ListTraverser(*self._load_refs(refs), store=self._store)
            else:
                objs = self._store.related_to(
                    obj=self._object,
                    filters=[stix2.Filter("type", "=", self._types[item])]
                )
                return ListTraverser(*objs, store=self._store)

        return EmptyTraverser()

    def _get_extension(self, item: str):
        if item and hasattr(self._object, 'extensions'):
            extension = item.replace('_', '-') + '-ext'
            return ObjectTraverser(self._object.extensions.get(extension), self._store)
        raise AttributeError


    def _get_fuzzy_attr(self, item: str) -> (str, Any):
        variants = (item, item + "_ref", item + "_refs")
        for variant in variants:
            if hasattr(self._object, variant):
                return variant, getattr(self._object, variant)
        raise AttributeError

    def _get_fields(self, ref_type):
        type_alias = self._types[ref_type]
        fields = self._type_refs.get(type_alias)

        return fields

    def _gather_refs(self, fields):
        result = []
        for field in fields:
            if hasattr(self._object, field):
                value = getattr(self._object, field)
                if type(value) is list:
                    result.extend(value)
                else:
                    result.append(value)

        return result

    def _load_refs(self, refs):
        if type(refs) is not list:
            refs = [refs]
        return [self._store.get(ref) for ref in refs]

    def _get_reference_types(self):
        refs = set()
        type_refs = {}

        def extract_types(prop):
            if prop.auth_type == ReferenceProperty._WHITELIST:
                return prop.generics | prop.specifics

            return None

        attrs = getattr(self._object, '_properties', dict())
        for name, val in attrs.items():
            if name.endswith('_ref') or name.endswith('_refs'):
                refs.add(name)
                types = set()

                if isinstance(val, ReferenceProperty):
                    types = extract_types(val)

                if isinstance(val, ListProperty) and isinstance(val.contained, ReferenceProperty):
                    types = extract_types(val.contained)

                for ref_type in types:
                    if ref_type not in type_refs:
                        type_refs[ref_type] = []

                    type_refs[ref_type].append(name)

        return refs, type_refs

class ListTraverser:
    _list: list[ObjectTraverser]

    def __init__(self, *args, store = None):
        self._list = []

        if store:
            self._store = store
        else:
            self._store = stix2.Environment(
                store=stix2.MemoryStore()
            )

        for obj in args:
            if type(obj) in (ObjectTraverser, ValueTraverser, EmptyTraverser, ListTraverser):
                self._list.append(obj)
            else:
                self._list.append(ObjectTraverser(obj=obj, env=self._store))

    def __str__(self):
        return repr(self._list)

    def __call__(self, *args, **kwargs):
        return [obj() for obj in self._list]

    def __getattr__(self, item):
        result = []
        for i in self._list:
            obj = i.__getattr__(item)

            if isinstance(obj, ListTraverser):
                result.extend(obj._list)

            elif type(obj) in (EmptyTraverser, ObjectTraverser):
                result.append(obj)

            else:
                result.append(ValueTraverser(obj))

        return  ListTraverser(*result, store=self._store)


    def __getitem__(self, item):
        try:
            return self._list.__getitem__(item)
        except IndexError:
            return EmptyTraverser()

class StixTraverser:
    def __init__(self, *args):
        self._store = stix2.Environment(
            store=stix2.MemoryStore()
        )
        for obj in args:
            if obj is not None:
                self._store.add(obj)

        self._types = _get_reverse_types()

    def __getattr__(self, item):
        if item in self._types:
            objs = self._store.query([
                stix2.Filter("type", "=", self._types[item])
            ])

            return ListTraverser(*objs, store=self._store)

    def __call__(self, path: str):
        items = path.split('.')
        obj = getattr(self, items[0])
        for item in items[1:]:
            if item.isnumeric():
                obj = obj[int(item)]
            else:
                obj = getattr(obj, item)

        return obj
