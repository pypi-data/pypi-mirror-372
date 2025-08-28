from pydantic import TypeAdapter


def json_to_model(model_type: any, json):
    return TypeAdapter(model_type).validate_python(json)
