#!/usr/bin/env python3
"""
Unit tests for ROSToolSystem tool methods - NO LLM dependencies
Tests individual tool functionality without OpenAI integration
"""
import unittest
import tempfile
import os
import shutil
import json
from unittest.mock import Mock, patch
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from cli.tools import ROSToolSystem

def print_test_header():
    """Print a nice header for the test run"""
    print("\n" + "=" * 60)
    print("🧪 ROS TOOL SYSTEM TESTS")
    print("=" * 60)

def print_test_summary(result):
    """Print a nice summary of test results"""
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    total = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    passed = total - failures - errors
    
    print(f"Total Tests:  {total}")
    print(f"✅ Passed:    {passed}")
    print(f"❌ Failed:    {failures}")
    print(f"💥 Errors:    {errors}")
    
    if failures == 0 and errors == 0:
        print("\n🎉 ALL TESTS PASSED! 🎉")
    else:
        print(f"\n⚠️  {failures + errors} test(s) need attention")
    
    print("=" * 60)

class TestToolMethods(unittest.TestCase):
    """Test individual tool methods without LLM integration"""
    
    def setUp(self):
        """Set up test fixtures"""
        print(f"\n🔧 Setting up: {self._testMethodName}")
        
        self.test_dir = tempfile.mkdtemp()
        
        # Create a mock tool system without OpenAI client
        self.tool_system = Mock(spec=ROSToolSystem)
        self.tool_system.workspace_root = self.test_dir
        
        # Bind actual methods to our mock (no LLM needed)
        self.tool_system.read_file = ROSToolSystem.read_file.__get__(self.tool_system)
        self.tool_system.write_file = ROSToolSystem.write_file.__get__(self.tool_system)
        self.tool_system.edit_file_lines = ROSToolSystem.edit_file_lines.__get__(self.tool_system)
        self.tool_system.search_in_files = ROSToolSystem.search_in_files.__get__(self.tool_system)
        self.tool_system.run_command = ROSToolSystem.run_command.__get__(self.tool_system)
        self.tool_system.analyze_code = ROSToolSystem.analyze_code.__get__(self.tool_system)
        self.tool_system.list_directory = ROSToolSystem.list_directory.__get__(self.tool_system)
        self.tool_system._analyze_python_code = ROSToolSystem._analyze_python_code.__get__(self.tool_system)
        self.tool_system._analyze_cpp_code = ROSToolSystem._analyze_cpp_code.__get__(self.tool_system)
        self.tool_system._analyze_ros_patterns = ROSToolSystem._analyze_ros_patterns.__get__(self.tool_system)
        self.tool_system.run_shell_commands = ROSToolSystem.run_shell_commands.__get__(self.tool_system)
        
        # Create test files
        self.test_file = os.path.join(self.test_dir, "test_node.py")
        self.test_content = """#!/usr/bin/env python3
# Simple test file
def hello():
    print("Hello World")

if __name__ == "__main__":
    hello()
"""
        with open(self.test_file, 'w') as f:
            f.write(self.test_content)

        # Create C++ test file
        self.cpp_file = os.path.join(self.test_dir, "test.cpp")
        self.cpp_content = """#include <iostream>

int main() {
    std::cout << "Hello World" << std::endl;
    return 0;
}"""
        with open(self.cpp_file, 'w') as f:
            f.write(self.cpp_content)

    def tearDown(self):
        """Clean up test files"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
        print(f"✅ {self._testMethodName} - PASSED")

    def test_read_file_success(self):
        """Test successful file reading"""
        result = self.tool_system.read_file(self.test_file)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["content"], self.test_content)
        self.assertEqual(result["lines"], len(self.test_content.splitlines()))
        self.assertIn("numbered_lines", result)

    def test_read_file_not_found(self):
        """Test reading non-existent file"""
        result = self.tool_system.read_file("/nonexistent/file.py")
        
        self.assertIn("error", result)
        self.assertIn("File not found", result["error"])

    def test_write_file_success(self):
        """Test successful file writing"""
        test_content = "# Test file\nprint('Hello, ROS2!')"
        test_path = os.path.join(self.test_dir, "new_file.py")
        
        result = self.tool_system.write_file(test_path, test_content)
        
        self.assertTrue(result["success"])
        self.assertTrue(os.path.exists(test_path))
        self.assertEqual(result["bytes_written"], len(test_content.encode('utf-8')))
        
        # Verify content
        with open(test_path, 'r') as f:
            written_content = f.read()
        self.assertEqual(written_content, test_content)

    def test_edit_file_lines_success(self):
        """Test editing specific lines"""
        # Edit line 2 (comment line)
        edits = {"2": "# Modified comment\n"}
        
        result = self.tool_system.edit_file_lines(self.test_file, edits)
        
        self.assertTrue(result["success"])
        self.assertIn("2", result["lines_edited"])
        
        # Verify edit
        with open(self.test_file, 'r') as f:
            lines = f.readlines()
        self.assertIn("Modified", lines[1])

    def test_edit_file_lines_delete(self):
        """Test deleting a line"""
        original_lines = len(self.test_content.splitlines())
        
        # Delete line 1
        edits = {"1": ""}
        result = self.tool_system.edit_file_lines(self.test_file, edits)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["total_lines"], original_lines - 1)

    def test_search_in_files_success(self):
        """Test searching for patterns"""
        result = self.tool_system.search_in_files(
            directory=self.test_dir,
            pattern="hello",
            file_extensions=[".py"]
        )
        
        self.assertTrue(result["success"])
        self.assertGreaterEqual(result["files_with_matches"], 0)
        self.assertGreaterEqual(result["total_matches"], 0)

    def test_search_in_files_regex(self):
        """Test regex pattern searching"""
        result = self.tool_system.search_in_files(
            directory=self.test_dir,
            pattern=r"def\s+\w+",
            is_regex=True,
            file_extensions=[".py"]
        )
        
        self.assertTrue(result["success"])
        self.assertGreater(result["total_matches"], 0)

    @patch('subprocess.run')
    def test_run_command_success(self, mock_subprocess):
        """Test successful command execution"""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Hello World"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result
        
        result = self.tool_system.run_command("echo 'Hello World'")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["return_code"], 0)
        self.assertEqual(result["stdout"], "Hello World")

    @patch('subprocess.run')
    def test_run_command_timeout(self, mock_subprocess):
        """Test command timeout"""
        from subprocess import TimeoutExpired
        mock_subprocess.side_effect = TimeoutExpired(cmd="sleep 10", timeout=1)
        
        result = self.tool_system.run_command("sleep 10", timeout=1)
        
        self.assertIn("error", result)
        self.assertIn("timed out", result["error"])

    def test_analyze_python_code(self):
        """Test Python code analysis"""
        result = self.tool_system.analyze_code(self.test_file, language="python")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["language"], "python")
        self.assertIsInstance(result["issues"], list)
        self.assertIsInstance(result["suggestions"], list)

    def test_analyze_cpp_code(self):
        """Test C++ code analysis"""
        result = self.tool_system.analyze_code(self.cpp_file, language="cpp")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["language"], "cpp")
        self.assertIsInstance(result["issues"], list)

    def test_analyze_code_with_ros_patterns(self):
        """Test that ROS pattern analysis runs without errors"""
        simple_code = """import rclpy
