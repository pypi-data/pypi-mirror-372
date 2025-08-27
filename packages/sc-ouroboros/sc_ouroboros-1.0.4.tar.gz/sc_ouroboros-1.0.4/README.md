<p align="center" style="margin-bottom: 0;">
  <img src="docs/media/sphere_snake.png" alt="Ouroboros logo" width="120">
</p>
<h1 align="center" style="margin-top: 0;">Ouroboros</h1>

Ouroboros is designed to find cell cycle phase, cell cycle pseudotime and dormancy depth in scRNAseq datasets. It uses transfer learning within the latent space of a variational autoencoder to infer these features on new datasets. 

For more information see the Wiki: *add wiki*

## Installation 

Ouroboros supports Python **3.9–3.10**.

Install from PyPI:
```bash 
pip install sc-ouroboros
```
Install from Conda:
```bash
conda install glchang::sc-ouroboros
```

Install directly from GitHub with:
```bash 
pip install git+https://github.com/haleymac/Ouroboros.git
```

[ScPhere](https://github.com/klarman-cell-observatory/scPhere) is included as part of Ouroboros and has been updated for compatibility with TensorFlow 2. ScPhere was originally developed by Jiarui Ding and colleagues at the Klarman Cell Observatory.

#### Optional dependency
Cartopy – required for some plotting functions, such as plot_robinson_projection. Installation via conda is recommended to ensure required system dependencies are installed first:
```bash 
conda install cartopy
```
## Running Ouroboros 
For a full tutorial see the Wiki: *add wiki*

Ouroboros is a command line tool designed to take either a saved .h5ad object or if you are an R user a saved csv with a cell/gene count matrix. 


### To run Ouroboros on an h5ad/ Scanpy object

It's important to note that Ouroboros only works on **raw** counts, so make sure your raw counts are saved under adata.layers['raw_counts'] where Ouroboros can find them, and then save your scanpy object as an h5ad:

```python 
anndata.write_h5ad(adata.h5ad)
```

Then you can run Ouroboros on the command line like so: 
```bash 
ouroboros \
    --data /path/to/h5ad  \
    --data_type h5ad \
    --species human \
    --outdir /path/to/output/directory \
    --seed 0 \
    --repeat 5 
```

Arguments: 
| Argument      | Description                                                                   |
| ------------- | ----------------------------------------------------------------------------- |
| `--data`      | **Required.** Path to your input data file. Must be a `.h5ad` or `.csv` file. |
| `--data_type` | **Required.** Format of the input data. Must be `h5ad` or `csv`.              |
| `--species`   | Species of origin for the dataset. Must be `human` or `mouse`.  Default is human |
| `--outdir`    | Output directory where results (embeddings, figures, logs) will be saved. Default is '.'|
| `--seed`      | Seed used for Ouroborous for data reproducibility. Default is 0 |
| `--repeat`*    | Number of times to retrain model (only if input data is missing any training genes). Default is 1.|

\* If any gene is missing from training feature set from the input data, the model must be retrained. To ensure robust performance, Ouroboros will retrain the VAE {repeat} times and select the model that correlates with the consensus. However, increasing the repeat parameter will significantly extend runtime.





### To run Ouroboros on an R/Seurat object
Apologies, I'm mostly a python user so Ouroboros is largely tailered to those who use scanpy and h5ad objects. Given this, running Ouroboros for an R user requires a little bit of fussing, but is possible! Here are the instructions for doing so:

It's important to note that Ouroboros only works on **raw** counts. If you are using R (and therefore probably Seurat?) you will need to save your counts as a csv, with genes as your column names and cell ids under the columns 'cell_id' like so: 

** MAKE SURE YOU SAVE YOUR RAW COUNTS, NOT YOUR NORMALIZED COUNTS!!!!**
```
# Extract RAW counts matrix from Seurat object
counts <- GetAssayData(seurat_obj, slot = "counts")

# Transpose and convert to data frame
df <- as.data.frame(Matrix::t(counts))

# Add cell IDs as a column named "cell_id"
df$cell_id <- rownames(df)

# Move 'cell_id' to the first column
df <- df[, c("cell_id", setdiff(names(df), "cell_id"))]

# Write to CSV
write.csv(df, file = "test_df.csv", row.names = FALSE)
```

Once your h5ad or csv is saved, you can call Ouroboros on the command line:






## Plotting Ouroboros output

We have included several python functions to help you explore the Ouroboros output sphere. 

See Wiki tutorials for more information [*add link*]


## Acknowledgements
This project makes use of scPhere, developed by the Broad Institute and distributed under the BSD 3-Clause License.

We have included a lightly modified version of scPhere (updated for TensorFlow 2.x support) within this repository.

If you use functionality derived from scPhere, please also cite:
Ding, J., Regev, A. Deep generative model embedding of single-cell RNA-Seq profiles on hyperspheres and hyperbolic spaces. Nat Commun 12, 2554 (2021). https://doi.org/10.1038/s41467-021-22851-4

## License
Ouroboros is distributed under the MIT License (see LICENSE).
scPhere is distributed under the BSD 3-Clause License (see scphere/LICENSE).
