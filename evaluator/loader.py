import os
import json
import yaml
import logging
from typing import List
from app.schemas.test_case import TestCase
from pydantic import ValidationError

logger = logging.getLogger(__name__)

class TestLoader:
    def __init__(self, base_path: str = "datasets"):
        self.base_path = base_path

    def load_test_suite(self, tags: List[str] = None) -> List[TestCase]:
        """
        Loads test cases from the datasets directory.
        
        Args:
            tags: Optional list of tags to filter by. If a test matches ANY tag, it is included.
                  If tags is None or empty, all tests are returned.
        """
        test_cases = []
        
        # Walk through the directory
        for root, _, files in os.walk(self.base_path):
            for file in files:
                file_path = os.path.join(root, file)
                
                try:
                    loaded_tests = self._load_file(file_path)
                    for test_data in loaded_tests:
                        try:
                            # Validate schema
                            test_case = TestCase(**test_data)
                            
                            # Filter by tags if requested
                            if tags:
                                if not any(tag in test_case.tags for tag in tags):
                                    continue
                                    
                            test_cases.append(test_case)
                        except ValidationError as e:
                            logger.error(f"Validation error in file {file_path}, test id {test_data.get('id', 'unknown')}: {e}")
                except Exception as e:
                    logger.warning(f"Could not load file {file_path}: {e}")
                    
        return test_cases
    
    def load_specific_file(self, file_path: str) -> List[TestCase]:
        """Load a specific test file."""
        test_cases = []
        try:
            loaded_tests = self._load_file(file_path)
            for test_data in loaded_tests:
                try:
                    test_cases.append(TestCase(**test_data))
                except ValidationError as e:
                    logger.error(f"Validation error in {file_path}: {e}")
        except Exception as e:
            logger.error(f"Failed to load file {file_path}: {e}")
            raise
            
        return test_cases

    def _load_file(self, file_path: str) -> List[dict]:
        """Reads a file and returns a list of raw test case dictionaries."""
        if file_path.endswith('.json'):
            with open(file_path, 'r') as f:
                data = json.load(f)
                # Support single object or list of objects
                if isinstance(data, dict):
                    return [data]
                elif isinstance(data, list):
                    return data
        elif file_path.endswith('.yaml') or file_path.endswith('.yml'):
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
                if isinstance(data, dict):
                    return [data]
                elif isinstance(data, list):
                    return data
        
        return []
