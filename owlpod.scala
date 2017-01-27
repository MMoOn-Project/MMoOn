import org.aksw.owlpod.{OwlpodRunner, _}
import org.aksw.owlpod.config._
import org.aksw.owlpod.reporting._
import org.aksw.owlpod.serialisation._
import org.aksw.owlpod.serialisation.OWLFormat._
import org.aksw.owlpod.serialisation.outputconfigs._
import org.aksw.owlpod.tasks._
import org.aksw.owlpod.tasks.ImportConfig._
import org.aksw.owlpod.util._
import org.semanticweb.owlapi.util.CommonBaseIRIMapper

import scalax.file.Path

object Con extends OwlpodRunner with CommonRunConfig {

  lazy val setups = Seq(
    CurationSetup(
      name = "MMoOn OG",
      ontDocSets = Seq(mmoonOGDocs),
      tasks = Seq(
        SeparateOrdinalDigits,
        new AddInferences(),
        new RemoveExternalDeclarations()),
      outputConfig = MultipleFormats(Set(Turtle, NTriples, OWLXML, RDFXML),
        formatLocations = AddFilenameInfix(""), skipUndeclared = true, overwriteExisting = true,
        postprocessors = Seq(MMoOnVersionFix, TrimComments(false), MMoOnVersionFix,
          NormalizeBlankLinesForTurtle)),
      iriMappings = Seq(mmoonRepoIriMapper)
    )
  )
}

object ProtegePostprocess extends OwlpodRunner with CommonRunConfig {

  lazy val setups = Seq(
    CurationSetup(
      name = "MMoOn OpenGerman Protege Post-Processing",
      ontDocSets = Seq(mmoonOGDocs),
      tasks = Seq(),
      outputConfig = ReplaceSources(postprocessors = Seq(/*MMoOnVersionFix, */TrimComments(true)/*, MMoOnVersionFix,*/,
        NormalizeBlankLinesForTurtle)),
      iriMappings = Seq(mmoonRepoIriMapper)
    )
  )
}

trait CommonRunConfig { this: OwlpodRunner =>

  lazy val defaults = SetupDefaults(
    reporter = LogReporter(printStacktraces = true),
    executionPolicy = FailOnEverythingPolicy
  )

  lazy val mmoonRoot = Path.fromString(".").toAbsolute

  lazy val mmoonOGDocs = OntologyDocumentList(
    "core/mmoon.ttl",
    "lang/deu/schemas/OpenGerman/deu_schema.ttl",
    "lang/deu/inventories/OpenGerman/deu_inventory.ttl"
  )

  lazy val mmoonOHDocs = OntologyDocumentList(
    "lang/heb/schemas/OpenHebrew/heb_schema.ttl",
    "lang/heb/inventories/OpenHebrew/heb_inventory.ttl"
  )

  lazy val mmoonRepoIriMapper: CommonBaseIRIMapper = {

    val im = new CommonBaseIRIMapper(mmoonRoot.toURI)
    ontIRI2ShortPath foreach { case (iri, sp) => im.addMapping(iri, sp) }
    im
  }

  protected lazy val ontIRI2ShortPath = Map(
    "http://mmoon.org/mmoon/".toIRI -> "core/mmoon.ttl",
    "http://mmoon.org/lang/deu/schema/og/".toIRI -> "lang/deu/schemas/OpenGerman/deu_schema.ttl",
    "http://mmoon.org/lang/deu/inventory/og/".toIRI -> "lang/deu/inventories/OpenGerman/deu_inventory.ttl",
    "http://mmoon.org/lang/heb/schema/oh/".toIRI -> "lang/heb/schemas/OpenHebrew/heb_schema.ttl",
    "http://mmoon.org/lang/heb/inventory/oh/".toIRI -> "lang/heb/inventories/OpenHebrew/heb_inventory.ttl"
  )

  def main(args: Array[String]) {
    runSetups()
  }
}
