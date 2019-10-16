from benchlingapi.models import schema


def test_field_schema():
    s = schema.FieldSchema()
    d = s.load({"isMulti": True, "textValue": None, "type": "dropdown", "value": []})
    print(s.dump(d))
