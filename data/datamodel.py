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

mmoon = Namespace("http://mmoon.org/mmoon/")
mmoon_heb = Namespace("http://mmoon.org/lang/heb/schema/oh/")
heb_inventory = Namespace("http://mmoon.org/lang/heb/inventory/oh/")
gold = Namespace("http://purl.org/linguistics/gold/")
DC = Namespace("http://purl.org/dc/elements/1.1/")

def Lexeme:
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
        graph.add((lexeme, RDF.type, heb_schema.Lexeme))
        graph.add((lexeme, mmoon_heb.hasWordclassAffiliation, self.wordClass))
        graph.add((lexeme, mmoon_heb.hasMR, self.binjan))
        for wordform in self.wordforms:
            graph.add((lexeme, mmoon_heb.hasWordform, self.wordform.getIri()))
            graph.add((self.wordform.getIri(), mmoon_heb.hasWordform, lexeme))

def Wordform:
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
        graph.add((wordform, RDF.type, heb_schema.Wordform))
        graph.add((wordform, mmoon_heb.consistsOfRoot, self.root.getIri()))
        graph.add((wordform, mmoon_heb.consistsOfAffix, self.affix.getIri()))

def Root:
    root = ''
    def __init__(self, root):
        self.root = root
    def getIri(self):
        return rdflib.term.URIRef(heb_inventory+"Root_"+self.root)
    def toRDF(self, graph):
        # TODO use heb2lat
        root = self.getIri()
        graph.add((root, RDF.type, heb_schema.Root))

def Affix:
    affix = ''
    def __init__(self, affix):
        self.affix = affix
    def getIri(self):
        return rdflib.term.URIRef(heb_inventory+"Affix_"+self.root)
    def toRDF(self, graph):
        # TODO use heb2lat
        affix = self.getIri()
        graph.add((affix, RDF.type, heb_schema.Transfix))

def main(args=sys.argv[1:]):
    graph = rdflib.Graph()
    graph.bind("mmoon", mmoon)
    graph.bind("heb_schema", mmoon_heb)
    graph.bind("heb_inventory", heb_inventory)
    graph.bind("gold", gold)
    graph.bind("owl", OWL)
    graph.bind("dc", DC)

    wordclassResource = mmoon_heb.Verb
    heb_schema.Lexeme

    lexeme = Lexeme("lexeme", heb_schema.binjan_piel_1, mmoon_heb.Verb)


            if any(wordclassResource == kategorie for kategorie in lexemeKategorie):
                isLexeme = True
                lexeme = rdflib.term.URIRef(heb_inventory+"Lexeme_"+voc)
                graph.add((lexeme, RDF.type, mmoon_heb.Lexeme))
            elif rdfType and rdfType == mmoon_heb.Suffix:
                lexeme = rdflib.term.URIRef(heb_inventory+"Suffix_"+voc)
                graph.add((lexeme, RDF.type, rdfType))
            else:
                lexeme = rdflib.term.URIRef(heb_inventory+"Word_"+voc)
                graph.add((lexeme, RDF.type, mmoon.Word))
            vocrep = rdflib.term.URIRef(heb_inventory+"Representation_"+voc)
            vocliteral = rdflib.term.Literal(row['vocalized'], lang="he")

            graph.add((vocrep, RDF.type, mmoon_heb.Representation))
            graph.add((vocrep, mmoon_heb.vocalizedRepresentation, vocliteral))
            if lexeme:
                graph.add((lexeme, RDFS.label, vocliteral))
                graph.add((lexeme, mmoon.hasRepresentation, vocrep))

        if row['unvocalized']:
            unvoc = row['unvocalized']
            unvocrep = rdflib.term.URIRef(heb_inventory+"Representation_"+unvoc)
            unvocliteral = rdflib.term.Literal(row['unvocalized'], lang="he")

            graph.add((unvocrep, RDF.type, mmoon_heb.Representation))
            graph.add((unvocrep, mmoon_heb.unvocalizedRepresentation, unvocliteral))

            if lexeme:
                graph.add((lexeme, mmoon.hasRepresentation, unvocrep))

        if row['deutsch']:
            sense = addSense(graph, row['deutsch'], "de")
            if lexeme:
                graph.add((lexeme, mmoon.hasSense, sense))

        if row['englisch']:
            sense = addSense(graph, row['englisch'], "en")
            if lexeme:
                graph.add((lexeme, mmoon.hasSense, sense))

        if row['russisch']:
            sense = addSense(graph, row['russisch'], "ru")
            if lexeme:
                graph.add((lexeme, mmoon.hasSense, sense))

        if row['root'] or row['secundaryRoot']:
            # secondary-root -> secondary-root
            # root -> primary-root
            # nur eins von beiden -> root
            if (row['root'] == row['secundaryRoot'] or not row['root'] or not row['secundaryRoot']):
                root = row['secundaryRoot']
                if not root:
                    root = row['root']
                rootResource = addRootResource(graph, root, mmoon_heb.PrimaryRoot)
                roots.append(rootResource)
            else :
                #rootResourceA = addRootResource(graph, row['root'], mmoon_heb.PrimaryRoot)
                rootResource = addRootResource(graph, row['secundaryRoot'], mmoon_heb.SecondaryRoot, row['root'])
                roots.append(rootResource)

        #######

        if lexeme:
            if wordclassResource:
                graph.add((lexeme, mmoon.hasWordclassAffiliation, wordclassResource))
            for inflectionalCategory in inflectionalCategories :
                graph.add((lexeme, mmoon.hasInflectionalCategory, inflectionalCategory))
            if binjan:
                graph.add((lexeme, mmoon.consistsOfMorph, binjan))

            for root in roots :
                graph.add((lexeme, mmoon_heb.consistsOfMorph, root))
                graph.add((root, mmoon.belongsTo, lexeme))

    graph.add((heb_inventory.term(""), OWL.imports, mmoon_heb.term("")))
    graph.serialize(out_file_rdf, "turtle")

