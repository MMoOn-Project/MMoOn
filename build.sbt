organization := "org.mmoon"

name := "OWLPod for MMoOn"

sources := {
    (baseDirectory.value / "owlpod.scala").get
}

mainClass in (Compile, run) := Some("ProtegePostprocess")

scalaVersion := "2.11.8"

libraryDependencies += "org.aksw.owlpod" %% "owlpod" % "0.5.3-SNAPSHOT"

resolvers ++= Seq(
    "AKSW Snapshots" at "http://maven.aksw.org/repository/snapshots/",
    "AKSW Internal" at "http://maven.aksw.org/repository/internal/"

)
