"""
Generate OpenAPI specification for the Jira Dashboard Backend API.
This script creates the openapi.json file with complete API documentation.
"""
import json
import os
import sys

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.api.main import app

def generate_openapi():
    """
    Generate OpenAPI specification file.
    Creates a comprehensive API documentation file.
    """
    print("Generating OpenAPI specification...")
    
    # Get the OpenAPI schema
    openapi_schema = app.openapi()
    
    # Ensure output directory exists
    output_dir = "interfaces"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "openapi.json")
    
    # Write to file with proper formatting
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2, ensure_ascii=False)
    
    print(f"OpenAPI specification generated at: {output_path}")
    print(f"Total endpoints: {len(openapi_schema.get('paths', {}))}")
    
    # Print summary of endpoints
    paths = openapi_schema.get('paths', {})
    for path, methods in paths.items():
        for method, details in methods.items():
            if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                summary = details.get('summary', 'No summary')
                print(f"  {method.upper()} {path} - {summary}")

if __name__ == "__main__":
    generate_openapi()
