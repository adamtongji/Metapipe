#!/usr/bin/env python

import os,sys
import json
import argparse
import subprocess
from decorator import time_func, time_dec


def sh(args):

    return subprocess.call(args, shell=True)


def input_check(*files):
    for _files in files[0]:
        if _files.endswith("gz"):
            # print "If your run ciri,please uncompress the gzip file ^_^"
            pass
            # sys.exit(1)
        elif _files.endswith("fastq") or _files.endswith("fq"):
            continue
        else:
            print _files
            print "Unknown input format"
            sys.exit(1)
    if len(files)>1:
        _file0 = files[0]+files[1]
        if len(_file0)>len(set(_file0)):
                print "Same files in input.  Pleas check treat and control filenames!"
                sys.exit(1)

    for _file in files:
        for each in _file:
            if not os.path.isfile(each):
                print '{0} do not exist!'.format(each)
                sys.exit(1)


def parse_args():
    myparser=argparse.ArgumentParser(description="Analysis pipeline for MetaMed database")
    shareparser = argparse.ArgumentParser(add_help=False)
    shareparser.add_argument('--input', type=str,required=True, help="Input fastq files")
    shareparser.add_argument('--outdir', type=str,required=True, default="./"
                             ,help = "Output directory [deafult:./]")
    shareparser.add_argument('--outprefix', type=str, required=True, default="output",
                             help="Output filename prefix [default:output]")
    shareparser.add_argument('--keeptemp',action="store_true",default=False,
                             help="Keep all temp file for mapping and expression estimation")
    subparser= myparser.add_subparsers(help="meta_pipe.py command help", dest = "command")
    wgsparser = subparser.add_parser('WGS',help="Input whole genome sequencing data",
                                       parents=[shareparser],add_help=True)
    # wgsparser.add_argument('--bowtie', type=str,default = "bowtie2",
    #                        help = "Bowtie2 path")
    wgsparser.add_argument('--index', type=str, required=True,
                           help="Bowtie2 index path")
    wgsparser.add_argument('--thread',type=int,default=1,
                           help="Number of cpu cores used for this pipeline [default:1]")
    wgsparser.add_argument('--sensitive',action="store_true",default=False,
                           help='Turn this options on if BGC mapping rate is very low in normal ratio.\
                                ')
    s16parser = subparser.add_parser('16S',help="Input 16s rDNA sequencing data",
                                     parents=[shareparser],add_help=True)
    # s16parser.add_argument('--qiime',type=str,default ='',
    #                        help='qiime software path')
    s16parser.add_argument('--mapfile',type=str,required=True,
                           help = 'Sequencing barcode file in qiime format')
    s16parser.add_argument('--filter',type=float,default=0.01,
                           help="Filter out microbes lower than the ratio of metagenome [default:0.01] ")
    args = vars(myparser.parse_args())
    command = args.pop("command", None)
    return command, args


@time_func
def WGS_main(input=None,  index=None, outdir=None, outprefix=None,
            thread=None, sensitive=None,keeptemp=None):
    seqfile = input.split(",")
    input_check(seqfile)
    if not os.path.isdir(outdir):
        sh("mkdir -p {}".format(outdir))
        sh("mkdir -p {}/tmp/".format(outdir))
    if not sensitive:
        if len(seqfile)==1:
            sh("{0} -p {1} -x {2} -U {3} -S {4}/tmp/{5}.sam"\
               .format("bowtie2", thread, index, seqfile[0],outdir,outprefix))
        elif len(seqfile)==2:
            sh("{0} -p {1} -x {2} -1 {3} -2 {6} -S {4}/tmp/{5}.sam" \
               .format("bowtie2", thread, index, seqfile[0], outdir,outprefix ,seqfile[1]))
        else:
            print "Error in input files!"
            sys.exit(1)
    else:
        if len(seqfile) == 1:
            sh("{0} -p {1} --local -x {2} -U {3} -S {4}/tmp/{5}.sam" \
               .format("bowtie2", thread, index, seqfile[0], outdir, outprefix))
        elif len(seqfile) == 2:
            sh("{0} -p {1} --local -x {2} -1 {3} -2 {6} -S {4}/tmp/{5}.sam" \
               .format("bowtie2", thread, index, seqfile[0], outdir, outprefix, seqfile[1]))
        else:
            print "Error in input files!"
            sys.exit(1)
    # samtools version: 1.4.1
    sh("samtools view -hbS {0}/tmp/{1}.sam -o {0}/tmp/{1}.bam -@ {2}".format(outdir, outprefix, thread))
    sh("samtools sort {0}/tmp/{1}.bam -o {0}/tmp/{1}.sorted.bam -T {0}/tmp/{1}.tmp -@ {2}"\
       .format(outdir,outprefix, thread))
    sh("samtools view -b -F 0x04 -q 1 -o {0}/tmp/{1}.filter.bam {0}/tmp/{1}.sorted.bam -@ {2}"\
       .format(outdir,outprefix, thread))
    sh("samtools index {0}/tmp/{1}.filter.bam".format(outdir,outprefix))
    sh("samtools idxstats {0}/tmp/{1}.filter.bam >{0}/tmp/{1}_mapped.txt".format(outdir, outprefix))
    _wgs_statistic("{0}/tmp/{1}_mapped.txt".format(outdir, outprefix),
                   "{0}/wgs_bgc_summary0.txt".format(outdir))
    sh("sort -k2gr,2gr {0}/wgs_bgc_summary0.txt > {0}/wgs_bgc_summary.txt; \
        rm {0}/wgs_bgc_summary0.txt".format(outdir))
    if not keeptemp:
        sh("rm -rf {0}/tmp/".format(outdir))


