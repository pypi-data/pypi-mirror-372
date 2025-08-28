from typing import Any

from ut_obj.uri import Uri

TyUri = str
TyDoUri = dict[Any, TyUri]

TnDoUri = None | TyDoUri
TnUri = None | TyUri


class DoUri:

    @staticmethod
    def sh_uri(d_uri: TnDoUri) -> TnUri:
        if not d_uri:
            return None
        schema = d_uri.get('schema')
        authority = d_uri.get('schema')
        path = d_uri.get('path')
        query = d_uri.get('query')
        _uri = None
        if schema is not None:
            _uri = f"{schema}"
        if authority is not None:
            _uri = f"{_uri}://{authority}"
        if path is not None:
            _uri = f"{_uri}{path}"
        if query is not None:
            _uri = f"{_uri}?{query}"
        return _uri

    @staticmethod
    def sh_uri_with_params(d_uri: TnDoUri, **kwargs) -> TnUri:
        if not d_uri:
            return None
        _uri = DoUri.sh_uri(d_uri)
        params = kwargs.get('params')
        _uri = Uri.add_params(_uri, params)
        return _uri
