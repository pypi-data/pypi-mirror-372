import unittest
import pandas as pd
import pyterrier as pt
from unittest.mock import Mock, MagicMock
import json

from mp_procs.dproc import append_query_gen, process_keyphrases


class TestDocumentProcessors(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        # Initialize PyTerrier if not already started
        if not pt.java.started():
            pt.java.init()
            
        # Sample document data
        self.sample_docs = pd.DataFrame([
            {"docno": "doc1", "text": "This is a test document"},
            {"docno": "doc2", "text": "Another test document"},
            {"docno": "doc3", "text": "Third document for testing"}
        ])
    
    def test_append_query_gen_basic(self):
        """Test basic query generation appending functionality."""
        # Mock artifact that adds querygen column
        mock_artifact = Mock()
        mock_artifact.transform.return_value = self.sample_docs.copy().assign(
            querygen=["generated query 1", "generated query 2", "generated query 3"]
        )
        
        # Create processor
        processor = append_query_gen(artifact=mock_artifact, repeat=1)
        
        # Transform documents
        result = processor.transform(self.sample_docs)
        
        # Check results
        expected_texts = [
            "This is a test document generated query 1",
            "Another test document generated query 2", 
            "Third document for testing generated query 3"
        ]
        
        self.assertEqual(len(result), 3)
        self.assertListEqual(result["text"].tolist(), expected_texts)
        self.assertNotIn("querygen", result.columns)  # Should be dropped by default
    
    def test_append_query_gen_repeat(self):
        """Test query generation with repeat parameter."""
        mock_artifact = Mock()
        mock_artifact.transform.return_value = self.sample_docs.copy().assign(
            querygen=["query1", "query2", "query3"]
        )
        
        processor = append_query_gen(artifact=mock_artifact, repeat=3)
        result = processor.transform(self.sample_docs)
        
        # Should append the query 3 times
        expected_text = "This is a test document query1 query1 query1"
        self.assertEqual(result.iloc[0]["text"], expected_text)
    
    def test_append_query_gen_no_drop(self):
        """Test keeping querygen column when drop_querygen=False."""
        mock_artifact = Mock()
        mock_artifact.transform.return_value = self.sample_docs.copy().assign(
            querygen=["query1", "query2", "query3"]
        )
        
        processor = append_query_gen(artifact=mock_artifact, drop_querygen=False)
        result = processor.transform(self.sample_docs)
        
        self.assertIn("querygen", result.columns)
    
    def test_append_query_gen_missing_column(self):
        """Test handling when querygen column is missing."""
        mock_artifact = Mock()
        mock_artifact.transform.return_value = self.sample_docs.copy()  # No querygen column
        
        processor = append_query_gen(artifact=mock_artifact)
        result = processor.transform(self.sample_docs)
        
        # Should return original documents unchanged
        pd.testing.assert_frame_equal(result, self.sample_docs)
    
    def test_append_query_gen_null_values(self):
        """Test handling null values in querygen column."""
        mock_artifact = Mock()
        mock_artifact.transform.return_value = self.sample_docs.copy().assign(
            querygen=["query1", None, "query3"]
        )
        
        processor = append_query_gen(artifact=mock_artifact)
        result = processor.transform(self.sample_docs)
        
        # Null values should be replaced with empty string
        expected_texts = [
            "This is a test document query1",
            "Another test document ",  # Note the space from empty querygen
            "Third document for testing query3"
        ]
        self.assertListEqual(result["text"].tolist(), expected_texts)
    
    def test_process_keyphrases_basic(self):
        """Test basic keyphrase processing functionality."""
        mock_artifact = Mock()
        mock_artifact.transform.return_value = self.sample_docs.copy().assign(
            keyphrases=[
                '{"1": ["test", "document"]}',
                '{"1": ["another", "test"]}', 
                '{"1": ["third", "testing"]}'
            ]
        )
        
        processor = process_keyphrases(artifact=mock_artifact, repeat=1)
        result = processor.transform(self.sample_docs)
        
        expected_texts = [
            "This is a test document test document",
            "Another test document another test",
            "Third document for testing third testing"
        ]
        
        self.assertEqual(len(result), 3)
        self.assertListEqual(result["text"].tolist(), expected_texts)
        self.assertNotIn("keyphrases", result.columns)
    
    def test_process_keyphrases_repeat(self):
        """Test keyphrase processing with repeat parameter."""
        mock_artifact = Mock()
        mock_artifact.transform.return_value = self.sample_docs.copy().assign(
            keyphrases=['{"1": ["keyword"]}', '{"1": ["term"]}', '{"1": ["phrase"]}']
        )
        
        processor = process_keyphrases(artifact=mock_artifact, repeat=2)
        result = processor.transform(self.sample_docs)
        
        expected_text = "This is a test document keyword keyword"
        self.assertEqual(result.iloc[0]["text"], expected_text)
    
    def test_process_keyphrases_dict_input(self):
        """Test keyphrase processing with dict input instead of JSON string."""
        mock_artifact = Mock()
        mock_artifact.transform.return_value = self.sample_docs.copy().assign(
            keyphrases=[
                {"1": ["test", "document"]},
                {"1": ["another", "test"]}, 
                {"1": ["third", "testing"]}
            ]
        )
        
        processor = process_keyphrases(artifact=mock_artifact)
        result = processor.transform(self.sample_docs)
        
        expected_text = "This is a test document test document"
        self.assertEqual(result.iloc[0]["text"], expected_text)
    
    def test_process_keyphrases_missing_field_1(self):
        """Test handling when keyphrases don't have '1' field."""
        mock_artifact = Mock()
        mock_artifact.transform.return_value = self.sample_docs.copy().assign(
            keyphrases=[
                '{"2": ["test", "document"]}',  # No "1" field
                '{"1": ["another", "test"]}', 
                '{}'  # Empty dict
            ]
        )
        
        processor = process_keyphrases(artifact=mock_artifact)
        result = processor.transform(self.sample_docs)
        
        expected_texts = [
            "This is a test document",  # No keyphrases added
            "Another test document another test",
            "Third document for testing"  # No keyphrases added
        ]
        self.assertListEqual(result["text"].tolist(), expected_texts)
    
    def test_process_keyphrases_invalid_json(self):
        """Test handling invalid JSON in keyphrases."""
        mock_artifact = Mock()
        mock_artifact.transform.return_value = self.sample_docs.copy().assign(
            keyphrases=[
                "invalid json",
                '{"1": ["valid", "keyphrases"]}',
                None
            ]
        )
        
        processor = process_keyphrases(artifact=mock_artifact)
        result = processor.transform(self.sample_docs)
        
        expected_texts = [
            "This is a test document",  # Invalid JSON, no keyphrases added
            "Another test document valid keyphrases",
            "Third document for testing"  # None value, no keyphrases added
        ]
        self.assertListEqual(result["text"].tolist(), expected_texts)
    
    def test_process_keyphrases_key_error_handling(self):
        """Test graceful handling of KeyError from artifact.transform."""
        mock_artifact = Mock()
        
        # First call raises KeyError, individual calls work for some docs
        def side_effect(docs_df):
            if len(docs_df) > 1:
                raise KeyError("Document not found")
            else:
                # Return single document with keyphrases for doc1, without for others
                doc = docs_df.iloc[0]
                if doc["docno"] == "doc1":
                    return docs_df.assign(keyphrases=['{"1": ["single", "doc"]}'])
                else:
                    return docs_df  # No keyphrases column
        
        mock_artifact.transform.side_effect = side_effect
        
        processor = process_keyphrases(artifact=mock_artifact)
        result = processor.transform(self.sample_docs)
        
        # Should handle missing documents gracefully
        self.assertEqual(len(result), 3)
        self.assertEqual(result.iloc[0]["text"], "This is a test document single doc")
        self.assertEqual(result.iloc[1]["text"], "Another test document")  # Unchanged
        self.assertEqual(result.iloc[2]["text"], "Third document for testing")  # Unchanged
    
    def test_process_keyphrases_no_drop(self):
        """Test keeping keyphrases column when drop_keyphrases=False."""
        mock_artifact = Mock()
        mock_artifact.transform.return_value = self.sample_docs.copy().assign(
            keyphrases=['{"1": ["test"]}', '{"1": ["another"]}', '{"1": ["third"]}']
        )
        
        processor = process_keyphrases(artifact=mock_artifact, drop_keyphrases=False)
        result = processor.transform(self.sample_docs)
        
        self.assertIn("keyphrases", result.columns)


if __name__ == '__main__':
    unittest.main()