@time_func
def S16_main(input=None, mapfile=None, outdir=None, outprefix=None,
             keeptemp=None, filter=None): # only support SE sequencing data
    if not os.path.isdir(outdir):
        sh("mkdir -p {}".format(outdir))
        sh("mkdir -p {}/tmp".format(outdir))
    sh("convert_fastaqual_fastq.py -c fastq_to_fastaqual -f {0} -o {1}/tmp/fastaqual" \
           .format(input, outdir))
    sh("split_libraries.py -m {0} -f {1}/tmp/fastaqual/*.fna -q {1}/tmp/fastaqual/*.qual -s 15 -o {1}/tmp/{2}.lib -k -a 6 -r -b 10 -M 5 -e 0" \
           .format(mapfile,outdir,outprefix))
    sh("pick_de_novo_otus.py -i {0}/tmp/{1}.lib/seqs.fna -o {0}/tmp/cdhit_picked_otus" \
           .format(outdir, outprefix))
    sh("summarize_taxa_through_plots.py -i {0}/tmp/cdhit_picked_otus/otu_table.biom \
    -o {0}/tmp/cdhit_picked_otus/taxa_summary -m {1} 2>/dev/null" \
           .format(outdir, mapfile))

    _S16_statistic("{0}/tmp/cdhit_picked_otus/taxa_summary/otu_table_L6.txt".format(outdir),
                   "{0}/S16_bgc_summary0.txt".format(outdir), filter)
    sh("sort -k2gr,2gr {0}/S16_bgc_summary0.txt > {0}/S16_bgc_summary.txt; \
     rm {0}/S16_bgc_summary0.txt".format(outdir))
    if not keeptemp:
        sh("rm -rf {0}/tmp/".format(outdir))


def _S16_statistic(infile, outfile, filters):
    with open(outfile,"w") as fo:
        myf = [i.rstrip().split("\t") for i in open(infile)]
        outf = []
        for _line in myf:
            if not _line[0].startswith("#"):
                microbe = _line[0].split(";")[-1].split("_")[-1]
                ratio = "{:.4f}".format(float(_line[1]))
                if float(ratio)>filters:
                    g = open("m2bgc.json")
                    my_dict = json.load(g)
                    if my_dict.has_key(microbe):
                        bgc= my_dict[microbe]
                        outf.append([bgc, ratio])
        for _line in outf:
            outline = "\t".join(_line)
            print >>fo, outline


def _wgs_statistic(infile, outfile):
    with open(outfile,"w") as fo:
        myf = [i.rstrip().split("\t") for i in open(infile)]
        outf = []
        for _line in myf:
            if _line[0].startswith("B") and int(_line[2])>0:
                g = open("16s_reference_json.json")
                my_dict = json.load(g)
                my_key = _line[0].split("|")[0]
                if my_dict.has_key(my_key):
                    print str(my_key)
                    bgc = my_dict[str(my_key)]["description"]
                    counts = str(_line[2])
                    outf.append([bgc, counts])

        outf2 = [str("\t".join(i)) for i in outf]
        for _lines in outf2:

            print >> fo, _lines


@time_dec
def main():
    command_functions = \
        {'WGS': WGS_main,
         '16S': S16_main}
    command, args = parse_args()
    command_functions[command](**args)


if __name__=="__main__":

    reload(sys)
    sys.setdefaultencoding('utf-8')
    main()