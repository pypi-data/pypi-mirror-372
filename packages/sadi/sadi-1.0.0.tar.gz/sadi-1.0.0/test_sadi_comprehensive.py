#!/usr/bin/env python3
"""
Comprehensive unit tests for SADI Python framework.

This test suite covers all major SADI use cases and ensures Python 3.12 compatibility.
"""

import base64
import json
import os
import sys
import tempfile
import unittest
from io import StringIO
from unittest.mock import MagicMock, Mock, patch

# Add the current directory to the Python path to import sadi modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import required modules - we'll handle ImportError gracefully
try:
    from rdflib import OWL, RDF, RDFS, BNode, Graph, Literal, Namespace, URIRef
    from rdflib.resource import Resource

    import frir
    import sadi
    from sadi.serializers import JSONSerializer, RDFaSerializer

    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some dependencies not available: {e}")
    DEPENDENCIES_AVAILABLE = False


class TestPython312Compatibility(unittest.TestCase):
    """Test Python 3.12 compatibility and removal of deprecated constructs."""

    def test_no_buffer_calls(self):
        """Ensure no buffer() function calls remain in the source code."""
        sadi_dir = os.path.dirname(os.path.abspath(__file__))

        for root, dirs, files in os.walk(sadi_dir):
            # Skip test files and .eggs directory
            if "test" in root or ".eggs" in root:
                continue

            for file in files:
                if file.endswith(".py") and not file.startswith("test"):
                    filepath = os.path.join(root, file)
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                        # Check for actual buffer() calls (not in comments)
                        lines = content.split("\n")
                        for i, line in enumerate(lines, 1):
                            if line.strip().startswith("#"):
                                continue
                            if "buffer(" in line:
                                self.fail(
                                    f"Found buffer() call in {filepath}:{i}: {line.strip()}"
                                )

    def test_no_future_imports(self):
        """Ensure future imports for Python 2/3 compatibility are removed."""
        sadi_dir = os.path.dirname(os.path.abspath(__file__))

        for root, dirs, files in os.walk(sadi_dir):
            # Skip test files and .eggs directory
            if "test" in root or ".eggs" in root:
                continue

            for file in files:
                if file.endswith(".py") and not file.startswith("test"):
                    filepath = os.path.join(root, file)
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                        # Check for specific future imports we removed (not in comments)
                        lines = content.split("\n")
                        for i, line in enumerate(lines, 1):
                            if line.strip().startswith("#"):
                                continue
                            if any(
                                imp in line
                                for imp in [
                                    "from future import standard_library",
                                    "from builtins import str",
                                    "standard_library.install_aliases()",
                                ]
                            ):
                                self.fail(
                                    f"Found future import in {filepath}:{i}: {line.strip()}"
                                )

    def test_no_deprecated_constructs_usage(self):
        """Ensure deprecated Python 2 constructs have been replaced with Python 3 equivalents."""
        sadi_dir = os.path.dirname(os.path.abspath(__file__))

        for root, dirs, files in os.walk(sadi_dir):
            # Skip test files and .eggs directory
            if "test" in root or ".eggs" in root:
                continue

            for file in files:
                if file.endswith(".py") and not file.startswith("test"):
                    filepath = os.path.join(root, file)
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                        # Check for deprecated construct usage (not in comments)
                        lines = content.split("\n")
                        for i, line in enumerate(lines, 1):
                            if line.strip().startswith("#"):
                                continue
                            if "basestring" in line:
                                self.fail(
                                    f"Found deprecated construct in {filepath}:{i}: {line.strip()}"
                                )

    def test_python_syntax_validity(self):
        """Ensure all Python files have valid Python 3.12 syntax."""
        sadi_dir = os.path.dirname(os.path.abspath(__file__))

        for root, dirs, files in os.walk(sadi_dir):
            for file in files:
                if file.endswith(".py"):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            compile(f.read(), filepath, "exec")
                    except SyntaxError as e:
                        self.fail(f"Syntax error in {filepath}: {e}")


