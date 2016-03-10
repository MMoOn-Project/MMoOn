#!/usr/bin/python3

# http://mmoon.org/lang/heb/schema/oh/PrimaryRoot
import urllib
import rdflib
from rdflib import RDF
from rdflib import RDFS
from rdflib import OWL
from rdflib import Namespace
from heb2lat import lat2heb
import hashlib

mmoon = Namespace("http://mmoon.org/mmoon/")
mmoon_heb = Namespace("http://mmoon.org/lang/heb/schema/oh/")
heb_inventory = Namespace("http://mmoon.org/lang/heb/inventory/oh/")

schema = mmoon_heb
inventory = heb_inventory

class Lexeme:
    lexeme = ''
    binjan = None
    wordClass = None
    wordforms = []
    def __init__(self, lexeme, binjan, wordClass=None):
        self.lexeme = lexeme
        self.binjan = binjan
        self.wordClass = wordClass
    def addWordform(self, wordform):
        self.wordforms.append(wordform)
    def toRDF(self, graph):
        # TODO use heb2lat
        lexeme = rdflib.term.URIRef(heb_inventory+"Lexeme_"+self.lexeme)
        hebString = lat2heb(self.lexeme)
        lexemeHeb = rdflib.term.URIRef(heb_inventory+"Lexeme_"+hebString)
        graph.add((lexeme, RDF.type, mmoon_heb.Lexeme))
        graph.add((lexeme, RDFS.label, rdflib.term.Literal(self.lexeme)))
        graph.add((lexeme, RDFS.label, rdflib.term.Literal(hebString, lang="he")))
        graph.add((lexeme, mmoon.hasWordclassAffiliation, self.wordClass))
        graph.add((lexeme, mmoon.hasMorphologicalRelationship, self.binjan))
        graph.add((lexemeHeb, RDF.type, mmoon_heb.Lexeme))
        graph.add((lexemeHeb, OWL.sameAs, lexeme))
        graph.add((lexemeHeb, RDFS.label, rdflib.term.Literal(hebString, lang="he")))
        # TODO add representations
        for wordform in self.wordforms:
            graph.add((lexeme, mmoon.hasWordform, wordform.getIri()))
            graph.add((wordform.getIri(), mmoon.belongsToLexeme, lexeme))

class Wordform:
    wordform = ''
    root = None
    transfix = None
    def __init__(self, wordform, root, transfix):
        self.root = root
        self.wordform = wordform
        self.transfix = transfix
    def getIri(self):
        return rdflib.term.URIRef(heb_inventory+"Wordform_"+self.wordform)
    def getHebIri(self):
        heb = lat2heb(self.wordform)
        return rdflib.term.URIRef(heb_inventory+"Wordform_"+heb)
    def toRDF(self, graph):
        wordform = self.getIri()
        wordformHeb = self.getHebIri()
        hebString = lat2heb(self.wordform)
        graph.add((wordform, RDF.type, mmoon_heb.Wordform))
        graph.add((wordform, RDFS.label, rdflib.term.Literal(self.wordform)))
        graph.add((wordform, RDFS.label, rdflib.term.Literal(lat2heb(self.wordform), lang="he")))
        graph.add((wordform, mmoon.consistsOfRoot, self.root.getIri()))
        graph.add((wordform, mmoon.consistsOfTransfix, self.transfix.getIri()))
        graph.add((wordformHeb, RDF.type, mmoon_heb.Wordform))
        graph.add((wordformHeb, OWL.sameAs, wordform))
        graph.add((wordformHeb, RDFS.label, rdflib.term.Literal(hebString, lang="he")))

class Root:
    root = ''
    def __init__(self, root):
        self.root = root
    def getIri(self):
        return rdflib.term.URIRef(heb_inventory+"Root_"+self.root)
    def getHebIri(self):
        heb = lat2heb(self.root)
        return rdflib.term.URIRef(heb_inventory+"Root_"+heb)
    def toRDF(self, graph):
        # TODO use heb2lat
        root = self.getIri()
        rootHeb = self.getHebIri()
        hebString = lat2heb(self.root)
        graph.add((root, RDF.type, mmoon_heb.Root))
        graph.add((root, RDFS.label, rdflib.term.Literal(self.root)))
        graph.add((root, RDFS.label, rdflib.term.Literal(hebString, lang="he")))
        graph.add((rootHeb, RDF.type, mmoon_heb.Root))
        graph.add((rootHeb, OWL.sameAs, root))
        graph.add((rootHeb, RDFS.label, rdflib.term.Literal(hebString, lang="he")))

class Transfix:
    transfix = ''
    morpheme = None
    def __init__(self, transfix, morpheme):
        self.transfix = transfix
        self.morpheme = morpheme
    def getIri(self):
        return rdflib.term.URIRef(heb_inventory+"Transfix_"+self.transfix)
    def getHebIri(self):
        heb = lat2heb(self.transfix)
        return rdflib.term.URIRef(heb_inventory+"Transfix_"+heb)
    def toRDF(self, graph):
        # TODO use heb2lat
        transfix = self.getIri()
        transfixHeb = self.getHebIri()
        hebString = lat2heb(self.transfix)
        graph.add((transfix, RDF.type, mmoon_heb.Transfix))
        graph.add((transfix, RDFS.label, rdflib.term.Literal(self.transfix)))
        graph.add((transfix, RDFS.label, rdflib.term.Literal(hebString, lang="he")))
        graph.add((transfix, mmoon.correspondsToMorpheme, self.morpheme))
        graph.add((self.morpheme, mmoon.hasRealization, transfix))
        graph.add((transfixHeb, RDF.type, mmoon_heb.Transfix))
        graph.add((transfixHeb, OWL.sameAs, transfix))
        graph.add((transfixHeb, RDFS.label, rdflib.term.Literal(hebString, lang="he")))

def getNewGraph():

    graph = rdflib.Graph()
    graph.bind("mmoon", mmoon)
    graph.bind("heb_schema", mmoon_heb)
    graph.bind("heb_inventory", heb_inventory)
    graph.bind("owl", OWL)

    return graph

def writeGraphToFile(graph, filename):
    graph.add((heb_inventory.term(""), OWL.imports, mmoon_heb.term("")))
    graph.serialize(filename, "turtle")
