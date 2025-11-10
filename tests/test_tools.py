import unittest

from src.tools import tools, list_tools, get_tool, call_tool


class ToolsRegistryTests(unittest.TestCase):
    def tearDown(self):
        # tests register functions in memory; if needed, reload module to reset registry
        pass

    def test_register_and_get_tool(self):
        @tools(name="hello_tool", description="returns hello")
        def hello(name: str) -> str:
            return f"hello {name}"

        info = get_tool("hello_tool")
        self.assertIsNotNone(info)
        self.assertEqual(info.name, "hello_tool")
        self.assertEqual(info.description, "returns hello")
        self.assertEqual(call_tool("hello_tool", "world"), "hello world")

    def test_decorator_without_args(self):
        @tools
        def add(a: int, b: int) -> int:
            return a + b

        info = get_tool("add")
        self.assertIsNotNone(info)
        self.assertEqual(call_tool("add", 2, 3), 5)


if __name__ == "__main__":
    unittest.main()
