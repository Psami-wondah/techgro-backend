def serialize_dict(a) -> dict:
    return {**{'_id':str(a[i]) for i in a if i == '_id'}, **{i:a[i] for i in a if i != '_id'}}

def serialize_list(a) -> list:
    return [serialize_dict(i) for i in a ]

def auth_serializer(a) -> dict:
    return {**{'id':str(a[i]) for i in a if i == '_id'}, **{i:a[i] for i in a if i != '_id' }}