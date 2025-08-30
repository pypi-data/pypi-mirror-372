from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, Mapping, Optional

try:
    from typing_extensions import Self
except ImportError:
    from typing import Self

if TYPE_CHECKING:
    from allspice.allspice import AllSpice

from .exceptions import MissingEqualityImplementation, ObjectIsInvalid, RawRequestEndpointMissing


class ReadonlyApiObject:
    def __init__(self, allspice_client):
        self.allspice_client = allspice_client
        self.deleted = False  # set if .delete was called, so that an exception is risen

    def __str__(self) -> str:
        return "AllSpiceObject (%s):" % (type(self))

    def __eq__(self, other) -> bool:
        """Compare only fields that are part of the gitea-data identity"""
        raise MissingEqualityImplementation()

    def __hash__(self) -> int:
        """Hash only fields that are part of the gitea-data identity"""
        raise MissingEqualityImplementation()

    _fields_to_parsers: ClassVar[dict] = {}

    # TODO: This should probably be made an abstract function as all children
    # redefine it.
    @classmethod
    def request(cls, allspice_client: AllSpice) -> Self:
        # This never would've worked, so maybe we should remove this function
        # outright.
        return cls._request(allspice_client)

    @classmethod
    def _request(cls, allspice_client: AllSpice, args: Mapping) -> Self:
        result = cls._get_gitea_api_object(allspice_client, args)
        api_object = cls.parse_response(allspice_client, result)
        return api_object

    @classmethod
    def _get_gitea_api_object(cls, allspice_client: AllSpice, args: Mapping) -> Mapping:
        """Retrieving an object always as GET_API_OBJECT"""
        if hasattr(cls, "API_OBJECT"):
            raw_request_endpoint = getattr(cls, "API_OBJECT")
            return allspice_client.requests_get(raw_request_endpoint.format(**args))
        else:
            raise RawRequestEndpointMissing()

    @classmethod
    def parse_response(cls, allspice_client: AllSpice, result: Mapping) -> Self:
        # allspice_client.logger.debug("Found api object of type %s (id: %s)" % (type(cls), id))
        api_object = cls(allspice_client)
        cls._initialize(allspice_client, api_object, result)
        return api_object

    @classmethod
    def _initialize(cls, allspice_client: AllSpice, api_object: Self, result: Mapping):
        for name, value in result.items():
            if name in cls._fields_to_parsers and value is not None:
                parse_func = cls._fields_to_parsers[name]
                value = parse_func(allspice_client, value)
            cls._add_read_property(name, value, api_object)
        # add all patchable fields missing in the request to be writable
        for name in cls._fields_to_parsers.keys():
            if not hasattr(api_object, name):
                cls._add_read_property(name, None, api_object)

    @classmethod
    def _add_read_property(cls, name: str, value: Any, api_object: ReadonlyApiObject):
        if not hasattr(api_object, name):
            setattr(api_object, "_" + name, value)
            prop = property((lambda n: lambda self: self._get_var(n))(name))
            setattr(cls, name, prop)
        else:
            raise AttributeError(f"Attribute {name} already exists on api object.")

    def _get_var(self, name: str) -> Any:
        if self.deleted:
            raise ObjectIsInvalid()
        return getattr(self, "_" + name)


class ApiObject(ReadonlyApiObject):
    _patchable_fields: ClassVar[set[str]] = set()

    def __init__(self, allspice_client: AllSpice):
        super().__init__(allspice_client)
        self._dirty_fields = set()

    def _commit(self, route_fields: dict, dirty_fields: Optional[Mapping] = None):
        if self.deleted:
            raise ObjectIsInvalid()
        if not hasattr(self, "API_OBJECT"):
            raise RawRequestEndpointMissing()

        raw_request_endpoint = getattr(self, "API_OBJECT")

        if dirty_fields is None:
            dirty_fields = self.get_dirty_fields()

        self.allspice_client.requests_patch(
            raw_request_endpoint.format(**route_fields),
            dirty_fields,
        )
        self._dirty_fields = set()

    def commit(self):
        raise NotImplementedError()

    _parsers_to_fields: ClassVar[dict] = {}

    def get_dirty_fields(self) -> dict[str, Any]:
        dirty_fields_values = {}
        for field in self._dirty_fields:
            value = getattr(self, field)
            if field in self._parsers_to_fields:
                dirty_fields_values[field] = self._parsers_to_fields[field](value)
            else:
                dirty_fields_values[field] = value
        return dirty_fields_values

    @classmethod
    def _initialize(cls, allspice_client: AllSpice, api_object: Self, result: Mapping):
        super()._initialize(allspice_client, api_object, result)
        for name in cls._patchable_fields:
            cls._add_write_property(name, None, api_object)

    @classmethod
    def _add_write_property(cls, name: str, value: Any, api_object: Self):
        if not hasattr(api_object, "_" + name):
            setattr(api_object, "_" + name, value)
        prop = property(
            (lambda n: lambda self: self._get_var(n))(name),
            (lambda n: lambda self, v: self.__set_var(n, v))(name),
        )
        setattr(cls, name, prop)

    def __set_var(self, name: str, value: Any):
        if self.deleted:
            raise ObjectIsInvalid()
        self._dirty_fields.add(name)
        setattr(self, "_" + name, value)
