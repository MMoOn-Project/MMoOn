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
import better.files._

object Con extends OwlpodRunner with CommonRunConfig {

  lazy val setups = Seq(
    CurationSetup(
      name = "MMoOn OG",
      ontDocSets = Seq(mmoonCore, mmoonOGDocs),
      tasks = Seq(
        SeparateOrdinalDigits,
        new AddInferences()),
      outputConfig = MultipleFormats(Set(Turtle, NTriples, OWLXML, RDFXML),
        formatLocations = AddFilenameInfix("op"),
        postprocessors = Seq(TrimComments(), NormalizeBlankLinesForTurtle)),
      iriMappings = Seq(mmoonRepoIriMapper)
    )
  )
}

object ProtegePostprocess extends OwlpodRunner with CommonRunConfig {

  lazy val setups = Seq(
    CurationSetup(
      name = "MMoOn OpenGerman Protege Post-Processing",
      ontDocSets = Seq(mmoonCore, mmoonOGDocs),
      tasks = Seq(RemoveExternalAxioms()),
      outputConfig = ReplaceSources(
        postprocessors = Seq(TrimComments(), NormalizeBlankLinesForTurtle)),
      iriMappings = Seq(mmoonRepoIriMapper)
    )
  )
}

object Jenkins {

  def runner(targetDir: String) = new CommonRunConfig with OwlpodRunner {

    lazy val setups = Seq(
      CurationSetup(
        name = s"Jenkins format multiplexing to $targetDir",
        ontDocSets = Seq(mmoonCore, mmoonOGDocs, mmoonPEDocs),
        tasks = Seq(RemoveExternalAxioms()),
        outputConfig = MultipleFormats(
          Set(Turtle, NTriples, OWLXML, RDFXML, Manchester, Functional),
          PreserveRelativePaths(mmoonRoot.pathAsString, targetDir),
          postprocessors = Seq(TrimComments(), NormalizeBlankLinesForTurtle),
          overwriteExisting = true
        ),
        iriMappings = Seq(mmoonRepoIriMapper)
      )
    )
  }

  def main(args: Array[String]): Unit = args.toList match {

    case targetDir :: Nil => runner(targetDir).runSetups()
    case _ => sys.error("expecting exactly one command line argument stating target directory")
  }
}

trait CommonRunConfig { this: OwlpodRunner =>

  lazy val defaults = SetupDefaults(
    reporter = LogReporter(printStacktraces = true),
    executionPolicy = FailOnEverythingPolicy
  )

  lazy val mmoonRoot: File = File(".").path.toAbsolutePath

  lazy val mmoonCore = OntologyDocumentList("core/mmoon.ttl")

  lazy val mmoonOGDocs = OntologyDocumentList(
    "deu/schema/og/deu_schema.ttl",
    "deu/inventory/og/deu_inventory.ttl"
  )

  lazy val mmoonOHDocs = OntologyDocumentList(
    "lang/heb/schemas/OpenHebrew/heb_schema.ttl",
    "lang/heb/inventories/OpenHebrew/heb_inventory.ttl"
  )

  lazy val mmoonPEDocs = OntologyDocumentList(
    "deu/schema/pe/deu_schema.ttl",
//    "deu/inventory/pe/deu_inventory.ttl",
    "spa/schema/pe/spa_schema.ttl"
//    "spa/inventory/pe/spa_inventory.ttl"
  )

  lazy val mmoonRepoIriMapper: CommonBaseIRIMapper = {

    val im = new CommonBaseIRIMapper(mmoonRoot.uri)
    ontIRI2ShortPath foreach { case (iri, sp) => im.addMapping(iri, sp) }
    im
  }

  protected lazy val ontIRI2ShortPath = Map(
    "http://mmoon.org/core/".toIRI -> "core/mmoon.ttl",
    "http://mmoon.org/core/v1.0.0/".toIRI -> "core/mmoon.ttl",
    "http://mmoon.org/deu/schema/og/".toIRI -> "deu/schema/og/deu_schema.ttl",
    "http://mmoon.org/deu/inventory/og/".toIRI -> "deu/inventory/og/deu_inventory.ttl",
    "http://mmoon.org/lang/heb/schema/oh/".toIRI -> "lang/heb/schemas/OpenHebrew/heb_schema.ttl",
    "http://mmoon.org/lang/heb/inventory/oh/".toIRI -> "lang/heb/inventories/OpenHebrew/heb_inventory.ttl",
    "http://mmoon.org/deu/schema/pe/".toIRI -> "deu/schema/pe/deu_schema.ttl",
    "http://mmoon.org/deu/inventory/pe/".toIRI -> "deu/inventory/pe/deu_inventory.ttl",
    "http://mmoon.org/spa/schema/pe/".toIRI -> "spa/schema/pe/spa_schema.ttl",
    "http://mmoon.org/spa/inventory/pe/".toIRI -> "spa/inventory/pe/spa_inventory.ttl"
  )

  def main(args: Array[String]) {
    runSetups()
  }
}
