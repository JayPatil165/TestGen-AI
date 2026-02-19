from .utils.math_utils import add
from .utils.string_utils import to_upper
from .api.endpoints import get_user

def process_data(data):
    if not data:
        return None
    val = add(10, 20)
    user = get_user(1)
    return to_upper(f"User {user['name']} has value {val}")

if __name__ == "__main__":
    print(process_data("start"))