def addSense(graph, senseDefinitionString, language):
    senseDefinitionString = senseDefinitionString.strip()
    senseDefinitionStringQuoted = urllib.parse.quote(senseDefinitionString)

    sense = rdflib.term.URIRef(heb_inventory+"Sense_" + language + "_"+senseDefinitionStringQuoted)

    graph.add((sense, RDF.type, mmoon.Sense))
    graph.add((sense, mmoon.senseDefinition, rdflib.term.Literal(senseDefinitionString, lang=language)))
    graph.add((sense, DC.language, rdflib.term.Literal(language)))
    return sense

def addRootResource(graph, root, classResource, primaryRoot=None):
    # https://stackoverflow.com/questions/33068727/how-to-split-unicode-strings-character-by-character-in-python
    #rootDashed = "-".join(regex.findall('\p{L}\p{M}*', root))
    rootDashed = "-".join(regex.findall('\X', root))

    rootResource = rdflib.term.URIRef(heb_inventory+"Root_"+root)
    #rootResource = rdflib.term.URIRef(heb_inventory+"root_"+heb2latComp(rootDashed))
    rootliteral = rdflib.term.Literal(root, lang="he")

    rootDashedRepresentation = rdflib.term.URIRef(heb_inventory+"Representation_"+rootDashed)
    rootDashedLiteral = rdflib.term.Literal(rootDashed, lang="he")

    graph.add((rootResource, RDF.type, classResource))
    graph.add((rootResource, RDF.type, mmoon_heb.Root))
    graph.add((rootResource, RDFS.label, rootliteral))
    graph.add((rootResource, mmoon.hasRepresentation, rootDashedRepresentation))

    graph.add((rootDashedRepresentation, RDF.type, mmoon_heb.Representation))
    graph.add((rootDashedRepresentation, mmoon.orthographicRepresentation, rootDashedLiteral))

    if primaryRoot:
        primaryRootResource = addRootResource(graph, primaryRoot, mmoon_heb.PrimaryRoot)
        graph.add((rootResource, mmoon_heb.consistsOfRoot, primaryRootResource))

    return rootResource

def normalizeRoot(root):

    forbiddenChars = ["(", ")", "[", "]", "/", "."]
    root = root.strip()

    if not root or root == "—" or root == "—" or any(char in root for char in forbiddenChars):
        return ""

    root = regex.sub('[a-zA-Z]', '', root)
    root = regex.sub('[1-9]', '', root)
    return root.replace(" ", "").replace("-", "").replace("־", "")


if __name__ == "__main__":
    main()
