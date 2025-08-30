# CellProportion

![My Image](image2.png)

A Python package for comparing cell type proportions between experimental groups in **single-cell RNA-seq** and **spatial transcriptomics** data.

## 🚀 Features

- **Flexible Input**: Works directly with AnnData objects or Pandas DataFrames
- **Multiple Statistical Methods**: 
  - `signed_r2` – Signed R² from regression (captures direction + fit strength)
  - `mean_diff` – Simple difference in mean proportions
  - `log2_fc` – Log₂ fold-change for multiplicative differences
  - `corr` – Pearson correlation with group labels
- **Spatial Analysis**: Compare proportions within tissue regions/spatial domains
- **Statistical Testing**: Mann-Whitney U tests with significance categorization
- **Visualization Ready**: Built-in color schemes and customizable color mapping
- **Robust Error Handling**: Comprehensive validation and informative warnings

## 📦 Installation

```bash
pip install cellproportion
```

## 🔧 Quick Start

### Single-Cell Analysis

```python
import pandas as pd
import scanpy as sc
from cellproportion import cell_type_abundance

# Load your single-cell data
adata = sc.read_h5ad("your_data.h5ad")

# Compare cell type proportions between conditions
results = cell_type_abundance(
    adata,                          # AnnData object
    annotation="cell_type",         # Column with cell type labels
    sample_types="condition",       # Column with experimental conditions
    sample_ID="patient_id",         # Column with sample/patient IDs
    sample_types_1="tumor",         # First group for comparison
    sample_types_2="normal",        # Second group for comparison
    method="signed_r2",             # Statistical method
    signed_r2_cutoff=0.15,         # Optional: cutoff for significance
    explain=True                    # Print method explanation
)

print(results.head())
```

### Spatial Transcriptomics Analysis

```python
from cellproportion.spatial import spatial_cell_type_abundance

# Analyze proportions within each spatial region
spatial_results = spatial_cell_type_abundance(
    adata,                          # AnnData with spatial information
    region_col="tissue_region",     # Column with spatial region labels
    annotation="cell_type",
    sample_types="condition", 
    sample_ID="patient_id",
    sample_types_1="tumor",
    sample_types_2="normal",
    method="signed_r2"
)

print(f"Analyzed {spatial_results['region'].nunique()} spatial regions")
print(spatial_results.head())
```

### Using DataFrames

```python
# Works with any DataFrame containing the required columns
metadata_df = pd.DataFrame({
    'cell_type': ['T_cell', 'B_cell', 'Macrophage'] * 100,
    'condition': ['tumor', 'normal'] * 150,
    'patient_id': ['P1', 'P2', 'P3'] * 100,
    # ... other columns
})

results = cell_type_abundance(
    metadata_df,
    annotation="cell_type",
    sample_types="condition",
    sample_ID="patient_id",
    sample_types_1="tumor",
    sample_types_2="normal"
)
```

## 📊 Understanding the Results

The output DataFrame contains:

- **V1**: Cell type annotation
- **V2**: Statistical metric value (depends on method chosen)
- **V3**: P-value from Mann-Whitney U test
- **sig_p**: Significance category (`p<0.01`, `p<0.05`, `p<0.1`, `p<0.5`, `p>0.5`)
- **color**: Color code for visualization

```python
# Example output
print(results[['V1', 'V2', 'V3', 'sig_p']].head())
#         V1        V2      V3   sig_p
# 0   T_cell  0.234567  0.0123  p<0.05
# 1   B_cell -0.123456  0.2341  p<0.5
# 2  NK_cell  0.456789  0.0001  p<0.01
```

## 🎨 Custom Color Mapping

Create a TSV file with your preferred colors:

```tsv
annotation	color
T_cell	#E41A1C
B_cell	#377EB8
NK_cell	#4DAF4A
Macrophage	#984EA3
```

```python
results = cell_type_abundance(
    adata,
    # ... other parameters
    colours_file="my_colors.tsv"
)
```

## 📈 Statistical Methods Explained

```python
from cellproportion.methods import explain_v2

# Get detailed explanations of all methods
explanations = explain_v2()
for method, info in explanations.items():
    print(f"\n{method.upper()}:")
    for key, value in info.items():
        print(f"  {key}: {value}")
```

### Method Comparison

| Method | Best For | Pros | Cons |
|--------|----------|------|------|
| `signed_r2` | Linear relationships | Direction + fit strength | Assumes linearity |
| `mean_diff` | Simple comparisons | Easy interpretation | Ignores variance |
| `log2_fc` | Multiplicative changes | Ratio-based | Sensitive to low values |
| `corr` | Association strength | Scale-invariant | Only linear association |

## 🔬 Advanced Usage

### Batch Processing Multiple Datasets

```python
datasets = ["dataset1.h5ad", "dataset2.h5ad", "dataset3.h5ad"]
all_results = []

for dataset_path in datasets:
    adata = sc.read_h5ad(dataset_path)
    results = cell_type_abundance(adata, method="signed_r2")
    results['dataset'] = dataset_path
    all_results.append(results)

combined_results = pd.concat(all_results, ignore_index=True)
```

### Method Comparison

```python
methods = ["signed_r2", "mean_diff", "log2_fc", "corr"]
method_comparison = {}

for method in methods:
    results = cell_type_abundance(adata, method=method)
    method_comparison[method] = results

# Compare results across methods
comparison_df = pd.DataFrame({
    method: method_comparison[method].set_index('V1')['V2'] 
    for method in methods
})
```

## 📝 Citation

If you use CellProportion in your research, please cite:

```bibtex
@software{cellproportion2024,
  author = {Patel, Ankit},
  title = {CellProportion: Cell type proportion analysis for single-cell and spatial transcriptomics},
  url = {https://github.com/avpatel18/cellproportion},
  version = {1.0.0},
  year = {2025}
}
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🐛 Bug Reports

If you encounter any bugs or have feature requests, please file an issue on [GitHub Issues](https://github.com/avpatel18/cellproportion/issues).

## 📧 Contact

- **Author**: Ankit Patel
- **Email**: ankit.patel@qmul.ac.uk
- **GitHub**: [@avpatel18](https://github.com/avpatel18)
