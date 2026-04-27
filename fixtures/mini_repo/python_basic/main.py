from helper import helper


# helper is mentioned here as documentation noise.
NOISE = "helper appears in a string but is not a reference"


class Greeter:
    def greet(self, name: str) -> str:
        return helper(name)


def build_message(name: str) -> str:
    value = helper(name)
    return f"Message: {value}"
