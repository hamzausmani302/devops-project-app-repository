
def get_app_version() -> str:
    with open(".ver", "r") as f:
        content = f.read()
        return content
