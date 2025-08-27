# moose

A tool for taxonomically selecting, grouping and summarizing pairwise
alignment classifications into something more concise and readable.

## authors

* [Noah Hoffman](https://github.com/nhoffman)
* [Tim Holland](https://github.com/tholland)
* [Daniel Hoogestraat](https://github.com/dhoogest)
* [Tyler Land](https://github.com/tyleraland)
* [Steve Salipante](mailto:stevesal@uw.edu)
* [Chris Rosenthal](mailto:crosenth@gmail.com)

## about

Moose groups pairwise alignments by taxonomy and alignment scores.  It works 
safely with large data sets utilizing the Python Data Analysis Library.

## dependencies

* Python >= 3.7
* [Pandas](https://pandas.pydata.org/) >= 2.0.2

## installation

Moose can be installed in a few ways:

From PyPI:

```
% pip install moose_classifier
```

Or cloned from Github:

```
% git clone https://github.com/crosenth/moose.git
% python moose/setup.py install
```

## examples

The following examples will use results using 16s sequences aligned to a local
NCBI nt database.  For instructions on creating a local blast nt database see
the NCBI walkthrough
[here](https://www.ncbi.nlm.nih.gov/sites/books/NBK537770/) and
and [here](https://www.ncbi.nlm.nih.gov/sites/books/NBK279688/).

The simplest example pipes blast "10 qaccver saccver pident staxid" into
the classifier and outputs a table of species level taxonomy results:

```
% blastn -db nt -outfmt "10 qaccver saccver pident staxid" -query sequences.fasta | classify --columns qaccver,saccver,pident,staxid
specimen,assignment_id,assignment,best_rank,max_percent,min_percent,min_threshold,reads,clusters,pct_reads
query1,0,Homo sapiens,species,99.67,99.67,0.00,1,1,100.00
query10,0,Actinobacteria*;uncultured bacterium*,species,100.00,93.21,0.00,1,1,100.00
query11,0,Bacteroidetes*;uncultured bacterium*/organism,species,100.00,91.26,0.00,1,1,100.00
query12,0,Apteryx australis*;Bacteria*;Firmicutes*,species,100.00,98.26,0.00,1,1,100.00
query13,0,Dikarya*;uncultured bacterium/eukaryote,species,100.00,82.88,0.00,1,1,100.00
query14,0,Saccharomyces cerevisiae*;uncultured eukaryote,species,100.00,99.00,0.00,1,1,100.00
query2,0,Homo sapiens;Pan troglodytes,species,97.07,95.40,0.00,1,1,100.00
query6,0,Bacteria*;Escherichia coli;Staphylococcus,species,100.00,98.62,0.00,1,1,100.00
query7,0,Bacteroidetes*;uncultured bacterium*/organism*,species,100.00,91.61,0.00,1,1,100.00
query8,0,Bacteria*;Escherichia coli;Staphylococcus,species,100.00,98.62,0.00,1,1,100.00
query9,0,Bacteria*;uncultured organism*,species,100.00,98.62,0.00,1,1,100.00
```

This example shows the bare minimum information required to simplify and group
alignment results: a query sequence (qseqid), subject sequence (sseqid), a
percent identiy (pident) and a subject taxonomy id (staxid). If the staxid
column is unavailable an accession to taxonomy id map file can be used with
the `--seq-info` argument. Results are output in csv format.

Sending the `blastn` results to a standalone file we can look a bit closer 
at what happened.  And for purposes of this walkthrough the csv output will
be displated in as a nicely formatted table:

```
% blastn -outfmt "10 qaccver saccver pident staxid" -query sequences.fasta -out blast.csv
% wc --lines blast.csv
1084 blast.csv
% classify --columns qaccver,saccver,pident,staxid blast.csv
specimen,assignment_id,assignment,best_rank,max_percent,min_percent,min_threshold,reads,clusters,pct_reads
|----------+---------------+------------------------------------------------+-----------+-------------+-------------+---------------+-------+----------+-----------|
| specimen | assignment_id | assignment                                     | best_rank | max_percent | min_percent | min_threshold | reads | clusters | pct_reads |
|----------+---------------+------------------------------------------------+-----------+-------------+-------------+---------------+-------+----------+-----------|
| query1   | 0             | Homo sapiens                                   | species   | 99.67       | 99.67       | 0.00          | 1     | 1        | 100.00    |
| query10  | 0             | Actinobacteria*;uncultured bacterium*          | species   | 100.00      | 93.21       | 0.00          | 1     | 1        | 100.00    |
| query11  | 0             | Bacteroidetes*;uncultured bacterium*/organism  | species   | 100.00      | 91.26       | 0.00          | 1     | 1        | 100.00    |
| query12  | 0             | Apteryx australis*;Bacteria*;Firmicutes*       | species   | 100.00      | 98.26       | 0.00          | 1     | 1        | 100.00    |
| query13  | 0             | Dikarya*;uncultured bacterium/eukaryote        | species   | 100.00      | 82.88       | 0.00          | 1     | 1        | 100.00    |
| query14  | 0             | Saccharomyces cerevisiae*;uncultured eukaryote | species   | 100.00      | 99.00       | 0.00          | 1     | 1        | 100.00    |
| query2   | 0             | Homo sapiens;Pan troglodytes                   | species   | 97.07       | 95.40       | 0.00          | 1     | 1        | 100.00    |
| query6   | 0             | Bacteria*;Escherichia coli;Staphylococcus      | species   | 100.00      | 98.62       | 0.00          | 1     | 1        | 100.00    |
| query7   | 0             | Bacteroidetes*;uncultured bacterium*/organism* | species   | 100.00      | 91.61       | 0.00          | 1     | 1        | 100.00    |
| query8   | 0             | Bacteria*;Escherichia coli;Staphylococcus      | species   | 100.00      | 98.62       | 0.00          | 1     | 1        | 100.00    |
| query9   | 0             | Bacteria*;uncultured organism*                 | species   | 100.00      | 98.62       | 0.00          | 1     | 1        | 100.00    |
|----------+---------------+------------------------------------------------+-----------+-------------+-------------+---------------+-------+----------+-----------|
```

1,084 lines of blast results are conveniently grouped taxonomically and 
with a single row per specimen query sequence.

Taxonomy grouping is accomplished with a lineages table that can be specified
using the `--lineages` argument.  If a lineages file is not supplied it will be
generated automatically using NCBI taxonomy data by default.  A Moose classify 
built lineages table can be saved to a file using the `lineages-out` command 
which will speed up subsequent classify runs:

```
classify --columns qaccver,saccver,pident,staxid --lineages-out lineages.csv --specimen one blast.csv
```

### Taxonomony grouping

By default, classifications are taxonomically grouped according to
`--max-group-size` with 3 being the default.  Classification names will start
at the species level by default and recursively regroup at a higher taxonomony
until `--max-group-size` is satisfied.  

By increasing the `--max-group-size 5`:
```
classify --columns qaccver,saccver,pident,staxid --lineages lineages.csv --max-group-size 5 blast.csv
|----------+---------------+---------------------------------------------------------------------------------------------------------------------+-----------+-------------+-------------+---------------+-------+----------+-----------|
| specimen | assignment_id | assignment                                                                                                          | best_rank | max_percent | min_percent | min_threshold | reads | clusters | pct_reads |
|----------+---------------+---------------------------------------------------------------------------------------------------------------------+-----------+-------------+-------------+---------------+-------+----------+-----------|
| query1   | 0             | Homo sapiens                                                                                                        | species   | 99.67       | 99.67       | 0.00          | 1     | 1        | 100.00    |
| query10  | 0             | Actinomycetales bacterium 'ARUP UnID 260'*;Corynebacterium*;uncultured actinobacterium/bacterium*                   | species   | 100.00      | 93.21       | 0.00          | 1     | 1        | 100.00    |
| query11  | 0             | Prevotella*;uncultured Bacteroidales bacterium*;uncultured Bacteroidetes bacterium;uncultured bacterium*/organism   | species   | 100.00      | 91.26       | 0.00          | 1     | 1        | 100.00    |
| query12  | 0             | Apteryx australis*;Bacilli*;Staphylococcus*;bacterium*;uncultured Firmicutes bacterium*;uncultured bacterium*       | species   | 100.00      | 98.26       | 0.00          | 1     | 1        | 100.00    |
| query13  | 0             | Saccharomycetales*;Xanthophyllomyces dendrorhous;uncultured bacterium/eukaryote                                     | species   | 100.00      | 82.88       | 0.00          | 1     | 1        | 100.00    |
| query14  | 0             | Saccharomyces cerevisiae*;uncultured eukaryote                                                                      | species   | 100.00      | 99.00       | 0.00          | 1     | 1        | 100.00    |
| query2   | 0             | Homo sapiens;Pan troglodytes                                                                                        | species   | 97.07       | 95.40       | 0.00          | 1     | 1        | 100.00    |
| query6   | 0             | Escherichia coli;Staphylococcus;bacterium CulaenoE10F;human oral bacterium C20;uncultured bacterium*                | species   | 100.00      | 98.62       | 0.00          | 1     | 1        | 100.00    |
| query7   | 0             | Prevotella*;uncultured Bacteroidales bacterium*;uncultured Bacteroidetes bacterium*;uncultured bacterium*/organism* | species   | 100.00      | 91.61       | 0.00          | 1     | 1        | 100.00    |
| query8   | 0             | Escherichia coli;Staphylococcus;bacterium CulaenoE10F;human oral bacterium C20;uncultured bacterium*                | species   | 100.00      | 98.62       | 0.00          | 1     | 1        | 100.00    |
| query9   | 0             | Bacteria*;Escherichia coli;Staphylococcus;uncultured organism*                                                      | species   | 100.00      | 98.62       | 0.00          | 1     | 1        | 100.00    |
|----------+---------------+---------------------------------------------------------------------------------------------------------------------+-----------+-------------+-------------+---------------+-------+----------+-----------|
```

And

```
classify --columns qaccver,saccver,pident,staxid --lineages lineages.csv --max-group-size 9 blast.csv
|----------+---------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------+-------------+-------------+---------------+-------+----------+-----------|
| specimen | assignment_id | assignment                                                                                                                                                                    | best_rank | max_percent | min_percent | min_threshold | reads | clusters | pct_reads |
|----------+---------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------+-------------+-------------+---------------+-------+----------+-----------|
| query1   | 0             | Homo sapiens                                                                                                                                                                  | species   | 99.67       | 99.67       | 0.00          | 1     | 1        | 100.00    |
| query10  | 0             | Actinomycetales bacterium 'ARUP UnID 260'*;Corynebacterium*;uncultured actinobacterium/bacterium*                                                                             | species   | 100.00      | 93.21       | 0.00          | 1     | 1        | 100.00    |
| query11  | 0             | Prevotella amnii/bivia;Prevotella sp. 3-5;uncultured Bacteroidales bacterium*;uncultured Bacteroidetes bacterium;uncultured Prevotella sp.*;uncultured bacterium*/organism    | species   | 100.00      | 91.26       | 0.00          | 1     | 1        | 100.00    |
| query12  | 0             | Apteryx australis*;Bacilli*;Staphylococcus*;bacterium*;uncultured Firmicutes bacterium*;uncultured bacterium*                                                                 | species   | 100.00      | 98.26       | 0.00          | 1     | 1        | 100.00    |
| query13  | 0             | Saccharomycetales*;Xanthophyllomyces dendrorhous;uncultured bacterium/eukaryote                                                                                               | species   | 100.00      | 82.88       | 0.00          | 1     | 1        | 100.00    |
| query14  | 0             | Saccharomyces cerevisiae*;uncultured eukaryote                                                                                                                                | species   | 100.00      | 99.00       | 0.00          | 1     | 1        | 100.00    |
| query2   | 0             | Homo sapiens;Pan troglodytes                                                                                                                                                  | species   | 97.07       | 95.40       | 0.00          | 1     | 1        | 100.00    |
| query6   | 0             | Escherichia coli;Staphylococcus;bacterium CulaenoE10F;human oral bacterium C20;uncultured bacterium*                                                                          | species   | 100.00      | 98.62       | 0.00          | 1     | 1        | 100.00    |
| query7   | 0             | Prevotella amnii/bivia*;Prevotella sp. 3-5;uncultured Bacteroidales bacterium*;uncultured Bacteroidetes bacterium*;uncultured Prevotella sp.*;uncultured bacterium*/organism* | species   | 100.00      | 91.61       | 0.00          | 1     | 1        | 100.00    |
| query8   | 0             | Escherichia coli;Staphylococcus;bacterium CulaenoE10F;human oral bacterium C20;uncultured bacterium*                                                                          | species   | 100.00      | 98.62       | 0.00          | 1     | 1        | 100.00    |
| query9   | 0             | Escherichia coli;Staphylococcus;bacterium CulaenoE10F;human oral bacterium C20;uncultured bacterium*/organism*                                                                | species   | 100.00      | 98.62       | 0.00          | 1     | 1        | 100.00    |
|----------+---------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------+-------------+-------------+---------------+-------+----------+-----------|
```

And using `--max-group-size 1`:

```
classify --columns qaccver,saccver,pident,staxid --lineages lineages.csv --max-group-size 1 blast.csv
|----------+---------------+--------------+--------------+-------------+-------------+---------------+-------+----------+-----------|
| specimen | assignment_id | assignment   | best_rank    | max_percent | min_percent | min_threshold | reads | clusters | pct_reads |
|----------+---------------+--------------+--------------+-------------+-------------+---------------+-------+----------+-----------|
| query1   | 0             | Homo sapiens | species      | 99.67       | 99.67       | 0.00          | 1     | 1        | 100.00    |
| query10  | 0             | Bacteria*    | superkingdom | 100.00      | 93.21       | 0.00          | 1     | 1        | 100.00    |
| query11  | 0             | root*        | root         | 100.00      | 91.26       | 0.00          | 1     | 1        | 100.00    |
| query12  | 0             | root*        | root         | 100.00      | 98.26       | 0.00          | 1     | 1        | 100.00    |
| query13  | 0             | root*        | root         | 100.00      | 82.88       | 0.00          | 1     | 1        | 100.00    |
| query14  | 0             | Eukaryota*   | superkingdom | 100.00      | 99.00       | 0.00          | 1     | 1        | 100.00    |
| query2   | 0             | Homininae    | subfamily    | 97.07       | 95.40       | 0.00          | 1     | 1        | 100.00    |
| query6   | 0             | Bacteria*    | superkingdom | 100.00      | 98.62       | 0.00          | 1     | 1        | 100.00    |
| query7   | 0             | root*        | root         | 100.00      | 91.61       | 0.00          | 1     | 1        | 100.00    |
| query8   | 0             | Bacteria*    | superkingdom | 100.00      | 98.62       | 0.00          | 1     | 1        | 100.00    |
| query9   | 0             | root*        | root         | 100.00      | 98.62       | 0.00          | 1     | 1        | 100.00    |
|----------+---------------+--------------+--------------+-------------+-------------+---------------+-------+----------+-----------|
```

Using the `--specimen` argument the results can be grouped together to further simplify the results:

```
classify --columns qaccver,saccver,pident,staxid --lineages lineages.csv --max-group-size 1 --specimen one blast.csv
|----------+---------------+--------------+--------------+-------------+-------------+---------------+-------+----------+-----------|
| specimen | assignment_id | assignment   | best_rank    | max_percent | min_percent | min_threshold | reads | clusters | pct_reads |
|----------+---------------+--------------+--------------+-------------+-------------+---------------+-------+----------+-----------|
| one      | 0             | root*        | root         | 100.00      | 82.88       | 0.00          | 5     | 5        | 45.45     |
| one      | 1             | Bacteria*    | superkingdom | 100.00      | 93.21       | 0.00          | 3     | 3        | 27.27     |
| one      | 2             | Homo sapiens | species      | 99.67       | 99.67       | 0.00          | 1     | 1        | 9.09      |
| one      | 3             | Homininae    | subfamily    | 97.07       | 95.40       | 0.00          | 1     | 1        | 9.09      |
| one      | 4             | Eukaryota*   | superkingdom | 100.00      | 99.00       | 0.00          | 1     | 1        | 9.09      |
|----------+---------------+--------------+--------------+-------------+-------------+---------------+-------+----------+-----------|
```

If `--columns` is not specified the classifier will check for a header with 
minimum qseqid,sseqid,pident columns.  If no header than blast outfmt 6 columns
are assumed.

### Alignment selection
TODO

### Rank thresholds

The Moose classifier is built to accept dynamic thresholds for any taxonomic
to provide the best possible classification using the `--rank-thresholds`
argument. An example input looks like this:

```
% cl rank_thresholds.csv
|--------+------+---------+--------+-------+-------+--------+-------+---------|
| tax_id | root | kingdom | phylum | class | order | family | genus | species | subspecies |
|--------+------+---------+--------+-------+-------+--------+-------+---------|
| 1      | 75.0 | 75.0    | 80.0   | 90.0  | 93.0  | 95.0   | 97.0  |  99.0   |
|--------+------+---------+--------+-------+-------+--------+-------+---------|
```

Any tax_id can be specified in a rank thresholds file.  If a tax_id is not
present the rank thresholds file the classifier will work its way up the 
reference sequence's taxonomy lineage in order to assign rank thresholds.

The classifier will use the rank threshold table to select the lowest possible
best hits available for classification.  Example usage:

```
classify --columns qaccver,saccver,pident,staxid --lineages lineages.csv --rank-thresholds rank_thresholds.csv --specimen one blast.csv
|----------+---------------+-----------------------------------------------------------------------------------+-----------+-------------+-------------+---------------+-------+----------+-----------|
| specimen | assignment_id | assignment                                                                        | best_rank | max_percent | min_percent | min_threshold | reads | clusters | pct_reads |
|----------+---------------+-----------------------------------------------------------------------------------+-----------+-------------+-------------+---------------+-------+----------+-----------|
| one      | 0             | Bacteroidetes*;uncultured bacterium*/organism*                                    | species   | 100.00      | 99.27       | 99.00         | 2     | 2        | 18.18     |
| one      | 1             | Bacteria*;Escherichia coli;Staphylococcus                                         | species   | 100.00      | 99.31       | 99.00         | 2     | 2        | 18.18     |
| one      | 2             | Saccharomyces cerevisiae*;uncultured eukaryote                                    | species   | 100.00      | 99.33       | 99.00         | 1     | 1        | 9.09      |
| one      | 3             | Homo sapiens                                                                      | species   | 99.67       | 99.67       | 99.00         | 1     | 1        | 9.09      |
| one      | 4             | Homo                                                                              | genus     | 97.07       | 97.07       | 97.00         | 1     | 1        | 9.09      |
| one      | 5             | Clavispora lusitaniae*                                                            | species   | 100.00      | 100.00      | 99.00         | 1     | 1        | 9.09      |
| one      | 6             | Bacteria*;uncultured organism*                                                    | species   | 100.00      | 99.31       | 99.00         | 1     | 1        | 9.09      |
| one      | 7             | Apteryx australis*;Bacteria*;Firmicutes*                                          | species   | 100.00      | 99.31       | 99.00         | 1     | 1        | 9.09      |
| one      | 8             | Actinomycetales bacterium 'ARUP UnID 260'*;Corynebacterium*;uncultured bacterium* | species   | 100.00      | 99.64       | 99.00         | 1     | 1        | 9.09      |
|----------+---------------+-----------------------------------------------------------------------------------+-----------+-------------+-------------+---------------+-------+----------+-----------|
```

There are a few things to notice when using a rank thresholds table.
The first is the min_percent column will correspond to the lowest rank 
threshold used for hit selection.  The second is the difference in 
classifications after dropping hits below the min_threshold.

Lastly, the genus level Homo classification was not rolled into the 
Homo sapiens classification because the rank thresholds table determined that
the best hits available for that query sequence could only be classified at the genus
level.  This is despite the fact that the genus level Homo classification was
derived from Homo sapien reference sequences.  What the rank thresholds table
defines is classification uncertainty.  So, despite the Homo sapien
reference sequences hits the classifier could not determine the query sequence 
was in fact Homo sapien but only of genus level Homo origin.

### Specimen map

A three column specimen,qseqid,weight file included using the `--specimen-map`
argument.  An example might look like this:

```
cat specimen_map.csv
one,query1,100
one,query2,95
one,query6,75
one,query7,70
one,query8,65
one,query9,60
one,query10,55
one,query11,50
one,query12,45
one,query13,40
one,query14,35
classify --columns qaccver,saccver,pident,staxid --lineages lineages.csv --rank-thresholds rank_thresholds.csv --specimen-map specimen_map.csv blast.csv | cl
|----------+---------------+-----------------------------------------------------------------------------------+-----------+-------------+-------------+---------------+-------+----------+-----------|
| specimen | assignment_id | assignment                                                                        | best_rank | max_percent | min_percent | min_threshold | reads | clusters | pct_reads |
|----------+---------------+-----------------------------------------------------------------------------------+-----------+-------------+-------------+---------------+-------+----------+-----------|
| one      | 0             | Bacteria*;Escherichia coli;Staphylococcus                                         | species   | 100.00      | 99.31       | 99.00         | 140   | 2        | 20.29     |
| one      | 1             | Bacteroidetes*;uncultured bacterium*/organism*                                    | species   | 100.00      | 99.27       | 99.00         | 120   | 2        | 17.39     |
| one      | 2             | Homo sapiens                                                                      | species   | 99.67       | 99.67       | 99.00         | 100   | 1        | 14.49     |
| one      | 3             | Homo                                                                              | genus     | 97.07       | 97.07       | 97.00         | 95    | 1        | 13.77     |
| one      | 4             | Bacteria*;uncultured organism*                                                    | species   | 100.00      | 99.31       | 99.00         | 60    | 1        | 8.70      |
| one      | 5             | Actinomycetales bacterium 'ARUP UnID 260'*;Corynebacterium*;uncultured bacterium* | species   | 100.00      | 99.64       | 99.00         | 55    | 1        | 7.97      |
| one      | 6             | Apteryx australis*;Bacteria*;Firmicutes*                                          | species   | 100.00      | 99.31       | 99.00         | 45    | 1        | 6.52      |
| one      | 7             | Clavispora lusitaniae*                                                            | species   | 100.00      | 100.00      | 99.00         | 40    | 1        | 5.80      |
| one      | 8             | Saccharomyces cerevisiae*;uncultured eukaryote                                    | species   | 100.00      | 99.33       | 99.00         | 35    | 1        | 5.07      |
|----------+---------------+-----------------------------------------------------------------------------------+-----------+-------------+-------------+---------------+-------+----------+-----------|
```

The classifer will interpret each qseqid in the specimen map file as part of
the specimen.  If a qseqid is not included in the blast.csv results then a 
classification of `[no blast result]` will be assigned:

```
cat specimen_map.csv
one,query1,100
one,query2,95
one,query3,90
one,query4,85
one,query5,80
one,query6,75
one,query7,70
one,query8,65
one,query9,60
one,query10,55
one,query11,50
one,query12,45
one,query13,40
one,query14,35
classify --columns qaccver,saccver,pident,staxid --lineages lineages.csv --rank-thresholds rank_thresholds.csv --specimen-map specimen_map.csv blast.csv
|----------+---------------+-----------------------------------------------------------------------------------+-----------+-------------+-------------+---------------+-------+----------+-----------|
| specimen | assignment_id | assignment                                                                        | best_rank | max_percent | min_percent | min_threshold | reads | clusters | pct_reads |
|----------+---------------+-----------------------------------------------------------------------------------+-----------+-------------+-------------+---------------+-------+----------+-----------|
| one      | 0             | [no blast result]                                                                 |           |             |             |               | 255   | 3        | 26.98     |
| one      | 1             | Bacteria*;Escherichia coli;Staphylococcus                                         | species   | 100.00      | 99.31       | 99.00         | 140   | 2        | 14.81     |
| one      | 2             | Bacteroidetes*;uncultured bacterium*/organism*                                    | species   | 100.00      | 99.27       | 99.00         | 120   | 2        | 12.70     |
| one      | 3             | Homo sapiens                                                                      | species   | 99.67       | 99.67       | 99.00         | 100   | 1        | 10.58     |
| one      | 4             | Homo                                                                              | genus     | 97.07       | 97.07       | 97.00         | 95    | 1        | 10.05     |
| one      | 5             | Bacteria*;uncultured organism*                                                    | species   | 100.00      | 99.31       | 99.00         | 60    | 1        | 6.35      |
| one      | 6             | Actinomycetales bacterium 'ARUP UnID 260'*;Corynebacterium*;uncultured bacterium* | species   | 100.00      | 99.64       | 99.00         | 55    | 1        | 5.82      |
| one      | 7             | Apteryx australis*;Bacteria*;Firmicutes*                                          | species   | 100.00      | 99.31       | 99.00         | 45    | 1        | 4.76      |
| one      | 8             | Clavispora lusitaniae*                                                            | species   | 100.00      | 100.00      | 99.00         | 40    | 1        | 4.23      |
| one      | 9             | Saccharomyces cerevisiae*;uncultured eukaryote                                    | species   | 100.00      | 99.33       | 99.00         | 35    | 1        | 3.70      |
|----------+---------------+-----------------------------------------------------------------------------------+-----------+-------------+-------------+---------------+-------+----------+-----------|
```

Multiple specimens can be specified with qseqids of the same name:

```
cat specimen_map.csv
one,query1,100
one,query2,95
one,query3,90
one,query4,85
one,query5,80
one,query6,75
one,query7,70
one,query8,65
one,query9,60
one,query10,55
one,query11,50
one,query12,45
one,query13,40
one,query14,35
two,query3,1000
two,query6,500
two,query1,25
two,query8,900
classify --columns qaccver,saccver,pident,staxid --lineages lineages.csv --rank-thresholds rank_thresholds.csv --specimen-map specimen_map.csv blast.csv
|----------+---------------+-----------------------------------------------------------------------------------+-----------+-------------+-------------+---------------+-------+----------+-----------|
| specimen | assignment_id | assignment                                                                        | best_rank | max_percent | min_percent | min_threshold | reads | clusters | pct_reads |
|----------+---------------+-----------------------------------------------------------------------------------+-----------+-------------+-------------+---------------+-------+----------+-----------|
| one      | 0             | [no blast result]                                                                 |           |             |             |               | 255   | 3        | 26.98     |
| one      | 1             | Bacteria*;Escherichia coli;Staphylococcus                                         | species   | 100.00      | 99.31       | 99.00         | 140   | 2        | 14.81     |
| one      | 2             | Bacteroidetes*;uncultured bacterium*/organism*                                    | species   | 100.00      | 99.27       | 99.00         | 120   | 2        | 12.70     |
| one      | 3             | Homo sapiens                                                                      | species   | 99.67       | 99.67       | 99.00         | 100   | 1        | 10.58     |
| one      | 4             | Homo                                                                              | genus     | 97.07       | 97.07       | 97.00         | 95    | 1        | 10.05     |
| one      | 5             | Bacteria*;uncultured organism*                                                    | species   | 100.00      | 99.31       | 99.00         | 60    | 1        | 6.35      |
| one      | 6             | Actinomycetales bacterium 'ARUP UnID 260'*;Corynebacterium*;uncultured bacterium* | species   | 100.00      | 99.64       | 99.00         | 55    | 1        | 5.82      |
| one      | 7             | Apteryx australis*;Bacteria*;Firmicutes*                                          | species   | 100.00      | 99.31       | 99.00         | 45    | 1        | 4.76      |
| one      | 8             | Clavispora lusitaniae*                                                            | species   | 100.00      | 100.00      | 99.00         | 40    | 1        | 4.23      |
| one      | 9             | Saccharomyces cerevisiae*;uncultured eukaryote                                    | species   | 100.00      | 99.33       | 99.00         | 35    | 1        | 3.70      |
| two      | 0             | Bacteria*;Escherichia coli;Staphylococcus                                         | species   | 100.00      | 99.31       | 99.00         | 1400  | 2        | 57.73     |
| two      | 1             | [no blast result]                                                                 |           |             |             |               | 1000  | 1        | 41.24     |
| two      | 2             | Homo sapiens                                                                      | species   | 99.67       | 99.67       | 99.00         | 25    | 1        | 1.03      |
|----------+---------------+-----------------------------------------------------------------------------------+-----------+-------------+-------------+---------------+-------+----------+-----------|
```

If a query sequence is not included in the specimen map but returned as part
of the blast.csv results then it will be added as its own specimen:

```
cat specimen_map.csv
one,query1,100
one,query4,85
one,query5,80
one,query6,75
one,query7,70
classify --columns qaccver,saccver,pident,staxid --lineages lineages.csv --rank-thresholds rank_thresholds.csv --specimen-map specimen_map.csv blast.csv
|----------+---------------+-----------------------------------------------------------------------------------+-----------+-------------+-------------+---------------+-------+----------+-----------|
| specimen | assignment_id | assignment                                                                        | best_rank | max_percent | min_percent | min_threshold | reads | clusters | pct_reads |
|----------+---------------+-----------------------------------------------------------------------------------+-----------+-------------+-------------+---------------+-------+----------+-----------|
| one      | 0             | [no blast result]                                                                 |           |             |             |               | 165   | 2        | 40.24     |
| one      | 1             | Homo sapiens                                                                      | species   | 99.67       | 99.67       | 99.00         | 100   | 1        | 24.39     |
| one      | 2             | Bacteria*;Escherichia coli;Staphylococcus                                         | species   | 100.00      | 99.31       | 99.00         | 75    | 1        | 18.29     |
| one      | 3             | Bacteroidetes*;uncultured bacterium*/organism*                                    | species   | 100.00      | 99.27       | 99.00         | 70    | 1        | 17.07     |
| query10  | 0             | Actinomycetales bacterium 'ARUP UnID 260'*;Corynebacterium*;uncultured bacterium* | species   | 100.00      | 99.64       | 99.00         | 1     | 1        | 100.00    |
| query11  | 0             | Bacteroidetes*;uncultured bacterium*/organism                                     | species   | 100.00      | 99.27       | 99.00         | 1     | 1        | 100.00    |
| query12  | 0             | Apteryx australis*;Bacteria*;Firmicutes*                                          | species   | 100.00      | 99.31       | 99.00         | 1     | 1        | 100.00    |
| query13  | 0             | Clavispora lusitaniae*                                                            | species   | 100.00      | 100.00      | 99.00         | 1     | 1        | 100.00    |
| query14  | 0             | Saccharomyces cerevisiae*;uncultured eukaryote                                    | species   | 100.00      | 99.33       | 99.00         | 1     | 1        | 100.00    |
| query2   | 0             | Homo                                                                              | genus     | 97.07       | 97.07       | 97.00         | 1     | 1        | 100.00    |
| query8   | 0             | Bacteria*;Escherichia coli;Staphylococcus                                         | species   | 100.00      | 99.31       | 99.00         | 1     | 1        | 100.00    |
| query9   | 0             | Bacteria*;uncultured organism*                                                    | species   | 100.00      | 99.31       | 99.00         | 1     | 1        | 100.00    |
|----------+---------------+-----------------------------------------------------------------------------------+-----------+-------------+-------------+---------------+-------+----------+-----------|
```

### copy numbers

Multiple copies of the gene may be present in a species genome which may
distort the relative weight abundance of a classification.  The Moose
Classifier excepts a two column csv file with columns `--copy-numbers`:

```
|--------+-------|
| tax_id | count |
|--------+-------|
```

and will divide the final classification tax_id by the count number in this
file and expressed under the `corrected` column in the output file.  This is
useful for adjusting relative abundance of species when, for example, 
doing 16s classifications.


