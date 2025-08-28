import json


def pprint(obj) -> None:
    print(
        json.dumps(
            vars(obj),
            indent=2,
            default=lambda o: o.__dict__,
            ensure_ascii=False
        )
    )
