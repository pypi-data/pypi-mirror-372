# MP-Procs: Modular Pipeline Query and Document Processors

A PyTerrier-compatible package providing modular query and document processing components for information retrieval pipelines.

## Overview

MP-Procs offers a collection of transformers that can be seamlessly integrated into PyTerrier pipelines to enhance query processing and document indexing. The package is designed for experimental IR research, allowing researchers to easily combine and evaluate different processing strategies.

## Features

### Query Processors (`mp_procs.qproc`)

- **Segmentation-based Query Enhancement**
  - `weighted_segmentation_boost`: Boost terms in multi-word segments
  - `append_segmentation_with_or`: Append segments using logical OR with #syn/#band operators
  - `synonym_segmentation`: Treat segments as synonym groups with curly braces

- **Query Intelligence**
  - `intent_trigger_weighted`: Add intent-specific trigger phrases based on predicted query intent
  - `single_rare_term_emphasis_weighted`: Emphasize rare terms based on IDF statistics

- **Text Preprocessing**
  - `sanitize_column_transform`: Remove special characters and clean query text

### Document Processors (`mp_procs.dproc`)

- **Query Generation**
  - `append_query_gen`: Generate additional queries using DocT5Query
  
- **Content Enhancement**
  - `process_keyphrases`: Extract and append keyphrases to document content

## Installation

```bash
# Install from local source
cd /path/to/thesis_code/mp_procs
pip install -e .
```

### Requirements

- `python-terrier >= 0.10.0`
- `pyterrier-alpha`
- `pandas`


## Pipeline Integration

### Complete IR Pipeline Example

```python
import pyterrier as pt
import pyterrier-alpha as pta
from mp_procs.qproc import weighted_segmentation_boost, sanitize_column_transform
from mp_procs.dproc import process_keyphrases

# Load dataset
dataset = pt.get_dataset("irds:trec-robust04")
topics, qrels = dataset.get_topics("title"), dataset.get_qrels()

# Query processing
query_artifact = pta.Artifact.from_url("tira:disks45/nocr/trec-robust-2004/ows/query-segmentation-hyb-a")
query_enhancer = weighted_segmentation_boost(boost_weight=1.2)
query_pipeline = query_artifact >> query_enhancer
topics = query_pipeline(topics)

# Document processing and indexing
keyphrase_proc = process_keyphrases(artifact=keyphrase_artifact, repeat=2)
indexer = pt.IterDictIndexer("./enhanced_index", overwrite=True, meta={"docno": 20})
index_ref = (keyphrase_proc >> indexer).index(dataset.get_corpus_iter())

# Retrieval
retriever = pt.terrier.Retriever(index_ref, wmodel="BM25")

# Complete pipeline
pipeline = query_pipeline >> retriever

# Evaluate
results = pipeline.transform(topics)
evaluation = pt.Evaluate(results, qrels, metrics=["map", "ndcg_cut_10"])
print(evaluation)
```

## Configuration Options

### Query Processors

| Function | Key Parameters | Description |
|----------|----------------|-------------|
| `weighted_segmentation_boost` | `boost_weight=1.2`, `seg_col="segmentation"` | Boost factor for segment terms |
| `append_segmentation_with_or` | `seg_col="segmentation"` | Use #syn/#band operators |
| `synonym_segmentation` | `seg_col="segmentation"` | Create {synonym groups} |
| `intent_trigger_weighted` | `trigger_weight=1.5`, `intent_col="intent_prediction"` | Weight for trigger phrases |
| `single_rare_term_emphasis_weighted` | `emphasis_weight=1.5`, `avg_idf_low=5.0` | Rare term boosting thresholds |
| `sanitize_column_transform` | `source_col="query"`, `target_col="query"` | Column mapping for cleaning |

### Document Processors

| Function | Key Parameters | Description |
|----------|----------------|-------------|
| `append_query_gen` | `repeat=1` | Number of generated queries to append |
| `process_keyphrases` | `repeat=1` | Number of keyphrase extractions |

## Entry Points

The package registers entry points for automatic discovery:

```toml
[project.entry-points."modpipe.qproc"]
SegmentationWeighted = "mp_procs.qproc:weighted_segmentation_boost"
SegmentationAppendOr = "mp_procs.qproc:append_segmentation_with_or"
SegmentationSynonyms = "mp_procs.qproc:synonym_segmentation"
PredictorBoost = "mp_procs.qproc:single_rare_term_emphasis_weighted"
IntentTriggerAppend = "mp_procs.qproc:intent_trigger_weighted"
SpellingModification = "mp_procs.qproc:sanitize_column_transform"

[project.entry-points."modpipe.dproc"]
DocT5Query = "mp_procs.dproc:append_query_gen"
KeyphraseExtraction = "mp_procs.dproc:process_keyphrases"
```

## Testing

Run the test suite:

```bash
cd mp_procs
python -m pytest tests/ -v
```

Or run specific tests:

```bash
python -m unittest tests.test_queryprocessor.TestQueryProcessors.test_weighted_segmentation_boost_basic
```

## Error Handling

All processors gracefully handle missing columns and invalid data:

- Missing required columns → return DataFrame unchanged
- Empty/null values → skip processing for those rows  
- Invalid data types → attempt conversion or skip gracefully
- Chain compatibility → all processors accept and return pandas DataFrames

## Contributing

This package is part of a research thesis on modular IR pipelines. For issues or contributions:

1. Follow PyTerrier transformer conventions
2. Add comprehensive tests for new processors
3. Update entry points in `pyproject.toml`
4. Maintain backward compatibility

## License

This project is part of academic research. Please cite appropriately if used in publications.

## Citation

If you use this package in your research, please cite:

```bibtex
@misc{mp_procs2025,
  title={MP-Procs: Modular Pipeline Processors for Information Retrieval},
  author={[Patrick Stahl]},
  year={2025},
  note={Thesis code for modular IR pipeline research}
}
```