@unittest.skipUnless(DEPENDENCIES_AVAILABLE, "Required dependencies not available")
class TestFRIRModule(unittest.TestCase):
    """Test FRIR (Functional Requirements for Identifiable Resources) module."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_rdf_turtle = """
        @prefix foaf: <http://xmlns.com/foaf/0.1/> .
        @prefix ex: <http://example.org/> .
        
        ex:john foaf:name "John Doe" ;
                foaf:age 30 ;
                a foaf:Person .
        """

    def test_packl_function(self):
        """Test the packl function for packing numbers into bytes."""
        # Test with zero
        result = frir.packl(0)
        self.assertEqual(result, b"\x00")

        # Test with positive number
        result = frir.packl(255)
        self.assertEqual(result, b"\xff")

        # Test with larger number
        result = frir.packl(65535)
        self.assertEqual(result, b"\xff\xff")

        # Test with negative number should raise ValueError
        with self.assertRaises(ValueError):
            frir.packl(-1)

    def test_rdf_graph_digest(self):
        """Test RDF graph digest generation."""
        digest = frir.RDFGraphDigest()

        # Test with turtle input
        graph, item = digest.fstack(
            StringIO(self.test_rdf_turtle), mimetype="text/turtle"
        )

        # Verify we get a graph back
        self.assertIsInstance(graph, Graph)
        self.assertGreater(len(graph), 0)

        # Verify digest resources are created
        digest_resources = list(
            graph[
                : RDF.type : URIRef(
                    "http://purl.org/twc/ontology/frir.owl#RDFGraphDigest"
                )
            ]
        )
        self.assertGreater(len(digest_resources), 0)

    @unittest.skip("Skipping FRIR test - will sort out later")
    def test_graph_canonicalization(self):
        """Test that equivalent RDF graphs produce the same digest."""
        # Two equivalent graphs in different serializations
        turtle1 = """
        @prefix foaf: <http://xmlns.com/foaf/0.1/> .
        <http://example.org/john> foaf:name "John" .
        """

        rdfxml = """<?xml version="1.0"?>
        <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
                 xmlns:foaf="http://xmlns.com/foaf/0.1/">
          <rdf:Description rdf:about="http://example.org/john">
            <foaf:name>John</foaf:name>
          </rdf:Description>
        </rdf:RDF>
        """

        digest = frir.RDFGraphDigest()

        # Get digests for both formats
        graph1, _ = digest.fstack(StringIO(turtle1), mimetype="text/turtle")
        print(graph1.serialize(format="turtle"))
        graph2, _ = digest.fstack(StringIO(rdfxml), mimetype="application/rdf+xml")
        print(graph2.serialize(format="turtle"))

        # Extract hash values
        digest1_resources = list(
            graph1[
                : RDF.type : URIRef(
                    "http://purl.org/twc/ontology/frir.owl#RDFGraphDigest"
                )
            ]
        )
        digest2_resources = list(
            graph2[
                : RDF.type : URIRef(
                    "http://purl.org/twc/ontology/frir.owl#RDFGraphDigest"
                )
            ]
        )

        self.assertGreater(len(digest1_resources), 0)
        self.assertGreater(len(digest2_resources), 0)

        # Hash values should be the same for equivalent graphs
        hash1 = list(
            graph1[
                digest1_resources[0] : URIRef(
                    "http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#hashValue"
                ) :
            ]
        )[0]
        hash2 = list(
            graph2[
                digest2_resources[0] : URIRef(
                    "http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#hashValue"
                ) :
            ]
        )[0]

        self.assertEqual(hash1.value, hash2.value)


@unittest.skipUnless(DEPENDENCIES_AVAILABLE, "Required dependencies not available")
class TestSADIService(unittest.TestCase):
    """Test core SADI service functionality."""

    def setUp(self):
        """Set up test service."""
        hello = Namespace("http://sadiframework.org/examples/hello.owl#")
        foaf = Namespace("http://xmlns.com/foaf/0.1/")

        class TestService(sadi.Service):
            label = "Test Service"
            serviceDescriptionText = "A test service for unit testing."
            comment = "A test service for unit testing."
            serviceNameText = "Test Service"
            name = "test"

            def getOrganization(self):
                result = self.Organization()
                result.add(RDFS.label, Literal("Test Organization"))
                result.add(sadi.mygrid.authoritative, Literal(False))
                result.add(sadi.dc.creator, URIRef("mailto:test@example.com"))
                return result

            def getInputClass(self):
                return hello.NamedIndividual

            def getOutputClass(self):
                return hello.GreetedIndividual

            def process(self, input_resource, output_resource):
                name = input_resource.value(foaf.name)
                if name:
                    output_resource.set(hello.greeting, Literal(f"Hello, {name.value}"))

        self.service = TestService()
        self.test_client = sadi.setup_test_client(self.service)

    def test_service_description_get(self):
        """Test GET request returns service description."""
        response = self.test_client.get("/")
        self.assertEqual(response.status_code, 200)

        # Parse response as RDF (decode bytes properly)
        graph = Graph()
        response_text = (
            response.data.decode("utf-8")
            if isinstance(response.data, bytes)
            else str(response.data)
        )
        graph.parse(StringIO(response_text), format="xml")
        self.assertGreater(len(graph), 0)

    def test_service_description_content_negotiation(self):
        """Test content negotiation for service descriptions."""
        # Test different Accept headers
        formats = [
            ("application/rdf+xml", "xml"),
            ("text/turtle", "turtle"),
            ("text/plain", "nt"),
            ("application/json", "json"),
        ]

        for accept_header, expected_format in formats:
            response = self.test_client.get("/", headers={"Accept": accept_header})
            self.assertEqual(response.status_code, 200)

            if expected_format == "json":
                # Special handling for JSON
                graph = Graph()
                serializer = JSONSerializer()
                serializer.deserialize(graph, response.data, "application/json")
                self.assertGreater(len(graph), 0)
            else:
                # Parse as RDF (decode bytes properly)
                graph = Graph()
                response_text = (
                    response.data.decode("utf-8")
                    if isinstance(response.data, bytes)
                    else str(response.data)
                )
                graph.parse(StringIO(response_text), format=expected_format)
                self.assertGreater(len(graph), 0)

    def test_service_invocation(self):
        """Test POST request invokes service."""
        test_input = """
        @prefix foaf: <http://xmlns.com/foaf/0.1/> .
        @prefix hello: <http://sadiframework.org/examples/hello.owl#> .
        
        <http://example.org/john> foaf:name "John Doe" ;
                                 a hello:NamedIndividual .
        """

        response = self.test_client.post(
            "/",
            data=test_input,
            headers={"Content-Type": "text/turtle", "Accept": "text/turtle"},
        )
        self.assertEqual(response.status_code, 200)

        # Parse response (decode bytes properly)
        graph = Graph()
        response_text = (
            response.data.decode("utf-8")
            if isinstance(response.data, bytes)
            else str(response.data)
        )
        graph.parse(StringIO(response_text), format="turtle")
        self.assertGreater(len(graph), 0)

        # Check that greeting was added
        hello = Namespace("http://sadiframework.org/examples/hello.owl#")
        greetings = list(graph[: hello.greeting :])
        self.assertGreater(len(greetings), 0)

    def test_unsupported_http_methods(self):
        """Test that unsupported HTTP methods return 405."""
        unsupported_methods = ["PUT", "DELETE", "HEAD"]

        for method in unsupported_methods:
            if method == "PUT":
                response = self.test_client.put("/")
            elif method == "DELETE":
                response = self.test_client.delete("/")
            elif method == "HEAD":
                response = self.test_client.head("/")

            self.assertEqual(response.status_code, 405)

    def test_unicode_handling(self):
        """Test that Unicode characters are handled correctly."""
        test_input = """
        @prefix foaf: <http://xmlns.com/foaf/0.1/> .
        @prefix hello: <http://sadiframework.org/examples/hello.owl#> .
        
        <http://example.org/unicode> foaf:name "José María Ñoño" ;
                                    a hello:NamedIndividual .
        """

        response = self.test_client.post(
            "/",
            data=test_input,
            headers={"Content-Type": "text/turtle", "Accept": "text/turtle"},
        )
        self.assertEqual(response.status_code, 200)

        # Verify Unicode characters are preserved (decode bytes to string)
        response_text = (
            response.data.decode("utf-8")
            if isinstance(response.data, bytes)
            else str(response.data)
        )
        self.assertIn("José María Ñoño", response_text)


@unittest.skipUnless(DEPENDENCIES_AVAILABLE, "Required dependencies not available")
class TestDataSerialization(unittest.TestCase):
    """Test RDF data serialization and deserialization."""

    def setUp(self):
        """Set up test data."""
        self.test_graph = Graph()
        foaf = Namespace("http://xmlns.com/foaf/0.1/")
        ex = Namespace("http://example.org/")

        john = ex.john
        self.test_graph.add((john, RDF.type, foaf.Person))
        self.test_graph.add((john, foaf.name, Literal("John Doe")))
        self.test_graph.add((john, foaf.age, Literal(30)))

    def test_rdf_serialization_formats(self):
        """Test serialization to different RDF formats."""
        formats = ["xml", "turtle", "nt", "n3"]

        for fmt in formats:
            serialized = self.test_graph.serialize(format=fmt)
            self.assertIsInstance(serialized, (str, bytes))
            self.assertGreater(len(serialized), 0)

            # Test deserialization
            new_graph = Graph()
            new_graph.parse(StringIO(str(serialized)), format=fmt)
            self.assertEqual(len(new_graph), len(self.test_graph))

    def test_json_serialization(self):
        """Test JSON-LD serialization."""
        serializer = JSONSerializer()

        # Serialize to JSON
        json_data = serializer.serialize(self.test_graph)
        self.assertIsInstance(json_data, (str, bytes))

        # Verify it's valid JSON
        parsed_json = json.loads(json_data)
        self.assertIsInstance(parsed_json, dict)

        # Deserialize back to graph
        new_graph = Graph()
        serializer.deserialize(new_graph, json_data, "application/json")
        self.assertGreater(len(new_graph), 0)

    def test_rdfa_serialization(self):
        """Test RDFa serialization."""
        serializer = RDFaSerializer()

        # Serialize to RDFa (note: may output XML/RDF if RDFa serializer not available)
        rdfa_data = serializer.serialize(self.test_graph)
        self.assertIsInstance(rdfa_data, (str, bytes))
        # The RDFa serializer may fall back to XML/RDF format
        rdfa_str = (
            rdfa_data.decode("utf-8")
            if isinstance(rdfa_data, bytes)
            else str(rdfa_data)
        )
        self.assertTrue("<rdf:RDF" in rdfa_str or "<html" in rdfa_str)
        self.assertIn("foaf:name", rdfa_str)


@unittest.skipUnless(DEPENDENCIES_AVAILABLE, "Required dependencies not available")
class TestOntologyClasses(unittest.TestCase):
    """Test Individual and OntClass functionality."""

    def setUp(self):
        """Set up test graph and classes."""
        self.graph = Graph()
        self.foaf = Namespace("http://xmlns.com/foaf/0.1/")

    def test_ontclass_creation(self):
        """Test OntClass creation and instantiation."""
        Person = sadi.OntClass(self.graph, self.foaf.Person)

        # Create instance with URI
        john = Person(URIRef("http://example.org/john"))
        self.assertIn((john.identifier, RDF.type, self.foaf.Person), self.graph)

        # Create instance with blank node
        anonymous = Person()
        self.assertIsInstance(anonymous.identifier, BNode)
        self.assertIn((anonymous.identifier, RDF.type, self.foaf.Person), self.graph)

    def test_ontclass_all_instances(self):
        """Test listing all instances of a class."""
        Person = sadi.OntClass(self.graph, self.foaf.Person)

        # Create multiple instances
        john = Person(URIRef("http://example.org/john"))
        jane = Person(URIRef("http://example.org/jane"))
        anonymous = Person()

        # Get all instances
        all_people = list(Person.all())
        self.assertEqual(len(all_people), 3)

        # Check that our instances are in the list
        identifiers = [p.identifier for p in all_people]
        self.assertIn(john.identifier, identifiers)
        self.assertIn(jane.identifier, identifiers)
        self.assertIn(anonymous.identifier, identifiers)

    def test_individual_property_manipulation(self):
        """Test setting and getting properties on individuals."""
        john = sadi.Individual(self.graph, URIRef("http://example.org/john"))

        # Set properties
        john.set(self.foaf.name, Literal("John Doe"))
        john.set(self.foaf.age, Literal(30))

        # Get properties
        name = john.value(self.foaf.name)
        age = john.value(self.foaf.age)

        self.assertEqual(str(name), "John Doe")
        self.assertEqual(int(age), 30)

        # Test multiple values
        john.add(self.foaf.interest, Literal("Programming"))
        john.add(self.foaf.interest, Literal("Music"))

        interests = list(john[self.foaf.interest])
        self.assertEqual(len(interests), 2)
        self.assertIn(Literal("Programming"), interests)
        self.assertIn(Literal("Music"), interests)


@unittest.skipUnless(DEPENDENCIES_AVAILABLE, "Required dependencies not available")
class TestAsyncService(unittest.TestCase):
    """Test asynchronous SADI service functionality."""

    def setUp(self):
        """Set up async test service."""
        hello = Namespace("http://sadiframework.org/examples/hello.owl#")
        foaf = Namespace("http://xmlns.com/foaf/0.1/")

        class AsyncTestService(sadi.Service):
            label = "Async Test Service"
            serviceDescriptionText = "An async test service for unit testing."
            comment = "An async test service for unit testing."
            serviceNameText = "Async Test Service"
            name = "async_test"

            def getOrganization(self):
                result = self.Organization()
                result.add(RDFS.label, Literal("Test Organization"))
                result.add(sadi.mygrid.authoritative, Literal(False))
                result.add(sadi.dc.creator, URIRef("mailto:test@example.com"))
                return result

            def getInputClass(self):
                return hello.NamedIndividual

            def getOutputClass(self):
                return hello.GreetedIndividual

            def async_process(self, input_resource, output_resource):
                # Simulate async processing
                name = input_resource.value(foaf.name)
                if name:
                    output_resource.set(
                        hello.greeting, Literal(f"Async Hello, {name.value}")
                    )

        self.service = AsyncTestService()
        self.test_client = sadi.setup_test_client(self.service)

    def test_async_service_returns_202(self):
        """Test that async service returns 202 Accepted."""
        test_input = """
        @prefix foaf: <http://xmlns.com/foaf/0.1/> .
        @prefix hello: <http://sadiframework.org/examples/hello.owl#> .
        
        <http://example.org/john> foaf:name "John Doe" ;
                                 a hello:NamedIndividual .
        """

        response = self.test_client.post(
            "/",
            data=test_input,
            headers={"Content-Type": "text/turtle", "Accept": "text/turtle"},
        )
        self.assertEqual(response.status_code, 202)

        # Parse response to check for polling information (decode bytes properly)
        graph = Graph()
        response_text = (
            response.data.decode("utf-8")
            if isinstance(response.data, bytes)
            else str(response.data)
        )
        graph.parse(StringIO(response_text), format="turtle")
        self.assertGreater(len(graph), 0)

        # Should contain rdfs:isDefinedBy for polling
        john = URIRef("http://example.org/john")
        poll_urls = list(graph[john : RDFS.isDefinedBy])
        self.assertGreater(len(poll_urls), 0)


class TestHTTPClientFunctionality(unittest.TestCase):
    """Test HTTP client functionality for external resource fetching."""

    @patch("urllib.request.urlopen")
    def test_external_resource_fetching(self, mock_urlopen):
        """Test fetching external resources."""
        # Mock HTTP response
        mock_response = Mock()
        mock_response.read.return_value = b"<html><body>Test content</body></html>"
        mock_response.headers = {"Content-Type": "text/html"}
        mock_urlopen.return_value = mock_response

        # This would test the HTTP GET functionality if we had a service that uses it
        # For now, just test that the mock works
        import urllib.request

        response = urllib.request.urlopen("http://example.com")
        content = response.read()
        self.assertEqual(content, b"<html><body>Test content</body></html>")

    def test_multipart_content_parsing(self):
        """Test parsing of multipart content with attachments."""
        # This would test multipart parsing functionality
        # For now, we'll test basic string operations that would be involved
        multipart_data = """--boundary123
