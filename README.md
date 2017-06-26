README
=============

## Metapipe: Preprocessing pipeline for MetaMed database

### Download and Install: <br>
**Requirements:** <br>
`Python 2.7.*` https://www.python.org/downloads/ <br>
`Miniconda` https://conda.io/miniconda.html <br>


#### Linux or Macox command line installation
```Bash
## First, install the environment
bash install.sh
## Second, activate the environment before run this pipeline
source activate metapipe
## Finally, run metapipe
python metapipe.py [options]
```
#### Download bowtie2 index (for WGS/shotgun data) <br>
```Bash
wget -c 106.14.203.86:8080/data/bowtie2index.tar.gz
```
or: <br>
[Download Index Here](http://106.14.203.86:8080/data/bowtie2index.tar.gz "悬停显示")

### Main arguments: <br>

```Bash
usage: metapipe.py [-h] {WGS,16S} ... 
    WGS       Input whole genome sequencing data 
    16S       Input 16s rDNA sequencing data 
```
#### WGS Mode <br>
```Bash
usage: metapipe.py WGS [-h] --input INPUT --outdir OUTDIR --outprefix
                       OUTPREFIX [--keeptemp] --index INDEX [--thread THREAD]
                       [--sensitive]
```
Example: <br>
```Bash
python meta_pipe.py WGS --input wgs_r1.fastq,wgs_r2.fastq --index ./bowtie2index/mibig_bgc --outdir ./wgs_result 
--outprefix wgs_test --thread 4 --sensitive
```
|  Parameter   |  Introduction |
| :---------- | :-------- |
| -h, --help     |       show this help message and exit |
|  --input INPUT    |     Input fastq files ("a.fq" for sinle end data <br> and "s1.fq,s2.fq" for pair end data ) |
|  --outdir OUTDIR   |   Output directory [deafult:./] |
| --outprefix OUTPREFIX | Output filename prefix [default:output]|
|  --keeptemp      |      Keep all temp files for mapping and expression estimation|
|  --index INDEX     |    Bowtie2 index prefix |
|  --thread THREAD   |    Number of cpu cores used for this pipeline [default:1] |
|  --sensitive      |     Turn this options on if BGC mapping rate is very low in normal mode. |
<br>

#### 16S rDNA Mode <br>
```Bash
usage: metapipe.py 16S [-h] --input INPUT --outdir OUTDIR --outprefix
                       OUTPREFIX [--keeptemp] --mapfile MAPFILE
                       [--filter FILTER]
```
Example: <br>
```Bash
python meta_pipe.py 16S --input ./16s.fastq --outdir ./16s_result --outprefix 16s_test --mapfile ./16s_map.txt
```

|  Parameter   |  Introduction |
| :---------- | :-------- |
|  -h, --help    |        show this help message and exit |
|  --input INPUT   |      Input fastq files |
|  --outdir OUTDIR   |    Output directory [deafult:./] |
|  --outprefix OUTPREFIX | Output filename prefix [default:output] |
|  --keeptemp     |       Keep all temp files for mapping and expression estimation |
|  --mapfile MAPFILE  |   Sequencing barcode file in qiime format |
|  --filter FILTER  |     Filter out microbes lower than the ratio of metagenome [default:0.01] |

#### Sequencing barcode file in qiime format(mapfile) example in tab-delimited format <br>
`#SampleID	BarcodeSequence	LinkerPrimerSequence	Description` <br>
`SRR048044	TCAGCGCAAC	CCGTCAATTCMTTTRAGT	female_Stool`  <br>

### Example output file
#### WGS mode output <br>
|  #BGC names  |  #Read count |
| :---------- | :-------- |
|Epilancin 15X biosynthetic gene cluster |	19|
|Salivaricin 9 biosynthetic gene cluster |	4 |

#### 16S rDNA mode output <br>
|  #BGC names  |  #Percent score |
| :---------- | :-------- |
|Alpha-galactosylceramide biosynthetic gene cluster|	0.3933|
|Flavecin biosynthetic gene cluster	| 0.0139 |


