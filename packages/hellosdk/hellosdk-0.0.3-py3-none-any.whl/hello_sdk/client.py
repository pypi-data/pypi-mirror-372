class HelloClient:
    def __init__(self, greeting="Hello"):
        self.greeting = greeting

    def say_hello(self, name: str) -> str:
        return f"{self.greeting}, {name}!"