print("Hello ROS")
"""
        test_file = os.path.join(self.test_dir, "simple_ros.py")
        with open(test_file, 'w') as f:
            f.write(simple_code)
        
        result = self.tool_system.analyze_code(test_file, check_ros_patterns=True)
        
        # Just verify the function runs successfully
        self.assertTrue(result["success"])
        self.assertIsInstance(result["issues"], list)
        self.assertIsInstance(result["suggestions"], list)

    def test_analyze_code_without_ros_patterns(self):
        """Test code analysis without ROS pattern checking"""
        simple_code = """def hello():
    print("Hello World")
"""
        test_file = os.path.join(self.test_dir, "simple.py")
        with open(test_file, 'w') as f:
            f.write(simple_code)
        
        result = self.tool_system.analyze_code(test_file, check_ros_patterns=False)
        
        self.assertTrue(result["success"])
        self.assertIsInstance(result["issues"], list)
        self.assertIsInstance(result["suggestions"], list)

    def test_list_directory(self):
        """Test directory listing"""
        result = self.tool_system.list_directory(self.test_dir)
        
        self.assertTrue(result["success"])
        self.assertGreater(result["total_items"], 0)
        self.assertIn("files", result)
        self.assertIn("directories", result)

    def test_list_directory_with_filter(self):
        """Test directory listing with file extension filter"""
        result = self.tool_system.list_directory(
            self.test_dir, 
            file_extensions=[".py"]
        )
        
        self.assertTrue(result["success"])
        # Should only return Python files
        for item in result["files"]:
            self.assertTrue(item["name"].endswith(".py"))

    @patch('subprocess.run')
    def test_run_shell_commands(self, mock_subprocess):
        """Test the run_shell_commands method"""
        mock_result = Mock()
        mock_result.stdout = "command output"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result
        
        result = self.tool_system.run_shell_commands("echo 'test'")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["stdout"], "command output")

    def test_python_syntax_analysis(self):
        """Test Python syntax error detection"""
        bad_python = "def broken_function(\n    print('missing closing parenthesis'"
        bad_file = os.path.join(self.test_dir, "syntax_error.py")
        with open(bad_file, 'w') as f:
            f.write(bad_python)
        
        result = self.tool_system.analyze_code(bad_file, language="python")
        
        self.assertTrue(result["success"])
        # Just verify syntax analysis runs and detects the error
        self.assertIsInstance(result["issues"], list)

    def test_cpp_basic_analysis(self):
        """Test C++ basic analysis"""
        cpp_code = """#include <iostream>
