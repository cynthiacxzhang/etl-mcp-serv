import sys
import unittest

# Ensure project src is importable
sys.path.insert(0, "src")

from src.tools import registry


class RegistryTests(unittest.TestCase):
    def tearDown(self):
        # clear the internal registry after each test
        try:
            registry._REGISTRY.clear()
        except Exception:
            pass

    def test_register_and_call_sync(self):
        @registry.tools(name="hello_tool")
        def hello(name: str) -> str:
            return f"hello {name}"

        self.assertIn("hello_tool", registry.list_tools())
        out = registry.call_tool("hello_tool", "world")
        self.assertEqual(out, "hello world")

    def test_register_and_call_async(self):
        @registry.tools(name="async_tool")
        async def async_add(a: int, b: int) -> int:
            return a + b

        self.assertIn("async_tool", registry.list_tools())
        # call via async helper
        import asyncio

        out = asyncio.run(registry.call_tool_async("async_tool", 2, 3))
        self.assertEqual(out, 5)


if __name__ == "__main__":
    unittest.main()
