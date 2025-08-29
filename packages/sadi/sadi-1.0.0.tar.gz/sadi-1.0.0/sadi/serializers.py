# Python 3.12 compatibility: removed future library dependencies and imp module
# from builtins import str, object  # These are built-in in Python 3
import collections
import email
import json
import sys

# import imp  # Removed in Python 3.12 - not needed for UTF-8 default encoding
from io import BytesIO, StringIO
from xml.sax.xmlreader import InputSource

import rdflib
from rdflib import *

from . import mimeparse

# Python 3.12 compatibility: setDefaultEncoding not needed since UTF-8 is default
# def setDefaultEncoding():
#     currentStdOut = sys.stdout
#     currentStdIn = sys.stdin
#     currentStdErr = sys.stderr
#
#     imp.reload(sys)
#     # sys.setdefaultencoding('utf-8')
#
#     sys.stdout = currentStdOut
#     sys.stdin = currentStdIn
#     sys.stderr = currentStdErr

# setDefaultEncoding()  # Not needed in Python 3.12

frir = Namespace("http://purl.org/twc/ontology/frir.owl#")


class CSVSerializer(object):
    def __init__(self, delimiter=","):
        self.delimiter = delimiter

    def serialize(self, graph):
        return None  # Not implemented

    def deserialize(self, graph, content):
        reader = csv.reader(StringIO(content), delimiter=self.delimiter)
        rowNum = 1
        for row in reader:
            rowURI = URIRef("row:" + str(rowNum))
            colNum = 1
            for value in row:
                colURI = URIRef("column:" + str(colNum))
                # if len(value) > 0:
                graph.add((rowURI, colURI, Literal(value)))
                colNum += 1
            rowNum += 1
        return frir.TabularDigest


class DefaultSerializer(object):
    def __init__(self, inputFormat, outputFormat=None, graphAware=False):
        self.inputFormat = inputFormat
        if outputFormat == None:
            self.outputFormat = inputFormat
        else:
            self.outputFormat = outputFormat
        self.graphAware = graphAware

    def bindPrefixes(self, graph):
        pass
        # for n in ns.all().items():
        #    graph.bind(n[0].lower(), URIRef(n[1]))

    def serialize(self, graph):
        self.bindPrefixes(graph)
        # For N-Triples format, we need to handle relative URIs specially
        if self.outputFormat == "nt":
            # Create a new graph with absolute URIs to avoid relative URI issues
            base_uri = "http://example.org/service"
            absolute_graph = Graph()
            for s, p, o in graph:
                # Convert relative URIs to absolute ones
                if isinstance(s, URIRef) and str(s).startswith("#"):
                    s = URIRef(base_uri + str(s))
                if isinstance(p, URIRef) and str(p).startswith("#"):
                    p = URIRef(base_uri + str(p))
                if isinstance(o, URIRef) and str(o).startswith("#"):
                    o = URIRef(base_uri + str(o))
                absolute_graph.add((s, p, o))
            return absolute_graph.serialize(format=self.outputFormat, encoding="utf-8")
        else:
            return graph.serialize(format=self.outputFormat, encoding="utf-8")

    def deserialize(self, graph, content, mimetype):
        if type(content) == str or type(content) == str:
            # if self.inputFormat == 'xml':
            #    inputSource = InputSource()
            #    inputSource.setEncoding('utf-8')
            #    inputSource.setCharacterStream(StringIO(content))
            #    graph.parse(inputSource,format=self.inputFormat)
            # else:
            graph.parse(data=content, format=self.inputFormat)
        else:
            graph.parse(content, format=self.inputFormat)
        return frir.RDFGraphDigest


class JsonLdSerializer(DefaultSerializer):
    def __init__(self):
        DefaultSerializer.__init__(self, "json-ld", graphAware=True)

    def serialize(self, graph):
        context = {}
        if hasattr(graph, "context"):
            context = graph.context
        return graph.serialize(format="json-ld", context=context, auto_compact=True)