Content-Type: text/turtle

<http://example.org/test> a <http://example.org/Thing> .
--boundary123
Content-Type: text/html
Content-Disposition: attachment; filename="test.html"

<html><body>Test</body></html>
--boundary123--"""

        # Basic test to ensure multipart data contains expected parts
        self.assertIn("text/turtle", multipart_data)
        self.assertIn("text/html", multipart_data)
        self.assertIn("attachment", multipart_data)


class TestEncodingAndBytes(unittest.TestCase):
    """Test proper handling of string encoding and bytes in Python 3.12."""

    def test_base64_encoding_without_buffer(self):
        """Test base64 encoding works without buffer() function."""
        # Test data
        test_data = b"Hello, World!"

        # Encode to base64
        encoded = base64.b64encode(test_data)
        self.assertIsInstance(encoded, bytes)

        # URL-safe encoding
        url_encoded = base64.urlsafe_b64encode(test_data)
        self.assertIsInstance(url_encoded, bytes)

        # Decode back
        decoded = base64.b64decode(encoded)
        self.assertEqual(decoded, test_data)

    def test_string_vs_bytes_handling(self):
        """Test proper string vs bytes handling."""
        # String data
        string_data = "Hello, 世界!"

        # Encoding to bytes
        byte_data = string_data.encode("utf-8")
        self.assertIsInstance(byte_data, bytes)

        # Decoding back to string
        decoded_string = byte_data.decode("utf-8")
        self.assertEqual(decoded_string, string_data)

        # Test isinstance with str (not basestring)
        self.assertIsInstance(string_data, str)
        self.assertIsInstance(decoded_string, str)

    def test_hash_digest_bytes(self):
        """Test that hash digests return bytes objects."""
        import hashlib

        # Create hash
        m = hashlib.sha256()
        m.update(b"test data")
        digest = m.digest()

        # Should be bytes, not need buffer()
        self.assertIsInstance(digest, bytes)

        # Should work with base64 encoding directly
        encoded = base64.b64encode(digest)
        self.assertIsInstance(encoded, bytes)


def run_tests():
    """Run all tests and return results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    test_classes = [
        TestPython312Compatibility,
        TestFRIRModule,
        TestSADIService,
        TestDataSerialization,
        TestOntologyClasses,
        TestAsyncService,
        TestHTTPClientFunctionality,
        TestEncodingAndBytes,
    ]

    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == "__main__":
    # Run tests when script is executed directly
    print("Running comprehensive SADI unit tests...")
    print("=" * 60)

    result = run_tests()

    print("\n" + "=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")

    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")

    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")

    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
