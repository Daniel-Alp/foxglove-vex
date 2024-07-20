def build_schema(json) -> dict:
    if isinstance(json, dict):
        schema = {}
        schema["type"] = "object"
        schema["properties"] = {}
        for key in json:
            schema["properties"][key] = build_schema(json[key])
        return schema
    
    elif isinstance(json, str):
        return {"type": "string"}   
    
    elif isinstance(json, float) or isinstance(json, int):
        return {"type": "number"}
    
    elif isinstance(json, bool):
        return {"type": "boolean"}

if __name__ == "__main__":
    pass
