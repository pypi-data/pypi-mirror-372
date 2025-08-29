"""Data import functions for Bioprocess Intelligence client."""
from typing import Dict, List, Optional, Any
import os
from .fragments import (
    CORE_PROCESS_FIELDS,
    CORE_COLLECTION_FIELDS,
    CORE_PARAMETER_FIELDS,
    CORE_METADATA_FIELDS,
    CORE_VARIABLE_FIELDS,
    CORE_VARIABLE_FIELDS_WITH_DATA
)

def import_process_from_excel(self, collection_id: str, file_path: str, name: Optional[str] = None) -> Dict[str, Any]:
    """Import a process from an Excel file into a collection.
    
    Args:
        collection_id: ID of the collection to import into (maps to topic_id in backend)
        file_path: Path to Excel file
        name: Optional name for the process. If not provided, will be extracted from the file
        
    Returns:
        Dict containing process details including id, name, and collection (topic) info
        
    Raises:
        FileNotFoundError: If the Excel file does not exist
        PermissionError: If the Excel file cannot be read
        ValueError: If the file is empty, too large, or has invalid extension
        Exception: For import failures including network and server errors
    """
    mutation = f"""
        {CORE_PROCESS_FIELDS}
        mutation ImportProcess($input: ImportProcessInputType!) {{
            importProcess(input: $input) {{
                process {{
                    ...CoreProcessFields
                    topic {{
                        id
                        name
                    }}
                }}
            }}
        }}
    """
    
    # Upload file and get its ID
    file_id = self._upload_file(file_path)
    
    variables = {
        'input': {
            'topicId': collection_id,  # Using topicId for backend compatibility
            'fileId': file_id,
            'name': name or os.path.splitext(os.path.basename(file_path))[0]
        }
    }
    
    try:
        response = self._execute_query(mutation, variables)
        process = response['data']['importProcess']['process']
        
        # Return process details with collection info
        return process
        
    except Exception as e:
        if 'Permission denied' in str(e):
            raise PermissionError(f"Permission denied importing process into collection {collection_id}")
        else:
            raise Exception(f"Error importing Excel file: {str(e)}") from e

def import_variables(self, process_id: str, file_path: str, variable_mapping: Dict[str, str]) -> List[Dict[str, Any]]:
    """Import variables from a data file into a process.
    
    Args:
        process_id: ID of the process to import variables into
        file_path: Path to data file (Excel or CSV)
        variable_mapping: Mapping of file columns to variable names
        
    Returns:
        List of created variables
    """
    mutation = f"""
        {CORE_VARIABLE_FIELDS_WITH_DATA}
        mutation ImportVariables($input: ImportVariablesInputType!) {{
            importVariables(input: $input) {{
                variables {{
                    ...CoreVariableFieldsWithData
                }}
            }}
        }}
    """
    
    # Upload file and get its ID
    file_id = self._upload_file(file_path)
    
    variables = {
        'input': {
            'processId': process_id,
            'fileId': file_id,
            'mapping': variable_mapping
        }
    }
    
    response = self._execute_query(mutation, variables)
    return response['data']['importVariables']['variables']

def import_metadata(self, process_id: str, file_path: str, metadata_mapping: Dict[str, str]) -> List[Dict[str, Any]]:
    """Import metadata from a file into a process.
    
    Args:
        process_id: ID of the process to import metadata into
        file_path: Path to data file (Excel or CSV)
        metadata_mapping: Mapping of file columns to metadata names
        
    Returns:
        List of created metadata
    """
    mutation = f"""
        {CORE_METADATA_FIELDS}
        mutation ImportMetadata($input: ImportMetadataInputType!) {{
            importMetadata(input: $input) {{
                metadata {{
                    ...CoreMetadataFields
                }}
            }}
        }}
    """
    
    # Upload file and get its ID
    file_id = self._upload_file(file_path)
    
    variables = {
        'input': {
            'processId': process_id,
            'fileId': file_id,
            'mapping': metadata_mapping
        }
    }
    
    response = self._execute_query(mutation, variables)
    return response['data']['importMetadata']['metadata']
