import argparse
import subprocess
import sys
import os
import shutil
from pathlib import Path

# --- Configuration ---
PACKAGE_NAME = "perceptic_core_client"
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
OUTPUT_DIR = PROJECT_ROOT / "src"
VERSION_FILE = PROJECT_ROOT / "VERSION"
# ---

def check_java():
    """Checks if Java is installed and accessible."""
    try:
        subprocess.run(["java", "-version"], check=True, capture_output=True)
        print("Java installation found.")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: Java Runtime Environment (JRE) not found.", file=sys.stderr)
        print("openapi-generator-cli requires Java to run.", file=sys.stderr)
        print("Please install Java and ensure it's in your PATH.", file=sys.stderr)
        return False

def check_openapi_generator():
    """Checks if openapi-generator-cli is installed and accessible."""
    try:
        subprocess.run(["openapi-generator-cli", "list"], check=True, capture_output=True)
        print("openapi-generator-cli found.")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: openapi-generator-cli not found.", file=sys.stderr)
        print("Please install it, e.g., using 'npm install @openapitools/openapi-generator-cli -g' or ensure it's in your PATH.", file=sys.stderr)
        return False

def run_generator(spec_path: Path, output_dir: Path, package_name: str):
    """Runs the openapi-generator-cli command."""
    if not spec_path.is_file():
        print(f"Error: OpenAPI spec file not found at: {spec_path}", file=sys.stderr)
        return False

    # Ensure output directory exists and is empty
    if output_dir.exists():
         print(f"Cleaning existing output directory: {output_dir}")
         if str(output_dir).startswith(str(PROJECT_ROOT / "src")): # Basic safety check
             shutil.rmtree(output_dir)
         else:
             print(f"Error: Output directory {output_dir} seems unsafe to remove.", file=sys.stderr)
             return False
    output_dir.mkdir(parents=True)

    additional_props = f"projectName={package_name},useOneOfDiscriminatorLookup=true,generateSourceCodeOnly=true,packageName={package_name}"

    command = [
        "openapi-generator-cli", "generate",
        "-g", "python",
        "-i", str(spec_path),
        "-o", str(output_dir),
        # "--package-name", package_name, # Handled by additional props
        "--skip-validate-spec",
        "--additional-properties", additional_props
    ]

    print(f"Running generator command: {' '.join(command)}")
    try:
        process = subprocess.run(command, check=True, capture_output=True, text=True)
        print("Generator output:")
        print(process.stdout)
        if process.stderr:
             print("Generator errors/warnings:", file=sys.stderr)
             print(process.stderr, file=sys.stderr)
        print("Client generation successful.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running openapi-generator-cli: {e}", file=sys.stderr)
        print("Command output:", file=sys.stderr)
        print(e.stdout, file=sys.stderr)
        print(e.stderr, file=sys.stderr)
        return False
    except FileNotFoundError:
         print("Error: 'openapi-generator-cli' command not found. Is it installed and in PATH?", file=sys.stderr)
         return False
    except Exception as e: # Catch other potential errors like JSON parsing
         print(f"An unexpected error occurred during generation: {e}", file=sys.stderr)
         return False

def write_version_file(version: str, version_file_path: Path):
    """Writes the version to the VERSION file."""
    print(f"Writing version '{version}' to {version_file_path}")
    try:
        version_file_path.write_text(version.strip() + "\n", encoding='utf-8')
        return True
    except IOError as e:
        print(f"Error writing VERSION file: {e}", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description="Generate Python client from a local Perceptic Core OpenAPI spec file.")
    parser.add_argument(
        "--spec-path",
        type=Path,
        required=True,
        help="Path to the local OpenAPI specification file"
    )
    parser.add_argument(
        "--version",
        type=str,
        required=True,
        help="The version string to assign to the package (e.g., 0.5.0)"
    )
    args = parser.parse_args()
    spec_path = args.spec_path.resolve() # Get absolute path
    version = args.version

    print(f"--- Starting client generation from spec: {spec_path} for version: {version} ---")

    # --- Pre-checks ---
    if not check_java() or not check_openapi_generator():
        sys.exit(1)

    # --- Generate Client ---
    if not run_generator(spec_path, OUTPUT_DIR, PACKAGE_NAME):
         print("Client generation failed.", file=sys.stderr)
         sys.exit(1)

    # --- Write Version ---
    if not write_version_file(version, VERSION_FILE):
         sys.exit(1)

    print(f"--- Client generation completed successfully for version: {version} ---")
    print(f"Generated client code is in: {OUTPUT_DIR}")
    print(f"Version file created at: {VERSION_FILE}")

if __name__ == "__main__":
    main()
