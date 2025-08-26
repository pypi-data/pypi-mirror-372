class Util:

    @staticmethod
    def add_url_path(base_url: str, path: str) -> str:
        return f"{base_url.rstrip('/')}/{path.lstrip('/')}"