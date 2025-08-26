import unittest
from hello_sdk import HelloClient

class TestHelloClient(unittest.TestCase):

    def test_say_hello(self):
        client = HelloClient()
        self.assertEqual(client.say_hello("World"), "Hello, World!")

    def test_say_bonjour(self):
        client = HelloClient(greeting="Bonjour")
        self.assertEqual(client.say_hello("PyPI"), "Bonjour, PyPI!")

    def test_empty_name(self):
        client = HelloClient()
        self.assertEqual(client.say_hello(""), "Hello, !")

    def test_whitespace_name(self):
        client = HelloClient()
        self.assertEqual(client.say_hello("   "), "Hello,    !")

    def test_custom_greeting(self):
        client = HelloClient(greeting="Hey")
        self.assertEqual(client.say_hello("Alice"), "Hey, Alice!")

    def test_numeric_name(self):
        client = HelloClient()
        self.assertEqual(client.say_hello("123"), "Hello, 123!")

    def test_special_chars(self):
        client = HelloClient()
        self.assertEqual(client.say_hello("@user#1"), "Hello, @user#1!")

    def test_unicode_name(self):
        client = HelloClient()
        self.assertEqual(client.say_hello("世界"), "Hello, 世界!")

    def test_long_name(self):
        name = "A" * 1000
        client = HelloClient()
        self.assertEqual(client.say_hello(name), f"Hello, {name}!")

    def test_change_greeting_after_init(self):
        client = HelloClient()
        client.greeting = "Hola"
        self.assertEqual(client.say_hello("Mundo"), "Hola, Mundo!")

if __name__ == "__main__":
    unittest.main()
