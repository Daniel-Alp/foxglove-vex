import orjson

def build_shema(json):
    json_type = type(json)
    if json_type is dict:
        schema = {}
        schema["type"] = "object"
        schema["properties"] = {}
        for key in json:
            schema["properties"][key] = build_shema(json[key])
        return schema

    elif json_type is str:
        return {"type": "string"}   
    
    elif json_type is float or json_type is int:
        return {"type": "number"}
    
    elif json_type is bool:
        return {"type": "boolean"}

if __name__ == "__main__":
    example = "{\"message\": \"hello, world!\",\"nested object\": {\"x\": 123,\"y\": 4.56}, \"indicator\": true}"
    json = orjson.loads(example) 
    schema = build_shema(json)

    print()
    print(orjson.dumps(json, option=orjson.OPT_INDENT_2).decode("utf-8"))
    print()
    print(orjson.dumps(schema, option=orjson.OPT_INDENT_2).decode("utf-8"))
