# AI Gene Enrichment

A comprehensive Python package for performing gene enrichment analysis using multiple bioinformatics tools and AI-powered synthesis. This tool integrates Enrichr, ToppFun, gProfiler, literature search, and AI summarization to provide detailed biological insights from gene lists.

## License

This project is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License (CC-BY-NC 4.0). This means you are free to:

- **Share** — copy and redistribute the material in any medium or format
- **Adapt** — remix, transform, and build upon the material

Under the following terms:
- **Attribution** — You must give appropriate credit and indicate if changes were made
- **NonCommercial** — You may not use the material for commercial purposes

For commercial licensing inquiries, please contact: cboyce3@mgh.harvard.edu

## Installation

### From PyPI (Recommended)

```bash
pip install ai-gene-enrichment
```

### From Source

1. Clone this repository:
   ```bash
   git clone https://github.com/calvinrboyce/ai-gene-enrichment.git
   cd ai-gene-enrichment
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install in development mode:
   ```bash
   pip install -e .
   ```

4. Set up your OpenAI API key:
   ```bash
   # Create a .env file
   echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
   ```

## Usage
AI synthesis requires an API key to access OpenAI's models. API keys can be obtained by PIs or other researchers by setting up an organization at [platform.openai.com](https://platform.openai.com) and adding an API key at [platform.openai.com/settings/organization/api-keys](https://platform.openai.com/settings/organization/api-keys). Note that using more sophisticated models beyond the default may require organization verification and you may have to earn a higher usage tier with OpenAI. With the default model you can expect to spend <$0.03 per gene list

### Basic Usage

```python
import os
import dotenv
from aige import AIGeneEnrichment

# Load environment variables
dotenv.load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize the agent
aige = AIGeneEnrichment(openai_api_key)

# Define your gene list
genes = ["ANLN", "CENPF", "NUSAP1", "TOP2A", "CCNB1", "PRC1", "TPX2", "UBE2C", "BIRC5"]

# Run analysis
results = aige.run_analysis(
    genes=genes,
    email="your.email@example.com",  # Required for NCBI literature search
    background_genes=[],  # Optional background gene set for enrichment analysis
    ranked=True,  # Set to True if genes are ranked by differential expression
    search_terms=["cancer", "metastasis", "cell cycle"],  # Optional literature search terms
    context="This gene list characterizes a cluster of cells in a brain metastasis"
)

# Access results
print(results['summary'])
for theme in results['themes']:
    print(f"Theme: {theme['theme']}")
    print(f"Description: {theme['description']}")
```

### Advanced Configuration

```python
# Customize enrichment sources and parameters
aige = AIGeneEnrichment(
    open_ai_api_key=openai_api_key,
    open_ai_model="gpt-4o",
    results_dir="custom_results",
    enrichr_sources={
        "CellMarker_2024": "CellMarker",
        "MSigDB_Hallmark_2020": "MSigDB-H",
        "ChEA_2022": "ChEA"
    },
    gprofiler_sources=['HPA', 'MIRNA'],
    toppfun_sources=['TFBS', 'MicroRNA'],
    terms_per_source=20,  # Number of terms to retrieve per source
    papers_per_gene=3,    # Number of papers to retrieve per gene
    max_papers=15         # Number of papers to retrieve for full gene list
)

# Example with background gene set
background_genes = ["GENE1", "GENE2", "GENE3", ...]  # Your background gene set
results = agent.run_analysis(
    genes=genes,
    email="your.email@example.com",
    background_genes=background_genes,  # Use custom background for enrichment
    ranked=True,
    search_terms=["cancer", "metastasis"],
    context="Analysis with custom background gene set"
)
```

### Background Gene Sets

The agent supports custom background gene sets for enrichment analysis, which can improve the statistical significance and biological relevance of your results. When a background gene set is provided:

- **Enrichr**: Uses the background genes as the reference set for statistical testing
- **gProfiler**: Uses the background genes as the custom background for enrichment calculations
- **ToppFun**: Currently uses default background (background genes not yet supported)

**Note**: When no background genes are provided (empty list), the tools use their default reference sets.



### Working with Results

The analysis returns a structured dictionary with the following components:

```python
results = {
    'themes': [
        {
            'theme': 'Cell Cycle Regulation',
            'description': 'Genes involved in cell cycle control and progression...',
            'terms': ['GO:0007049', 'KEGG:04110', ...]
        }
    ],
    'summary': 'Comprehensive analysis summary...'
}
```

### Output Files

When `save_results=True` (default), the agent creates an Excel spreadsheet of the results

## Dependencies

- `openai>=1.0.0`: OpenAI API integration
- `requests>=2.31.0`: HTTP requests
- `python-dotenv>=1.0.0`: Environment variable management
- `biopython>=1.82`: PubMed literature search
- `gprofiler-official>=1.0.0`: gProfiler API client
- `openpyxl>=3.1.5`: Excel file generation

## API Reference

### AIGeneEnrichment

Main class for running gene enrichment analysis workflows.

#### Constructor Parameters

- `open_ai_api_key` (str): OpenAI API key (required)
- `open_ai_model` (str): OpenAI model to use (default: "gpt-4.1-mini")
- `results_dir` (str): Directory to save results (default: "aige_results")
- `enrichr_sources` (dict): Enrichr sources to use. Dictionary should map the name of the source (found in Enrichr's documentation) to an abbreviated version to be used in the analysis (default: {})
- `gprofiler_sources` (list): gProfiler sources to use. List should include terms from ['TF', 'MIRNA', 'HPA', 'CORUM'] to be used in the analysis (default: [])
- `toppfun_sources` (list): ToppFun sources to use. List should include terms from ['MousePheno', 'Domain', 'Pubmed', 'Cytoband', 'TFBS', 'GeneFamily', 'Coexpression', 'CoexpressionAtlas', 'ToppCell', 'Computational', 'MicroRNA', 'Drug', 'Disease'] to be used in the analysis (default: ['ToppCell'])
- `terms_per_source` (int): Number of terms per source (default: 20)
- `num_papers` (int): Number of papers to fetch from lit search (default: 20)

#### Methods

##### `run_analysis(genes, email, background_genes=[], ranked=True, search_terms=[], context="None", save_results=True, analysis_name=None)`

Run the complete gene enrichment analysis workflow.

**Parameters:**
- `genes` (List[str]): List of gene symbols to analyze (required)
- `email` (str): Email address for NCBI's reference (required for literature search)
- `background_genes` (List[str]): List of background genes to use for enrichment analysis (default: [])
- `ranked` (bool): Whether the genes are ranked by differential expression (default: True)
- `search_terms` (List[str]): List of search terms to use in literature search (default: [])
- `context` (str): Context of where the genes came from and what you're studying (default: "None")
- `save_results` (bool): Whether to save results to files (default: True)
- `analysis_name` (str): Name for the analysis run, used in file naming (default: None)

**Returns:**
- `Dict[str, Any]`: Themed results dictionary containing:
  - `themes`: List of identified biological themes, each with:
    - `theme`: Theme name
    - `description`: Description of the theme's function and identification rationale
    - `confidence`: Confidence score (0-1)
    - `terms`: List of enrichment terms that contributed to theme identification
  - `summary`: Comprehensive analysis summary