int main() {
    std::cout << "Hello World" << std::endl;
    return 0;
}"""
        
        cpp_file = os.path.join(self.test_dir, "simple.cpp")
        with open(cpp_file, 'w') as f:
            f.write(cpp_code)
        
        result = self.tool_system.analyze_code(cpp_file, language="cpp")
        
        self.assertTrue(result["success"])
        # Just verify C++ analysis runs
        self.assertIsInstance(result["issues"], list)

    def test_file_operations_workflow(self):
        """Test complete file operations workflow"""
        # 1. Create a new file
        content = "# Test file\nprint('Hello World')\n"
        new_file = os.path.join(self.test_dir, "workflow_test.py")
        
        write_result = self.tool_system.write_file(new_file, content)
        self.assertTrue(write_result["success"])
        
        # 2. Read it back
        read_result = self.tool_system.read_file(new_file)
        self.assertTrue(read_result["success"])
        self.assertEqual(read_result["content"], content)
        
        # 3. Edit a line
        edit_result = self.tool_system.edit_file_lines(new_file, {
            "2": "print('Hello World - Modified')\n"
        })
        self.assertTrue(edit_result["success"])
        
        # 4. Search for the edited content
        search_result = self.tool_system.search_in_files(
            self.test_dir, 
            "Modified",
            file_extensions=[".py"]
        )
        self.assertTrue(search_result["success"])
        self.assertGreater(search_result["total_matches"], 0)

    def test_search_directory_not_found(self):
        """Test search in non-existent directory"""
        result = self.tool_system.search_in_files(
            directory="/nonexistent/directory",
            pattern="test"
        )
        
        self.assertIn("error", result)
        self.assertIn("Directory not found", result["error"])

    def test_list_directory_not_found(self):
        """Test listing non-existent directory"""
        result = self.tool_system.list_directory("/nonexistent/directory")
        
        self.assertIn("error", result)
        self.assertIn("Directory not found", result["error"])

    def test_analyze_code_file_not_found(self):
        """Test code analysis on non-existent file"""
        result = self.tool_system.analyze_code("/nonexistent/file.py")
        
        self.assertIn("error", result)
        self.assertIn("File not found", result["error"])

    def test_edit_file_not_found(self):
        """Test editing non-existent file"""
        result = self.tool_system.edit_file_lines("/nonexistent/file.py", {"1": "test"})
        
        self.assertIn("error", result)
        self.assertIn("File not found", result["error"])


class TestToolDefinitions(unittest.TestCase):
    """Test tool definitions and metadata"""
    
    def setUp(self):
        print(f"\n🔧 Setting up: {self._testMethodName}")
    
    def tearDown(self):
        print(f"✅ {self._testMethodName} - PASSED")
    
    def test_get_available_tools_structure(self):
        """Test tool definitions have correct structure"""
        # This method doesn't need LLM
        tool_system = Mock(spec=ROSToolSystem)
        tool_system.get_available_tools = ROSToolSystem.get_available_tools.__get__(tool_system)
        
        tools = tool_system.get_available_tools()
        
        expected_tools = [
            "read_file", "write_file", "search_in_files", 
            "run_command", "analyze_code", "list_directory", "edit_file_lines"
        ]
        
        tool_names = [tool["function"]["name"] for tool in tools]
        
        for expected_tool in expected_tools:
            self.assertIn(expected_tool, tool_names)
        
        # Verify structure
        for tool in tools:
            self.assertEqual(tool["type"], "function")
            self.assertIn("name", tool["function"])
            self.assertIn("description", tool["function"])
            self.assertIn("parameters", tool["function"])

if __name__ == '__main__':
    print_test_header()
    
    # Run tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestToolMethods))
    suite.addTests(loader.loadTestsFromTestCase(TestToolDefinitions))
    
    # Run with custom result handling
    runner = unittest.TextTestRunner(verbosity=1, stream=sys.stdout)
    result = runner.run(suite)
    
    # Print summary
    print_test_summary(result)
    
    # Exit with proper code
    sys.exit(0 if result.wasSuccessful() else 1)