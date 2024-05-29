def build_shema(json) -> dict:
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
    pass
