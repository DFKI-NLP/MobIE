# DFKI MobIE Corpus

This repository contains the DFKI MobIE Corpus (formerly "DAYSTREAM Corpus"), a dataset of 3,232 German-language documents collected between May 2015 - Apr 2019 that have been annotated with fine-grained geo-entities, such as _location-street_, _location-stop_ and _location-route_, as well as standard named entity types (_organization_, _date_, _number_, etc). All location-related entities have been linked to either Open Street Map identifiers or database ids of Deutsche Bahn / Rhein-Main-Verkehrsverbund. The corpus has also been annotated with a set of 7 traffic-related n-ary relations and events, such as _Accidents_, _Traffic jams_, and _Canceled Routes_. It consists of Twitter messages, and traffic reports from e.g. radio stations, police and public transport providers. It allows for training and evaluating both named entity recognition algorithms that aim for fine-grained typing of geo-entities, entity linking of these entities, as well as n-ary relation extraction systems.

You can find the description of the corpus here: [https://aclanthology.org/2021.konvens-1.22/](https://aclanthology.org/2021.konvens-1.22/)

The corpus is provided in two formats - AVRO and JSONL, with train/dev/test splits.  To ensure a high data quality for evaluating event extraction, we do not include events automatically annotated with Snorkel (see paper) in the provided Test split of the dataset. 

For details on the schema used for storing annotations, see below. Due to Github storage limitations, we offer two versions of the corpus - a version without geo-information which is included in this repository, and an externally hosted version which includes WKB data (and is hence much larger, ~1.2GB) :

 * [MobIE Corpus (Aug 2021)](v1_20210811/)
 * [MobIE Corpus with WKB shapes (Aug 2021)](https://cloud.dfki.de/owncloud/index.php/s/YFqRNKkRDwqZWXG)

### NER only CONLL2003 formatted version:

- [MobIE NER CONLL2003-formatted (Aug 2021)](v1_20210811/ner_conll03_formatted.zip)

## Dataset Statistics

|                                   | Twitter                        | RSS                            | Total                          |
|-----------------------------------|--------------------------------|--------------------------------|--------------------------------|
| docs                              | 2562                           | 670                            | 3232                           |
| tokens                            | 62330                          | 28641                          | 90971                          |
| entities                          | 13573                          | 6911                           | 20484                          |
| relations                         | 1461                           | 575                            | 2036                           |
| linked entities (org,loc), KB+NIL | 8715                           | 4389                           | 13104                          |
| first-date                        | 	Sat May 23 20:48:32 CEST 2015 | 	Fri Jan 08 10:50:49 CET 2016  | 	Sat May 23 20:48:32 CEST 2015 |
| last-date                         | Mon Apr 01 09:18:25 CEST 2019  | 	Sun Mar 31 18:10:05 CEST 2019 | 	Mon Apr 01 09:18:25 CEST 2019 |

## Usage and Attribution

This data is distributed under the [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) license.

Send pull requests to submit annotation amendments.

If you use this data, please recognize our hard work and cite the relevant paper:

_MobIE: A German Dataset for Named Entity Recognition, Entity Linking and Relation Extraction in the Mobility Domain. Leonhard Hennig, Phuc Tran Truong, Aleksandra Gabryszak. Proceedings of KONVENS, 2021._ [(bib)](Konvens_2021_MobIE_Corpus.bib) [(pdf)](Konvens_2021_MobIE_Corpus.pdf)

## Format

The corpus consists of Documents which store the original text and all annotations, according to the following AVRO schema:

 * [document.avsc](document.avsc)

You can use the following JAVA tools to read the AVRO version of the corpus:

 * [Corpus Reader Tools](sdw-tools-1.0-SNAPSHOT.jar)

To read the corpus in AVRO format, use the following code snippet:

   ```java
   File inputFile = new File("train.avro");
   DataFileReader<Document> reader = AvroUtils.createReader(inputFile);
   while (reader.hasNext()) {
      Document doc = reader.next();
      // do something
   }

   ```

Each document contains a list of ConceptMentions, which correspond to Named Entities and other typed concepts (e.g. trigger phrases):

   ```java
   for (ConceptMention c : doc.getConceptMentions()) {
       String nerTag = c.getType();
       String value = c.getNormalizedValue();
       int start = c.getSpan().getStart();
       int end = c.getSpan().getEnd();
       String originalText = doc.getText().substring(start, end);
       // etc ...
   }
   ```

Each ConceptMention contains a list of reference ids. The first reference id with key "spreeDBReferenceId" refers to ids of the Daystream project's internal knowledge bases. For "location-city" entities, there is a second id "osm_id", which resolves to Open Street Map identifiers. For "location-stop" and "location-route", we are currently unable to provide the proprietary ids from Deutsche Bahn or Rhein-Main-Verkehrsverbund, and thus can only supply geo-information for resolution (see below). For "location-street", the ids are autogenerated when merging road segments from Open Street Map.

   ```java
   for (Reference r : c.getRefids()) {
       if (r.getKey().equals("osmRelationId")) {
           String osmId = r.getValue();
       }
   }
   ```

Since we cannot always guarantee the use of well-established IDs, we also include geo-information for each linked location:

   ```java
   for (String attributeKey : c.getAttributes().keySet()) {
       if (attributeKey.equals("wkb")) {
           String wkbPolygon = c.getAttributes.get(attributeKey);
       }
       if (attributeKey.equals("wkb-point")) {
           String wkbPoint = c.getAttributes.get(attributeKey);
       }
       if (attributeKey.equals("latitude")) {
           String latitude = c.getAttributes.get(attributeKey);
       }
       if (attributeKey.equals("longitude")) {
           String longitude = c.getAttributes.get(attributeKey);
       }
   }
   ```


You can retrieve RelationMentions:

   ```java
   for (RelationMention r : doc.getRelationMentions()) {
       String relationType = c.getName();
       int start = c.getSpan().getStart();
       int end = c.getSpan().getEnd();
       String originalText = doc.getText().substring(start, end);
       for (RelationArgument arg : r.getRelationArguments()) {
           String role = arg.getRole();
           ConceptMention c = arg.getConceptMention();
           // ...
       }
       // ...
   }
   ```

ConceptMentions and RelationMentions are stored at the document level, and for each sentence as well. You can access a sentence's list of RelationMentions using:

   ```java
   for (Sentence s : doc.getSentences()) {
       List<RelationMention> relationMentions = s.getRelationMentions();
       // ...
   }
   ```

A subset of the relation mentions in the Train and Dev splits of the corpus are automatically annotated with a weakly supervised labeling approach. These relation mentions can be filtered by their Provenance information:

```java
List<RelationMention> snorkeledRelations = new ArrayList<RelationMention>();
for (RelationMention r : doc.getRelationMentions) {
    if (r.getProvenances().get(0).getAnnotator().equals("snorkel")) {
        snorkeledRelations.add(r);
    }
}
```



## Annotation Guidelines

[MobIE Corpus Annotation Guidelines v1.1 (Jul 2021)](MobIE_Corpus_Annotation_Guidelines_Jul_2021_v1.1.pdf)
