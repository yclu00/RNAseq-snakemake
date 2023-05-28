configfile: "config.yaml"
import os
   

hisat2_index_prefix="ref/index/chr19"
rule all:
    input:
        "featureCounts_Output_Result/matrix.txt"   
rule fastqc:
    input:
        expand("data/{sample}_1.fastq.gz",sample=config["samples"]), 
        expand("data/{sample}_2.fastq.gz",sample=config["samples"])
    output:
        expand("results/fastqc/{sample}_1_fastqc.html",sample=SAMPLES)  
        expand("results/fastqc/{sample}_2_fastqc.html",sample=SAMPLES)
    conda:
        "environment.yaml"
    shell:       
        "fastqc -t 2 -o results/fastqc {input}"

rule trim:
    input:
        fq1=expand("data/{sample}_1.fastq.gz",sample=sample=config["samples"]),
        fq2=expand("data/{sample}_2.fastq.gz",sample=sample=config["samples"])
    output:
        fq1_out=expand("results/trimmomatic/{sample}_1.paired.fq.gz",sample=SAMPLES),
        fq2_out=expand("results/trimmomatic/{sample}_2.paired.fq.gz",sample=SAMPLES),
        fq1_unpaired=expand("results/trimmomatic/{sample}_1.unpaired.fq.gz",sample=SAMPLES),
        fq2_unpaired=expand("results/trimmomatic/{sample}_2.unpaired.fq.gz",sample=SAMPLES)
    conda:
        "environment.yaml"
    shell:
        "trimmomatic PE -threads 4 {input.fq1} {input.fq2} "
        "{output.fq1_out} {output.fq1_unpaired} "  
        "{output.fq2_out} {output.fq2_unpaired} "
        "ILLUMINACLIP:adapter:2:30:10 "
        "SLIDINGWINDOW:5:20 LEADING:5 TRAILING:5 MINLEN:50"

#hisat2_index_prefix="ref/index/chr19"
rule hisat2_build:
    input:
        config['ref_genome']
    output:
        hisat2_index_prefix + ".1.ht2"
    conda:
        "environment.yaml"
    shell:
        "hisat2-build -p 2 {input} {hisat2_index_prefix} "
rule hisat2:
    input:
        fq1=expand("results/trimmomatic/{sample}_1.paired.fq.gz",sample=SAMPLES),
        fq2=expand("results/trimmomatic/{sample}_2.paired.fq.gz",sample=SAMPLES),
        ref_dir=hisat2_index_prefix + ".1.ht2"
    output:
        temp(expand("results/hisat2Mapping/{sample}.sam",sample=SAMPLES))
    threads:8
    log:
        hisat2_log="results/hisat2Mapping/hisat2Mapping.log"
    conda:
        "environment.yaml"
    shell:    
        "(hisat2 -p {threads} -x {hisat2_index_prefix} "
        "-1 {input.fq1} -2 {input.fq2}  "
        "-S {output} --new-summary) "
        "2> {log.hisat2_log}" 

rule sam2bam:
    input:
        sam_file=expand("results/hisat2Mapping/{sample}.sam",sample=SAMPLES)
    output:
        protected(expand("results/hisat2Mapping/{sample}.srt.bam",sample=SAMPLES))
    threads: 8
    params: "4G"
    conda:
        "environment.yaml"
    shell:
        "samtools sort -@ {threads} -m {params} "
        "-o {output} {input.sam_file}"
rule bam_index:
    input:
        expand("results/hisat2Mapping/{sample}.srt.bam",sample=SAMPLES)
    output:
        expand("results/hisat2Mapping/{sample}.srt.bam.bai",sample=SAMPLES)
    conda:
        "environment.yaml"
    shell:
        "samtools index {input} "
rule quantfication:
    input:
        config["ref_genome_gtf"],
        srt_bam=expand("results/hisat2Mapping/{sample}.srt.bam",sample=SAMPLES)
    output:
        mtr="featureCounts_Output_Result/matrix.txt"
    threads: 8
    conda:
        "environment.yaml"
    shell:
        "featureCounts -p -T {threads} -a {input} "
        "-o {output.mtr} "
