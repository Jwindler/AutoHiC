# Detailed Results of AutoHiC



## autohic_results

```sh
autohic_results/
├── 0
│   ├── chr_len_filtered_errors.json
│   ├── chr_len_remove_error.txt
│   ├── debris_error.json
│   ├── error_summary.json
│   ├── infer_result
│   ├── inversion_error.json
│   ├── len_filtered_errors.json
│   ├── len_filtered_errors.xlsx
│   ├── len_remove_error.xlsx
│   ├── overlap_filtered_errors.json
│   ├── overlap_remove_error.txt
│   ├── png
│   ├── score_filtered_errors.xlsx
│   ├── translocation_error.json
│   └── zoomed_errors.json
├── 1
├── 2
├── 3
├── 4
└── chromosome
```

Mainly the intermediate files of AutoHiC:

- `chr_len_filtered_errors.json`: Errors filtered by chromosome length
- `chr_len_remove_error.txt`: Errors removed based on chromosome length
- `debris_error.json`: Debris error information
- `error_summary.json`: Summary information on the number of errors per stage
- `infer_result`: Visualization of errors identified by the AutoHiC model
- `inversion_error.json`: Inversion error information
- `len_filtered_errors.json`: Errors filtered by error length (json format)
- `len_filtered_errors.xlsx`: Errors filtered by error length (xlsx format)
- `len_remove_error.xlsx`: Errors removed based on error length
- `overlap_filtered_errors.json`: Errors filtered by overlap
- `overlap_remove_error.txt`: Errors removed based on overlap
- `png`: Image generated from the interaction matrix for identifying errors
- `score_filtered_errors.xlsx`: Errors filtered by confidence score
- `translocation_error.json`: Translocation error information
- `zoomed_errors.json`: Error scaled by threshold



## data

```sh
data/
├── reference
│   ├── contig.fa 
│   ├── contig.fa.amb
│   ├── contig.fa.ann
│   ├── contig.fa.bwt
│   ├── contig.fa.pac
│   └── contighd.fa.sa
└── restriction_sites
    ├── contig.chrom.sizes
    └── contig_DpnII.txt
```

- `reference`: contig's bwa index results

- `contig_DpnII.txt`: restriction enzyme site
- `contig.chrom.sizes`: contig sequence length



## hic_results

```sh
hic_results/
├── 3d-dna
└── juicer
```

- `3d-dna`: 3d-dna results

- `juicer`: Juicer results



## logs

```sh
logs/
├── 3d-dna.log
├── epoch_3.log
├── epoch_4.log
├── bwa_index.log
├── chromosome_epoch.log
└── juicer.log
```

- `bwa_index.log`: bwa index log
- `Juicer.log`: Juicer log
- `3d-dna.log`: 3d-dna log
- `epoch_x.log`: AutoHiC iterative adjustment log
- `chromosome_epoch.log`: AutoHiC divides chromosomes log



## quast_output

```sh
quast_output/
├── chromosome
└── contig
```

- `contig`: Contig level genome QUAST results
- `chromosome`: Chromosome level genome QUAST results
