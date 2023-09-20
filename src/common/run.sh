#!/bin/bash

# Load variables from config file
# source /home/jzj/HiC-OpenCV/cfg-autohic.txt
echo "Run AutoHiC"
echo "--------------------------------"
source $1
date


# mkdir folder
mkdir -p $RESULT_DIR/$JOB_NAME/data/reference $RESULT_DIR/$JOB_NAME/data/restriction_sites
mkdir -p $RESULT_DIR/$JOB_NAME/hic_results/juicer
mkdir -p $RESULT_DIR/$JOB_NAME/hic_results/3d-dna
mkdir -p $RESULT_DIR/$JOB_NAME/autohic_results $RESULT_DIR/$JOB_NAME/logs

# get genome name from reference genome
filename_with_extension=$(basename $REFERENCE_GENOME)

# remove extension
GENOME_NAME=$(echo "$filename_with_extension" | cut -d'.' -f1)

# link data
ln -s $REFERENCE_GENOME $RESULT_DIR/$JOB_NAME/data/reference
NEW_GENOME_DIR=$RESULT_DIR/$JOB_NAME/data/reference/$GENOME_NAME.${REFERENCE_GENOME##*.}
ln -s $FASTQ_DIR $RESULT_DIR/$JOB_NAME/hic_results/juicer/$GENOME_NAME

# Juicer
echo "Start Index genome"
bwa index $NEW_GENOME_DIR > $RESULT_DIR/$JOB_NAME/logs/bwa_index.log 2>&1
echo "Bwa index done"

echo "Start generate site positions"
cd $RESULT_DIR/$JOB_NAME/data/restriction_sites
python $JUICER_DIR/misc/generate_site_positions.py $ENZYME $GENOME_NAME $NEW_GENOME_DIR
echo "Generate site positions done"

echo "Start generate chrom sizes"
ENZYME_TXT=$RESULT_DIR/$JOB_NAME/data/restriction_sites/$GENOME_NAME"_"$ENZYME.txt
CHROM_SIZES=$RESULT_DIR/$JOB_NAME/data/restriction_sites/$GENOME_NAME.chrom.sizes
awk 'BEGIN{OFS="\t"}{print $1, $NF}'  $ENZYME_TXT > $CHROM_SIZES
echo "Generate chrom sizes done"

echo "Start run Juicer done"
CHROM_SIZES=$RESULT_DIR/$JOB_NAME/data/restriction_sites/$GENOME_NAME.chrom.sizes
NEW_FASTQ_DIR=$RESULT_DIR/$JOB_NAME/hic_results/juicer/$GENOME_NAME
$JUICER_DIR/scripts/juicer.sh -z $NEW_GENOME_DIR -p $CHROM_SIZES -y $ENZYME_TXT -s $ENZYME -d $NEW_FASTQ_DIR -D $JUICER_DIR -S early -t $N_CPU > $RESULT_DIR/$JOB_NAME/logs/juicer.log 2>&1
echo "Juicer done"


# 3d-dna
echo "Strat run 3d-dna done"
cd $RESULT_DIR/$JOB_NAME/hic_results/3d-dna
MERGED_NODUPS=$RESULT_DIR/$JOB_NAME/hic_results/juicer/$GENOME_NAME/aligned/merged_nodups.txt
echo "--------------------------------"
echo ""
date
$TD_DNA_DIR/run-asm-pipeline.sh -r $NUMBER_OF_EDIT_ROUNDS $NEW_GENOME_DIR $MERGED_NODUPS > $RESULT_DIR/$JOB_NAME/logs/3d-dna.log 2>&1
echo "3d-dna done"

date