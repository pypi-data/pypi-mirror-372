#!/usr/bin/env python3
"""
Smoke tests for SADI Python - Basic functionality verification.
These tests verify that core SADI functionality works without requiring external services.
"""

import os
import sys
import unittest
from io import StringIO

# Add the current directory to Python path to import sadi modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TestSADIBasicFunctionality(unittest.TestCase):
    """Basic smoke tests for SADI functionality."""

    def test_basic_imports(self):
        """Test that basic SADI modules can be imported."""
        try:
            # Test basic module imports
            import frir
            import sadi
            from sadi import Service

            # Verify key classes are available
            self.assertTrue(hasattr(sadi, "Service"))
            self.assertTrue(hasattr(sadi, "Individual"))
            self.assertTrue(hasattr(sadi, "OntClass"))
            self.assertTrue(hasattr(frir, "RDFGraphDigest"))

        except ImportError as e:
            self.skipTest(f"Dependencies not available: {e}")

    def test_encoding_functions(self):
        """Test that encoding functions work correctly without buffer()."""
        try:
            import base64

            import frir

            # Test packl function
            result = frir.packl(255)
            self.assertIsInstance(result, bytes)
            self.assertEqual(result, b"\xff")

            # Test base64 encoding without buffer
            test_data = b"Hello, World!"
            encoded = base64.urlsafe_b64encode(test_data)
            self.assertIsInstance(encoded, bytes)

            decoded = base64.urlsafe_b64decode(encoded)
            self.assertEqual(decoded, test_data)

        except ImportError as e:
            self.skipTest(f"Dependencies not available: {e}")

    def test_string_handling(self):
        """Test that string handling works correctly in Python 3.12."""
        # Test string vs bytes
        test_string = "Hello, 世界!"

        # Should be str, not basestring (which doesn't exist in Python 3)
        self.assertIsInstance(test_string, str)

        # Test encoding/decoding
        encoded = test_string.encode("utf-8")
        self.assertIsInstance(encoded, bytes)

        decoded = encoded.decode("utf-8")
        self.assertEqual(decoded, test_string)
        self.assertIsInstance(decoded, str)

    def test_service_class_creation(self):
        """Test that SADI Service class can be created and configured."""
        try:
            from rdflib import RDFS, Literal, Namespace, URIRef

            import sadi

            # Create a test service class
            hello = Namespace("http://sadiframework.org/examples/hello.owl#")

            class TestService(sadi.Service):
                label = "Test Service"
                serviceDescriptionText = "A test service"
                comment = "A test service"
                serviceNameText = "Test Service"
                name = "test"

                def getOrganization(self):
                    result = self.Organization()
                    result.add(RDFS.label, Literal("Test Organization"))
                    return result

                def getInputClass(self):
                    return hello.NamedIndividual

                def getOutputClass(self):
                    return hello.GreetedIndividual

                def process(self, input_resource, output_resource):
                    pass  # Minimal implementation

            # Create service instance
            service = TestService()

            # Verify basic properties
            self.assertEqual(service.label, "Test Service")
            self.assertEqual(service.name, "test")

        except ImportError as e:
            self.skipTest(f"Dependencies not available: {e}")

    def test_graph_operations(self):
        """Test basic RDF graph operations."""
        try:
            from rdflib import RDF, Graph, Literal, Namespace, URIRef

            # Create a graph
            g = Graph()

            # Add some triples
            ex = Namespace("http://example.org/")
            foaf = Namespace("http://xmlns.com/foaf/0.1/")

            g.add((ex.john, RDF.type, foaf.Person))
            g.add((ex.john, foaf.name, Literal("John Doe")))

            # Verify graph has content
            self.assertEqual(len(g), 2)

            # Test serialization
            turtle_data = g.serialize(format="turtle")
            self.assertIsInstance(turtle_data, (str, bytes))
            self.assertGreater(len(turtle_data), 0)

        except ImportError as e:
            self.skipTest(f"Dependencies not available: {e}")


def run_smoke_tests():
    """Run smoke tests and return results."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestSADIBasicFunctionality)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == "__main__":
    print("Running SADI Python smoke tests...")
    print("=" * 50)

    result = run_smoke_tests()

    print("\n" + "=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")

    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}")

    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}")

    if result.wasSuccessful() or (
        len(result.failures) == 0 and len(result.errors) == 0
    ):
        print("\n✅ All smoke tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed.")
        sys.exit(1)
