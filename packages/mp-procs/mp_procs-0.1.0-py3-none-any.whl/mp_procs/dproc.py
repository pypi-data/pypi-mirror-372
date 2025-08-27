import json
import pandas as pd, pyterrier as pt
import pyterrier_alpha as pta

def append_query_gen(
    *,
    artifact,
    repeat: int = 1,
    querygen_col: str = "querygen",
    text_col: str = "text",
    drop_querygen: bool = True,
) -> pt.Transformer:
    """
    Append generated queries to document text.
    
    This function takes a DocT5Query artifact object and appends the generated queries
    to the document text multiple times based on the repeat parameter.
    """
    def _transform(docs_df: pd.DataFrame) -> pd.DataFrame:
        docs_df = artifact.transform(docs_df)

        if querygen_col in docs_df.columns:
            docs_df = docs_df.copy()
            docs_df[querygen_col] = docs_df[querygen_col].fillna("")
            
            # Repeat the querygen text the specified number of times
            repeated_querygen = docs_df[querygen_col]
            for _ in range(repeat):
                docs_df[text_col] = docs_df[text_col] + " " + repeated_querygen
            
            if drop_querygen:
                docs_df.drop(columns=[querygen_col], inplace=True)
        
        return docs_df

    return pt.apply.generic(_transform)


def process_keyphrases(
    *,
    artifact,
    repeat: int = 1,
    keyphrase_col: str = "keyphrases",
    text_col: str = "text",
    drop_keyphrases: bool = True,
) -> pt.Transformer:
    """
    Extract keyphrases from an artifact and append them to document text.
    Handles missing documents gracefully and extracts keyphrases from the "1" field.
    
    Args:
        artifact: The keyphrase extraction artifact object
        repeat: Number of times to append the keyphrases to the text
        
    Returns:
        A PyTerrier transformer that extracts and appends keyphrases to text
    """
    def _transform(docs_df: pd.DataFrame) -> pd.DataFrame:
        try:
            docs_with_keyphrases = artifact.transform(docs_df)
        except KeyError as e:
            #print(f"Warning: Some documents missing from keyphrase data, handling gracefully...")
            result_docs = []
            for idx, doc in docs_df.iterrows():
                try:
                    # Try to get keyphrases for this single document
                    single_doc_df = pd.DataFrame([doc])
                    transformed = artifact.transform(single_doc_df)
                    result_docs.append(transformed.iloc[0].to_dict())
                except KeyError:
                    # If this document has no keyphrases, add it without keyphrases
                    doc_dict = doc.to_dict()
                    result_docs.append(doc_dict)
            
            docs_with_keyphrases = pd.DataFrame(result_docs)
        
        # Now append keyphrases if present
        if keyphrase_col in docs_with_keyphrases.columns:
            docs_with_keyphrases = docs_with_keyphrases.copy()
            
            # Extract keyphrases from "1" field and append to text
            def extract_keyphrases_1(keyphrases_data):
                if pd.isna(keyphrases_data) or not keyphrases_data:
                    return ""
                
                try:
                    if isinstance(keyphrases_data, str):
                        keyphrases_dict = json.loads(keyphrases_data)
                    else:
                        keyphrases_dict = keyphrases_data
                    
                    keyphrases_1 = keyphrases_dict.get("1", [])
                    if keyphrases_1:
                        return " " + " ".join(keyphrases_1)
                    else:
                        return ""
                except (json.JSONDecodeError, TypeError, AttributeError):
                    return ""
            
            # Apply the extraction and append to text
            keyphrases_text = docs_with_keyphrases[keyphrase_col].apply(extract_keyphrases_1)
            
            for _ in range(repeat):
                docs_with_keyphrases[text_col] = docs_with_keyphrases[text_col].astype(str) + keyphrases_text
            
            if drop_keyphrases:
                docs_with_keyphrases.drop(columns=[keyphrase_col], inplace=True)
        
        return docs_with_keyphrases

    return pt.apply.generic(_transform)