class RDFaSerializer(DefaultSerializer):
    def __init__(self):
        DefaultSerializer.__init__(self, "rdfa", "xml")

    def deserialize(self, graph, content, mimetype):
        content = str(content)
        try:
            # print "Time to Tidy RDFa!!!"
            from tidylib import tidy_document

            document, errors = tidy_document(content, options={"numeric-entities": 1})
            content = document
            # if len(errors) > 0:
            # print errors
        except:
            pass
            # print "failure using tidy. The RDFa document may not parse successfully."
        DefaultSerializer.deserialize(self, graph, content, mimetype)


class MultipartSerializer(object):
    def __init__(self, serializers):
        self.serializers = serializers

    def deserialize(self, graph, content, mimetype):
        if type(content) == str or type(content) == str:
            msg = email.message_from_string("Content-Type:" + mimetype + "\n" + content)
        else:
            msg = email.message_from_string(
                "Content-Type:" + mimetype + "\n" + content.read()
            )
        named_parts = {}
        unnamed_parts = []
        for part in msg.walk():
            if part.is_multipart():
                continue
            filename = part.get_filename(None)
            if filename:
                named_parts[filename] = part
            else:
                unnamed_parts.append(part)
        rdf = [
            part
            for part in unnamed_parts
            if part.get_content_type() in self.serializers
        ]
        if len(rdf) == 0:
            raise Exception("SADI With Attachments requires one unnamed RDF part.")
        # print '\n'.join([str(x) for x in rdf])
        # print '\n'.join([str(x) for x in named_parts.values()])
        rdf_content = rdf[0].get_payload()
        # print "using this RDF content:"
        # print rdf_content
        ser = self.serializers[rdf[0].get_content_type()]
        ser.deserialize(graph, str(rdf_content), rdf[0].get_content_type())
        graph.attachments.update(named_parts)
        return frir.RDFGraphDigest

    def serialize(self, graph):
        raise Exception("Multipart serialization is unsupported")


class JSONSerializer(object):
    graphAware = False

    def serialize(self, graph):

        def getValue(node):
            if type(node) == BNode:
                return "_:" + str(node)
            else:
                # Python 3.12 compatibility: Return string instead of bytes for JSON serialization
                return str(node)

        def makeObject(o):
            result = {}
            result["value"] = getValue(o)
            if type(o) == URIRef:
                result["type"] = "uri"
            elif type(o) == BNode:
                result["type"] = "bnode"
            else:
                result["type"] = "literal"
                if o.language != None:
                    result["language"] = o.language
                if o.datatype != None:
                    result["datatype"] = str(o.datatype)
            return result

        def makeResource():
            return collections.defaultdict(list)

        result = collections.defaultdict(makeResource)
        for stmt in graph:
            result[getValue(stmt[0])][getValue(stmt[1])].append(makeObject(stmt[2]))
        return json.dumps(result)

    def getResource(self, r, bnodes):
        result = None
        if r.startswith("_:"):
            if r in bnodes:
                result = bnodes[r]
            else:
                result = BNode()
                bnodes[r] = result
        else:
            result = URIRef(r)
        return result

    def deserialize(self, graph, content, mimetype):
        # if type(content) != str:
        #    graph.parse(StringIO(content,newline=None),format=f)
        # else:
        #    graph.parse(content,format=f)

        data = content
        # Handle bytes objects by decoding to string first
        if isinstance(content, bytes):
            content = content.decode("utf-8")
            data = json.loads(content)
        elif type(content) == str or type(content) == str:
            data = json.loads(content)
        else:
            data = json.load(content)
        # print data
        bnodes = {}
        for s in list(data.keys()):
            subject = self.getResource(s, bnodes)
            for p in list(data[s].keys()):
                predicate = self.getResource(p, bnodes)
                objs = data[s][p]
                for o in objs:
                    obj = None
                    if o["type"] == "literal":
                        datatype = None
                        if "datatype" in o:
                            datatype = URIRef(o["datatype"])
                        lang = None
                        if "lang" in o:
                            lang = o["lang"]
                        value = o["value"]
                        obj = Literal(value, lang, datatype)
                    else:
                        obj = self.getResource(o["value"], bnodes)
                    graph.add((subject, predicate, obj))
        return frir.RDFGraphDigest
