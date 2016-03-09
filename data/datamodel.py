#!/usr/bin/python3

# http://mmoon.org/lang/heb/schema/oh/PrimaryRoot
import urllib
import rdflib
from rdflib import RDF
from rdflib import RDFS
from rdflib import OWL
#from rdflib import DC
from rdflib import Namespace
import hashlib
import regex
import sys
import getopt

mmoon = Namespace("http://mmoon.org/mmoon/")
mmoon_heb = Namespace("http://mmoon.org/lang/heb/schema/oh/")
heb_inventory = Namespace("http://mmoon.org/lang/heb/inventory/oh/")
gold = Namespace("http://purl.org/linguistics/gold/")
DC = Namespace("http://purl.org/dc/elements/1.1/")

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
    def __init__(self, affix):
        self.affix = affix
    def getIri(self):
        return rdflib.term.URIRef(heb_inventory+"Affix_"+self.affix)
    def toRDF(self, graph):
        # TODO use heb2lat
        affix = self.getIri()
        graph.add((affix, RDF.type, mmoon_heb.Transfix))
        graph.add((affix, RDFS.label, rdflib.term.Literal(self.affix)))
        # TODO add AtomicMorpheme and so on

def main(args=sys.argv[1:]):
    try:
        opts, args = getopt.getopt(args, "hf:c:r:", ["help", "file=", "csvoutfile=", "rdfoutfile="])
    except getopt.GetoptError as err:
        # print help information and exit:
        LOG.error(err)  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    out_file_rdf = None

    for opt, opt_val in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-r", "--rdfoutfile"):
            out_file_rdf = opt_val
        else:
            assert False, "unhandled option"

    graph = rdflib.Graph()
    graph.bind("mmoon", mmoon)
    graph.bind("heb_schema", mmoon_heb)
    graph.bind("heb_inventory", heb_inventory)
    graph.bind("gold", gold)
    graph.bind("owl", OWL)
    graph.bind("dc", DC)

    wordclassResource = mmoon_heb.Verb
    #mmoon_heb.Lexeme

    lexeme = Lexeme("דִּבֵּר", mmoon_heb.binjan_piel_1, mmoon_heb.Verb)
    root = Root("דבר")
    #"◌ִּ◌ֵּ◌"
    affix = Affix("◌ִּ◌ֵּ◌")
    wordform = Wordform("דְּבֵּר", root, affix)
    lexeme.addWordform(wordform)

    lexeme.toRDF(graph)
    root.toRDF(graph)
    affix.toRDF(graph)
    wordform.toRDF(graph)

    graph.add((heb_inventory.term(""), OWL.imports, mmoon_heb.term("")))
    graph.serialize(out_file_rdf, "turtle")

if __name__ == "__main__":
    main()
