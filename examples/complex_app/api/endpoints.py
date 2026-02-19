def get_user(user_id):
    if user_id == 1:
        return {"id": 1, "name": "Alice"}
    return {"id": 0, "name": "Guest"}

def create_user(name):
    return {"id": 99, "name": name}
