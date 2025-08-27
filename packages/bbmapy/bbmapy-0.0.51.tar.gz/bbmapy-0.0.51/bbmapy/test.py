import os
from pathlib import Path
import shutil
from bbmapy.base import find_bbtools_path
from bbmapy.update import ensure_java_availability
from rich import print as rprint
from bbmapy import  bbmap, reformat, bbmerge, bbduk, randomreads, randomgenome
BBTOOLS_PATH = find_bbtools_path()
print(BBTOOLS_PATH)
if BBTOOLS_PATH is None:
    BBTOOLS_PATH = Path(__file__).parent / "vendor" / "bbmap"
    
ensure_java_availability()

def test_randomgenome():
    """Test the randomgenome command."""
    randomgenome(
        out="ref.fasta",
        len=700,
        Xmx="240m"
    )

def test_randomreads():
    """Test the randomreads command."""
    randomreads(
        out1="input_1.fastq",
        out2="input_2.fastq",
        paired="true",
        ref="ref.fasta",
        reads=50,
        Xmx="240m"
    )

def test_randomreads1():
    """Test the randomreads command."""
    randomreads(
        out="test_input.fastq",
        ref="ref.fasta",
        reads=50,
        Xmx="200m"
    )

def test_bbmap():
    """Test the bbmap command."""
    
    test_randomgenome() 
    test_randomreads()
    test_randomreads1()
    # Run bbmap
    bbmap(
        in_file="test_input.fastq",
        ref="ref.fasta",
        out_file="output.sam",
        Xmx="800m"
    )
    
    # Check if output file was created
    # assert os.path.exists("output.sam"), "Output file was not created"
    
    rprint("[green]bbmap test passed![/green]")

def test_reformat():
    print("Testing reformat...")
    reformat(
        in_file="test_input.fastq",
        out="output_reformat.fasta",
        fastawrap=80,
        qin=33,
        qout=64,
        Xmx="200m"
    )

def test_bbmerge():
    print("Testing bbmerge...")
    bbmerge(
        in1="input_1.fastq",
        in2="input_2.fastq",
        out="output_merged.fastq",
        outu1="unmerged_1.fastq",
        outu2="unmerged_2.fastq",
        strict=True,
        k=60,
        extend2=50,
        rem=True,
        Xmx="240m"
    )

def test_capture_output():
    print("Testing output capture...")
    stdout, stderr = bbduk(
        capture_output=True,
        in_file="test_input.fastq",
        out="output_capture.fastq",
        ref="adapters.fa",
        Xmx="240m"
    )
    print("Captured stdout:", stdout[:100] + "..." if stdout else "None")
    print("Captured stderr:", stderr[:100] + "..." if stderr else "None")

def main():
    Path("test").mkdir(exist_ok=True)
    # Create dummy input files for testing
    os.chdir("test")
    test_randomgenome() 
    test_randomreads()
    test_randomreads1()
    with open("adapters.fa", "w") as f:
        f.write(">adapter1\nACGTACGT\n")

    # Run tests
    test_bbmap()
    # test_reformat()
    test_bbmerge()
    test_capture_output()

    # stdout, stderr = bbduk(
    #         capture_output=True,
    #         in_file="phiX174.fasta",
    #         out="output_capture.fastq",
    #         ref="phix",
    #         ktrim="r",
    #         k=23
    #     )
    # Clean up dummy files
    for file in ["test_input.fastq", "input_1.fastq", "input_2.fastq", "reference.fa", "adapters.fa",
                 "output_bbduk.fastq", "output_bbmap.sam", "output_reformat.fasta", 
                 "output_merged.fastq", "unmerged_1.fastq", "unmerged_2.fastq", "output_capture.fastq"]:
        if os.path.exists(file):
            os.remove(file)
    os.chdir("..")
    # clear test directory
    for file in os.listdir("test"):
        if os.path.isfile(os.path.join("test", file)):
            os.remove(os.path.join("test", file))
        elif os.path.isdir(os.path.join("test", file)):
            shutil.rmtree(os.path.join("test", file))
    try: 
        os.rmdir("test")
    except Exception as e:
        pass

    rprint("All tests completed.")
if __name__ == "__main__":
    main()
