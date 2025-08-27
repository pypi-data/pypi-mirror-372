import unittest
import pandas as pd
import pyterrier as pt
from unittest.mock import Mock, patch
import re

from mp_procs.qproc import (
    weighted_segmentation_boost,
    append_segmentation_with_or,
    synonym_segmentation,
    single_rare_term_emphasis_weighted,
    intent_trigger_weighted,
    sanitize_column_transform,
    _DEFAULT_STOPWORDS
)


class TestQueryProcessors(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        # Initialize PyTerrier if not already started
        if not pt.java.started():
            pt.java.init()
            
        # Sample query data
        self.sample_queries = pd.DataFrame([
            {"qid": "q1", "query": "hubble telescope"},
            {"qid": "q2", "query": "space exploration"},
            {"qid": "q3", "query": "artificial intelligence"}
        ])
        
        # Sample queries with segmentation data
        self.queries_with_segmentation = pd.DataFrame([
            {
                "qid": "q1", 
                "query": "hubble telescope",
                "segmentation": "hubble telescope || space observatory"
            },
            {
                "qid": "q2", 
                "query": "machine learning",
                "segmentation": "machine learning || artificial intelligence || deep learning"
            },
            {
                "qid": "q3",
                "query": "single term",
                "segmentation": "term"
            }
        ])

    def test_weighted_segmentation_boost_basic(self):
        """Test basic weighted segmentation boost functionality."""
        processor = weighted_segmentation_boost(boost_weight=1.5)
        result = processor.transform(self.queries_with_segmentation)
        
        # Check that multi-word segments get boosted
        self.assertIn("hubble^1.5 telescope^1.5", result.iloc[0]["query"])
        self.assertIn("space^1.5 observatory^1.5", result.iloc[0]["query"])
        
        # Check single-word segments are added without boost
        self.assertIn("term", result.iloc[2]["query"])
        self.assertNotIn("term^", result.iloc[2]["query"])

    def test_weighted_segmentation_boost_missing_column(self):
        """Test handling when segmentation column is missing."""
        processor = weighted_segmentation_boost()
        result = processor.transform(self.sample_queries)
        
        # Should return original queries unchanged
        pd.testing.assert_frame_equal(result, self.sample_queries)

    def test_weighted_segmentation_boost_empty_segmentation(self):
        """Test handling of empty segmentations."""
        queries_empty_seg = pd.DataFrame([
            {"qid": "q1", "query": "test query", "segmentation": ""},
            {"qid": "q2", "query": "another query", "segmentation": None}
        ])
        
        processor = weighted_segmentation_boost()
        result = processor.transform(queries_empty_seg)
        
        # Queries should remain unchanged
        self.assertEqual(result.iloc[0]["query"], "test query")
        self.assertEqual(result.iloc[1]["query"], "another query")

    def test_weighted_segmentation_boost_list_input(self):
        """Test segmentation input as list."""
        queries_list_seg = pd.DataFrame([
            {
                "qid": "q1", 
                "query": "test query",
                "segmentation": [["hubble", "telescope"], ["space"]]
            }
        ])
        
        processor = weighted_segmentation_boost(boost_weight=2.0)
        result = processor.transform(queries_list_seg)
        
        self.assertIn("hubble^2.0 telescope^2.0", result.iloc[0]["query"])
        self.assertIn("space", result.iloc[0]["query"])

    def test_weighted_segmentation_boost_stopwords(self):
        """Test stopword filtering."""
        queries_with_stopwords = pd.DataFrame([
            {
                "qid": "q1", 
                "query": "test query",
                "segmentation": "the hubble telescope || and space"
            }
        ])
        
        processor = weighted_segmentation_boost()
        result = processor.transform(queries_with_stopwords)
        
        # Should exclude stopwords from boosting
        self.assertNotIn("the^", result.iloc[0]["query"])
        self.assertNotIn("and^", result.iloc[0]["query"])
        self.assertIn("hubble^", result.iloc[0]["query"])

    def test_append_segmentation_with_or_basic(self):
        """Test basic OR segmentation functionality."""
        processor = append_segmentation_with_or()
        result = processor.transform(self.queries_with_segmentation)
        
        # Check #syn structure
        self.assertTrue(result.iloc[0]["query"].startswith("#syn("))
        self.assertIn("#band(hubble telescope)", result.iloc[0]["query"])
        self.assertIn("#band(space observatory)", result.iloc[0]["query"])

    def test_append_segmentation_with_or_single_terms(self):
        """Test handling of single-term segments."""
        queries_single_terms = pd.DataFrame([
            {
                "qid": "q1", 
                "query": "test",
                "segmentation": "word1 || word2"
            }
        ])
        
        processor = append_segmentation_with_or()
        result = processor.transform(queries_single_terms)
        
        # Single terms should not use #band
        self.assertIn("word1", result.iloc[0]["query"])
        self.assertIn("word2", result.iloc[0]["query"])
        self.assertNotIn("#band(word1)", result.iloc[0]["query"])

    def test_synonym_segmentation_basic(self):
        """Test basic synonym segmentation functionality."""
        processor = synonym_segmentation()
        result = processor.transform(self.queries_with_segmentation)
        
        # Check curly brace synonym groups
        self.assertIn("{hubble telescope}", result.iloc[0]["query"])
        self.assertIn("{space observatory}", result.iloc[0]["query"])

    def test_synonym_segmentation_filtering(self):
        """Test that single-word segments are filtered out."""
        queries_mixed_segments = pd.DataFrame([
            {
                "qid": "q1", 
                "query": "test",
                "segmentation": "single || multi word || another"
            }
        ])
        
        processor = synonym_segmentation()
        result = processor.transform(queries_mixed_segments)
        
        # Only multi-word segments should become synonym groups
        self.assertIn("{multi word}", result.iloc[0]["query"])
        self.assertNotIn("{single}", result.iloc[0]["query"])
        self.assertNotIn("{another}", result.iloc[0]["query"])

    def test_single_rare_term_emphasis_weighted_basic(self):
        """Test basic rare term emphasis functionality."""
        queries_with_idf = pd.DataFrame([
            {
                "qid": "q1", 
                "query": "common rare specific",
                "avg-idf": 4.0,
                "max-idf": 8.0
            }
        ])
        
        processor = single_rare_term_emphasis_weighted(
            avg_idf_low=5.0,
            max_minus_avg_gap=2.0,
            emphasis_weight=2.0
        )
        result = processor.transform(queries_with_idf)
        
        # Should boost the longest term (assuming it's the rare one)
        query = result.iloc[0]["query"]
        self.assertIn("specific^2.0", query)

    def test_single_rare_term_emphasis_no_boost_conditions(self):
        """Test that emphasis is not applied when conditions aren't met."""
        queries_high_avg_idf = pd.DataFrame([
            {
                "qid": "q1", 
                "query": "common terms",
                "avg-idf": 6.0,  # Too high
                "max-idf": 8.0
            }
        ])
        
        processor = single_rare_term_emphasis_weighted()
        result = processor.transform(queries_high_avg_idf)
        
        # Should remain unchanged
        self.assertEqual(result.iloc[0]["query"], "common terms")

    def test_single_rare_term_emphasis_missing_columns(self):
        """Test handling when IDF columns are missing."""
        processor = single_rare_term_emphasis_weighted()
        result = processor.transform(self.sample_queries)
        
        # Should return unchanged
        pd.testing.assert_frame_equal(result, self.sample_queries)

    def test_intent_trigger_weighted_instrumental(self):
        """Test instrumental intent trigger."""
        queries_with_intent = pd.DataFrame([
            {
                "qid": "q1", 
                "query": "fix computer",
                "intent_prediction": "instrumental"
            }
        ])
        
        processor = intent_trigger_weighted(trigger_weight=2.0)
        result = processor.transform(queries_with_intent)
        
        self.assertIn("how^2.0 to^2.0", result.iloc[0]["query"])

    def test_intent_trigger_weighted_factual(self):
        """Test factual intent trigger."""
        queries_with_intent = pd.DataFrame([
            {
                "qid": "q1", 
                "query": "what is AI",
                "intent_prediction": "factual"
            }
        ])
        
        processor = intent_trigger_weighted(trigger_weight=1.5)
        result = processor.transform(queries_with_intent)
        
        self.assertIn("definition^1.5 of^1.5", result.iloc[0]["query"])

    def test_intent_trigger_weighted_transactional(self):
        """Test transactional intent trigger."""
        queries_with_intent = pd.DataFrame([
            {
                "qid": "q1", 
                "query": "laptop computer",
                "intent_prediction": "transactional"
            }
        ])
        
        processor = intent_trigger_weighted()
        result = processor.transform(queries_with_intent)
        
        self.assertIn("buy^1.5", result.iloc[0]["query"])

    def test_intent_trigger_weighted_navigational(self):
        """Test navigational intent trigger."""
        queries_with_intent = pd.DataFrame([
            {
                "qid": "q1", 
                "query": "google website",
                "intent_prediction": "navigational"
            }
        ])
        
        processor = intent_trigger_weighted()
        result = processor.transform(queries_with_intent)
        
        self.assertIn("official^1.5", result.iloc[0]["query"])

    def test_intent_trigger_weighted_abstain(self):
        """Test abstain intent (no modification)."""
        queries_with_intent = pd.DataFrame([
            {
                "qid": "q1", 
                "query": "unclear query",
                "intent_prediction": "abstain"
            }
        ])
        
        processor = intent_trigger_weighted()
        result = processor.transform(queries_with_intent)
        
        # Should remain unchanged
        self.assertEqual(result.iloc[0]["query"], "unclear query")

    def test_intent_trigger_weighted_missing_column(self):
        """Test handling when intent column is missing."""
        processor = intent_trigger_weighted()
        result = processor.transform(self.sample_queries)
        
        # Should return unchanged
        pd.testing.assert_frame_equal(result, self.sample_queries)

    def test_intent_trigger_weighted_unknown_intent(self):
        """Test handling of unknown intent values."""
        queries_unknown_intent = pd.DataFrame([
            {
                "qid": "q1", 
                "query": "test query",
                "intent_prediction": "unknown_intent"
            }
        ])
        
        processor = intent_trigger_weighted()
        result = processor.transform(queries_unknown_intent)
        
        # Should remain unchanged
        self.assertEqual(result.iloc[0]["query"], "test query")

    def test_sanitize_column_transform_basic(self):
        """Test basic sanitization functionality."""
        queries_with_special_chars = pd.DataFrame([
            {"qid": "q1", "query": "what's the 'best' approach?"},
            {"qid": "q2", "query": "search (term) here"},
            {"qid": "q3", "query": "url/path:example"}
        ])
        
        processor = sanitize_column_transform()
        result = processor.transform(queries_with_special_chars)
        
        self.assertEqual(result.iloc[0]["query"], "whats the best approach?")
        self.assertEqual(result.iloc[1]["query"], "search term here")
        self.assertEqual(result.iloc[2]["query"], "urlpathexample")

    def test_sanitize_column_transform_different_columns(self):
        """Test sanitization with different source and target columns."""
        queries_with_correction = pd.DataFrame([
            {"qid": "q1", "query": "original", "corrected": "what's corrected?"}
        ])
        
        processor = sanitize_column_transform(
            source_col="corrected",
            target_col="query"
        )
        result = processor.transform(queries_with_correction)
        
        self.assertEqual(result.iloc[0]["query"], "whats corrected?")
        self.assertIn("corrected", result.columns)

    def test_sanitize_column_transform_missing_column(self):
        """Test handling when source column is missing."""
        processor = sanitize_column_transform(source_col="missing_col")
        result = processor.transform(self.sample_queries)
        
        # Should return unchanged
        pd.testing.assert_frame_equal(result, self.sample_queries)

    def test_edge_case_empty_query(self):
        """Test handling of empty queries."""
        empty_queries = pd.DataFrame([
            {"qid": "q1", "query": "", "segmentation": "some || segments"}
        ])
        
        processor = weighted_segmentation_boost()
        result = processor.transform(empty_queries)
        
        # Should still process segmentations even with empty base query
        self.assertIn("some", result.iloc[0]["query"])


    def test_pipeline_compatibility(self):
        """Test that processors can be chained together."""
        queries_full_data = pd.DataFrame([
            {
                "qid": "q1",
                "query": "what's AI?",
                "segmentation": "artificial intelligence || machine learning",
                "intent_prediction": "factual"
            }
        ])
        
        # Chain multiple processors
        sanitizer = sanitize_column_transform()
        segmenter = weighted_segmentation_boost(boost_weight=1.2)
        intent_proc = intent_trigger_weighted(trigger_weight=1.3)
        
        # Apply in sequence
        result = sanitizer.transform(queries_full_data)
        result = segmenter.transform(result)
        result = intent_proc.transform(result)
        
        final_query = result.iloc[0]["query"]
        
        # Should contain elements from all processors
        self.assertNotIn("'", final_query)  # Sanitized
        self.assertIn("artificial^1.2", final_query)  # Segmentation boost
        self.assertIn("definition^1.3", final_query)  # Intent trigger


if __name__ == '__main__':
    unittest.main()