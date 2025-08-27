# pylint: disable-all

import __init__ as castnet
from types import SimpleNamespace


def dog_name(params):
    print(f"this new dog's name is {params['name']}")


SCHEMA = {
    "Dog": {
        "attributes": {"cuteness": int, "breed": str, "tricks": str},
        "callbacks": [
            {"methods": "POST", "attributes": ["name"], "callback": dog_name},
            {
                "methods": "POST",
                "attributes": ["source_id"],
                "callback": lambda x: print(x["source_id"]),
            },
            {
                "methods": "POST",
                "attributes": ["tricks"],
                "callback": lambda x: print(x["tricks"]),
            },
            {
                "methods": "POST",
                "attributes": ["tricks", "cuteness"],
                "callback": lambda x: print(x["cuteness"]),
            },
        ],
    },
    "Person": {
        "attributes": {"lastName": str, "age": int, "petPreference": str},
        "relationships": {"HAS_CAT": "Cat", "HAS_DOG": "Dog"},
    },
    "Cat": {"attributes": {"cuteness": int, "breed": str, "chaos": int}},
}

URL_KEY = {"cats": "Cat", "dogs": "Dog", "people": "Person"}

conn = castnet.CastNetConn(None, "jrejci", None, SCHEMA, URL_KEY)

request = SimpleNamespace()
request.json = {"id": "dog1", "name": "pupper", "cuteness": 10}
request.method = "POST"
request.path = "/dogs"

conn.generic_post(request)
