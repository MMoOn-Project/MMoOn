#!/usr/bin/python3

# http://mmoon.org/lang/heb/schema/oh/PrimaryRoot
import urllib
import rdflib
from rdflib import RDF
from rdflib import RDFS
from rdflib import Namespace
import hashlib
import regex

mmoon = Namespace("http://mmoon.org/mmoon/")
mmoon_heb = Namespace("http://mmoon.org/lang/heb/schema/oh/")
heb_inventory = Namespace("http://mmoon.org/lang/heb/inventory/oh/")

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
        graph.add((lexeme, RDF.type, mmoon_heb.Lexeme))
        graph.add((lexeme, RDFS.label, rdflib.term.Literal(self.lexeme)))
        graph.add((lexeme, mmoon.hasWordclassAffiliation, self.wordClass))
        graph.add((lexeme, mmoon.hasMorphologicalRelationship, self.binjan))
        # TODO add representations
        for wordform in self.wordforms:
            graph.add((lexeme, mmoon.hasWordform, wordform.getIri()))
            graph.add((wordform.getIri(), mmoon.belongsToLexeme, lexeme))

class Wordform:
    wordform = ''
    root = None
    affix = None
    def __init__(self, wordform, root, affix):
        self.root = root
        self.wordform = wordform
        self.affix = affix
    def getIri(self):
        return rdflib.term.URIRef(heb_inventory+"Wordform_"+self.wordform)
    def toRDF(self, graph):
        # TODO use heb2lat
        wordform = self.getIri()
        graph.add((wordform, RDF.type, mmoon_heb.Wordform))
        graph.add((wordform, RDFS.label, rdflib.term.Literal(self.wordform)))
        graph.add((wordform, mmoon.consistsOfRoot, self.root.getIri()))
        graph.add((wordform, mmoon.consistsOfAffix, self.affix.getIri()))

class Root:
    root = ''
    def __init__(self, root):
        self.root = root
    def getIri(self):
        return rdflib.term.URIRef(heb_inventory+"Root_"+self.root)
    def toRDF(self, graph):
        # TODO use heb2lat
        root = self.getIri()
        graph.add((root, RDF.type, mmoon_heb.Root))
        graph.add((root, RDFS.label, rdflib.term.Literal(self.root)))

class Affix:
    affix = ''
    morpheme = None
    def __init__(self, affix, morpheme):
        self.affix = affix
        self.morpheme = morpheme
    def getIri(self):
        return rdflib.term.URIRef(heb_inventory+"Transfix_"+self.affix)
    def toRDF(self, graph):
        # TODO use heb2lat
        affix = self.getIri()
        graph.add((affix, RDF.type, mmoon_heb.Transfix))
        graph.add((affix, RDFS.label, rdflib.term.Literal(self.affix)))
        graph.add((affix, mmoon.correspondsToMorpheme, self.morpheme))
        graph.add((self.morpheme, mmoon.hasRealization, affix))
