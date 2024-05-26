import orjson

def build_shema(json):
    json_type = type(json)

    #Currently does not support arrays
    if json_type is dict:
        for key in json:
            build_shema(json[key])        
    elif json_type is str:
        print("string", json)
    elif json_type is float or json_type is int:
        print("number", json)
    elif json_type is bool:
        print("boolean", json)

if __name__ == "__main__":
    example = "{\"message\": \"hello, world!\",\"nested object\": {\"x\": 123,\"y\": 4.56}, \"indicator\": true}"
    json = orjson.loads(example) 

    print()
    print(orjson.dumps(json, option=orjson.OPT_INDENT_2).decode("utf-8"))
    print()
    build_shema(json)