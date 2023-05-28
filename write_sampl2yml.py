#! /usr/bin/env python3
#This script is used to write the paths of the samples, output f#iles and reference files in YAML format.
#Author:yc_lu

import os
import yaml

#Checking whether the file exists
def check_file(file_path):
    return os.path.isfile(file_path)
    
#Getting all fq_file names and paths
fastq_files=[]

for root, dirs, files in os.walk("/home/lyc/PRJNA230969/data"):
    for file in files:
        if file.endswith("_1.fastq.gz") or \
        file.endswith("_1.fq.gz"):
            sample_name=file.split("_1")[0]
            r1_path=os.path.join(root,file)
            r2_path=os.path.join(root,file.replace("_1","_2"))
            if check_file(r1_path) and check_file(r2_path):
                fastq_files.append((sample_name, \
                r1_path,r2_path))

#Building_config_file
config={
    'samples': {},
    'ref_genome': 'ref/mm10/chr19.fa',
    'ref_genome_gtf': 'annotations/gtf' \
    '/GRCm38.83.chr19.gtf'
}

for sample_name, r1_path, r2_path in fastq_files:
    config['samples'][sample_name]={
        "r1": r1_path,
        "r2": r2_path 
    }

with open("config.yaml","w") as f:
    yaml.dump(config,f)

