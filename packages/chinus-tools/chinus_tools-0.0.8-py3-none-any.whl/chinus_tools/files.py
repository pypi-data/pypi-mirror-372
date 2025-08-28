import json

__all__ = ['Json']


class Json:
    @staticmethod
    def loads(*args, **kwargs):
        return json.loads(*args, **kwargs)

    @staticmethod
    def dumps(*args, **kwargs):
        return json.dumps(*args, **kwargs)

    @staticmethod
    def load(file_path: str, *args, **kwargs):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f, *args, **kwargs)

    @staticmethod
    def dump(obj, file_path: str, *args, **kwargs):
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(obj, f, *args, **kwargs)
