from typing import Any, Dict, List, Optional, TypedDict, NotRequired

JSON_API_CONTENT_TYPE = 'application/vnd.api+json'


class JsonApiResource(TypedDict):
    type: str
    id: NotRequired[str]
    attributes: NotRequired[Dict[str, Any]]


class JsonApiResponse(TypedDict):
    data: NotRequired[Any]
    errors: NotRequired['JsonApiError']
    meta: NotRequired[Dict[str, Any]]
    links: NotRequired[Dict[str, Any]]


class JsonApiResourceArrayResponse(JsonApiResponse):
    data: NotRequired[List[JsonApiResource]]


class JsonApiError(TypedDict):
    status: int
    source: Dict[str, str]
    code: NotRequired[str]
    detail: NotRequired[str]


class JsonApiException(Exception):
    def __init__(self, errors: List[JsonApiError], message: Optional[str] = None):
        status = errors[0]['status'] if errors else 500
        message = message or (
            errors[0].get('detail') if errors and 'detail' in errors[0] else errors[0].get('code', '') if errors else ''
        )
        super().__init__(f'{status}: {message}')
        self.errors = errors


def object_to_resource(object: Dict[str, Any], type: str, id_field_name: Optional[str] = None) -> JsonApiResource:
    if id_field_name is None:
        return JsonApiResource(type=type, attributes=object)
    if id_field_name not in object or object[id_field_name] is None:
        raise ValueError(f'undefined ID field {id_field_name} while converting an object to JSON:API {type}')
    return JsonApiResource(type=type, id=str(object[id_field_name]), attributes=object)


def resource_to_object(resource: JsonApiResource, id_field_name: str) -> Dict[str, Any]:
    attributes = resource.get('attributes', {}).copy()
    if 'id' in resource and resource['id'] is not None:
        attributes[id_field_name] = resource['id']
    return attributes


def object_to_jsonapi(object: Dict[str, Any], type: str, id_field_name: Optional[str] = None) -> JsonApiResponse:
    return JsonApiResponse(data=object_to_resource(object, type, id_field_name))


def array_to_jsonapi(
    objects: List[Dict[str, Any]], type: str, id_field_name: Optional[str] = None
) -> JsonApiResourceArrayResponse:
    resources = [object_to_resource(obj, type, id_field_name) for obj in objects]
    return JsonApiResourceArrayResponse(data=resources)


def jsonapi_to_object(response: JsonApiResponse, id_field_name: str) -> Dict[str, Any]:
    if 'data' not in response:
        raise ValueError('calling jsonapi_to_object on response with no data')
    return resource_to_object(response['data'], id_field_name)


def jsonapi_to_object_array(response: JsonApiResourceArrayResponse, id_field_name: str) -> List[Dict[str, Any]]:
    if 'data' not in response:
        raise ValueError('calling jsonapi_to_object_array on response with no data')
    return [resource_to_object(r, id_field_name) for r in response['data']]


class Response:
    def json(self, body: Any) -> Any:
        pass

    def content_type(self, type: str) -> 'Response':
        return self


def send_jsonapi(res: Response, body: JsonApiResponse) -> None:
    res.content_type(JSON_API_CONTENT_TYPE).json(body)


def validate_required_or_fail(value: Any, property_path: str = 'id') -> None:
    if not value:
        message = f'{property_path} cannot be empty'
        raise JsonApiException(
            [
                JsonApiError(
                    code='required', status=422, source={'pointer': f'/data/attributes/{property_path}'}, detail=message
                )
            ],
            message,
        )
