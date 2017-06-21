#!/bin/bash

conda create -n metamed -c bioconda python=2.7 qiime matplotlib=1.4.3 mock nose bowtie2 samtools=1.4.1  
# echo "source activate metamed" >> ~/.bashrc
# source ~/.bashrc