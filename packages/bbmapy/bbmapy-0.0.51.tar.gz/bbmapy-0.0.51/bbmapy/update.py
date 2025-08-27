import os
import re
import shutil
import subprocess
import tempfile
import urllib.request
from pathlib import Path
import jdk

def ensure_java_availability(on_runtime=False, on_build=False,on_conda_build_test=False):
    """
    Ensure Java runtime environment is available. on conda build time the paths and global env variables are different.
    """
    # Check if Java is in PATH
    java_path = shutil.which('java')
    if java_path:
        print(f"Java found in PATH: {java_path}")
        return True
    glob_pref_variables = {
        'PREFIX': 'PREFIX',
        'BUILD_PREFIX': 'BUILD_PREFIX',
        'TEST_PREFIX': 'TEST_PREFIX',
        'CONDA_PREFIX': 'CONDA_PREFIX'
    } # need to figure out a better way to do this...
    # if on_build:
    #     glob_pref_variables = ['PREFIX', 'BUILD_PREFIX']
    # if on_conda_build_test:
    #     glob_pref_variables = ['TEST_PREFIX']
    # if on_runtime:
    #     glob_pref_variables = ['CONDA_PREFIX']
    prefix_path = None
    for pref_variable, pref_key in glob_pref_variables.items():
        if pref_variable in os.environ:
            prefix_path = os.environ[pref_variable]
            print(f"prefix path: {prefix_path} from {pref_key}")
            break
    if prefix_path is None:
        print(f"prefix path not found in the usual conda suspects, here is the full list of env variables: {os.environ.keys()}")
        print("trying to use the last bin folder in the path variable")
        lbin_path = [p for p in os.environ['PATH'].split(':') if "bin" in p][-1]
        if lbin_path:
            prefix_path = os.path.dirname(lbin_path)
            print(f"prefix path: {prefix_path}")
        else:
            raise ValueError(f"couldn't find a bin folder in the path variable")
    print("Java not found in PATH, installing...")
    version = '11'
    jre_path = jdk.install(version, jre=True, path=prefix_path,vendor="adoptium")
    print(f"Java adoptium JRE {version} installed to {jre_path}")
    print("Trying to add to conda environment PATH...")
    # subprocess.run(f'conda env config vars set JAVA_HOME="{jre_path}"',shell=True, check=True)
    # subprocess.run(f'conda env config vars set PATH="{jre_path}/bin:$PATH"',shell=True, check=True)
    # just in case, create a symlink to to the java binary in the conda envs' bin directory
    java_bin_path = os.path.join(jre_path, 'bin', 'java')
    # remove if a symlink exists
    if os.path.exists(os.path.join(prefix_path, 'bin', 'java')):
        os.remove(os.path.join(prefix_path, 'bin', 'java'))
    os.symlink(java_bin_path, os.path.join(prefix_path, 'bin', 'java'))
    print("Java added to this conda environment PATH, testing...")
    # check if java is in PATH
    print(f"testing if java is in PATH")
    java_path = shutil.which('java')
    if not java_path:
           raise FileNotFoundError("Java executable not found in PATH")
    print("Java executable found in PATH: " + java_path)
    return True

def get_bbmap_version(vendor_dir):
    """Get BBMap version by running bbmap.sh version"""
    try:
        # Run bbmap.sh version and capture output
        bbmap_path = os.path.join(vendor_dir, 'bbmap', 'bbmap.sh')
        # print(bbmap_path)
        result = subprocess.run([bbmap_path, 'version'], capture_output=True)
        
        # Get second line and extract version
        # print(result.stderr)
        version_line = result.stderr.decode('utf-8').split('\n')[1]
        # print(version_line)
        version_match = re.search(r'BBTools version (\d+\.\d+)', version_line)
        if version_match:
            return version_match.group(1)
        raise ValueError("Could not parse BBMap version from output")
    except subprocess.CalledProcessError:
        raise RuntimeError("Failed to run bbmap.sh version")

def download_bbtools_sourceforge():
    """Download latest BBTools from SourceForge"""
    bbtools_url = "https://sourceforge.net/projects/bbmap/files/latest/download"
    
    print("Downloading BBTools...")
    with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as tmp_file:
        urllib.request.urlretrieve(bbtools_url, tmp_file.name)
        return tmp_file.name

def extract_bbtools(archive_path, vendor_dir):
    """Extract BBTools archive to vendor directory"""
    print("Extracting BBTools...")
    
    # Clear vendor directory
    if os.path.exists(vendor_dir):
        shutil.rmtree(vendor_dir)
    os.makedirs(vendor_dir)
    
    # Extract archive
    shutil.unpack_archive(archive_path, vendor_dir)

def update_version(new_version):
    """Update version in pyproject.toml, README.md, and meta.yaml"""
    # Update pyproject.toml
    pyproject_path = Path("pyproject.toml")
    # meta_yaml_path = Path("recipes/bbmapy/meta.yaml")
    readme_path = Path("README.md")
    
    if pyproject_path.exists():
        content = pyproject_path.read_text()
        # Update version in pyproject.toml
        version_match = re.search(r'version = "0.0.(\d+)"', content)
        new_version = int(version_match.group(1))+1
        new_version = f"0.0.{new_version}"
        content = re.sub(
            r'version = "[^"]+"',
            f'version = "{new_version}"',
            content
        )
        pyproject_path.write_text(content)
        print(f"Updated pyproject.toml version to {new_version}")
    
    # Update README.md
    if readme_path.exists():
        content = readme_path.read_text()
        # Update version badge or version section in README
        content = re.sub(
            r'Current BBMap version: 0.0.\d+',
            f'Current BBMap version: {new_version}',
            content
        )
        readme_path.write_text(content)
        print(f"Updated README.md version to {new_version}")
    
def regenerate_commands():
    """Regenerate Python commands from BBTools scripts"""
    print("Regenerating commands...")
    subprocess.run(['python', '-m', 'bbmapy.scanner'], check=True)

def main():
    # Get package root directory
    package_root = Path(__file__).parent.parent
    print(package_root)
    vendor_dir = package_root / "bbmapy/vendor"
    os.makedirs(vendor_dir, exist_ok=True)

    try:
        # Download and extract BBTools
        archive_path = download_bbtools_sourceforge()
        extract_bbtools(archive_path, vendor_dir)
        os.unlink(archive_path)
        
        # Get and update version
        bbmap_version = get_bbmap_version(vendor_dir)
        update_version(bbmap_version)
        
        # Regenerate commands
        regenerate_commands()
        
        print("Update completed successfully!")
        
    except Exception as e:
        print(f"Error during update: {e}")
        raise

if __name__ == "__main__":
    main() 
    # this scripts is for development purposes only, when creating a new release to pypi and maybe bioconda.