from typing import Union, Tuple
from bbmapy.base import _pack_args, _run_command


def addadapters(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for addadapters.sh

    Help message:
    Written by Brian Bushnell
Last modified February 17, 2015

***DEPRECATED***

Description:  Randomly adds adapters to a file, or grades a trimmed file.
The input is a set of reads, paired or unpaired.
The output is those same reads with adapter sequence replacing some of the bases in some reads.
For paired reads, adapters are located in the same position in read1 and read2.
This is designed for benchmarking adapter-trimming software, and evaluating methodology.
randomreads.sh is better for paired reads, though, as it actually adds adapters at the correct location,
so that overlap may be used for adapter detection.

Usage:  addadapters.sh in_file=<file> in2=<file2> out=<outfile> out2=<outfile2> adapters=<file>

in2 and out2 are for paired reads and are optional.
If input is paired and there is only one output file, it will be written interleaved.

Parameters:
ow=f                (overwrite) Overwrites files that already exist.
int=f               (interleaved) Determines whether INPUT file is considered interleaved.
qin_file=auto            ASCII offset for input quality.  May be 33 (Sanger), 64 (Illumina), or auto.
qout=auto           ASCII offset for output quality.  May be 33 (Sanger), 64 (Illumina), or auto (same as input).
add                 Add adapters to input files.  Default mode.
grade               Evaluate trimmed input files.
adapters=<file>     Fasta file of adapter sequences.
literal=<sequence>  Comma-delimited list of adapter sequences.
left                Adapters are on the left (3') end of the read.
right               Adapters are on the right (5') end of the read.  Default mode.
adderrors=t         Add errors to adapters based on the quality scores.
addpaired=t         Add adapters to the same location for read 1 and read 2.
arc=f               Add reverse-complemented adapters as well as forward.
rate=0.5            Add adapters to this fraction of reads.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for addadapters.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("addadapters.sh", args, capture_output)

def addssu(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for addssu.sh

    Help message:
    Written by Brian Bushnell
Last modified Jan 29, 2020

Description:  Adds, removes, or replaces SSU sequence of existing sketches.
Sketches and SSU fasta files must be annotated with TaxIDs.

Usage:           addssu.sh in_file=a.sketch out=b.sketch 16S=16S.fa 18S=18S.fa

Standard parameters:
in_file=<file>       Input sketch file.
out=<file>      Output sketch file.

Additional files (optional):
16S=<file>      A fasta file of 16S sequences.  These should be renamed
                so that they start with tid|# where # is the taxID.
                Should not contain organelle rRNA.
18S=<file>      A fasta file of 18S sequences.  These should be renamed
                so that they start with tid|# where # is the taxID.
                Should not contain organelle rRNA.
tree=auto       Path to TaxTree, if performing prok/euk-specific operations.

Processing parameters:
preferSSUMap=f
preferSSUMapEuks=f
preferSSUMapProks=f
SSUMapOnly=f
SSUMapOnlyEuks=f
SSUMapOnlyProks=f
clear16S=f
clear18S=f
clear16SEuks=f
clear18SEuks=f
clear16SProks=f
clear18SProks=f


Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-da             Disable assertions.

For more detailed information, please read /bbmap/docs/guides/BBSketchGuide.txt.
Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for addssu.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("addssu.sh", args, capture_output)

def adjusthomopolymers(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for adjusthomopolymers.sh

    Help message:
    Written by Brian Bushnell
Last modified October 3, 2019

Description:  Shrinks or expands homopolymers.

Usage:  adjusthomopolymers.sh in_file=<input file> out=<output file> rate=<float>

Input may be fasta or fastq, compressed or uncompressed.

Standard parameters:
in_file=<file>       Primary input, or read 1 input.
in2=<file>      Read 2 input if reads are in two files.
out=<file>      Primary output, or read 1 output.
out2=<file>     Read 2 output if reads are in two files.
overwrite=f     (ow) Set to false to force the program to abort rather than
                overwrite an existing file.
ziplevel=2      (zl) Set to 1 (lowest) through 9 (max) to change compression
                level; lower compression is faster.

Processing parameters:
rate=0.0        0.1 will expand by 10%; -0.1 will shrink by 10%.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for adjusthomopolymers.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("adjusthomopolymers.sh", args, capture_output)

def alignrandom(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for alignrandom.sh

    Help message:
    Written by Brian Bushnell
Last modified May 30, 2025

Description:  Aligns a query sequence to a reference using BandedAligner.
The sequences can be any characters, but N is a special case.
Outputs the identity, rstart, and rstop positions.
Optionally prints a state space exploration map.
This map can be fed to visualizealignment.sh to make an image.

Usage:
alignrandom.sh start mult steps iters buckets

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for alignrandom.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("alignrandom.sh", args, capture_output)

def alltoall(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for alltoall.sh

    Help message:
    Written by Brian Bushnell
Last modified February 5, 2020

Description:  Aligns all to all to produce an identity matrix.

Usage:  alltoall.sh in_file=<input file> out=<output file>

Input may be fasta or fastq, compressed or uncompressed.

Standard parameters:
in_file=<file>       Input sequences.
out=<file>      Output data.
t=              Set the number of threads; default is logical processors.
overwrite=f     (ow) Set to false to force the program to abort rather than
                overwrite an existing file.
showspeed=t     (ss) Set to 'f' to suppress display of processing speed.
ziplevel=2      (zl) Set to 1 (lowest) through 9 (max) to change compression
                level; lower compression is faster.
reads=-1        If positive, quit after this many sequences.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for alltoall.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("alltoall.sh", args, capture_output)

def analyzeaccession(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for analyzeaccession.sh

    Help message:
    Written by Brian Bushnell
Last modified September 9, 2019

Description:  Looks at accessions to see how to compress them.

Usage:  analyzeaccession.sh *accession2taxid.gz out=<output file>

Parameters:
perfile=t       Use multiple threads per file and multiple files at a time.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for analyzeaccession.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("analyzeaccession.sh", args, capture_output)

def analyzegenes(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for analyzegenes.sh

    Help message:
    Written by Brian Bushnell
Last modified September 27, 2018

Description:  Generates a prokaryotic gene model (.pkm) for gene calling.
Input is fasta and gff files.
The .pkm file may be used by CallGenes.

Usage:  analyzegenes.sh in_file=x.fa gff=x.gff out=x.pgm

File parameters:
in_file=<file>       A fasta file or comma-delimited list of fasta files.
gff=<file>      A gff file or comma-delimited list.  This is optional;
                if present, it must match the number of fasta files.
                If absent, a fasta file 'foo.fasta' will imply the
                presence of 'foo.gff'.
out=<file>      Output pgm file.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for analyzegenes.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("analyzegenes.sh", args, capture_output)

def analyzesketchresults(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for analyzesketchresults.sh

    Help message:
    Written by Brian Bushnell
Last modified December 19, 2019

Description:  Analyzes sketch results from query, ref, ani format.

Usage:  analyzesketchresults.sh in_file=<file> out=<outfile>


Parameters and their defaults:

in_file=<file>           Required input file of Sketch results in 3column format.
in2=<file>          Optional second input file of Sketch results in amino mode.
out=stdout.txt      Output file for summary of per-tax-level averages.
outaccuracy=<file>  Output file for accuracy results; requires query taxIDs and printcal.
outmap=<file>       Output file for ANI vs AAI.  Requires in2.
bbsketch            Parse BBSketch output format (default).
mash                Parse Mash output format.  Files should be named like this:
                    tid_511145_Escherichia_coli_str._K-12_substr._MG1655.fa.gz
blast               Parse Blast output format (TODO).

ow=f                (overwrite) Overwrites files that already exist.
app=f               (append) Append to files that already exist.

Java Parameters:
-Xmx                This will set Java's memory usage, overriding autodetection.
                    -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom               This flag will cause the process to exit if an out-of-memory exception occurs.  Requires Java 8u92+.
-da                 Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for analyzesketchresults.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("analyzesketchresults.sh", args, capture_output)

def applyvariants(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for applyvariants.sh

    Help message:
    Written by Brian Bushnell
Last modified January 26, 2021

Description:  Mutates a reference by applying a set of variants.
When 2 variants overlap, the one with the higher allele count is used.

Usage:  applyvariants.sh in_file=<input file> vcf=<vcf file> out=<output file>

Standard parameters:
in_file=<file>       Reference fasta.
vcf=<file>      Variants.
basecov=<file>  Optional per-base coverage from BBMap or Pileup.
out=<file>      Output fasta.
overwrite=f     (ow) Set to false to force the program to abort rather than
                overwrite an existing file.
ziplevel=2      (zl) Set to 1 (lowest) through 9 (max) to change compression
                level; lower compression is faster.

Processing parameters:		
mincov=0        If positive and depth is below this, change ref to N.
                Requires a coverage file.
maxindel=-1     If positive, ignore indels longer than this.
noframeshifts=f Ignore indels that are not a multiple of 3 in length.

Renaming:
name=           Optionally rename sequences to this.
addnumbers=f    Add _1 and so forth to ensure sequence names are unique.
prefix=t        Use the name as a prefix to the old name, instead of replacing
                the old name.
delimiter=_     Symbol to place between parts of the new name.
                For space or tab, use the literal word.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for applyvariants.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("applyvariants.sh", args, capture_output)

def a_sample_mt(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for a_sample_mt.sh

    Help message:
    Written by Brian Bushnell
Last modified July 31, 2019

Description:  Does nothing.  Should be fast.
This is a template for making wrappers for new tools.

Usage:  a_sample_mt.sh in_file=<input file> out=<output file>

Input may be fasta or fastq, compressed or uncompressed.

Standard parameters:
in_file=<file>       Primary input, or read 1 input.
in2=<file>      Read 2 input if reads are in two files.
out=<file>      Primary output, or read 1 output.
out2=<file>     Read 2 output if reads are in two files.
ziplevel=2      (zl) Set to 1 (lowest) through 9 (max) to change compression
                level; lower compression is faster.

Processing parameters:
None yet!

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for a_sample_mt.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("a_sample_mt.sh", args, capture_output)

def bandedaligner(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for bandedaligner.sh

    Help message:
    Written by Brian Bushnell
Last modified May 4, 2025

Description:  Aligns a query sequence to a reference using BandedAligner.
The sequences can be any characters, but N is a special case.
Outputs the identity, rstart, and rstop positions.
Optionally prints a state space exploration map.
This map can be fed to visualizealignment.sh to make an image.

Usage:
bandedaligner.sh <query> <ref>
bandedaligner.sh <query> <ref> <map>
bandedaligner.sh <query> <ref> <map> <iterations> <simd>

Parameters:
query           A literal nucleotide sequence or fasta file.
ref             A literal nucleotide sequence or fasta file.
map             Optional output text file for matrix score space.
                Set to null for benchmarking with no visualization.
iterations      Optional integer for benchmarking multiple iterations.
simd            Enable SIMD mode.  Needs a large band to be effective.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for bandedaligner.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("bandedaligner.sh", args, capture_output)

def bandedplusaligner(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for bandedplusaligner.sh

    Help message:
    Written by Brian Bushnell
Last modified May 4, 2025

Description:  Aligns a query sequence to a reference using BandedPlusAligner2.
The sequences can be any characters, but N is a special case.
Outputs the identity, rstart, and rstop positions.
Optionally prints a state space exploration map.
This map can be fed to visualizealignment.sh to make an image.

Usage:
bandedplusaligner.sh <query> <ref>
bandedplusaligner.sh <query> <ref> <map>
bandedplusaligner.sh <query> <ref> <map> <iterations> <simd>

Parameters:
query           A literal nucleotide sequence or fasta file.
ref             A literal nucleotide sequence or fasta file.
map             Optional output text file for matrix score space.
                Set to null for benchmarking with no visualization.
iterations      Optional integer for benchmarking multiple iterations.
simd            Enable SIMD mode.  Needs a large band to be effective.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for bandedplusaligner.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("bandedplusaligner.sh", args, capture_output)

def bbcms(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for bbcms.sh

    Help message:
    Written by Brian Bushnell
Last modified September 20, 2022

Description:  Error corrects reads and/or filters by depth, storing
kmer counts in a count-min sketch (a Bloom filter variant).
This uses a fixed amount of memory.  The error-correction algorithm is taken
from Tadpole; with plenty of memory, the behavior is almost identical to 
Tadpole.  As the number of unique kmers in a dataset increases, the accuracy 
decreases such that it will make fewer corrections.  It is still capable
of making useful corrections far past the point where Tadpole would crash
by running out of memory, even with the prefilter flag.  But if there is
sufficient memory to use Tadpole, then Tadpole is more desirable.

Because accuracy declines with an increasing number of unique kmers, it can
be useful with very large datasets to run this in 2 passes, with the first 
pass for filtering only using a 2-bit filter with the flags tossjunk=t and 
ecc=f (and possibly mincount=2 and hcf=0.4), and the second pass using a 
4-bit filter for the actual error correction.

Usage:  bbcms.sh in_file=<input file> out=<output> outb=<reads failing filters>

Example of use in error correction:
bbcms.sh in_file=reads.fq out=ecc.fq bits=4 hashes=3 k=31 merge

Example of use in depth filtering:
bbcms.sh in_file=reads.fq out=high.fq outb=low.fq k=31 mincount=2 ecc=f hcf=0.4

Error correction and depth filtering can be done simultaneously.

File parameters:
in_file=<file>       Primary input, or read 1 input.
in2=<file>      Read 2 input if reads are in two files.
out=<file>      Primary read output.
out2=<file>     Read 2 output if reads are in two files.
outb=<file>     (outbad/outlow) Output for reads failing mincount.
outb2=<file>    (outbad2/outlow2) Read 2 output if reads are in two files.
extra=<file>    Additional comma-delimited files for generating kmer counts.
ref=<file>      If ref is set, then only files in the ref list will be used
                for kmer counts, and the input files will NOT be used for
                counts; they will just be filtered or corrected.
overwrite=t     (ow) Set to false to force the program to abort rather than
                overwrite an existing file.

Hashing parameters:
k=31            Kmer length, currently 1-31.
hashes=3        Number of hashes per kmer.  Higher generally reduces 
                false positives at the expense of speed; rapidly
                diminishing returns above 4.
ksmall=         Optional sub-kmer length; setting to slightly lower than k 
                can improve memory efficiency by reducing the number of hashes
                needed.  e.g. 'k=31 ksmall=29 hashes=2' has better speed and
                accuracy than 'k=31 hashes=3' when the filter is very full.
minprob=0.5     Ignore kmers with probability of being correct below this.
memmult=1.0     Fraction of free memory to use for Bloom filter.  1.0 should
                generally work; if the program crashes with an out of memory
                error, set this lower.  You may be able to increase accuracy
                by setting it slightly higher.
cells=          Option to set the number of cells manually.  By default this
                will be autoset to use all available memory.  The only reason
                to set this is to ensure deterministic output.
seed=0          This will change the hash function used.  Useful if running
                iteratively with a very full table.  -1 uses a random seed.
symmetricwrite=t  (sw) Increases counting accuracy for a slight speed penalty.
                Could be slow on very low-complexity sequence.
                
Depth filtering parameters:
mincount=0      If positive, reads with kmer counts below mincount will
                be discarded (sent to outb).
hcf=1.0         (highcountfraction) Fraction of kmers that must be at least
                mincount to pass.
requireboth=t   Require both reads in a pair to pass in order to go to out.
                When true, if either read has a count below mincount, both
                reads in the pair will go to outb.  When false, reads will
                only go to outb if both fail.
tossjunk=f      Remove reads or pairs with outermost kmer depth below 2.
(Suggested params for huge metagenomes: mincount=2 hcf=0.4 tossjunk=t)

Error correction parameters:
ecc=t           Perform error correction.
bits=           Bits used to store kmer counts; max count is 2^bits-1.
                Supports 2, 4, 8, 16, or 32.  16 is best for high-depth data;
                2 or 4 are for huge, low-depth metagenomes that saturate the 
                bloom filter otherwise.  Generally 4 bits is recommended for 
                error-correction and 2 bits is recommended for filtering only.
ecco=f          Error-correct paired reads by overlap prior to kmer-counting.
merge=t         Merge paired reads by overlap prior to kmer-counting, and 
                again prior to correction.  Output will still be unmerged.
smooth=3        Remove spikes from kmer counts due to hash collisions.
                The number is the max width of peaks to be smoothed; range is
                0-3 (3 is most aggressive; 0 disables smoothing).
                This also affects tossjunk.
                

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for bbcms.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("bbcms.sh", args, capture_output)

def bbcountunique(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for bbcountunique.sh

    Help message:
    Written by Brian Bushnell
Last modified August 1, 2016

Description:  Generates a kmer uniqueness histogram, binned by file position.
There are 3 columns for single reads, 6 columns for paired:
count        number of reads or pairs processed
r1_first     percent unique 1st kmer of read 1
r1_rand      percent unique random kmer of read 1
r2_first     percent unique 1st kmer of read 2
r2_rand      percent unique random kmer of read 2
pair         percent unique concatenated kmer from read 1 and 2

Please read bbmap/docs/guides/CalcUniquenessGuide.txt for more information.

Usage:	bbcountunique.sh in_file=<input> out=<output>

Input parameters:
in2=null            Second input file for paired reads
interleaved=auto    Set true/false to override autodetection of the input file as paired interleaved.
samplerate=1        Set to below 1 to sample a fraction of input reads.
reads=-1            Only process this number of reads, then quit (-1 means all)

Output parameters:
out=<file>          File for output stats

Processing parameters:
k=25                Kmer length (range 1-31).
interval=25000      Print one line to the histogram per this many reads.
cumulative=f        Show cumulative numbers rather than per-interval numbers.
percent=t           Show percentages of unique reads.
count=f             Show raw counts of unique reads.
printlastbin_file=f      (plb) Print a line for the final undersized bin.
minprob=0           Ignore kmers with a probability of correctness below this (based on q-scores).

Java Parameters:
-Xmx                This will set Java's memory usage, overriding autodetection.
                    -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom               This flag will cause the process to exit if an
                    out-of-memory exception occurs.  Requires Java 8u92+.
-da                 Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for bbcountunique.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("bbcountunique.sh", args, capture_output)

def bbcrisprfinder(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for bbcrisprfinder.sh

    Help message:
    Written by Brian Bushnell with help from Simon Roux
Last modified Nov 22, 2023

Description:  Finds interspersed repeats contained within sequences;
specifically, only information within a sequence is used.  This is based
on the repeat-spacer model of crisprs.  Designed for short reads, 
but should work with full genomes.

Usage:  bbcrisprfinder.sh in_file=<input file>
See bbmap/pipelines/crisprPipeline.sh for more examples.

Standard parameters:
in_file=<file>       Primary input (a fasta or fastq file).
out=<file>      Output for annotated reads containing 
                interspersed repeats.  Reads not matching the criteria
                are discarded (though pairs are retained).
outc=<file>     Output for crispr sequences and their flanking repeats.
                Repeats are in lower-case; spacer is upper-case.
outr=<file>     Output of just repeats (one copy of each unique repeat).
                Only includes full-length repeats.
outs=<file>     Output of just spacers (one copy of each unique spacer).
                Only includes spacers adjacent to at least one full-length
                repeat (so the bounds are known).
chist=<file>    Histogram of crispr stats.
phist=<file>    Histogram of palindrome stats.
*All output files are optional.

Processing parameters:
merge=f         Try to merge paired reads before processing them.
masked=f        Indicates that the sequences are masked to lowercase;
                repeats will not be extended outside of lowercase regions.
                BBDuk or BBMask can produce masked sequences.
pad=0           Extend the boundaries of the repeats by this much when
                printing to outcrisper.  The padding will be in uppercase.
                This helps to show why a repeat was not extended.
annotate=f      Rename reads to indicate the repeat boundaries.  Annotations
                look like this: [56-77,117-138;150],P=7,M=5,L=6,S=62,T=6+0
                ...meaning the repeat occurs at positions 56-77 and 117-138;
                the read length is 150; and there is a palindrome of length
                7 with 5 matches, a loop length of 6, starting at position
                62, with tails outside the palindromic region length 6 and 0.
reads=-1        If positive, quit after processing this many reads.

Repeat Parameters:
krepeat=13      (kr) Use this seed kmer length to find repeats.  
                Repeats shorter than k may not be found.  Max is 31.
mm=1            (mmr) Mask this many bases in the middle of kmers to allow 
                imperfect repeats.  Also requires rmismatches to be set.
minrepeats=2    Ignore repeats with fewer than this many nearby copies.
                The more copies, the better consensus will refine the borders.
                For this purpose 2 partials count as 1 full-length repeat.
rmismatches=3   (rmm) Maximum allowed mismatches in a repeat pair.
minspacer=14    Ignore spacers shorter than this.
maxspacer=60    Ignore spacers longer than this.
minrepeat=20    Ignore repeats shorter than this.
maxrepeat=54    Ignore repeats longer than this.
minrgc=0.09     Ignore repeats with GC below this.
maxrgc=0.89     Ignore repeats with GC above this.
grow=t          Extend repeats through mismatches, if rmm>0.  Increases the
                number of unique repeats, and decreases unique spacers. 
lookahead=5     Minimum subsequent matches to extend through a mismatch.

Reference Parameters:
ref=<file>      If a reference of known CRISPR repeats is supplied, all
                detected repeates will be aligned to it, using the best match
                to override the predicted repeat boundaries.  Subsequent
                parameters in this section have no effect without a ref.
outref=<file>   Output the reference sequences used, annotated to indicate
                the number of uses and palindrome position.
kref=13         Kmer length for selecting ref sequences to attempt align.
                Lower is more sensitive but can take exponentially longer.
                'k' will set both krepeat and kref to the same value.
mmref=1         (maskMiddleRef) Number of bases masked in the middle of the
                kmer. 0 is umasked, and more increases mismatch tolerance.
minrefm=18      (minRefMatches) Reject alignments with fewer matching bases.
refmm=5         (refMismatches) Reject alignments with more mismatches.
refmmf=0.2      (refmismatchfraction) Allowed mismatches will be the maximum
                of refmm and refmmf*length.
minrefc=0       (minRefCount) Only load reference sequences with a count
                of at least this.  Intended for repeats generated via the
                'outr' flag, whose headers have a 'count=x' term indicating
                how many times that exact repeat was encountered.  Small
                numbers can be slow with large references.
discardaf=t     (discardAlignmentFailures) When the best alignment for a
                repeat fails repeat thresholds like minspacer, minrepeat, or
                rmismatches, discard that repeat.
shrinkaf=f      Trim mismatches from the ends of alignment failures.
revertaf=f      Revert alignment failures to their pre-alignment borders.
discardua=f     (discardUnaligned) Discard repeats that do not align to any
                ref repeats.  This means they did not meet minrefm/maxrefmm.
minrepeat0=11   Allow repeats this short prior to alignment (discarded unless
                they lengthen).  Has no impact if below kref or krepeat.
sortref=auto    Sort alignment candidates by count, then length.  May be set
                to t/f/auto. When set to auto, sequences will be sorted only
                if counts are present.
doublefetch=t   (ff) Fetch ref sequences using kmers from both repeat copies.
                Increases sensitivity in the presence of mismatches.
doublealign=t   (aa) Align ref sequences to both ref repeat copies.

Consensus Parameters:
consensus=t     When 3+ nearby repeat copies are found, adjust the boundaries
                so that all are identical.
minoverlapconsensus=18  Only try consensus on repeats that overlap at least
                        this much.
maxtrimconsensus=5      Do not trim more than this many bases on each end.

Partial Repeat Parameters:
bruteforce=t    Look for partial or inexact repeats adjacent to detected
                repeats.  These can improve consensus.
mintailrepeat=9 (mtr) Minimum length of partial repeats on read tips.
rmmt=1          Maximum allowed mismatches in short repeats at read tips.
rmmtpad=3       Ignore this many extra leading mismatches when looking
                for tip repeats (they will be trimmed later).

Palindrome Parameters:
minpal=5        If greater than 0, each repeat will be scanned for its 
                longest palindrome of at least this length (just the
                palindrome sequence, excluding the loop or tail).
                Palindromes will be annotated alongside repeats.
pmatches=4      Minimum number of matches in a palindrome.
pmismatches=2   Maximum allowed mismatches in a palindrome.
minloop=3       Ignore palindromes with a loop shorter than this.
maxloop=26      Ignore palindromes with a loop longer than this.
mintail=0       Ignore palindromes with a tail shorter than this.
maxtail=24      Ignore palindromes with a tail longer than this.
maxtaildif=21   Ignore palindromes with a tail length difference greater 
                than this.
reqpal=f        Discard repeats that lack a suitable palindrome.
symmetric=f     Trim repeats to make them symmetric around the palindrome.
                Not recommended.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for bbcrisprfinder.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("bbcrisprfinder.sh", args, capture_output)

def bbduk(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for bbduk.sh

    Help message:
    Written by Brian Bushnell
Last modified November 18, 2024

Description:  Compares reads to the kmers in a reference dataset, optionally 
allowing an edit distance. Splits the reads into two outputs - those that 
match the reference, and those that don't. Can also trim (remove) the matching 
parts of the reads rather than binning the reads.
Please read bbmap/docs/guides/BBDukGuide.txt for more information.

Usage:  bbduk.sh in_file=<input file> out=<output file> ref=<contaminant files>

Input may be stdin or a fasta or fastq file, compressed or uncompressed.
If you pipe via stdin/stdout, please include the file type; e.g. for gzipped 
fasta input, set in_file=stdin.fa.gz

Input parameters:
in_file=<file>           Main input. in_file=stdin.fq will pipe from stdin.
in2=<file>          Input for 2nd read of pairs in a different file.
ref=<file,file>     Comma-delimited list of reference files.
                    In addition to filenames, you may also use the keywords:
                    adapters, artifacts, phix, lambda, pjet, mtst, kapa
literal=<seq,seq>   Comma-delimited list of literal reference sequences.
                    Polymers are also allowed with the 'poly' prefix;
                    for example, 'literal=ATGGT,polyGC' will add both ATGGT
                    and GCGCGCGCGCGCGCGCGCGCGCGCGCGCGCGCGCGC - 32+ of them,
                    enough replicates to ensure that all kmers are present.
touppercase=f       (tuc) Change all bases upper-case.
interleaved=auto    (int) t/f overrides interleaved autodetection.
                    Must be set mainually when streaming fastq input.
qin_file=auto            Input quality offset: 33 (Sanger), 64, or auto.
reads=-1            If positive, quit after processing X reads or pairs.
copyundefined=f     (cu) Process non-AGCT IUPAC reference bases by making all
                    possible unambiguous copies.  Intended for short motifs
                    or adapter barcodes, as time/memory use is exponential.
samplerate=1        Set lower to only process a fraction of input reads.
samref=<file>       Optional reference fasta for processing sam files.

Output parameters:
out=<file>          (outnonmatch) Write reads here that do not contain 
                    kmers matching the database.  'out=stdout.fq' will pipe 
                    to standard out.
out2=<file>         (outnonmatch2) Use this to write 2nd read of pairs to a 
                    different file.
outm=<file>         (outmatch) Write reads here that fail filters.  In default
                    kfilter mode, this means any read with a matching kmer.
                    In any mode, it also includes reads that fail filters such
                    as minlength, mingc, maxgc, entropy, etc.  In other words,
                    it includes all reads that do not go to 'out'.
outm2=<file>        (outmatch2) Use this to write 2nd read of pairs to a 
                    different file.
outs=<file>         (outsingle) Use this to write singleton reads whose mate 
                    was trimmed shorter than minlen.
stats=<file>        Write statistics about which contamininants were detected.
refstats=<file>     Write statistics on a per-reference-file basis.
rpkm=<file>         Write RPKM for each reference sequence (for RNA-seq).
dump=<file>         Dump kmer tables to a file, in fasta format.
duk=<file>          Write statistics in duk's format. *DEPRECATED*
nzo=t               Only write statistics about ref sequences with nonzero hits.
overwrite=t         (ow) Grant permission to overwrite files.
showspeed=t         (ss) 'f' suppresses display of processing speed.
ziplevel=2          (zl) Compression level; 1 (min) through 9 (max).
fastawrap=70        Length of lines in fasta output.
qout=auto           Output quality offset: 33 (Sanger), 64, or auto.
statscolumns=3      (cols) Number of columns for stats output, 3 or 5.
                    5 includes base counts.
rename=f            Rename reads to indicate which sequences they matched.
refnames=f          Use names of reference files rather than scaffold IDs.
trd=f               Truncate read and ref names at the first whitespace.
ordered=f           Set to true to output reads in same order as input.
maxbasesout=-1      If positive, quit after writing approximately this many
                    bases to out (outu/outnonmatch).
maxbasesoutm=-1     If positive, quit after writing approximately this many
                    bases to outm (outmatch).
json=f              Print to screen in json format.

Histogram output parameters:
bhist=<file>        Base composition histogram by position.
qhist=<file>        Quality histogram by position.
qchist=<file>       Count of bases with each quality value.
aqhist=<file>       Histogram of average read quality.
bqhist=<file>       Quality histogram designed for box plots.
lhist=<file>        Read length histogram.
phist=<file>        Polymer length histogram.
gchist=<file>       Read GC content histogram.
enthist=<file>      Read entropy histogram.
ihist=<file>        Insert size histogram, for paired reads in mapped sam.
gcbins=100          Number gchist bins.  Set to 'auto' to use read length.
maxhistlen=6000     Set an upper bound for histogram lengths; higher uses 
                    more memory.  The default is 6000 for some histograms
                    and 80000 for others.

Histograms for mapped sam/bam files only:
histbefore=t        Calculate histograms from reads before processing.
ehist=<file>        Errors-per-read histogram.
qahist=<file>       Quality accuracy histogram of error rates versus quality 
                    score.
indelhist=<file>    Indel length histogram.
mhist=<file>        Histogram of match, sub, del, and ins rates by position.
idhist=<file>       Histogram of read count versus percent identity.
idbins=100          Number idhist bins.  Set to 'auto' to use read length.
varfile=<file>      Ignore substitution errors listed in this file when 
                    calculating error rates.  Can be generated with
                    CallVariants.
vcf=<file>          Ignore substitution errors listed in this VCF file 
                    when calculating error rates.
ignorevcfindels=t   Also ignore indels listed in the VCF.

Processing parameters:
k=27                Kmer length used for finding contaminants.  Contaminants 
                    shorter than k will not be found.  k must be at least 1.
rcomp=t             Look for reverse-complements of kmers in addition to 
                    forward kmers.
maskmiddle=t        (mm) Treat the middle base of a kmer as a wildcard, to 
                    increase sensitivity in the presence of errors.  This may
                    also be set to a number, e.g. mm=3, to mask that many bp.
                    The default mm=t corresponds to mm=1 for odd-length kmers
                    and mm=2 for even-length kmers (as of v39.04), while
                    mm=f is always equivalent to mm=0.
minkmerhits=1       (mkh) Reads need at least this many matching kmers 
                    to be considered as matching the reference.
minkmerfraction=0.0 (mkf) A reads needs at least this fraction of its total
                    kmers to hit a ref, in order to be considered a match.
                    If this and minkmerhits are set, the greater is used.
mincovfraction=0.0  (mcf) A reads needs at least this fraction of its total
                    bases to be covered by ref kmers to be considered a match.
                    If specified, mcf overrides mkh and mkf.
hammingdistance=0   (hdist) Maximum Hamming distance for ref kmers (subs only).
                    Memory use is proportional to (3*K)^hdist.
qhdist=0            Hamming distance for query kmers; impacts speed, not memory.
editdistance=0      (edist) Maximum edit distance from ref kmers (subs 
                    and indels).  Memory use is proportional to (8*K)^edist.
hammingdistance2=0  (hdist2) Sets hdist for short kmers, when using mink.
qhdist2=0           Sets qhdist for short kmers, when using mink.
editdistance2=0     (edist2) Sets edist for short kmers, when using mink.
forbidn=f           (fn) Forbids matching of read kmers containing N.
                    By default, these will match a reference 'A' if 
                    hdist>0 or edist>0, to increase sensitivity.
removeifeitherbad=t (rieb) Paired reads get sent to 'outmatch' if either is 
                    match (or either is trimmed shorter than minlen).  
                    Set to false to require both.
trimfailures=f      Instead of discarding failed reads, trim them to 1bp.
                    This makes the statistics a bit odd.
findbestmatch=f     (fbm) If multiple matches, associate read with sequence 
                    sharing most kmers.  Reduces speed.
skipr1=f            Don't do kmer-based operations on read 1.
skipr2=f            Don't do kmer-based operations on read 2.
ecco=f              For overlapping paired reads only.  Performs error-
                    correction with BBMerge prior to kmer operations.
recalibrate=f       (recal) Recalibrate quality scores.  Requires calibration
                    matrices generated by CalcTrueQuality.
sam=<file,file>     If recalibration is desired, and matrices have not already
                    been generated, BBDuk will create them from the sam file.
amino=f             Run in amino acid mode.  Some features have not been
                    tested, but kmer-matching works fine.  Maximum k is 12.

Speed and Memory parameters:
threads=auto        (t) Set number of threads to use; default is number of 
                    logical processors.
prealloc=f          Preallocate memory in table.  Allows faster table loading 
                    and more efficient memory usage, for a large reference.
monitor=f           Kill this process if it crashes.  monitor=600,0.01 would 
                    kill after 600 seconds under 1% usage.
minrskip=1          (mns) Force minimal skip interval when indexing reference 
                    kmers.  1 means use all, 2 means use every other kmer, etc.
maxrskip=1          (mxs) Restrict maximal skip interval when indexing 
                    reference kmers. Normally all are used for scaffolds<100kb, 
                    but with longer scaffolds, up to maxrskip-1 are skipped.
rskip=              Set both minrskip and maxrskip to the same value.
                    If not set, rskip will vary based on sequence length.
qskip=1             Skip query kmers to increase speed.  1 means use all.
speed=0             Ignore this fraction of kmer space (0-15 out of 16) in both
                    reads and reference.  Increases speed and reduces memory.
Note: Do not use more than one of 'speed', 'qskip', and 'rskip'.

Trimming/Filtering/Masking parameters:
Note - if ktrim, kmask, and ksplit are unset, the default behavior is kfilter.
All kmer processing modes are mutually exclusive.
Reads only get sent to 'outm' purely based on kmer matches in kfilter mode.

ktrim=f             Trim reads to remove bases matching reference kmers, plus
                    all bases to the left or right.
                    Values: 
                       f (don't trim), 
                       r (trim to the right), 
                       l (trim to the left)
ktrimtips=0         Set this to a positive number to perform ktrim on both
                    ends, examining only the outermost X bases.
kmask=              Replace bases matching ref kmers with another symbol.
                    Allows any non-whitespace character, and processes short
                    kmers on both ends if mink is set.  'kmask=lc' will
                    convert masked bases to lowercase.
maskfullycovered=f  (mfc) Only mask bases that are fully covered by kmers.
ksplit=f            For single-ended reads only.  Reads will be split into
                    pairs around the kmer.  If the kmer is at the end of the
                    read, it will be trimmed instead.  Singletons will go to
                    out, and pairs will go to outm.  Do not use ksplit with
                    other operations such as quality-trimming or filtering.
mink=0              Look for shorter kmers at read tips down to this length, 
                    when k-trimming or masking.  0 means disabled.  Enabling
                    this will disable maskmiddle.
qtrim=f             Trim read ends to remove bases with quality below trimq.
                    Performed AFTER looking for kmers.  Values: 
                       rl (trim both ends), 
                       f (neither end), 
                       r (right end only), 
                       l (left end only),
                       w (sliding window).
trimq=6             Regions with average quality BELOW this will be trimmed,
                    if qtrim is set to something other than f.  Can be a 
                    floating-point number like 7.3.
quantize            Bin quality scores to reduce file size.  quantize=2 will
                    eliminate all odd quality scores, while quantize=0,10,37
                    will only allow qualty scores of 0, 10, or 37.
trimclip=f          Trim soft-clipped bases from sam files.
minlength=10        (ml) Reads shorter than this after trimming will be 
                    discarded.  Pairs will be discarded if both are shorter.
mlf=0               (minlengthfraction) Reads shorter than this fraction of 
                    original length after trimming will be discarded.
maxlength=          Reads longer than this after trimming will be discarded.
minavgquality=0     (maq) Reads with average quality (after trimming) below 
                    this will be discarded.
maqb=0              If positive, calculate maq from this many initial bases.
minbasequality=0    (mbq) Reads with any base below this quality (after 
                    trimming) will be discarded.
maxns=-1            If non-negative, reads with more Ns than this 
                    (after trimming) will be discarded.
mcb=0               (minconsecutivebases) Discard reads without at least 
                    this many consecutive called bases.
ottm=f              (outputtrimmedtomatch) Output reads trimmed to shorter 
                    than minlength to outm rather than discarding.
tp=0                (trimpad) Trim this much extra around matching kmers.
tbo=f               (trimbyoverlap) Trim adapters based on where paired 
                    reads overlap.
strictoverlap=t     Adjust sensitivity for trimbyoverlap mode.
minoverlap=14       Require this many bases of overlap for detection.
mininsert=40        Require insert size of at least this for overlap.
                    Should be reduced to 16 for small RNA sequencing.
tpe=f               (trimpairsevenly) When kmer right-trimming, trim both 
                    reads to the minimum length of either.
forcetrimleft=0     (ftl) If positive, trim bases to the left of this position
                    (exclusive, 0-based).
forcetrimright=0    (ftr) If positive, trim bases to the right of this position
                    (exclusive, 0-based).
forcetrimright2=0   (ftr2) If positive, trim this many bases on the right end.
forcetrimmod=0      (ftm) If positive, right-trim length to be equal to zero,
                    modulo this number.
restrictleft=0      If positive, only look for kmer matches in the 
                    leftmost X bases.
restrictright=0     If positive, only look for kmer matches in the 
                    rightmost X bases.
NOTE:  restrictleft and restrictright are mutually exclusive.  If trimming
       both ends is desired, use ktrimtips.
mingc=0             Discard reads with GC content below this.
maxgc=1             Discard reads with GC content above this.
gcpairs=t           Use average GC of paired reads.
                    Also affects gchist.
tossjunk=f          Discard reads with invalid characters as bases.
swift=f             Trim Swift sequences: Trailing C/T/N R1, leading G/A/N R2.

Header-parsing parameters - these require Illumina headers:
chastityfilter=f    (cf) Discard reads with id containing ' 1:Y:' or ' 2:Y:'.
barcodefilter=f     Remove reads with unexpected barcodes if barcodes is set,
                    or barcodes containing 'N' otherwise.  A barcode must be
                    the last part of the read header.  Values:
                       t:     Remove reads with bad barcodes.
                       f:     Ignore barcodes.
                       crash: Crash upon encountering bad barcodes.
barcodes=           Comma-delimited list of barcodes or files of barcodes.
xmin_file=-1             If positive, discard reads with a lesser X coordinate.
ymin_file=-1             If positive, discard reads with a lesser Y coordinate.
xmax=-1             If positive, discard reads with a greater X coordinate.
ymax=-1             If positive, discard reads with a greater Y coordinate.

Polymer trimming:
trimpolya=0         If greater than 0, trim poly-A or poly-T tails of
                    at least this length on either end of reads.
trimpolygleft=0     If greater than 0, trim poly-G prefixes of at least this
                    length on the left end of reads.  Does not trim poly-C.
trimpolygright=0    If greater than 0, trim poly-G tails of at least this 
                    length on the right end of reads.  Does not trim poly-C.
trimpolyg=0         This sets both left and right at once.
filterpolyg=0       If greater than 0, remove reads with a poly-G prefix of
                    at least this length (on the left).
Note: there are also equivalent poly-C flags.

Polymer tracking:
pratio=base,base    'pratio=G,C' will print the ratio of G to C polymers.
plen=20             Length of homopolymers to count.

Entropy/Complexity parameters:
entropy=-1          Set between 0 and 1 to filter reads with entropy below
                    that value.  Higher is more stringent.
entropywindow=50    Calculate entropy using a sliding window of this length.
entropyk=5          Calculate entropy using kmers of this length.
minbasefrequency=0  Discard reads with a minimum base frequency below this.
entropytrim=f       Values:
                       f:  (false) Do not entropy-trim.
                       r:  (right) Trim low entropy on the right end only.
                       l:  (left) Trim low entropy on the left end only.
                       rl: (both) Trim low entropy on both ends.
entropymask=f       Values:
                       f:  (filter) Discard low-entropy sequences.
                       t:  (true) Mask low-entropy parts of sequences with N.
                       lc: Change low-entropy parts of sequences to lowercase.
entropymark=f       Mark each base with its entropy value.  This is on a scale
                    of 0-41 and is reported as quality scores, so the output
                    should be fastq or fasta+qual.
NOTE: If set, entropytrim overrides entropymask.

Cardinality estimation:
cardinality=f       (loglog) Count unique kmers using the LogLog algorithm.
cardinalityout=f    (loglogout) Count unique kmers in output reads.
loglogk=31          Use this kmer length for counting.
loglogbuckets=2048  Use this many buckets for counting.
khist=<file>        Kmer frequency histogram; plots number of kmers versus
                    kmer depth.  This is approximate.
khistout=<file>     Kmer frequency histogram for output reads.

Side Channel:
sideout=<file>      Output for aligned reads.
sideref=phix        Reference for side-channel alignment; must be a single
                    sequence and virtually repeat-free at selected k.
sidek1=17           Kmer length for seeding alignment to reference.
sidek2=13           Kmer length for seeding alignment of unaligned reads
                    with an aligned mate.
sideminid1=0.66     Minimum identity to accept individual alignments.
sideminid2=0.58     Minimum identity for aligning reads with aligned mates.
sidemm1=1           Middle mask length for sidek1.
sidemm2=1           Middle mask length for sidek2.
Note:  The side channel is a special additional output that allows alignment
to a secondary reference while also doing trimming.  Alignment does not affect
whether reads go to the normal outputs (out, outm).  The main purpose is to
simplify pipelines that need trimmed, aligned phiX reads for recalibration.


Java Parameters:

-Xmx                This will set Java's memory usage, overriding autodetection.
                    -Xmx20g will 
                    specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.  
                    The max is typically 85% of physical memory.
-eoom               This flag will cause the process to exit if an 
                    out-of-memory exception occurs.  Requires Java 8u92+.
-da                 Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for bbduk.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("bbduk.sh", args, capture_output)

def bbest(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for bbest.sh

    Help message:
    Written by Brian Bushnell
Last modified November 4, 2015

Description:  Calculates EST (expressed sequence tags) capture by an assembly from a sam file.
Designed to use BBMap output generated with these flags: k=13 maxindel=100000 customtag ordered

Usage:        bbest.sh in_file=<sam file> out=<stats file>

Parameters:
in_file=<file>       Specify a sam file (or stdin) containing mapped ests.
out=<file>      Specify the output stats file (default is stdout).
ref=<file>      Specify the reference file (optional).
est=<file>      Specify the est fasta file (optional).
fraction=0.98   Min fraction of bases mapped to ref to be 
                considered 'all mapped'.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for bbest.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("bbest.sh", args, capture_output)

def bbfakereads(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for bbfakereads.sh

    Help message:
    Written by Brian Bushnell
Last modified February 17, 2015

Description:  Generates fake read pairs from ends of contigs or single reads.
Specifically for simulating a fake LMP library from long reads or an assembly;
for synthetic read generation from a reference see randomreads.sh or randomreadsmg.sh.

Usage:        bbfakereads.sh in_file=<file> out=<outfile> out2=<outfile2>

Out2 is optional; if there is only one output file, it will be written interleaved.

Standard parameters:
ow=f                (overwrite) Overwrites files that already exist.
zl=4                (ziplevel) Set compression level, 1 (low) to 9 (max).
fastawrap=100       Length of lines in fasta output.
tuc=f               (touppercase) Change lowercase letters in reads to uppercase.
qin_file=auto            ASCII offset for input quality.  May be 33 (Sanger), 64 (Illumina), or auto.
qout=auto           ASCII offset for output quality.  May be 33 (Sanger), 64 (Illumina), or auto (same as input).
qfin_file=<.qual file>   Read qualities from this qual file, for the reads coming from 'in_file=<fasta file>'
qfout=<.qual file>  Write qualities from this qual file, for the reads going to 'out=<fasta file>'
qfout2=<.qual file> Write qualities from this qual file, for the reads coming from 'out2=<fasta file>'
verifyinterleaved=f (vint) When true, checks a file to see if the names look paired.  Prints an error message if not.
tossbrokenreads=f   (tbr) Discard reads that have different numbers of bases and qualities.  By default this will be detected and cause a crash.

Faking parameters:
length=250          Generate reads of this length.
minlength=1         Don't generate reads shorter than this.
overlap=0           If you set overlap, then reads will by variable length, overlapping by 'overlap' in the middle.
identifier=null     (id) Output read names are prefixed with this.
addspace=t          Set to false to omit the  space before /1 and /2 of paired reads.

Java Parameters:
-Xmx                This will set Java's memory usage, overriding autodetection.
                    -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom               This flag will cause the process to exit if an
                    out-of-memory exception occurs.  Requires Java 8u92+.
-da                 Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for bbfakereads.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("bbfakereads.sh", args, capture_output)

def bbmap(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for bbmap.sh

    Help message:
    BBMap
Written by Brian Bushnell, from Dec. 2010 - present
Last modified September 15, 2022

Description:  Fast and accurate splice-aware read aligner.
Please read bbmap/docs/guides/BBMapGuide.txt for more information.

To index:     bbmap.sh ref=<reference fasta>
To map:       bbmap.sh in_file=<reads> out=<output sam>
To map without writing an index:
    bbmap.sh ref=<reference fasta> in_file=<reads> out=<output sam> nodisk

in_file=stdin will accept reads from standard in, and out=stdout will write to 
standard out, but file extensions are still needed to specify the format of the 
input and output files e.g. in_file=stdin.fa.gz will read gzipped fasta from 
standard in; out=stdout.sam.gz will write gzipped sam.

Indexing Parameters (required when building the index):
nodisk=f                Set to true to build index in memory and write nothing 
                        to disk except output.
ref=<file>              Specify the reference sequence.  Only do this ONCE, 
                        when building the index (unless using 'nodisk').
build=1                 If multiple references are indexed in the same directory,
                        each needs a unique numeric ID (unless using 'nodisk').
k=13                    Kmer length, range 8-15.  Longer is faster but uses 
                        more memory.  Shorter is more sensitive.
                        If indexing and mapping are done in two steps, K should
                        be specified each time.
path=<.>                Specify the location to write the index, if you don't 
                        want it in the current working directory.
usemodulo=f             Throw away ~80% of kmers based on remainder modulo a 
                        number (reduces RAM by 50% and sensitivity slightly).
                        Should be enabled both when building the index AND 
                        when mapping.
rebuild=f               Force a rebuild of the index (ref= should be set).

Input Parameters:
build=1                 Designate index to use.  Corresponds to the number 
                        specified when building the index.
in_file=<file>               Primary reads input; required parameter.
in2=<file>              For paired reads in two files.
interleaved=auto        True forces paired/interleaved input; false forces 
                        single-ended mapping. If not specified, interleaved 
                        status will be autodetected from read names.
fastareadlen=500        Break up FASTA reads longer than this.  Max is 500 for
                        BBMap and 6000 for BBMapPacBio.  Only works for FASTA
                        input (use 'maxlen' for FASTQ input).  The default for
                        bbmap.sh is 500, and for mapPacBio.sh is 6000.
unpigz=f                Spawn a pigz (parallel gzip) process for faster 
                        decompression than using Java.  
                        Requires pigz to be installed.
touppercase=t           (tuc) Convert lowercase letters in reads to upper case 
                        (otherwise they will not match the reference).

Sampling Parameters:

reads=-1                Set to a positive number N to only process the first N
                        reads (or pairs), then quit.  -1 means use all reads.
samplerate=1            Set to a number from 0 to 1 to randomly select that
                        fraction of reads for mapping. 1 uses all reads.
skipreads=0             Set to a number N to skip the first N reads (or pairs), 
                        then map the rest.

Mapping Parameters:
fast=f                  This flag is a macro which sets other paramters to run 
                        faster, at reduced sensitivity.  Bad for RNA-seq.
slow=f                  This flag is a macro which sets other paramters to run 
                        slower, at greater sensitivity.  'vslow' is even slower.
maxindel=16000          Don't look for indels longer than this. Lower is faster.
                        Set to >=100k for RNAseq with long introns like mammals.
strictmaxindel=f        When enabled, do not allow indels longer than 'maxindel'.
                        By default these are not sought, but may be found anyway.
tipsearch=100           Look this far for read-end deletions with anchors
                        shorter than K, using brute force.
minid=0.76              Approximate minimum alignment identity to look for. 
                        Higher is faster and less sensitive.
minhits=1               Minimum number of seed hits required for candidate sites.
                        Higher is faster.
local=f                 Set to true to use local, rather than global, alignments.
                        This will soft-clip ugly ends of poor alignments.
perfectmode=f           Allow only perfect mappings when set to true (very fast).
semiperfectmode=f       Allow only perfect and semiperfect (perfect except for 
                        N's in the reference) mappings.
threads=auto            (t) Set to number of threads desired.  By default, uses 
                        all cores available.
ambiguous=best          (ambig) Set behavior on ambiguously-mapped reads (with 
                        multiple top-scoring mapping locations).
                            best    (use the first best site)
                            toss    (consider unmapped)
                            random  (select one top-scoring site randomly)
                            all     (retain all top-scoring sites)
samestrandpairs=f       (ssp) Specify whether paired reads should map to the
                        same strand or opposite strands.
requirecorrectstrand=t  (rcs) Forbid pairing of reads without correct strand 
                        orientation.  Set to false for long-mate-pair libraries.
killbadpairs=f          (kbp) If a read pair is mapped with an inappropriate
                        insert size or orientation, the read with the lower  
                        mapping quality is marked unmapped.
pairedonly=f            (po) Treat unpaired reads as unmapped.  Thus they will 
                        be sent to 'outu' but not 'outm'.
rcomp=f                 Reverse complement both reads prior to mapping (for LMP
                        outward-facing libraries).
rcompmate=f             Reverse complement read2 prior to mapping.
pairlen=32000           Set max allowed distance between paired reads.  
                        (insert size)=(pairlen)+(read1 length)+(read2 length)
rescuedist=1200         Don't try to rescue paired reads if avg. insert size
                        greater than this.  Lower is faster.
rescuemismatches=32     Maximum mismatches allowed in a rescued read.  Lower
                        is faster.
averagepairdist=100     (apd) Initial average distance between paired reads.
                        Varies dynamically; does not need to be specified.
deterministic=f         Run in deterministic mode.  In this case it is good
                        to set averagepairdist.  BBMap is deterministic
                        without this flag if using single-ended reads,
                        or run singlethreaded.
bandwidthratio=0        (bwr) If above zero, restrict alignment band to this 
                        fraction of read length.  Faster but less accurate.
bandwidth=0             (bw) Set the bandwidth directly.
                        fraction of read length.  Faster but less accurate.
usejni=f                (jni) Do alignments faster, in C code.  Requires 
                        compiling the C code; details are in /jni/README.txt.
maxsites2=800           Don't analyze (or print) more than this many alignments 
                        per read.
ignorefrequentkmers=t   (ifk) Discard low-information kmers that occur often.
excludefraction=0.03    (ef) Fraction of kmers to ignore.  For example, 0.03
                        will ignore the most common 3% of kmers.
greedy=t                Use a greedy algorithm to discard the least-useful
                        kmers on a per-read basis.
kfilter=0               If positive, potential mapping sites must have at
                        least this many consecutive exact matches.


Quality and Trimming Parameters:
qin_file=auto                Set to 33 or 64 to specify input quality value ASCII
                        offset. 33 is Sanger, 64 is old Solexa.
qout=auto               Set to 33 or 64 to specify output quality value ASCII 
                        offset (only if output format is fastq).
qtrim=f                 Quality-trim ends before mapping.  Options are: 
                        'f' (false), 'l' (left), 'r' (right), and 'lr' (both).
untrim=f                Undo trimming after mapping.  Untrimmed bases will be 
                        soft-clipped in cigar strings.
trimq=6                 Trim regions with average quality below this 
                        (phred algorithm).
mintrimlength=60        (mintl) Don't trim reads to be shorter than this.
fakefastaquality=-1     (ffq) Set to a positive number 1-50 to generate fake
                        quality strings for fasta input reads.
ignorebadquality=f      (ibq) Keep going, rather than crashing, if a read has 
                        out-of-range quality values.
usequality=t            Use quality scores when determining which read kmers
                        to use as seeds.
minaveragequality=0     (maq) Do not map reads with average quality below this.
maqb=0                  If positive, calculate maq from this many initial bases.

Output Parameters:
out=<file>              Write all reads to this file.
outu=<file>             Write only unmapped reads to this file.  Does not 
                        include unmapped paired reads with a mapped mate.
outm=<file>             Write only mapped reads to this file.  Includes 
                        unmapped paired reads with a mapped mate.
mappedonly=f            If true, treats 'out' like 'outm'.
bamscript=<file>        (bs) Write a shell script to <file> that will turn 
                        the sam output into a sorted, indexed bam file.
ordered=f               Set to true to output reads in same order as input.  
                        Slower and uses more memory.
overwrite=f             (ow) Allow process to overwrite existing files.
secondary=f             Print secondary alignments.
sssr=0.95               (secondarysitescoreratio) Print only secondary alignments
                        with score of at least this fraction of primary.
ssao=f                  (secondarysiteasambiguousonly) Only print secondary 
                        alignments for ambiguously-mapped reads.
maxsites=5              Maximum number of total alignments to print per read.
                        Only relevant when secondary=t.
quickmatch=f            Generate cigar strings more quickly.
trimreaddescriptions=f  (trd) Truncate read and ref names at the first whitespace,
                        assuming that the remainder is a comment or description.
ziplevel=2              (zl) Compression level for zip or gzip output.
pigz=f                  Spawn a pigz (parallel gzip) process for faster 
                        compression than Java.  Requires pigz to be installed.
machineout=f            Set to true to output statistics in machine-friendly 
                        'key=value' format.
printunmappedcount=f    Print the total number of unmapped reads and bases.
                        If input is paired, the number will be of pairs
                        for which both reads are unmapped.
showprogress=0          If positive, print a '.' every X reads.
showprogress2=0         If positive, print the number of seconds since the
                        last progress update (instead of a '.').
renamebyinsert=f        Renames reads based on their mapped insert size.

Bloom-Filtering Parameters (bloomfilter.sh is the standalone version).
bloom=f                 Use a Bloom filter to ignore reads not sharing kmers
                        with the reference.  This uses more memory, but speeds
                        mapping when most reads don't match the reference.
bloomhashes=2           Number of hash functions.
bloomminhits=3          Number of consecutive hits to be considered matched.
bloomk=31               Bloom filter kmer length.
bloomserial=t           Use the serialized Bloom filter for greater loading
                        speed, if available.  If not, generate and write one.

Post-Filtering Parameters:
idfilter=0              Independant of minid; sets exact minimum identity 
                        allowed for alignments to be printed.  Range 0 to 1.
subfilter=-1            Ban alignments with more than this many substitutions.
insfilter=-1            Ban alignments with more than this many insertions.
delfilter=-1            Ban alignments with more than this many deletions.
indelfilter=-1          Ban alignments with more than this many indels.
editfilter=-1           Ban alignments with more than this many edits.
inslenfilter=-1         Ban alignments with an insertion longer than this.
dellenfilter=-1         Ban alignments with a deletion longer than this.
nfilter=-1              Ban alignments with more than this many ns.  This 
                        includes nocall, noref, and off scaffold ends.

Sam flags and settings:
noheader=f              Disable generation of header lines.
sam=1.4                 Set to 1.4 to write Sam version 1.4 cigar strings, 
                        with = and X, or 1.3 to use M.
saa=t                   (secondaryalignmentasterisks) Use asterisks instead of
                        bases for sam secondary alignments.
cigar=t                 Set to 'f' to skip generation of cigar strings (faster).
keepnames=f             Keep original names of paired reads, rather than 
                        ensuring both reads have the same name.
intronlen=999999999     Set to a lower number like 10 to change 'D' to 'N' in 
                        cigar strings for deletions of at least that length.
rgid=                   Set readgroup ID.  All other readgroup fields 
                        can be set similarly, with the flag rgXX=
                        If you set a readgroup flag to the word 'filename',
                        e.g. rgid=filename, the input file name will be used.
mdtag=f                 Write MD tags.
nhtag=f                 Write NH tags.
xmtag=f                 Write XM tags (may only work correctly with ambig=all).
amtag=f                 Write AM tags.
nmtag=f                 Write NM tags.
xstag=f                 Set to 'xs=fs', 'xs=ss', or 'xs=us' to write XS tags 
                        for RNAseq using firststrand, secondstrand, or 
                        unstranded libraries.  Needed by Cufflinks.  
                        JGI mainly uses 'firststrand'.
stoptag=f               Write a tag indicating read stop location, prefixed by YS:i:
lengthtag=f             Write a tag indicating (query,ref) alignment lengths, 
                        prefixed by YL:Z:
idtag=f                 Write a tag indicating percent identity, prefixed by YI:f:
inserttag=f             Write a tag indicating insert size, prefixed by X8:Z:
scoretag=f              Write a tag indicating BBMap's raw score, prefixed by YR:i:
timetag=f               Write a tag indicating this read's mapping time, prefixed by X0:i:
boundstag=f             Write a tag indicating whether either read in the pair
                        goes off the end of the reference, prefixed by XB:Z:
notags=f                Turn off all optional tags.

Histogram and statistics output parameters:
scafstats=<file>        Statistics on how many reads mapped to which scaffold.
refstats=<file>         Statistics on how many reads mapped to which reference
                        file; only for BBSplit.
sortscafs=t             Sort scaffolds or references by read count.
bhist=<file>            Base composition histogram by position.
qhist=<file>            Quality histogram by position.
aqhist=<file>           Histogram of average read quality.
bqhist=<file>           Quality histogram designed for box plots.
lhist=<file>            Read length histogram.
ihist=<file>            Write histogram of insert sizes (for paired reads).
ehist=<file>            Errors-per-read histogram.
qahist=<file>           Quality accuracy histogram of error rates versus 
                        quality score.
indelhist=<file>        Indel length histogram.
mhist=<file>            Histogram of match, sub, del, and ins rates by 
                        read location.
gchist=<file>           Read GC content histogram.
gcbins=100              Number gchist bins.  Set to 'auto' to use read length.
gcpairs=t               Use average GC of paired reads.
idhist=<file>           Histogram of read count versus percent identity.
idbins=100              Number idhist bins.  Set to 'auto' to use read length.
statsfile=stderr        Mapping statistics are printed here.

Coverage output parameters (these may reduce speed and use more RAM):
covstats=<file>         Per-scaffold coverage info.
rpkm=<file>             Per-scaffold RPKM/FPKM counts.
covhist=<file>          Histogram of # occurrences of each depth level.
basecov=<file>          Coverage per base location.
bincov=<file>           Print binned coverage per location (one line per X bases).
covbinsize=1000         Set the binsize for binned coverage output.
nzo=t                   Only print scaffolds with nonzero coverage.
twocolumn=f             Change to true to print only ID and Avg_fold instead of 
                        all 6 columns to the 'out=' file.
32bit=f                 Set to true if you need per-base coverage over 64k.
strandedcov=f           Track coverage for plus and minus strand independently.
startcov=f              Only track start positions of reads.
secondarycov=t          Include coverage of secondary alignments.
physcov=f               Calculate physical coverage for paired reads.
                        This includes the unsequenced bases.
delcoverage=t           (delcov) Count bases covered by deletions as covered.
                        True is faster than false.
covk=0                  If positive, calculate kmer coverage statistics.

Java Parameters:
-Xmx                    This will set Java's memory usage, 
                        overriding autodetection.
                        -Xmx20g will specify 20 gigs of RAM, and -Xmx800m 
                        will specify 800 megs.  The max is typically 85% of 
                        physical memory.  The human genome requires around 24g,
                        or 12g with the 'usemodulo' flag.  The index uses 
                        roughly 6 bytes per reference base.
-eoom                   This flag will cause the process to exit if an 
                        out-of-memory exception occurs.  Requires Java 8u92+.
-da                     Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter 
any problems, or post at: http://seqanswers.com/forums/showthread.php?t=41057

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for bbmap.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("bbmap.sh", args, capture_output)

def bbmapskimmer(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for bbmapskimmer.sh

    Help message:
    No help message found.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for bbmapskimmer.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("bbmapskimmer.sh", args, capture_output)

def bbmask(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for bbmask.sh

    Help message:
    Written by Brian Bushnell
Last modified October 17, 2017

Description:  Masks sequences of low-complexity, or containing repeat kmers, or covered by mapped reads.
By default this program will mask using entropy with a window=80 and entropy=0.75
Please read bbmap/docs/guides/BBMaskGuide.txt for more information.

Usage:   bbmask.sh in_file=<file> out=<file> sam=<file,file,...file>

Input may be stdin or a fasta or fastq file, raw or gzipped.
sam is optional, but may be a comma-delimited list of sam files to mask.
Sam files may also be used as arguments without sam=, so you can use *.sam for example.
If you pipe via stdin/stdout, please include the file type; e.g. for gzipped fasta input, set in_file=stdin.fa.gz

Input parameters:
in_file=<file>           Input sequences to mask. 'in_file=stdin.fa' will pipe from standard in.
sam=<file,file>     Comma-delimited list of sam files.  Optional.  Their mapped coordinates will be masked.
touppercase=f       (tuc) Change all letters to upper-case.
interleaved=auto    (int) If true, forces fastq input to be paired and interleaved.
qin_file=auto            ASCII offset for input quality.  May be 33 (Sanger), 64 (Illumina), or auto.

Output parameters:
out=<file>          Write masked sequences here.  'out=stdout.fa' will pipe to standard out.
overwrite=t         (ow) Set to false to force the program to abort rather than overwrite an existing file.
ziplevel=2          (zl) Set to 1 (lowest) through 9 (max) to change compression level; lower compression is faster.
fastawrap=70        Length of lines in fasta output.
qout=auto           ASCII offset for output quality.  May be 33 (Sanger), 64 (Illumina), or auto (same as input).

Processing parameters:
threads=auto        (t) Set number of threads to use; default is number of logical processors.
maskrepeats=f       (mr) Mask areas covered by exact repeat kmers.
kr=5                Kmer size to use for repeat detection (1-15).  Use minkr and maxkr to sweep a range of kmers.
minlen=40           Minimum length of repeat area to mask.
mincount=4          Minimum number of repeats to mask.
masklowentropy=t    (mle) Mask areas with low complexity by calculating entropy over a window for a fixed kmer size.
ke=5                Kmer size to use for entropy calculation (1-15).  Use minke and maxke to sweep a range.  Large ke uses more memory.
window=80           (w) Window size for entropy calculation.
entropy=0.70        (e) Mask windows with entropy under this value (0-1).  0.0001 will mask only homopolymers and 1 will mask everything.
lowercase=f         (lc) Convert masked bases to lower case.  Default is to convert them to N.
split=f             Split into unmasked pieces and discard masked pieces.

Coverage parameters (only relevant if sam files are specified):
mincov=-1           If nonnegative, mask bases with coverage outside this range.
maxcov=-1           If nonnegative, mask bases with coverage outside this range.
delcov=t            Include deletions when calculating coverage.
NOTE: If neither mincov nor maxcov are set, all covered bases will be masked.

Other parameters:
pigz=t              Use pigz to compress.  If argument is a number, that will set the number of pigz threads.
unpigz=t            Use pigz to decompress.

Java Parameters:
-Xmx                This will set Java's memory usage, overriding autodetection.
                    -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom               This flag will cause the process to exit if an
                    out-of-memory exception occurs.  Requires Java 8u92+.
-da                 Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for bbmask.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("bbmask.sh", args, capture_output)

def bbmerge(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for bbmerge.sh

    Help message:
    Written by Brian Bushnell and Jonathan Rood
Last modified October 8, 2024

Description:  Merges paired reads into single reads by overlap detection.
With sufficient coverage, can merge nonoverlapping reads by kmer extension.
Kmer modes (Tadpole or Bloom Filter) require much more memory, and should
be used with the bbmerge-auto.sh script rather than bbmerge.sh.
Please read bbmap/docs/guides/BBMergeGuide.txt for more information.

Usage for interleaved files:	bbmerge.sh in_file=<reads> out=<merged reads> outu=<unmerged reads>
Usage for paired files:     	bbmerge.sh in1=<read1> in2=<read2> out=<merged reads> outu1=<unmerged1> outu2=<unmerged2>

Input may be stdin or a file, fasta or fastq, raw or gzipped.

Input parameters:
in_file=null              Primary input. 'in2' will specify a second file.
interleaved=auto     May be set to true or false to override autodetection of
                     whether the input file as interleaved.
reads=-1             Quit after this many read pairs (-1 means all).

Output parameters:
out=<file>           File for merged reads. 'out2' will specify a second file.
outu=<file>          File for unmerged reads. 'outu2' will specify a second file.
outinsert=<file>     (outi) File to write read names and insert sizes.
outadapter=<file>    (outa) File to write consensus adapter sequences.
outc=<file>          File to write input read kmer cardinality estimate.
ihist=<file>         (hist) Insert length histogram output file.
nzo=t                Only print histogram bins with nonzero values.
showhiststats=t      Print extra header lines with statistical information.
ziplevel=2           Set to 1 (lowest) through 9 (max) to change compression
                     level; lower compression is faster.
ordered=f            Output reads in same order as input.
mix=f                Output both the merged (or mergable) and unmerged reads
                     in the same file (out=).  Useful for ecco mode.

Trimming/Filtering parameters:
qtrim=f              Trim read ends to remove bases with quality below minq.
                     Trims BEFORE merging.
                     Values: t (trim both ends), 
                             f (neither end), 
                             r (right end only), 
                             l (left end only).
qtrim2=f             May be specified instead of qtrim to perform trimming 
                     only if merging is unsuccessful, then retry merging.
trimq=10             Trim quality threshold.  This may be a comma-delimited
                     list (ascending) to try multiple values.
minlength=1          (ml) Reads shorter than this after trimming, but before
                     merging, will be discarded. Pairs will be discarded only
                     if both are shorter.
maxlength=-1         Reads with longer insert sizes will be discarded.
tbo=f                (trimbyoverlap) Trim overlapping reads to remove 
                     rightmost (3') non-overlapping portion, instead of joining.
minavgquality=0      (maq) Reads with average quality below this, after 
                     trimming, will not be attempted to be merged.
maxexpectederrors=0  (mee) If positive, reads with more combined expected 
                     errors than this will not be attempted to be merged.
forcetrimleft=0      (ftl) If nonzero, trim left bases of the read to 
                     this position (exclusive, 0-based).
forcetrimright=0     (ftr) If nonzero, trim right bases of the read 
                     after this position (exclusive, 0-based).
forcetrimright2=0    (ftr2) If positive, trim this many bases on the right end.
forcetrimmod=5       (ftm) If positive, trim length to be equal to 
                     zero modulo this number.
ooi=f                Output only incorrectly merged reads, for testing.
trimpolya=t          Trim trailing poly-A tail from adapter output.  Only 
                     affects outadapter.  This also trims poly-A followed
                     by poly-G, which occurs on NextSeq.

Processing Parameters:
usejni=f             (jni) Do overlapping in C code, which is faster.  Requires
                     compiling the C code; details are in /jni/README.txt.
                     However, the jni path is currently disabled.
merge=t              Create merged reads.  If set to false, you can still 
                     generate an insert histogram.
ecco=f               Error-correct the overlapping part, but don't merge.
trimnonoverlapping=f (tno) Trim all non-overlapping portions, leaving only
                     consensus sequence.  By default, only sequence to the 
                     right of the overlap (adapter sequence) is trimmed.
useoverlap=t         Attempt find the insert size using read overlap.
mininsert=15         Minimum insert size to merge reads.
mininsert0=12        Insert sizes less than this will not be considered.
                     Must be less than or equal to mininsert.
minoverlap=12        Minimum number of overlapping bases to allow merging.
minoverlap0=8        Overlaps shorter than this will not be considered.
                     Must be less than or equal to minoverlap.
minq=9               Ignore bases with quality below this.
maxq=41              Cap output quality scores at this.
quantize=1           Set to a higher number to eliminate some quality scores
                     for a lower output filesize.
entropy=t            Increase the minimum overlap requirement for low-
                     complexity reads.
efilter=6            Ban overlaps with over this many times the expected 
                     number of errors.  Lower is more strict. -1 disables.
pfilter=0.00004      Ban improbable overlaps.  Higher is more strict. 0 will
                     disable the filter; 1 will allow only perfect overlaps.
kfilter=0            Ban overlaps that create kmers with count below
                     this value (0 disables).  If this is used minprob should
                     probably be set to 0.  Requires good coverage.
ouq=f                Calculate best overlap using quality values.
owq=t                Calculate best overlap without using quality values.
usequality=t         If disabled, quality values are completely ignored,
                     both for overlap detection and filtering.  May be useful
                     for data with inaccurate quality values.
iupacton=f           (itn) Change ambiguous IUPAC symbols to N.
adapter=             Specify the adapter sequences used for these reads, if
                     known; this can be a fasta file or a literal sequence.
                     Read 1 and 2 can have adapters specified independently
                     with the adapter1 and adapter2 flags.  adapter=default
                     will use a list of common adapter sequences.

Neural Network Mode:
nn=t                 Use a neural network for increased merging accuracy.
                     This is highly recommended, but will conflict with
                     strictness and ratiomode flags.  Stringency in nn mode
                     should be adjusted via the cutoff flag instead.
cutoff=0.872857      Merge reads with nn score above this value. Lower will
                     increase the merge rate at the cost of false positives.
net=<file>           Optional network to specify (for developer use); the
                     default is bbmap/resources/bbmerge.bbnet.

Ratio Mode: 
ratiomode=t          Score overlaps based on the ratio of matching to 
                     mismatching bases.
maxratio=0.09        Max error rate; higher increases merge rate.
ratiomargin_file=5.5      Lower increases merge rate; min is 1.
ratiooffset=0.55     Lower increases merge rate; min is 0.
maxmismatches=20     Maximum mismatches allowed in overlapping region.
ratiominoverlapreduction=3  This is the difference between minoverlap in 
                     flat mode and minoverlap in ratio mode; generally, 
                     minoverlap should be lower in ratio mode.
minsecondratio=0.1   Cutoff for second-best overlap ratio.
forcemerge=f         Disable all filters and just merge everything 
                     (not recommended).

Strictness (these are mutually exclusive macros that set other parameters):
strict=f             Decrease false positive rate and merging rate.
verystrict=f         (vstrict) Greatly decrease FP and merging rate.
ultrastrict=f        (ustrict) Decrease FP and merging rate even more.
maxstrict=f          (xstrict) Maximally decrease FP and merging rate.
loose=f              Increase false positive rate and merging rate.
veryloose=f          (vloose) Greatly increase FP and merging rate.
ultraloose=f         (uloose) Increase FP and merging rate even more.
maxloose=f           (xloose) Maximally decrease FP and merging rate.
fast=f               Fastest possible mode; less accurate.

Tadpole Parameters (for read extension and error-correction):
*Note: These require more memory and should be run with bbmerge-auto.sh.*
k=31                 Kmer length.  31 (or less) is fastest and uses the least
                     memory, but higher values may be more accurate.  
                     60 tends to work well for 150bp reads.
extend=0             Extend reads to the right this much before merging.
                     Requires sufficient (>5x) kmer coverage.
extend2=0            Extend reads this much only after a failed merge attempt,
                     or in rem/rsem mode.
iterations=1         (ei) Iteratively attempt to extend by extend2 distance
                     and merge up to this many times.
rem=f                (requireextensionmatch) Do not merge if the predicted
                     insert size differs before and after extension.
                     However, if only the extended reads overlap, then that
                     insert will be used.  Requires setting extend2.
rsem=f               (requirestrictextensionmatch) Similar to rem but stricter.
                     Reads will only merge if the predicted insert size before
                     and after extension match.  Requires setting extend2.
                     Enables the lowest possible false-positive rate.
ecctadpole=f         (ecct) If reads fail to merge, error-correct with Tadpole
                     and try again.  This happens prior to extend2.
reassemble=t         If ecct is enabled, use Tadpole's reassemble mode for 
                     error correction.  Alternatives are pincer and tail.
removedeadends       (shave) Remove kmers leading to dead ends.
removebubbles        (rinse) Remove kmers in error bubbles.
mindepthseed=3       (mds) Minimum kmer depth to begin extension.
mindepthextend=2     (mde) Minimum kmer depth continue extension.
branchmult1=20       Min ratio of 1st to 2nd-greatest path depth at high depth.
branchmult2=3        Min ratio of 1st to 2nd-greatest path depth at low depth.
branchlower=3        Max value of 2nd-greatest path depth to be considered low.
ibb=t                Ignore backward branches when extending.
extra=<file>         A file or comma-delimited list of files of reads to use
                     for kmer counting, but not for merging or output.
prealloc=f           Pre-allocate memory rather than dynamically growing; 
                     faster and more memory-efficient for large datasets.  
                     A float fraction (0-1) may be specified, default 1.
prefilter=0          If set to a positive integer, use a countmin sketch to 
                     ignore kmers with depth of that value or lower, to
                     reduce memory usage.
filtermem=0          Allows manually specifying prefilter memory in bytes, for
                     deterministic runs.  0 will set it automatically.
minprob=0.5          Ignore kmers with overall probability of correctness 
                     below this, to reduce memory usage.
minapproxoverlap=26  For rem mode, do not merge reads if the extended reads
                     indicate that the raw reads should have overlapped by
                     at least this much, but no overlap was found.


Bloom Filter Parameters (for kmer operations with less memory than Tadpole)
*Note: These require more memory and should be run with bbmerge-auto.sh.*
eccbloom=f           (eccb) If reads fail to merge, error-correct with bbcms
                     and try again.
testmerge=f          Test kmer counts around the read merge junctions.  If
                     it appears that the merge created new errors, undo it.
                     This reduces the false-positive rate, but not as much as
                     rem or rsem.

Java Parameters:
-Xmx                 This will set Java's memory usage, 
                     overriding autodetection.
                     For example, -Xmx400m will specify 400 MB RAM.
-eoom                This flag will cause the process to exit if an 
                     out-of-memory exception occurs.  Requires Java 8u92+.
-da                  Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for bbmerge.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("bbmerge.sh", args, capture_output)

def bbnorm(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for bbnorm.sh

    Help message:
    Written by Brian Bushnell
Last modified October 19, 2017

Description:  Normalizes read depth based on kmer counts.
Can also error-correct, bin reads by kmer depth, and generate a kmer depth histogram.
However, Tadpole has superior error-correction to BBNorm.
Please read bbmap/docs/guides/BBNormGuide.txt for more information.

Usage:     bbnorm.sh in_file=<input> out=<reads to keep> outt=<reads to toss> hist=<histogram output>

Input parameters:
in_file=null             Primary input.  Use in2 for paired reads in a second file
in2=null            Second input file for paired reads in two files
extra=null          Additional files to use for input (generating hash table) but not for output
fastareadlen=2^31   Break up FASTA reads longer than this.  Can be useful when processing scaffolded genomes
tablereads=-1       Use at most this many reads when building the hashtable (-1 means all)
kmersample=1        Process every nth kmer, and skip the rest
readsample=1        Process every nth read, and skip the rest
interleaved=auto    May be set to true or false to force the input read file to ovverride autodetection of the input file as paired interleaved.
qin_file=auto            ASCII offset for input quality.  May be 33 (Sanger), 64 (Illumina), or auto.

Output parameters:
out=<file>          File for normalized or corrected reads.  Use out2 for paired reads in a second file
outt=<file>         (outtoss) File for reads that were excluded from primary output
reads=-1            Only process this number of reads, then quit (-1 means all)
sampleoutput=t      Use sampling on output as well as input (not used if sample rates are 1)
keepall=f           Set to true to keep all reads (e.g. if you just want error correction).
zerobin_file=f           Set to true if you want kmers with a count of 0 to go in the 0 bin instead of the 1 bin in histograms.
                    Default is false, to prevent confusion about how there can be 0-count kmers.
                    The reason is that based on the 'minq' and 'minprob' settings, some kmers may be excluded from the bloom filter.
tmpdir=$TMPDIR      This will specify a directory for temp files (only needed for multipass runs).  If null, they will be written to the output directory.
usetempdir=t        Allows enabling/disabling of temporary directory; if disabled, temp files will be written to the output directory.
qout=auto           ASCII offset for output quality.  May be 33 (Sanger), 64 (Illumina), or auto (same as input).
rename=f            Rename reads based on their kmer depth.

Hashing parameters:
k=31                Kmer length (values under 32 are most efficient, but arbitrarily high values are supported)
bits=32             Bits per cell in bloom filter; must be 2, 4, 8, 16, or 32.  Maximum kmer depth recorded is 2^cbits.  Automatically reduced to 16 in 2-pass.
                    Large values decrease accuracy for a fixed amount of memory, so use the lowest number you can that will still capture highest-depth kmers.
hashes=3            Number of times each kmer is hashed and stored.  Higher is slower.
                    Higher is MORE accurate if there is enough memory, and LESS accurate if there is not enough memory.
prefilter=f         True is slower, but generally more accurate; filters out low-depth kmers from the main hashtable.  The prefilter is more memory-efficient because it uses 2-bit cells.
prehashes=2         Number of hashes for prefilter.
prefilterbits=2     (pbits) Bits per cell in prefilter.
prefiltersize=0.35  Fraction of memory to allocate to prefilter.
buildpasses=1       More passes can sometimes increase accuracy by iteratively removing low-depth kmers
minq=6              Ignore kmers containing bases with quality below this
minprob=0.5         Ignore kmers with overall probability of correctness below this
threads=auto        (t) Spawn exactly X hashing threads (default is number of logical processors).  Total active threads may exceed X due to I/O threads.
rdk=t               (removeduplicatekmers) When true, a kmer's count will only be incremented once per read pair, even if that kmer occurs more than once.

Normalization parameters:
fixspikes=f         (fs) Do a slower, high-precision bloom filter lookup of kmers that appear to have an abnormally high depth due to collisions.
target=100          (tgt) Target normalization depth.  NOTE:  All depth parameters control kmer depth, not read depth.
                    For kmer depth Dk, read depth Dr, read length R, and kmer size K:  Dr=Dk*(R/(R-K+1))
maxdepth=-1         (max) Reads will not be downsampled when below this depth, even if they are above the target depth.            
mindepth=5          (min) Kmers with depth below this number will not be included when calculating the depth of a read.
minkmers=15         (mgkpr) Reads must have at least this many kmers over min depth to be retained.  Aka 'mingoodkmersperread'.
percentile=54.0     (dp) Read depth is by default inferred from the 54th percentile of kmer depth, but this may be changed to any number 1-100.
uselowerdepth=t     (uld) For pairs, use the depth of the lower read as the depth proxy.
deterministic=t     (dr) Generate random numbers deterministically to ensure identical output between multiple runs.  May decrease speed with a huge number of threads.
passes=2            (p) 1 pass is the basic mode.  2 passes (default) allows greater accuracy, error detection, better contol of output depth.

Error detection parameters:
hdp=90.0            (highdepthpercentile) Position in sorted kmer depth array used as proxy of a read's high kmer depth.
ldp=25.0            (lowdepthpercentile) Position in sorted kmer depth array used as proxy of a read's low kmer depth.
tossbadreads=f      (tbr) Throw away reads detected as containing errors.
requirebothbad=f    (rbb) Only toss bad pairs if both reads are bad.
errordetectratio=125   (edr) Reads with a ratio of at least this much between their high and low depth kmers will be classified as error reads.
highthresh=12       (ht) Threshold for high kmer.  A high kmer at this or above are considered non-error.
lowthresh=3         (lt) Threshold for low kmer.  Kmers at this and below are always considered errors.

Error correction parameters:
ecc=f               Set to true to correct errors.  NOTE: Tadpole is now preferred for ecc as it does a better job.
ecclimit=3          Correct up to this many errors per read.  If more are detected, the read will remain unchanged.
errorcorrectratio=140  (ecr) Adjacent kmers with a depth ratio of at least this much between will be classified as an error.
echighthresh=22     (echt) Threshold for high kmer.  A kmer at this or above may be considered non-error.
eclowthresh=2       (eclt) Threshold for low kmer.  Kmers at this and below are considered errors.
eccmaxqual=127      Do not correct bases with quality above this value.
aec=f               (aggressiveErrorCorrection) Sets more aggressive values of ecr=100, ecclimit=7, echt=16, eclt=3.
cec=f               (conservativeErrorCorrection) Sets more conservative values of ecr=180, ecclimit=2, echt=30, eclt=1, sl=4, pl=4.
meo=f               (markErrorsOnly) Marks errors by reducing quality value of suspected errors; does not correct anything.
mue=t               (markUncorrectableErrors) Marks errors only on uncorrectable reads; requires 'ecc=t'.
overlap=f           (ecco) Error correct by read overlap.

Depth binning parameters:
lowbindepth=10      (lbd) Cutoff for low depth bin.
highbindepth=80     (hbd) Cutoff for high depth bin.
outlow=<file>       Pairs in which both reads have a median below lbd go into this file.
outhigh=<file>      Pairs in which both reads have a median above hbd go into this file.
outmid=<file>       All other pairs go into this file.

Histogram parameters:
hist=<file>         Specify a file to write the input kmer depth histogram.
histout=<file>      Specify a file to write the output kmer depth histogram.
histcol=3           (histogramcolumns) Number of histogram columns, 2 or 3.
pzc=f               (printzerocoverage) Print lines in the histogram with zero coverage.
histlen=1048576     Max kmer depth displayed in histogram.  Also affects statistics displayed, but does not affect normalization.

Peak calling parameters:
peaks=<file>        Write the peaks to this file.  Default is stdout.
minHeight=2         (h) Ignore peaks shorter than this.
minVolume=5         (v) Ignore peaks with less area than this.
minWidth=3          (w) Ignore peaks narrower than this.
minPeak=2           (minp) Ignore peaks with an X-value below this.
maxPeak=BIG         (maxp) Ignore peaks with an X-value above this.
maxPeakCount=8      (maxpc) Print up to this many peaks (prioritizing height).

Java Parameters:
-Xmx                This will set Java's memory usage, overriding autodetection.
                    -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom               This flag will cause the process to exit if an
                    out-of-memory exception occurs.  Requires Java 8u92+.
-da                 Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for bbnorm.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("bbnorm.sh", args, capture_output)

def bbrealign(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for bbrealign.sh

    Help message:
    Written by Brian Bushnell
Last modified November 8, 2018

Description:  Realigns mapped reads to a reference.

Usage:  bbrealign.sh in_file=<file> ref=<file> out=<file>

Input may be a sorted or unsorted sam or bam file.
The reference should be fasta.

I/O parameters:
in_file=<file>       Input reads.
out=<file>      Output reads.
ref=<file>      Reference fasta.
overwrite=f     (ow) Set to false to force the program to abort rather than
                overwrite an existing file.

Trimming parameters:
border=0        Trim at least this many bases on both ends of reads.
qtrim=r         Quality-trim reads on this end
                   r: right, l: left, rl: both, f: don't quality-trim.
trimq=10        Quality-trim bases below this score.

Realignment parameters:
unclip=f        Convert clip symbols from exceeding the ends of the
                realignment zone into matches and substitutitions.
repadding=70    Pad alignment by this much on each end.  Typically,
                longer is more accurate for long indels, but greatly
                reduces speed.
rerows=602      Use this many rows maximum for realignment.  Reads longer
                than this cannot be realigned.
recols=2000     Reads may not be aligned to reference seqments longer 
                than this.  Needs to be at least read length plus
                max deletion length plus twice padding.
msa=            Select the aligner.  Options:
                   MultiStateAligner11ts:     Default.
                   MultiStateAligner9PacBio:  Use for PacBio reads, or for
                   Illumina reads mapped to PacBio/Nanopore reads.

Sam-filtering parameters:
minpos=         Ignore alignments not overlapping this range.
maxpos=         Ignore alignments not overlapping this range.
minreadmapq=4   Ignore alignments with lower mapq.
contigs=        Comma-delimited list of contig names to include. These 
                should have no spaces, or underscores instead of spaces.
secondary=f     Include secondary alignments.
supplimentary=f Include supplimentary alignments.
invert=f        Invert sam filters.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for bbrealign.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("bbrealign.sh", args, capture_output)

def bbsort(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for bbsort.sh

    Help message:
    Written by Brian Bushnell
Last modified October 10, 2022

Description:  Sorts reads by name or other keys such as length,
quality, mapping position, flowcell coordinates, or taxonomy.
Writes temp files if memory is exceeded.

Usage:   bbsort.sh in_file=<file> out=<file>

Input may be fasta, fastq, or sam, compressed or uncompressed.
Temp files will use the same format as the output.  Pairs are
kept together if reads are paired, and in2/out2 may be used for that.

Example 1 - sort by name:
bbsort.sh in_file=raw.fq out=sorted.fq
Example 2 - sort by sequence:
bbsort.sh in_file=raw.fq out=sorted.fq sequence
Example 3 - sort by mapping position:
bbsort.sh in_file=mapped.sam out=sorted.sam position

Parameters:

in_file=<file>       Input file.
out=<file>      Output file.
name=t          Sort reads by name.
length=f        Sort reads by length.
quality=f       Sort reads by quality.
position=f      Sort reads by position (for mapped reads).
taxa=f          Sort reads by taxonomy (for NCBI naming convention).
sequence=f      Sort reads by sequence, alphabetically.
clump=f         Sort reads by shared kmers, like Clumpify.
flowcell=f      Sort reads by flowcell coordinates.
shuffle=f       Shuffle reads randomly (untested).
list=<file>     Sort reads according to this list of names.
ascending=t     Sort ascending.

Memory parameters (you might reduce these if you experience a crash)
memmult=0.30    Write a temp file when used memory exceeds this fraction
                of available memory.
memlimit=0.65   Wait for temp files to finish writing until used memory
                drops below this fraction of available memory.
delete=t        Delete temporary files.
allowtemp=t     Allow writing temporary files.

Taxonomy-sorting parameters (for taxa mode only):
tree=           Specify a taxtree file.  On Genepool, use 'auto'.
gi=             Specify a gitable file.  On Genepool, use 'auto'.
accession=      Specify one or more comma-delimited NCBI accession to
                taxid files.  On Genepool, use 'auto'.

Note: name, length, and quality are mutually exclusive.
Sorting by quality actually sorts by average expected error rate,
so ascending will place the highest-quality reads first.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding
                autodetection.  -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an 
                out-of-memory exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for bbsort.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("bbsort.sh", args, capture_output)

def bbsplit(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for bbsplit.sh

    Help message:
    BBSplit
Written by Brian Bushnell, from Dec. 2010 - present
Last modified June 11, 2018

Description:  Maps reads to multiple references simultaneously.
Outputs reads to a file for the reference they best match, with multiple options for dealing with ambiguous mappings.

To index:     bbsplit.sh build=<1> ref_x=<reference fasta> ref_y=<another reference fasta>
To map:       bbsplit.sh build=<1> in_file=<reads> out_x=<output file> out_y=<another output file>

To be concise, and do everything in one command:
bbsplit.sh ref=x.fa,y.fa in_file=reads.fq basename=o%.fq

that is equivalent to
bbsplit.sh build=1 in_file=reads.fq ref_x=x.fa ref_y=y.fa out_x=ox.fq out_y=oy.fq

By default paired reads will yield interleaved output, but you can use the # symbol to produce twin output files.
For example, basename=o%_#.fq will produce ox_1.fq, ox_2.fq, oy_1.fq, and oy_2.fq.

     
Indexing Parameters (required when building the index):
ref=<file,file>     A list of references, or directories containing fasta files.
ref_<name>=<ref.fa> Alternate, longer way to specify references. e.g., ref_ecoli=ecoli.fa
                    These can also be comma-delimited lists of files; e.g., ref_a=a1.fa,a2.fa,a3.fa
build=<1>           If multiple references are indexed in the same directory, each needs a unique build ID.
path=<.>            Specify the location to write the index, if you don't want it in the current working directory.

Input Parameters:
build=<1>           Designate index to use.  Corresponds to the number specified when building the index.
in_file=<reads.fq>       Primary reads input; required parameter.
in2=<reads2.fq>     For paired reads in two files.
qin_file=<auto>          Set to 33 or 64 to specify input quality value ASCII offset.
interleaved=<auto>  True forces paired/interleaved input; false forces single-ended mapping.
                    If not specified, interleaved status will be autodetected from read names.

Mapping Parameters:
maxindel=<20>       Don't look for indels longer than this.  Lower is faster.  Set to >=100k for RNA-seq.
minratio=<0.56>     Fraction of max alignment score required to keep a site.  Higher is faster.
minhits=<1>         Minimum number of seed hits required for candidate sites.  Higher is faster.
ambiguous=<best>    Set behavior on ambiguously-mapped reads (with multiple top-scoring mapping locations).
                       best   (use the first best site)
                       toss   (consider unmapped)
                       random   (select one top-scoring site randomly)
                       all   (retain all top-scoring sites.  Does not work yet with SAM output)
ambiguous2=<best>   Set behavior only for reads that map ambiguously to multiple different references.
                    Normal 'ambiguous=' controls behavior on all ambiguous reads;
                    Ambiguous2 excludes reads that map ambiguously within a single reference.
                       best   (use the first best site)
                       toss   (consider unmapped)
                       all   (write a copy to the output for each reference to which it maps)
                       split   (write a copy to the AMBIGUOUS_ output for each reference to which it maps)
qtrim=<true>        Quality-trim ends to Q5 before mapping.  Options are 'l' (left), 'r' (right), and 'lr' (both).
untrim=<true>       Undo trimming after mapping.  Untrimmed bases will be soft-clipped in cigar strings.

Output Parameters:
out_<name>=<file>   Output reads that map to the reference <name> to <file>.
basename=prefix%suffix     Equivalent to multiple out_%=prefix%suffix expressions, in which each % is replaced by the name of a reference file.
bs=<file>           Write a shell script to 'file' that will turn the sam output into a sorted, indexed bam file.
scafstats=<file>    Write statistics on how many reads mapped to which scaffold to this file.
refstats=<file>     Write statistics on how many reads were assigned to which reference to this file.
                    Unmapped reads whose mate mapped to a reference are considered assigned and will be counted.
nzo=t               Only print lines with nonzero coverage.

***** Notes *****
Almost all BBMap parameters can be used; run bbmap.sh for more details.
Exceptions include the 'nodisk' flag, which BBSplit does not support.
BBSplit is recommended for fastq and fasta output, not for sam/bam output.
When the reference sequences are shorter than read length, use Seal instead of BBSplit.

Java Parameters:
-Xmx                This will set Java's memory usage, overriding autodetection.
                    -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom               This flag will cause the process to exit if an
                    out-of-memory exception occurs.  Requires Java 8u92+.
-da                 Disable assertions.

This list is not complete.  For more information, please consult $DIRdocs/readme.txt
Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for bbsplit.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("bbsplit.sh", args, capture_output)

def bbsplitpairs(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for bbsplitpairs.sh

    Help message:
    Written by Brian Bushnell
Last modified February 17, 2015

Description:  Separates paired reads into files of 'good' pairs and 'good' singletons by removing 'bad' reads that are shorter than a min length.
Designed to handle situations where reads become too short to be useful after trimming.  This program also optionally performs quality trimming.

Usage:        bbsplitpairs.sh in_file=<input file> out=<pair output file> outs=<singleton output file> minlen=<minimum read length, an integer>

Input may be fasta or fastq, compressed or uncompressed.

Optional parameters (and their defaults)

in_file=<file>           The 'in_file=' flag is needed if the input file is not the first parameter.  'in_file=stdin' will pipe from standard in.
in2=<file>          Use this if 2nd read of pairs are in a different file.
out=<file>          The 'out=' flag is needed if the output file is not the second parameter.  'out=stdout' will pipe to standard out.
out2=<file>         Use this to write 2nd read of pairs to a different file.
outsingle=<file>    (outs) Write singleton reads here.

overwrite=t         (ow) Set to false to force the program to abort rather than overwrite an existing file.
showspeed=t         (ss) Set to 'f' to suppress display of processing speed.
interleaved=auto    (int) If true, forces fastq input to be paired and interleaved.
qtrim=f             Trim read ends to remove bases with quality below trimq.
                    Values: rl (trim both ends), f (neither end), r (right end only), l (left end only).
trimq=6             Trim quality threshold.
minlen=20           (ml) Reads shorter than this after trimming will be discarded.
ziplevel=2          (zl) Set to 1 (lowest) through 9 (max) to change compression level; lower compression is faster.
fixinterleaving=f   (fint) Fixes corrupted interleaved files by examining pair names.  Only use on files with broken interleaving.
repair=f            (rp) Fixes arbitrarily corrupted paired reads by examining read names.  High memory.
ain_file=f               (allowidenticalnames) When detecting pair names, allows identical names, instead of requiring /1 and /2 or 1: and 2:

Java Parameters:
-Xmx                This will set Java's memory usage, overriding autodetection.
                    -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom               This flag will cause the process to exit if an
                    out-of-memory exception occurs.  Requires Java 8u92+.
-da                 Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for bbsplitpairs.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("bbsplitpairs.sh", args, capture_output)

def bbversion(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for bbversion.sh

    Help message:
    Written by Brian Bushnell
Last modified May 4, 2017

Description:  Prints the BBTools version number.
Add an argument to print the version name too.

Usage:  bbversion.sh

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for bbversion.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("bbversion.sh", args, capture_output)

def bbwrap(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for bbwrap.sh

    Help message:
    Last modified February 13, 2020

Description:  Wrapper for BBMap to allow multiple input and output files for the same reference.

To index:                 bbwrap.sh ref=<reference fasta>
To map:                   bbwrap.sh in_file=<file,file,...> out=<file,file,...>
To map without an index:  bbwrap.sh ref=<reference fasta> in_file=<file,file,...> out=<file,file,...> nodisk
To map pairs and singletons and output them into the same file:
bbwrap.sh in1=read1.fq,singleton.fq in2=read2.fq,null out=mapped.sam append

BBWrap will not work with stdin and stdout, or histogram output.

Other Parameters:

in_file=<file,file>  Input sequences to map.
inlist=<fofn>   Alternately, input and output can be a file of filenames,
                one line per file, using the flag inlist, outlist, outmlist,
                in2list, etc.
mapper=bbmap    Select mapper.  May be BBMap, BBMapPacBio, 
                or BBMapPacBioSkimmer.
append=f        Append to files rather than overwriting them.  
                If append is enabled, and there is exactly one output file,
                all output will be written to that file.

***** All BBMap parameters can be used; see bbmap.sh for more details. *****

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for bbwrap.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("bbwrap.sh", args, capture_output)

def bloomfilter(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for bloomfilter.sh

    Help message:
    Written by Brian Bushnell
Last modified September 20, 2022

Description:  Filters reads potentially sharing a kmer with a reference.
The more memory, the higher the accuracy.  Reads going to outu are guaranteed
to not match the reference, but reads going to outm might may or may not
match the reference.

Usage:  bloomfilter.sh in_file=<input file> out=<nonmatches> outm=<matches> ref=<reference>

Example:
bloomfilter.sh in_file=reads.fq outm=nonhuman.fq out=human.fq k=31 minhits=3 ref=human.fa

Error correction and depth filtering can be done simultaneously.

File parameters:
in_file=<file>       Primary input, or read 1 input.
in2=<file>      Read 2 input if reads are in two files.
outm=<file>     (out) Primary matched read output.
outm2=<file>    (out2) Matched read 2 output if reads are in two files.
outu=<file>     Primary unmatched read output.
outu2=<file>    Unmatched read 2 output if reads are in two files.
outc=<file>     Optional output stream for kmer counts.
ref=<file>      Reference sequence file, or a comma-delimited list.
                For depth-based filtering, set this to the same as the input.
overwrite=t     (ow) Set to false to force the program to abort rather than
                overwrite an existing file.

Hashing parameters:
k=31            Kmer length.
hashes=2        Number of hashes per kmer.  Higher generally reduces 
                false positives at the expense of speed.
sw=t            (symmetricwrite) Increases accuracy when bits>1 and hashes>1.
minprob=0.5     Ignore reference kmers with probability of being correct
                below this (affects fastq references only).
memmult=1.0     Fraction of free memory to use for Bloom filter.  1.0 should
                generally work; if the program crashes with an out of memory
                error, set this lower.  Higher increases specificity.
cells=          Option to set the number of cells manually.  By default this
                will be autoset to use all available memory.  The only reason
                to set this is to ensure deterministic output.
seed=0          This will change the hash function used.
bits=           Bits per cell; it is set automatically from mincount.

Reference-matching parameters:
minhits=3       Consecutive kmer hits for a read to be considered matched.
                Higher reduces false positives at the expense of sensitivity.
mincount=1      Minimum number of times a read kmer must occur in the 
                reference to be considered a match (or printed to outc).
requireboth=f   Require both reads in a pair to match the ref in order to go
                to outm.  By default, pairs go to outm if either matches.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for bloomfilter.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("bloomfilter.sh", args, capture_output)

def bloomfilterparser(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for bloomfilterparser.sh

    Help message:
    Written by Brian Bushnell
Last modified October 5, 2022

Description:  Parses verbose output from bloomfilter.sh for a specific paper.
Irrelevant for most people, but useful for reproducing published results.
You use it to parse output from bloomfilter.sh and tabulate it.

Usage:  bloomfilterparser.sh in_file=<input file> out=<output file>

...where the input file is whatever bloomfilter.sh prints to the screen.  E.G.
in_file=slurm-3249652.out out=summary.txt

You get details of calls to increment() if you add the verbose flag.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for bloomfilterparser.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("bloomfilterparser.sh", args, capture_output)

def calcmem(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for calcmem.sh

    Help message:
    No help message found.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for calcmem.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("calcmem.sh", args, capture_output)

def calctruequality(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for calctruequality.sh

    Help message:
    Written by Brian Bushnell
Last modified October 8, 2024

Description:  Calculates observed quality scores from mapped sam/bam files.
Generates matrices for use in recalibrating quality scores.  By default, 
the matrices are written to /ref/qual/ in the current directory.

If you have multiple sam/bam files demultiplexed from a single sequencing run,
it is recommended to use all of them as input for increased statistical power.
Once the matrices are generated, recalibration can be done on mapped or
unmapped reads; you may get better results by recalibrating the fastq and 
remapping the calibrated reads.

Note!  Diploid organisms with a high heterozygousity rate will induce
inaccurate recalibration at the high end of the quality scale unless SNP
locations are masked or variations are called.  For example, recalibrating 
human reads mapped to an unmasked human reference would generate an 
expected maximal Q-score of roughly 30 due to the human 1/1000 SNP rate.
Variations can be ignored by using the callvars flag or providing
a file of variations.

Usage:

Step 1.  Generate matrices (from mapped sam or bam files):
calctruequality.sh in_file=<file,file,...file> path=<directory>

Step 2.  Recalibrate reads (any kind of files):
bbduk.sh in_file=<file> out=<file> recalibrate


Parameters (and their defaults)

Input parameters:
in_file=<file,file>      Sam file or comma-delimited list of files.  Alignments 
                    must use = and X cigar symbols, or have MD tags, or
                    ref must be specified.
reads=-1            Stop after processing this many reads (if positive).
samstreamer=t       (ss) Load reads multithreaded to increase speed.
unpigz=t            Use pigz to decompress.

Output parameters:
overwrite=t         (ow) Set to true to allow overwriting of existing files.
path=.              Directory to write quality matrices (within /ref subdir).
write=t             Write matrices.
showstats=t         Print a summary.
pigz=f              Use pigz to compress.

Other parameters:
t=auto              Number of worker threads.
passes=2            Recalibration passes, 1 or 2.  2 is slower but gives more
                    accurate quality scores.
recalqmax=42        Adjust max quality scores tracked.  The actual highest
                    quality score allowed is recalqmax-1.
trackall=f          Track all available quality metrics and produce all
                    matrices, including the ones that are not selected for 
                    quality adjustment.  Reduces speed, but allows testing the
                    effects of different recalibration matrices.
indels=t            Include indels in quality calculations.
usetiles=f          Use per-tile quality statistics to generate matrices.
                    If this is true, the flag must also be used during
                    recalibration (e.g. in BBDuk).

Variation calling:
varfile=<file>      Use the variants in this var file, instead of calling
                    variants.  The format can be produced by CallVariants.
vcf=<file>          Use the variants in this VCF file, instead of
                    calling variants.
callvars=f          Call SNPs, and do not count them as errors.
ploidy=1            Set the organism's ploidy.
ref=                Required for variation-calling.

*** 'Variant-Calling Cutoffs' flags in callvariants.sh are also supported ***

Selecting matrices:
loadq102=           For each recalibration matrix, enable or disable that matrix with t/f.
                    You can specify pass1 or pass2 like this: loadq102_p1=f loadq102_p2=t.
                    The default is loadqbp_p1=t loadqbp_p2=t loadqb123_p=t.
clearmatrices=f     If true, clear all the existing matrix selections.  For example:
                    'clearmatrices loadqbp_p1'
                    This would ignore defaults and select only qbp for the first pass.

Available matrices:
q102                Quality, leading quality, trailing quality.
qap                 Quality, average quality, position.
qbp                 Quality, current base, position.
q10                 Quality, leading quality.
q12                 Quality, trailing quality.
qb12                Quality, leading base, current base.
qb012               Quality, two leading bases, current base.
qb123               Quality, leading base, current base, trailing base.
qb234               Quality, current base, two trailing bases.
q12b12              Quality, trailing quality, leading base, current base.
qp                  Quality, position.
q                   Current quality score only.


Java Parameters:
-Xmx                This will set Java's memory usage, overriding autodetection.
                    -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom               This flag will cause the process to exit if an
                    out-of-memory exception occurs.  Requires Java 8u92+.
-da                 Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for calctruequality.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("calctruequality.sh", args, capture_output)

def callgenes(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for callgenes.sh

    Help message:
    Written by Brian Bushnell
Last modified May 4, 2025

Description:  Finds orfs and calls genes in unspliced prokaryotes.
This includes bacteria, archaea, viruses, and mitochondria.
Can also predict 16S, 18S, 23S, 5S, and tRNAs.

Usage:  callgenes.sh in_file=contigs.fa out=calls.gff outa=aminos.faa out16S=16S.fa

File parameters:
in_file=<file>       A fasta file; the only required parameter.
out=<file>      Output gff file.
outa=<file>     Amino acid output.
out16s=<file>   16S output.
model=<file>    A pgm file or comma-delimited list.
                If unspecified a default model will be used.
stats=stderr    Stats output (may be stderr, stdin, a file, or null).
hist=null       Gene length histogram.
compareto=      Optional reference gff file to compare with the gene calls.
                'auto' will name it based on the input file name.

Formatting parameters:
json=false      Print stats in JSON.
binlen=21       Histogram bin length.
bins=1000       Maximum histogram bins.
pz=f            (printzero) Print histogram lines with zero count.



Other parameters:
minlen=60       Don't call genes shorter than this.
trd=f           (trimreaddescription) Set to true to trim read headers after
                the first whitespace.  Necessary for IGV.
merge=f         For paired reads, merge before calling.
detranslate=f   Output canonical nucleotide sequences instead of amino acids.
recode=f        Re-encode nucleotide sequences over called genes, leaving
                non-coding regions unchanged.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for callgenes.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("callgenes.sh", args, capture_output)

def callpeaks(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for callpeaks.sh

    Help message:
    Written by Brian Bushnell
Last modified December 19, 2018

Description:  Calls peaks from a 2-column (x, y) tab-delimited histogram.

Usage:        callpeaks.sh in_file=<histogram file> out=<output file>

Peak-calling parameters:
in_file=<file>           'in_file=stdin.fq' will pipe from standard in.
out=<file>          Write the peaks to this file.  Default is stdout.
minHeight=2         (h) Ignore peaks shorter than this.
minVolume=5         (v) Ignore peaks with less area than this.
minWidth=3          (w) Ignore peaks narrower than this.
minPeak=2           (minp) Ignore peaks with an X-value below this. 
                    Useful when low-count kmers are filtered).
maxPeak=BIG         (maxp) Ignore peaks with an X-value above this.
maxPeakCount=10     (maxpc) Print up to this many peaks (prioritizing height).
countColumn=1       (col) For multi-column input, this column, zero-based, 
                    contains the counts.
ploidy=-1           Specify ploidy; otherwise it will be autodetected.
logscale=f          Transform to log-scale prior to peak-calling.  Useful
                    for kmer-frequency histograms.

Smoothing parameters:
smoothradius=0      Integer radius of triangle filter.  Set above zero to 
                    smooth data prior to peak-calling.  Higher values are 
                    smoother.
smoothprogressive=f Set to true to widen the filter as the x-coordinate
                    increases.  Useful for kmer-frequency histograms.
maxradius=10        Maximum radius of progressive smoothing function.
progressivemult=2   Increment radius each time depth increases by this factor.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for callpeaks.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("callpeaks.sh", args, capture_output)

def callvariants(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for callvariants.sh

    Help message:
    Written by Brian Bushnell
Last modified October 6, 2020

Description:  Calls variants from sam or bam input.
In default mode, all input files are combined and treated as a single sample.
In multisample mode, each file is treated as an individual sample,
and gets its own column in the VCF file.  Unless overridden, input file
names are used as sample names.
Please read bbmap/docs/guides/CallVariantsGuide.txt for more information,
or bbmap/pipelines/variantPipeline.sh for a usage example.

Usage:  callvariants.sh in_file=<file,file,...> ref=<file> vcf=<file>

Input may be sorted or unsorted.
The reference should be fasta.

I/O parameters:
in_file=<file>       Input; may be one file or multiple comma-delimited files.
list=<file>     Optional text file containing one input file per line.
                Use list or in, but not both.
out=<file>      Output variant list in var format.  If the name ends
                with .vcf then it will be vcf format.
vcf=<file>      Output variant list in vcf format.
outgff=<file>   Output variant list in gff format.
ref=<file>      Reference fasta.  Required to display ref alleles.
                Variant calling wil be more accurate with the reference.
vcfin_file=<file>    Force calls at these locations, even if allele count is 0.
shist=<file>    (scorehist) Output for variant score histogram.
zhist=<file>    (zygosityhist) Output for zygosity histogram.
qhist=<file>    (qualityhist) Output for variant base quality histogram.
overwrite=f     (ow) Set to false to force the program to abort rather than
                overwrite an existing file.
extended=t      Print additional variant statistics columns.
sample=         Optional comma-delimited list of sample names.
multisample=f   (multi) Set to true if there are multiple sam/bam files,
                and each should be tracked as an individual sample.
vcf0=           Optional comma-delimited list of per-sample outputs.
                Only used in multisample mode.
bgzip=t         Use bgzip for gzip compression.
samstreamer=t   (ss) Load reads multithreaded to increase speed.
                Disable to reduce the number of threads used.  The number of
                streamer threads can be set with e.g. 'ss=4'; default is 6.
streamermf=8    (ssmf) Allow multiple sam files to be read simultaneously.
                Set ssmf=X to specify the maximum number or ssmf=f
                to disable.

Processing Parameters:
prefilter=f     Use a Bloom filter to exclude variants seen fewer than
                minreads times.  Doubles the runtime but greatly reduces
                memory usage.  The results are identical.
coverage=t      (cc) Calculate coverage, to better call variants.
ploidy=1        Set the organism's ploidy.
rarity=1.0      Penalize the quality of variants with allele fraction 
                lower than this.  For example, if you are interested in
                4% frequency variants, you could set both rarity and
                minallelefraction to 0.04.  This is affected by ploidy - 
                a variant with frequency indicating at least one copy
                is never penalized.
covpenalty=0.8  (lowcoveragepenalty) A lower penalty will increase the 
                scores of low-coverage variants, and is useful for 
                low-coverage datasets.
useidentity=t   Include average read identity in score calculation.
usepairing=t    Include pairing rate in score calculation.
usebias=t       Include strand bias in score calculation.
useedist=t      Include read-end distance in score calculation.
homopolymer=t   Penalize scores of substitutions matching adjacent bases.
nscan=t         Consider the distance of a variant from contig ends when 
                calculating strand bias.
callsub=t       Call substitutions.
calldel=t       Call deletions.
callins=t       Call insertions.
calljunct=f     Call junctions (in development).
nopassdot=f     Use . as genotype for variations failing the filter.

Coverage Parameters (these mainly affect speed and memory use):
32bit=f         Set to true to allow coverage tracking over depth 65535,
                which increases memory use.  Variant calls are impacted
                where coverage exceeds the maximum.
atomic=auto     Increases multithreaded speed; forces 32bit to true.
                Defaults to true if there are more than 8 threads.
strandedcov=f   (stranded) Tracks per-strand ref coverage to print the MCOV
                and DP4 fields.  Requires more memory when enabled.  Strand
                of variant reads is tracked regardless of this flag.

Trimming Parameters:
border=5        Trim at least this many bases on both ends of reads.
qtrim=r         Quality-trim reads on this end
                   r: right, l: left, rl: both, f: don't quality-trim.
trimq=10        Quality-trim bases below this score.

Realignment Parameters:
realign=f       Realign all reads with more than a couple mismatches.
                Decreases speed.  Recommended for aligners other than BBMap.
unclip=f        Convert clip symbols from exceeding the ends of the
                realignment zone into matches and substitutitions.
repadding=70    Pad alignment by this much on each end.  Typically,
                longer is more accurate for long indels, but greatly
                reduces speed.
rerows=602      Use this many rows maximum for realignment.  Reads longer
                than this cannot be realigned.
recols=2000     Reads may not be aligned to reference seqments longer 
                than this.  Needs to be at least read length plus
                max deletion length plus twice padding.
msa=            Select the aligner.  Options:
                   MultiStateAligner11ts:     Default.
                   MultiStateAligner9PacBio:  Use for PacBio reads, or for
                   Illumina reads mapped to PacBio/Nanopore reads.

Sam-filtering Parameters:
minpos=         Ignore alignments not overlapping this range.
maxpos=         Ignore alignments not overlapping this range.
minreadmapq=4   Ignore alignments with lower mapq.
contigs=        Comma-delimited list of contig names to include. These 
                should have no spaces, or underscores instead of spaces.
secondary=f     Include secondary alignments.
supplimentary=f Include supplimentary alignments.
duplicate=f     Include reads flagged as duplicates.
invert=f        Invert sam filters.

Variant-Calling Cutoffs:
minreads=2              (minad) Ignore variants seen in fewer reads.
maxreads=BIG            (maxad) Ignore variants seen in more reads.
mincov=0                Ignore variants in lower-coverage locations.
maxcov=BIG              Ignore variants in higher-coverage locations.
minqualitymax=15        Ignore variants with lower max base quality.
minedistmax=20          Ignore variants with lower max distance from read ends.
minmapqmax=0            Ignore variants with lower max mapq.
minidmax=0              Ignore variants with lower max read identity.
minpairingrate=0.1      Ignore variants with lower pairing rate.
minstrandratio=0.1      Ignore variants with lower plus/minus strand ratio.
minquality=12.0         Ignore variants with lower average base quality.
minedist=10.0           Ignore variants with lower average distance from ends.
minavgmapq=0.0          Ignore variants with lower average mapq.
minallelefraction=0.1   Ignore variants with lower allele fraction.  This
                        should be adjusted for high ploidies.
minid=0                 Ignore variants with lower average read identity.
minscore=20.0           Ignore variants with lower Phred-scaled score.
clearfilters            Clear all filters.  Filter flags placed after
                        the clearfilters flag will still be applied.

There are additionally max filters for score, quality, mapq, allelefraction,
and identity.

Other Parameters:
minvarcopies=0          If set to 0, a genotype (vcf GT field) of 0 or 0/0
                        will be called if observed allele frequency suggests
                        this is a minor allele.  If set to 1, GT field will
                        contain at least one 1.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for callvariants.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("callvariants.sh", args, capture_output)

def cat(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for cat.sh

    Help message:
    Written by Brian Bushnell
Last modified January 20, 2025

Description:  Concatenates and recompresses files.

Usage:  cat.sh *.fna out=catted.fa.gz

Standard parameters:
in_file=<file>       Comma-delimited input.  Filenames with no 'in_file=' will
                also be treated as input files.
out=<file>      Output.  Defaults to stdout.
ziplevel=2      (zl) Set to 1 (lowest) through 9 (max) to change compression
                level; lower compression is faster.

Processing parameters:
None yet!

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for cat.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("cat.sh", args, capture_output)

def cg2illumina(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for cg2illumina.sh

    Help message:
    Written by Brian Bushnell
Last modified May 6, 2024

Description:  Converts BGI/Complete Genomics reads to Illumina header format,
and optionally appends barcodes/indexes. For example, 
@E200008112L1C001R00100063962/1 
would become
@E200008112:0:FC:1:6396:1:1 1:N:0:

Usage:  bgi2illumina.sh in_file=<input file> out=<output file> barcode=<string>

Input may be fasta or fastq, compressed or uncompressed.

Standard parameters:
in_file=<file>       Primary input, or read 1 input.
in2=<file>      Read 2 input if reads are in two files.
out=<file>      Primary output, or read 1 output.
out2=<file>     Read 2 output if reads are in two files.
overwrite=f     (ow) Set to false to force the program to abort rather than
                overwrite an existing file.
ziplevel=2      (zl) Set to 1 (lowest) through 9 (max) to change compression
                level; lower compression is faster.

Processing parameters:
barcode=        (index) Optionally append a barcode to the header.
parseextra=f    Set this to true if the reads headers have comments 
                delimited by a whitespace.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for cg2illumina.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("cg2illumina.sh", args, capture_output)

def checkstrand(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for checkstrand.sh

    Help message:
    Written by Brian Bushnell
Last modified April 11, 2025

Description:  Estimates the strandedness of a library without alignment; 
intended for RNA-seq data.  Only the reads are required input to determine
strandedness, so this works when run with just a fastq file.  If sam/bam
input is used, additional alignment-based metrics will be reported.
If an assembly and gff file are provided, the affinity of reads to the plus 
or minus (sense or antisense) strand will also be calculated.  If a genome
is specified with no gff file, the genes will be called automatically with a
prokaryotic gene caller.  Strandedness and P/(P+M) ratios are similar but 
calculated in different ways, and thus will not exactly agree, but should be 
close.  For most calculations, only read 1 is used, or the merge of read 1
and read 2 if the merge flag is enabled and they overlap.


Output meaning:

Depth_Analysis: Based on comparing the fraction of kmers in forward and
                reverse orientation to a binomial distribution.
Strandedness:   Percent of reads that came from the majority strand, based
                on kmer depth.
StrandednessN:  Depth-normalized strandedness, where each unique kmer
                contributes equally regardless of depth.
AvgKmerDepth:   Average depth of kmers; typically higher than read depth.
Kmers>Depth1:   Fraction of kmers with depth over 1.  Singleton kmers cannot
                be used to calculate strandedness from depth.

Stop_Codon_Analysis:  Based on counting stop codons.
MajorStrandORF: Predicted major strand based on stop-codon analysis.
AvgReadLen:     Average length of R1, or the merged read pair.
AvgORFLen+:     Average ORF length in the best frame on the plus side of R1.
AvgORFLen-:     Average ORF length in the best frame on the minus side of R1.
AvgStopCount+:  Average number of stop codons in the best frame on plus side.
AvgStopCount-:  Average number of stop codons in the best frame on minus side.
GC_Content:     GC content of reads, which affects stop codon frequency.

PolyA_Analysis: Based on counting poly-A or poly-T tails.
MajorStrandPA:  Predicted major strand based on poly-A tail analysis.
                This is unreliable if the poly-A fraction is low.
PolyA/(PA+PT):  Ratio of (reads with poly-A tails)/(poly-A + poly-T tails).
PolyAFraction:  Fraction of reads ending in poly-A or poly-T.

Ref_Analysis:   Compares read kmer frequencies to a reference (if present).
                The reference can be a transcriptome or genome, and a gff file
                will be used if provided.
MajorStrandREF: The strand containing a majority of forward read kmers.
P/(P+M)_Ratio:  P is the sum of counts of plus kmers, and M is minus kmers.
GeneCoverage:   Fraction of transcriptome kmers represented in reads.
GenePrecision:  Fraction of read kmers found in the transcriptome.

Read_Gene_Calling_Analysis:  Uses gene-calling on reads to calculate which
                strand better fits a prokaryotic gene model.
MajorStrandRGC: Predicted major strand based on read gene calling.
P/(P+M)_Ratio:  P is the read count best matching the plus strand; M is minus.
AvgScorePlus:   Average score of called plus-strand genes.
AvgScoreMinus:  Average score of called plus-strand genes.
UsedFraction:   Fraction of reads with any called genes (or partial genes);
                this can be increased by merging the reads for longer frames.

Alignment_Results:  Requires sam/bam input.  The reads must have been
                mapped to a transcriptome or RNA-seq assembly, or to a 
                specified genome, or a gff file must be provided.
StrandednessAL: Percent of reads aligned to the dominant strand.  More 
                accurate for transcriptome-mapped than genome-mapped reads.
StrandednessAN: Depth-normalized strandedness, where each feature or
                contig contributes equally.
MajorStrandAL:  Strand to which a majority of reads aligned.
P/(P+M)_Ratio:  P is the number of plus-mapped reads, M is minus.
P/(P+M)_RatioN: Depth-normalized plus/total ratio.
PlusFeatures:   Fraction of features with majority plus-mapped reads.
AlignmentRate:  Fraction of reads that aligned.
Feature-Mapped: Fraction of reads that aligned to a feature in the gff.


Usage:  checkstrand.sh in_file=<input file>

Running on a fastq is simple, but there are multiple ways to run CheckStrand
on aligned data (in_file=, ref=, and gff= flags are not needed if the files have
proper extensions):

#1) This won't give alignment results, just kmer results
checkstrand.sh mapped.sam

#2) This will do gene-calling and the alignment strandedness will be based 
    on gene sense strand, but only works for prokaryotes/viruses
checkstrand.sh mapped.sam contigs.fa

#3) This will use the annotation and the alignment strandedness will be based
    on gene sense strand, works for proks, and should work for eukaryotes 
    (there are lots of ways to annotate multi-exon genes though)
checkstrand.sh mapped.sam genes.gff

#4) This will assume that the reference was a sense-strand transcriptome,
    and the alignment strandedness will be based on contig plus strand
checkstrand.sh mapped.sam transcriptome

#5) This will assume that the reference was unstranded contigs assembled
    from RNA-seq data, so the alignment strandedness will be based on
    contig majority strand
checkstrand.sh mapped.sam rnacontigs


Standard parameters:
in_file=<file>       Primary input (a fastq, fasta, sam or bam file).
in2=<file>      Secondary input for paired fastq in twin files.  Read 2 is 
                ignored unless merge=t.
out=<file>      Optional destination to redirect results instead of stdout.
outp=<file>     Optional output for plus-mapped reads.     
outm=<file>     Optional output for minus-mapped reads.
*Note: outp/outm require sam/bam input and either transcriptome mode or a gff.
The destination of plus-mapped r1 would be outp, but outm for plus-mapped r2.

Processing parameters:
ref=<file>      Optional reference (assembly) input.
gff=<file>      Optional gene annotation file input.
scafreport=<file>  Optional per-scaffold strandedness output.
transcriptome=f Set this to 't' if the reference is a sense-strand 
                transcriptome (rather than a genome assembly).  This applies
                to either a reference specified by 'ref' or the reference
                used for alignment, fo sam/bam input.
rnacontigs=f    Set this to 't' if the reference is contigs assembled from
                RNA-seq data, but with unknown orientation.  Only affects
                alignment results.
size=80000      Sketch size; larger may be more precise.
merge=f         Attempt to merge paired reads, and use the merged read when
                successful.  If unsuccessful only R1 is used.  This has a 
                performance impact on CPUs with few cores.
orf=t           Analyze stop codons and open reading frames.  Usually this
                will allow major strand determination without a reference, 
                unless GC is very high.
callreads=t     Perform gene-calling on reads using a prokarotic gene model.
                Not very relevant to eukaryotes.
passes=2        Two passes refines the gene model for better gene-calling on
                reads.  Only used if there is a reference.
samplerate=1.0  Set to a lower number to subsample the input reads; increases
                speed on CPUs with few cores.
sampleseed=17   Positive numbers are deterministic; negative use random seeds.
reads=-1        If positive, quit after processing this many reads.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for checkstrand.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("checkstrand.sh", args, capture_output)

def cladeloader(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for cladeloader.sh

    Help message:
    Written by Brian Bushnell
Last modified May 4, 2025

Description:  Loads fasta files and writes clade files.

Usage: cladeloader.sh in_file=contigs.fa out=clades.clade

Parameters:
in_file=<file,file>  Fasta files with tid in headers.
out=<file>      Output file.
maxk=5          Limit max kmer length (range 3-5).
a48             Output counts in ASCII-48 instead of decimal.
16s=<file,file> Optional tax-labeled file of 16S sequences.
18s=<file,file> Optional tax-labeled file of 16S sequences.
replaceribo     Set true if existing ssu should be replaced by new ones.
usetree=f       Load a taxonomic tree to generate lineage strings.
aligner=quantum Options include ssa2, glocal, drifting, banded, crosscut.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for cladeloader.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("cladeloader.sh", args, capture_output)

def clumpify(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for clumpify.sh

    Help message:
    Written by Brian Bushnell
Last modified January 10, 2025

Description:  Sorts sequences to put similar reads near each other.
Can be used for increased compression or error correction.
Please read bbmap/docs/guides/ClumpifyGuide.txt for more information.

Usage:   clumpify.sh in_file=<file> out=<file> reorder

Input may be fasta or fastq, compressed or uncompressed.  Cannot accept sam.

Parameters and their defaults:
in_file=<file>           Input file.
in2=<file>          Optional input for read 2 of twin paired files.
out=<file>          Output file.  May not be standard out.
out2=<file>         Optional output for read 2 of twin paired files.
groups=auto         Use this many intermediate files (to save memory).
                    1 group is fastest.  Auto will estimate the number
                    of groups needed based on the file size, so it should
                    not ever run out of memory.
lowcomplexity=f     For compressed low-complexity libraries such as RNA-seq,
                    this will more conservatively estimate how much memory
                    is needed to automatically decide the number of groups.
rcomp=f             Give read clumps the same orientation to increase 
                    compression.  Should be disabled for paired reads.
overwrite=f         (ow) Set to false to force the program to abort rather 
                    than overwrite an existing file.
qin_file=auto            Auto-detect input quality encoding.  May be set to:
                       33:  ASCII-33 (Sanger) encoding.
                       64:  ASCII-64 (old Illumina) encoding.
                    All modern sequence is encoded as ASCII-33.
qout=auto           Use input quality encoding as output quality encoding.
changequality=f     (cq) If true, fix broken quality scores such as Ns with
                    Q>0.  Default is false to ensure lossless compression.
fastawrap=70        Set to a higher number like 4000 for longer lines in 
                    fasta format, which increases compression.

Compression parameters:
ziplevel=6          (zl) Gzip compression level (1-11).  Higher is slower.
                    Level 11 is only available if pigz is installed and is
                    extremely slow to compress, but faster to decompress.
                    Naming the output file to *.bz2 will use bzip2 instead of
                    gzip for ~9% additional compression, which requires
                    bzip2, pbzip2, or lbzip2 in the path.
blocksize=128       Size of blocks for pigz, in kb.  Higher gives slightly
                    better compression.
shortname=f         Make the names as short as possible.  'shortname=shrink'
                    will shorten the names where possible, but retain the 
                    flowcell and barcode information.
reorder=f           Reorder clumps for additional compression.  Only valid
                    when groups=1, passes=1, and ecc=f.  Possible modes:
                       f:  Do not reorder clumps.
                       c:  Reorder using consensus reads.  Uses additional
                           time and memory.
                       p:  Reorder using pair information.  Requires paired
                           reads.  Yields the highest compression.
                       a:  Automatically choose between 'c' and 'p'.  The
                           flag reorder with no argument will set 'reorder=a'.
quantize=f          Bin the quality scores, like NextSeq.  This greatly
                    increases compression, but information is lost.

Temp file parameters:
compresstemp=auto   (ct) Gzip temporary files.  By default temp files will be
                    compressed if the output file is compressed.
deletetemp=t        Delete temporary files.
deleteinput=f       Delete input upon successful completion.
usetmpdir=f         Use tmpdir for temp files.
tmpdir=             By default, this is the environment variable TMPDIR.

Hashing parameters:
k=31                Use kmers of this length (1-31).  Shorter kmers may
                    increase compression, but 31 is recommended for error
                    correction.
mincount=0          Don't use pivot kmers with count less than this.
                    Setting mincount=2 can increase compression.
                    Increases time and memory usage.
seed=1              Random number generator seed for hashing.  
                    Set to a negative number to use a random seed.
hashes=4            Use this many masks when hashing.  0 uses raw kmers.
                    Often hashes=0 increases compression, but it should
                    not be used with error-correction.
border=1            Do not use kmers within this many bases of read ends.

Deduplication parameters:
dedupe=f            Remove duplicate reads.  For pairs, both must match.
                    By default, deduplication does not occur.
                    If dedupe and markduplicates are both false, none of
                    the other duplicate-related flags will have any effect.
markduplicates=f    Don't remove; just append ' duplicate' to the name.
allduplicates=f     Mark or remove all copies of duplicates, instead of
                    keeping the highest-quality copy.
addcount=f          Append the number of copies to the read name.
                    Mutually exclusive with markduplicates or allduplicates.
entryfilter=f       This assists in removing exact duplicates, which saves
                    memory in libraries that split unevenly due to huge
                    numbers of duplicates.  Enabled automatically as needed.
subs=2              (s) Maximum substitutions allowed between duplicates.
subrate=0.0         (dsr) If set, the number of substitutions allowed will be
                    max(subs, subrate*min(length1, length2)) for 2 sequences.
allowns=t           No-called bases will not be considered substitutions.
scanlimit=5         (scan) Continue for this many reads after encountering a
                    nonduplicate.  Improves detection of inexact duplicates.
umi=f               If reads have UMIs in the headers, require them to match
                    to consider the reads duplicates.
umisubs=0           Consider UMIs as matching if they have up to this many
                    mismatches.
containment=f       Allow containments (where one sequence is shorter).
affix=f             For containments, require one sequence to be an affix
                    (prefix or suffix) of the other.
optical=f           If true, mark or remove optical duplicates only.
                    This means they are Illumina reads within a certain
                    distance on the flowcell.  Normal Illumina names needed.
                    Also for tile-edge and well duplicates.
dupedist=40         (dist) Max distance to consider for optical duplicates.
                    Higher removes more duplicates but is more likely to
                    remove PCR rather than optical duplicates.
                    This is platform-specific; recommendations:
                       NextSeq      40  (and spany=t)
                       HiSeq 1T     40
                       HiSeq 2500   40
                       HiSeq 3k/4k  2500
                       Novaseq6000  12000
                       NovaseqX+    50
spany=f             Allow reads to be considered optical duplicates if they
                    are on different tiles, but are within dupedist in the
                    y-axis.  Should only be enabled when looking for 
                    tile-edge duplicates (as in NextSeq).
spanx=f             Like spany, but for the x-axis.  Not necessary 
                    for NextSeq.
spantiles=f         Set both spanx and spany.
adjacent=f          Limit tile-spanning to adjacent tiles (those with 
                    consecutive numbers).
*** Thus, for NextSeq, the recommended deduplication flags are: ***
dedupe optical spany adjacent

Pairing/ordering parameters (for use with error-correction):
unpair=f            For paired reads, clump all of them rather than just
                    read 1.  Destroys pairing.  Without this flag, for paired
                    reads, only read 1 will be error-corrected.
repair=f            After clumping and error-correction, restore pairing.
                    If groups>1 this will sort by name which will destroy
                    clump ordering; with a single group, clumping will
                    be retained.

Error-correction parameters:
ecc=f               Error-correct reads.  Requires multiple passes for
                    complete correction.
ecco=f              Error-correct paired reads via overlap before clumping.
passes=1            Use this many error-correction passes.  6 passes are 
                    suggested, though more will be more through.
conservative=f      Only correct the highest-confidence errors, to minimize
                    chances of eliminating a minor allele or inexact repeat.
aggressive=f        Maximize the number of errors corrected.
consensus=f         Output consensus sequence instead of clumps.

Advanced error-correction parameters:
mincc=4             (mincountcorrect) Do not correct to alleles occuring less
                    often than this.
minss=4             (minsizesplit) Do not split into new clumps smaller than 
                    this.
minsfs=0.17         (minsizefractionsplit) Do not split on pivot alleles in
                    areas with local depth less than this fraction of clump size.
minsfc=0.20         (minsizefractioncorrect) Do not correct in areas with local
                    depth less than this.
minr=30.0           (minratio) Correct to the consensus if the ratio of the
                    consensus allele to second-most-common allele is >=minr,
                    for high depth.  Actual ratio used is:
                    min(minr, minro+minorCount*minrm+quality*minrqm).
minro=1.9           (minratiooffset) Base ratio.
minrm=1.8           (minratiomult) Ratio multiplier for secondary allele count.
minrqm=0.08         (minratioqmult) Ratio multiplier for base quality.
minqr=2.8           (minqratio) Do not correct bases when cq*minqr>rqsum.
minaqr=0.70         (minaqratio) Do not correct bases when cq*minaqr>5+rqavg.
minid=0.97          (minidentity) Do not correct reads with identity to 
                    consensus less than this.
maxqadjust=0        Adjust quality scores by at most maxqadjust per pass.
maxqi=-1            (maxqualityincorrect) Do not correct bases with quality 
                    above this (if positive).
maxci=-1            (maxcountincorrect) Do not correct alleles with count 
                    above this (if positive).
findcorrelations=t  Look for correlated SNPs in clumps to split into alleles.
maxcorrelations=12  Maximum number of eligible SNPs per clump to consider for
                    correlations.  Increasing this number can reduce false-
                    positive corrections at the possible expense of speed.

Java Parameters:
-Xmx                This will set Java's memory usage, overriding autodetection.
                    -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom               This flag will cause the process to exit if an
                    out-of-memory exception occurs.  Requires Java 8u92+.
-da                 Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for clumpify.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("clumpify.sh", args, capture_output)

def commonkmers(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for commonkmers.sh

    Help message:
    Written by Brian Bushnell
Last modified February 20, 2015

Description:  Prints the most common kmers in each sequence.
This is intended for short kmers only!

Usage:  commonkmers.sh in_file=<file> out=<file>

Parameters:
k=2             Kmer length, 0-12.
display=3       Print this many kmers per sequence.
count=f         Print the kmer counts as well.

ow=f            (overwrite) Overwrites files that already exist.
app=f           (append) Append to files that already exist.
zl=4            (ziplevel) Set compression level, 1 (low) to 9 (max).
qin_file=auto        ASCII offset for input quality.  May be 33 (Sanger), 64 (Illumina), or auto.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for commonkmers.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("commonkmers.sh", args, capture_output)

def comparegff(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for comparegff.sh

    Help message:
    Written by Brian Bushnell
Last modified August 12, 2019

Description:  Compares CDS, rRNA, and tRNA lines in gff files.

Usage:  comparegff.sh in_file=<input gff> ref=<reference gff>

Standard parameters:
in_file=<file>       Query gff.
ref=<file>      Reference gff.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for comparegff.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("comparegff.sh", args, capture_output)

def comparelabels(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for comparelabels.sh

    Help message:
    Written by Brian Bushnell
Last modified May 9, 2024

Description:  Compares delimited labels in read headers to count 
how many match.  The 'unknown' label is a special case.  The original 
goal was to measure the differences between demultiplexing methods.
Labels can be added with the rename.sh suffix flag, or the 
novademux.sh rename+nosplit flags, or seal.sh with rename, addcount=f,
and tophitonly.  The assumption is that a header will look like:
@VP2:12:H7:2:1101:8:2 1:N:0:CAAC (tab) CAAC (tab) CAAC
...in which case the labels CAAC would be compared and found equal.


Usage:  comparelables.sh in_file=<input file> out=<output file>

Input may be fasta or fastq, compressed or uncompressed.

Standard parameters:
in_file=<file>       Primary input, or read 1 input.
out=stdout      Print the results to this destination.  Default is stdout
                but a file may be specified.
labelstats=     Optional destination for per-label stats.
quantset=<file> If set, ignore reads with labels not contained in this file;
                one label per line.  'unknown' is automatically included.
swap=f          Swap the order of label 1 and label 2.
delimiter=tab   Compare the last two terms in the header, using this 
                single-character delimiter.  Most symbols can be expressed
                as literals (e.g. 'delimiter=_' for underscore) but you can
                also spell out some of the problematic ones:
                   space, tab, pound, greaterthan, lessthan, equals,
                   colon, semicolon, bang, and, quote, singlequote,
                   backslash, hat, dollar, dot, pipe, questionmark, star,
                   plus, openparen, closeparen, opensquare, opencurly

Output Terminology:
aa             Both labels were equal.
uu             Both labels were unknown.
au             Label 1 was assigned, label 2 was unknown.
ua             Label 1 was unknown, label 2 was assigned.
ab             Both labels were assigned, but not equal.  For per-label
               stats, indicates label 1 was assigned to this, and label 2
               was assigned to something else.
ba             In per-label stats, indicates label 2 was assigned to this and
               label 1 was assigned to something else. 
yield          Fraction of reads assigned to the same label.  E.g. if aa=10,
               au=1, ab=2, then yield2 = aa/(aa+au+ab) = 10/13 = 0.77.
contam         Fraction of reads assigned to a different label, using the
               other as ground truth.  For example, if aa=10, au=1, ab=2,
               then contam1=ab/(aa+au+ab) = 2/13 = 153846 PPM.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for comparelabels.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("comparelabels.sh", args, capture_output)

def comparesketch(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for comparesketch.sh

    Help message:
    Written by Brian Bushnell
Last modified Jan 7, 2020

Description:  Compares query sketches to others, and prints their kmer identity.
The input can be sketches made by sketch.sh, or fasta/fastq files.
It's recommended to first sketch references with sketch.sh for large files,
or when taxonomic information is desired.

Please read bbmap/docs/guides/BBSketchGuide.txt for more information.

Usage:  comparesketch.sh in_file=<file,file,file...> ref=<file,file,file...>
Alternative:  comparesketch.sh in_file=<file,file,file...> file file file
Alternative:  comparesketch.sh in_file=<file,file,file...> *.sketch
Alternative:  comparesketch.sh alltoall *.sketch.gz

File parameters:
in_file=<file,file...>   Sketches or fasta files to compare.
out=stdout          Comparison output.  Can be set to a file instead.
outsketch=<file>    Optionally write sketch files generated from the input.
ref=<file,file...>  List of sketches to compare against.  Files given without
                    a prefix (ref=) will be treated as references,
                    so you can use *.sketch without ref=.
                    You can also do ref=nt#.sketch to load all numbered files
                    fitting that pattern.
                    On NERSC, you can use these abbreviations (e.g. ref=nt):
                       nt:      nt sketches
                       refseq:  Refseq sketches
                       silva:   Silva sketches
                       img:     IMG sketches
                       mito:    RefSeq mitochondrial sketches
                       fungi:   RefSeq fungi sketches
                       protein: RefSeq prokaryotic amino acid sketches
                    Using an abbreviation automatically sets the blacklist, 
                    and k.  If the reference is in amino space, the query
                    also be in amino acid space with the flag amino added.
                    If the query is in nucleotide space, use the flag
                    'translate', but this will only work for prokaryotes.

Blacklist and Whitelist parameters:
blacklist=<file>    Ignore keys in this sketch file.  Additionally, there are
                    built-in blacklists that can be specified:
                       nt:      Blacklist for nt
                       refseq:  Blacklist for Refseq
                       silva:   Blacklist for Silva
                       img:     Blacklist for IMG
whitelist=f         Ignore keys that are not in the index.  Requires index=t.

Sketch-making parameters:
mode=perfile        Possible modes, for sequence input:
                       single: Generate one sketch.
                       sequence: Generate one sketch per sequence.
                       perfile: Generate one sketch per file.
sketchonly=f        Don't run comparisons, just write the output sketch file.
k=31                Kmer length, 1-32.  To maximize sensitivity and 
                    specificity, dual kmer lengths may be used:  k=31,24
                    Dual kmers are fastest if the shorter is a multiple 
                    of 4.  Query and reference k must match.
samplerate=1        Set to a lower value to sample a fraction of input reads.
                    For raw reads (rather than an assembly), 1-3x coverage
                    gives best results, by reducing error kmers.  Somewhat
                    higher is better for high-error-rate data like PacBio.
minkeycount=1       Ignore kmers that occur fewer times than this.  Values
                    over 1 can be used with raw reads to avoid error kmers.
minprob=0.0001      Ignore kmers below this probability of correctness.
minqual=0           Ignore kmers spanning bases below this quality.
entropy=0.66        Ignore sequence with entropy below this value.
merge=f             Merge paired reads prior to sketching.
amino=f             Use amino acid mode.  Input should be amino acids.
translate=f         Call genes and translate to proteins.  Input should be
                    nucleotides.  Designed for prokaryotes.
sixframes=f         Translate all 6 frames instead of predicting genes.
ssu=t               Scan for and retain full-length SSU sequence.
printssusequence=f  Print the query SSU sequence (JSON mode only).

Size parameters:
size=10000          Desired size of sketches (if not using autosize).
mgf=0.01            (maxfraction) Max fraction of genomic kmers to use.
minsize=100         Do not generate sketches for genomes smaller than this.
autosize=t          Use flexible sizing instead of fixed-length.  This is
                    nonlinear; a human sketch is only ~6x a bacterial sketch.
sizemult=1          Multiply the autosized size of sketches by this factor.
                    Normally a bacterial-size genome will get a sketch size
                    of around 10000; if autosizefactor=2, it would be ~20000.
density=            If this flag is set (to a number between 0 and 1),
                    autosize and sizemult are ignored, and this fraction of
                    genomic kmers are used.  For example, at density=0.001,
                    a 4.5Mbp bacteria will get a 4500-kmer sketch.
sketchheapfactor=4  If minkeycount>1, temporarily track this many kmers until
                    counts are known and low-count kmers are discarded.

Sketch comparing parameters:
threads=auto        Use this many threads for comparison.
index=auto          Index the sketches for much faster searching.
                    Requires more memory and adds startup time.
                    Recommended true for many query sketches, false for few.
prealloc=f          Preallocate the index for greater efficiency.
                    Can be set to a number between 0 and 1 to determine how 
                    much of total memory should be used.
alltoall            (ata) Compare all refs to all.  Must be sketches.
compareself=f       In all-to-all mode, compare a sketch to itself.

Taxonomy-related parameters:
tree=<file>         Specify a TaxTree file.  On Genepool, use tree=auto.
                    Only necessary for use with printtaxa and level.
                    Assumes comparisons are done against reference sketches
                    with known taxonomy information.
level=2             Only report the best record per taxa at this level.
                    Either level names or numbers may be used.
                        0: disabled
                        1: subspecies
                        2: species
                        3: genus
                       ...etc
include=            Restrict output to organisms in these clades.
                    May be a comma-delimited list of names or NCBI TaxIDs.
includelevel=0      Promote the include list to this taxonomic level.
                    For example, include=h.sapiens includelevel=phylum
                    would only include organisms in the same phylum as human.
includestring=      Only report records whose name contains this string.
exclude=            Ignore organisms in these clades.
                    May be a comma-delimited list of names or NCBI TaxIDs.
excludelevel=0      Promote the exclude list to this taxonomic level.
                    For example, exclude=h.sapiens excludelevel=phylum
                    would exclude all organisms in the same phylum as human.
excludestring=      Do not records whose name contains this string.
minlevel=           Use this to restrict comparisons to distantly-related
                    organisms.  Intended for finding misclassified organisms
                    using all-to-all comparisons.  minlevel=order would only
                    report hits between organisms related at the order level
                    or higher, not between same species or genus.
banunclassified=f   Ignore organisms descending from nodes like 
                    'unclassified Bacteria'
banvirus=f          Ignore viruses.
requiressu=f        Ignore records without SSUs.
minrefsize=0        Ignore ref sketches smaller than this (unique kmers).
minrefsizebases=0   Ignore ref sketches smaller than this (total base pairs).

Output format:
format=2            2: Default format with, per query, one query header line;
                       one column header line; and one reference line per hit.
                    3: One line per hit, with columns query, reference, ANI,
                       and sizeRatio. Useful for all-to-all comparisons.
                    4: JSON (format=json also works).
                    5: Constellation (format=constellation also works).
usetaxidname=f      For format 3, print the taxID in the name column.
usetaxname          for format 3, print the taxonomic name in the name column.
useimgname          For format 3, print the img ID in the name column.

Output columns (for format=2):
printall=f          Enable all output columns.
printani=t          (ani) Print average nucleotide identity estimate.
completeness=t      Genome completeness estimate.
score=f             Score (used for sorting the output).
printmatches=t      Number of kmer matches to reference.
printlength=f       Number of kmers compared.
printtaxid=t        NCBI taxID.
printimg=f          IMG identifier (only for IMG data).
printgbases=f       Number of genomic bases.
printgkmers=f       Number of genomic kmers.
printgsize=t        Estimated number of unique genomic kmers.
printgseqs=t        Number of sequences (scaffolds/reads).
printtaxname=t      Name associated with this taxID.
printname0=f        (pn0) Original seqeuence name.
printfname=t        Query filename.
printtaxa=f         Full taxonomy of each record.
printcontam=t       Print contamination estimate, and factor contaminant kmers
                    into calculations.  Kmers are considered contaminant if
                    present in some ref sketch but not the current one.
printunique=t       Number of matches unique to this reference.
printunique2=f      Number of matches unique to this reference's taxa.
printunique3=f      Number of query kmers unique to this reference's taxa,
                    regardless of whether they are in this reference sketch.
printnohit=f        Number of kmers that don't hit anything.
printrefhits=f      Average number of ref sketches hit by shared kmers.
printgc=f           GC content.
printucontam=f      Contam hits that hit exactly one reference sketch.
printcontam2=f      Print contamination estimate using only kmer hits
                    to unrelated taxa.
contamlevel=species Taxonomic level to use for contam2/unique2/unique3.
NOTE: unique2/unique3/contam2/refhits require an index.

printdepth=f        (depth) Print average depth of sketch kmers; intended
                    for shotgun read input.
printdepth2=f       (depth2) Print depth compensating for genomic repeats.
                    Requires reference sketches to be generated with depth.
actualdepth=t       If this is false, the raw average count is printed.
                    If true, the raw average (observed depth) is converted 
                    to estimated actual depth (including uncovered areas).
printvolume=f       (volume) Product of average depth and matches.
printca=f           Print common ancestor, if query taxID is known.
printcal=f          Print common ancestor tax level, if query taxID is known.
recordsperlevel=0   If query TaxID is known, and this is positive, print this
                    many records per common ancestor level.

Sorting:
sortbyscore=t       Default sort order is by score, a composite metric.
sortbydepth=f       Include depth as a factor in sort order.
sortbydepth2=f      Include depth2 as a factor in sort order.
sortbyvolume=f      Include volume as a factor in sort order.
sortbykid=f         Sort strictly by KID.
sortbyani=f         Sort strictly by ANI/AAI/WKID.
sortbyhits=f        Sort strictly by the number of kmer hits.

Other output parameters:
minhits=3           (hits) Only report records with at least this many hits.
minani=0            (ani) Only report records with at least this ANI (0-1).
minwkid=0.0001      (wkid) Only report records with at least this WKID (0-1).
anifromwkid=t       Calculate ani from wkid.  If false, use kid.
minbases=0          Ignore ref sketches of sequences shortert than this.
minsizeratio=0      Don't compare sketches if the smaller genome is less than
                    this fraction of the size of the larger.
records=20          Report at most this many best-matching records.
color=family        Color records at the family level.  color=f will disable.
                    Colors work in most terminals but may cause odd characters
                    to appear in text editors.  So, color defaults to f if 
                    writing to a file.  Requires the taxtree to be loaded.
intersect=f         Print sketch intersections.  delta=f is suggested.

Metadata flags (optional, for the query sketch header):
taxid=-1            Set the NCBI taxid.
imgid=-1            Set the IMG id.
spid=-1             Set the JGI sequencing project id.
name=               Set the name (taxname).
name0=              Set name0 (normally the first sequence header).
fname=              Set fname (normally the file name).
meta_=              Set an arbitrary metadata field.
                    For example, meta_Month=March.

Other parameters:
requiredmeta=       (rmeta) Required optional metadata values.  For example:
                    rmeta=subunit:ssu,source:silva
bannedmeta=         (bmeta) Forbidden optional metadata values.


Java Parameters:
-Xmx                This will set Java's memory usage, overriding autodetection.
                    -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom               This flag will cause the process to exit if an
                    out-of-memory exception occurs.  Requires Java 8u92+.
-da                 Disable assertions.

For more detailed information, please read /bbmap/docs/guides/BBSketchGuide.txt.
Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for comparesketch.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("comparesketch.sh", args, capture_output)

def comparessu(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for comparessu.sh

    Help message:
    Written by Brian Bushnell
Last modified December 4, 2019

Description:  Aligns SSUs to each other and reports identity.
This requires sequences annotated with a taxID in their header.

Usage:  comparessu.sh in_file=<input file> out=<output file>

Input may be fasta or fastq, compressed or uncompressed.

Standard parameters:
in_file=<file>       Input sequences.
out=<file>      Output data.
t=              Set the number of threads; default is logical processors.
overwrite=f     (ow) Set to false to force the program to abort rather than
                overwrite an existing file.
showspeed=t     (ss) Set to 'f' to suppress display of processing speed.
ziplevel=2      (zl) Set to 1 (lowest) through 9 (max) to change compression
                level; lower compression is faster.
reads=-1        If positive, quit after this many sequences.

Processing parameters:
ata=f           Do an all-to-all comparison.  Otherwise, each sequence will
                only be compared to one other randomly-selected sequence
                per taxonomic level.
minlen=0        Ignore sequences shorter than this.
maxlen=BIG      Ignore sequences longer than this.
maxns=-1        If positive, ignore sequences with more than this many Ns.


Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for comparessu.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("comparessu.sh", args, capture_output)

def comparevcf(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for comparevcf.sh

    Help message:
    Written by Brian Bushnell
Last modified April 30, 2019

Description:  Performs set operations on VCF files:
Union, intersection, and subtraction.

Usage:  comparevcf.sh in_file=<file,file,...> out=<file>

I/O parameters:
in_file=<file>       Input; must be at least 2 files.
out=<file>      Output file.
ref=<file>      Reference file; optional.  Usually not needed.
shist=<file>    (scorehist) Output for variant score histogram.
overwrite=f     (ow) Set to false to force the program to abort rather than
bgzip=f         Use bgzip for gzip compression.

Processing Mode (choose one only):
subtract=t      Subtract all other files from the first file.
union=f         Make a union of all files.
intersection=f  Make an intersection of all files.

Processing Parameters:
addsamples=t    Include all samples in the output lines. (TODO)
splitalleles=f  Split multi-allelic lines into multiple lines.
splitsubs=f     Split multi-base substitutions into SNPs.
canonize=t      Trim variations down to a canonical representation.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for comparevcf.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("comparevcf.sh", args, capture_output)

def consect(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for consect.sh

    Help message:
    Written by Brian Bushnell
Last modified October 25, 2016

Description:  Generates the conservative consensus of multiple
error-correction tools.  Corrections will be accepted only
if all tools agree.  This tool is designed for substitutions only,
not indel corrections.

Usage:  consect.sh in_file=<file,file,file,...> out=<file>

Standard parameters:
in_file=             A comma-delimited list of files; minimum of 3.
                All files must have reads in the same order.
                The first file must contain the uncorrected reads.
                All additional files must contain corrected reads.
out=<file>      Output of consensus reads.
overwrite=f     (ow) Set to false to force the program to abort rather than
                overwrite an existing file.

Processing parameters:
None yet!

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for consect.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("consect.sh", args, capture_output)

def consensus(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for consensus.sh

    Help message:
    Written by Brian Bushnell
Last modified February 10, 2020

Description:  Generates the consensus sequence of a reference
using aligned sequences.  This can be used for polishing assemblies,
making representative ribosomal sub units, correcting PacBio reads, etc.

If unaligned sequences are used as input, they should be in fasta or fastq
format, and they will be aligned to the first reference sequence.

Usage:  consensus.sh in_file=mapped.sam ref=ref.fa out=consensus.fa

Recommended settings for assembly polishing via Illumina reads:  mafsub=0.5


Standard parameters:
in_file=<file>       Reads mapped to the reference; should be sam or bam.
ref=<file>      Reference; may be fasta or fastq.
out=<file>      Modified reference; may be fasta or fastq.
outm=<file>     Optional output for binary model file.
                Preferred extension is .alm.
inm=<file>      Optional input model file for statistics.
hist=<file>     Optional score histogram output.
overwrite=f     (ow) Set to false to force the program to abort rather than
                overwrite an existing file.

Processing parameters:
mindepth=2      Do not change to alleles present at depth below this.
mafsub=0.25     Do not incorporate substitutions below this allele fraction.
mafdel=0.50     Do not incorporate deletions below this allele fraction.
mafins=0.50     Do not incorporate insertions below this allele fraction.
mafn=0.40       Do not change Ns (noref) to calls below this allele fraction.
usemapq=f       Include mapq as a positive factor in edge weight.
nonly=f         Only change Ns to different bases.
noindels=f      Don't allow indels.
ceiling=        If set, alignments will be weighted by their inverse identity.
                For example, at ceiling=105, a read with 96% identity will get
                bonus weight of 105-96=9 while a read with 70% identity will
                get 105-70=35.  This favors low-identity reads.
name=           Set the output sequence name (for a single output sequence).

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for consensus.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("consensus.sh", args, capture_output)

def copyfile(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for copyfile.sh

    Help message:
    Written by Brian Bushnell
Last modified October 9, 2023

Description:  Copies a file.
The main purpose is to recompress it.

Usage:  copyfile.sh in_file=<file> out=<file>

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for copyfile.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("copyfile.sh", args, capture_output)

def countbarcodes(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for countbarcodes.sh

    Help message:
    Written by Brian Bushnell
Last modified October 16, 2015

Description: Counts the number of reads with each barcode.

Usage:   countbarcodes.sh in_file=<file> counts=<file>

Input may be stdin or a fasta or fastq file, raw or gzipped.
If you pipe via stdin/stdout, please include the file type; e.g. for gzipped fasta input, set in_file=stdin.fa.gz

Input parameters:
in_file=<file>           Input reads, whose names end in a colon then barcode.
counts=<file>       Output of counts.
interleaved=auto    (int) If true, forces fastq input to be paired and interleaved.
qin_file=auto            ASCII offset for input quality.  May be 33 (Sanger), 64 (Illumina), or auto.
unpigz=t            Use pigz to decompress.
expected=           Comma-delimited list of expected bar codes.
valid=              Comma-delimited list of valid bar codes.
countundefined=t    Count barcodes that contain non-ACGT symbols.
printheader=t       Print a header.
maxrows=-1          Optionally limit the number of rows printed.

Output parameters:
out=<file>          Write bar codes and counts here.  'out=stdout' will pipe to standard out.

Java Parameters:
-Xmx                This will set Java's memory usage, overriding autodetection.
                    -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom               This flag will cause the process to exit if an
                    out-of-memory exception occurs.  Requires Java 8u92+.
-da                 Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for countbarcodes.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("countbarcodes.sh", args, capture_output)

def countbarcodes2(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for countbarcodes2.sh

    Help message:
    Written by Brian Bushnell
Last modified May 14, 2024

Description: Counts and summarizes the number of reads with each barcode,
using class BarcodeStats.  Can also do barcode assignment.

Usage:   countbarcodes.sh in_file=<file> counts=<file>

Input may be stdin or a fasta or fastq file, raw or gzipped.

Input Parameters:
in_file=<file>           Input reads, whose names end in a colon then barcode.
countsin_file=<file>     Input of counts; optional.
quantset=<file>     Only quantify barcodes in this file.
interleaved=auto    (int) If true, fastq input will be considered interleaved.
expected=           Comma-delimited list of expected bar codes.

Output parameters:
maxrows=-1          Optionally limit the number of rows printed.
printheader=t       Print a header.
out=<file>          (counts) Write bar codes and counts here.  'out=stdout' 
                    will pipe to standard out.
barcodesout=<file>  Barcode assignment counts.
mapout=<file>       Map of observed to expected barcode assignments.
outcontam=<file>    Requires labeled data, and causes contam quantification.

Processing Parameters:
countundefined=t    Count barcodes that contain non-ACGT symbols.
pcrmatrix=f         Use a PCRMatrix for barcode assignment.
mode=hdist          PCRMatrix type.


Java Parameters:
-Xmx                This will set Java's memory usage, overriding autodetection.
                    -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom               This flag will cause the process to exit if an
                    out-of-memory exception occurs.  Requires Java 8u92+.
-da                 Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for countbarcodes2.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("countbarcodes2.sh", args, capture_output)

def countduplicates(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for countduplicates.sh

    Help message:
    Written by Brian Bushnell
Last modified October 14, 2022

Description:  Counts duplicate sequences probabilistically,
using around 20 bytes per unique read.  Read pairs are treated
as a single read.  Reads are converted to a hashcode and only
the hashcode is stored when tracking duplicates, so (rare) hash
collisions will result in false positive duplicate detection.
Optionally outputs the deduplicated and/or duplicate reads.

Usage:  countduplicates.sh in_file=<input file>

Input may be fasta, fastq, or sam, compressed or uncompressed.
in2, out2, and outd2 are accepted for paired files.

Standard parameters:
in_file=<file>       Primary input, or read 1 input.
out=<file>      Optional output for deduplicated reads.
outd=<file>     Optional output for duplicate reads.  An extension like .fq
                will output reads; .txt will output headers only.
stats=stdout    May be replaced by a filename to write stats to a file.
showspeed=t     (ss) Set to 'f' to suppress display of processing speed.

Processing parameters (these are NOT mutually exclusive):
bases=t         Include bases when generating hashcodes. 
names=f         Include names (headers) when generating hashcodes.
qualities=f     Include qualities when generating hashcodes.
maxfraction=-1.0  Set to a positive number 0-1 to FAIL input
                  that exceeds this fraction of reads with duplicates.
maxrate=-1.0    Set to a positive number >=1 to FAIL input that exceeds this
                average duplication rate (the number of copies per read).
failcode=0      Set to some other number like 1 to produce a
                non-zero exit code for failed input.
samplerate=1.0  Fraction of reads to subsample, to conserve memory.  Sampling
                is deterministic - if a read is sampled, copies will be too.
                Unsampled reads are not sent to any output stream or counted 
                in statistics.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for countduplicates.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("countduplicates.sh", args, capture_output)

def countgc(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for countgc.sh

    Help message:
    Written by Brian Bushnell
Last modified January 21, 2015

Description:  Counts GC content of reads or scaffolds.

Usage:  countgc in_file=<input> out=<output> format=<format>

Input may be stdin or a fasta or fastq file, compressed or uncompressed.
Output (which is optional) is tab-delimited.
format=1:   name   length   A   C   G   T   N
format=2:   name   GC
format=4:   name   length   GC
Note that in format 1, A+C+G+T=1 even when N is nonzero.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for countgc.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("countgc.sh", args, capture_output)

def countsharedlines(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for countsharedlines.sh

    Help message:
    Written by Brian Bushnell
Last modified September 15, 2015

Description:  Counts the number of lines shared between sets of files.
One output file will be printed for each input file.  For example,
an output file for a file in the 'in1' set will contain one line per
file in the 'in2' set, indicating how many lines are shared.

Usage:  countsharedlines.sh in1=<file,file...> in2=<file,file...>

Parameters:
include=f       Set to 'true' to include the filtered names rather than excluding them.
prefix=f        Allow matching of only the line's prefix (all characters up to first whitespace).
case=t          (casesensitive) Match case also.
ow=t            (overwrite) Overwrites files that already exist.
app=f           (append) Append to files that already exist.
zl=4            (ziplevel) Set compression level, 1 (low) to 9 (max).

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for countsharedlines.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("countsharedlines.sh", args, capture_output)

def crosscontaminate(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for crosscontaminate.sh

    Help message:
    Written by Brian Bushnell
Last modified February 17, 2015

Description:  Generates synthetic cross-contaminated files from clean files.
Intended for use with synthetic reads generated by SynthMDA or RandomReads.

Usage:        crosscontaminate.sh in_file=<file,file,...> out=<file,file,...>

Input parameters:
in_file=<file,file,...>  Clean input reads.
innamefile=<file>   A file containing the names of input files, 
                    one name per line.
interleaved=auto    (int) t/f overrides interleaved autodetection.
qin_file=auto            Input quality offset: 33 (Sanger), 64, or auto.
reads=-1            If positive, quit after processing X reads or pairs.

Processing Parameters:
minsinks=1          Min contamination destinations from one source.
maxsinks=8          Max contamination destinations from one source.
minprob=0.000005    Min allowed contamination rate (geometric distribution).
maxprob=0.025       Max allowed contamination rate.

Output parameters:
out=<file,file,...> Contaminated output reads.
outnamefile=<file>  A file containing the names of output files, 
                    one name per line.
overwrite=t         (ow) Grant permission to overwrite files.
#showspeed=t        (ss) 'f' suppresses display of processing speed.
ziplevel=2          (zl) Compression level; 1 (min) through 9 (max).
threads=auto        (t) Set number of threads to use; default is number of 
                    logical processors.
qout=auto           Output quality offset: 33 (Sanger), 64, or auto.
shuffle=f           Shuffle contents of output files.
shufflethreads=3    Use this many threads for shuffling (uses more memory).

Java Parameters:
-Xmx                This will set Java's memory usage, overriding autodetection.
                    -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom               This flag will cause the process to exit if an
                    out-of-memory exception occurs.  Requires Java 8u92+.
-da                 Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for crosscontaminate.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("crosscontaminate.sh", args, capture_output)

def crosscutaligner(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for crosscutaligner.sh

    Help message:
    Written by Brian Bushnell
Last modified May 4, 2025

Description:  Aligns a query sequence to a reference using CrossCutAligner.
This fully explores the matrix using 4 arrays of roughly length reflen.
The sequences can be any characters, but N is a special case.
Outputs the identity, rstart, and rstop positions.
CrossCut is a nontraditional aligner that fills antidiagonals,
incurring zero data dependencies between loops.  This allows
perfect SIMD vectorization.

Usage:
crosscutaligner.sh <query> <ref>
crosscutaligner.sh <query> <ref> <map>
crosscutaligner.sh <query> <ref> <map> <iterations> <simd>

Parameters:
query           A literal nucleotide sequence or fasta file.
ref             A literal nucleotide sequence or fasta file.
map             Optional output text file for matrix score space.
                Set to null for benchmarking with no visualization.
                This has not yet been tested and will produce unknown results.
iterations      Optional integer for benchmarking multiple iterations.
simd            Use vector instructions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for crosscutaligner.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("crosscutaligner.sh", args, capture_output)

def cutgff(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for cutgff.sh

    Help message:
    Written by Brian Bushnell
Last modified October 15, 2019

Description:  Cuts out features defined by a gff file, and writes them
to a new fasta.  Features are output in their sense strand.

Usage:  cutgff.sh in_file=<fna file> gff=<gff file> out=<fna file>

in_file= is optional, and gff filenames will be automaitically assumed based on
the fasta name if not specified.  This allows running on multiple files
like this:

cutgff.sh types=rRNA out=16S.fa minlen=1440 maxlen=1620 attributes=16S bacteria/*.fna.gz


File Parameters:
in_file=<file>           Input FNA (fasta) file.
gff=<file>          Input GFF file (optional).
out=<file>          Output FNA file.

Other Parameters:
types=CDS           Types of features to cut.
invert=false        Invert selection: rather outputting the features,
                    mask them with Ns in the original sequences.
attributes=         A comma-delimited list of strings.  If present, one of
                    these strings must be in the gff line attributes.
bannedattributes=   A comma-delimited list of banned strings.
banpartial=t        Ignore lines with 'partial=true' in attributes.
minlen=1            Ignore lines shorter than this.
maxlen=2147483647   Ignore lines longer than this.
renamebytaxid=f     Rename sequences with their taxID.  Input sequences
                    must be named appropriately, e.g. in NCBI format.
taxmode=accession   Valid modes are:
                       accession: Sequence names must start with an accession.
                       gi:        Seqence names must start with gi|number
                       taxid:     Sequence names must start with tid|number
                       header:    Best effort for various header formats.
requirepresent=t    Crash if a taxID cannot be found for a sequence.
oneperfile=f        Only output one sequence per file.
align=f             Align ribosomal sequences to consensus (if available);
                    discard those with low identity, and flip those
                    annotated on the wrong strand.
maxns=-1            If non-negative, ignore features with more than this many
                    undefined bases (Ns or IUPAC symbols).
maxnfraction=-1.0   If non-negative, ignore features with more than this
                    fraction of undefined bases (Ns or IUPAC symbols).
                    Should be 0.0 to 1.0.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for cutgff.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("cutgff.sh", args, capture_output)

def cutprimers(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for cutprimers.sh

    Help message:
    Written by Brian Bushnell
Last modified May 15, 2018

Description:  Cuts out sequences between primers identified in sam files.
Intended for use with sam files generated by msa.sh; one sam file for the
forward primer, and one for the reverse primer.

Usage:	cutprimers.sh in_file=<file> out=<file> sam1=<file> sam2=<file>

Parameters:

in_file=<file>       File containing reads. in_file=stdin.fa will pipe from stdin.
out=<file>      Output sequences. out=stdout will pipe to stdout.
sam1=<file>     Sam file containing mapped locations of primer sequence 1.
sam2=<file>     Sam file containing mapped locations of primer sequence 2.
fake=t          Output 1bp 'N' reads in cases where there is no primer.
include=f       Include the flanking primer sequences in output.

Java Parameters:

-Xmx            This will set Java's memory usage, overriding automatic
                memory detection. -Xmx20g will specify 
                20 gigs of RAM, and -Xmx200m will specify 200 megs.  
                The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for cutprimers.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("cutprimers.sh", args, capture_output)

def decontaminate(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for decontaminate.sh

    Help message:
    Written by Brian Bushnell.
Last modified June 28, 2016

Description:  Decontaminates multiplexed assemblies via normalization and mapping.

Usage:  decontaminate.sh reads=<file,file> ref=<file,file> out=<directory>
or
decontaminate.sh readnamefile=<file> refnamefile=<file> out=<directory>

Input Parameters:
reads=<file,file>   Input reads, one file per library.
ref=<file,file>     Input assemblies, one file per library.
readnamefile=<file> List of input reads, one line per library.
refnamefile=<file>  List of input assemblies, one line per library.

interleaved=auto    True forces paired/interleaved input; false forces single-ended mapping.
                    If not specified, interleaved status will be autodetected from read names.
unpigz=t            Spawn a pigz (parallel gzip) process for faster decompression.  Requires pigz to be installed.
touppercase=t       (tuc) Convert lowercase letters in reads to upper case (otherwise they will not match the reference).

Output Parameters:
pigz=f              Spawn a pigz (parallel gzip) process for faster compression.  Requires pigz to be installed.
tmpdir=.            Write temp files here.  By default is uses the system's $TMPDIR or current directory.
outdir=.            Write ouput files here.

Mapping Parameters:
kfilter=55          Set to a positive number N to require minimum N contiguous matches for a mapped read.
ambig=random        Determines how coverage will be calculated for ambiguously-mapped reads.
                        first: Add coverage only at first genomic mapping location.
                        random: Add coverage at a random best-scoring location.
                        all: Add coverage at all best-scoring locations.
                        toss: Discard ambiguously-mapped reads without adding coverage.

Filtering Parameters:
minc=3.5            Min average coverage to retain scaffold.
minp=20             Min percent coverage to retain scaffold.
minr=18             Min mapped reads to retain scaffold.
minl=500            Min length to retain scaffold.
ratio=1.2           Contigs will not be removed by minc unless the coverage changed by at least this factor.  0 disables this filter.
mapraw=t            Set true to map the unnormalized reads.  Required to filter by 'ratio'.
basesundermin_file=-1    If positive, removes contigs with at least this many bases in low-coverage windows.
window=500          Sliding window size 
windowcov=5         Average coverage below this will be classified as low.

Tadpole Parameters:
ecct=f              Error-correct with Tadpole before normalization.
kt=42               Kmer length for Tadpole.
aggressive=f        Do aggressive error correction.
conservative=f      Do conservative error correction.
tadpoleprefilter=1  (tadpre) Ignore kmers under this depth to save memory.

Normalization Parameters:
mindepth=2          Min depth of reads to keep.
target=20           Target normalization depth.
hashes=4            Number of hashes in Bloom filter.
passes=1            Normalization passes.
minprob=0.5         Min probability of correctness to add a kmer.
dp=0.75             (depthpercentile) Percentile to use for depth proxy (0.5 means median).
prefilter=t         Prefilter, for large datasets.
filterbits=32       (fbits) Bits per cell in primary filter.
prefilterbits=2     (pbits) Bits per cell in prefilter.
k=31                Kmer length for normalization.  Longer is more precise but less sensitive.

Other parameters:
opfn=0              (onlyprocessfirstn) Set to a positive number to only process that many datasets.  This is for internal testing of specificity.

Java Parameters:
-Xmx                This will set Java's memory usage, overriding autodetection.
                    -Xmx20g will specify 20 gigs of RAM, and -Xmx800m will specify 800 megs.
                    The max is typically 85% of physical memory.
-eoom               This flag will cause the process to exit if an
                    out-of-memory exception occurs.  Requires Java 8u92+.
-da                 Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for decontaminate.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("decontaminate.sh", args, capture_output)

def dedupe(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for dedupe.sh

    Help message:
    Written by Brian Bushnell and Jonathan Rood
Last modified February 19, 2020

Description:  Accepts one or more files containing sets of sequences (reads or scaffolds).
Removes duplicate sequences, which may be specified to be exact matches, subsequences, or sequences within some percent identity.
Can also find overlapping sequences and group them into clusters.
Please read bbmap/docs/guides/DedupeGuide.txt for more information.

Usage:     dedupe.sh in_file=<file or stdin> out=<file or stdout>

An example of running Dedupe for clustering short reads:
dedupe.sh in_file=x.fq am=f ac=f fo c pc rnc=f mcs=4 mo=100 s=1 pto cc qin_file=33 csf=stats.txt pattern=cluster_%.fq dot=graph.dot

Input may be fasta or fastq, compressed or uncompressed.
Output may be stdout or a file.  With no output parameter, data will be written to stdout.
If 'out=null', there will be no output, but statistics will still be printed.
You can also use 'dedupe <infile> <outfile>' without the 'in_file=' and 'out='.

I/O parameters:
in_file=<file,file>        A single file or a comma-delimited list of files.
out=<file>            Destination for all output contigs.
pattern=<file>        Clusters will be written to individual files, where the '%' symbol in the pattern is replaced by cluster number.
outd=<file>           Optional; removed duplicates will go here.
csf=<file>            (clusterstatsfile) Write a list of cluster names and sizes.
dot=<file>            (graph) Write a graph in dot format.  Requires 'fo' and 'pc' flags.
threads=auto          (t) Set number of threads to use; default is number of logical processors.
overwrite=t           (ow) Set to false to force the program to abort rather than overwrite an existing file.
showspeed=t           (ss) Set to 'f' to suppress display of processing speed.
minscaf=0             (ms) Ignore contigs/scaffolds shorter than this.
interleaved=auto      If true, forces fastq input to be paired and interleaved.
ziplevel=2            Set to 1 (lowest) through 9 (max) to change compression level; lower compression is faster.

Output format parameters:
storename=t           (sn) Store scaffold names (set false to save memory).
#addpairnum=f         Add .1 and .2 to numeric id of read1 and read2.
storequality=t        (sq) Store quality values for fastq assemblies (set false to save memory).
uniquenames=t         (un) Ensure all output scaffolds have unique names.  Uses more memory.
mergenames=f          When a sequence absorbs another, concatenate their headers.
mergedelimiter=>      Delimiter between merged headers.  Can be a symbol name like greaterthan.
numbergraphnodes=t    (ngn) Label dot graph nodes with read numbers rather than read names.
sort=f                Sort output (otherwise it will be random).  Options:
                         length:  Sort by length
                         quality: Sort by quality
                         name:    Sort by name
                         id:      Sort by input order
ascending=f           Sort in ascending order.
ordered=f             Output sequences in input order.  Equivalent to sort=id ascending.
renameclusters=f      (rnc) Rename contigs to indicate which cluster they are in.
printlengthinedges=f  (ple) Print the length of contigs in edges.

Processing parameters:
absorbrc=t            (arc) Absorb reverse-complements as well as normal orientation.
absorbmatch=t         (am) Absorb exact matches of contigs.
absorbcontainment=t   (ac) Absorb full containments of contigs.
#absorboverlap=f      (ao) Absorb (merge) non-contained overlaps of contigs (TODO).
findoverlap=f         (fo) Find overlaps between contigs (containments and non-containments).  Necessary for clustering.
uniqueonly=f          (uo) If true, all copies of duplicate reads will be discarded, rather than keeping 1.
rmn=f                 (requirematchingnames) If true, both names and sequence must match.
usejni=f              (jni) Do alignments in C code, which is faster, if an edit distance is allowed.
                      This will require compiling the C code; details are in /jni/README.txt.

Subset parameters:
subsetcount=1         (sstc) Number of subsets used to process the data; higher uses less memory.
subset=0              (sst) Only process reads whose ((ID%subsetcount)==subset).

Clustering parameters:
cluster=f             (c) Group overlapping contigs into clusters.
pto=f                 (preventtransitiveoverlaps) Do not look for new edges between nodes in the same cluster.
minclustersize=1      (mcs) Do not output clusters smaller than this.
pbr=f                 (pickbestrepresentative) Only output the single highest-quality read per cluster.

Cluster postprocessing parameters:
processclusters=f     (pc) Run the cluster processing phase, which performs the selected operations in this category.
                      For example, pc AND cc must be enabled to perform cc.
fixmultijoins=t       (fmj) Remove redundant overlaps between the same two contigs.
removecycles=t        (rc) Remove all cycles so clusters form trees.
cc=t                  (canonicizeclusters) Flip contigs so clusters have a single orientation.
fcc=f                 (fixcanoncontradictions) Truncate graph at nodes with canonization disputes.
foc=f                 (fixoffsetcontradictions) Truncate graph at nodes with offset disputes.
mst=f                 (maxspanningtree) Remove cyclic edges, leaving only the longest edges that form a tree.

Overlap Detection Parameters
exact=t               (ex) Only allow exact symbol matches.  When false, an 'N' will match any symbol.
touppercase=t         (tuc) Convert input bases to upper-case; otherwise, lower-case will not match.
maxsubs=0             (s) Allow up to this many mismatches (substitutions only, no indels).  May be set higher than maxedits.
maxedits=0            (e) Allow up to this many edits (subs or indels).  Higher is slower.
minidentity=100       (mid) Absorb contained sequences with percent identity of at least this (includes indels).
minlengthpercent=0    (mlp) Smaller contig must be at least this percent of larger contig's length to be absorbed.
minoverlappercent=0   (mop) Overlap must be at least this percent of smaller contig's length to cluster and merge.
minoverlap=200        (mo) Overlap must be at least this long to cluster and merge.
depthratio=0          (dr) When non-zero, overlaps will only be formed between reads with a depth ratio of at most this.
                      Should be above 1.  Depth is determined by parsing the read names; this information can be added
                      by running KmerNormalize (khist.sh, bbnorm.sh, or ecc.sh) with the flag 'rename'
k=31                  Seed length used for finding containments and overlaps.  Anything shorter than k will not be found.
numaffixmaps=1        (nam) Number of prefixes/suffixes to index per contig. Higher is more sensitive, if edits are allowed.
hashns=f              Set to true to search for matches using kmers containing Ns.  Can lead to extreme slowdown in some cases.
#ignoreaffix1=f       (ia1) Ignore first affix (for testing).
#storesuffix=f        (ss) Store suffix as well as prefix.  Automatically set to true when doing inexact matches.

Other Parameters
qtrim=f               Set to qtrim=rl to trim leading and trailing Ns.
trimq=6               Quality trim level.
forcetrimleft=-1      (ftl) If positive, trim bases to the left of this position (exclusive, 0-based).
forcetrimright=-1     (ftr) If positive, trim bases to the right of this position (exclusive, 0-based).

Note on Proteins / Amino Acids
Dedupe supports amino acid space via the 'amino' flag.  This also changes the default kmer length to 10.
In amino acid mode, all flags related to canonicity and reverse-complementation are disabled,
and nam (numaffixmaps) is currently limited to 2 per tip.

Java Parameters:
-Xmx                  This will set Java's memory usage, overriding autodetection.
                      -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom                 This flag will cause the process to exit if an out-of-memory exception occurs.  Requires Java 8u92+.
-da                   Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for dedupe.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("dedupe.sh", args, capture_output)

def dedupe2(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for dedupe2.sh

    Help message:
    Written by Brian Bushnell and Jonathan Rood
Last modified September 15, 2015

Dedupe2 is identical to Dedupe except it supports hashing unlimited kmer
prefixes and suffixes per sequence.  Dedupe supports at most 2 of each,
but uses slightly more memory.  You can manually set the number of kmers to
hash per read with the numaffixmaps (nam) flag.  Dedupe will automatically
call Dedupe2 if necessary (if nam=3 or higher) so this script is no longer
necessary.

For documentation, please consult dedupe.sh; syntax is identical.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for dedupe2.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("dedupe2.sh", args, capture_output)

def dedupebymapping(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for dedupebymapping.sh

    Help message:
    Written by Brian Bushnell
Last modified April 4, 2020

Description:  Deduplicates mapped reads based on pair mapping coordinates.

Usage:   dedupebymapping.sh in_file=<file> out=<file>

Parameters:
in_file=<file>           The 'in_file=' flag is needed if the input file is not the 
                    first parameter.  'in_file=stdin' will pipe from standard in.
out=<file>          The 'out=' flag is needed if the output file is not the 
                    second parameter.  'out=stdout' will pipe to standard out.
overwrite=t         (ow) Set to false to force the program to abort rather 
                    than overwrite an existing file.
ziplevel=2          (zl) Set to 1 (lowest) through 9 (max) to change 
                    compression level; lower compression is faster.
keepunmapped=t      (ku) Keep unmapped reads.  This refers to unmapped
                    single-ended reads or pairs with both unmapped.
keepsingletons=t    (ks) Keep all pairs in which only one read mapped.  If 
                    false, duplicate singletons will be discarded.
ignorepairorder=f   (ipo) If true, consider reverse-complementary pairs
                    as duplicates.

Java Parameters:
-Xmx                This will set Java's memory usage, overriding autodetection.
                    -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom               This flag will cause the process to exit if an
                    out-of-memory exception occurs.  Requires Java 8u92+.
-da                 Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for dedupebymapping.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("dedupebymapping.sh", args, capture_output)

def demuxbyname(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for demuxbyname.sh

    Help message:
    Written by Brian Bushnell
Last modified March 2, 2024

Description:  Demultiplexes sequences into multiple files based on their 
names, substrings of their names, or prefixes or suffixes of their names.
Allows unlimited output files while maintaining only a small number of 
open file handles.

Usage:
demuxbyname.sh in_file=<file> in2=<file> out=<file> out2=<file> names=<string,string,...>

Alternately:
demuxbyname.sh in_file=<file> out=<file> outu=<file> names=<file> barcode
This will parse the barcode from Illumina reads with a header like this:
@A00178:73:HH7H3DSXX:4:1101:13666:1047 1:N:0:ACGTTGGT+TGACGCAT

demuxbyname.sh in_file=<file> out=<file> delimiter=whitespace prefixmode=f
This will demultiplex by the substring after the last whitespace.

demuxbyname.sh in_file=<file> out=<file> length=8 prefixmode=t
This will demultiplex by the first 8 characters of read names.

demuxbyname.sh in_file=<file> out=<file> delimiter=: prefixmode=f
This will split on colons, and use the last substring as the name;
so for Illumina reads in the above format it would demux by barcode.

in2 and out2 are for paired reads in twin files and are optional.
If input is paired and there is only one output file, it will be written interleaved.

File Parameters:
in_file=<file>       Input file.
in2=<file>      If input reads are paired in twin files, use in2 for the 
                second file.
out=<file>      Output files for reads with matched headers (must contain %
                symbol).  For example, out=out_%.fq with names XX and YY 
                would create out_XX.fq and out_YY.fq.  If twin files for
                paired reads are desired, use the # symbol.  For example,
                out=out_%_#.fq in this case would create out_XX_1.fq, 
                out_XX_2.fq, out_YY_1.fq, and out_YY_2.fq.
outu=<file>     Output file for reads with unmatched headers.
stats=<file>    Print statistics about how many reads went to each file.
names=          List of strings (or files containing strings) to parse from
                read names.  Files should contain one name per line.  This is
                optional.  If a list of names is provided, files will only be
                created for those names.  For example, 'prefixmode=t length=5'
                would create a file for every unique first 5 characters in 
                read names, and every read would be written to one of those
                files.  But if there was addionally 'names=ABCDE,FGHIJ' then
                at most 2 files would be created, and anything not matching 
                those names would go to outu.

Processing Modes (determines how to convert a read into a name):
prefixmode=t    (pm) Match prefix of read header.  If false, match suffix of
                read header.  prefixmode=f is equivalent to suffixmode=t.
barcode=f       Parse barcodes from Illumina headers.
tile=f          Parse tile numbers from Illumina headers.
chrom=f         For mapped sam files, make one file per chromosome (scaffold)
                using the rname.
header=f        Use the entire sequence header.
delimiter=      For prefix or suffix mode, specifying a delimiter will allow
                exact matches even if the length is variable.  This allows 
                demultiplexing based on names that are found without 
                specifying a list of names.  In suffix mode, everything after
                the last delimiter will be used.  Normally the delimiter will
                be used as a literal string (a Java regular expression); for 
                example, ':' or 'HISEQ'.  But there are some special 
                delimiters which will be replaced by the symbol they name, 
                because they can cause problems.
                These are provided for convenience due to OS conflicts:
                   space, tab, whitespace, pound, greaterthan, lessthan, 
                   equals, colon, semicolon, bang, and, quote, singlequote
                These are provided because they interfere with Java regular 
                expression syntax:
                   backslash, hat, dollar, dot, pipe, questionmark, star,
                   plus, openparen, closeparen, opensquare, opencurly
                In other words, to match '.', you should set 'delimiter=dot'.
substring=f     Names can be substrings of read headers.  Substring mode is
                slow if the list of names is large.  Requires a list of names.

Other Processing Parameters:
column=-1       If positive, split the header on a delimiter and match that 
                column (1-based).  For example, using this header:
                NB501886:61:HL3GMAFXX:1:11101:10717:1140 1:N:0:ACTGAGC+ATTAGAC
                You could demux by tile (11101) using 'delimiter=: column=5'
                Column is 1-based (first column is 1).
                If column is omitted when a delimiter is present, prefixmode
                will use the first substring, and suffixmode will use the 
                last substring.
length=0        If positive, use a suffix or prefix of this length from read
                name instead of or in addition to the list of names.
                For example, you could create files based on the first 8 
                characters of read names.
hdist=0         Allow a hamming distance for demultiplexing barcodes.  This
                requires a list of names (barcodes).  It is unrelated to 
                probabiilty mode's hdist3.
replace=        Replace some characters in the output filenames.  For example,
                replace=+- would replace the + symbol in headers with the - 
                symbol in output filenames.  So you could match the barcode 
                ACTGAGC+ATTAGAC, but write to file ACTGAGC-ATTAGAC.

Buffering Parameters
streams=8       Allow at most this many active streams.  The actual number
                of open files will be 1 greater than this if outu is set,
                and doubled if output is paired and written in twin files 
                instead of interleaved.  Setting this to at least the number
                of expected output files can make things go much faster.
minreads=0      Don't create a file for fewer than this many reads; instead,
                send them to unknown.  This option will incur additional
                memory usage.
rpb=8000        Dump buffers to files when they fill with this many reads.
                Higher can be faster; lower uses less memory.
bpb=8000000     Dump buffers to files when they contain this many bytes.
                Higher can be faster; lower uses less memory.

Common parameters:
ow=t            (overwrite) Overwrites files that already exist.
zl=4            (ziplevel) Set compression level, 1 (low) to 9 (max).
int=auto        (interleaved) Determines whether INPUT file is considered 
                interleaved.
qin_file=auto        ASCII offset for input quality.  All modern platforms use 33.
qout=auto       ASCII offset for output quality.                    

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify
                200 megs.  The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for demuxbyname.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("demuxbyname.sh", args, capture_output)

def demuxserver(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for demuxserver.sh

    Help message:
    Written by Brian Bushnell
Last modified June 27, 2024

Description:   Starts a server for demultiplexing queries.

Usage:  demuxserver.sh port=<number>


Parameters:

port=3068           Port number.
domain_file=             Domain to be displayed in the help message.
                    Default is demux.jgi.doe.gov.

Java Parameters:
-Xmx                This will set Java's memory usage, overriding autodetection.
                    -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom               This flag will cause the process to exit if an
                    out-of-memory exception occurs.  Requires Java 8u92+.
-da                 Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for demuxserver.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("demuxserver.sh", args, capture_output)

def diskbench(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for diskbench.sh

    Help message:
    Written by Brian Bushnell
Last modified March 5, 2018

Description:  Benchmarks a disk with multithreaded I/O.

Usage:  diskbench.sh path=<path> data=<8g> passes=<2> threads=<>

Parameters:
path=           Location to read and write.
data=8g         Number of bytes to process per pass.
threads=        Number of threads to use.  By default, all logical threads.
                In RW mode the number of active threads is doubled.
mode=rw         I/O mode:
                   r:  Test read speed only.
                   w:  Test write speed only.
                   rw: Test read and write speed simultaneously.

Processing parameters:
None yet!

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for diskbench.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("diskbench.sh", args, capture_output)

def driftingaligner(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for driftingaligner.sh

    Help message:
    Written by Brian Bushnell
Last modified May 4, 2025

Description:  Aligns a query sequence to a reference using DriftingAligner.
The sequences can be any characters, but N is a special case.
Outputs the identity, rstart, and rstop positions.
Optionally prints a state space exploration map.
This map can be fed to visualizealignment.sh to make an image.

Usage:
driftingaligner.sh <query> <ref>
driftingaligner.sh <query> <ref> <map>
driftingaligner.sh <query> <ref> <map> <iterations>

Parameters:
query           A literal nucleotide sequence or fasta file.
ref             A literal nucleotide sequence or fasta file.
map             Optional output text file for matrix score space.
                Set to null for benchmarking with no visualization.
iterations      Optional integer for benchmarking multiple iterations.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for driftingaligner.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("driftingaligner.sh", args, capture_output)

def driftingplusaligner(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for driftingplusaligner.sh

    Help message:
    Written by Brian Bushnell
Last modified May 4, 2025

Description:  Aligns a query sequence to a reference using DriftingPlusAligner2.
The sequences can be any characters, but N is a special case.
Outputs the identity, rstart, and rstop positions.
Optionally prints a state space exploration map.
This map can be fed to visualizealignment.sh to make an image.

Usage:
driftingalignerplus.sh <query> <ref>
driftingalignerplus.sh <query> <ref> <map>
driftingalignerplus.sh <query> <ref> <map> <iterations>

Parameters:
query           A literal nucleotide sequence or fasta file.
ref             A literal nucleotide sequence or fasta file.
map             Optional output text file for matrix score space.
                Set to null for benchmarking with no visualization.
iterations      Optional integer for benchmarking multiple iterations.
simd            Add this flag to use simd mode.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for driftingplusaligner.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("driftingplusaligner.sh", args, capture_output)

def estherfilter(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for estherfilter.sh

    Help message:
    Written by Brian Bushnell
Last modified January 21, 2015

Description:  BLASTs queries against reference, and filters out hits with
              scores less than 'cutoff'.  The score is taken from column 12
              of the BLAST output.  The specific BLAST command is:
              blastall -p blastn -i QUERY -d REFERENCE -e 0.00001 -m 8

Usage:  estherfilter.sh <query> <reference> <cutoff>

For example:

estherfilter.sh reads.fasta genes.fasta 1000 > results.txt

'fasta' can be used as a fourth argument to get output in Fasta format.  Requires more memory.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for estherfilter.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("estherfilter.sh", args, capture_output)

def explodetree(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for explodetree.sh

    Help message:
    Written by Brian Bushnell
Last modified December 13, 2017

Description:   Constructs a directory and file tree of sequences
corresponding to a taxonomic tree.

Usage:  explodetree.sh in_file=<file> out=<path> tree=<file>

Parameters:
in_file=             A fasta file annotated with taxonomic data in headers, 
                such as modified RefSeq.
out=            (path) Location to write the tree.
tree=           Location of taxtree file.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for explodetree.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("explodetree.sh", args, capture_output)

def fetchproks(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for fetchproks.sh

    Help message:
    Written by Brian Bushnell
Last modified December 19, 2019

Description:  Writes a shell script to download one genome assembly
and gff per genus or species, from ncbi.  Attempts to select the best assembly
on the basis of contiguity.

Usage:  fetchproks.sh <url> <outfile> <max species per genus: int> <use best: t/f>

Examples:
fetchproks.sh ftp://ftp.ncbi.nih.gov/genomes/refseq/bacteria/ bacteria.sh 2 true
fetchproks.sh ftp://ftp.ncbi.nih.gov/genomes/refseq/archaea/ archaea.sh 0 true
fetchproks.sh ftp://ftp.ncbi.nih.gov/genomes/refseq/viral/ viral.sh 0 true
fetchproks.sh ftp://ftp.ncbi.nih.gov/genomes/refseq/protozoa/ protozoa.sh 0 true
fetchproks.sh ftp://ftp.ncbi.nih.gov/genomes/refseq/invertebrate/ invertebrate.sh 0 true
fetchproks.sh ftp://ftp.ncbi.nih.gov/genomes/refseq/fungi/ fungi.sh 0 true
fetchproks.sh ftp://ftp.ncbi.nih.gov/genomes/refseq/plant/ plant.sh 0 true
fetchproks.sh ftp://ftp.ncbi.nih.gov/genomes/refseq/vertebrate_mammalian/ vertebrate_mammalian.sh 0 true
fetchproks.sh ftp://ftp.ncbi.nih.gov/genomes/refseq/vertebrate_other/ vertebrate_other.sh 0 true

Mitochondrion, plasmid, and plastid are different and use gbff2gff.

Processing parameters:
None yet!

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for fetchproks.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("fetchproks.sh", args, capture_output)

def filterassemblysummary(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for filterassemblysummary.sh

    Help message:
    Written by Brian Bushnell
Last modified May 18, 2016

Description:   Filters NCBI assembly summaries according to their taxonomy.
The specific files are available here:

ftp://ftp.ncbi.nlm.nih.gov/genomes/ASSEMBLY_REPORTS/assembly_summary_genbank.txt
or ftp://ftp.ncbi.nlm.nih.gov/genomes/genbank/assembly_summary_genbank.txt
ftp://ftp.ncbi.nlm.nih.gov/genomes/ASSEMBLY_REPORTS/assembly_summary_refseq.txt
or ftp://ftp.ncbi.nlm.nih.gov/genomes/refseq/assembly_summary_refseq.txt

Usage:  filterassemblysummary.sh in_file=<input file> out=<output file> tree=<tree file> table=<table file> ids=<numbers> level=<name or number>

Standard parameters:
in_file=<file>       Primary input.
out=<file>      Primary output.
overwrite=f     (ow) Set to false to force the program to abort rather than
                overwrite an existing file.

Processing parameters:
level=          Taxonomic level, such as phylum.  Filtering will operate on
                sequences within the same taxonomic level as specified ids.
reqlevel=       Require nodes to have ancestors at these levels.  For example,
                reqlevel=species,genus would ban nodes that are not defined
                at both the species and genus levels.
ids=            Comma-delimited list of NCBI numeric IDs.
names=          Alternately, a list of names (such as 'Homo sapiens').
                Note that spaces need special handling.
include=f       'f' will discard filtered sequences, 't' will keep them.
tree=           A taxonomic tree made by TaxTree, such as tree.taxtree.gz.
table=          A table translating gi numbers to NCBI taxIDs.
                Only needed if gi numbers will be used.
* Note *
Tree and table files are in /global/projectb/sandbox/gaag/bbtools/tax
For non-Genepool users, or to make new ones, use taxtree.sh and gitable.sh

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for filterassemblysummary.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("filterassemblysummary.sh", args, capture_output)

def filterbarcodes(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for filterbarcodes.sh

    Help message:
    Written by Brian Bushnell
Last modified February 17, 2015

Description: Filters barcodes by quality, and generates quality histograms.

Usage:       filterbarcodes.sh in_file=<file> out=<file> maq=<integer>

Input parameters:
in_file=<file>       Reads that have already been muxed with barcode qualities using mergebarcodes.sh.
int=auto        (interleaved) If true, forces fastq input to be paired and interleaved.
qin_file=auto        ASCII offset for input quality.  May be 33 (Sanger), 64 (Illumina), or auto.

Output parameters:
out=<file>      Write filtered reads here.  'out=stdout.fq' will pipe to standard out.
cor=<file>      Correlation between read and index qualities.
bqhist=<file>   Barcode quality histogram by position.
baqhist=<file>  Barcode average quality histogram.
bmqhist=<file>  Barcode min quality histogram.
overwrite=t     (ow) Set to false to force the program to abort rather than overwrite an existing file.
ziplevel=2      (zl) Set to 1 (lowest) through 9 (max) to change compression level; lower compression is faster.
fastawrap=80    Length of lines in fasta output.
qout=auto       ASCII offset for output quality.  May be 33 (Sanger), 64 (Illumina), or auto (same as input).
maq=0           Filter reads with barcode average quality less than this.
mmq=0           Filter reads with barcode minimum quality less than this.

Other parameters:
pigz=t          Use pigz to compress.  If argument is a number, that will set the number of pigz threads.
unpigz=t        Use pigz to decompress.

Java Parameters:
-Xmx                This will set Java's memory usage, overriding autodetection.
                    -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom               This flag will cause the process to exit if an
                    out-of-memory exception occurs.  Requires Java 8u92+.
-da                 Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for filterbarcodes.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("filterbarcodes.sh", args, capture_output)

def filterbycoverage(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for filterbycoverage.sh

    Help message:
    Written by Brian Bushnell
Last modified May 3, 2016

Description:  Filters an assembly by contig coverage.
The coverage stats file can be generated by BBMap or Pileup.

Usage:  filterbycoverage.sh in_file=<assembly> cov=<coverage stats> out=<filtered assembly> mincov=5

Parameters:
in_file=<file>       File containing input assembly.
cov=<file>      File containing coverage stats generated by pileup.
cov0=<file>     Optional file containing coverage stats before normalization.
out=<file>      Destination of clean output assembly.
outd=<file>     (outdirty) Destination of dirty output containing only removed contigs.
minc=5          (mincov) Discard contigs with lower average coverage.
minp=40         (minpercent) Discard contigs with a lower percent covered bases.
minr=0          (minreads) Discard contigs with fewer mapped reads.
minl=1          (minlength) Discard contigs shorter than this (after trimming).
trim=0          (trimends) Trim the first and last X bases of each sequence.
ratio=0         If cov0 is set, contigs will not be removed unless the coverage ratio (of cov to cov0) is at least this (0 disables it).
ow=t            (overwrite) Overwrites files that already exist.
app=f           (append) Append to files that already exist.
zl=4            (ziplevel) Set compression level, 1 (low) to 9 (max).

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for filterbycoverage.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("filterbycoverage.sh", args, capture_output)

def filterbyname(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for filterbyname.sh

    Help message:
    Written by Brian Bushnell
Last modified September 1, 2016

Description:  Filters reads by name.

Usage:  filterbyname.sh in_file=<file> in2=<file2> out=<outfile> out2=<outfile2> names=<string,string,string> include=<t/f>

in2 and out2 are for paired reads and are optional.
If input is paired and there is only one output file, it will be written interleaved.
Important!  Leading > and @ symbols are NOT part of sequence names;  they are part of
the fasta, fastq, and sam specifications.  Therefore, this is correct:
names=e.coli_K12
And these are incorrect:
names=>e.coli_K12
names=@e.coli_K12

Parameters:
include=f       Set to 'true' to include the filtered names rather than excluding them.
substring=f     Allow one name to be a substring of the other, rather than a full match.
                   f: No substring matching.
                   t: Bidirectional substring matching.
                   header: Allow input read headers to be substrings of names in list.
                   name: Allow names in list to be substrings of input read headers.
prefix=f        Allow names to match read header prefixes.
case=t          (casesensitive) Match case also.
ow=t            (overwrite) Overwrites files that already exist.
app=f           (append) Append to files that already exist.
zl=4            (ziplevel) Set compression level, 1 (low) to 9 (max).
int=f           (interleaved) Determines whether INPUT file is considered interleaved.
names=          A list of strings or files.  The files can have one name per line, or
                be a standard read file (fasta, fastq, or sam).
minlen=0        Do not output reads shorter than this.
ths=f           (truncateheadersymbol) Ignore a leading @ or > symbol in the names file.
tws=f           (truncatewhitespace) Ignore leading or trailing whitespace in the names file.
truncate=f      Set both ths and tws at the same time.

Positional parameters:
These optionally allow you to output only a portion of a sequence.  Zero-based, inclusive.
Intended for a single sequence and include=t mode.
from=-1         Only print bases starting at this position.
to=-1           Only print bases up to this position.
range=          Set from and to with a single flag.


Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

To read from stdin, set 'in_file=stdin'.  The format should be specified with an extension, like 'in_file=stdin.fq.gz'
To write to stdout, set 'out=stdout'.  The format should be specified with an extension, like 'out=stdout.fasta'

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for filterbyname.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("filterbyname.sh", args, capture_output)

def filterbysequence(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for filterbysequence.sh

    Help message:
    Written by Brian Bushnell
Last modified November 22, 2023

Description:  Filters sequences by exact sequence matches.
This can also handle inexact matches but is extremely slow in that mode.

Usage:  filterbysequence.sh in_file=<file> out=<file> ref=<file> include=<t/f>

I/O Parameters:
in_file=             Primary input. 'in2' will specify a second file.
out=            Primary out. 'out2' will specify a second file.
ref=            A reference file or comma-delimited list of files.
literal=        A literal sequence or comma-delimited list of sequences.
ow=t            (overwrite) Overwrites files that already exist.

Processing Parameters:
include=f       Set to 'true' to include the filtered sequences rather
                than excluding them.
rcomp=t         Match reverse complements as well.
case=f          (casesensitive) Require matching case.
storebases=t    (sb) Store ref bases.  Requires more memory.  If false,
                case-sensitive matching cannot be done, and the matching
                will be probabilistic based on 128-bit hashcodes.
threads=auto    (t) Specify the number of worker threads.
subs=0          Maximum number of substitutions allowed.
mf=0.0          (mismatchfraction) Maximum fraction of bases that can
                mismatch.  The actual number allowed is the max of subs
                and mf*min(query.length, ref.length).
lengthdif=0     Maximum allowed length difference between query and ref.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for filterbysequence.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("filterbysequence.sh", args, capture_output)

def filterbytaxa(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for filterbytaxa.sh

    Help message:
    Written by Brian Bushnell
Last modified June 18, 2018

Description:   Filters sequences according to their taxonomy,
as determined by the sequence name.  Sequences should
be labeled with a gi number, NCBI taxID, or species name.

Usage:  filterbytaxa.sh in_file=<input file> out=<output file> tree=<tree file> table=<table file> ids=<numbers> level=<name or number>

I/O parameters:
in_file=<file>       Primary input, or read 1 input.
out=<file>      Primary output, or read 1 output.
results=<file>  Optional; prints a list indicating which taxa were retained.
overwrite=f     (ow) Set to false to force the program to abort rather than
                overwrite an existing file.
showspeed=t     (ss) Set to 'f' to suppress display of processing speed.
ziplevel=2      (zl) Set to 1 (lowest) through 9 (max) to change compression
                level; lower compression is faster.

Processing parameters:
level=          Taxonomic level, such as phylum.  Filtering will operate on
                sequences within the same taxonomic level as specified ids.
                If not set, only matches to a node or its descendants will 
                be considered.
reqlevel=       Require nodes to have ancestors at these levels.  For example,
                reqlevel=species,genus would ban nodes that are not defined
                at both the species and genus levels.
ids=            Comma-delimited list of NCBI numeric IDs.  Can also be a
                file with one taxID per line.  Names (like bacteria) are also
                acceptable.
include=f       'f' will discard filtered sequences, 't' will keep them.
besteffort=f    Intended for include mode.  Iteratively increases level
                while the input file has no hits to the tax list.
tree=<file>     Specify a TaxTree file like tree.taxtree.gz.  
                On Genepool, use 'auto'.
gi=<file>       Specify a gitable file like gitable.int1d.gz. Only needed
                if gi numbers will be used.  On Genepool, use 'auto'.
accession=      Specify one or more comma-delimited NCBI accession to taxid
                files.  Only needed if accesions will be used; requires ~45GB
                of memory.  On Genepool, use 'auto'.
printnodes=t    Print the names of nodes added to the filter.
requirepresent=t   Crash with an error message if a header cannot be resolved
                   to a taxid.

String-matching parameters:
regex=          Filter names matching this Java regular expression.
contains=       Filter names containing this substring (case-insensitive).

* Note *
Tree and table files are in /global/projectb/sandbox/gaag/bbtools/tax
For non-Genepool users, or to make new ones, use taxtree.sh and gitable.sh

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for filterbytaxa.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("filterbytaxa.sh", args, capture_output)

def filterbytile(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for filterbytile.sh

    Help message:
    Written by Brian Bushnell
Last modified November 18, 2024

Description:  Filters reads based on positional quality over a flowcell.
Quality is estimated based on quality scores and kmer uniqueness; ideally,
the input to this program will already be adapter-trimmed and 
quality-score recalibrated.  PhiX, if present, will be used to estimate
absolute error rates from kmer uniqueness rates.
All reads within a small unit of area called a micro-tile are averaged,
then the micro-tile is either retained or discarded as a unit depending
on whether its metrics fall outside of a specified range (generally some
number of standard deviations away from average).
This program can process individual libraries, but achieves optimal 
performance when processing one lane at a time.  For this purpose it is best
to use as much memory as possible (e.g., 200GB RAM for 5 billion reads),
though it will still work with much less memory.

Please read bbmap/docs/guides/FilterByTileGuide.txt for more information.


Usage:	filterbytile.sh in_file=<input> out=<output>

Input parameters:
in_file=<file>           Primary input file.
in2=<file>          Second input file for paired reads in twin files.
indump=<file>       Specify an already-made dump file to use instead of
                    analyzing the input reads.
barcodes=<file>     Optional list of expected barcodes, one per line.
reads=-1            Process this number of reads, then quit (-1 means all).
interleaved=auto    Set true/false to override autodetection of the
                    input file as paired interleaved.

Output parameters:
out=<file>          Output file for filtered reads.
dump=<file>         Write a summary of quality information by coordinates.
                    This can be later used for filtering individual libraries.
counts=<file>       Write barcode counts.


Tile parameters:
xsize=500           Initial width of micro-tiles.  For NovaSeqX use 520.
ysize=500           Initial height of micro-tiles.  For NovaSeqX use 590.
size=               Allows setting xsize and ysize to the same value.
target=1600         Iteratively widen the micro-tiles until they contain
                    an average of at least this many reads.
alignedreads=250    Average aligned reads per tile for error rate calibration.

A micro-tile is discarded if any of several metrics indicate a problem.
The metrics are kmer uniqueness (u), average quality (q), probability
of being error-free (e), and poly-G rate (pg).  
Each has 3 parameters: deviations (d), fraction (f), and absolute (a).  
After calculating the difference (delta) between a micro-tile and average, 
it is discarded only if all three of these conditions are true for at least
one metric (using quality as the example):
1) delta is greater than (qd) standard deviations.
2) delta is greater than average times the fraction (qf).
3) delta is greater than the absolute value (qa).
Tiles are also marked for discard if they have too few reads to calculate
statistics or an inferred error rate (ier) above an absolute value; ier
does not need deviations because it is calibrated. 

Filtering parameters:
udeviations=1.5     (ud) Standard deviations for uniqueness discarding.
qdeviations=2.4     (qd) Standard deviations for quality discarding.
edeviations=3.0     (ed) Standard deviations for error-free probablity. 
pgdeviations=1.4    (pgd) Standard deviations for poly-G discarding.
ufraction=0.01      (uf) Min fraction for uniqueness discarding.
qfraction=0.08      (qf) Min fraction for quality discarding.
efraction=0.2       (ef) Min fraction for error-free probablity discarding.
pgfraction=0.2      (pgf) Min fraction for poly-G discarding.
uabsolute=1         (ua) Min absolute value for uniqueness discarding.
qabsolute=2.0       (qa) Min absolute value for quality discarding.
eabsolute=6         (ea) Min absolute value for error-free probablity.
pgabsolute=0.2      (pga) Min absolute value for poly-G discarding.
ier=0.012           (inferrederrorrate) Maximum predicted base error rate.
                    A more recent addition and usually superior to using
                    uniqueness deviations, if ~1% PhiX is spiked in.
mdf=0.4             (maxdiscardfraction) Don't discard more than this 
                    fraction of tiles no matter how bad the data is.

Alignment parameters:
Note: Alignment will only be performed if there is no input sam file,
and nothing will go to the output sam file unless internal alignment occurs.
samin_file=<file>        Optional aligned sam input file for error rate analysis.
samout=<file>       Output file for aligned reads.  Can be sam or fastq.
align=true          If no sam file is present, align reads to the reference.
alignref=phix       Reference for aligning reads if there is no sam file.
alignk1=17          Kmer length for seeding alignment to reference.
alignk2=13          Kmer length for seeding alignment of unaligned reads
                    with an aligned mate.
minid1=0.62         Minimum identity to accept individual alignments.
minid2=0.54         Minimum identity for aligning reads with aligned mates.
alignmm1=1          Middle mask length for alignk1.
alignmm2=1          Middle mask length for alignk2.

Note: Alignment is optional, but allows translation of kmer depth to error 
rate at high resolution.  The default reference, phiX, is nonrepetitive down
to k=13.  For internal alignment, the reference must be a short single 
sequence that is almost completely nonrepetitive at the selected kmer length.
If a sam file is used, any reference is OK and the alignment parameters are
ignored, but it should have few mutations.  A SNP rate of 1/1000 (like human)
is acceptable but sets an inferred error rate floor of 0.001 (Q30).

Other parameters:
usekmers=t          Load kmers to calculate uniqueness and depth.
lowqualityonly=t    (lqo) Only discard low quality reads within bad areas, 
                    rather than the whole micro-tile.  This usually discards
                    most of the reads in the bad micro-tiles anyway.
recalibrate=f       Recalibrate reads while filling tile info.
                    Requires calibration matrices from CalcTrueQuality.
                    Changes sam output, but not positionally-filter output.
dmult=-.1           Lower increases amount removed when lqo=t.  At 0, only 
                    reads with below average quality (or polyG) are removed.
idmaskwrite=15      A bitmask, (2^N-1), controlling the fraction of kmers
                    loaded in the bloom filter.  15 means 1/16th are loaded.
                    0 uses all kmers.
idmaskread=7        Controls fraction of kmers read when counting uniqueness.
k=31                Kmer length for Bloom filter (uniqueness calculation).
hashes=3            Bloom filter hashes.
cbits=2             Bloom filter bits per cell.
merge=f             Merge reads for insert and error rate statistics.
                    This can make the program take ~50% longer and only
                    affects the dump file.

Java Parameters:
-Xmx                This will set Java's memory usage, overriding autodetection.
                    -Xmx20g will specify 20 GB of RAM; -Xmx200m will specify 
                    200 MB.  The max is typically 85% of physical memory.
-eoom               This flag will cause the process to exit if an
                    out-of-memory exception occurs.  Requires Java 8u92+.
-da                 Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for filterbytile.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("filterbytile.sh", args, capture_output)

def filterlines(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for filterlines.sh

    Help message:
    Written by Brian Bushnell
Last modified July 6, 2015

Description:  Filters lines by exact match or substring.

Usage:  filterlines.sh in_file=<file> out=<file> names=<file> include=<t/f>

Parameters:
include=f       Set to 'true' to include the filtered names rather than excluding them.
prefix=f        Allow matching of only the line's prefix (all characters up to first whitespace).
substring=f     Allow one name to be a substring of the other, rather than a full match.
                   f:    No substring matching.
                   t:    Bidirectional substring matching.
                   line: Allow input lines to be substrings of names in list.
                   name: Allow names in list to be substrings of input lines.
case=t          (casesensitive) Match case also.
ow=t            (overwrite) Overwrites files that already exist.
app=f           (append) Append to files that already exist.
zl=4            (ziplevel) Set compression level, 1 (low) to 9 (max).
names=          A list of strings or files, comma-delimited.  Files must have one name per line.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

To read from stdin, set 'in_file=stdin'.  The format should be specified with an extension, like 'in_file=stdin.fq.gz'
To write to stdout, set 'out=stdout'.  The format should be specified with an extension, like 'out=stdout.fasta'

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for filterlines.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("filterlines.sh", args, capture_output)

def filtersam(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for filtersam.sh

    Help message:
    Written by Brian Bushnell
Last modified September 20, 2022

Description:  Filters a sam file to remove reads with variations unsupported
by other reads (bad vars, aka bad subs).  For particularly bad data,
it may be advisable to iteratively re-call variants and re-run FilterSam.
Calling variants may be performed like this:

callvariants.sh in_file=mapped.sam ref=ref.fa out=vars.vcf clearfilters minreads=2

Usage:  filtersam.sh in_file=<file> out=<file> vcf=<file>

Parameters:
in_file=<file>       Input sam or bam file.
ref=<file>      Optional fasta reference file.
out=<file>      Output file for good reads.
outb=<file>     Output file for bad reads.
vcf=<file>      VCF file of variants called from these reads.
vars=<file>     Alternatively, variants can be provided in CallVariants'
                native output format.
mbv=2           (maxbadvars) Discarded reads with more bad vars than this.
mbad=2          (maxbadalleledepth) A var is bad if the allele depth is at
                most this much.
mbaf=0.01       (maxbadalleledepth) A var is bad if the allele fraction is at
                most this much.  The more stringent of mbad or mbaf is used,
                so in low depth regions mbad is dominant while in high depth 
                regions mbaf is more important.  Vars are considered bad if
                they fail either threshold (meaning ad<=mbad or af<=mbaf).
mbrd=2          (minbadreaddepth) Substitutions may only be considered
                bad if the total read depth spanning the variant is
                at least this much.
border=5        (minenddist) Ignore vars within this distance of read ends.
sub=t           Consider bad substitutions.
ins=f           Consider bad insertions.
del=f           Consider bad deletions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for filtersam.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("filtersam.sh", args, capture_output)

def filtersilva(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for filtersilva.sh

    Help message:
    Written by Brian Bushnell
Last modified Jan 27, 2020

Description:  Removes .

Usage:           filtersilva.sh in_file=x.fa out=y.fa

Standard parameters:
in_file=<file>       Input file.
out=<file>      Output file.

Additional files:
tree=auto       Path to TaxTree.


Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-da             Disable assertions.

For more detailed information, please read /bbmap/docs/guides/BBSketchGuide.txt.
Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for filtersilva.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("filtersilva.sh", args, capture_output)

def filtersubs(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for filtersubs.sh

    Help message:
    Written by Brian Bushnell
Last modified August 22, 2024

Description:  Filters a sam file to select only reads with substitution errors
for bases with quality scores in a certain interval.  Used for manually 
examining specific reads that may have incorrectly calibrated quality scores.

Usage:  filtersubs.sh in_file=<file> out=<file> minq=<number> maxq=<number>

Parameters:
in_file=<file>       Input sam or bam file.
out=<file>      Output file.
minq=0          Keep only reads with substitutions of at least this quality.
maxq=99         Keep only reads with substitutions of at most this quality.
countindels=t   Also keep reads with indels in the quality range. 
minsubs=1       Require at least this many substitutions.
minclips=0      Discard reads with more clip operations than this.
maxclips=-1     If nonnegative, discard reads with more clip operations.
keepperfect=f   Also keep error-free reads.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for filtersubs.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("filtersubs.sh", args, capture_output)

def filtervcf(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for filtervcf.sh

    Help message:
    Written by Brian Bushnell
Last modified July 10, 2025

Description:  Filters VCF files by position or other attributes.
Filtering by optional fields (such as allele frequency) require VCF files
generated by CallVariants.

Usage:  filtervcf.sh in_file=<file> out=<file>

I/O parameters:
in_file=<file>       Input VCF.
out=<file>      Output VCF.
ref=<file>      Reference fasta (optional).
overwrite=f     (ow) Set to false to force the program to abort rather than
                overwrite an existing file.
bgzip=f         Use bgzip for gzip compression.
splitalleles=f  Split multi-allelic lines into multiple lines.
splitsubs=f     Split multi-base substitutions into SNPs.
canonize=t      Trim variations down to a canonical representation.

Position-filtering parameters:
minpos=         Ignore variants not overlapping this range.
maxpos=         Ignore variants not overlapping this range.
contigs=        Comma-delimited list of contig names to include. These 
                should have no spaces, or underscores instead of spaces.
invert=f        Invert position filters.

Type-filtering parameters:
sub=t           Keep substitutions.
del=t           Keep deletions.
ins=t           Keep insertions.

Variant-quality filtering parameters:
minreads=0              Ignore variants seen in fewer reads.
minqualitymax=0         Ignore variants with lower max base quality.
minedistmax=0           Ignore variants with lower max distance from read ends.
minmapqmax=0            Ignore variants with lower max mapq.
minidmax=0              Ignore variants with lower max read identity.
minpairingrate=0.0      Ignore variants with lower pairing rate.
minstrandratio=0.0      Ignore variants with lower plus/minus strand ratio.
minquality=0.0          Ignore variants with lower average base quality.
minedist=0.0            Ignore variants with lower average distance from ends.
minavgmapq=0.0          Ignore variants with lower average mapq.
minallelefraction=0.0   Ignore variants with lower allele fraction.  This
                        should be adjusted for high ploidies.
minid=0                 Ignore variants with lower average read identity.
minscore=0.0            Ignore variants with lower Phred-scaled score.
clearfilters            Reset all variant filters to zero.

There are additionally max filters for score, quality, mapq, allelefraction,
and identity.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for filtervcf.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("filtervcf.sh", args, capture_output)

def findrepeats(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for findrepeats.sh

    Help message:
    Written by Brian Bushnell
Last modified July 5, 2023

Description:  Finds repeats in a genome.

No alignment is done; a sequence is considered to be a repeat of depth D if
all kmers within it have a depth of at least D.  Gaps of up to length G
consecutive kmers with lower counts may be allowed, which typically finds
far more and substantially longer repeats even with a small G.

Usage:  findrepeats.sh in_file=<input file> out=<output file>

Standard parameters:
in_file=<file>       Primary input (the genome fasta).
out=<file>      Primary output (list of repeats as TSV).  If no file is
                given this will be printed to screen; to suppress printing,
                use 'out=null'.
outs=<file>     (outsequence) Optional sequence output, for printing or 
                masking repeats.
overwrite=f     (ow) False ('f') forces the program to abort rather than
                overwrite an existing file.
showspeed=t     (ss) Set to 'f' to suppress display of processing speed.
ziplevel=2      (zl) Set to 1 (lowest) through 9 (max) to change compression
                level; lower compression is faster.

Processing parameters:
k=31            Kmer length to use (range is 1-31; 31 is recommended).
gap=0           Maximum allowed gap length within a repeat, in kmers.
                This allows inexact repeats.  Note that a 1bp mismatch
                will spawn a length K gap.
qhdist=0        Hamming distance within a kmer; allows inexact repeats.
                Values above 0 become exponentially slower.
minrepeat=0     Minimum repeat length to report, in bases.  Nothing shorter
                than kmer length will be found regardless of this value.
mindepth=2      Ignore copy counts below mindepth. 
maxdepth=-1     If positive, copy counts greater than this will be reported
                as this number.  This can greatly increase speed in rare 
                cases of thousand+ copy repeats.
preview=27      Print this many characters of the repeat per line.  Set to 0
                to suppress (may save memory).
mask=f          Write sequence with masked repeats to 'outs'. Possible values:
                   f: Do not mask.
                   t: Mask (by default, 't' or 'true' are the same as 'soft').
                   soft: Convert masked bases to lower case.
                   hard: Convert masked bases to 'N'.
                   Other characters: Convert masked bases to that character.
print=t         (printrepeats) Print repeat sequence to outs.  'print' and
                'mask' are mutually exclusive so enabling one will disable
                the other.
weak=f          (weaksubsumes) Ignore repeats that are weakly subsumed by 
                other repeats. A repeat is subsumed if there is another repeat
                with greater depth at the same coordinates.  Since a 3-copy 
                repeat is also a 2-copy repeat, only the 3-copy repeat will be
                reported.  However, in the case that the 3-copy repeat is
                inexact (has gaps) and the 2-copy repeat is perfect, both will
                be reported when 'weak=f' as per default.  If you set the
                'weak=t' flag, only the highest-depth version will be reported
                even if it has more gaps.  In either case all 3 repeats would
                be reported, but with 'weak=f' some copies would be reported
                twice for the same coordinates, once as a depth-2 perfect 
                repeat and again as a depth-3 imperfect repeat.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for findrepeats.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("findrepeats.sh", args, capture_output)

def fixgaps(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for fixgaps.sh

    Help message:
    Written by Brian Bushnell
Last modified September 11, 2019

Description:  Uses paired read insert sizes to estimate the correct
length of scaffold gaps, and resizes incorrectly-sized gaps.

Usage:  fixgaps.sh in_file=mapped.sam ref=scaffolds.fa out=fixed.fa

Standard parameters:
in_file=<file>       Reads mapped to the reference; should be sam or bam.
ref=<file>      Reference; may be fasta or fastq.
out=<file>      Modified reference; may be fasta or fastq.
overwrite=f     (ow) Set to false to force the program to abort rather than
                overwrite an existing file.

Processing parameters:
gap=10          Consider any consecutive streak of Ns at least this long to
                be a scaffold break.  Gaps will not be resized to less than
                this.
border=0.4      Ignore the outermost (border*readlen) of an insert (read pair)
                when incrementing coverage.  A higher value is more accurate 
                but requires more coverage and/or longer inserts.  Range: 0-1.
mindepth=10     Minimum spanning read pairs to correct a gap.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for fixgaps.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("fixgaps.sh", args, capture_output)

def fungalrelease(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for fungalrelease.sh

    Help message:
    Written by Brian Bushnell
Last modified April 24, 2019

Description:  Reformats a fungal assembly for release.
Also creates contig and agp files.

Usage:  fungalrelease.sh in_file=<input file> out=<output file>

I/O parameters:
in_file=<file>           Input scaffolds.
out=<file>          Output scaffolds.
outc=<file>         Output contigs.
qfin_file=<file>         Optional quality scores input.
qfout=<file>        Optional quality scores output.
qfoutc=<file>       Optional contig quality scores output.
agp=<file>          Output AGP file.
legend=<file>       Output name legend file.
overwrite=f         (ow) Set to false to force the program to abort rather than
                    overwrite an existing file.

Processing parameters:
fastawrap=60        Wrap length for fasta lines.
tuc=t               Convert sequence to upper case.
baniupac=t          Crash on encountering a non-ACGTN base call.
mingap=10           Expand all gaps (Ns) to be at least this long.
mingapin_file=1          Only expand gaps that are at least this long.
sortcscaffolds=t    Sort scaffolds descending by length.
sortcontigs=f       Sort contigs descending by length.
renamescaffolds=t   Rename scaffolds to 'scaffold_#'.
scafnum=1           Number of first scaffold.
renamecontigs=f     Rename contigs to 'contig_#' instead of 'scafname_c#'.
contignum=1         Number of first contig; only used if renamecontigs=t.
minscaf=1           Only retain scaffolds at least this long.
mincontig=1         Only retain contigs at least this long.

Java Parameters:
-Xmx                This will set Java's memory usage, overriding autodetection.
                    -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom               This flag will cause the process to exit if an
                    out-of-memory exception occurs.  Requires Java 8u92+.
-da                 Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for fungalrelease.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("fungalrelease.sh", args, capture_output)

def fuse(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for fuse.sh

    Help message:
    Written by Brian Bushnell
Last modified August 11, 2023

Description:  Fuses sequences together, padding gaps with Ns.

Usage:   fuse.sh in_file=<input file> out=<output file> pad=<number of Ns>

Parameters:
in_file=<file>       The 'in_file=' flag is needed if the input file is not the 
                first parameter.  'in_file=stdin' will pipe from standard in.
out=<file>      The 'out=' flag is needed if the output file is not the 
                second parameter.  'out=stdout' will pipe to standard out.
pad=300         Pad this many N between sequences.
maxlen=2g       If positive, don't make fused sequences longer than this.
quality=30      Fake quality scores, if generating fastq from fasta.
overwrite=t     (ow) Set to false to force the program to abort rather 
                than overwrite an existing file.
ziplevel=2      (zl) Set to 1 (lowest) through 9 (max) to change 
                compression level; lower compression is faster.
fusepairs=f     Default mode fuses all sequences into one long sequence.
                Setting fusepairs=t will instead fuse each pair together.
name=           Set name of output sequence.  Default is the name of
                the first input sequence.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding
                autodetection.  -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for fuse.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("fuse.sh", args, capture_output)

def gbff2gff(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for gbff2gff.sh

    Help message:
    Written by Brian Bushnell
Last modified August 14, 2019

Description:  Generates a GFF3 from a GBFF.
Only for features I care about though.

Usage:  gbff2gff.sh <gbff file> <gff file>

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for gbff2gff.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("gbff2gff.sh", args, capture_output)

def getreads(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for getreads.sh

    Help message:
    Written by Brian Bushnell
Last modified February 17, 2015

Description:  Selects reads with designated numeric IDs.

Usage:  getreads.sh in_file=<file> id=<number,number,number...> out=<file>

The first read (or pair) has ID 0, the second read (or pair) has ID 1, etc.

Parameters:
in_file=<file>       Specify the input file, or stdin.
out=<file>      Specify the output file, or stdout.
id=             Comma delimited list of numbers or ranges, in any order.
                For example:  id=5,93,17-31,8,0,12-13

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for getreads.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("getreads.sh", args, capture_output)

def gi2ancestors(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for gi2ancestors.sh

    Help message:
    Written by Brian Bushnell
Last modified June 13, 2016

Description:  Finds NCBI taxIDs of common ancestors of gi numbers.
Input should be formatted like this:
ori15	gi|818890693,gi|818890691,gi|837354594

Usage:  gi2ancestors.sh in_file=<input file> out=<output file>


Standard parameters:
in_file=<file>       Input text file with names sequence names and GI numbers.
out=<file>      Output file.
overwrite=f     (ow) Set to false to force the program to abort rather than
                overwrite an existing file.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for gi2ancestors.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("gi2ancestors.sh", args, capture_output)

def gi2taxid(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for gi2taxid.sh

    Help message:
    Written by Brian Bushnell.
Last modified December 19, 2019

Description:  Renames sequences to indicate their NCBI taxIDs.
The headers must be in NCBI or Silva format with gi numbers,
accessions, or organism names.  Only supports fasta and gff files.

Usage:  gi2taxid.sh in_file=<file> out=<file> server

Parameters:
in_file=<file>       Input sequences; required parameter.  Must be fasta.
                This can alternatively be a comma-delimited list,
                or just a bunch of space-delimited filenames, e.g.:
                gi2taxid.sh x.fa y.fa z.fa out=tid.fa tree=auto table=auto
out=<file>      Destination for renamed sequences.
invalid=<file>  Destination for headers with no taxid.
keepall=t       Keep sequences with no taxid in normal output.
prefix=t        Append the taxid as a prefix to the old header, but keep
                the old header.
title=tid       Set the title of the new number (e.g. ncbi, taxid, tid).
ziplevel=2      (zl) Compression level for gzip output.
pigz=t          Spawn a pigz (parallel gzip) process for faster 
                compression than Java.  Requires pigz to be installed.
silva=f         Parse headers in Silva format.
shrinknames=f   Replace multiple concatenated headers with the first.
deleteinvalid=f Delete the output file if there are any invalid headers.

Taxonomy file flags:
server=f        Use the taxonomy server instead of local files.
                Server mode only works for accessions (like RefSeq).
tree=           Specify a taxtree file.  On Genepool, use 'auto'.
gi=             Specify a gitable file.  On Genepool, use 'auto'.
accession=      Specify one or more comma-delimited NCBI accession to
                taxid files.  On Genepool, use 'auto'.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx800m will specify 800 megs.
                    The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for gi2taxid.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("gi2taxid.sh", args, capture_output)

def gitable(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for gitable.sh

    Help message:
    Written by Brian Bushnell.
Last modified July 29, 2019

Description:  Creates gitable.int1d from accession files:
ftp://ftp.ncbi.nih.gov/pub/taxonomy/accession2taxid/*.accession2taxid.gz
This is for use of gi numbers, which are deprecated by NCBI, and areneither 
necessary nor recemmended if accession numbers are present.
See TaxonomyGuide and fetchTaxonomy.sh for more information.

Usage:  gitable.sh shrunk.dead_nucl.accession2taxid.gz,shrunk.dead_prot.accession2taxid.gz,shrunk.dead_wgs.accession2taxid.gz,shrunk.nucl_gb.accession2taxid.gz,shrunk.nucl_wgs.accession2taxid.gz,shrunk.pdb.accession2taxid.gz,shrunk.prot.accession2taxid.gz gitable.int1d.gz

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM.  The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for gitable.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("gitable.sh", args, capture_output)

def glocalaligner(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for glocalaligner.sh

    Help message:
    Written by Brian Bushnell
Last modified May 4, 2025

Description:  Aligns a query sequence to a reference using GlocalAligner.
Explores the entire matrix.
The sequences can be any characters, but N is a special case.
Outputs the identity, rstart, and rstop positions.
Optionally prints a state space exploration map.
This map can be fed to visualizealignment.sh to make an image.

Usage:
glocalaligner.sh <query> <ref>
glocalaligner.sh <query> <ref> <map>
glocalaligner.sh <query> <ref> <map> <iterations>

Parameters:
query           A literal nucleotide sequence or fasta file.
ref             A literal nucleotide sequence or fasta file.
map             Optional output text file for matrix score space.
                Set to null for benchmarking with no visualization.
iterations      Optional integer for benchmarking multiple iterations.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for glocalaligner.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("glocalaligner.sh", args, capture_output)

def gradebins(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for gradebins.sh

    Help message:
    Written by Brian Bushnell
Last modified June 20, 2025

Description:  Grades metagenome bins for completeness and contamination.
The contigs can be labeled with their taxID; in which case the header should
contain 'tid_X' somewhere where X is a number unique to their proper genome.
Alternately, CheckM2 and/or EukCC output can be fed to it.
Do not include a 'chaff' file (for unbinned contigs) when grading.
Completeness Score is (sum of completeness*size)/(total size) for all bins.
Contamination Score is (sum of contam*size)/(total size) for all bins.
Total Score is (sum of (completeness-5*contam)^2) for all bins.
Bin Definitions:
UHQ: >=99% complete and <=1% contam (subset of VHQ)
VHQ: >=95% complete and <=2% contam (subset of HQ)
HQ:  >=90% complete and <=5% contam
MQ:  >=50% complete and <=10% contam, but not HQ
LQ:  <50% complete or >10% contam
VLQ: <20% complete or >5% contam    (subset of LQ)

Usage:  gradebins.sh ref=assembly bin*.fa
or
gradebins.sh ref=assembly.fa in_file=bin_directory
or
gradebins.sh taxin_file=tax.txt in_file=bins

Input parameters:
ref=<file>      The original assembly that was binned.
in_file=<directory>  Location of bin fastas.
checkm=<file>   Optional CheckM2 quality_report.tsv file or directory.
eukcc=<file>    Optional EukCC eukcc.csv file or directory.
cami=<file>     Optional binning file from CAMI which indicates contig TaxIDs.
taxin_file=<file>    Optional file with taxIDs and sizes (instead of loading ref).
                Does not need to include taxIDs.  The tax file loads faster.
gtdb=<file>     Optional gtdbtk file.
gff=<file>      Optional gff file.
imgmap=<file>   Optional IMG map file, for renamed IMG gff input.
spectra=<file>  Optional path to QuickClade index.
cov=<file>      Optional path to QuickBin coverage file.
loadmt=t        Load bins multithreaded.

Output parameters:
report=<file>   Report on bin size, quality, and taxonomy.
taxout=<file>   Generate a tax file from the reference (for use with taxin).
hist=<file>     Cumulative bin size and contamination histogram.
ccplot=<file>   Per-bin completeness/contam data.
contamhist=<file> Histogram plotting #bins or bases vs %contam.

Processing parameters:
userna=f        Require rRNAs and tRNAs for HQ genomes.  This needs either
                a gff file or the callgenes flag.  Specifically, HQ and
                subtypes require at least 1 16S, 23S, and 5S, plus 18 tRNAs.
callgenes=f     Call rRNAs and tRNAs.  Suboptimal for some RNA types.
aligner=ssa2    Do not change this.
quickclade=f    Assign taxonomy using QuickClade.


Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for gradebins.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("gradebins.sh", args, capture_output)

def grademerge(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for grademerge.sh

    Help message:
    Written by Brian Bushnell
Last modified February 17, 2015

Description:  Grades correctness of merging synthetic reads with headers 
generated by RandomReads and re-headered by RenameReads.

Usage:  grademerge.sh in_file=<file>

Parameters:
in_file=<file>       Specify the input file, or 'stdin'.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for grademerge.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("grademerge.sh", args, capture_output)

def gradesam(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for gradesam.sh

    Help message:
    Written by Brian Bushnell
Last modified May 23, 2014

Description:  Grades mapping correctness of a sam file of synthetic reads with headers generated by RandomReads3.java

Usage:   gradesam.sh in_file=<sam file> reads=<number of reads>

Parameters:
in_file=<file>       Specify the input sam file, or stdin.
reads=<int>     Number of reads in mapper's input (i.e., the fastq file).
thresh=20       Max deviation from correct location to be considered 'loosely correct'.
blasr=f         Set to 't' for BLASR output; fixes extra information added to read names.
ssaha2=f        Set to 't' for SSAHA2 or SMALT output; fixes incorrect soft-clipped read locations.
quality=3       Reads with a mapping quality of this or below will be considered ambiguously mapped.
bitset=t        Track read ID's to detect secondary alignments.
                Necessary for mappers that incorrectly output multiple primary alignments per read.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for gradesam.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("gradesam.sh", args, capture_output)

def icecreamfinder(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for icecreamfinder.sh

    Help message:
    Written by Brian Bushnell
Last modified May 6, 2020

Description:  Finds PacBio reads containing inverted repeats.
These are candidate triangle reads (ice cream cones).
Either ice cream cones only, or all inverted repeats, can be filtered.

Usage:  icecreamfinder.sh in_file=<input file> out=<output file> outb=<bad reads>

File I/O parameters:
in_file=<file>       Primary input.
out=<file>      (outgood) Output for good reads.
outa=<file>     (outambig) Output for with inverted repeats, but it is unclear
                whether that is natural or artifactual.
outb=<file>     (outbad) Output for reads suspected as chimeric.
outj=<file>     (outjunction) Output for junctions in inverted repeat reads.
stats=<file>    Print screen output here instead of to the screen.
json=f          Print stats as json.
asrhist=<file>  Adapter alignment score ratio histogram.
irsist=<file>   Inverted repeat alignment score ratio histogram.
ambig=          Determine where ambiguous reads are sent.  They will ALWAYS
                be sent to outa if specified.  If not, they will be sent
                to outg (good) unless overridden by this flag.  Options:
                   ambig=good:  Send ambiguous reads to outg.
                   ambig=bad:  Send ambiguous reads to outb.
                   ambig=good,bad:  Send ambiguous reads to outg and outb.
                   ambig=null:  Do not send to outg or outb.
overwrite=f     (ow) Set to false to force the program to abort rather than
                overwrite an existing file.
ziplevel=2      (zl) Set to 1 (lowest) through 9 (max) to change compression
                level; lower compression is faster.

Processing parameters:
alignrc=t       Align the reverse-complement of the read to itself to look 
                for inverted repeats.
alignadapter=t  Align adapter sequence to reads.
adapter=        default: ATCTCTCTCAACAACAACAACGGAGGAGGAGGAAAAGAGAGAGAT
icecreamonly=t  (ico) Only remove suspected triangle reads.  Otherwise, all
                inverted repeats are removed.
ksr=t           (keepshortreads) Keep non-triangle reads from triangle ZMWs.
kzt=f           (keepzmwstogether) Send all reads from a ZMW to the same file.
targetqlen=352  (qlen) Make queries of this length from a read tip.
qlenfraction=0.15   Try to make queries at most this fraction of read length.
                For short reads this will override targetqlen.
minlen=40       Do not output reads shorter than this, after trimming.
minqlen=100     Do not make queries shorter than this.  For very short
                reads this will override qlenfraction.
shortfraction=0.4   Only declare a read to be a triangle if the short half 
                of the repeat is at least this fraction of read length.
ccs=f           Input reads are CCS, meaning they are all full-pass.
                In this case you should increase minratio.
trim=t          Trim adapter sequence from read tips.
trimpolya=f     Trim terminal poly-A and poly-T sequences, for some isoseq
                libraries.
minpolymer=5    Don't trim poly-A sequence shorter than this.
polyerror=0.2   Max error rate for trimming poly-A.


Speed and sensitivity:
jni=f           Enable C code for higher speed and identical results.
minratio=       Fraction of maximal alignment score to consider as matching.
                Higher is more stringent; lower allows more sequencing errors.
                This is VERY SENSITIVE.  For error-corrected reads it should
                be set higher.  It is roughly the expected identity of one
                read to another (double the per-read error rate).
minratio1=0.59  Set minratio for the first alignment pass only.
minratio2=0.64  Set minratio for the second alignment pass only.
adapterratio=0.18   Initial adapter detection sensitivity; affects speed.
adapterratio2=.325  Final adapter detection sensitivity.
minscore=-800   Exit alignment early if score drops below this.

Entropy parameters (recommended setting is 'entropy=t'):
minentropy=-1   Set to 0.4 or above to remove low-entropy reads;
                range is 0-1, recommended value is 0.55.  0.7 is too high.
                Negative numbers disable this function.
entropyk=3      Kmer length for entropy calculation.
entropylen=350  Reads with entropy below cutoff for at least this many
                consecutive bases will be removed.
entropyfraction=0.5     Alternative minimum length for short reads; the shorter
                        of entropylen and entfraction*readlength will be used.
entropywindow=50        Window size used for entropy calculation.
maxmonomerfraction=0.74 (mmf) Also require this fraction of bases in each
                        window to be the same base.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for icecreamfinder.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("icecreamfinder.sh", args, capture_output)

def icecreamgrader(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for icecreamgrader.sh

    Help message:
    Written by Brian Bushnell
Last modified January 21, 2020

Description:  Counts the rate of triangle reads in a file
generated by IceCreamMaker with custom headers.

Usage:  icecreamgrader.sh in_file=<input file>

Standard parameters:
in_file=<file>       Reads to grade.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for icecreamgrader.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("icecreamgrader.sh", args, capture_output)

def icecreammaker(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for icecreammaker.sh

    Help message:
    Written by Brian Bushnell
Last modified January 21, 2020

Description:  Generates synthetic PacBio reads to mimic the chimeric
inverted repeats from 'triangle reads', aka 'ice cream cones' - 
reads missing one adapter.

Usage:  icecreammaker.sh in_file=<file> out=<file> reads=100k minlen=500 maxlen=5000

Standard parameters:
in_file=<file>       A reference genome fasta (optional).
out=<file>      Synthetic read output.
idhist=<file>   Identity histogram output.
overwrite=f     (ow) Set to false to force the program to abort rather than
                overwrite an existing file.
ziplevel=2      (zl) Set to 1 (lowest) through 9 (max) to change compression
                level; lower compression is faster.

Length parameters:
NOTE:

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for icecreammaker.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("icecreammaker.sh", args, capture_output)

def idmatrix(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for idmatrix.sh

    Help message:
    Written by Brian Bushnell
Last modified November 25, 2014

Description:  Generates an identity matrix via all-to-all alignment.

*** WARNING: This program may produce incorrect results in some cirumstances.
*** It is not advisable to use until fixed.

Usage:	idmatrix.sh in_file=<file> out=<file>

Parameters:
in_file=<file>       File containing reads. in_file=stdin.fa will pipe from stdin.
out=<file>      Matrix output. out=stdout will pipe to stdout.
threads=auto    (t) Set number of threads to use; default is number of 
                logical processors.
percent=f       Output identity as percent rather than a fraction.
edits=          Allow at most this much edit distance.  Default is the
                length of the longest input sequence. Lower is faster.
width=          Alignment bandwidth, lower is faster.  Default: 2*edits+1.
usejni=f        (jni) Do alignments faster, in C code.  Requires 
                compiling the C code; details are in /jni/README.txt.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding automatic
                memory detection. -Xmx20g will specify 
                20 gigs of RAM, and -Xmx200m will specify 200 megs.  
                The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for idmatrix.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("idmatrix.sh", args, capture_output)

def idtree(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for idtree.sh

    Help message:
    Written by Brian Bushnell
Last modified July 1, 2016

Description:  Makes a Newick tree from an identity matrix.
Intended for use with matrices created by idmatrix.sh.

Usage:  idtree.sh in_file=<input file> out=<output file>

Standard parameters:
in_file=<file>       Identity matrix in TSV format.
out=<file>      Newick tree output.
overwrite=f     (ow) Set to false to force the program to abort rather than
                overwrite an existing file.

Processing parameters:
None yet!

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for idtree.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("idtree.sh", args, capture_output)

def indelfree(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for indelfree.sh

    Help message:
    Written by Brian Bushnell
Last modified July 15, 2025

Description:  Aligns sequences, not allowing indels.
Brute force mode guarantees all alignments will be found and reported,
up to the maximum allowed number of substitutions.
Indexed mode may remove this guarantee (depending on kmer length,
query length, and number of substitutions) but can be much faster.
This loads all reads into memory and streams the reference, unlike
a traditional aligner, so it is designed for a relatively small query set
and potentially enormous reference set.

Usage:  indelfree.sh in_file=spacers.fa ref=contigs.fa out=mapped.sam

Parameters:
in_file=<file>       Query input.  These will be stored in memory.
ref=<file>      Reference input.  These will be streamed.
out=<file>      Sam output.
subs=5          Maximum allowed substitutions.
simd            Enable SIMD alignment.  Only accelerates brute force mode.
threads=        Set the max number of threads; default is logical cores.

Index Parameters:
index=t         If true, build a kmer index to accelerate search.
k=13            Index kmer length (1-15); longer is faster but less sensitive.
                Very short kmers are slower than brute force mode.
mm=1            Middle mask length; the number of wildcard bases in the kmer.
                Must be shorter than k-1; 0 disables middle mask.
blacklist=2     Blacklist homopolymer kmers up to this repeat length.
step=1          Only use every Nth query kmer.
minhits=1       Require this many seed hits to perform alignment.
minprob=0.9999  Calculate the number of seed hits needed, on a per-query
                basis, to ensure this probability of finding valid alignments.
                1 ensures optimality; 0 requires all seed hits; and negative
                numbers disable this, using the minhits setting only.
                When enabled, the min hits used for a query is the maximum
                of minhits and the probabilistic model.
prescan=t       Count query hits before filling seed location lists.
list=t          Store seed hits in lists rather than maps.
                Maps are optimized for shorter kmers and more positive hits.


Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for indelfree.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("indelfree.sh", args, capture_output)

def invertkey(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for invertkey.sh

    Help message:
    Written by Brian Bushnell
Last modified October 2, 2017

Description:  Inverts a sketch key, given a matching reference.

Usage:  invertsketch.sh in_file=<reference> key=<key> k=<31>

I/O parameters:
out=<file>      Output file.
overwrite=f     (ow) Set to false to force the program to abort rather than
                overwrite an existing file.

Processing parameters:


Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for invertkey.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("invertkey.sh", args, capture_output)

def javasetup(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for javasetup.sh

    Help message:
    No help message found.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for javasetup.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("javasetup.sh", args, capture_output)

def kapastats(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for kapastats.sh

    Help message:
    Written by Brian Bushnell
Last modified December 6, 2018

Description:  Gathers statistics on Kapa spike-in rates.

Usage:  kapastats.sh in_file=<input file> out=<output file>

Parameters:
in_file=<file>       TSV file of plate IDs, one ID per line.
out=<file>      Primary output, or read 1 output.
overwrite=f     (ow) Set to false to force the program to abort rather than
                overwrite an existing file.
raw=f           Output raw observations rather than statistics.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for kapastats.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("kapastats.sh", args, capture_output)

def kcompress(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for kcompress.sh

    Help message:
    Written by Brian Bushnell
Last modified July 16, 2018

Description:  Compresses sequence data into a fasta file containing each kmer
exactly once.  Allows arbitrary kmer set operations via multiple passes.

Usage:  kcompress.sh in_file=<reads> out=<contigs> min_file=<1> max=<2147483647>

Input parameters:
in_file=<file>           Primary input file for reads to use as kmer data.
in2=<file>          Second input file for paired data.
reads=-1            Only process this number of reads, then quit (-1 means all).

Output parameters:
out=<file>          Write contigs (in contig mode).
showstats=t         Print assembly statistics after writing contigs.
fuse=0              Fuse output sequences into chunks at least this long,
                    padded with 1 N between sequences.

Prefiltering parameters:
prefilter=0         If set to a positive integer, use a countmin sketch
                    to ignore kmers with depth of that value or lower.
prehashes=2         Number of hashes for prefilter.
prefiltersize=0.2   (pff) Fraction of memory to use for prefilter.
minprobprefilter=t  (mpp) Use minprob for the prefilter.
prepasses=1         Use this many prefiltering passes; higher be more thorough
                    if the filter is very full.  Set to 'auto' to iteratively 
                    prefilter until the remaining kmers will fit in memory.

Hashing parameters:
k=31                Kmer length (1 to 31).
prealloc=t          Pre-allocate memory rather than dynamically growing; 
                    faster and more memory-efficient.  A float fraction (0-1)
                    may be specified; default is 1.
minprob=0.5         Ignore kmers with overall probability of correctness below this.
minprobmain_file=t       (mpm) Use minprob for the primary kmer counts.
threads=X           Spawn X threads (default is number of logical processors).

Assembly parameters:
mincount=1          (min) Only retain kmers that occur at least this many times.
maxcount=BIG        (max) Only retain kmers that occur at most this many times.
requiresamecount    (rsc) Only build contigs from kmers with exactly the same count.
rcomp=t             Store forward and reverse kmers together.  Setting this to
                    false will only use forward kmers.


Java Parameters:
-Xmx                This will set Java's memory usage, overriding autodetection.
                    -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom               This flag will cause the process to exit if an
                    out-of-memory exception occurs.  Requires Java 8u92+.
-da                 Disable assertions.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for kcompress.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("kcompress.sh", args, capture_output)

def keepbestcopy(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for keepbestcopy.sh

    Help message:
    Written by Brian Bushnell
Last modified October 4, 2019

Description:  Discards all but the best copy of a ribosomal gene per TaxID.
Gene sequences should be named like this: >tid|123|whatever
Sequences are selected based on the number of fully defined bases.

Usage:  keepbest.sh in_file=<input file> out=<output file> rate=<float>

Input may be fasta or fastq, compressed or uncompressed.

Standard parameters:
in_file=<file>       Input sequences.
out=<file>      Output sequences.
overwrite=f     (ow) Set to false to force the program to abort rather than
                overwrite an existing file.
ziplevel=2      (zl) Set to 1 (lowest) through 9 (max) to change compression
                level; lower compression is faster.

Processing parameters:
maxlen=1600     Prefer sequences shorter than this.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for keepbestcopy.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("keepbestcopy.sh", args, capture_output)

def kmercountexact(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for kmercountexact.sh

    Help message:
    Written by Brian Bushnell
Last modified October 14, 2020

Description:  Counts the number of unique kmers in a file.
Generates a kmer frequency histogram and genome size estimate (in peaks output),
and prints a file containing all kmers and their counts.
Supports K=1 to infinity, though not all values are allowed.
SEE ALSO: bbnorm.sh/khist.sh, loglog.sh, and kmercountmulti.sh.

Usage:   kmercountexact.sh in_file=<file> khist=<file> peaks=<file>

Input may be fasta or fastq, compressed or uncompressed.
Output may be stdout or a file.  out, khist, and peaks are optional.


Input parameters:
in_file=<file>           Primary input file.
in2=<file>          Second input file for paired reads.
amino=f             Run in amino acid mode.

Output parameters:
out=<file>          Print kmers and their counts.  This is produces a
                    huge file, so skip it if you only need the histogram.
fastadump=t         Print kmers and counts as fasta versus 2-column tsv.
mincount=1          Only print kmers with at least this depth.
reads=-1            Only process this number of reads, then quit (-1 means all).
dumpthreads=-1      Use this number of threads for dumping kmers (-1 means auto).

Hashing parameters:
k=31                Kmer length (1-31 is fastest).
prealloc=t          Pre-allocate memory rather than dynamically growing; faster and more memory-efficient.  A float fraction (0-1) may be specified, default 1.
prefilter=0         If set to a positive integer, use a countmin sketch to ignore kmers with depth of that value or lower.
prehashes=2         Number of hashes for prefilter.
prefiltersize=0.2   Fraction of memory to use for prefilter.
minq=6              Ignore kmers containing bases with quality below this. (TODO)
minprob=0.0         Ignore kmers with overall probability of correctness below this.
threads=X           Spawn X hashing threads (default is number of logical processors).
onepass=f           If true, prefilter will be generated in same pass as kmer counts.  Much faster but counts will be lower, by up to prefilter's depth limit.
rcomp=t             Store and count each kmer together and its reverse-complement.

Histogram parameters:
khist=<file>        Print kmer frequency histogram.
histcolumns=2       2 columns: (depth, count).  3 columns: (depth, rawCount, count).
histmax=100000      Maximum depth to print in histogram output.
histheader=t        Set true to print a header line.
nzo=t               (nonzeroonly) Only print lines for depths with a nonzero kmer count.
gchist=f            Add an extra histogram column with the average GC%.

Intersection parameters:
ref=<file>          An input assembly of the input reads.
intersection=<file> Output file for a 2-D histogram of read and ref kmer counts.
refmax=6            Maximum reference kmer depth to track; read depth is controlled by 'histmax'.

Smoothing parameters:
smoothkhist=f       Smooth the output kmer histogram.
smoothpeaks=t       Smooth the kmer histogram for peak-calling, but does not affect the output histogram.
smoothradius=1      Initial radius of progressive smoothing function.
maxradius=10        Maximum radius of progressive smoothing function.
progressivemult=2   Increment radius each time depth increases by this factor.
logscale=t          Transform to log-scale prior to peak-calling.
logwidth=0.1        The larger the number, the smoother.

Peak calling parameters:
peaks=<file>        Write the peaks to this file.  Default is stdout. 
                    Also contains the genome size estimate in bp.
minHeight=2         (h) Ignore peaks shorter than this.
minVolume=5         (v) Ignore peaks with less area than this.
minWidth=3          (w) Ignore peaks narrower than this.
minPeak=2           (minp) Ignore peaks with an X-value below this.
maxPeak=BIG         (maxp) Ignore peaks with an X-value above this.
maxPeakCount=12     (maxpc) Print up to this many peaks (prioritizing height).
ploidy=-1           Specify ploidy; otherwise it will be autodetected.

Sketch parameters (for making a MinHashSketch):
sketch=<file>       Write a minhash sketch to this file.
sketchlen=10000     Output the top 10000 kmers.  Only kmers with at least mincount are included.
sketchname=         Name of output sketch.
sketchid=           taxID of output sketch.

Quality parameters:
qtrim=f             Trim read ends to remove bases with quality below minq.
                    Values: t (trim both ends), f (neither end), r (right end only), l (left end only).
trimq=4             Trim quality threshold.
minavgquality=0     (maq) Reads with average quality (before trimming) below this will be discarded.

Overlap parameters (for overlapping paired-end reads only):
merge=f             Attempt to merge reads before counting kmers.
ecco=f              Error correct via overlap, but do not merge reads.   

Java Parameters:
-Xmx                This will set Java's memory usage, overriding autodetection.
                    -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom               This flag will cause the process to exit if an
                    out-of-memory exception occurs.  Requires Java 8u92+.
-da                 Disable assertions.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for kmercountexact.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("kmercountexact.sh", args, capture_output)

def kmercountmulti(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for kmercountmulti.sh

    Help message:
    Written by Brian Bushnell
Last modified February 20, 2020

Description:  Estimates cardinality of unique kmers in sequence data.
Processes multiple kmer lengths simultaneously to produce a histogram.

Usage:  kmercountmulti.sh in_file=<file> sweep=<20,100,8> out=<histogram output>

Parameters:
in_file=<file>           (in1) Input file, or comma-delimited list of files.
in2=<file>          Optional second file for paired reads.
out=<file>          Histogram output.  Default is stdout.
k=                  Comma-delimited list of kmer lengths to use.
sweep=min,max,incr  Use incremented kmer values from min to max. For example,
                    sweep=20,26,2 is equivalent to k=20,22,24,26.
buckets=2048        Use this many buckets for counting; higher decreases
                    variance, for large datasets.  Must be a power of 2.
seed=-1             Use this seed for hash functions.  
                    A negative number forces a random seed.
minprob=0           Set to a value between 0 and 1 to exclude kmers with a 
                    lower probability of being correct.
hashes=1            Use this many hash functions.  More hashes yield greater
                    accuracy, but H hashes takes H times as long.
stdev=f             Print standard deviations.

Shortcuts:
The # symbol will be substituted for 1 and 2.
For example:
kmercountmulti.sh in_file=read#.fq
...is equivalent to:
kmercountmulti.sh in1=read1.fq in2=read2.fq

Java Parameters:
-Xmx                This will set Java's memory usage, overriding autodetection.
                    -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom               This flag will cause the process to exit if an
                    out-of-memory exception occurs.  Requires Java 8u92+.
-da                 Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for kmercountmulti.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("kmercountmulti.sh", args, capture_output)

def kmercoverage(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for kmercoverage.sh

    Help message:
    Written by Brian Bushnell
Last modified May 23, 2014

*** DEPRECATED: This should still work but is no longer maintained. ***

Description:  Annotates reads with their kmer depth.

Usage:        kmercoverage in_file=<input> out=<read output> hist=<histogram output>

Input parameters:
in2=null            Second input file for paired reads
extra=null          Additional files to use for input (generating hash table) but not for output
fastareadlen=2^31   Break up FASTA reads longer than this.  Can be useful when processing scaffolded genomes
tablereads=-1       Use at most this many reads when building the hashtable (-1 means all)
kmersample=1        Process every nth kmer, and skip the rest
readsample=1        Process every nth read, and skip the rest

Output parameters:
hist=null           Specify a file to output the depth histogram
histlen=10000       Max depth displayed on histogram
reads=-1            Only process this number of reads, then quit (-1 means all)
sampleoutput=t      Use sampling on output as well as input (not used if sample rates are 1)
printcoverage=f     Only print coverage information instead of reads
useheader=f         Append coverage info to the read's header
minmedian=0         Don't output reads with median coverage below this
minaverage=0        Don't output reads with average coverage below this
zerobin_file=f           Set to true if you want kmers with a count of 0 to go in the 0 bin instead of the 1 bin in histograms.
                    Default is false, to prevent confusion about how there can be 0-count kmers.
                    The reason is that based on the 'minq' and 'minprob' settings, some kmers may be excluded from the bloom filter.

Hashing parameters:
k=31                Kmer length (values under 32 are most efficient, but arbitrarily high values are supported)
cbits=8             Bits per cell in bloom filter; must be 2, 4, 8, 16, or 32.  Maximum kmer depth recorded is 2^cbits.
                    Large values decrease accuracy for a fixed amount of memory.
hashes=4            Number of times a kmer is hashed.  Higher is slower.
                    Higher is MORE accurate if there is enough memory, and LESS accurate if there is not enough memory.
prefilter=f         True is slower, but generally more accurate; filters out low-depth kmers from the main hashtable.
prehashes=2         Number of hashes for prefilter.
passes=1            More passes can sometimes increase accuracy by iteratively removing low-depth kmers
minq=7              Ignore kmers containing bases with quality below this
minprob=0.5         Ignore kmers with overall probability of correctness below this
threads=X           Spawn exactly X hashing threads (default is number of logical processors).  Total active threads may exceed X by up to 4.

Java Parameters:
-Xmx                This will set Java's memory usage, overriding autodetection.
                    -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom               This flag will cause the process to exit if an
                    out-of-memory exception occurs.  Requires Java 8u92+.
-da                 Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for kmercoverage.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("kmercoverage.sh", args, capture_output)

def kmerfilterset(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for kmerfilterset.sh

    Help message:
    Written by Brian Bushnell
Last modified October 24, 2019

Description:  Generates a set of kmers such that every input sequence will
contain at least one kmer in the set.  This is a greedy algorithm which
retains the top X most common kmers each pass, and removes the sequences
matching those kmers, so subsequent passes are faster.

This will not generate an optimally small set but the output will be
quite small.  The file size may be further decreased with kcompress.sh.

Usage:  kmerfilterset.sh in_file=<input file> out=<output file> k=<integer>

File parameters:
in_file=<file>       Primary input.
out=<file>      Primary output.
temp=<file>     Temporary file pattern (optional).  Must contain # symbol.
initial=<file>  Initial kmer set (optional).  This can be used to accelerate
                the process.

Processing parameters:
k=31            Kmer length.
rcomp=t         Consider forward and reverse-complement kmers identical.
minkpp=1        (minkmersperpass) Retain at least this many kmers per pass.
                Higher is faster but results in a larger set.
maxkpp=2        (maxkmersperpass) Retain at most this many kmers per pass;
                0 means unlimited.
mincount=1      Ignore kmers seen fewer than this many times in this pass.
maxpasses=3000  Don't run more than this many passes.
maxns=BIG       Ignore sequences with more than this many Ns.
minlen=0        Ignore sequences shorter than this.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for kmerfilterset.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("kmerfilterset.sh", args, capture_output)

def kmerlimit(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for kmerlimit.sh

    Help message:
    Written by Brian Bushnell
Last modified July 31, 2018

Description:  Stops producing reads when the unique kmer limit is reached.
This is approximate.  If the input has been Clumpified, the order should be
randomized first with shuffle2.sh or sortbyname.sh with the flowcell flag.

Differences between versions:
kmerlimit.sh uses 1 pass and outputs all reads until a limit is hit,
meaning the input reads should be in random order with respect to sequence.
kmerlimit2.sh uses 2 passes and randomly subsamples from the file, so
it works with reads in any order.

Usage:  kmerlimit.sh in_file=<input file> out=<output file> limit=<number>

Standard parameters:
in_file=<file>       Primary input, or read 1 input.
in2=<file>      Read 2 input if reads are in two files.
out=<file>      Primary output, or read 1 output.
out2=<file>     Read 2 output if reads are in two files.
overwrite=t     (ow) Set to false to force the program to abort rather than
                overwrite an existing file.
ziplevel=2      (zl) Set to 1 (lowest) through 9 (max) to change compression
                level; lower compression is faster.

Processing parameters:
k=31            Kmer length, 1-32.
limit=          The number of unique kmers to produce.
mincount=1      Ignore kmers seen fewer than this many times.
minqual=0       Ignore bases with quality below this.
minprob=0.2     Ignore kmers with correctness probability below this.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for kmerlimit.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("kmerlimit.sh", args, capture_output)

def kmerlimit2(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for kmerlimit2.sh

    Help message:
    Written by Brian Bushnell
Last modified July 31, 2018

Description:  Subsamples reads to reach a target unique kmer limit.

Differences between versions:
kmerlimit.sh uses 1 pass and outputs all reads until a limit is hit,
meaning the input reads should be in random order with respect to sequence.
kmerlimit2.sh uses 2 passes and randomly subsamples from the file, so
it works with reads in any order.

Usage:  kmerlimit2.sh in_file=<input file> out=<output file> limit=<number>

Standard parameters:
in_file=<file>       Primary input, or read 1 input.
in2=<file>      Read 2 input if reads are in two files.
out=<file>      Primary output, or read 1 output.
out2=<file>     Read 2 output if reads are in two files.
overwrite=t     (ow) Set to false to force the program to abort rather than
                overwrite an existing file.
ziplevel=2      (zl) Set to 1 (lowest) through 9 (max) to change compression
                level; lower compression is faster.

Processing parameters:
k=31            Kmer length, 1-32.
limit=          The number of unique kmers to produce.
mincount=1      Ignore kmers seen fewer than this many times.
minqual=0       Ignore bases with quality below this.
minprob=0.2     Ignore kmers with correctness probability below this.
trials=25       Simulation trials.
seed=-1         Set to a positive number for deterministic output.
maxlen=50m      Max length of a temp array used in simulation.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for kmerlimit2.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("kmerlimit2.sh", args, capture_output)

def kmerposition(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for kmerposition.sh

    Help message:
    Written by Jasper Toscani Field
Last modified June 11, 2020

Description:  Counts positional occurrences of reference kmers in reads.

Usage:  kmerposition.sh in_file=<input file> out=<output file> ref=<reference file> k=<kmer length>

Input may be fasta or fastq, compressed or uncompressed.

Standard parameters:
in_file=<file>       Primary input, or read 1 input.
in2=<file>      Read 2 input if reads are in two files.
ref=<file>      Reference file.
out=<file>      Primary output, statistics on found kmers.

Processing parameters:
k=19            Kmer length.
rcomp=t         If true, also match for reverse-complements.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for kmerposition.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("kmerposition.sh", args, capture_output)

def kmutate(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for kmutate.sh

    Help message:
    Written by Brian Bushnell
Last modified January 26, 2021

Description:  Given a reference, generates a kmer spectrum including a 
specified number of substitutions, insertions, and deletions.  The output is 
useful for analyzing barcodes or other short oligos, and filtering using
BBDuk or Seal. Input may be fasta or fastq, compressed or raw.
See also kcompress, kmercountexact, and bbkmerset.

Usage:  kmutate.sh in_file=<file> out=<file> k=<kmer length> edist=<edit distance>

Examples:

        kmutate.sh in_file=x.fa out=y.fa k=31 edist=2
This will generate all 31-mers in x.fa, along with all 31-mer mutants with
an edit distance of up to 2.  For example, 1 substitution, or 1 substitution
plus 1 deletion, or any other combination of subsitutions, insertions,
and deletions that sum to 0, 1, or 2.

        kmutate.sh in_file=x.fa out=y.fa k=31 idist=1 ddist=3
This will generate all 31-mers in x.fa, along with all 31-mer mutants allowing
up to 1 insertion and 3 deletions, but no substitutions.  For example,
1 insertion and 3 deletions is possible (edit distance 4), but 1 deletion and 
1 substitution is not directly possible (though some equivalent mutants would
still be generated because a deletion and subsequent insertion is equivalent 
to a substitution).

Note that deletion events have limitations; e.g., they cannot occur on input
sequences of length k because the resulting sequence is shorter than k.  As
a result, running the program twice consecutively with edist=1 will not give
the same results as running once with edist=2 since the intermediate file will
be only k-length sequences.  However, running consecutively with sdist or
idist would be equivalent since they do not involve deletions.

Standard parameters:
in_file=<file>       Primary input, or read 1 input.
in2=<file>      Read 2 input if reads are in two files.
out=<file>      Primary output, or read 1 output.
overwrite=t     (ow) Set to false to force the program to abort rather than
                overwrite an existing file.

Processing parameters:
k=31            Kmer length; 1-31.
rcomp=t         Consider kmers equivalent to their reverse-complements.

Edit mode flags (used if edist>0):
edist=0         Set the maximal edit distance (0-3).
smax=99         (optional) Don't allow more than this many total substitutions.
dmax=99         (optional) Don't allow more than this many total deletions.
imax=99         (optional) Don't allow more than this many total insertions.

SDI mode flags:
sdist=0         Maximum substitutions allowed.
idist=0         Maximum insertions allowed.
ddist=0         Maximum deletions allowed (0-3).
emax=99         (optional) Don't allow more than this many total edits.

*** Note - please use SDI mode flags OR Edit mode flag, not both. ***
*** Both modes are equivalent, they just have different defaults. ***

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for kmutate.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("kmutate.sh", args, capture_output)

def lilypad(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for lilypad.sh

    Help message:
    Written by Brian Bushnell
Last modified September 13, 2019

Description:  Uses mapped paired reads to generate scaffolds from contigs.
Designed for use with ordinary paired-end Illumina libraries.

Usage:  lilypad.sh in_file=mapped.sam ref=contigs.fa out=scaffolds.fa

Standard parameters:
in_file=<file>       Reads mapped to the reference; should be sam or bam.
ref=<file>      Reference; may be fasta or fastq.
out=<file>      Modified reference; should be fasta.
overwrite=f     (ow) Set to false to force the program to abort rather than
                overwrite an existing file.

Processing parameters:
gap=10          Pad gaps with a minimum of this many Ns.
mindepth=4      Minimum spanning read pairs to join contigs.
maxinsert=3000  Maximum allowed insert size for proper pairs.
mincontig=200   Ignore contigs under this length if there is a 
                longer alternative.
minwr=0.8       (minWeightRatio) Minimum fraction of outgoing edges 
                pointing to the same contig.  Lower values will increase
                continuity at a risk of misassemblies.
minsr=0.8       (minStrandRatio) Minimum fraction of outgoing edges 
                indicating the same orientation.  Lower values will increase
                continuity at a possible risk of inversions.
passes=8        More passes may increase continuity.
samestrandpairs=f  Read pairs map to the same strand.  Currently untested.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for lilypad.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("lilypad.sh", args, capture_output)

def loadreads(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for loadreads.sh

    Help message:
    Written by Brian Bushnell
Last modified July 10, 2017

Description:  Tests the memory usage of a sequence file.

Usage:  loadreads.sh in_file=<file>

Parameters:
in_file=             Input file.
lowcomplexity=f Assume input library is low-complexity.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify
                20 gigs of RAM, and -Xmx200m will specify 200 megs.  The max
                is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for loadreads.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("loadreads.sh", args, capture_output)

def loglog(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for loglog.sh

    Help message:
    Written by Brian Bushnell
Last modified March 24, 2020

Description:  Estimates cardinality of unique kmers in sequence data.
See also kmercountmulti.sh.

Usage:  loglog.sh in_file=<file> k=<31>

Parameters:
in_file=<file>       (in1) Input file, or comma-delimited list of files.
in2=<file>      ptional second file for paired reads.
k=31            Use this kmer length for counting.
buckets=2048    Use this many buckets for counting; higher decreases
                variance, for large datasets.  Must be a power of 2.
seed=-1         Use this seed for hash functions.  A negative number forces
                a random seed.
minprob=0       Set to a value between 0 and 1 to exclude kmers with a lower 
                probability of being correct.


Shortcuts:
The # symbol will be substituted for 1 and 2.
For example:
loglog.sh in_file=read#.fq
...is equivalent to:
loglog.sh in1=read1.fq in2=read2.fq

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Supported input formats are fastq, fasta, scarf, sam, and bam.
Supported compression formats are gzip and bz2.
To read from stdin, set 'in_file=stdin'.  The format should be specified with an extension, like 'in_file=stdin.fq.gz'

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for loglog.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("loglog.sh", args, capture_output)

def makechimeras(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for makechimeras.sh

    Help message:
    Written by Brian Bushnell
Last modified February 17, 2015

Description:  Makes chimeric sequences from nonchimeric sequences.
Designed for PacBio reads.

Usage:  makechimeras.sh in_file=<input> out=<output> chimeras=<integer>

Input Parameters:
in_file=<file>       The input file containing nonchimeric reads.
unpigz=t        Decompress with pigz for faster decompression.

Output Parameters:
out=<file>      Fasta output destination.
chimeras=-1     Number of chimeras to create (required parameter).
forcelength=0   If a positive number X, one parent will be length X, and the other will be length-X.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for makechimeras.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("makechimeras.sh", args, capture_output)

def makecontaminatedgenomes(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for makecontaminatedgenomes.sh

    Help message:
    Written by Brian Bushnell
Last modified August 29, 2017

Description:  Generates synthetic contaminated partial genomes from clean genomes.
Output is formatted as (prefix)_bases1_fname1_bases2_fname2_counter_(suffix).

Usage:        makecontaminatedgenomes.sh in_file=<file> out=<pattern>

I/O parameters:
in_file=<file>       A file containing one input file path per line.
out=<pattern>   A file name containing a # symbol (or other regex).
                The regex will be replaced by source filenames.

Processing Parameters:
count=1         Number of output files to make.
seed=-1         RNG seed; negative for a random seed.
exp1=1          Exponent for genome 1 size fraction.
exp2=1          Exponent for genome 2 size fraction.
subrate=0       Rate to add substitutions to new genomes (0-1).
indelrate=0     Rate to add substitutions to new genomes (0-1).
regex=#         Use this substitution regex for replacement.
delimiter=_     Use this delimiter in the new file names.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for makecontaminatedgenomes.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("makecontaminatedgenomes.sh", args, capture_output)

def makepolymers(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for makepolymers.sh

    Help message:
    Written by Brian Bushnell
Last modified October 3, 2017

Description:  Creates polymer sequences.
Can be used in conjunction with mutate.sh to generate low-complexity sequence.

Usage:  makepolymers.sh out=<output file> k=<repeat length> minlen=<sequence length>

I/O parameters:
out=<file>      Output genome.
overwrite=f     (ow) Set to false to force the program to abort rather than
                overwrite an existing file.

Processing parameters:
k=1             Length of repeating polymeric units.
                To generate a sweep of multiple values of k,
                specify both mink and maxk.
minlen=31       Ensure sequences are at least this long.
                Specifically, minlen=X will ensure sequences are long enough
                that all possible kmers of length X are present.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for makepolymers.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("makepolymers.sh", args, capture_output)

def makequickbinvector(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for makequickbinvector.sh

    Help message:
    Written by Brian Bushnell
Last modified April 7, 2025

Description:  Makes vectors for QuickBin network training.

Usage: makequickbinvector.sh in_file=contigs.fa out=vector.txt cov=cov.txt lines=1m

Parameters:
in_file=<file>       Assembly input; only required parameter.
cov=<file>      Cov file generated by Quickbin from sam files.
out=<file>      Output file.
lines=1m        Lines to output.
rate=0.5        Fraction of vectors with positive results.
mincontig=200   Do not load contigs shorter than this.
minlen=0        Do not print comparisons where either contig is shorter 
                than this.
maxlen=2B       Do not print comparisons where both contigs are longer
                than this.
maxgcdif=1.0    Max allowed GC difference for output.
maxkmerdif=1.0  Max allowed TNF cosine difference for output.
mcc=9           Max contigs per cluster.
maxdepthratio=1000.0  Max allowed depth ratio for output.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for makequickbinvector.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("makequickbinvector.sh", args, capture_output)

def mapPacBio(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for mapPacBio.sh

    Help message:
    No help message found.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for mapPacBio.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("mapPacBio.sh", args, capture_output)

def matrixtocolumns(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for matrixtocolumns.sh

    Help message:
    Written by Brian Bushnell
Last modified January 21, 2015

Description:  Transforms two matched identity matrices into 2-column format,
              one row per entry, one column per matrix.

Usage:  matrixtocolumns.sh in1=<matrix1> in2=<matrix2> out=<file>

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for matrixtocolumns.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("matrixtocolumns.sh", args, capture_output)

def memdetect(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for memdetect.sh

    Help message:
    No help message found.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for memdetect.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("memdetect.sh", args, capture_output)

def mergebarcodes(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for mergebarcodes.sh

    Help message:
    Written by Brian Bushnell
Last modified February 17, 2015

Description:  Concatenates barcodes and quality onto read names.

Usage:        mergebarcodes.sh in_file=<file> out=<file> barcode=<file>

Input may be stdin or a fasta or fastq file, raw or gzipped.
If you pipe via stdin/stdout, please include the file type; e.g. for gzipped fasta input, set in_file=stdin.fa.gz

Optional parameters (and their defaults)

Input parameters:
in_file=<file>       Input reads. 'in_file=stdin.fq' will pipe from standard in.
bar=<file>      File containing barcodes.
int=auto        (interleaved) If true, forces fastq input to be paired and interleaved.
qin_file=auto        ASCII offset for input quality.  May be 33 (Sanger), 64 (Illumina), or auto.

Output parameters:
out=<file>      Write muxed sequences here.  'out=stdout.fa' will pipe to standard out.
overwrite=t     (ow) Set to false to force the program to abort rather than overwrite an existing file.
ziplevel=2      (zl) Set to 1 (lowest) through 9 (max) to change compression level; lower compression is faster.
qout=auto       ASCII offset for output quality.  May be 33 (Sanger), 64 (Illumina), or auto (same as input).

Other parameters:
pigz=t          Use pigz to compress.  If argument is a number, that will set the number of pigz threads.
unpigz=t        Use pigz to decompress.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for mergebarcodes.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("mergebarcodes.sh", args, capture_output)

def mergeOTUs(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for mergeOTUs.sh

    Help message:
    Written by Brian Bushnell
Last modified January 21, 2015

Description:    Merges coverage stats lines (from pileup) for the same OTU,
                according to some custom naming scheme.

Usage:          mergeOTUs.sh in_file=<file> out=<file>

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for mergeOTUs.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("mergeOTUs.sh", args, capture_output)

def mergepgm(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for mergepgm.sh

    Help message:
    Written by Brian Bushnell
Last modified October 10, 2018

Description:  Merges .pgm files.

Usage:  mergepgm.sh in_file=x.pgm,y.pgm out=z.pgm

File parameters:
in_file=<file,file>  A pgm file or comma-delimited list of pgm files.
out=<file>      Output filename.
normalize=f     Merge proportionally to base counts, so small models
                have equal weight to large models.  Normalization happens
                before applying the @ multiplier.
@ symbol        Input filenames in the form of 'x.pgm@0.1' will have
                a multiplier applied to that model prior to merging.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for mergepgm.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("mergepgm.sh", args, capture_output)

def mergeribo(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for mergeribo.sh

    Help message:
    Written by Brian Bushnell
Last modified May 15, 2025

Description:  Merges files of SSU sequences to keep one per taxID.
By default, a consensus is generated per TaxID, then the sequence
best matching that consensus is used:
First, all sequences per TaxID are aligned to a reference consensus.
Second, the best-matching sequence is used as a seed, and all other
sequences for that TaxID are aligned to the seed to generate a new consensus.
Third, in 'consensus' mode, that consensus is simply output.
In 'best' mode (default), all sequences are aligned again to the new consensus,
and the best-matching is output.

Usage:  mergeribo.sh in_file=<file,file> out=<file>

Standard parameters:
in_file=<file,file>  Comma-delimited list of files.
out=<file>      Output file.
out2=<file>     Read 2 output if reads are in two files.
overwrite=f     (ow) Set to false to force the program to abort rather than
                overwrite an existing file.
showspeed=t     (ss) Set to 'f' to suppress display of processing speed.
ziplevel=2      (zl) Set to 1 (lowest) through 9 (max) to change compression
                level; lower compression is faster.
fastawrap=70    4000 is recommended to minimize filesize.

Processing parameters:
alt=<file>      Lower priority data.  Only used if there is no SSU associated
                with the TaxID from the primary input.
best=t          Output the best representative per taxID.
consensus=f     Output a consensus per taxID instead of the best input
                sequence.  Mutually exclusive with best.
fast=f          Output the best sequence based on alignment to global consensus
                (the seed) rather than individual consensus.
minid=0.62      Ignore sequences with identity lower than this to the global
                consensus.
maxns=-1        Ignore sequences with more than this many Ns, if non-negative.
minlen=1        Ignore sequences shorter than this.
maxlen=4000     Ignore sequences longer than this.
16S=t           Align to 16S consensus to pick the seed. Mutually exclusive.
18S=f           Align to 18S consensus to pick the seed. Mutually exclusive.
level=          If specified with a term like 'species' or 'genus', nodes
                will be promoted to that level, minimum, before consensus.
dada2=f         Output headers in dada2 format.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for mergeribo.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("mergeribo.sh", args, capture_output)

def mergesam(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for mergesam.sh

    Help message:
    Written by Brian Bushnell
Last modified March 8, 2017

Description:  Concatenates sam files, keeping only the header from the first.

Usage:  mergesam.sh <files> out=<file>

Java Parameters:
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for mergesam.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("mergesam.sh", args, capture_output)

def mergesketch(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for mergesketch.sh

    Help message:
    Written by Brian Bushnell
Last modified December 19, 2019

Description:  Merges multiple sketches into a single sketch.

Please read bbmap/docs/guides/BBSketchGuide.txt for more information.

Usage:           mergesketch.sh in_file=a.sketch,b.sketch out=c.sketch
With wildcards:  mergesketch.sh *.sketch out=c.sketch

Standard parameters:
in_file=<file>       Input sketches or fasta files; may be a comma-delimited
                list.  in_file= is optional so wildcards may be used.
out=<file>      Output sketch.
amino=f         Use amino acid mode.

Sketch-making parameters:
mode=single     Possible modes, for fasta input:
                   single: Generate one sketch per file.
                   sequence: Generate one sketch per sequence.
autosize=t      Produce an output sketch of whatever size the union 
                happens to be.
size=           Restrict output sketch to this upper bound of size.
k=32,24         Kmer length, 1-32.
keyfraction=0.2 Only consider this upper fraction of keyspace.
minkeycount=1   Ignore kmers that occur fewer times than this.  Values
                over 1 can be used with raw reads to avoid error kmers.
depth=f         Retain kmer counts if available.

Metadata parameters: (if blank the values of the first sketch will be used)
taxid=-1        Set the NCBI taxid.
imgid=-1        Set the IMG id.
spid=-1         Set the JGI sequencing project id.
name=           Set the name (taxname).
name0=          Set name0 (normally the first sequence header).
fname=          Set fname (normally the file name).
meta_=          Set an arbitrary metadata field.
                For example, meta_Month=March.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

For more detailed information, please read /bbmap/docs/guides/BBSketchGuide.txt.
Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for mergesketch.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("mergesketch.sh", args, capture_output)

def mergesorted(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for mergesorted.sh

    Help message:
    Written by Brian Bushnell
Last modified September 12, 2018

Description:  Sorts reads by name or other keys such as length,
quality, mapping position, flowcell coordinates, or taxonomy.
Intended to merge temp files produced by SortByName if the program
ran out of time during merging.

Usage:   mergesorted.sh sort_temp* out=<file>

Input may be fasta, fastq, or sam, compressed or uncompressed.

Parameters:

in_file=<file,file,...>  Input files.  Files may be specified without in_file=.
out=<file>          Output file.
delete=t            Delete input files after merging.
name=t              Sort reads by name.
length=f            Sort reads by length.
quality=f           Sort reads by quality.
position=f          Sort reads by position (for mapped reads).
taxa=f              Sort reads by taxonomy (for NCBI naming convention).
sequence=f          Sort reads by sequence, alphabetically.
flowcell=f          Sort reads by flowcell coordinates.
shuffle=f           Shuffle reads randomly (untested).
list=<file>         Sort reads according to this list of names.
ascending=t         Sort ascending.
memmult=.35         Write a temp file when used memory drops below this
                    fraction of total memory.

Taxonomy-sorting parameters:
tree=               Specify a taxtree file.  On Genepool, use 'auto'.
gi=                 Specify a gitable file.  On Genepool, use 'auto'.
accession=          Specify one or more comma-delimited NCBI accession to
                    taxid files.  On Genepool, use 'auto'.

Java Parameters:
-Xmx                This will set Java's memory usage, overriding autodetection.
                    -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom               This flag will cause the process to exit if an 
                    out-of-memory exception occurs.  Requires Java 8u92+.
-da                 Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for mergesorted.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("mergesorted.sh", args, capture_output)

def microalign(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for microalign.sh

    Help message:
    Written by Brian Bushnell
Last modified March 21, 2025

Description:  Wrapper for MicroAligner.
Can align reads to a small, single-contig reference like PhiX.
Probably faster than BBMap.  Produces most of the same histograms,
like idhist, mhist, etc.
Not currently designed for reference with multiple sequences,
or duplicate kmers of length used for indexing.

Usage:  microalign.sh in_file=<input file> out=<output file> ref=<reference>

Input may be fasta or fastq, compressed or uncompressed.

Standard parameters:
in_file=<file>       Primary input, or read 1 input.
in2=<file>      Read 2 input if reads are in two files.
out=<file>      Primary output, or read 1 output.
out2=<file>     Read 2 output if reads are in two files.
outu=<file>     Optional unmapped read output.
outu2=<file>    Optional unmapped read 2 output.

Processing parameters:
k=17            Main kmer length.
k2=13           Sub-kmer length for paired reads only.
minid=0.66      Minimum alignment identity.
minid2=0.56     Minimum alignment identity if the mate is mapped.
mm=1            Middle mask length; the index uses gapped kmers.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for microalign.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("microalign.sh", args, capture_output)

def msa(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for msa.sh

    Help message:
    Written by Brian Bushnell
Last modified February 5, 2020

Description:  Aligns a query sequence to reference sequences.
Outputs the best matching position per reference sequence.
If there are multiple queries, only the best-matching query will be used.
MSA in this context stands for MultiStateAligner, not Multiple Sequence Alignment.

Usage:
msa.sh in_file=<file> out=<file> literal=<literal,literal,...>
or
msa.sh in_file=<file> out=<file> ref=<lfile>

Parameters:
in_file=<file>       File containing reads.
out=<file>      Sam output file.
literal=        A sequence of bases to match, or a comma-delimited list.
ref=<file>      A fasta file of bases to match.  Please set either ref
                or literal, not both.
rcomp=t         Also look for reverse-complements of the sequences.
addr=f          Add r_ prefix to reverse-complemented alignments.
replicate=f     Make copies of sequences with undefined bases for every
                possible combination.  For example, ATN would expand to
                ATA, ATC, ATG, and ATT.
cutoff=0        Ignore alignments with identity below this (range 0-1).
swap=f          Swap the reference and query; e.g., report read alignments
                to the reference instead of reference alignments to the reads.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding automatic
                memory detection. -Xmx20g will specify 
                20 gigs of RAM, and -Xmx200m will specify 200 megs.  
                The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for msa.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("msa.sh", args, capture_output)

def mutate(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for mutate.sh

    Help message:
    Written by Brian Bushnell
Last modified May 25, 2025

Description:  Creates a mutant version of a genome.
Also produces a VCF listing the added mutations.

Usage:  mutate.sh in_file=<input file> out=<output file> id=<identity>

I/O parameters:
in_file=<file>       Input genome.
out=<file>      Output mutant genome.
vcf=<file>      Output VCF file showing variations added.
overwrite=f     (ow) Set to false to force the program to abort rather than
                overwrite an existing file.
ziplevel=2      (zl) Set to 1 (lowest) through 9 (max) to change compression
                level; lower compression is faster.

Processing parameters:
subrate=0       Substitution rate, 0 to 1.
insrate=0       Insertion rate, 0 to 1.
delrate=0       Deletion rate, 0 to 1.
indelrate=0     Sets ins and del rate each to half of this value.
maxindel=1      Max indel length.
indelspacing=3  Minimum distance between subsequent indels.
id=1            Target identity, 0 to 1; 1 means 100%.
                If this is used it will override subrate and indelrate;
                99% of the mutations will be substitutions, and 1% indels.
fraction=1      Genome fraction, 0 to 1; 1 means 100%.  A lower fraction
                will randomly select that fraction on a per-sequence basis,
                possibly incurring one chimeric junction per sequence.
                Not compatible with VCF output.
period=-1       If positive, place exactly one mutation every X bases.
prefix=         Set this flag to rename the new contigs with this prefix
                and a number.
amino=f         Treat the input as amino acid sequence.
ploidy=1        Set the ploidy.  ploidy>1 allows heterozygous mutations.
                This will create one copy of each input sequence per ploidy.
hetrate=0.5     If polyploid, fraction of mutations that are heterozygous.
nohomopolymers=f  If true, prevent indels in homopolymers that lead to
                ambiguous variant calls.  For example, inserting A between
                AC or deleting T from TTTT.  This is mainly for grading 
                purposes.  It does not fully solve the problem, but greatly
                improves concordance (reducing disagreements by 70%).
                NOTE! nohomopolymers is temporarily disabled.
pad=0           Add this many random bases to the ends of input sequences.
                Padleft and padright may also be specified independently.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for mutate.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("mutate.sh", args, capture_output)

def muxbyname(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for muxbyname.sh

    Help message:
    Written by Brian Bushnell
Last modified June 22, 2016

Description:  Multiplexes reads from multiple files after renaming them based on their initial file.
Opposite of demuxbyname.

Usage:  muxbyname.sh in_file=<file,file,file...> out=<output file>
Input files may also be given without an in_file= prefix, so that you can use wildcards:
muxbyname.sh *.fastq out=muxed.fastq


Standard parameters:
in_file=<file,file>  A list of input files.
in2=<file,file> Read 2 input if reads are in paired files.
out=<file>      Primary output, or read 1 output.
out2=<file>     Read 2 output if reads are in paired files.
overwrite=f     (ow) Set to false to force the program to abort rather than
                overwrite an existing file.
showspeed=t     (ss) Set to 'f' to suppress display of processing speed.
ziplevel=2      (zl) Set to 1 (lowest) through 9 (max) to change compression
                level; lower compression is faster.

Processing parameters:
None yet!

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for muxbyname.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("muxbyname.sh", args, capture_output)

def netfilter(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for netfilter.sh

    Help message:
    Written by Brian Bushnell
Last modified Oct 30, 2023

Description:  Scores sequences using a neural network.  This is similar
to scoresequence.sh but multithreaded and with more filtering options.

Usage:  netfilter.sh in_file=<sequences> out=<pass> outu=<fail> net=<net file>

Input may be fasta or fastq, compressed or uncompressed.

Standard parameters:
in_file=<file>       Input sequences.
out=<file>      Sequences passing the filter.
outu=<file>     Sequences failing the filter.
net=<file>      Network file to apply to the sequences.
hist=<file>     Histogram of scores (x100, so 0-1 maps to 0-100).
overwrite=f     (ow) Set to false to force the program to abort rather than
                overwrite an existing file.

Processing parameters:
rcomp=f         Use the max score of a sequence and its reverse complement.
parse=f         Parse sequence headers for 'result=' to determine whether
                they are positive or negative examples.  Positive examples
                should be annotated with result=1, and negative with result=0.
annotate=f      Rename output sequences by appending 'score='.
filter=t        Retain only reads above or below a cutoff.  Setting the cutoff
                or highpass flag will automatically set this to true.
cutoff=auto     Score cutoff for filtering; scores mostly range from 0 to 1.
                'auto' will use the cutoff embedded in the network.
highpass=t      Retain sequences ABOVE cutoff if true, else BELOW cutoff.
scoremode=      single (default): Apply the network once to each sequence.
                  If the sequence is longer than the network's inputs, use the
                  first X bases.
                average: Apply the network to the sequence once every 
                  'stepsize' bases, and use the average.  May be slow.
                max: Like average, but uses the maximum score.
                min: Like average, but uses the minimum score.
pairmode=       average (default): For paired reads, average the two scores.
                max: Use the higher of the two scores.
                min: Use the lower of the two scores.
stepsize=1      If scoremode is other than 'single', score a window every
                this many bases.  The window width is defined by the network.
                Higher values of stepsize are faster.
overlap=        This can be set instead of stepsize; if either flag is used it
                will override the other.  Setting overlap will make windows
                overlap that much, so 'overlap=0' is equivalent to 'stepsize=W'
                where W is the width of the network in bases.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for netfilter.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("netfilter.sh", args, capture_output)

def novademux(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for novademux.sh

    Help message:
    Written by Brian Bushnell
Last modified November 18, 2024

Description:  Demultiplexes sequencer reads into multiple files based on
their barcodes.  Uses statistical analysis to ensure optimal yield and
minimal crosstalk in the presence of errors.  Barcodes (indexes) must be
embedded in read headers, and the expected barcodes must be provided
as a text file with one barcode (or barcode pair) per line.

Usage example for single-ended or interleaved files:

novademux.sh in_file=reads.fq out=out_%.fq outu=unknown.fq expected=barcodes.txt

For twin files:
novademux.sh in_file=in_#.fq out=out_%_#.fq.gz outu=unk_#.fq expected=barcodes.txt


File Parameters:
in_file=<file>       Input file.
in2=<file>      If input reads are paired in twin files, use in2 for the 
                second file.  You can alternatively use the # symbol,
                e.g. 'in_file=read_#.fastq.gz', which is equivalent to
                'in1=read_1.fastq.gz in2=read_2.fastq.gz'.
out=<file>      Output files for reads with matched headers (must contain %
                symbol).  For example, out=out_%.fq with indexes XX and YY 
                would create out_XX.fq and out_YY.fq.  If twin files for
                paired reads are desired, use the # symbol.  For example,
                out=out_%_#.fq in this case would create out_XX_1.fq, 
                out_XX_2.fq, out_YY_1.fq, and out_YY_2.fq.
outu=<file>     Output file for reads with unmatched headers.
stats=<file>    Print statistics about how many reads went to each file.
expected=       List of barcodes (or files containing containing barcodes) 
                to parse from read headers.  Files should contain one barcode 
                per line.  For example, 'expected=barcodes.txt' or
                'expected=ACGTACGT,GGTTAACC,AACCGGTT'.  This list must be
                contain all pooled barcodes to ensure accuracy, including
                PhiX if present.
writeempty=t    Write empty files for expected but absent barcodes.
subset=         Optional list of barcodes when only some output files are
                desired; only demultiplex these libraries.
nosplit=f       When true, dump all reads to outu instead of individual files.
rename=f        When true, append the assigned barcode (or 'unknown') to
                each read header, after a tab.  Can be used in conjunction 
                with nosplit to simply label reads.
rc1=f           Reverse-complement index1 from expected and samplemap.
rc2=f           Reverse-complement index2 from expected and samplemap.
addpolyg=f      It is recommended to set this to true on a platform where
                no signal is read as G.  This will add poly-G as a dummy
                expected barcode.  If no signal yields a different base call,
                use the appropriate flag (addpolyc, etc).
remap=          Change symbols for output filenames.  For example, remap=+-
                would output barcode ACGT+TGCA to file ACGT-TCGA.fq.gz.

Legacy Output Stats File Support:
legacy=         Set this to a path like '.' to output legacy stats files.
samplemap=      An input csv or tsv containing barcodes and sample names,
                for legacy stats.  If present 'expected' can be omitted.
lane=0          Set this to a number to print the lane in legacy files.

Barcode Parsing Modes (choose one):
barcode         Parse the barcode automatically, assuming the standard
                Illumina header format.  This is the default.
header          Match the entire read header.
prefix          Match the prefix of the read header (length must be set).
suffix          Match the suffix of the read header (length must be set).
hdelimiter=     (headerdelimiter) Split the header using this delimiter,
                then select a term (column must be set).  Normally the 
                delimiter will be used as a literal string (a Java regular
                expression); for example, ':' or 'HISEQ'.  But there are
                some special delimiters which will be replaced by the symbol
                they name, because they can cause problems.
                These are provided for convenience due to OS conflicts:
                   space, tab, whitespace, pound, greaterthan, lessthan, 
                   equals, colon, semicolon, bang, and, quote, singlequote
                These are provided because they interfere with Java regular 
                expression syntax:
                   backslash, hat, dollar, dot, pipe, questionmark, star,
                   plus, openparen, closeparen, opensquare, opencurly
                In other words, to match '.', you should set 'hdelimiter=dot'.

length=0        For prefix or suffix mode, use this many characters from
                the read header.  Must be positive in these modes.
column=0        Select the term when using a header delimiter.  This is
                1-based (first term is column 1) so it must be positive.

Barcode Assignment Mode (choose one):
mode=prob       prob: Default mode.  Assigns reads to the bin where they most
                   likely belong, from gathering statistics across the pool.
                tile: Similar to prob, but calculates statistics on a per-tile
                   basis for higher precision.  This mode is recommended as
                   long as the tile numbers are in the read headers.
                hdist: Demultiplex reads to the bin with the fewest 
                   mismatches.  This is the fastest and least accurate mode.
                   Here, 'hdist' stands for 'Hamming distance'.
Note: prob and tile mode may require a license.

Server Parameters (for prob Mode only):
server=auto     true:  Barcode counts are sent to a remote server for 
                       processing, and barcode assignments are sent back.
                false: Barcode counts are processed locally.
                auto:  Sets flag to false unless the local machine contains
                       proprietary probabilistic processing code.

Sensitivity Cutoffs for Prob/Tile Mode:
maxhdist=6     Maximum Hamming distance (number of mismatches) allowed.
                Lower values will reduce yield with little benefit.
pairhdist=f     When true, maxhdist will apply to the Hamming distance of
                both barcodes combined (if using dual indexes).  When false,
                maxhdist will apply to each barcode individually.
minratio=1m     Minimum ratio of probabilities allowed; k/m/b suffixes are
                allowed.  ratio=1m will only assign a barcode to a bin if
                it is at least 1 million times more likely to belong in that
                bin than in all others combined.  Lower values will increase
                yield but may increase crosstalk.
minprob=-5.6    Discard reads with a lower probability than this of belonging
                to any bin.  This is log10-scale, so -5 means 10^-5=0.00001.
                Lower values will increase yield but increase crosstalk.
                E.g., -6 would be lower than -5.
matrixthreads=1 More threads is faster but adds nondeterminism.
Note: These cutoffs are optimized for dual 10bp indexes.  For single 10bp
indexes, 'minratio=5000 minprob=-3.2' is recommended.

Sensitivity Cutoffs for HDist Mode
maxhdist=1      Maximum Hamming distance (number of mismatches) allowed.
                Lower values will reduce yield and decrease crosstalk.
                Setting maxhdist=0 will allow exact matches only.
pairhdist=f     When true, maxhdist will apply to the Hamming distance of
                both barcodes combined (if using dual indexes).  When false,
                maxhdist will apply to each barcode individually.
clearzone=1     (cz) Minimum difference between the closest and second-closest
                Hamming distances.  For example, AAAG is 1 mismatch from
                AAAA and 3 mismatches away from GGGG, for a margin of 3-1=2.
                This would be demultiplexed into AAAA as long as the
                clearzone is set to at most 2.  Lower values increase both
                yield and crosstalk.

Buffering Parameters
streams=8       Allow at most this many active streams.  The actual number
                of open files will be 1 greater than this if outu is set,
                and doubled if output is paired and written in twin files 
                instead of interleaved.  Setting this to at least the number
                of expected output files can make things go much faster.
minreads=0      Don't create a file for fewer than this many reads; instead,
                send them to unknown.  This option will incur additional
                memory usage.
rpb=8000        Dump buffers to files when they fill with this many reads.
                Higher can be faster; lower uses less memory.
bpb=8000000     Dump buffers to files when they contain this many bytes.
                Higher can be faster; lower uses less memory.

Special Processing of Spike-ins (particularly for spike-ins with no barcodes)
spikelabel=     If and only if a spike-in label is set here, reads will be
                aligned to a reference, and matching reads will be sent to
                the file with this label.  May be a barcode or other string.
refpath=phix    Override this with a file path for a custom reference.
kspike=27       Use this kmer length to map reads.
minid=0.7       Identity cutoff for matching the reference.
mapall=f        Map all reads to the reference, instead of just unassigned
                reads.

Common parameters:
ow=t            (overwrite) Overwrites files that already exist.
zl=4            (ziplevel) Set compression level, 1 (low) to 9 (max).
int=auto        (interleaved) Determines whether INPUT file is considered 
                interleaved.                

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify
                200 megs.  The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for novademux.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("novademux.sh", args, capture_output)

def partition(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for partition.sh

    Help message:
    Written by Brian Bushnell
Last modified September 6, 2023

Description:  Splits a sequence file evenly into multiple files.

Usage:  partition.sh in_file=<file> in2=<file2> out=<outfile> out2=<outfile2> ways=<number>

in2 and out2 are for paired reads and are optional.
If input is paired and out2 is not specified, data will be written interleaved.
Output filenames MUST contain a '%' symbol.  This will be replaced by a number.

Parameters and their defaults:

in_file=<file>       Input file.
out=<file>      Output file pattern (containing a % symbol, like 'part%.fa').
ways=-1         The number of output files to create; must be positive.
pacbio=f        Set to true to keep PacBio subreads together.
bp=f            Optimize for an even split by base pairs instead of sequences.
                Not compatible with PacBio mode.

ow=f            (overwrite) Overwrites files that already exist.
app=f           (append) Append to files that already exist.
zl=4            (ziplevel) Set compression level, 1 (low) to 9 (max).
int=f           (interleaved) Determines whether INPUT file is considered interleaved.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for partition.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("partition.sh", args, capture_output)

def phylip2fasta(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for phylip2fasta.sh

    Help message:
    Written by Brian Bushnell
Last modified October 3, 2014

Description:  Transforms interleaved phylip to fasta.

Usage:   phylip2fasta.sh in_file=<input> out=<output>

Input may be stdin or an interleaved phylip file, compressed or uncompressed.

Input Parameters:
in_file=<file>       The input phylip file; this is the only required parameter.
unpigz=true     Decompress with pigz for faster decompression.

Output Parameters:
out=<file>      Fasta output destination.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for phylip2fasta.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("phylip2fasta.sh", args, capture_output)

def picksubset(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for picksubset.sh

    Help message:
    Written by Brian Bushnell
Last modified July 30, 2024

Description:  Selects a subset of files from an all-to-all identity
comparison.  The subset will contain exactly X files with maximal
pairwise ANI, or all files with at most Y pairwise identity.
This program is similar to representative.sh but does not use taxonomy.

Input should be in 3+ column TSV format (first 3 are required):
(query, ref, ANI)
...as produced by CompareSketch when run like this:
comparesketch.sh ata format=3 includeself perfile records=99999 *.fasta

Usage:  picksubset.sh in_file=<file> out=<file> invalid=<file> files=<number>

Parameters:
in_file=             Input file comparing all-to-all comparisons.
out=            Output file for the list of files to retain.
invalid=        Output file for the list of files to discard.
overwrite=f     (ow) Set to false to force the program to abort rather than
                overwrite an existing file.
files=0         Number of files to retain.
ani=0           Maximum pairwise ANI allowed, expressed as a percent.
NOTE: files or ani, or both, must be set.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will
                specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                The max is typically around 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for picksubset.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("picksubset.sh", args, capture_output)

def pileup(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for pileup.sh

    Help message:
    Written by Brian Bushnell
Last modified September 28, 2024

Description:  Calculates per-scaffold or per-base coverage information from an unsorted sam or bam file.
Supports SAM/BAM format for reads and FASTA for reference.
Sorting is not needed, so output may be streamed directly from a mapping program.
Requires a minimum of 1 bit per reference base plus 100 bytes per scaffold (even if no reference is specified).
If per-base coverage is needed (including for stdev and median), at least 4 bytes per base is needed.

Usage:        pileup.sh in_file=<input> out=<output>

Input Parameters:
in_file=<file>           The input sam file; this is the only required parameter.
ref=<file>          Scans a reference fasta for per-scaffold GC counts, not otherwise needed.
fastaorf=<file>     An optional fasta file with ORF header information in PRODIGAL's output format.  Must also specify 'outorf'.
unpigz=t            Decompress with pigz for faster decompression.
addfromref=t        Allow ref scaffolds not present in sam header to be added from the reference.
addfromreads=f      Allow ref scaffolds not present in sam header to be added from the reads.
                    Note that in this case the ref scaffold lengths will be inaccurate.

Output Parameters:
out=<file>          (covstats) Per-scaffold coverage info.
rpkm=<file>         Per-scaffold RPKM/FPKM counts.
twocolumn=f         Change to true to print only ID and Avg_fold instead of all 6 columns.
countgc=t           Enable/disable counting of read GC content.
outorf=<file>       Per-orf coverage info to this file (only if 'fastaorf' is specified).
outsam=<file>       Print the input sam stream to this file (or stdout).  Useful for piping data.
hist=<file>         Histogram of # occurrences of each depth level.
basecov=<file>      Coverage per base location.
rangecov=<file>     Concise ranges where coverage depth is at least mincov.
mincov=1            When calculating percent covered, ignore bases under this depth.
                    Also used as threshold for rangecov.
bincov=<file>       Binned coverage per location (one line per X bases).
binsize=1000        Binsize for binned coverage output.
keepshortbins=t     (ksb) Keep residual bins shorter than binsize.
normcov=<file>      Normalized coverage by normalized location (X lines per scaffold).
normcovo=<file>     Overall normalized coverage by normalized location (X lines for the entire assembly).
normb=-1            If positive, use a fixed number of bins per scaffold; affects 'normcov' and 'normcovo'.
normc=f             Normalize coverage to fraction of max per scaffold; affects 'normcov' and 'normcovo'.
delta=f             Only print base coverage lines when the coverage differs from the previous base.
nzo=f               Only print scaffolds with nonzero coverage.
concise=f           Write 'basecov' in a more concise format.
header=t            (hdr) Include headers in output files.
headerpound=t       (#) Prepend header lines with '#' symbol.
stdev=t             Calculate coverage standard deviation.
covminscaf=0        (minscaf) Don't print coverage for scaffolds shorter than this.
covwindow=0         Calculate how many bases are in windows of this size with
                    low average coverage.  Produces an extra stats column.
covwindowavg=5      Average coverage below this will be classified as low.
k=0                 If positive, calculate kmer coverage statstics for this kmer length.
keyvalue=f          Output statistics to screen as key=value pairs.

Processing Parameters:
strandedcov=f       Track coverage for plus and minus strand independently.
startcov=f          Only track start positions of reads.
stopcov=f           Only track stop positions of reads.
secondary=t         Use secondary alignments, if present.
softclip=f          Include soft-clipped bases in coverage.
minmapq=0           (minq) Ignore alignments with mapq below this.
physical=f          (physcov) Calculate physical coverage for paired reads.  This includes the unsequenced bases.
tlen=t              Track physical coverage from the tlen field rather than recalculating it.
arrays=auto         Set to t/f to manually force the use of coverage arrays.  Arrays and bitsets are mutually exclusive.
bitsets=auto        Set to t/f to manually force the use of coverage bitsets.
32bit=f             Set to true if you need per-base coverage over 64k; does not affect per-scaffold coverage precision.
                    This option will double RAM usage (when calculating per-base coverage).
delcoverage=t       (delcov) Count bases covered by deletions or introns as covered.
                    True is faster than false.
dupecoverage=t      (dupes) Include reads flagged as duplicates in coverage.
samstreamer=t       (ss) Load reads multithreaded to increase speed.

Trimming Parameters: 
** NOTE: These are applied before adding coverage, to allow mimicking **
** tools like CallVariants, which uses 'qtrim=r trimq=10 border=5'    **
qtrim=f             Quality-trim.  May be set to:
                       f (false): Don't quality-trim.
                       r (right): Trim right (3') end only.
                       l (left): Trim right (5') end only.
                       rl (both): Trim both ends.
trimq=-1            If positive, quality-trim to this threshold.
border=0            Ignore this many bases on the left and right end.

Output format (tab-delimited):
ID, Avg_fold, Length, Ref_GC, Covered_percent, Covered_bases, Plus_reads, Minus_reads, Read_GC, Median_fold, Std_Dev

ID:                Scaffold ID
Length:            Scaffold length
Ref_GC:            GC ratio of reference
Avg_fold:          Average fold coverage of this scaffold
Covered_percent:   Percent of scaffold with any coverage (only if arrays or bitsets are used)
Covered_bases:     Number of bases with any coverage (only if arrays or bitsets are used)
Plus_reads:        Number of reads mapped to plus strand
Minus_reads:       Number of reads mapped to minus strand
Read_GC:           Average GC ratio of reads mapped to this scaffold
Median_fold:       Median fold coverage of this scaffold (only if arrays are used)
Std_Dev:           Standard deviation of coverage (only if arrays are used)

Java Parameters:

-Xmx               This will set Java's memory usage, overriding 
                   autodetection. -Xmx20g will 
                   specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.  
                   The max is typically 85% of physical memory.
-eoom              This flag will cause the process to exit if an out-of-memory
                   exception occurs.  Requires Java 8u92+.
-da                Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for pileup.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("pileup.sh", args, capture_output)

def pileup2(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for pileup2.sh

    Help message:
    Written by Brian Bushnell
Last modified April 17, 2024

Description:  This is a version of Pileup designed to process multiple files
concurrently.  If you only have one input file just use regular Pileup.
Other than those mentioned here, the flags are the same as in pileup.sh.

Usage:        pileup2.sh in_file=<file,file,file> out=<file>
Alternate:    pileup2.sh *.sam out=<file>

Parameters:
in_file=<file,file>     The input sam/bam files.  Omit the 'in_file=' if a wildcard
                   is used.
streams=-1         If positive, use at most this many concurrent streams.
                   Default is half the number of logical processors.  Note 
                   that each stream uses multiple threads.
atomic=false       Use atomic arrays instead of locks.
prealloc=false     Preallocate coverage arrays instead of creating them 
                   as needed.

Java Parameters:
-Xmx               This will set Java's memory usage, overriding 
                   autodetection. -Xmx20g will 
                   specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.  
                   The max is typically 85% of physical memory.
-eoom              This flag will cause the process to exit if an out-of-memory
                   exception occurs.  Requires Java 8u92+.
-da                Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for pileup2.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("pileup2.sh", args, capture_output)

def plotflowcell(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for plotflowcell.sh

    Help message:
    Written by Brian Bushnell
Last modified August 9, 2018

Description:  Generates statistics about flowcell positions.
Seems entirely superceded by filterbytile now; to be removed after 39.12.

Usage:	plotflowcell.sh in_file=<input> out=<output>

Input parameters:
in_file=<file>           Primary input file.
in2=<file>          Second input file for paired reads in two files.
indump=<file>       Specify an already-made dump file to use instead of
                    analyzing the input reads.
reads=-1            Process this number of reads, then quit (-1 means all).
interleaved=auto    Set true/false to override autodetection of the
                    input file as paired interleaved.

Output parameters:
out=<file>          Output file for filtered reads.
dump=<file>         Write a summary of quality information by coordinates.

Tile parameters:
xsize=500           Initial width of micro-tiles.
ysize=500           Initial height of micro-tiles.
size=               Allows setting xsize and ysize tot he same value.
target=800          Iteratively increase the size of micro-tiles until they
                    contain an average of at least this number of reads.

Other parameters:
trimq=-1            If set to a positive number, trim reads to that quality
                    level instead of filtering them.
qtrim=r             If trimq is positive, to quality trimming on this end
                    of the reads.  Values are r, l, and rl for right,
                    left, and both ends.

Java Parameters:
-Xmx                This will set Java's memory usage, overriding autodetection.
                    -Xmx20g will specify 20 GB of RAM; -Xmx200m will specify 
                    200 MB.  The max is typically 85% of physical memory.
-eoom               This flag will cause the process to exit if an
                    out-of-memory exception occurs.  Requires Java 8u92+.
-da                 Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for plotflowcell.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("plotflowcell.sh", args, capture_output)

def plotgc(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for plotgc.sh

    Help message:
    Written by Brian Bushnell
Last modified February 27, 2017

Description:  Prints sequence gc content once per interval.

Usage:  plotgc.sh in_file=<input file> out=<output file>

Parameters:
in_file=<file>       Input file. in_file=stdin.fa will pipe from stdin.
out=<file>      Output file.  out=stdout will pipe to stdout.
interval=1000   Interval length.
offset=0        Position offset.  For 1-based indexing use offset=1.
psb=t           (printshortbins) Print gc content for the last bin of a contig
                even when shorter than interval.

Java Parameters:

-Xmx            This will set Java's memory usage, overriding automatic
                memory detection. -Xmx20g will 
                specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.  
                The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for plotgc.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("plotgc.sh", args, capture_output)

def plothist(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for plothist.sh

    Help message:
    Written by Brian Bushnell
Last modified November 5, 2024

Description:  Generates histograms from a tile dump.
Also works on other 2D numeric matrices with a header.
Output files are automatically named from the header columns.

Usage:  plothist.sh in_file=<input file> bins=<number>

Parameters:
in_file=<file>       Input dump file.
bins=1000       Bins per histogram.
overwrite=t     (ow) Set to false to force the program to abort rather than
                overwrite an existing file.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for plothist.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("plothist.sh", args, capture_output)

def plotreadposition(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for plotreadposition.sh

    Help message:
    Written by Brian Bushnell
Last modified March 11, 2024

Description:  Plots Illumina read positions and barcode hamming distance.

Usage:  plotreadposition.sh in_file=<file.fq> out=<file.tsv> expected=<barcodes.txt>

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for plotreadposition.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("plotreadposition.sh", args, capture_output)

def polyfilter(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for polyfilter.sh

    Help message:
    Written by Brian Bushnell
Last modified October 1, 2024

Description:  Filters reads to remove those with suspicious homopolymers.

Usage:  polyfilter.sh in_file=<input reads> out=<filtered reads>

Example:
polyfilter.sh in_file=reads.fq out=clean.fq outb=bad.fq k=31 polymers=G


File parameters:
in_file=<file>       Primary input, or read 1 input.
in2=<file>      Read 2 input if reads are in two files.
out=<file>      Output for clean reads.
outb=<file>     Output for bad (homopolymer) reads.
extra=<file>    Comma-delimited list of additional sequence files.
                For depth-based filtering, set this to the same as the input.
overwrite=t     (ow) Set to false to force the program to abort rather than
                overwrite an existing file.

Hashing parameters:
k=31            Kmer length.
hashes=2        Number of hashes per kmer.  Higher generally reduces 
                false positives at the expense of speed.
sw=t            (symmetricwrite) Increases accuracy when bits>1 and hashes>1.
minprob=0.5     Ignore reference kmers with probability of being correct
                below this (affects fastq references only).
memmult=1.0     Fraction of free memory to use for Bloom filter.  1.0 should
                generally work; if the program crashes with an out of memory
                error, set this lower.  Higher increases specificity.
cells=          Option to set the number of cells manually.  By default this
                will be autoset to use all available memory.  The only reason
                to set this is to ensure deterministic output.
seed=0          This will change the hash function used.
bits=           Bits per cell; it is set automatically from mincount.

Filtering rules:
Reads will always be discarded if they fails ldf2, entropy2, or minpolymer2.
Reads will also be discarded if they fail (minpolymer AND (ldf OR entropy)).
A read pair will be discarded if either read is discarded.

Depth-filtering parameters:
mincount=2      Minimum number of times a read kmer must occur in the 
                read set to be considered 'high-depth'.
ldf=0.24        (lowdepthfraction) Consider a read low-depth if at least
                this fraction of kmers are low depth.  Setting this above 1
                will disable depth analysis (making the program run faster).
ldf2=1.1        Discard reads with at least this fraction of low-depth kmers.
                Values above 1 disables this filter (e.g., for metagenomes).

Entropy-filtering parameters:
entropy=0.67    Reads with average entropy below this are considered 
                low-entropy.
entropy2=0.2    Reads with average entropy below this are discarded.

Quality-filtering parameters (only useful if q-scores are correct):
quality=12.5    Reads with average quality below this are considered 
                low-quality.
quality2=7.5    Reads with average quality below this are discarded.

Homopolymer-filtering parameters:
polymers=GC     Look for homopolymers of these symbols.  e.g., polymers=GC
                would look for poly-G or poly-C (but not poly-GC).
minpolymer=20   Minimum length of homopolymers.
minpolymer2=29  Discard any read with a homopolymer of at least this length.
purity=0.85     Min fraction of the homopolymer region that is the correct
                symbol.  For example, GGGGGGAGGG is length 10 with 9 Gs, for
                a purity of 0.90 (insufficient in this case due to length).

Trimming parameters:
trimpolymers=   Homopolymers to use for trimming.  If unspecified, it will
                be the same as 'polymers'.
trimleft=6      Trim left ends where there is a homopolymer at least this
                long; 0 disables trimming.
trimright=6     Trim left ends where there is a homopolymer at least this
                long; 0 disables trimming.
trim=           Sets both trimleft and trimright.
maxnonpoly=2    Trim through up to this many consecutive mismatches.
minlen=50       Discard reads shorter than this after trimming.

Other parameters:
quantize=1      If greater than 1, bin the quality scores to reduce file size.
cardinality=t   Report estimated number of unique output kmers.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for polyfilter.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("polyfilter.sh", args, capture_output)

def postfilter(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for postfilter.sh

    Help message:
    Written by Brian Bushnell
Last modified July 27, 2015

Description:  Maps reads, then filters an assembly by contig coverage.
Intended to reduce misassembly rate of SPAdes by removing suspicious contigs.

Usage:  postfilter.sh in_file=<reads> ref=<contigs> out=<filtered contigs>

Standard Parameters:
in_file=<file>           File containing input reads.
in2=<file>          Optional file containing read mates.
ref=<file>          File containing input assembly.
cov=covstats.txt    File to write coverage stats generated by pileup.
out=filtered.fa     Destination of clean output assembly.
outdirty=<file>     (outd) Destination of removed contigs; optional.
ow=f                (overwrite) Overwrites files that already exist.
app=f               (append) Append to files that already exist.
zl=4                (ziplevel) Set compression level, 1 (low) to 9 (max).
int=f               (interleaved) Determines whether input reads are considered interleaved.

Filtering Parameters:
minc=2              (mincov) Discard contigs with lower average coverage.
minp=95             (minpercent) Discard contigs with a lower percent covered bases.
minr=6              (minreads) Discard contigs with fewer mapped reads.
minl=400            (minlength) Discard shorter contigs.
trim=0              (trimends) Trim the first and last X bases of each sequence.

Mapping Parameters (unlisted params will use BBMap defaults)
minhits=2
maxindel=0
tipsearch=0
bw=20
rescue=f

Java Parameters:
-Xmx                This will set Java's memory usage, overriding autodetection.
                    -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom               This flag will cause the process to exit if an
                    out-of-memory exception occurs.  Requires Java 8u92+.
-da                 Disable assertions.

Other parameters will be passed directly to BBMap.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for postfilter.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("postfilter.sh", args, capture_output)

def printtime(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for printtime.sh

    Help message:
    Written by Brian Bushnell
Last modified January 21, 2015

Description:    Prints time elapsed since last called on the same file.

Usage:          printtime.sh <filename>

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for printtime.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("printtime.sh", args, capture_output)

def processfrag(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for processfrag.sh

    Help message:
    Written by Brian Bushnell
Last modified March 15, 2016

Description:  Reformats output from a script.
Made for generating the BBMerge paper data.

Usage:  processfrags.sh <file>

Processing parameters:
None yet!

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for processfrag.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("processfrag.sh", args, capture_output)

def processhi_c(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for processhi-c.sh

    Help message:
    Written by Brian Bushnell
Last modified March 28, 2018

Description:  Finds and trims junctions in mapped Hi-C reads.
For the purpose of reporting junction motifs, this requires paired-end reads,
because only improper pairs will be considered as possibly containing 
junctions.  However, all reads that map with soft-clipping will be trimmed
on the 3' (right) end, regardless of pairing status.

Usage:  processhi-c.sh in_file=<mapped reads> out=<trimmed reads>

Parameters:
in_file=<file>       A sam/bam file containing mapped reads.
out=<file>      Output file of trimmed reads.
overwrite=f     (ow) Set to false to force the program to abort rather than
                overwrite an existing file.
printkmers=t    Generate files with kmer counts at junction sites.
junctions=junctions_k%.txt  File pattern for junction output.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for processhi-c.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("processhi-c.sh", args, capture_output)

def processspeed(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for processspeed.sh

    Help message:
    Written by Brian Bushnell
Last modified December 6, 2016

Description:  Summarizes results of Linux time command.

Usage:        processspeed.sh <file>

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for processspeed.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("processspeed.sh", args, capture_output)

def quabblealigner(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for quabblealigner.sh

    Help message:
    Written by Brian Bushnell
Last modified May 24, 2025

Description:  Aligns a query sequence to a reference using QuabbleAligner.
The sequences can be any characters, but N is a special case.
Outputs the identity, rstart, and rstop positions.
Optionally prints a state space exploration map.
This map can be fed to visualizealignment.sh to make an image.

Usage:
quabblealigner.sh <query> <ref>
quabblealigner.sh <query> <ref> <map>
quabblealigner.sh <query> <ref> <map> <iterations>

Parameters:
query           A literal nucleotide sequence or fasta file.
ref             A literal nucleotide sequence or fasta file.
map             Optional output text file for matrix score space.
                Set to null for benchmarking with no visualization.
iterations      Optional integer for benchmarking multiple iterations.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for quabblealigner.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("quabblealigner.sh", args, capture_output)

def quantumaligner(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for quantumaligner.sh

    Help message:
    Written by Brian Bushnell
Last modified May 4, 2025

Description:  Aligns a query sequence to a reference using QuantumAligner.
The sequences can be any characters, but N is a special case.
Outputs the identity, rstart, and rstop positions.
Optionally prints a state space exploration map.
This map can be fed to visualizealignment.sh to make an image.

Usage:
quantumaligner.sh <query> <ref>
quantumaligner.sh <query> <ref> <map>
quantumaligner.sh <query> <ref> <map> <iterations>

Parameters:
query           A literal nucleotide sequence or fasta file.
ref             A literal nucleotide sequence or fasta file.
map             Optional output text file for matrix score space.
                Set to null for benchmarking with no visualization.
iterations      Optional integer for benchmarking multiple iterations.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for quantumaligner.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("quantumaligner.sh", args, capture_output)

def quickbin(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for quickbin.sh

    Help message:
    Written by Brian Bushnell
Last modified June 23, 2025

Description:  Bins contigs using coverage and kmer frequencies.
If reads or covstats are provided, coverage will be calculated from those;
otherwise, it will be parsed from contig headers.  Coverage can be parsed
from Spades or Tadpole contig headers; alternatively, renamebymapping.sh
can be used to annotate the headers with coverage from multiple sam files.
Any number of sam files may be used (from different samples of the same
environment, usually).  The more sam files, the more accurate.  Ideally,
sam files will be generated from paired reads like this:
bbmap.sh ref=contigs.fa in_file=reads.fq ambig=random mateqtag minid=0.9 maxindel=10 out=mapped.sam
For PacBio-only metagenomes, it is best to generate synthetic paired 
reads from the PacBio CCS reads and align them:
randomreadsmg.sh in_file=ccs.fa out=synth.fq depth=10 variance=0 paired length=250 avginsert=600 

Usage:  
quickbin.sh in_file=contigs.fa out=bins *.sam covout=cov.txt
or
quickbin.sh in_file=contigs.fa out=bins cov=cov.txt
or
quickbin.sh contigs.fa out=bins *.sam

File parameters:
in_file=<file>       Assembly input.  A file named *.fa does not need 'in_file='.
reads=<file>    Read input (sam or bam).  Multiple sam files may be used,
                comma-delimited, or as plain arguments without 'reads='.
                Multiple files will be assumed to be independent samples.
covout=<file>   Coverage file summarizing sam files; allows rerunning
                QuickBin much faster.
cov=<file>      Cov file generated by QuickBin via 'covout'; can be used
                instead of sam/bam.  Files named cov*.txt do not need 'cov='
out=<pattern>   Output pattern.  If this contains a % symbol, like bin%.fa,
                one file will be created per bin.  If not, all contigs will
                be written to the same file, with the name modified to
                indicate their bin number.  A term without a '.' symbol
                like 'out=output' will be considered a directory.
chaff           Enable to write small clusters to a shared file.

Size parameters:
mincluster=50k  (mcs) Minimum output cluster size in base pairs; smaller 
                clusters will share a residual file if chaff=t.
mincontig=100   Don't load contigs smaller than this; reduces memory usage.
minseed=3000    Minimum contig length to create a new cluster; reducing this
                can increase speed dramatically for large metagenomes,
                increase sensitivity for small contigs, and slightly increase
                contamination.  In particular, large metagenomes with only 
                1 sample will run slowly if this is below 2000; with 
                at least 3 samples the speed should not be affected much.
minresidue=200  Discard unclustered contigs shorter than this; reduces memory.
dumpsequence    (TODO) Discard sequence to reduce memory usage.
dumpheaders     (TODO) Discard headers to reduce memory usage.
minpentamersize=2k  Increase this to reduce memory usage.

Stringency parameters:
normal          Default stringency is 'normal'.  All settings, in order of
                increasing sensitivity, are:  xstrict, ustrict, vstrict,
                strict, normal, loose, vloose, uloose, xloose.  'normal'
                aims at under 1% contamination; 'uloose' is more comparable
                in stringency to other binners.  To set a stringency just add
                that flag (without an = sign).  Acceptable shorthand is
                xs, us, vs, s, n, l, vl, ul, xl.

Quantization parameters:
gcwidth=0.02    Width of GC matrix gridlines.  Smaller is faster.
depthwidth=0.5  Width of depth matrix gridlines.  Smaller is faster.  This
                is on a log2 scale so 0.5 would mean 2 gridlines per power
                of 2 depth - lines at 0.707, 1, 1.414, 2, 2.818, 4, etc.
Note: Halving either quantization parameter can roughly double speed,
but may decrease recovery of shorter contigs.

Neural network parameters:
net=auto        Specify a neural network file to use; default is 
                bbmap/resources/quickbin1D_all.bbnet
cutoff=0.52     Neural network output threshold; higher increases specificity,
                lower increases sensitivity.  This is a soft cutoff that
                moderates other stringency settings, so increasing it would
                make 'strict' mode stricter.

Edge-processing parameters:
e1=0                  Edge-first clustering passes; may increase speed
                      at the cost of purity.
e2=4                  Later edge-based clustering passes.
edgeStringency1=0.25  Stringency for edge-first clustering; 
                      lower is more stringent.
edgeStringency2=1.1    Stringency for later edge-based clustering.
maxEdges=3            Follow up to this many edges per contig.
minEdgeWeight=2       Ignore edges made from fewer read pairs.
minEdgeRatio=0.4      Ignore edges under this fraction of max edge weight.
goodEdgeMult=1.4      Merge stringency multiplier for contigs joined by
                      an edge; lower is more stringent.
minmapq=20            When loading sam files, do not make edges from reads
                      with map lower than this.  Setting it to 0 will allow
                      ambigiously-mapped reads and may improve completeness.
                      Reads below minmapq are still used for depth.
minid=0.96            When loading sam files, ignore reads aligned with
                      identity below this, both for edges and coverage.

Other parameters:
sketchoutput=f        Use SendSketch to identify taxonomy of output clusters.
validate=f            If contig headers have a term such as 'tid_1234', this
                      will be parsed and used to evaluate correctness.
printcc=f             Print completeness/contam after each step.
callssu=f             Call 16S and 18S genes; do not merge clusters with
                      incompatible SSU sequence.
minssuid=0.98         SSUs with identity below this are incompatible.
aligner=quantum       Options include ssa2, glocal, drifting, banded, crosscut.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for quickbin.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("quickbin.sh", args, capture_output)

def quickclade(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for quickclade.sh

    Help message:
    Written by Brian Bushnell
Last modified May 4, 2025

Description:  Assigns taxonomy to query sequences by comparing kmer
frequencies to those in a reference database.  Developed for taxonomic
assignment of metagenomic bins, but it can also run on a per-sequence basis.
QuickClade is extremely fast and uses little memory.  However, the accuracy
declines for incomplete genomes.  The recommended minimum sequence length
is not yet known, but lower values of k5dif are more likely to be correct
to a lower taxonomic level.  k5dif represents the sum of the absolute values
of the differences between the 5-mer frequency spectra, so the range is 0-1.
Because no marker genes are used, QuickClade should perform similarly for any
clade in the reference dataset.
While the default reference is taxonomically labeled, you can use whatever
you want as a reference, with or without taxonomic labels.

Usage Examples:
quickclade.sh query1.fa query2.fa query3.fa
or
quickclade.sh bins
or
quickclade.sh contigs.fa percontig out=results.tsv usetree


File Parameters:
in_file=<file,file>  Query files or directories.  Loose file or directory names are
                also permitted.  Input can be fasta, fastq, or spectra files;
                spectra files are made by cladeloader.sh.
ref=<file,file> Reference files; the current default is:
                /clusterfs/jgi/groups/gentech/homes/bbushnell/clade/refseq_main.spectra.gz
                It is plaintext, human-readable, and pretty small.
out=stdout      Set to a file to redirect output.  Only the query results will
                be written here; progress messages will still go to stderr.

Basic Parameters:
percontig       Run one query per contig instead of per file.
minlen=0        Ignore sequences shorter than this in percontig mode.
hits=1          Print this many top hits per query.
steps=7         Only search up to this many GC intervals (of 0.01) away from
                the query GC.
oneline         Print results one line per query, tab-delimited.
callssu=f       Call 16S and 18S for alignment to reference SSU.
                This will affect the top hit ordering only if hits>1.

Advanced Parameters (mainly for benchmarking):
printmetrics    Output accuracy statistics; mainly useful for labeled data.
                Labeled data should have 'tid_1234' or similar in the header.
                Works best with 'usetree'.
printqtid       Print query TaxID.
banself         Ignore records with the same TaxID as the query.  Makes the
                program behave like that organism is not in the reference.
simd            Use vector instructions to accelerate comparisons.
maxk=5          Can be set to 4 or 3 to restrict kmer frequency comparisons
                to smaller kmers.  This may improve accuracy for small
                sequences/bins, but slightly reduces accuracy for large
                sequences/bins.
ccm=1.0         Threshold for using pentamers; lower is faster.
ccm2=1.5        Threshold for using tetramers.
gcdif=0.07      Initial maximum GC difference.
strdif=0.10     Initial maximum strandedness difference.
gcmult=0.5      Max GC difference as a fraction of best 5-mer difference.
strmult=1.2     Max strandedness difference as a fraction of best 5-mer diff.
ee=t            Early exit; increases speed.
entropy         Calculate entropy for queries.  Slow; negligible utility.
heap=1          Number of intermediate comparisons to store.
usetree         Load a taxonomic tree for better grading for labeled data.
aligner=quantum Options include ssa2, glocal, drifting, banded, crosscut.
Distance Metrics:
abs             Use absolute difference of kmer frequencies.
cos             Use 1-cosine similarity of kmer frequencies.
euc             Use Euclidian distance.
hel             Use Hellinger distance.
abscomp         GC-compensated version of abs (default).
Note:  The distance metric strongly impacts ccm, gcmult, and strmult.
       Defaults are optimized for abscomp.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for quickclade.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("quickclade.sh", args, capture_output)

def randomgenome(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for randomgenome.sh

    Help message:
    Written by Brian Bushnell
Last modified October 17, 2019

Description:  Generates a random, (probably) repeat-free genome.

Usage:  randomgenome.sh len=<total size> chroms=<int> gc=<float> out=<file>

Parameters:
out=<file>      Output.
overwrite=f     (ow) Set to false to force the program to abort rather than
                overwrite an existing file.
len=100000      Total genome size.
chroms=1        Number of pieces.
gc=0.5          GC fraction.
nopoly=f        Ban homopolymers.
pad=0           Add this many Ns to contig ends; does not count toward 
                genome size.
seed=-1         Set to a positive number for deterministic output.
amino=f         Produce random amino acids instead of nucleotides.
includestop=f   Include stop codons in random amino sequences.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for randomgenome.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("randomgenome.sh", args, capture_output)

def randomreads(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for randomreads.sh

    Help message:
    Written by Brian Bushnell
Last modified April 1, 2019

Description:  Generates random synthetic reads from a reference genome.  Read names indicate their genomic origin.
Allows precise customization of things like insert size and synthetic mutation type, sizes, and rates.
Read names generated by this program are used by MakeRocCure (samtoroc.sh) and GradeSamFile (gradesam.sh).
They can also be used by BBMap (bbmap.sh) and BBMerge (bbmerge.sh) to automatically calculate
true and false positive rates, if the flag 'parsecustom' is used.

Usage:   randomreads.sh ref=<file> out=<file> length=<number> reads=<number>

Basic parameters:
out=null        Output file.  If reads are paired and a single file name is
                given, output will be interleaved.  For paired reads in twin
                files, set out1= and out2= 
ref=null        Reference file.  Not needed if the reference is already indexed.
build=1         If multiple references are indexed in the same directory,
                each needs a unique build ID.
midpad=300      Specifies space between scaffolds in packed index.
reads=0         Generate this many reads (or pairs).
coverage=-1     If positive, generate enough reads to hit this coverage
                target, based on the genome size.
overwrite=t     Set to false to disallow overwriting of existing files.
replacenoref=f  Set to true to replace Ns in the reference sequence 
                with random letters.
simplenames=f   Set to true to generate read names that clearly indicate
                genomic origin, without BBMap internal coordinates.
illuminanames=f Set to true to have matching names for paired reads, 
                rather than naming by location.
renamebyinsert=f    Insert the insert size into the name.
addpairnum=f    Set true to add ' 1:' and ' 2:' to the end of read names.
addslash=f      Set true to add '/1' and '/2' to the end of read names.
spaceslash=f    Set true to add a space before slash read pairnum.
prefix=null     Generated reads will start with this prefix, 
                rather than naming by location.
seed=0          Use this to set the random number generator seed; 
                use -1 for a random seed.

Length Parameters - normally only minlength and maxlength are needed.
minlength=150   Generate reads of up to this length.
maxlength=150   Generate reads of at least this length.
gaussianlength=f  Use a gaussian length distribution (for PacBio).
                  Otherwise, the distribution is linear.
midlength=-1    Gaussian curve peaks at this point.  Must be between
                minlength and maxlength, in Gaussian mode.
readlengthsd=-1 Standard deviation of the Gaussian curve.  Note that the
                final curve is a sum of multiple curves, but this will affect
                overall curve width.  By default this is set to 1/4 of range.

Pairing parameters:
paired=f        Set to true for paired reads.
mininsert=      Controls minimum insert length.  Default depends on read length.
maxinsert=      Controls maximum insert length.  Default depends on read length.
triangle=f      Make a triangular insert size distribution.
flat=f          Make a roughly flat insert size distribution..
superflat=f     Make a perfectly flat insert size distribution.
gaussian=t      Make a bell-shaped insert size distribution, with 
                standard deviation of (maxinsert-mininsert)/6.
samestrand=f    Generate paired reads on the same strand.

Mutation parameters:
snprate=0       Add snps to reads with this probability (0-1).
insrate=0       Add insertions to reads with this probability (0-1).
delrate=0       Add deletions to reads with this probability (0-1).
subrate=0       Add contiguous substitutions to reads with this probability (0-1).
nrate=0         Add nocalls to reads with this probability (0-1).

Note: With a 'rate' of X, each read has an X chance of getting at least 
1 mutation, X^2 chance of 2+ mutations, X^3 chance of 3+ mutations, 
and so forth up to the maximum allowed number of mutations of that type.

maxsnps=3       Add at most this many snps per read.
maxinss=2       Add at most this many deletions per read.
maxdels=2       Add at most this many insertions per read.
maxsubs=2       Add at most this many contiguous substitutions per read.
maxns=0         Add at most this many blocks of Ns per read.

maxinslen=12    Max length of insertions.
maxdellen=400   Max length of deletions.
maxsublen=12    Max length of contiguous substitutions.
maxnlen=1       Min length of N blocks.

mininslen=1     Min length of insertions.
mindellen=1     Min length of deletions.
minsublen=2     Min length of contiguous substitutions.
minnlen=1       Min length of N blocks.

Illumina quality parameters:
maxq=36         Upper bound of quality values.
midq=28         Approximate average of quality values.
minq=20         Lower bound of quality values.
q=              Sets maxq, midq, and minq to the same value.
adderrors=t     Add substitution errors based on quality values, 
                after mutations.
qv=4            Vary the base quality of reads by up to this much
                to simulate tile effects.

PacBio quality parameters:
pacbio=f        Use a PacBio error model, rather than Illumina 
                error model, and add PacBio errors after mutations.
pbmin_file=0.13      Minimum rate of PacBio errors for a read.
pbmax=0.17      Maximum rate of PacBio errors for a read.

Other Parameters:
overlap=1       Require reads to overlap scaffold end by at least this much.
banns=f         Do not generate reads over reference Ns.
metagenome=f    Assign scaffolds a random exponential coverage level,
                to simulate a metagenomic or RNA coverage distribution.
randomscaffold=f    Choose random scaffolds without respect to length.
amp=1           Simulate highly-amplified MDA single-cell data by 
                setting this to a higher number like 1000.
replacenoref=f  Replace intra- and inter-scaffold Ns with random bases.
pbadapter=      Add adapter sequence to some reads using this literal string.
fragadapter=    Add this sequence to paired reads with insert size 
                shorter than read length.
fragadapter2=   Use this sequence for read 2.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding the 
                program's automatic memory detection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 
		200 megs.
                    The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for randomreads.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("randomreads.sh", args, capture_output)

def randomreadsmg(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for randomreadsmg.sh

    Help message:
    Written by Brian Bushnell
Last modified July 15, 2025

Description:  Generates synthetic reads from a set of fasta assemblies.
Each assembly is assigned a random coverage level, with optional custom 
coverage for specific genomes.  Reads headers will contain the TaxID
of the originating genome, if the filename starts with 'tid_x_',
where x is a positive integer.

Usage:  randomreadsmg.sh *.fa out=reads.fq.gz
or
randomreadsmg.sh ecoli.fa=40 mruber.fa=0.1 phix.fa=10 out=reads.fq.gz

File parameters:
in_file=<file,file>  Assembly input.  Can be a single file, a directory of files,
                or comma-delimited list.  Unrecognized arguments with no '='
                sign will also be treated as input files.
out=<file>      Synthetic read output destination.
out2=<file>     Read 2 output if twin files are desired for paired reads.

Processing parameters:
mindepth=1      Minimum assembly average depth.
maxdepth=256    Maximum assembly average depth.
depth=          Sets minimum and maximum to the same level.
reads=-1        If positive, ignore depth and make this many reads per contig.
variance=0.5    Coverage within an assembly will vary by up to this much;
                one region can be up to this fraction deeper than another.
mode=min4       Random depth distribution; can be min4, exp, root, or linear.
cov_x=          Set a custom coverage level for the file named x.
                x can alternatively be the taxID if the filename starts
                with tid_x_; e.g. cov_foo.fa=5 for foo.fa, or cov_7=5
                for file tid_7_foo.fa
<file>=x        Alternate way to set custom depth; file will get depth x.
threads=        Set the max number of threads; default is logical core count.
                By default each input file uses 1 thread.  This flag will
                also force multithreaded processing when there is exactly 1
                input file, increasing speed for a complex simulation.
seed=-1         If positive, use the specified RNG seed.  This will cause
                deterministic output if threads=1.

Artifact parameters
pcr=0.0         Add PCR duplicates at this rate (0-1).
randomkmer=f    Bias read start sites with random kmer priming.
kprime=6        Length for random kmer priming.
kpower=0.5      Raise linear primer distribution to this power (>0).
                Higher powers increase priming bias.
minkprob=0.1    Minimum primer kmer probability.

Platform parameters
illumina        Use Illumina length and error mode (default).
pacbio          Use PacBio length and error mode.
ont             Use ONT length and error mode.
paired=true     Generate paired reads in Illumina mode.
length=150      Read length; default is 150 for Illumina mode.
avginsert=300   Average insert size; only affects paired reads.

Long read parameters
minlen=1000     Minimum read length for PacBio/ONT modes.
meanlen=15000   Mean read length for PacBio/ONT modes.
maxlen=100000   Max read length for PacBio/ONT modes.
tailfactor=0.2  Controls heavy tail for ONT length distribution.
pbsigma=0.5     Log-normal standard deviation for PacBio length distribution.

Error parameters (all platforms)
adderrors=f     Set to true to add model-specific errors.
subrate=0.0     Add substitutions at this rate, independent of platform models.
indelrate=0.0   Add length-1 indels at this rate, independent of platform models.

Illumina-specific parameters
qavg=25         Average quality score, for generating Illumina errors.
qrange=0        Quality score range (+/- this much).
addadapters     Add adapter sequence to paired reads with insert
                size shorter than read length.
adapter1=       Optionally specify a custom R1 adapter (as observed in R1).
adapter2=       Optionally specify a custom R2 adapter (as observed in R2).

Long-read error parameters
Note: These may be overriden for any platform, including Illumina.
srate=-1        Substitution rate; default 0.0025 ONT / 0.00015 PB.
irate=-1        Insertion rate; default 0.0055 ONT / 0.000055 PB.
drate=-1        Deletion rate; default 0.0045 ONT / 0.000045 PB.
hrate=-1        Homopolymer error boost; default 0.02 ONT / 0.000015 PB.
                The indel chance increases this much per homopolymer base.

Coverage variation parameters (only used with 'sinewave' flag):
sinewave        Enable realistic coverage variation within contigs.
numwaves=4      Number of sine waves to combine; more waves create more 
                complex coverage patterns with irregular peaks and valleys.
waveamp=0.70    Controls the maximum variation in coverage due to the sine 
                waves.  Higher values (0-1) create more dramatic differences 
                between high and low coverage regions.
oribias=0.25    Strength of the origin of replication bias. Controls the max
                linear decrease in coverage from start to end of contigs.
minprob=0.10    Sets the minimum coverage probability as a fraction of target.
                Makes it improbable for regions have coverage that drops 
                below this level, preventing assembly gaps.
minperiod=2k    Minimum sine wave period, in bp.
maxperiod=80k   Maximum sine wave period, in bp.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for randomreadsmg.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("randomreadsmg.sh", args, capture_output)

def readlength(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for readlength.sh

    Help message:
    Written by Brian Bushnell
Last modified December 19, 2018
Description:  Generates a length histogram of input reads.

Usage:	readlength.sh in_file=<input file>

in_file=<file>    	The 'in_file=' flag is needed only if the input file is not the first parameter.  'in_file=stdin.fq' will pipe from standard in.
in2=<file>   	Use this if 2nd read of pairs are in a different file.
out=<file>   	Write the histogram to this file.  Default is stdout.
bin_file=10       	Set the histogram bin size.
max=80000    	Set the max read length to track.
round=f      	Places reads in the closest bin, rather than the highest bin of at least readlength.
nzo=t        	(nonzeroonly) Do not print empty bins.
reads=-1     	If nonnegative, stop after this many reads.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for readlength.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("readlength.sh", args, capture_output)

def reducecolumns(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for reducecolumns.sh

    Help message:
    Written by Brian Bushnell
Last modified February 24, 2025

Usage: reducecolumns.sh <in> <out> column column column

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for reducecolumns.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("reducecolumns.sh", args, capture_output)

def reducesilva(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for reducesilva.sh

    Help message:
    Written by Brian Bushnell
Last modified July 31, 2015

Description:  Reduces Silva entries down to one entry per taxa (the first).
This is accomplished by splitting the semicolon-delimited name on semicolons,
and assuming everything is in the form of:
kingdom;phylum;class;order;family;genus;species
...so it's not very reliable.

Usage:  reducesilva.sh in_file=<file> out=<file> column=<1>

Parameters:
column          The taxonomic level.  0=species, 1=genus, etc.
ow=f            (overwrite) Overwrites files that already exist.
zl=4            (ziplevel) Set compression level, 1 (low) to 9 (max).
fastawrap=70    Length of lines in fasta output.

Sampling parameters:
reads=-1        Set to a positive number to only process this many INPUT sequences, then quit.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for reducesilva.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("reducesilva.sh", args, capture_output)

def reformat(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for reformat.sh

    Help message:
    Written by Brian Bushnell
Last modified November 22, 2023

Description:  Reformats reads to change ASCII quality encoding, interleaving, file format, or compression format.
Optionally performs additional functions such as quality trimming, subsetting, and subsampling.
Supports fastq, fasta, fasta+qual, scarf, oneline, sam, bam, gzip, bz2.
Please read bbmap/docs/guides/ReformatGuide.txt for more information.

Usage:  reformat.sh in_file=<file> in2=<file2> out=<outfile> out2=<outfile2>

in2 and out2 are for paired reads and are optional.
If input is paired and there is only one output file, it will be written interleaved.

Parameters and their defaults:

ow=f                    (overwrite) Overwrites files that already exist.
app=f                   (append) Append to files that already exist.
zl=4                    (ziplevel) Set compression level, 1 (low) to 9 (max).
int=f                   (interleaved) Determines whether INPUT file is considered interleaved.
fastawrap=70            Length of lines in fasta output.
fastareadlen=0          Set to a non-zero number to break fasta files into reads of at most this length.
fastaminlen=1           Ignore fasta reads shorter than this.
qin_file=auto                ASCII offset for input quality.  May be 33 (Sanger), 64 (Illumina), or auto.
qout=auto               ASCII offset for output quality.  May be 33 (Sanger), 64 (Illumina), or auto (same as input).
qfake=30                Quality value used for fasta to fastq reformatting.
qfin_file=<.qual file>       Read qualities from this qual file, for the reads coming from 'in_file=<fasta file>'
qfin2=<.qual file>      Read qualities from this qual file, for the reads coming from 'in2=<fasta file>'
qfout=<.qual file>      Write qualities from this qual file, for the reads going to 'out=<fasta file>'
qfout2=<.qual file>     Write qualities from this qual file, for the reads coming from 'out2=<fasta file>'
outsingle=<file>        (outs) If a read is longer than minlength and its mate is shorter, the longer one goes here.
deleteinput=f           Delete input upon successful completion.
ref=<file>              Optional reference fasta for sam processing.

Processing Parameters:

verifypaired=f          (vpair) When true, checks reads to see if the names look paired.  Prints an error message if not.
verifyinterleaved=f     (vint) sets 'vpair' to true and 'interleaved' to true.
allowidenticalnames=f   (ain) When verifying pair names, allows identical names, instead of requiring /1 and /2 or 1: and 2:
tossbrokenreads=f       (tbr) Discard reads that have different numbers of bases and qualities.  By default this will be detected and cause a crash.
ignorebadquality=f      (ibq) Fix out-of-range quality values instead of crashing with a warning.
addslash=f              Append ' /1' and ' /2' to read names, if not already present.  Please include the flag 'int=t' if the reads are interleaved.
spaceslash=t            Put a space before the slash in addslash mode.
addcolon=f              Append ' 1:' and ' 2:' to read names, if not already present.  Please include the flag 'int=t' if the reads are interleaved.
underscore=f            Change whitespace in read names to underscores.
rcomp=f                 (rc) Reverse-complement reads.
rcompmate=f             (rcm) Reverse-complement read 2 only.
comp=f                  (complement) Reverse-complement reads.
changequality=t         (cq) N bases always get a quality of 0 and ACGT bases get a min quality of 2.
quantize=f              Quantize qualities to a subset of values like NextSeq.  Can also be used with comma-delimited list, like quantize=0,8,13,22,27,32,37
tuc=f                   (touppercase) Change lowercase letters in reads to uppercase.
uniquenames=f           Make duplicate names unique by appending _<number>.
remap=                  A set of pairs: remap=CTGN will transform C>T and G>N.
                        Use remap1 and remap2 to specify read 1 or 2.
iupacToN=f              (itn) Convert non-ACGTN symbols to N.
monitor=f               Kill this process if it crashes.  monitor=600,0.01 would kill after 600 seconds under 1% usage.
crashjunk=t             Crash when encountering reads with invalid bases.
tossjunk=f              Discard reads with invalid characters as bases.
fixjunk=f               Convert invalid bases to N (or X for amino acids).
dotdashxton=f           Specifically convert . - and X to N (or X for amino acids).
fixheaders=f            Convert nonstandard header characters to standard ASCII.
recalibrate=f           (recal) Recalibrate quality scores.  Must first generate matrices with CalcTrueQuality.
maxcalledquality=41     Quality scores capped at this upper bound.
mincalledquality=2      Quality scores of ACGT bases will be capped at lower bound.
trimreaddescription=f   (trd) Trim the names of reads after the first whitespace.
trimrname=f             For sam/bam files, trim rname/rnext fields after the first space.
fixheaders=f            Replace characters in headers such as space, *, and | to make them valid file names.
warnifnosequence=t      For fasta, issue a warning if a sequenceless header is encountered.
warnfirsttimeonly=t     Issue a warning for only the first sequenceless header.
utot=f                  Convert U to T (for RNA -> DNA translation).
padleft=0               Pad the left end of sequences with this many symbols.
padright=0              Pad the right end of sequences with this many symbols.
pad=0                   Set padleft and padright to the same value.
padsymbol=N             Symbol to use for padding.

Histogram output parameters:

bhist=<file>            Base composition histogram by position.
qhist=<file>            Quality histogram by position.
qchist=<file>           Count of bases with each quality value.
aqhist=<file>           Histogram of average read quality.
bqhist=<file>           Quality histogram designed for box plots.
lhist=<file>            Read length histogram.
gchist=<file>           Read GC content histogram.
gcbins=100              Number gchist bins.  Set to 'auto' to use read length.
gcplot=f                Add a graphical representation to the gchist.
maxhistlen=6000         Set an upper bound for histogram lengths; higher uses more memory.
                        The default is 6000 for some histograms and 80000 for others.

Histograms for sam files only (requires sam format 1.4 or higher):

ehist=<file>            Errors-per-read histogram.
qahist=<file>           Quality accuracy histogram of error rates versus quality score.
indelhist=<file>        Indel length histogram.
mhist=<file>            Histogram of match, sub, del, and ins rates by read location.
ihist=<file>            Insert size histograms.  Requires paired reads in a sam file.
idhist=<file>           Histogram of read count versus percent identity.
idbins=100              Number idhist bins.  Set to 'auto' to use read length.

Sampling parameters:

reads=-1                Set to a positive number to only process this many INPUT reads (or pairs), then quit.
skipreads=-1            Skip (discard) this many INPUT reads before processing the rest.
samplerate=1            Randomly output only this fraction of reads; 1 means sampling is disabled.
sampleseed=-1           Set to a positive number to use that prng seed for sampling (allowing deterministic sampling).
samplereadstarget=0     (srt) Exact number of OUTPUT reads (or pairs) desired.
samplebasestarget=0     (sbt) Exact number of OUTPUT bases desired.
                        Important: srt/sbt flags should not be used with stdin, samplerate, qtrim, minlength, or minavgquality.
upsample=f              Allow srt/sbt to upsample (duplicate reads) when the target is greater than input.
prioritizelength=f      If true, calculate a length threshold to reach the target, and retain all reads of at least that length (must set srt or sbt).

Trimming and filtering parameters:

qtrim=f                 Trim read ends to remove bases with quality below trimq.
                        Values: t (trim both ends), f (neither end), r (right end only), l (left end only), w (sliding window).
trimq=6                 Regions with average quality BELOW this will be trimmed.  Can be a floating-point number like 7.3.
minlength=0             (ml) Reads shorter than this after trimming will be discarded.  Pairs will be discarded only if both are shorter.
mlf=0                   (mlf) Reads shorter than this fraction of original length after trimming will be discarded.
maxlength=0             If nonzero, reads longer than this after trimming will be discarded.
breaklength=0           If nonzero, reads longer than this will be broken into multiple reads of this length.  Does not work for paired reads.
requirebothbad=t        (rbb) Only discard pairs if both reads are shorter than minlen.
invertfilters=f         (invert) Output failing reads instead of passing reads.
minavgquality=0         (maq) Reads with average quality (after trimming) below this will be discarded.
maqb=0                  If positive, calculate maq from this many initial bases.
chastityfilter=f        (cf) Reads with names  containing ' 1:Y:' or ' 2:Y:' will be discarded.
barcodefilter=f         Remove reads with unexpected barcodes if barcodes is set, or barcodes containing 'N' otherwise.  
                        A barcode must be the last part of the read header.
barcodes=               Comma-delimited list of barcodes or files of barcodes.
maxns=-1                If 0 or greater, reads with more Ns than this (after trimming) will be discarded.
minconsecutivebases=0   (mcb) Discard reads without at least this many consecutive called bases.
forcetrimleft=0         (ftl) If nonzero, trim left bases of the read to this position (exclusive, 0-based).
forcetrimright=-1       (ftr) If nonnegative, trim right bases of the read after this position (exclusive, 0-based).
forcetrimright2=0       (ftr2) If positive, trim this many bases on the right end.
forcetrimmod=5          (ftm) If positive, trim length to be equal to zero modulo this number.
mingc=0                 Discard reads with GC content below this.
maxgc=1                 Discard reads with GC content above this.
gcpairs=t               Use average GC of paired reads.
                        Also affects gchist.

Tag-filtering parameters:

tag=                    Look for this tag in the header to filter by the next value.  To filter reads
                        with a header like 'foo,depth=5.5,bar' where you only want depths
                        of at least 3, the necessary flags would be 'tag=depth= minvalue=3 delimiter=,'
delimiter=              Character after the end of the value, such as delimiter=X.  Control and
                        whitespace symbols may be spelled out, like delimiter=tab or delimiter=pipe.
                        The tag may contain the delimiter.  If the value is the last term in the header,
                        the delimiter doesn't matter but is still required.
minvalue=               If set, only accept a numeric value of at least this.
maxvalue=               If set, only accept a numeric value of at most this.
value=                  If set, only accept a string value of exactly this.

Illumina-specific parameters:
top=true                Include reads from the top of the flowcell.
bottom=true             Include reads from the bottom of the flowcell.

Sam and bam processing options:

mappedonly=f            Toss unmapped reads.
unmappedonly=f          Toss mapped reads.
pairedonly=f            Toss reads that are not mapped as proper pairs.
unpairedonly=f          Toss reads that are mapped as proper pairs.
primaryonly=f           Toss secondary alignments.  Set this to true for sam to fastq conversion.
minmapq=-1              If non-negative, toss reads with mapq under this.
maxmapq=-1              If non-negative, toss reads with mapq over this.
requiredbits=0          (rbits) Toss sam lines with any of these flag bits unset.  Similar to samtools -f.
filterbits=0            (fbits) Toss sam lines with any of these flag bits set.  Similar to samtools -F.
stoptag=f               Set to true to write a tag indicating read stop location, prefixed by YS:i:
sam=                    Set to 'sam=1.3' to convert '=' and 'X' cigar symbols (from sam 1.4+ format) to 'M'.
                        Set to 'sam=1.4' to convert 'M' to '=' and 'X' (sam=1.4 requires MD tags to be present, or ref to be specified).

Sam and bam alignment filtering options:
These require = and X symbols in cigar strings, or MD tags, or a reference fasta.
-1 means disabled; to filter reads with any of a symbol type, set to 0.

subfilter=-1            Discard reads with more than this many substitutions.
minsubs=-1              Discard reads with fewer than this many substitutions.
insfilter=-1            Discard reads with more than this many insertions.
delfilter=-1            Discard reads with more than this many deletions.
indelfilter=-1          Discard reads with more than this many indels.
editfilter=-1           Discard reads with more than this many edits.
inslenfilter=-1         Discard reads with an insertion longer than this.
dellenfilter=-1         Discard reads with a deletion longer than this.
minidfilter=-1.0        Discard reads with identity below this (0-1).
maxidfilter=1.0         Discard reads with identity above this (0-1).
clipfilter=-1           Discard reads with more than this many soft-clipped bases.

Kmer counting and cardinality estimation:
k=0                     If positive, count the total number of kmers.
cardinality=f           (loglog) Count unique kmers using the LogLog algorithm.
loglogbuckets=1999      Use this many buckets for cardinality estimation.

Shortcuts: 
The # symbol will be substituted for 1 and 2.  The % symbol in out will be substituted for input name minus extensions.
For example:
reformat.sh in_file=read#.fq out=%.fa
...is equivalent to:
reformat.sh in1=read1.fq in2=read2.fq out1=read1.fa out2=read2.fa

Java Parameters:
-Xmx                    This will set Java's memory usage, overriding autodetection.
                        -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                        The max is typically 85% of physical memory.
-eoom                   This flag will cause the process to exit if an out-of-memory exception occurs.  Requires Java 8u92+.
-da                     Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for reformat.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("reformat.sh", args, capture_output)

def reformatpb(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for reformatpb.sh

    Help message:
    Written by Brian Bushnell
Last modified June 16, 2020

Description:  Provides some of Reformat's functionality in a ZMW-aware tool.

Usage:  reformatpb.sh in_file=<input file> out=<output file> outb=<bad reads>

File I/O parameters:
in_file=<file>       Primary input.
out=<file>      (outgood) Output for good reads.
outb=<file>     (outbad) Output for discarded reads.
stats=<file>    Print screen output here instead of to the screen.
json=f          Print stats as json.
schist=<file>   Subread count per ZMW histogram.
overwrite=f     (ow) Set to false to force the program to abort rather than
                overwrite an existing file.
ziplevel=2      (zl) Set to 1 (lowest) through 9 (max) to change compression
                level; lower compression is faster.

Processing parameters:
kzt=f           (keepzmwstogether) Send all reads from a ZMW to the same file,
                either good or bad output.
minlen=40       Do not output reads shorter than this, after trimming.
ccsin_file=f         Input reads are CCS, meaning they are all full-pass.
                Not currently used for anything.
trimpolya=f     Trim terminal poly-A and poly-T sequences, for some isoseq
                libraries.
minpolymer=5    Don't trim poly-A sequence shorter than this.
polyerror=0.2   Max error rate for trimming poly-A.
flaglongreads=f    True to flag reads longer than 1.5x median to be discarded.
longreadmult=1.5   Multiplier to consider a read suspiciously long.

Whitelists and Blacklists:
whitelist=      ZMW identifiers, as a comma-delimited list of integers,
                or files with one integer per line.  All ZMWs not in the
                list will be discarded.
blacklist=      All ZMWs in the list will be discarded.

Sampling parameters (avoid using more than one of these at a time):
reads=-1        If positive, quit after processing this many reads.
zmws=-1         If positive, quit after processing this many ZMWs.
bestpass=f      Set to true to keep only the best read per ZMW.  This is
                the median length read of the non-outermost reads.
                If there are 2 or fewer passes, the longest will be chosen.
longestpass=f   Set to true to keep only the longest read per ZMW.
samplerate=1.0  Retain this fraction of input reads.
samplereadstarget=-1  If positive, retain this many reads.
samplebasestarget=-1  If positive, retain this many bases.
samplezmwstarget=-1   If positive, retain this many ZMWs.
subsamplefromends=f   If true, eliminate outermost reads first, then inner.

CCS Parameters (Note: CCS is still experimental)
ccs=f           Make a single consensus read per ZMW (CPU-intensive).
minpasses=0     Discard ZMWs with fewer than this many passes (estimated;
                first and last subread are usually partial).
minsubreads=0   Discard ZMWs with fewer than this many subreads.
reorient=f      Try aligning both strands in case ZMW ordering is broken.
minshredid=0.6  Do not include shreds with identity below this in consensus.

Entropy parameters (recommended setting is 'entropy=t'):
minentropy=-1   Set to 0.4 or above to remove low-entropy reads;
                range is 0-1, recommended value is 0.55.  0.7 is too high.
                Negative numbers disable this function.
entropyk=3      Kmer length for entropy calculation.
entropylen=350  Reads with entropy below cutoff for at least this many
                consecutive bases will be removed.
entropyfraction=0.5     Alternative minimum length for short reads; the shorter
                        of entropylen and entfraction*readlength will be used.
entropywindow=50        Window size used for entropy calculation.
maxmonomerfraction=0.74 (mmf) Also require this fraction of bases in each
                        window to be the same base.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for reformatpb.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("reformatpb.sh", args, capture_output)

def removebadbarcodes(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for removebadbarcodes.sh

    Help message:
    Written by Brian Bushnell.
Last modified March 5, 2018

Description:  Removes reads with barcodes containing non-ACGT bases.
Read headers must be in standard Illumina format.

Usage:  removebadbarcodes.sh in_file=<file> out=<file>

Parameters:
in_file=<file>       Input reads; required parameter.
out=<file>      Destination for good reads; optional.
ziplevel=2      (zl) Compression level for gzip output.
pigz=f          Spawn a pigz (parallel gzip) process for faster 
                compression than Java.  Requires pigz to be installed.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx800m will specify 800 megs.
                    The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for removebadbarcodes.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("removebadbarcodes.sh", args, capture_output)

def removecatdogmousehuman(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for removecatdogmousehuman.sh

    Help message:
    Written by Brian Bushnell
Last modified December 22, 2021
This script requires at least 52GB RAM.
It is designed for NERSC and uses hard-coded paths.

Description:  Removes all reads that map to the cat, dog, mouse, or human genome with at least 95% identity after quality trimming.
Removes approximately 98.6% of human 2x150bp reads, with zero false-positives to non-animals.
NOTE!  This program uses hard-coded paths and will only run on Nersc systems.

Usage:  removecatdogmousehuman.sh in_file=<input file> outu=<clean output file>

Input may be fasta or fastq, compressed or uncompressed.

Parameters:
threads=auto        (t) Set number of threads to use; default is number of logical processors.
overwrite=t         (ow) Set to false to force the program to abort rather than overwrite an existing file.
interleaved=auto    (int) If true, forces fastq input to be paired and interleaved.
trim=t              Trim read ends to remove bases with quality below minq.
                    Values: t (trim both ends), f (neither end), r (right end only), l (left end only).
untrim=t            Undo the trimming after mapping.
minq=4              Trim quality threshold.
ziplevel=2          (zl) Set to 1 (lowest) through 9 (max) to change compression level; lower compression is faster.
outm=<file>         File to output the reads that mapped to human.

***** All BBMap parameters can be used; run bbmap.sh for more details. *****

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for removecatdogmousehuman.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("removecatdogmousehuman.sh", args, capture_output)

def removehuman(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for removehuman.sh

    Help message:
    Written by Brian Bushnell
Last modified December 22, 2021
This script requires at least 16GB RAM.
It is designed for NERSC and uses hard-coded paths.

Description:  Removes all reads that map to the human genome with at least 95% identity after quality trimming.
Removes approximately 98.6% of human 2x150bp reads, with zero false-positives to non-animals.
NOTE!  This program uses hard-coded paths and will only run on Nersc systems unless you change the path.

Usage:  removehuman.sh in_file=<input file> outu=<clean output file>

Input may be fasta or fastq, compressed or uncompressed.

Parameters:
threads=auto        (t) Set number of threads to use; default is number of logical processors.
overwrite=t         (ow) Set to false to force the program to abort rather than overwrite an existing file.
interleaved=auto    (int) If true, forces fastq input to be paired and interleaved.
trim=t              Trim read ends to remove bases with quality below minq.
                    Values: t (trim both ends), f (neither end), r (right end only), l (left end only).
untrim=t            Undo the trimming after mapping.
minq=4              Trim quality threshold.
ziplevel=2          (zl) Set to 1 (lowest) through 9 (max) to change compression level; lower compression is faster.
outm=<file>         File to output the reads that mapped to human.
path=               Set the path to an indexed human genome.

***** All BBMap parameters can be used; run bbmap.sh for more details. *****

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for removehuman.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("removehuman.sh", args, capture_output)

def removehuman2(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for removehuman2.sh

    Help message:
    Written by Brian Bushnell
Last modified December 22, 2021
This script requires at least 17GB RAM.
It is designed for NERSC and uses hard-coded paths.

Description:  Removes all reads that map to the human genome with at least 88% identity after quality trimming.
This is more aggressive than removehuman.sh and uses an unmasked human genome reference.
It removes roughly 99.99% of human 2x150bp reads, but may incur false-positive removals.
NOTE!  This program uses hard-coded paths and will only run on Nersc systems unless you change the path.

Usage:  removehuman.sh in_file=<input file> outu=<clean output file>

Input may be fasta or fastq, compressed or uncompressed.

Parameters:
threads=auto        (t) Set number of threads to use; default is number of logical processors.
overwrite=t         (ow) Set to false to force the program to abort rather than overwrite an existing file.
interleaved=auto    (int) If true, forces fastq input to be paired and interleaved.
trim=t              Trim read ends to remove bases with quality below minq.
                    Values: t (trim both ends), f (neither end), r (right end only), l (left end only).
untrim=t            Undo the trimming after mapping.
minq=4              Trim quality threshold.
ziplevel=2          (zl) Set to 1 (lowest) through 9 (max) to change compression level; lower compression is faster.
outm=<file>         File to output the reads that mapped to human.
path=               Set the path to an indexed human genome.

***** All BBMap parameters can be used; run bbmap.sh for more details. *****

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for removehuman2.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("removehuman2.sh", args, capture_output)

def removemicrobes(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for removemicrobes.sh

    Help message:
    Written by Brian Bushnell
Last modified December 22, 2021
This script requires at least 10GB RAM.
It is designed for NERSC and uses hard-coded paths.

Description:  Removes all reads that map to selected common microbial contaminant genomes.
Removes approximately 98.5% of common contaminant reads, with zero false-positives to non-bacteria.
NOTE!  This program uses hard-coded paths and will only run on Nersc systems.

Usage:  removemicrobes.sh in_file=<input file> outu=<clean output file>

Input may be fasta or fastq, compressed or uncompressed.

Parameters:
in_file=<file>           Input reads.  Should already be adapter-trimmed.
outu=<file>         Destination for clean reads.
outm=<file>         Optional destination for contaminant reads.
threads=auto        (t) Set number of threads to use; default is number of logical processors.
overwrite=t         (ow) Set to false to force the program to abort rather than overwrite an existing file.
interleaved=auto    (int) If true, forces fastq input to be paired and interleaved.
trim=t              Trim read ends to remove bases with quality below minq.
                    Values: t (trim both ends), f (neither end), r (right end only), l (left end only).
untrim=t            Undo the trimming after mapping.
minq=4              Trim quality threshold.
ziplevel=6          (zl) Set to 1 (lowest) through 9 (max) to change compression level; lower compression is faster.

build=1             Choses which masking mode was used:  
                    1 is most stringent and should be used for bacteria.
                    2 uses fewer bacteria for masking (only RefSeq references).
                    3 is only masked for plastids and entropy, for use on anything except bacteria.
                    4 is unmasked.

***** All BBMap parameters can be used; run bbmap.sh for more details. *****

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for removemicrobes.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("removemicrobes.sh", args, capture_output)

def removesmartbell(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for removesmartbell.sh

    Help message:
    Written by Brian Bushnell
Last modified May 2, 2017

Description:  Remove Smart Bell adapters from PacBio reads.

Usage:        removesmartbell in_file=<input> out=<output> split=t

Input may be fasta or fastq, compressed or uncompressed (not H5 files).

Parameters:
in_file=file         Specify the input file, or stdin.
out=file        Specify the output file, or stdout.
adapter=        Specify the adapter sequence (default is normal SmrtBell).
split=t            t: Splits reads at adapters.
                   f: Masks adapters with X symbols.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for removesmartbell.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("removesmartbell.sh", args, capture_output)

def rename(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for rename.sh

    Help message:
    Written by Brian Bushnell
Last modified September 25, 2024

Description:  Renames reads to <prefix>_<number> where you specify the prefix
and the numbers are ordered.  There are other renaming modes too.
If reads are paired, pairs should be processed together; if reads are 
interleaved, the interleaved flag should be set.  This ensures that if a
read number (such as 1: or 2:) is added, it will be added correctly.

Usage:  rename.sh in_file=<file> in2=<file2> out=<outfile> out2=<outfile2> prefix=<>

in2 and out2 are for paired reads and are optional.
If input is paired and there is only one output file, it will be written interleaved.

Parameters:
prefix=             The string to prepend to existing read names.
suffix=             If a suffix is supplied, it will be appended to the existing read name, after a tab.
ow=f                (overwrite) Overwrites files that already exist.
zl=4                (ziplevel) Set compression level, 1 (low) to 9 (max).
int=f               (interleaved) Determines whether INPUT file is considered interleaved.
fastawrap=70        Length of lines in fasta output.
minscaf=1           Ignore fasta reads shorter than this.
qin_file=auto            ASCII offset for input quality.  May be 33 (Sanger), 64 (Illumina), or auto.
qout=auto           ASCII offset for output quality.  May be 33 (Sanger), 64 (Illumina), or auto (same as input).
ignorebadquality=f  (ibq) Fix out-of-range quality values instead of crashing with a warning.

Renaming modes (if not default):
renamebyinsert=f    Rename the read to indicate its correct insert size.
renamebymapping=f   Rename the read to indicate its correct mapping coordinates.
renamebytrim=f      Rename the read to indicate its correct post-trimming length.
renamebycoords=f    Rename Illumina headers to leave coordinates but remove redundant info.
addprefix=f         Rename the read by prepending the prefix to the existing name.
prefixonly=f        Only use the prefix; don't add _<number>
addunderscore=t     Add an underscore after the prefix (if there is a prefix).
addpairnum=t        Add a pairnum (e.g. ' 1:') to paired reads in some modes.
fixsra=f            Fixes headers of SRA reads renamed from Illumina.
                    Specifically, it converts something like this:
                    SRR17611.11 HWI-ST79:17:D091UACXX:4:1101:210:824 length=75
                    ...into this:
                    HWI-ST79:17:D091UACXX:4:1101:210:824 1:

Trimming:
trimleft=0          Trim this many characters from the header start.
trimright=0         Trim this many characters from the header end.
trimbeforesymbol=0  Trim this many characters before the last instance of
                    a specified symbol.
symbol=             Trim before this symbol.  This can be a literal like ':'
                    or a word like tab or lessthan for reserved symbols.

Other parameters:
reads=-1            Set to a positive number to only process this many INPUT reads (or pairs), then quit.
quantize=           Set this to reduce compressed file size by binning quality.
                    E.g., quantize=2 will eliminate odd qscores.

Java Parameters:
-Xmx                This will set Java's memory usage, overriding autodetection.
                    -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom               This flag will cause the process to exit if an
                    out-of-memory exception occurs.  Requires Java 8u92+.
-da                 Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for rename.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("rename.sh", args, capture_output)

def renamebymapping(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for renamebymapping.sh

    Help message:
    Written by Brian Bushnell
Last modified February 21, 2025

Description:  Renames contigs based on mapping information.
Appends coverage and optionally taxID from parsing sam line headers.
For taxID renaming, read headers should contain a term like 'tid_1234';
output will be named as 'original tid_1234 cov_45.67' with potentially
multiple coverage entries (if there are multiple sam files) but
only one tid entry based on the highest-coverage sam file.
Designed for metagenome binning evaluation and synthetic read generation.

Usage:  renamebymapping.sh in_file=contigs.fa out=renamed.fa *.sam

Parameters:
in_file=<file>        Assembly to rename.
out=<file>       Renamed assembly.
sam=<file>       This can be a file, directory, or comma-delimited list.
                 Unrecognized arguments that are existing files will also
                 be treated as sam files.  Bam is acceptable too.
delimiter=space  Delimiter between appended fields.
wipe=f           Replace the original header with contig_#.
depth=t          Add a depth field.
tid=t            Add a tid field (if not already present).

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for renamebymapping.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("renamebymapping.sh", args, capture_output)

def renamebysketch(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for renamebysketch.sh

    Help message:
    Written by Brian Bushnell
Last modified January 9, 2025

Description:  Renames fasta files with a TaxID, based on SendSketch results.
Designed for metagenome binning evaluation and synthetic read generation.

Usage:  renamebysketch.sh *.fa

Input may be fasta or fastq, compressed or uncompressed.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for renamebysketch.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("renamebysketch.sh", args, capture_output)

def renameimg(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for renameimg.sh

    Help message:
    Written by Brian Bushnell
Last modified August 23, 2017

Description:  Renames img records to be prefixed by their id.
This is for internal JGI use and has no external utility.

Usage:  renameimg.sh in_file=auto out=renamed.fa.gz

Parameters:
in_file=         3-column tsv with imgID, taxID, and file path.
            These files will have their sequences renamed and concatenated.
img=        Optional, if a different (presumably bigger) file will be used for taxonomic assignment.
            For example, in could be a subset of img, potentially with incorrect taxIDs.

Java Parameters:
-Xmx        This will set Java's memory usage, overriding autodetection.
            -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom       This flag will cause the process to exit if an out-of-memory exception occurs.  Requires Java 8u92+.
-da         Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for renameimg.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("renameimg.sh", args, capture_output)

def renameref(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for renameref.sh

    Help message:
    Written by Isla and Brian Bushnell
Last modified July 15, 2025

Description:  Converts reference sequence names in genomics files,
supporting SAM, BAM, FASTA, VCF, and GFF.  Updates reference names in headers
and data records according to a mapping file.  Useful for converting between
reference naming conventions (e.g. HG19 <-> GRCh37).
Sequence names not in the mapping file are kept as-is.  Name mapping will
first be attempted using the full header, and secondly using the prefix
of the original name up to the first whitespace.

Usage:
renameref.sh in_file=<input file> out=<output file> mapping=<ref_mapping.tsv>

Examples:
renameref.sh in_file=aligned.sam out=converted.sam mapping=hg19_to_grch37.tsv
renameref.sh in_file=data.sam out=renamed.sam mapping=refs.tsv strict=true

Parameters:
in_file=<file>       Input file to process
out=<file>      Output file with converted reference names  
map=<file>      Tab-delimited file with old_name<tab>new_name mappings
invert=<bool>   Reverse the order of names in the map file.
strict=<bool>   Crash on unknown references (default: false)
verbose=<bool>  Print detailed progress information (default: false)

Mapping file format:
chr1	1
chr2	2
chrX	X
chrM	MT

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for renameref.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("renameref.sh", args, capture_output)

def repair(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for repair.sh

    Help message:
    Written by Brian Bushnell
Last modified November 9, 2016

Description:  Re-pairs reads that became disordered or had some mates eliminated.
Please read bbmap/docs/guides/RepairGuide.txt for more information.

Usage:  repair.sh in_file=<input file> out=<pair output> outs=<singleton output>

Input may be fasta, fastq, or sam, compressed or uncompressed.

Parameters:
in_file=<file>       The 'in_file=' flag is needed if the input file is not the first 
                parameter.  'in_file=stdin' will pipe from standard in.
in2=<file>      Use this if 2nd read of pairs are in a different file.
out=<file>      The 'out=' flag is needed if the output file is not the second
                parameter.  'out=stdout' will pipe to standard out.
out2=<file>     Use this to write 2nd read of pairs to a different file.
outs=<file>     (outsingle) Write singleton reads here.
overwrite=t     (ow) Set to false to force the program to abort rather than
                overwrite an existing file.
showspeed=t     (ss) Set to 'f' to suppress display of processing speed.
ziplevel=2      (zl) Set to 1 (lowest) through 9 (max) to change compression
                level; lower compression is faster.
fint=f          (fixinterleaving) Fixes corrupted interleaved files using read
                names.  Only use on files with broken interleaving - correctly
                interleaved files from which some reads were removed.
repair=t        (rp) Fixes arbitrarily corrupted paired reads by using read 
                names.  Uses much more memory than 'fint' mode.
ain_file=f           (allowidenticalnames) When detecting pair names, allows 
                identical names, instead of requiring /1 and /2 or 1: and 2:

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for repair.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("repair.sh", args, capture_output)

def replaceheaders(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for replaceheaders.sh

    Help message:
    Written by Brian Bushnell
Last modified May 23, 2016

Description:  Replaces read names with names from another file.
The other file can either be sequences or simply names, with
one name per line (and no > or @ symbols).  If you use one name
per line, please give the file a .header extension.

Usage:  replaceheaders.sh in_file=<file> hin_file=<headers file> out=<out file>

Parameters:
in_file=                 Input sequences.  Use in2 for a second paired file.
in_file=                 Header input sequences.  Use hin2 for a second paired file.
out=                Output sequences.  Use out2 for a second paired file.
ow=f                (overwrite) Overwrites files that already exist.
zl=4                (ziplevel) Set compression level, 1 (low) to 9 (max).
int=f               (interleaved) Determines whether INPUT file is considered interleaved.
fastawrap=70        Length of lines in fasta output.
qin_file=auto            ASCII offset for input quality.  May be 33 (Sanger), 64 (Illumina), or auto.
qout=auto           ASCII offset for output quality.  May be 33 (Sanger), 64 (Illumina), or auto (same as input).

Renaming modes (if not default):
addprefix=f         Rename the read by prepending the new name to the existing name.

Sampling parameters:
reads=-1            Set to a positive number to only process this many INPUT reads (or pairs), then quit.

Java Parameters:
-Xmx                This will set Java's memory usage, overriding autodetection.
                    -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom               This flag will cause the process to exit if an
                    out-of-memory exception occurs.  Requires Java 8u92+.
-da                 Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for replaceheaders.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("replaceheaders.sh", args, capture_output)

def representative(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for representative.sh

    Help message:
    Written by Brian Bushnell
Last modified September 4, 2019

Description:  Makes a representative set of taxa from all-to-all identity
comparison.  Input should be in 3+ column TSV format (first 3 are required):
(query, ref, ANI, qsize, rsize, qbases, rbases)
...as produced by CompareSketch with format=3 and usetaxidname.
Additional columns are allowed and will be ignored.

Usage:  representative.sh in_file=<input file> out=<output file>

Parameters:
overwrite=f     (ow) Set to false to force the program to abort rather than
                overwrite an existing file.
threshold=0     Ignore edges under threshold value.  This also affects the
                choice of centroids; a high threshold gives more weight to 
                higher-value edges.
minratio=0      Ignores edges with a ratio below this value.
invertratio=f   Invert the ratio when greater than 1.
printheader=t   Print a header line in the output.
printsize=t     Print the size of retained nodes.
printclusters=t Print the nodes subsumed by each retained node.
minsize=0       Ignore nodes under this size (in unique kmers).
maxsize=0       If positive, ignore nodes over this size (unique kmers).
minbases=0      Ignore nodes under this size (in total bases).
maxbases=0      If positive, ignore nodes over this size (total bases).

Taxonomy parameters:
level=          Taxonomic level, such as phylum.  Filtering will operate on
                sequences within the same taxonomic level as specified ids.
                If not set, only matches to a node or its descendants will 
                be considered.
ids=            Comma-delimited list of NCBI numeric IDs.  Can also be a
                file with one taxID per line.
names=          Alternately, a list of names (such as 'Homo sapiens').
                Note that spaces need special handling.
include=f       'f' will discard filtered sequences, 't' will keep them.
tree=<file>     Specify a TaxTree file like tree.taxtree.gz.  
                On Genepool, use 'auto'.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will
                specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                The max is typically around 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for representative.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("representative.sh", args, capture_output)

def rqcfilter2(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for rqcfilter2.sh

    Help message:
    Written by Brian Bushnell
Last modified September 20, 2024

Description:  RQCFilter2 is a revised version of RQCFilter that uses a common path for all dependencies.
The dependencies are available at http://portal.nersc.gov/dna/microbial/assembly/bushnell/RQCFilterData.tar

Performs quality-trimming, artifact removal, linker-trimming, adapter trimming, and spike-in removal using BBDuk.
Performs human/cat/dog/mouse/microbe removal using BBMap.
It requires 40 GB RAM for mousecatdoghuman, but only 1GB or so without them.

Usage:  rqcfilter2.sh in_file=<input file> path=<output directory> rqcfilterdata=<path to RQCFilterData directory>

Primary I/O parameters:
in_file=<file>           Input reads.
in2=<file>          Use this if 2nd read of pairs are in a different file.
path=null           Set to the directory to use for all output files.

Reference file paths:
rqcfilterdata=      Path to unzipped RQCFilterData directory.  Default is /global/projectb/sandbox/gaag/bbtools/RQCFilterData
ref=<file,file>     Comma-delimited list of additional reference files for filtering via BBDuk.

Output parameters:
scafstats=scaffoldStats.txt  Scaffold stats file name (how many reads matched which reference scaffold) .
kmerstats=kmerStats.txt      Kmer stats file name (duk-like output).
log=status.log               Progress log file name.
filelist=file-list.txt       List of output files.
stats=filterStats.txt        Overall stats file name.
stats2=filterStats2.txt      Better overall stats file name.
ihist=ihist_merge.txt        Insert size histogram name.  Set to null to skip merging.
outribo=ribo.fq.gz           Output for ribosomal reads, if removeribo=t.
reproduceName=reproduce.sh   Name of shellscript to reproduce these results.
usetmpdir=t                  Write temp files to TMPDIR.
tmpdir=                      Override TMPDIR.

Adapter trimming parameters:
trimhdist=1         Hamming distance used for trimming.
trimhdist2=         Hamming distance used for trimming with short kmers.  If unset, trimhdist will be used.
trimk=23            Kmer length for trimming stage.
mink=11             Minimum kmer length for short kmers when trimming.
trimfragadapter=t   Trim all known Illumina adapter sequences, including TruSeq and Nextera.
trimrnaadapter=f    Trim Illumina TruSeq-RNA adapters.
bisulfite=f         Currently, this trims the last 1bp from all reads after the adapter-trimming phase.
findadapters=t      For paired-end files, attempt to discover the adapter sequence with BBMerge and use that rather than a set of known adapters.
swift=f             Trim Swift sequences: Trailing C/T/N R1, leading G/A/N R2.

Quality trimming parameters:
qtrim=f             Trim read ends to remove bases with quality below minq.  Performed AFTER looking for kmers.
                    Values: rl (trim both ends), f (neither end), r (right end only), l (left end only).
trimq=10            Trim quality threshold.  Must also set qtrim for direction.
minlength=45        (ml) Reads shorter than this after trimming will be discarded.  Pairs will be discarded only if both are shorter.
mlf=0.333           (minlengthfraction) Reads shorter than this fraction of original length after trimming will be discarded.
minavgquality=5     (maq) Reads with average quality (before trimming) below this will be discarded.
maxns=0             Reads with more Ns than this will be discarded.
forcetrimmod=5      (ftm) If positive, right-trim length to be equal to zero, modulo this number.
forcetrimleft=-1    (ftl) If positive, trim bases to the left of this position
                    (exclusive, 0-based).
forcetrimright=-1   (ftr) If positive, trim bases to the right of this position
                    (exclusive, 0-based).
forcetrimright2=-1  (ftr2) If positive, trim this many bases on the right end.

Mapping parameters (for vertebrate contaminants):
mapk=14             Kmer length for mapping stage (9-15; longer is faster).
removehuman=f       (human) Remove human reads via mapping.
keephuman=f         Keep reads that map to human (or cat, dog, mouse) rather than removing them.
removedog=f         (dog) Remove dog reads via mapping.
removecat=f         (cat) Remove cat reads via mapping.
removemouse=f       (mouse) Remove mouse reads via mapping.
aggressivehuman=f   Aggressively remove human reads (and cat/dog/mouse) using unmasked references.
aggressivemicrobe=f Aggressively microbial contaminant reads using unmasked references.
aggressive=f        Set both aggressivehuman and aggressivemicrobe at once.
mapref=             Remove contaminants by mapping to this fasta file (or comma-delimited list).

Bloom filter parameters (for vertebrate mapping):
bloom=t             Use a Bloom filter to accelerate mapping.
bloomminreads=4m   Disable Bloom filter if there are fewer than this many reads.
bloomk=29           Kmer length for Bloom filter
bloomhashes=1       Number of hashes for the Bloom filter.
bloomminhits=6      Minimum consecutive hits to consider a read as matching.
bloomserial=t       Use the serialized Bloom filter for greater loading speed.
                    This will use the default Bloom filter parameters.

Microbial contaminant removal parameters:
detectmicrobes=f    Detect common microbes, but don't remove them.  Use this OR removemicrobes, not both.
removemicrobes=f    (microbes) Remove common contaminant microbial reads via mapping, and place them in a separate file.
taxlist=            (tax) Remove these taxa from the database before filtering.  Typically, this would be the organism name or NCBI ID, or a comma-delimited list.  Organism names should have underscores instead of spaces, such as Escherichia_coli.
taxlevel=order      (level) Level to remove.  For example, 'phylum' would remove everything in the same phylum as entries in the taxlist.
taxtree=auto        (tree) Override location of the TaxTree file.
gitable=auto        Override location of the gitable file.
loadgitable=f       Controls whether gi numbers may be used for taxonomy.
microberef=         Path to fasta file of microbes.
microbebuild=1      Chooses which masking was used.  1 is most stringent and should be used for bacteria.  Eukaryotes should use 3.

Extended microbial contaminant parameters:
detectmicrobes2=f   (detectothermicrobes) Detect an extended set of microbes that are currently being screened.  This can be used in conjunction with removemicrobes.

Filtering parameters (for artificial and genomic contaminants):
skipfilter=f        Skip this phase.  Not recommended.
filterpolya=f       Remove reads containing poly-A sequence (for RNA-seq).
filterpolyg=0       Remove reads that start with a G polymer at least this long (0 disables).
trimpolyg=6         Trim reads that start or end with a G polymer at least this long (0 disables).
phix=t              Remove reads containing phiX kmers.
lambda=f            Remove reads containing Lambda phage kmers.
pjet=t              Remove reads containing PJET kmers.
sip=f               Remove SIP spikeins.
maskmiddle=t        (mm) Treat the middle base of a kmer as a wildcard, to increase sensitivity in the presence of errors.
maxbadkmers=0       (mbk) Reads with more than this many contaminant kmers will be discarded.
filterhdist=1       Hamming distance used for filtering.
filterqhdist=1      Query hamming distance used for filtering.
copyundefined=f     (cu) Match all possible bases for sequences containing degerate IUPAC symbols.
entropy=f           Remove low-complexity reads.  The threshold can be specified by e.g entropy=0.4; default is 0.42 if enabled.
entropyk=2          Kmer length to use for entropy calculation.
entropywindow=40    Window size to use for entropy calculation.

Spikein removal/quantification parameters:
mtst=f              Remove mtst.
kapa=t              Remove and quantify kapa.
spikeink=31         Kmer length for spikein removal.
spikeinhdist=0      Hamming distance for spikein removal.
spikeinref=         Additional references for spikein removal (comma-delimited list).

Ribosomal filtering parameters:
ribohdist=1         Hamming distance used for rRNA removal.
riboedist=0         Edit distance used for rRNA removal.
removeribo=f        (ribo) Remove ribosomal reads via kmer-matching, and place them in a separate file.

Organelle filtering parameters:
chloromap=f         Remove chloroplast reads by mapping to this organism's chloroplast.
mitomap=f           Remove mitochondrial reads by mapping to this organism's mitochondria.
ribomap=f           Remove ribosomal reads by mapping to this organism's ribosomes.
NOTE: organism TaxID should be specified in taxlist, and taxlevel should be set to genus or species.

FilterByTile parameters:
filterbytile=t      Run FilterByTile to remove reads from low-quality parts of the flowcell.
tiledump=           Set this to the tiledump of the full lane (recommended).

Recalibration parameters:
recalibrate=t       Recalibrate quality scores based on PhiX alignment.
phixsam=            Set this to the aligned PhiX data for the lane (required).
quantize=2          Quantize the quality scores to reduce file size, using this divisor.
                    2 reduces size by roughly 25%.  Disabled if recalibrate=f.
                    Quantization happens AFTER all the quality-related steps.

Polyfilter parameters:
polyfilter=GC       Remove reads with homopolymers of these subunits.
                    Set polyfilter=null to disable.

Clumpify parameters:
clumpify=f          Run clumpify; all deduplication flags require this.
dedupe=f            Remove duplicate reads; all deduplication flags require this.
opticaldupes=f      Remove optical duplicates (Clumpify optical flag).
edgedupes=f         Remove tile-edge duplicates (Clumpify spany and adjacent flags).
dpasses=1           Use this many deduplication passes.
dsubs=2             Allow this many substitutions between duplicates.
ddist=40            Remove optical/edge duplicates within this distance.
lowcomplexity=f     Set to true for low-complexity libraries such as RNA-seq to improve estimation of memory requirements.
clumpifytmpdir=f    Use TMPDIR for clumpify temp files.
clumpifygroups=-1   If positive, force Clumpify to use this many groups.
*** For NextSeq, the recommended deduplication flags are: clumpify dedupe edgedupes
*** For NovaSeq, the recommended deduplication flags are: clumpify dedupe opticaldupes ddist=12000
*** For HiSeq, the recommended deduplication flags are: clumpify dedupe opticaldupes

Sketch parameters:
sketch=t            Run SendSketch on 2M read pairs.
silvalocal=t        Use the local flag for Silva (requires running RQCFilter on NERSC).
sketchreads=1m      Number of read pairs to sketch.
sketchsamplerate=1  Samplerate for SendSketch.
sketchminprob=0.2   Minprob for SendSketch.
sketchdb=nt,refseq,silva  Servers to use for SendSketch.

Other processing parameters:
threads=auto        (t) Set number of threads to use; default is number of logical processors.
library=frag        Set to 'frag', 'clip', 'lfpe', or 'clrs'.
filterk=31          Kmer length for filtering stage.
rcomp=t             Look for reverse-complements of kmers in addition to forward kmers.
nexteralmp=f        Split into different files based on Nextera LMP junction sequence.  Only for Nextera LMP, not normal Nextera.
extend=f            Extend reads during merging to allow insert size estimation of non-overlapping reads.
pigz=t              Use pigz for compression.
unpigz=t            Use pigz for decompression.
khist=f             Set to true to generate a kmer-frequency histogram of the output data.
merge=t             Set to false to skip generation of insert size histogram.

Header-specific parameters:  (NOTE - Be sure to disable these if the reads have improper headers, like SRA data.)
chastityfilter=t    Remove reads failing chastity filter.
barcodefilter=f     Crash when improper barcodes are discovered.  Set to 'f' to disable,
                    't' to remove improper barcodes, or 'crash' to crash if they are discovered.
barcodes=           A comma-delimited list of barcodes or files of barcodes.

Java Parameters:
-Xmx                This will set Java's memory usage, overriding autodetection.
                    -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom               This flag will cause the process to exit if an
                    out-of-memory exception occurs.  Requires Java 8u92+.
-da                 Disable assertions.

*****   All additional parameters supported by BBDuk may also be used, and will be passed directly to BBDuk   *****

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for rqcfilter2.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("rqcfilter2.sh", args, capture_output)

def runhmm(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for runhmm.sh

    Help message:
    Written by Brian Bushnell
Last modified August 5, 2020

Description:  Processes data.  (WIP)

Usage:  runhmm.sh in_file=<file> out=<file>

Parameters and their defaults:

ow=f                    (overwrite) Overwrites files that already exist.

Processing Parameters:

None yet!


Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for runhmm.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("runhmm.sh", args, capture_output)

def samtoroc(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for samtoroc.sh

    Help message:
    Written by Brian Bushnell
Last modified January 20, 2017

Description:  Creates a ROC curve from a sam file of synthetic reads with headers generated by RandomReads3.java

Usage:  samtoroc.sh in_file=<sam file> reads=<number of reads in input fastq>

Parameters:
in_file=<file>       Specify the input sam file, or stdin.
thresh=20       Max deviation from correct location to be considered 'loosely correct'.
blasr=f         Set to 't' for BLASR output; fixes extra information added to read names.
ssaha2=f        Set to 't' for SSAHA2 or SMALT output; fixes incorrect soft-clipped read locations.
bitset=t        Track read ID's to detect secondary alignments.
                Necessary for mappers that incorrectly output multiple primary alignments per read.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for samtoroc.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("samtoroc.sh", args, capture_output)

def scoresequence(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for scoresequence.sh

    Help message:
    Written by Brian Bushnell
Last modified Oct 11, 2023

Description:  Scores sequences using a neural network.  Only the initial Xbp
are used, for sequences longer than the network size.

Usage:  scoresequence.sh in_file=<sequences> out=<renamed sequences> net=<net file>

Input may be fasta or fastq, compressed or uncompressed.

Standard parameters:
in_file=<file>       Sequence data.
out=<file>      Sequences renamed with their scores.
net=<file>      Network file to apply to the sequences.
hist=<file>     Histogram of scores (x100, so 0-1 maps to 0-100).
overwrite=f     (ow) Set to false to force the program to abort rather than
                overwrite an existing file.

Processing parameters:
rcomp=f         Use the max score of a sequence and its reverse complement.
parse=f         Parse sequence headers for 'result=' to determine whether
                they are positive or negative examples.
annotate=t      Rename output reads by appending 'score='.
filter=f        Retain only reads above or below a cutoff.  Setting the cutoff
                or highpass flag will automatically set this to true.
cutoff=0.5      Score cutoff for filtering; scores mostly range from 0 to 1.
highpass=t      Retain sequences ABOVE cutoff if true, else BELOW cutoff.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for scoresequence.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("scoresequence.sh", args, capture_output)

def seal(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for seal.sh

    Help message:
    Written by Brian Bushnell
Last modified November 12, 2024

Description:  Performs high-speed alignment-free sequence quantification,
by counting the number of long kmers that match between a read and
a set of reference sequences.  Designed for RNA-seq with alternative splicing.
Please read bbmap/docs/guides/SealGuide.txt for more information.

Usage Examples (not comprehensive):

Sequence quantification:
seal.sh in_file=<file> ref=<file> rpkm=rpkm.txt stats=stats.txt
or
seal.sh in_file=<file> ref=<file,file,file...> refstats=refstats.txt

Splitting:
seal.sh in_file=<file> ref=<file,file,file...> pattern=out_%.fq outu=unmapped.fq
or
seal.sh in_file=<file> *.fasta pattern=out_%.fq outu=unmapped.fq

Input may be fasta or fastq, compressed or uncompressed.
If you pipe via stdin/stdout, please include the file type; e.g. for gzipped 
fasta input, set in_file=stdin.fa.gz


Input parameters:
in_file=<file>           Main input. in_file=stdin.fq will pipe from stdin.
in2=<file>          Input for 2nd read of pairs in a different file.
ref=<file,file>     Comma-delimited list of reference files or directories.
                    Filenames may also be used without ref=, e.g. *.fa.
                    In addition to filenames, you may also use the keywords:
                    adapters, artifacts, phix, lambda, pjet, mtst, kapa.
literal=<seq,seq>   Comma-delimited list of literal reference sequences.
touppercase=f       (tuc) Change all bases upper-case.
interleaved=auto    (int) t/f overrides interleaved autodetection.
                    Must be set mainually when streaming fastq input.
qin_file=auto            Input quality offset: 33 (Sanger), 64, or auto.
reads=-1            If positive, quit after processing X reads or pairs.
copyundefined=f     (cu) Process non-AGCT IUPAC reference bases by making all
                    possible unambiguous copies.  Intended for short motifs
                    or adapter barcodes, as time/memory use is exponential.

Output parameters:
out=<file>          (outmatch) Write reads here that contain kmers matching
                    the reference. 'out=stdout.fq' will pipe to standard out.
out2=<file>         (outmatch2) Use this to write 2nd read of pairs to a 
                    different file.
outu=<file>         (outunmatched) Write reads here that do not contain kmers 
                    matching the database.
outu2=<file>        (outunmatched2) Use this to write 2nd read of pairs to a 
                    different file.
pattern=<file>      Use this to write reads to one stream per ref sequence
                    match, replacing the % character with the sequence name.
                    For example, pattern=%.fq for ref sequences named dog and 
                    cat would create dog.fq and cat.fq.
stats=<file>        Write statistics about which contamininants were detected.
refstats=<file>     Write statistics on a per-reference-file basis.
rpkm=<file>         Write RPKM for each reference sequence (for RNA-seq).
dump=<file>         Dump kmer tables to a file, in fasta format.
nzo=t               Only write statistics about ref sequences with nonzero hits.
overwrite=t         (ow) Grant permission to overwrite files.
showspeed=t         (ss) 'f' suppresses display of processing speed.
ziplevel=2          (zl) Compression level; 1 (min) through 9 (max).
fastawrap=80        Length of lines in fasta output.
qout=auto           Output quality offset: 33 (Sanger), 64, or auto.
statscolumns=5      (cols) Number of columns for stats output, 3 or 5.
                    5 includes base counts.
rename=f            Append matched reference sequence names to read headers.
addcount=t          If renaming, include the ref hit counts.
tophitonly=f        If renaming, only add the top hit.
refnames=f          Use names of reference files rather than scaffold IDs.
                    With multiple reference files, this is more efficient
                    than tracking statistics on a per-sequence basis.
trd=f               Truncate read and ref names at the first whitespace.
ordered=f           Set to true to output reads in same order as input.
kpt=t               (keepPairsTogether) Paired reads will always be assigned
                    to the same ref sequence.

Processing parameters:
k=31                Kmer length used for finding contaminants.  Contaminants 
                    shorter than k will not be found.  k must be at least 1.
rcomp=t             Look for reverse-complements of kmers in addition to 
                    forward kmers.
maskmiddle=t        (mm) Treat the middle base of a kmer as a wildcard, to 
                    increase sensitivity in the presence of errors.  This may
                    also be set to a number, e.g. mm=3, to mask that many bp.
                    The default mm=t corresponds to mm=1 for odd-length kmers
                    and mm=2 for even-length kmers (as of v39.04), while
                    mm=f is always equivalent to mm=0.
minkmerhits=1       (mkh) A read needs at least this many kmer hits to be 
                    considered a match.
minkmerfraction=0.0 (mkf) A reads needs at least this fraction of its total
                    kmers to hit a ref, in order to be considered a match.
hammingdistance=0   (hdist) Maximum Hamming distance for ref kmers (subs only).
                    Memory use is proportional to (3*K)^hdist.
qhdist=0            Hamming distance for query kmers; impacts speed, not memory.
editdistance=0      (edist) Maximum edit distance from ref kmers (subs and 
                    indels).  Memory use is proportional to (8*K)^edist.
forbidn=f           (fn) Forbids matching of read kmers containing N.  
                    By default, these will match a reference 'A' if hdist>0
                    or edist>0, to increase sensitivity.
match=all           Determines when to quit looking for kmer matches.  Values:
                         all:    Attempt to match all kmers in each read.
                         first:  Quit after the first matching kmer.
                         unique: Quit after the first uniquely matching kmer.
ambiguous=random    (ambig) Set behavior on ambiguously-mapped reads (with an
                    equal number of kmer matches to multiple sequences).
                         first:  Use the first best-matching sequence.
                         toss:   Consider unmapped.
                         random: Select one best-matching sequence randomly.
                         all:    Use all best-matching sequences.
genesets=f          Assign ambiguously-mapping reads to a newly created gene
                    set that they share for stats/rpkm output.  May be slow.
clearzone=0         (cz) Threshhold for ambiguity.  If the best match shares X 
                    kmers with the read, the read will be considered
                    also ambiguously mapped to any sequence sharing at least
                    [X minus clearzone] kmers.
czf=0.0             (clearzonefraction) If positive, the actual clearzone used
                    for a read with N total kmers will be max(cz, czf*N).
ecco=f              For overlapping paired reads only.  Performs error-
                    correction with BBMerge prior to kmer operations.

Containment parameters:
processcontainedref=f  Require a reference sequence to be fully contained by
                    an input sequence
storerefbases=f     Store reference bases so that ref containments can be
                    validated.  If this is set to false and processcontainedref
                    is true, then it will only require that the read share the
                    same number of bases as are present in the ref sequence.

Taxonomy parameters (only use when doing taxonomy):
tax=<file>          Output destination for taxonomy information.
taxtree=<file>      (tree) A serialized TaxTree (tree.taxtree.gz).
gi=<file>           A serialized GiTable (gitable.int1d.gz). Only needed if 
                    reference sequence names start with 'gi|'.
mincount=1          Only display taxa with at least this many hits.
maxnodes=-1         If positive, display at most this many top hits.
minlevel=subspecies Do not display nodes below this taxonomic level.
maxlevel=life       Do not display nodes above this taxonomic level.
Valid levels are subspecies, species, genus, family, order, class,
phylum, kingdom, domain, life

Speed and Memory parameters:
threads=auto        (t) Set number of threads to use; default is number of 
                    logical processors.
prealloc=f          Preallocate memory in table.  Allows faster table loading 
                    and more efficient memory usage, for a large reference.
monitor=f           Kill this process if CPU usage drops to zero for a long
                    time.  monitor=600,0.01 would kill after 600 seconds 
                    under 1% usage.
rskip=1             Skip reference kmers to reduce memory usage.
                    1 means use all, 2 means use every other kmer, etc.
qskip=1             Skip query kmers to increase speed.  1 means use all.
speed=0             Ignore this fraction of kmer space (0-15 out of 16) in both
                    reads and reference.  Increases speed and reduces memory.
Note: Do not use more than one of 'speed', 'qskip', and 'rskip'.

Trimming/Masking parameters:
qtrim=f             Trim read ends to remove bases with quality below trimq.
                    Performed AFTER looking for kmers.  Values: 
                         t (trim both ends), 
                         f (neither end), 
                         r (right end only), 
                         l (left end only).
trimq=6             Regions with average quality BELOW this will be trimmed.
minlength=1         (ml) Reads shorter than this after trimming will be 
                    discarded.  Pairs will be discarded only if both are shorter.
maxlength=          Reads longer than this after trimming will be discarded.
                    Pairs will be discarded only if both are longer.
minavgquality=0     (maq) Reads with average quality (after trimming) below 
                    this will be discarded.
maqb=0              If positive, calculate maq from this many initial bases.
maxns=-1            If non-negative, reads with more Ns than this 
                    (after trimming) will be discarded.
forcetrimleft=0     (ftl) If positive, trim bases to the left of this position 
                    (exclusive, 0-based).
forcetrimright=0    (ftr) If positive, trim bases to the right of this position 
                    (exclusive, 0-based).
forcetrimright2=0   (ftr2) If positive, trim this many bases on the right end. 
forcetrimmod=0      (ftm) If positive, right-trim length to be equal to zero,
                    modulo this number.
restrictleft=0      If positive, only look for kmer matches in the 
                    leftmost X bases.
restrictright=0     If positive, only look for kmer matches in the 
                    rightmost X bases.

Java Parameters:
-Xmx                This will set Java's memory usage, overriding autodetection.
                    -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.  
                    The max is typically 85% of physical memory.
-eoom               This flag will cause the process to exit if an 
                    out-of-memory exception occurs.  Requires Java 8u92+.
-da                 Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for seal.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("seal.sh", args, capture_output)

def sendsketch(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for sendsketch.sh

    Help message:
    Written by Brian Bushnell
Last modified October 10, 2024

Description:  Compares query sketches to reference sketches hosted on a 
remote server via the Internet.  The input can be sketches made by sketch.sh,
or fasta/fastq files from which SendSketch will generate sketches.  
Only sketches will sent, not sequences.

Please read bbmap/docs/guides/BBSketchGuide.txt for more information.

Usage:  
sendsketch.sh in_file=file

To change nucleotide servers, add the server name, e.g.:
sendsketch.sh in_file=file nt

For the protein server with nucleotide input:
sendsketch.sh in_file=file protein

for the protein server with amino input:
sendsketch.sh in_file=file amino protein


Standard parameters:
in_file=<file>       Sketch or fasta file to compare.
out=stdout      Comparison output.  Can be set to a file instead.
outsketch=      Optional, to write the sketch to a file.
local=f         For local files, have the server load the sketches.
                Allows use of whitelists; recommended for Silva.
                Local can only be used when the client and server access 
                the same filesystem - e.g., Genepool and Cori.
address=        Address of remote server.  Default address:
                https://refseq-sketch.jgi.doe.gov/sketch
                You can also specify these abbreviations:
                   nt:      nt server
                   refseq:  Refseq server
                   silva:   Silva server
                   protein: RefSeq prokaryotic amino acid sketches
                   img:     IMG server (Not Yet Available)
                   mito:    RefSeq mitochondrial server (NYA)
                   fungi:   RefSeq fungi sketches (NYA)
                Using an abbreviation automatically sets the address, 
                the blacklist, and k.
aws=f           Set aws=t to use the aws servers instead of NERSC.
                When, for example, NERSC (or the whole SF Bay area) is down.

Sketch-making parameters:
mode=single     Possible modes, for fasta input:
                   single: Generate one sketch per file.
                   sequence: Generate one sketch per sequence.
k=31            Kmer length, 1-32.  This is automatic and does not need to
                be set for JGI servers, only for locally-hosted servers.
samplerate=1    Set to a lower value to sample a fraction of input reads.
                For raw reads (rather than an assembly), 1-3x coverage
                gives best results, by reducing error kmers.  Somewhat
                higher is better for high-error-rate data like PacBio.
minkeycount=1   Ignore kmers that occur fewer times than this.  Values
                over 1 can be used with raw reads to avoid error kmers.
minprob=0.0001  Ignore kmers below this probability of correctness.
minqual=0       Ignore kmers spanning bases below this quality.
entropy=0.66    Ignore sequence with entropy below this value.
merge=f         Merge paired reads prior to sketching.
amino=f         Use amino acid mode.  Input should be amino acids.
translate=f     Call genes and translate to proteins.  Input should be
                nucleotides.  Designed for prokaryotes.
sixframes=f     Translate all 6 frames instead of predicting genes.
ssu=t           Scan for and retain full-length SSU sequence.
printssusequence=f  Print the query SSU sequence (JSON mode only).
refid=          Instead of a query file, specify a reference sketch by name
                or taxid; e.g. refid=h.sapiens or refid=9606.

Size parameters:
size=10000      Desired size of sketches (if not using autosize).
mgf=0.01        (maxfraction) Max fraction of genomic kmers to use.
minsize=100     Do not generate sketches for genomes smaller than this.
autosize=t      Use flexible sizing instead of fixed-length.  This is
                nonlinear; a human sketch is only ~6x a bacterial sketch.
sizemult=1      Multiply the autosized size of sketches by this factor.
                Normally a bacterial-size genome will get a sketch size
                of around 10000; if autosizefactor=2, it would be ~20000.
density=        If this flag is set (to a number between 0 and 1),
                autosize and sizemult are ignored, and this fraction of
                genomic kmers are used.  For example, at density=0.001,
                a 4.5Mbp bacteria will get a 4500-kmer sketch.
sketchheapfactor=4  If minkeycount>1, temporarily track this many kmers until
                counts are known and low-count kmers are discarded.

Taxonomy and filtering parameters:
level=2         Only report the best record per taxa at this level.
                Either level names or numbers may be used.
                    0: disabled
                    1: subspecies
                    2: species
                    3: genus
                   ...etc
include=        Restrict output to organisms in these clades.
                May be a comma-delimited list of names or NCBI TaxIDs.
includelevel=0  Promote the include list to this taxonomic level.
                For example, include=h.sapiens includelevel=phylum
                would only include organisms in the same phylum as human.
includestring=  Only report records whose name contains this string.
exclude=        Ignore organisms in these clades.
                May be a comma-delimited list of names or NCBI TaxIDs.
excludelevel=0  Promote the exclude list to this taxonomic level.
                For example, exclude=h.sapiens excludelevel=phylum
                would exclude all organisms in the same phylum as human.
excludestring=  Do not records whose name contains this string.
banunclassified=f   Ignore organisms descending from nodes like 
                    'unclassified Bacteria'
banvirus=f      Ignore viruses.
requiressu=f    Ignore records without SSUs.
minrefsize=0    Ignore ref sketches smaller than this (unique kmers).
minrefsizebases=0   Ignore ref sketches smaller than this (total base pairs).

Output format:
format=2        2: Default format with, per query, one query header line;
                   one column header line; and one reference line per hit.
                3: One line per hit, with columns query, reference, ANI,
                   and sizeRatio.
                4: JSON (format=json also works).
                5: Constellation (format=constellation also works).
usetaxidname=f  For format 3, print the taxID in the name column.
usetaxname      for format 3, print the taxonomic name in the name column.
useimgname      For format 3, print the img ID in the name column.
d3=f            Output in JSON format, with a tree for visualization.

Output columns (for format=2):
printall=f      Enable all output columns.
printani=t      (ani) Print average nucleotide identity estimate.
completeness=t  Genome completeness estimate.
score=f         Score (used for sorting the output).
printmatches=t  Number of kmer matches to reference.
printlength=f   Number of kmers compared.
printtaxid=t    NCBI taxID.
printimg=f      IMG identifier (only for IMG data).
printgbases=f   Number of genomic bases.
printgkmers=f   Number of genomic kmers.
printgsize=t    Estimated number of unique genomic kmers.
printgseqs=t    Number of sequences (scaffolds/reads).
printtaxname=t  Name associated with this taxID.
printname0=f    (pn0) Original seqeuence name.
printqfname=t   Query filename.
printrfname=f   Reference filename.
printtaxa=f     Full taxonomy of each record.
printcontam=t   Print contamination estimate, and factor contaminant kmers
                into calculations.  Kmers are considered contaminant if
                present in some ref sketch but not the current one.
printunique=t   Number of matches unique to this reference.
printunique2=f  Number of matches unique to this reference's taxa.
printunique3=f  Number of query kmers unique to this reference's taxa,
                regardless of whether they are in this reference sketch.
printnohit=f    Number of kmers that don't hit anything.
printrefhits=f  Average number of ref sketches hit by shared kmers.
printgc=f       GC content.
printucontam=f  Contam hits that hit exactly one reference sketch.
printcontam2=f  Print contamination estimate using only kmer hits
                to unrelated taxa.
contamlevel=species Taxonomic level to use for contam2/unique2/unique3.
NOTE: unique2/unique3/contam2/refhits require an index.

printdepth=f    (depth) Print average depth of sketch kmers; intended
                for shotgun read input.
printdepth2=f   (depth2) Print depth compensating for genomic repeats.
                Requires reference sketches to be generated with depth.
actualdepth=t   If this is false, the raw average count is printed.
                If true, the raw average (observed depth) is converted 
                to estimated actual depth (including uncovered areas).
printvolume=f   (volume) Product of average depth and matches.
printca=f       Print common ancestor, if query taxID is known.
printcal=f      Print common ancestor tax level, if query taxID is known.
recordsperlevel=0   If query TaxID is known, and this is positive, print at
                    most this many records per common ancestor level.

Sorting:
sortbyscore=t   Default sort order is by score.
sortbydepth=f   Include depth as a factor in sort order.
sortbydepth2=f  Include depth2 as a factor in sort order.
sortbyvolume=f  Include volume as a factor in sort order.
sortbykid=f     Sort strictly by KID.
sortbyani=f     Sort strictly by ANI/AAI/WKID.
sortbyhits=f    Sort strictly by the number of kmer hits.

Other output parameters:
minhits=3       (hits) Only report records with at least this many hits.
minani=0        (ani) Only report records with at least this ANI (0-1).
minwkid=0.0001  (wkid) Only report records with at least this WKID (0-1).
anifromwkid=t   Calculate ani from wkid.  If false, use kid.
minbases=0      Ignore ref sketches of sequences shortert than this.
minsizeratio=0  Don't compare sketches if the smaller genome is less than
                this fraction of the size of the larger.
records=20      Report at most this many best-matching records.
color=family    Color records at the family level.  color=f will disable.
                Colors work in most terminals but may cause odd characters
                to appear in text editors.  So, color defaults to f if 
                writing to a file.
intersect=f     Print sketch intersections.  delta=f is suggested.

Metadata parameters (optional, for the query sketch header):
taxid=-1        Set the NCBI taxid.
imgid=-1        Set the IMG id.
spid=-1         Set the sequencing project id (JGI-specific).
name=           Set the name (taxname).
name0=          Set name0 (normally the first sequence header).
fname=          Set fname (normally the file name).
meta_=          Set an arbitrary metadata field.
                For example, meta_Month=March.

Other parameters:
requiredmeta=   (rmeta) Required optional metadata values.  For example:
                rmeta=subunit:ssu,source:silva
bannedmeta=     (bmeta) Forbidden optional metadata values.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

For more detailed information, please read /bbmap/docs/guides/BBSketchGuide.txt.
Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for sendsketch.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("sendsketch.sh", args, capture_output)

def seqtovec(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for seqtovec.sh

    Help message:
    Written by Brian Bushnell
Last modified January 29, 2024

Description:  Generates vectors from sequence.
These can be one-hot 4-bit vectors, or kmer frequency spectra.

Usage:  sectovec.sh in_file=<sequence data> out=<text vectors>

Input may be fasta or fastq, compressed or uncompressed.

Standard parameters:
in_file=<file>       Sequence data.
out=<file>      Vectors in tsv form, with the last column as the result.
overwrite=f     (ow) Set to false to force the program to abort rather than
                overwrite an existing file.

Processing parameters:
parse=f         Set to true to parse the result from individual sequence 
                headers, from a tab-delimited 'result=X' term.
result=-1       Set the desired result for all vectors.

Raw mode parameters:
width=55        Maximum vector width, in bases; the actual vector size will be
                4+4*width+1 (where the +1 is the desired output).  For
                longer sequences, only the first 'width' bases will be used;
                shorter sequences will be zero-padded.
rcomp=f         If true, also output vectors for the reverse-complement.

Spectrum mode parameters:
k=0             If k is positive, generate vectors of kmer frequencies instead
                of raw sequence. Range is 1-8; recommended range is 4-6.
dimensions=0    If positive, restrict the vector size in spectrum mode to
                dimensions+5.  The first 4 and last 1 columns are reserved.


Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for seqtovec.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("seqtovec.sh", args, capture_output)

def shred(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for shred.sh

    Help message:
    Written by Brian Bushnell
Last modified May 4, 2025
Description:  Shreds sequences into shorter, possibly overlapping sequences.

Usage: shred.sh in_file=<file> out=<file> length=<int>

in_file=<file>       Input sequences.
out=<file>      Destination of output shreds.
length=500      Desired length of shreds if a uniform length is desired.
minlen=-1       Shortest allowed shred.  The last shred of each input sequence
                may be shorter than desired length if this is not set.
maxlen=-1       Longest shred length.  If minlength and maxlength are both
                set, shreds will use a random flat length distribution.
median=-1       Alternatively, setting median and variance will override
                minlen and maxlen.
variance=-1
linear          When maxlen is greater than minlen, the distribution can
                be linear, exp, or log (pick one as a flag).
overlap=0       Amount of overlap between successive shreds.
reads=-1        If nonnegative, stop after this many input sequences.
equal=f         Shred each sequence into subsequences of equal size of at most
                'length', instead of a fixed size.
qfake=30        Quality score, if using fastq output.
filetid=f       Name shreds with a tid parsed from the filename (e.g. tid_5).
headertid=f     Name shreds with a tid parsed from sequence headers.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for shred.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("shred.sh", args, capture_output)

def shrinkaccession(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for shrinkaccession.sh

    Help message:
    Written by Brian Bushnell
Last modified July 29, 2019

Description:  Shrinks accession2taxid tables by removing unneeded columns.
This is not necessary but makes accession2taxid files smaller and load faster.

Usage:  shrinkaccession.sh in_file=<file> out=<outfile>

Parameters:
ow=f            (overwrite) Overwrites files that already exist.
app=f           (append) Append to files that already exist.
zl=4            (ziplevel) Set compression level, 1 (low) to 9 (max).
pigz=t          Use pigz for compression, if available.
gi=t            Retain gi numbers.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for shrinkaccession.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("shrinkaccession.sh", args, capture_output)

def shuffle(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for shuffle.sh

    Help message:
    Written by Brian Bushnell
Last modified November 9, 2016

Description:  Reorders reads randomly, keeping pairs together.

Usage:  shuffle.sh in_file=<file> out=<file>

Standard parameters:
in_file=<file>       The 'in_file=' flag is needed if the input file is not the first parameter.  'in_file=stdin' will pipe from standard in.
in2=<file>      Use this if 2nd read of pairs are in a different file.
out=<file>      The 'out=' flag is needed if the output file is not the second parameter.  'out=stdout' will pipe to standard out.
out2=<file>     Use this to write 2nd read of pairs to a different file.
overwrite=t     (ow) Set to false to force the program to abort rather than overwrite an existing file.
ziplevel=2      (zl) Set to 1 (lowest) through 9 (max) to change compression level; lower compression is faster.
int=auto        (interleaved) Set to t or f to override interleaving autodetection.

Processing parameters:
shuffle         Randomly reorders reads (default).
name            Sort reads by name.
coordinate      Sort reads by mapping location.
sequence        Sort reads by sequence.


Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for shuffle.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("shuffle.sh", args, capture_output)

def shuffle2(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for shuffle2.sh

    Help message:
    Written by Brian Bushnell
Last modified August 11, 2021

Description:  Reorders reads randomly, keeping pairs together.
Unlike Shuffle, Shuffle2 can write temp files to handle large datasets.

Usage:  shuffle2.sh in_file=<file> out=<file>

Standard parameters:
in_file=<file>       The 'in_file=' flag is needed if the input file is not the first parameter.  'in_file=stdin' will pipe from standard in.
in2=<file>      Use this if 2nd read of pairs are in a different file.
out=<file>      The 'out=' flag is needed if the output file is not the second parameter.  'out=stdout' will pipe to standard out.
out2=<file>     Use this to write 2nd read of pairs to a different file.
overwrite=t     (ow) Set to false to force the program to abort rather than overwrite an existing file.
ziplevel=2      (zl) Set to 1 (lowest) through 9 (max) to change compression level; lower compression is faster.
int=auto        (interleaved) Set to t or f to override interleaving autodetection.

Processing parameters:
shuffle         Randomly reorders reads (default).
seed=-1         Set to a positive number for deterministic shuffling.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for shuffle2.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("shuffle2.sh", args, capture_output)

def sketch(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for sketch.sh

    Help message:
    Written by Brian Bushnell
Last modified January 28, 2020

Description:  Creates one or more sketches from a fasta file,
optionally annotated with taxonomic information.

Please read bbmap/docs/guides/BBSketchGuide.txt for more information.

Usage:  sketch.sh in_file=<fasta file> out=<sketch file>

Standard parameters:
in_file=<file>           A fasta file containing one or more sequences.
out=<file>          Output filename.  If multiple files are desired it must
                    contain the # symbol.
blacklist=<file>    Ignore keys in this sketch file.  Additionaly, there are
                    built-in blacklists that can be specified:
                       nt:      Blacklist for nt
                       refseq:  Blacklist for Refseq
                       silva:   Blacklist for Silva
                       img:     Blacklist for IMG
files=1             Number of output sketch files to produce, for parallel 
                    loading.  Independent of the number of sketches produced; 
                    sketches will be randomly distributed between files.
k=32,24             Kmer length, 1-32.  To maximize sensitivity and 
                    specificity, dual kmer lengths may be used, e.g. k=32,24
                    Query and reference k must match.
rcomp=t             Look at reverse-complement kmers also.
amino=f             Use amino acid mode.  Input should be amino acids.
translate=f         Call genes and translate to proteins.  Input should be
                    nucleotides.  Designed for prokaryotes.
mode=single         Possible modes:
                       single: Write one sketch.
                       sequence: Write one sketch per sequence.
                       taxa: Write one sketch per taxonomic unit.
                          Requires more memory, and taxonomic annotation.
                       img: Write one sketch per IMG id.
delta=t             Delta-compress sketches.
a48=t               Encode sketches as ASCII-48 rather than hex.
depth=f             Track the number of times kmers appear.
                    Required for the depth2 field in comparisons.
entropy=0.66        Ignore sequence with entropy below this value.
ssu=t               Scan for and retain full-length SSU sequence.

Size parameters:
size=10000          Desired size of sketches (if not using autosize).
maxfraction=0.01    (mgf) Max fraction of genomic kmers to use.
minsize=100         Do not generate sketches for genomes smaller than this.
autosize=t          Use flexible sizing instead of fixed-length.  This is
                    nonlinear; a human sketch is only ~6x a bacterial sketch.
sizemult=1          Multiply the autosized size of sketches by this factor.
                    Normally a bacterial-size genome will get a sketch size
                    of around 10000; if autosizefactor=2, it would be ~20000.
density=            If this flag is set (to a number between 0 and 1),
                    autosize and sizemult are ignored, and this fraction of
                    genomic kmers are used.  For example, at density=0.001,
                    a 4.5Mbp bacteria will get a 4500-kmer sketch.

Metadata flags (optional; intended for single-sketch mode):
taxid=-1            Set the NCBI taxid.
imgid=-1            Set the IMG id.
spid=-1             Set the JGI sequencing project id.
name=               Set the name (taxname).
name0=              Set name0 (normally the first sequence header).
fname=              Set fname (normally the file name).
meta_=              Set an arbitrary metadata field.
                    For example, meta_Month=March.

Taxonomy-specific flags:
tree=               Specify a taxtree file.  On Genepool, use 'auto'.
gi=                 Specify a gitable file.  On Genepool, use 'auto'.
accession=          Specify one or more comma-delimited NCBI accession to
                    taxid files.  On Genepool, use 'auto'.
imgdump=            Specify an IMG dump file containing NCBI taxIDs,
                    for IMG mode.
taxlevel=subspecies Taxa hits below this rank will be promoted and merged
                    with others.
prefilter=f         For huge datasets full of junk like nt, this flag
                    will save memory by ignoring taxa smaller than minsize.
                    Requires taxonomic information (tree and gi).
tossjunk=t          For taxa mode, discard taxonomically uninformative
                    sequences.  This includes sequences with no taxid,
                    with a tax level NO_RANK, of parent taxid of LIFE.
silva=f             Parse headers using Silva or semicolon-delimited syntax.

Ribosomal flags, which allow SSU sequences to be attached to sketches:
processSSU=t        Run gene-calling to detect ribosomal SSU sequences.
16Sfile=<file>      Optional file of 16S sequences, annotated with TaxIDs.
18Sfile=<file>      Optional file of 18S sequences, annotated with TaxIDs.
preferSSUMap=f      Prefer file SSUs over called SSUs.
preferSSUMapEuks=t  Prefer file SSUs over called SSUs for Eukaryotes.
SSUMapOnly=f        Only use file SSUs.
SSUMapOnlyEuks=f    Only use file SSUs for Eukaryotes.  This prevents
                    associating an organism with its mitochondrial or
                    chloroplast 16S/18S, which is otherwise a problem.


Java Parameters:
-Xmx                This will set Java's memory usage, overriding autodetection.
                    -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom               This flag will cause the process to exit if an
                    out-of-memory exception occurs.  Requires Java 8u92+.
-da                 Disable assertions.

For more detailed information, please read /bbmap/docs/guides/BBSketchGuide.txt.
Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for sketch.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("sketch.sh", args, capture_output)

def sketchblacklist(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for sketchblacklist.sh

    Help message:
    Written by Brian Bushnell
Last modified November 7, 2019

Description:  Creates a blacklist sketch from common kmers, 
which occur in at least X different sequences or taxa.
Please read bbmap/docs/guides/BBSketchGuide.txt for more information.

Usage:  sketchblacklist.sh in_file=<fasta file> out=<sketch file>

Standard parameters:
in_file=<file>           A fasta file containing one or more sequences.
out=<file>          Output filename.
mintaxcount=100     Sketch kmers occuring in at least this many taxa.
k=31                Kmer length, 1-32.  To maximize sensitivity and 
                    specificity, dual kmer lengths may be used:  k=31,24
mode=sequence       Possible modes:
                       sequence: Count kmers once per sequence.
                       taxa: Count kmers once per taxonomic unit.
name=               Set the blacklist sketch name.
delta=t             Delta-compress sketches.
a48=t               Encode sketches as ASCII-48 rather than hex.
amino=f             Amino-acid mode.
entropy=0.66        Ignore sequence with entropy below this value.
keyfraction=0.16    Smaller values reduce blacklist size by ignoring a
                    a fraction of the key space.  Range: 0.0001-0.5.

Taxonomy-specific flags:
tree=               Specify a taxtree file.  On Genepool, use 'auto'.
gi=                 Specify a gitable file.  On Genepool, use 'auto'.
accession=          Specify one or more comma-delimited NCBI accession to
                    taxid files.  On Genepool, use 'auto'.
taxlevel=subspecies Taxa hits below this rank will be promoted and merged
                    with others.
prefilter=t         Use a bloom filter to ignore low-count kmers.
prepasses=2         Number of prefilter passes.
prehashes=2         Number of prefilter hashes.
prebits=-1          Manually override number of prefilter cell bits.
tossjunk=t          For taxa mode, discard taxonomically uninformative
                    sequences.  This includes sequences with no taxid,
                    with a tax level NO_RANK, of parent taxid of LIFE.
silva=f             Parse headers using Silva or semicolon-delimited syntax.

Java Parameters:
-Xmx                This will set Java's memory usage, overriding autodetection.
                    -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom               This flag will cause the process to exit if an
                    out-of-memory exception occurs.  Requires Java 8u92+.
-da                 Disable assertions.

For more detailed information, please read /bbmap/docs/guides/BBSketchGuide.txt.
Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for sketchblacklist.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("sketchblacklist.sh", args, capture_output)

def sketchblacklist2(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for sketchblacklist2.sh

    Help message:
    Written by Brian Bushnell
Last modified November 12, 2019

Description:  Creates a blacklist sketch from common kmers, 
which occur in at least X different sketches or taxa.
BlacklistMaker2 makes blacklists from sketches rather than sequences.
It is advisable to make the input sketches larger than normal,
e.g. sizemult=2, because new kmers will be introduced in the final
sketches to replace the blacklisted kmers.

Usage:  sketchblacklist.sh ref=<sketch files> out=<sketch file>
or      sketchblacklist.sh *.sketch out=<sketch file>
or      sketchblacklist.sh ref=taxa#.sketch out=<sketch file>

Standard parameters:
ref=<file>          Sketch files.
out=<file>          Output filename.
mintaxcount=20      Retain keys occuring in at least this many taxa.
length=300000       Retain at most this many keys (prioritizing high count).
k=32,24             Kmer lengths, 1-32.
mode=taxa           Possible modes:
                       sequence: Count kmers once per sketch.
                       taxa: Count kmers once per taxonomic unit.
name=               Set the blacklist sketch name.
delta=t             Delta-compress sketches.
a48=t               Encode sketches as ASCII-48 rather than hex.
amino=f             Amino-acid mode.

Taxonomy-specific flags:
tree=               Specify a taxtree file.  On Genepool, use 'auto'.
gi=                 Specify a gitable file.  On Genepool, use 'auto'.
accession=          Specify one or more comma-delimited NCBI accession to
                    taxid files.  On Genepool, use 'auto'.
taxlevel=subspecies Taxa hits below this rank will be promoted and merged
                    with others.
tossjunk=t          For taxa mode, discard taxonomically uninformative
                    sequences.  This includes sequences with no taxid,
                    with a tax level NO_RANK, of parent taxid of LIFE.

Java Parameters:
-Xmx                This will set Java's memory usage, overriding autodetection.
                    -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom               This flag will cause the process to exit if an
                    out-of-memory exception occurs.  Requires Java 8u92+.
-da                 Disable assertions.

For more detailed information, please read /bbmap/docs/guides/BBSketchGuide.txt.
Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for sketchblacklist2.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("sketchblacklist2.sh", args, capture_output)

def sortbyname(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for sortbyname.sh

    Help message:
    Written by Brian Bushnell
Last modified October 6, 2022

Description:  Sorts reads by name or other keys such as length,
quality, mapping position, flowcell coordinates, or taxonomy.
Writes temp files if memory is exceeded.

Usage:   sortbyname.sh in_file=<file> out=<file>

Input may be fasta, fastq, or sam, compressed or uncompressed.
Temp files will use the same format as the output.  Pairs are
kept together if reads are paired, and in2/out2 may be used for that.

Example 1 - sort by name:
sortbyname.sh in_file=raw.fq out=sorted.fq
Example 2 - sort by sequence:
sortbyname.sh in_file=raw.fq out=sorted.fq sequence
Example 3 - sort by mapping position:
sortbyname.sh in_file=mapped.sam out=sorted.sam position

Parameters:

in_file=<file>       Input file.
out=<file>      Output file.
name=t          Sort reads by name.
length=f        Sort reads by length.
quality=f       Sort reads by quality.
position=f      Sort reads by position (for mapped reads).
taxa=f          Sort reads by taxonomy (for NCBI naming convention).
sequence=f      Sort reads by sequence, alphabetically.
clump=f         Sort reads by shared kmers, like Clumpify.
flowcell=f      Sort reads by flowcell coordinates.
shuffle=f       Shuffle reads randomly (untested).
list=<file>     Sort reads according to this list of names.
ascending=t     Sort ascending.

Memory parameters (you might reduce these if you experience a crash)
memmult=0.30    Write a temp file when used memory exceeds this fraction
                of available memory.
memlimit=0.65   Wait for temp files to finish writing until used memory
                drops below this fraction of available memory.
delete=t        Delete temporary files.
allowtemp=t     Allow writing temporary files.

Taxonomy-sorting parameters (for taxa mode only):
tree=           Specify a taxtree file.  On Genepool, use 'auto'.
gi=             Specify a gitable file.  On Genepool, use 'auto'.
accession=      Specify one or more comma-delimited NCBI accession to
                taxid files.  On Genepool, use 'auto'.

Note: name, length, and quality are mutually exclusive.
Sorting by quality actually sorts by average expected error rate,
so ascending will place the highest-quality reads first.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding
                autodetection.  -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an 
                out-of-memory exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for sortbyname.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("sortbyname.sh", args, capture_output)

def splitbytaxa(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for splitbytaxa.sh

    Help message:
    Written by Brian Bushnell
Last modified Jan 7, 2020

Description:   Splits sequences according to their taxonomy,
as determined by the sequence name.  Sequences should
be labeled with a gi number, NCBI taxID, or species name.

Usage:  splitbytaxa.sh in_file=<input file> out=<output pattern> tree=<tree file> table=<table file> level=<name or number>

Input may be fasta or fastq, compressed or uncompressed.


Standard parameters:
in_file=<file>       Primary input.
out=<file>      Output pattern; must contain % symbol.
overwrite=f     (ow) Set to false to force the program to abort rather than
                overwrite an existing file.
showspeed=t     (ss) Set to 'f' to suppress display of processing speed.
ziplevel=2      (zl) Set to 1 (lowest) through 9 (max) to change compression
                level; lower compression is faster.

Processing parameters:
level=phylum    Taxonomic level, such as phylum.  Filtering will operate on
                sequences within the same taxonomic level as specified ids.
tree=           A taxonomic tree made by TaxTree, such as tree.taxtree.gz.
table=          A table translating gi numbers to NCBI taxIDs.
                Only needed if gi numbers will be used.
                On Genepool, use 'tree=auto table=auto'.
* Note *
Tree and table files are in /global/projectb/sandbox/gaag/bbtools/tax
For non-Genepool users, or to make new ones, use taxtree.sh and gitable.sh

Java Parameters:
-Xmx            This will set Java's memory usage, overriding automatic
                memory detection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify
                200 megs.  The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for splitbytaxa.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("splitbytaxa.sh", args, capture_output)

def splitnextera(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for splitnextera.sh

    Help message:
    Written by Brian Bushnell
Last modified March 6, 2015

Description:  Splits Nextera LMP libraries into subsets based on linker orientation:
LMP, fragment, unknown, and singleton.
Please read bbmap/docs/guides/SplitNexteraGuide.txt for more information.

Usage:  splitnextera.sh in_file=<file> out=<file> outf=<file> outu=<file> outs=<file>

For pairs in two files, use in1, in2, out1, out2, etc.

*** Note ***
For maximal speed, before running splitnextera, the linkers can be replaced with a constant first.

In other words, you can either do this (which is slightly faster):
bbduk.sh in_file=reads.fq out=replaced.fq ktmask=J k=19 hdist=1 mink=11 hdist2=0 literal=CTGTCTCTTATACACATCTAGATGTGTATAAGAGACAG
splitnextera.sh in_file=replaced.fq out=longmate.fq outf=frag.fq outu=unknown.fq outs=singleton.fq

Or this:
splitnextera.sh in_file=reads.fq out=longmate.fq outf=frag.fq outu=unknown.fq outs=singleton.fq mask=t


I/O parameters:
in_file=<file>       Input reads.  Set to 'stdin.fq' to read from stdin.
out=<file>      Output for pairs with LMP orientation.
outf=<file>     Output for pairs with fragment orientation.
outu=<file>     Pairs with unknown orientation.
outs=<file>     Singleton output.
ow=f            (overwrite) Overwrites files that already exist.
app=f           (append) Append to files that already exist.
zl=4            (ziplevel) Set compression level, 1 (low) to 9 (max).
int=f           (interleaved) Determines whether INPUT file is considered interleaved.
qin_file=auto        ASCII offset for input quality.  May be 33 (Sanger), 64 (Illumina), or auto.
qout=auto       ASCII offset for output quality.  May be 33 (Sanger), 64 (Illumina), or auto (same as input).

Processing Parameters:
mask=f          Set to true if you did not already convert junctions to some symbol, and it will be done automatically.
junction=J      Look for this symbol to designate the junction bases.
innerlmp=f      Generate long mate pairs from the inner pair also, when the junction is found in both reads.
rename=t        Rename read 2 of output when using single-ended input.
minlength=40    (ml) Do not output reads shorter than this.
merge=f         Attempt to merge overlapping reads before looking for junctions.
testmerge=0.0   If nonzero, only merge reads if at least the fraction of input reads are mergable.

Sampling parameters:

reads=-1        Set to a positive number to only process this many INPUT reads (or pairs), then quit.
samplerate=1    Randomly output only this fraction of reads; 1 means sampling is disabled.
sampleseed=-1   Set to a positive number to use that prng seed for sampling (allowing deterministic sampling).

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for splitnextera.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("splitnextera.sh", args, capture_output)

def splitribo(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for splitribo.sh

    Help message:
    Written by Brian Bushnell
Last modified January 22, 2020

Description:  Splits a file of various rRNAs into one file per type
(16S, 18S, 5S, 23s).

Usage:  splitribo.sh in_file=<file,file> out=<pattern>

Standard parameters:
in_file=<file>       Input file.
out=<pattern>   Output file pattern, such as out_#.fa.  The # symbol is
                required and will be substituted by the type name, such as
                16S, to make out_16S.fa, for example.
overwrite=f     (ow) Set to false to force the program to abort rather than
                overwrite an existing file.
ziplevel=9      (zl) Set to 1 (lowest) through 9 (max) to change compression
                level; lower compression is faster.

types=16S,18S,5S,23S,m16S,m18S,p16S
                Align to these sequences.  Fewer types is faster.  m16S
                and m18S are mitochondrial; p16S is plastid (chloroplast).

Processing parameters:
minid=0.59      Ignore alignments with identity lower than this to a 
                consensus sequences.
refineid=0.70   Refine score by aligning to clade-specific consensus if
                the best alignment to a universal consensus is below this.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for splitribo.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("splitribo.sh", args, capture_output)

def splitsam(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for splitsam.sh

    Help message:
    Written by Brian Bushnell
Last modified February 9, 2015

Description:  Splits a sam file into three files:
Plus-mapped reads, Minus-mapped reads, and Unmapped.
If 'header' is the 5th argument, header lines will be included.

Usage:  splitsam <input> <plus output> <minus output> <unmapped output>

Input may be stdin or a sam file, raw or gzipped.
Outputs must be sam files, and may be gzipped.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for splitsam.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("splitsam.sh", args, capture_output)

def splitsam4way(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for splitsam4way.sh

    Help message:
    Written by Brian Bushnell
Last modified January 21, 2015

Description:  Splits sam reads into 4 output files depending on mapping.

Usage:  splitsam4way.sh <input> <outplus> <outminus> <outchimeric> <outunmapped>

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for splitsam4way.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("splitsam4way.sh", args, capture_output)

def splitsam6way(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for splitsam6way.sh

    Help message:
    Written by Brian Bushnell
Last modified June 15, 2017

Description:  Splits sam reads into 6 output files depending on mapping.

Usage:  splitsam6way.sh <input> <r1plus> <r1minus> <r1unmapped> <r2plus> <r2minus> <r2unmapped>

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for splitsam6way.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("splitsam6way.sh", args, capture_output)

def stats(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for stats.sh

    Help message:
    Written by Brian Bushnell
Last modified March 3, 2020

Description:  Generates basic assembly statistics such as scaffold count, 
N50, L50, GC content, gap percent, etc.  For multiple files, please use
statswrapper.sh.  Works with fasta and fastq only (gzipped is fine).
Please read bbmap/docs/guides/StatsGuide.txt for more information.

Usage:        stats.sh in_file=<file>

Parameters:
in_file=file         Specify the input fasta file, or stdin.
out=stdout      Destination of primary output; may be directed to a file.
gc=file         Writes ACGTN content per scaffold to a file.
gchist=file     Filename to output scaffold gc content histogram.
shist=file      Filename to output cumulative scaffold length histogram.
gcbins=200      Number of bins for gc histogram.
n=10            Number of contiguous Ns to signify a break between contigs.
k=13            Estimate memory usage of BBMap with this kmer length.
minscaf=0       Ignore scaffolds shorter than this.
phs=f           (printheaderstats) Set to true to print total size of headers.
n90=t           (printn90) Print the N/L90 metrics.
extended=f      Print additional metrics such as L90, logsum, and score.
pdl=f           (printduplicatelines) Set to true to print lines in the 
                scaffold size table where the counts did not change.
n_=t            This flag will prefix the terms 'contigs' and 'scaffolds'
                with 'n_' in formats 3-6.
addname=f       Adds a column for input file name, for formats 3-6.

Logsum and Powsum:
logoffset=1000  Minimum length for calculating log sum.
logbase=2       Log base for calculating log sum.
logpower=1      Raise the log to a power to increase the weight 
                of longer scaffolds for log sum.
powsum=0.25     Use this power of the length to increase weight
                of longer scaffolds for power sum.

Assembly Score Metric:
score=f         Print assembly score.
aligned=0.0     Set the fraction of aligned reads (0-1).
assemblyscoreminlen=2000   Minimum length of scaffolds to include in
                           assembly score calculation.
assemblyscoremaxlen=50000  Maximum length of scaffolds to get bonus points
                           for being long.


format=<0-7>    Format of the stats information; default 1.
	format=0 prints no assembly stats.
	format=1 uses variable units like MB and KB, and is designed for compatibility with existing tools.
	format=2 uses only whole numbers of bases, with no commas in numbers, and is designed for machine parsing.
	format=3 outputs stats in 2 rows of tab-delimited columns: a header row and a data row.
	format=4 is like 3 but with scaffold data only.
	format=5 is like 3 but with contig data only.
	format=6 is like 3 but the header starts with a #.
	format=7 is like 1 but only prints contig info.
	format=8 is like 3 but in JSON.  You can also just use the 'json' flag.

gcformat=<0-5>  Select GC output format; default 1.
	gcformat=0:	(no base content info printed)
	gcformat=1:	name	length	A	C	G	T	N	GC
	gcformat=2:	name	GC
	gcformat=4:	name	length	GC
	gcformat=5:	name	length	GC	logsum	powsum
	Note that in gcformat 1, A+C+G+T=1 even when N is nonzero.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for stats.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("stats.sh", args, capture_output)

def stats3(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for stats3.sh

    Help message:
    Written by Brian Bushnell
Last modified January 21, 2025

Description:  In progress.
Generates some assembly stats for multiple files.

Usage:        stats3.sh in_file=file
Or:           stats3.sh in_file=file,file
Or:           stats3.sh file file file

Parameters:
in_file=file         Specify the input fasta file(s), or stdin.
                Multiple files can be lested without a 'in_file=' flag.
out=stdout      Destination of primary output; may be directed to a file.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for stats3.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("stats3.sh", args, capture_output)

def statswrapper(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for statswrapper.sh

    Help message:
    Written by Brian Bushnell
Last modified August 1, 2017

Description:  Runs stats.sh on multiple assemblies to produce one output line per file.

Usage:  statswrapper.sh in_file=<input file>

Parameters:
in_file=<file>       Specify the input fasta file, or stdin.  For multiple files a, b, and c: 'statswrapper.sh in_file=a,b,c'.
                'in_file=' may be omitted if this is the first arg, and asterisks may be used; e.g. statswrapper.sh *.fa
gc=<file>       Writes ACGTN content per scaffold to a file.
gchist=<file>   Filename to output scaffold gc content histogram.
gcbins=<200>    Number of bins for gc histogram.
n=<10>          Number of contiguous Ns to signify a break between contigs.
k=<13>          Estimate memory usage of BBMap with this kmer length.
minscaf=<0>     Ignore scaffolds shorter than this.
n_=<t>          This flag will prefix the terms 'contigs' and 'scaffolds' with 'n_' in formats 3-6.
addname=<t>     Adds a column for input file name, for formats 3-6.

format=<1 through 6>   Format of the stats information.  Default is format=3.
   format=1 uses variable units like MB and KB, and is designed for compatibility with existing tools.
   format=2 uses only whole numbers of bases, with no commas in numbers, and is designed for machine parsing.
   format=3 outputs stats in 2 rows of tab-delimited columns: a header row and a data row.
   format=4 is like 3 but with scaffold data only.
   format=5 is like 3 but with contig data only.
   format=6 is like 3 but the header starts with a #.

gcformat=<1 or 2>   Select GC output format.
   gcformat=1:   name   start   stop   A   C   G   T   N   GC
   gcformat=2:   name   GC
   Note that in gcformat 1, A+C+G+T=1 even when N is nonzero.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for statswrapper.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("statswrapper.sh", args, capture_output)

def streamsam(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for streamsam.sh

    Help message:
    Written by Brian Bushnell
Last modified March 21, 2018

Description:  Converts sam/bam to fastq rapidly with multiple threads.
bam files require samtools or sambamba in the path.

Usage:  streamsam.sh in_file=<file> out=<file>

Filtering parameters:
minpos=         Ignore alignments not overlapping this range.
maxpos=         Ignore alignments not overlapping this range.
minmapq=        Ignore alignments with mapq below this.
maxmapq=        Ignore alignments with mapq above this.
contigs=        Comma-delimited list of contig names to include. These 
                should have no spaces, or underscores instead of spaces.
mapped=t        Include mapped reads.
unmapped=t      Include unmapped reads.
secondary=f     Include secondary alignments.
supplimentary=t Include supplimentary alignments.
lengthzero=f    Include alignments without bases.
invert=f        Invert sam filters.
ordered=t       Keep reads in input order.  False is faster.
ref=<file>      Optional reference file.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for streamsam.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("streamsam.sh", args, capture_output)

def subsketch(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for subsketch.sh

    Help message:
    Written by Brian Bushnell
Last modified Jan 7, 2020

Description:  Shrinks sketches to a smaller fixed length.

Please read bbmap/docs/guides/BBSketchGuide.txt for more information.

Usage:       subsketch.sh in_file=file.sketch out=sub.sketch size=1000 autosize=f
Bulk usage:  subsketch.sh in_file=big#.sketch out=small#.sketch sizemult=0.5

Standard parameters:
in_file=<file>       Input sketch file containing one or more sketches.
out=<file>      Output sketch file.
size=10000      Size of sketches to generate, if autosize=f.
autosize=t      Autosize sketches based on genome size.
sizemult=1      Adjust default sketch autosize by this factor.
blacklist=      Apply a blacklist to the sketch before resizing.
files=31        If the output filename contains a # symbol,
                spread the output across this many files, replacing
                the # with a number.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

For more detailed information, please read /bbmap/docs/guides/BBSketchGuide.txt.
Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for subsketch.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("subsketch.sh", args, capture_output)

def summarizecontam(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for summarizecontam.sh

    Help message:
    Written by Brian Bushnell
Last modified March 19, 2018

Description:  Summarizes monthly contam files into a single file.
This is for internal JGI use.

Usage:  summarizecontam.sh <input files> out=<output file>

Parameters:
in_file=<file,file>  Input contam summary files, comma-delimited.
                Alternately, file arguments (from a * expansion) will be 
                considered input files.
out=<file>      Output.
tree=auto       Taxtree file location (optional).
overwrite=t     (ow) Set to false to force the program to abort rather than
                overwrite an existing file.

Filter Parameters (passing all required to pass):
minreads=0      Ignore records with fewer reads than this.
minsequnits=0   Ignore records with fewer seq units than this.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for summarizecontam.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("summarizecontam.sh", args, capture_output)

def summarizecoverage(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for summarizecoverage.sh

    Help message:
    Written by Brian Bushnell
Last modified April 5, 2020

Description:  Summarizes coverage information from basecov files
              created by pileup.sh.  They should be named like
              'sample1_basecov.txt' but other naming styles are fine too.

Usage:        summarizecoverage.sh *basecov.txt out=<output file>

Parameters:
in_file=<file>           'in_file=' is not necessary.  Any filename used as a
                    parameter will be assumed to be an input basecov file.
out=<file>          Write the summary here.  Default is stdout.
reflen=-1           If positive, use this as the total reference length.
                    Otherwise, assume basecov files report every ref base.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for summarizecoverage.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("summarizecoverage.sh", args, capture_output)

def summarizecrossblock(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for summarizecrossblock.sh

    Help message:
    Written by Brian Bushnell
Last modified June 10, 2016

Description:  Summarizes CrossBlock results.
Used for testing and validating CrossBlock.

Usage:  summarizecrossblock.sh in_file=<input file> out=<output file>

Standard parameters:
in_file=<file>       A text file of files, or a comma-delimited list of files.
                Each is a path to results.txt output from Crossblock.
out=<file>      Output file for the summary.
overwrite=f     (ow) Set to false to force the program to abort rather than
                overwrite an existing file.

Processing parameters:
None yet!

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for summarizecrossblock.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("summarizecrossblock.sh", args, capture_output)

def summarizemerge(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for summarizemerge.sh

    Help message:
    Written by Brian Bushnell
Last modified June 6, 2016

Description:  Summarizes the output of GradeMerge for comparing 
read-merging performance.

Usage:  summarizemerge.sh in_file=<file>

Parameters:
in_file=<file>       A file containing GradeMerge output.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for summarizemerge.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("summarizemerge.sh", args, capture_output)

def summarizequast(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for summarizequast.sh

    Help message:
    Written by Brian Bushnell
Last modified October 17, 2016

Description:  Summarizes the output of multiple Quast reports for
making box plots.

Usage:  summarizequast.sh */quast/report.tsv

Parameters:
out=stdout      Destination for summary.
required=       A required substring in assembly names for filtering.
normalize=t     Normalize each metric to the average per report.
box=t           Print only 5 points per metric for box plots.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for summarizequast.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("summarizequast.sh", args, capture_output)

def summarizescafstats(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for summarizescafstats.sh

    Help message:
    Written by Brian Bushnell
Last modified May 26, 2015

Description:  Summarizes the scafstats output of BBMap for evaluation
of cross-contamination.  The intended use is to map multiple libraries or 
assemblies, of different multiplexed organisms, to a concatenated reference 
containing one fused scaffold per organism.  This will convert all of the 
resulting stats files (one per library) to a single text file, with multiple 
columns, indicating how much of the input hit the primary versus nonprimary 
scaffolds.

Usage:  summarizescafstats.sh in_file=<file,file...> out=<file>

You can alternatively use a wildcard, like this:
summarizescafstats.sh scafstats_*.txt out=summary.txt

Parameters:
in_file=<file>       A list of stats files, or a text file containing one stats file name per line.
out=<file>      Destination for summary.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for summarizescafstats.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("summarizescafstats.sh", args, capture_output)

def summarizeseal(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for summarizeseal.sh

    Help message:
    Written by Brian Bushnell
Last modified June 22, 2016

Description:  Summarizes the stats output of Seal for evaluation of 
cross-contamination.  The intended use is to map multiple libraries or 
assemblies, of different multiplexed organisms, to a concatenated reference 
containing one fused scaffold per organism.  This will convert all of the 
resulting stats files (one per library) to a single text file, with multiple 
columns, indicating how much of the input hit the primary versus nonprimary 
scaffolds.

If ingoresametaxa or ignoresamebarcode are used, ref names must be 
in this format:
barcode,library,tax,location
For example:
6-G,N0296,gammaproteobacteria_bacterium,deep_ocean

Usage:  summarizeseal.sh in_file=<file,file...> out=<file>

You can alternately run 'summarizeseal.sh *.txt out=out.txt'

Parameters:
in_file=<file>              A list of stats files, or a text file containing one stats file name per line.
out=<file>             Destination for summary.
printtotal=t           (pt) Print a line summarizing the total contamination rate of all assemblies.
ignoresametaxa=f       Ignore secondary hits sharing taxonomy. 
ignoresamebarcode=f    Ignore secondary hits sharing a barcode.
ignoresamelocation=f   Ignore secondary hits sharing a sampling site.
totaldenominator=f     (td) Use all bases as denominator rather than mapped bases.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for summarizeseal.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("summarizeseal.sh", args, capture_output)

def summarizesketch(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for summarizesketch.sh

    Help message:
    Written by Brian Bushnell
Last modified January 25, 2018

Description:  Summarizes the output of BBSketch. 

Usage:  summarizesketch.sh in_file=<file,file...> out=<file>

You can alternately run 'summarizesketch.sh *.txt out=out.txt'

Parameters:
in_file=<file>       A list of stats files, or a text file containing one stats file name per line.
out=<file>      Destination for summary.
tree=           A TaxTree file.
level=genus     Ignore contaminants with the same taxonomy as the primary hit at this level.
unique=f        Use the contaminant with the most unique hits rather than highest score.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for summarizesketch.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("summarizesketch.sh", args, capture_output)

def synthmda(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for synthmda.sh

    Help message:
    Written by Brian Bushnell
Last modified October 22, 2015

Description:  Generates synthetic reads following an MDA-amplified single cell's coverage distribution.

Usage:  synthmda.sh in_file=<reference> out=<reads out file>

Input may be fasta or fastq, compressed or uncompressed.

Parameters:
reads=12000000      Generate this many reads.
paired=t            Generate paired reads.
length=150          Reads should be this long.
minlen=4000         Min length of MDA contig.
maxlen=150000       Max length of MDA contig.
cycles=9            Number of MDA cycles; higher is more spiky.
initialratio=1.3    Fraction of genome initially replicated; 
                    lower is more spiky.
ratio=1.7           Fraction of genome replicated per cycle.
refout=null         Write MDA'd genome to this file.
perfect=0           This fraction of reads will be error-free.
amp=200             'amp' flag sent to RandomReads (higher is more spiky).
build=7             Index MDA'd genome in this location.
prefix=null         Generated reads will start with this prefix.
overwrite=t         (ow) Set to false to force the program to abort rather 
                    than overwrite an existing file.

Java Parameters:
-Xmx                This will set Java's memory usage, overriding autodetection.
                    -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom               This flag will cause the process to exit if an
                    out-of-memory exception occurs.  Requires Java 8u92+.
-da                 Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for synthmda.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("synthmda.sh", args, capture_output)

def tadpipe(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for tadpipe.sh

    Help message:
    Written by Brian Bushnell
Last modified September 18, 2019

Description:  Runs TadpoleWrapper after some preprocessing,
to allow optimal assemblies using long kmers.
Only paired reads are supported.

Usage:
tadpipe.sh in_file=reads.fq out=contigs.fa


Parameters:
in_file=<file>           Input reads.
in2=<file>          Optional read 2, if reads are in two files.
out=contigs.fa      Output file name.
temp=$TMPDIR        Path to a directory for temp files.
delete=t            Delete intermediate files.
gz=f                Gzip intermediate files.

Other parameters can be passed to individual phases like this:

assemble_k=200,250  Set kmer lengths for assembly phase.
merge_strict        Set the strict flag in merge phase.
extend_el=120       Set the left-extension distance in the extension phase.

Valid prefixes:

filter_             PhiX and contaminant filtering.
trim_               Adapter trimmming.
merge_              Paired-read merging.
correct_            Error correction.
extend_             Read extension.
assemble_           Final assembly.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for tadpipe.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("tadpipe.sh", args, capture_output)

def tadpole(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for tadpole.sh

    Help message:
    Written by Brian Bushnell
Last modified February 3, 2021

Description:  Uses kmer counts to assemble contigs, extend sequences, 
or error-correct reads.  Tadpole has no upper bound for kmer length,
but some values are not supported.  Specifically, it allows 1-31,
multiples of 2 from 32-62, multiples of 3 from 63-93, etc.
Please read bbmap/docs/guides/TadpoleGuide.txt for more information.

Usage:
Assembly:     tadpole.sh in_file=<reads> out=<contigs>
Extension:    tadpole.sh in_file=<reads> out=<extended> mode=extend
Correction:   tadpole.sh in_file=<reads> out=<corrected> mode=correct

Recommended parameters for optimal assembly:
tadpole.sh in_file=<reads> out=<contigs> shave rinse pop k=<50-70% of read length>

Extension and correction may be done simultaneously.  Error correction on 
multiple files may be done like this:

tadpole.sh in_file=libA_r1.fq,libA_merged.fq in2=libA_r2.fq,null extra=libB_r1.fq out=ecc_libA_r1.fq,ecc_libA_merged.fq out2=ecc_libA_r2.fq,null mode=correct

Extending contigs with reads could be done like this:

tadpole.sh in_file=contigs.fa out=extended.fa el=100 er=100 mode=extend extra=reads.fq k=62


Input parameters:
in_file=<file>           Primary input file for reads to use as kmer data.
in2=<file>          Second input file for paired data.
extra=<file>        Extra files for use as kmer data, but not for error-
                    correction or extension.
reads=-1            Only process this number of reads, then quit (-1 means all).
NOTE: in, in2, and extra may also be comma-delimited lists of files.

Output parameters:
out=<file>          Write contigs (in contig mode) or corrected/extended 
                    reads (in other modes).
out2=<file>         Second output file for paired output.
outd=<file>         Write discarded reads, if using junk-removal flags.
dot=<file>          Write a contigs connectivity graph (partially implemented)
dump=<file>         Write kmers and their counts.
fastadump=t         Write kmers and counts as fasta versus 2-column tsv.
mincounttodump=1    Only dump kmers with at least this depth.
showstats=t         Print assembly statistics after writing contigs.

Prefiltering parameters:
prefilter=0         If set to a positive integer, use a countmin sketch
                    to ignore kmers with depth of that value or lower.
prehashes=2         Number of hashes for prefilter.
prefiltersize=0.2   (pff) Fraction of memory to use for prefilter.
minprobprefilter=t  (mpp) Use minprob for the prefilter.
prepasses=1         Use this many prefiltering passes; higher be more thorough
                    if the filter is very full.  Set to 'auto' to iteratively 
                    prefilter until the remaining kmers will fit in memory.
onepass=f           If true, prefilter will be generated in same pass as kmer
                    counts.  Much faster but counts will be lower, by up to
                    prefilter's depth limit.
filtermem=0         Allows manually specifying prefilter memory in bytes, for
                    deterministic runs.  0 will set it automatically.

Hashing parameters:
k=31                Kmer length (1 to infinity).  Memory use increases with K.
prealloc=t          Pre-allocate memory rather than dynamically growing; 
                    faster and more memory-efficient.  A float fraction (0-1)
                    may be specified; default is 1.
minprob=0.5         Ignore kmers with overall probability of correctness below this.
minprobmain_file=t       (mpm) Use minprob for the primary kmer counts.
threads=X           Spawn X worker threads; default is number of logical processors.
buildthreads=X      Spawn X contig-building threads. If not set, defaults to the same
                    as threads.  Setting this to 1 will make contigs deterministic.
rcomp=t             Store and count each kmer together and its reverse-complement.
coremask=t          All kmer extensions share the same hashcode.
fillfast=t          Speed up kmer extension lookups.

Assembly parameters:
mincountseed=3      (mcs) Minimum kmer count to seed a new contig or begin extension.
mincountextend=2    (mce) Minimum kmer count continue extension of a read or contig.
                    It is recommended that mce=1 for low-depth metagenomes.
mincountretain_file=0    (mincr) Discard kmers with count below this.
maxcountretain_file=INF  (maxcr) Discard kmers with count above this.
branchmult1=20      (bm1) Min ratio of 1st to 2nd-greatest path depth at high depth.
branchmult2=3       (bm2) Min ratio of 1st to 2nd-greatest path depth at low depth.
branchlower=3       (blc) Max value of 2nd-greatest path depth to be considered low.
minextension=2      (mine) Do not keep contigs that did not extend at least this much.
mincontig=auto      (minc) Do not write contigs shorter than this.
mincoverage=1       (mincov) Do not write contigs with average coverage below this.
maxcoverage=inf     (maxcov) Do not write contigs with average coverage above this.
trimends=0          (trim) Trim contig ends by this much.  Trimming by K/2 
                    may yield more accurate genome size estimation.
trimcircular=t      Trim one end of contigs ending in LOOP/LOOP by K-1,
                    to eliminate the overlapping portion.
contigpasses=16     Build contigs with decreasing seed depth for this many iterations.
contigpassmult=1.7  Ratio between seed depth of two iterations.
ownership=auto      For concurrency; do not touch.
processcontigs=f    Explore the contig connectivity graph.
popbubbles=t        (pop) Pop bubbles; increases contiguity.  Requires 
                    additional time and memory and forces processcontigs=t.

Processing modes:
mode=contig         contig: Make contigs from kmers.
                    extend: Extend sequences to be longer, and optionally
                            perform error correction.
                    correct: Error correct only.
                    insert: Measure insert sizes.
                    discard: Discard low-depth reads, without error correction.

Extension parameters:
extendleft=100      (el) Extend to the left by at most this many bases.
extendright=100     (er) Extend to the right by at most this many bases.
ibb=t               (ignorebackbranches) Do not stop at backward branches.
extendrollback=3    Trim a random number of bases, up to this many, on reads
                    that extend only partially.  This prevents the creation
                    of sharp coverage discontinuities at branches.

Error-correction parameters:
ecc=f               Error correct via kmer counts.
reassemble=t        If ecc is enabled, use the reassemble algorithm.
pincer=f            If ecc is enabled, use the pincer algorithm.
tail=f              If ecc is enabled, use the tail algorithm.
eccfull=f           If ecc is enabled, use tail over the entire read.
aggressive=f        (aecc) Use aggressive error correction settings.
                    Overrides some other flags like errormult1 and deadzone.
conservative=f      (cecc) Use conservative error correction settings.
                    Overrides some other flags like errormult1 and deadzone.
rollback=t          Undo changes to reads that have lower coverage for
                    any kmer after correction.
markbadbases=0      (mbb) Any base fully covered by kmers with count below 
                    this will have its quality reduced.
markdeltaonly=t     (mdo) Only mark bad bases adjacent to good bases.
meo=t               (markerrorreadsonly) Only mark bad bases in reads 
                    containing errors.
markquality=0       (mq) Set quality scores for marked bases to this.
                    A level of 0 will also convert the base to an N.
errormult1=16       (em1) Min ratio between kmer depths to call an error.
errormult2=2.6      (em2) Alternate ratio between low-depth kmers.
errorlowerconst=3   (elc) Use mult2 when the lower kmer is at most this deep.
mincountcorrect=3   (mcc) Don't correct to kmers with count under this.
pathsimilarityfraction=0.45(psf) Max difference ratio considered similar.
                           Controls whether a path appears to be continuous.
pathsimilarityconstant=3   (psc) Absolute differences below this are ignored.
errorextensionreassemble=5 (eer) Verify this many kmers before the error as
                           having similar depth, for reassemble.
errorextensionpincer=5     (eep) Verify this many additional bases after the
                           error as matching current bases, for pincer.
errorextensiontail=9       (eet) Verify additional bases before and after 
                           the error as matching current bases, for tail.
deadzone=0          (dz) Do not try to correct bases within this distance of
                    read ends.
window=12           (w) Length of window to use in reassemble mode.
windowcount=6       (wc) If more than this many errors are found within a
                    a window, halt correction in that direction.
qualsum=80          (qs) If the sum of the qualities of corrected bases within
                    a window exceeds this, halt correction in that direction.
rbi=t               (requirebidirectional) Require agreement from both 
                    directions when correcting errors in the middle part of 
                    the read using the reassemble algorithm.
errorpath=1         (ep) For debugging purposes.

Junk-removal parameters (to only remove junk, set mode=discard):
tossjunk=f          Remove reads that cannot be used for assembly.
                    This means they have no kmers above depth 1 (2 for paired
                    reads) and the outermost kmers cannot be extended.
                    Pairs are removed only if both reads fail.
tossdepth=-1        Remove reads containing kmers at or below this depth.
                    Pairs are removed if either read fails.
lowdepthfraction=0  (ldf) Require at least this fraction of kmers to be
                    low-depth to discard a read; range 0-1. 0 still
                    requires at least 1 low-depth kmer.
requirebothbad=f    (rbb) Only discard pairs if both reads are low-depth.
tossuncorrectable   (tu) Discard reads containing uncorrectable errors.
                    Requires error-correction to be enabled.

Shaving parameters:
shave=f             Remove dead ends (aka hair).
rinse=f             Remove bubbles.
wash=               Set shave and rinse at the same time.
maxshavedepth=1     (msd) Shave or rinse kmers at most this deep.
exploredist=300     (sed) Quit after exploring this far.
discardlength=150   (sdl) Discard shavings up to this long.
Note: Shave and rinse can produce substantially better assemblies
for low-depth data, but they are very slow for large metagenomes.
So they are recommended to be enabled for optimal results.

Overlap parameters (for overlapping paired-end reads only):
merge=f             Attempt to merge overlapping reads prior to 
                    kmer-counting, and again prior to correction.  Output
                    will still be unmerged pairs.
ecco=f              Error correct via overlap, but do not merge reads.
testmerge=t         Test kmer counts around the read merge junctions.  If
                    it appears that the merge created new errors, undo it.

Java Parameters:
-Xmx                This will set Java's memory usage, overriding autodetection.
                    -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom               This flag will cause the process to exit if an
                    out-of-memory exception occurs.  Requires Java 8u92+.
-da                 Disable assertions.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for tadpole.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("tadpole.sh", args, capture_output)

def tadwrapper(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for tadwrapper.sh

    Help message:
    Written by Brian Bushnell
Last modified August 18, 2016

Description:  Generates multiple assemblies with Tadpole
to estimate the optimal kmer length.

Usage:
tadwrapper.sh in_file=reads.fq out=contigs%.fa k=31,62,93

Parameters:
out=<file>      Output file name.  Must contain a % symbol.
outfinal=<file> Optional.  If set, the best assembly file 
                will be renamed to this.
k=31            Comma-delimited list of kmer lengths.
delete=f        Delete assemblies before terminating.
quitearly=f     Quit once metrics stop improving with longer kmers.
bisect=f        Recursively assemble with the kmer midway between
                the two best kmers until improvement halts.
expand=f        Recursively assemble with kmers shorter or longer
                than the current best until improvement halts.

All other parameters are passed to Tadpole.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for tadwrapper.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("tadwrapper.sh", args, capture_output)

def tagandmerge(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for tagandmerge.sh

    Help message:
    Written by Brian Bushnell
Last modified May 16, 2024

Description:  Accepts multiple input files from a demultiplexed lane.
Parses the barcode from the filename and adds (tab)BARCODE to read headers.
Outputs all reads into a single file.  Optionally, trims bases and drops R2.
Intended for evaluating demultiplexing methods.  For example:
tagandmerge.sh path/*0.*.fastq.gz dropr2 trim out=tagged.fq.gz barcodes=bc.txt

Usage:  tagandmerge.sh *.fastq.gz out=<output file>
or
tagandmerge.sh in_file=<file,file,file> out=<output file>

Input may be fasta or fastq, compressed or uncompressed.

Standard parameters:
in_file=<file,file>  A comma-delimited list of files.  If wildcards are used,
                omit in_file= and the commas.
out=<file>      Print all reads to this destination.
barcodes=<file> Print barcodes from file names to this destination.
trim=-1         If positive, trim all reads to this length.
dropr2=f        Discard read 2 if the input is interleaved.
shrinkheader=f  (shrink) Illumina only; remove unnecessary header fields.
remap=-+        Remap symbols in the barcode.  By default, '+' replaces '-'.
                To eliminate this set 'remap=null'.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for tagandmerge.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("tagandmerge.sh", args, capture_output)

def taxonomy(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for taxonomy.sh

    Help message:
    Written by Brian Bushnell
Last modified Jan 7, 2020

Description:   Prints the full taxonomy of a string.
String may be a gi number, NCBI taxID, or Latin name.
An NCBI identifier should just be a number or ncbi|number.
A gi number should be gi|number.
Please read bbmap/docs/guides/TaxonomyGuide.txt for more information.
Not: It is more convenient to use taxonomy.jgi-psf.org.

Usage:  taxonomy.sh tree=<tree file> <identifier>
Alternate usage: taxonomy.sh tree=<tree file> in_file=<file>

Usage examples:
taxonomy.sh tree=tree.taxtree.gz homo_sapiens canis_lupus 9606
taxonomy.sh tree=tree.taxtree.gz gi=gitable.int1.d.gz in_file=refseq.fasta

Processing parameters:
in_file=<file>       A file containing named sequences, or just the names.
out=<file>      Output file.  If blank, use stdout.
tree=<file>     Specify a TaxTree file like tree.taxtree.gz.  
                On Genepool, use 'auto'.
gi=<file>       Specify a gitable file like gitable.int1d.gz. Only needed
                if gi numbers will be used.  On Genepool, use 'auto'.
accession=      Specify one or more comma-delimited NCBI accession to taxid
                files.  Only needed if accesions will be used; requires ~45GB
                of memory.  On Genepool, use 'auto'.
level=null      Set to a taxonomic level like phylum to just print that level.
minlevel=-1     For multi-level printing, do not print levels below this.
maxlevel=life   For multi-level printing, do not print levels above this.
silva=f         Parse headers using Silva or semicolon-delimited syntax.
taxpath=auto    Set the path to taxonomy files; auto only works at NERSC.

Parameters without an '=' symbol will be considered organism identifiers.

* Note *
Tree and table files are in /global/projectb/sandbox/gaag/bbtools/tax
For non-Genepool users, or to make new ones, use taxtree.sh and gitable.sh

Java Parameters:
-Xmx            This will set Java's memory usage, 
                overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify
                200 megs.  The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for taxonomy.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("taxonomy.sh", args, capture_output)

def taxserver(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for taxserver.sh

    Help message:
    Written by Brian Bushnell and Shijie Yao
Last modified Jan 7, 2020

Description:   Starts a server that translates NCBI taxonomy.

Usage:  taxserver.sh tree=<taxtree file> table=<gitable file> port=<number>

Usage examples:
taxserver.sh tree=tree.taxtree.gz table=gitable.int1d.gz port=1234

On Genepool:
taxserver.sh tree=auto table=auto port=1234

For accession number support, add accession=<something>  E.g.:

External:
taxserver.sh -Xmx45g tree=tree.taxtree.gz table=gitable.int1d.gz accession=prot.accession2taxid.gz,nucl_wgs.accession2taxid.gz port=1234

On Genepool:
taxserver.sh tree=auto table=auto accession=auto port=1234

If all expected files are in some specific location, you can also do this:
taxserver.sh -Xmx45g tree=auto table=auto accession=auto port=1234 taxpath=/path/to/files

To kill remotely, launch with the flag kill=password, then access /kill/password

Parameters:

tree=auto           taxtree path.  Always necessary.
table=auto          gitable path.  Necessary for gi number support.
accession=null      Comma-delimited paths of accession files.
                    Necessary for accession support.
img=null            IMG dump file.
pattern=null        Pattern file, for storing accessions more efficiently.
port=3068           Port number.
domain_file=             Domain to be displayed in the help message.
                    Default is taxonomy.jgi-psf.org.
dbname=             Set the name of the database in the help message.
sketchcomparethreads=16    Limit compare threads per connection.
sketchloadthreads=4 Limit load threads (for local queries of fastq).
sketchonly=f        Don't hash taxa names.
k=31                Kmer length, 1-32.  To maximize sensitivity and 
                    specificity, dual kmer lengths may be used:  k=31,24
prealloc=f          Preallocate some data structures for faster loading.

Security parameters:

killcode=           Set a password to allow remote killing.
oldcode=            Set the password of a prior instance.
oldaddress=         Attempt to kill a prior instance after initialization,
                    by sending the old code to this address.  For example,
                    taxonomy.jgi-psf.org/kill/
allowremotefileaccess=f   Allow non-internal queries to use internal files
                    for sketching in local mode.
allowlocalhost=f    Consider a query internal if it originates from localhost
                    without being proxied.
addressprefix=128.  Queries originating from this IP address prefix will be
                    considered internal.


Unrecognized parameters with no = symbol will be treated as sketch files.
Other sketch parameters such as index and k are also allowed.
Please consult bbmap/docs/guides/TaxonomyGuide.txt and BBSketchGuide.txt for more information.

Java Parameters:
-Xmx                This will set Java's memory usage, overriding autodetection.
                    -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom               This flag will cause the process to exit if an
                    out-of-memory exception occurs.  Requires Java 8u92+.
-da                 Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for taxserver.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("taxserver.sh", args, capture_output)

def taxsize(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for taxsize.sh

    Help message:
    Written by Brian Bushnell
Last modified December 13, 2017

Description:  Calculates the amount of sequence per tax node.

Usage:  taxsize.sh in_file=<file> out=<file> tree=<file>

Parameters:
in_file=             A fasta file annotated with taxonomic data in headers, 
                such as modified RefSeq.
out=            Location to write the size data.
tree=           Location of taxtree file.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for taxsize.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("taxsize.sh", args, capture_output)

def taxtree(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for taxtree.sh

    Help message:
    Written by Brian Bushnell.
Last modified Jan 7, 2020

Description:  Creates tree.taxtree from names.dmp and nodes.dmp.
These are in taxdmp.zip available at ftp://ftp.ncbi.nih.gov/pub/taxonomy/
The taxtree file is needed for programs that can deal with taxonomy, 
like Seal and SortByTaxa.

Usage:  taxtree.sh names.dmp nodes.dmp merged.dmp tree.taxtree.gz

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM.  The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for taxtree.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("taxtree.sh", args, capture_output)

def testaligners(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for testaligners.sh

    Help message:
    Written by Brian Bushnell
Last modified May 18, 2025

Description:  Aligns a query sequence to a reference using multiple aligners.
Outputs the identity, rstart and rstop positions, time, and #loops.

Usage:
testaligners.sh <query> <ref>
testaligners.sh <query> <ref> <iterations> <threads> <simd>

Parameters:
query           A literal nucleotide sequence or fasta file.
ref             A literal nucleotide sequence or fasta file.
iterations      Optional integer for benchmarking multiple iterations.
threads         Number of parallel instances to use.
simd            Enable SIMD operations; requires AVX-256 and Java 17+.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for testaligners.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("testaligners.sh", args, capture_output)

def testaligners2(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for testaligners2.sh

    Help message:
    Written by Brian Bushnell
Last modified May 31, 2025

Description:  Tests multiple aligners using random sequences.
The sequences have variable pairwise ANI, and each
ANI level is tested multiple times for average accuracy
and loop count.
Outputs the identity, rstart and rstop positions, time, and #loops.
Note that the 'design' ANI is approximate and will not match
the measured ANI.

Usage:
testaligners2.sh iterations=30 maxani=100 minani=90 step=2

Parameters:
length=40k      Length of sequences.
iterations=32   Iterations to average; higher is more accurate.
maxani=80       Max ANI to model.
minani=30       Min ANI to model.
step=2          ANI step size.
sinewaves=0     Sinewave count to model variable conservation.
threads=        Parallel alignments; default is logical cores.
simd            Enable SIMD operations; requires AVX-256 and Java 17+.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for testaligners2.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("testaligners2.sh", args, capture_output)

def testfilesystem(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for testfilesystem.sh

    Help message:
    Written by Brian Bushnell
Last modified December 11, 2017

Description:  Logs filesystem performance by creating, deleting,
and copying files.

Usage:  testfilesystem.sh <in> <out> <log> <size> <ways> <interval in seconds>

'in' should contain the # symbol if ways>1.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for testfilesystem.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("testfilesystem.sh", args, capture_output)

def testformat(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for testformat.sh

    Help message:
    Written by Brian Bushnell
Last modified August 4, 2016

Description:  Tests file extensions and contents to determine format,
quality, compression, interleaving, and read length.  More than one file
may be specified.  Note that ASCII-33 (sanger) and ASCII-64 
(old Illumina/Solexa) cannot always be differentiated.

Usage:  testformat.sh <file>

See also:  testformat2.sh, stats.sh

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for testformat.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("testformat.sh", args, capture_output)

def testformat2(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for testformat2.sh

    Help message:
    Written by Brian Bushnell
Last modified July 10, 2023

Description:  Reads the entire file to find extended information about the format and contents.

Usage:  testformat2.sh <file>


Parameters:

full=t          Process the full file.
speed=f         Print processing time.

printjunk=f     Print headers of junk reads to stdout.
zmw=t           Parse PacBio ZMW IDs.

barcodelist=    Optional list of expected barcodes.  May be a filename
                with one line per barcode, or a comma-delimited literal. 
printbarcodes=f Print barcodes and counts to stdout.
edist=f         Calculate barcode edit distance.

printqhist=f    Print quality histogram to stdout.
printihist=f    Print insert size histogram to stdout.

bhistlen=10k    bhist.txt will be calculated from reads up to this length.
                To allow all reads, set to 0.

merge=t         Calculate mergability via BBMerge.
sketch=t        (card) Calculate cardinality via BBSketch.
                If enabled, also sends the sketch to the refseq server.
trim=t          Calculate trimmability from quality.

File output parameters (these can be eliminated by setting to null):

junk=junk.txt          Print headers of junk reads to this file.
barcodes=barcodes.txt  Print barcodes to this file.

hist=t                 False will clear all default histogram files.
qhist=qhist.txt        Print quality histogram to this file.
ihist=ihist.txt        Print insert size histogram to this file.
khist=khist.txt        Print kmer frequency histogram to this file.
bhist=bhist.txt        Print base composition histogram to this file.
lhist=lhist.txt        Print length histogram to this file.
gchist=gchist.txt      Print gc histogram to this file.
zmwhist=zmwhist.txt    Print ZMW pass count histogram to this file.


Terminology:

Format          File format, e.g. fastq.
Compression     Compression format, e.g. gz.
Interleaved     True if reads are paired in a single file.
MaxLen          Maximum observed read length.
MinLen          Minimum observed read length.
StdevLen        Standard deviation of observed read lengths.
ModeLen         Mode of observed read lengths.
QualOffset      Quality score offset.
NegativeQuals   Number of bases with negative quality scores.

Content         Nucleotides or AminoAcids.
Type            RNA, DNA, or Mixed.
Reads           Number of reads processed.
-JunkReads      Reads with invalid bases or other problems.
-ChastityFail   Reads failing Illumina's chastity filter.
-BadPairNames   Read pairs whose names don't match.

Bases           Number of bases processed.
-Lowercase      Lowercase bases.
-Uppercase      Uppercase bases.
-Non-Letter     Non-letter symbols in bases.
-FullyDefined   A, C, G, T, or U bases.
-No-call        N bases.
-Degenerate     Non-ACGTUN valid IUPAC symbols.
-Gap            - symbol.
-Invalid        Symbols that are not valid characters for sequence.

GC              GC content: (C+G)/(C+G+A+T+U).
Cardinality     Approximate number of unique 31-mers in the file.
Organism        Taxonomic name of top hit from BBSketch RefSeq server.
TaxID           TaxID from BBSketch.
Barcodes        Number of observed barcodes (for Illumina).
ZMWs            Number of observed ZMWs (for PacBio).

Mergable        Fraction of read pairs that appear to overlap.
-InsertMean     Average insert size, from merging.
-InsertMode     Insert size mode from, merging.
-AdapterReads   Fraction of reads with adapter sequence, from merging.
-AdapterBases   Fraction of bases that are adapter sequence, from merging.

QErrorRate      Average error rate from quality scores.
-QAvgLog        Logarithmic average quality score.
-QAvgLinear     Linear average quality score.
-TrimmedAtQ5    Fraction of bases trimmed at Q5.
-TrimmedAtQ10   Fraction of bases trimmed at Q10.
-TrimmedAtQ15   Fraction of bases trimmed at Q15.
-TrimmedAtQ20   Fraction of bases trimmed at Q20.

Qhist           Quality score histogram, one line per observed quality bin.
Ihist           Insert size histogram, based on pair merging.
BarcodeList     List of observed barcodes.
JunkList        List of headers of problematic reads.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for testformat2.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("testformat2.sh", args, capture_output)

def tetramerfreq(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for tetramerfreq.sh

    Help message:
    Written by Shijie Yao and Brian Bushnell
Last modified April 25, 2025

Description: DNA Tetramer analysis.
DNA tetramers are counted for each sub-sequence of window size in the sequence.  
The window slides along the sequence by the step length.
Sub-sequence shorter than the window size is ignored. Tetramers containing N are ignored. 

Usage: TetramerFreq.sh in_file=<input file> out=<output file> step=500 window=2000

Input may be fasta or fastq, compressed or uncompressed.

Standard parameters:
in_file=<file>       DNA sequence input file 
out=<file>      Output file name
step/s=INT      Step size (default 500) 
window/w=INT    Window size (default 2kb); <=0 turns windowing off (e.g. short reads)
short=T/F       Print lines for sequences shorter than window (default F)
k=INT           Kmer length (default 4)
gc              Print a GC column in the output.
float           Output kmer frequencies instead of counts.
comp            Output GC-compensated kmer frequencies.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for tetramerfreq.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("tetramerfreq.sh", args, capture_output)

def textfile(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for textfile.sh

    Help message:
    Written by Brian Bushnell
Last modified February 17, 2015

Description:  Displays contents of a text file.
Start line and stop line are zero-based.  Start is inclusive,
stop is exclusive.

Usage:  textfile.sh <file> <start line> <stop line>

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for textfile.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("textfile.sh", args, capture_output)

def tiledump(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for tiledump.sh

    Help message:
    Written by Brian Bushnell
Last modified November 14, 2024

Description:  Processes a tile dump from FilterByTile.

Usage:  tiledump.sh in_file=<input file> out=<output file>

Standard parameters:
in_file=<file>       Input dump file.
out=<file>      Output dump file.
overwrite=t     (ow) Set to false to force the program to abort rather than
                overwrite an existing file.

Processing parameters:
x=-1            Widen tiles to at least this X width.
y=-1            Widen tiles to at least this Y width.
reads=-1        Widen tiles to at least this average number of reads.
alignedreads=250  Average aligned reads per tile for error rate calibration.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for tiledump.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("tiledump.sh", args, capture_output)

def train(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for train.sh

    Help message:
    Written by Brian Bushnell
Last modified July 15, 2025

Description:  Trains or evaluates neural networks.

Usage:  train.sh in_file=<data> dims=<X,Y,Z> out=<trained network>

train.sh in_file=<data> netin_file=<network> evaluate

Input may be fasta or fastq, compressed or uncompressed.


I/O parameters:
in_file=<file>       Tab-delimited data vectors.  The first line should look like
                '#dims	5	1' with the number of inputs and outputs; the
                first X columns are inputs, and the last Y the desired result.
                Subsequent lines are tab-delimited floating point numbers.
                Can be created via seqtovec.sh.
validate=<file> Optional validation dataset used exclusively for evaluation.
net=<file>      Optional input network to train.
out=<file>      Final output network after the last epoch.
outb=<file>     Best discovered network according to evaluation metrics.
overwrite=f     (ow) Set to false to force the program to abort rather than
                overwrite an existing file.

Processing parameters:
evaluate=f      Don't do any training, just evaluate the network.
dims=           Set network dimensions.  E.g. dims=5,12,7,1
mindims,maxdims These allow random dimensions, but the number of inputs and
                outputs must agree.  e.g. mindims=5,6,3,1 maxdims=5,18,15,1
batches=400k    Number of batches to train.
alpha=0.08      Amount to adjust weights during backpropagation.  Larger 
                numbers train faster but may not converge.
balance=0.2     If the positive and negative samples are unequal, make copies
                of whichever has fewer until this ratio is met.  1.0 would
                make an equal number of positive and negative samples.
density=1.0     Retain at least this fraction of edges.
edges=-1        If positive, cap the maximum number of edges.
dense=t         Set dense=f (or sparse) to process as a sparse network.
                Dense mode is fastest for fully- or mostly-connected networks;
                sparse becomes faster below 0.25 density or so.

Advanced training parameters
seed=-1         A positive seed will yield deterministic output;
                negative will use a random seed.  For multiple networks,
                each gets a different seed but you only need to set it once.
nets=1          Train this many networks concurrently (per cycle).  Only the
                best network will be reported, so training more networks will
                yield give a better result.  Higher increases memory use, but
                also can improve CPU utilization on many-threaded CPUs.
cycles=1        Each cycle trains 'nets' networks in parallel.
setsize=60000   Iterate through subsets of at most this size while training;
                larger makes batches take longer.
fpb=0.08        Only train this fraction of the subset per batch, prioritizing
                samples with the most error; larger is slower.

Evaluation parameters
vfraction=0.1   If no validation file is given, split off this fraction of the
                input dataset to use exclusively for validation.
inclusive=f     Use the full training dataset for validation.  Note that
                'evaluate' mode automatically used the input for validation.
cutoffeval=     Set the evaluation cutoff directly; any output above this
                cutoff will be considered positive, and below will be
                considered negative, when evaluating a sample.  This does not 
                affect training other than the printed results and the best 
                network selection.  Overrides fpr, fnr, and crossover.
crossover=1     Set 'cutoffeval' dynamically using the intersection of the
                FPR and FNR curves.  If false positives are 3x as detrimental
                as false negatives, set this at 3.0; if false negatives are 2x
                as bad as false positives, set this at 0.5, etc.
fpr=            Set 'cutoffeval' dynamically using this false positive rate.
fnr=            Set 'cutoffeval' dynamically using this false negative rate.

Activation functions; fractions are relative and don't need to add to 1.
sig=0.6         Fraction of nodes using sigmoid function.
tanh=0.4        Fraction of nodes using tanh function.
rslog=0.02      Fraction of nodes using rotationally symmetric log.
msig=0.02       Fraction of nodes using mirrored sigmoid.
swish=0.0       Fraction of nodes using swish.
esig=0.0        Fraction of nodes using extended sigmoid.
emsig=0.0       Fraction of nodes using extended mirrored sigmoid.
bell=0.0        Fraction of nodes using a bell curve.
max=0.0         Fraction of nodes using a max function (TODO).
final=rslog     Type of function used in the final layer.

Exotic parameters
scan=0          Test this many seeds initially before picking one to train.
scanbatches=1k  Evaluate scanned seeds at this point to choose the best.
simd=f          Use SIMD instructions for greater speed; requires Java 18+.
cutoffbackprop=0.5   Optimize around this point for separating positive and
                     negative results.  Unrelated to cutoffeval.
pem=1.0         Positive error mult; when value>target, multiply the error 
                by this number to adjust the backpropagation penalty.
nem=1.0         Negative error mult; when value<target, multiply the error 
                by this number to adjust the backpropagation penalty.
fpem=10.5       False positive error mult; when target<cutoffbackprop
                value>(cutoffbackprop-spread), multiply error by this.
fnem=10.5       False negative error mult; when target>cutoffbackprop
                value<(cutoffbackprop+spread), multiply error by this.
spread=0.05     Allows applying fnem/fpem multipliers to values that
                are barely onsides, but too close to the cutoff.
epem=0.2        Excess positive error mult; error multiplier when 
                target>cutoff and value>target (overshot the target).
enem=0.2        Error multiplier when target<cutoff and value<target.
epm=0.2         Excess pivot mult; lower numbers give less priority to
                training samples that are excessively positive or negative.
cutoff=         Set both cutoffbackprop and cutoffeval.
ptriage=0.0001  Ignore this fraction of positive samples as untrainable.
ntriage=0.0005  Ignore this fraction of negative samples as untrainable.
anneal=0.003    Randomize weights by this much to avoid local minimae.
annealprob=.225 Probability of any given weight being annealed per batch.
ebs=1           (edgeblocksize) 8x gives best performance with AVX256 in
                sparse networks.  4x may be useful for raw sequence. 

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for train.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("train.sh", args, capture_output)

def translate6frames(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for translate6frames.sh

    Help message:
    Written by Brian Bushnell
Last modified February 17, 2015

Description:  Translates nucleotide sequences to all 6 amino acid frames,
or amino acids to a canonical nucleotide representation.
Input may be fasta or fastq, compressed or uncompressed.

Usage:  translate6frames.sh in_file=<input file> out=<output file>

See also:  callgenes.sh

Optional parameters (and their defaults)

Input parameters:
in_file=<file>       Main input. in_file=stdin.fa will pipe from stdin.
in2=<file>      Input for 2nd read of pairs in a different file.
int=auto        (interleaved) t/f overrides interleaved autodetection.
qin_file=auto        Input quality offset: 33 (Sanger), 64, or auto.
aain_file=f          False if input is nucleotides, true for amino acids.
reads=-1        If positive, quit after processing X reads or pairs.

Output parameters:
out=<file>      Write output here.  'out=stdout.fa' goes to standard out.
out2=<file>     Use this to write 2nd read of pairs to a different file.
overwrite=t     (ow) Grant permission to overwrite files.
append=f        Append to existing files.
ziplevel=2      (zl) Compression level; 1 (min) through 9 (max).
fastawrap=80    Length of lines in fasta output.
qout=auto       Output quality offset: 33 (Sanger), 64, or auto.
aaout=t         False to output nucleotides, true for amino acids.
tag=t           Tag read id with the frame, adding e.g. ' fr1'
frames=6        Only print this many frames.  
                If you already know the sense, set 'frames=3'.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for translate6frames.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("translate6frames.sh", args, capture_output)

def trimcontigs(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for trimcontigs.sh

    Help message:
    Written by Brian Bushnell
Last modified October 1, 2024

Description:  Trims contigs to remove sequence unsupported by read alignment.
The coverage range file can be generated by pileup.sh.

Usage:  trimcontigs.sh in_file=<assembly> ranges=<ranges> out=<trimmed assembly>

Parameters:
in_file=<file>       File containing input assembly.
ranges=<file>   File generated by pileup with the 'ranges' flag.
out=<file>      Destination of clean output assembly.
outdirty=<file> (outd) Optional dirty output containing removed contigs.
gffin_file=<file>    Optional gff file.
gffout=<file>   Modified gff file.
mincov=1        Discard contigs with lower average coverage than this.
minlen=1        Discard contigs shorter than this, after trimming.
trimmin_file=0       Trim the first and last X bases of each sequence.
trimmax=big     Don't trim more than this much on contig ends.
trimextra=5     Trim an additional amount when trimming.
maxuncovered=3  Don't trim where there are at most this many uncovered bases.
break=t         Break contigs where uncovered areas are present.
breaklist=      Optional file to report the list of broken contigs.
skippolyn=t     Don't break around uncovered poly-Ns (scaffold breaks).

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for trimcontigs.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("trimcontigs.sh", args, capture_output)

def unicode2ascii(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for unicode2ascii.sh

    Help message:
    Written by Brian Bushnell
Last modified October 17, 2017

Description:  Replaces unicode and control characters with printable ascii characters.
WARNING - this does not work in many cases, and is not recommended!
It is only retained because there is some situation in which it is needed.

Usage:  unicode2ascii.sh in_file=<file> out=<file>

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for unicode2ascii.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("unicode2ascii.sh", args, capture_output)

def unzip(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for unzip.sh

    Help message:
    Written by Brian Bushnell
Last modified April 25, 2019

Description:  Compresses or decompresses files based on extensions.
This only exists because the syntax and default behavior of many
compression utilities is unintuitive; it is just a wrapper, and
relies on existing executables in the command line (pigz, lbzip, etc.)
Does not delete the input file.
Does not untar files.

Usage:  unzip.sh in_file=<file> out=<file>

Parameters:
in_file=<file>       Input file.
out=<file>      Output file for good reads.
zl=             Set the compression level; 0-9 or 11.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for unzip.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("unzip.sh", args, capture_output)

def vcf2gff(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for vcf2gff.sh

    Help message:
    Written by Brian Bushnell
Last modified August 13, 2019

Description:  Generates a GFF3 from a VCF.

Usage:  vcf2gff.sh in_file=<vcf file> out=<gff file>

Parameters:
in_file=<file>       Input VCF file.
out=<file>      Output GFF file.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for vcf2gff.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("vcf2gff.sh", args, capture_output)

def visualizealignment(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for visualizealignment.sh

    Help message:
    Shell script written by Brian Bushnell
Java code written by Claude.
Last modified May 4, 2025

Description:  Converts a text exploration map from some aligners to an image.
Supports Quantum, Banded, Drifting, Glocal, WaveFront, and MSA9. 

Usage:
visualizealignment.sh <map>
or
visualizealignment.sh <map> <image>

Parameters:
map             Text file of score-space from an aligner.
image           Output name, context sensitive; supports png, bmp, jpg.
                Image name is optional; if absent, .txt will be replaced
                by .png in the input filename.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for visualizealignment.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("visualizealignment.sh", args, capture_output)

def wavefrontaligner(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for wavefrontaligner.sh

    Help message:
    Written by Brian Bushnell
Last modified April 30, 2025

Description:  Aligns a query sequence to a reference using WaveFrontAligner.
The implementation is designed for visualization and is thus very inefficient,
and purely for academic use.
The sequences can be any characters, but N is a special case.
Outputs the identity, rstart, and rstop positions.
Optionally prints a state space exploration map.
This map can be fed to visualizealignment.sh to make an image.

Usage:
wavefrontaligner.sh <query> <ref>
wavefrontaligner.sh <query> <ref> <map>
wavefrontaligner.sh <query> <ref> <map> <iterations>

Parameters:
query           A literal nucleotide sequence or fasta file.
ref             A literal nucleotide sequence or fasta file.
map             Optional output text file for matrix score space.
                Set to null for benchmarking with no visualization.
iterations      Optional integer for benchmarking multiple iterations.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for wavefrontaligner.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("wavefrontaligner.sh", args, capture_output)

def webcheck(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for webcheck.sh

    Help message:
    Written by Brian Bushnell
Last modified December 19, 2018

Description:  Parses a webcheck log.
Input is expected to look like this:
Tue Apr 26 16:40:09 2016|https://rqc.jgi-psf.org/control/|200 OK|0.61

Usage:  webcheck.sh <input files>


Standard parameters:
in_file=<file>       Primary input.  Can use a wildcard (*) if 'in_file=' is omitted.
out=<file>      Summary output; optional.
fail=<file>     Output of failing lines; optional.
invalid=<file>  Output of misformatted lines; optional.
extendedstats=f (es) Print more stats.
overwrite=f     (ow) Set to false to force the program to abort rather than
                overwrite an existing file.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will
                specify 200 megs. The max is typically 85% of physical memory.
-eoom           This flag will cause the process to exit if an out-of-memory
                exception occurs.  Requires Java 8u92+.
-da             Disable assertions.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for webcheck.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("webcheck.sh", args, capture_output)

def wobblealigner(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for wobblealigner.sh

    Help message:
    Written by Brian Bushnell
Last modified May 24, 2025

Description:  Aligns a query sequence to a reference using WobbleAligner.
The sequences can be any characters, but N is a special case.
Outputs the identity, rstart, and rstop positions.
Optionally prints a state space exploration map.
This map can be fed to visualizealignment.sh to make an image.

Usage:
wobblealigner.sh <query> <ref>
wobblealigner.sh <query> <ref> <map>
wobblealigner.sh <query> <ref> <map> <iterations>

Parameters:
query           A literal nucleotide sequence or fasta file.
ref             A literal nucleotide sequence or fasta file.
map             Optional output text file for matrix score space.
                Set to null for benchmarking with no visualization.
iterations      Optional integer for benchmarking multiple iterations.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for wobblealigner.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("wobblealigner.sh", args, capture_output)

def wobbleplusaligner(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for wobbleplusaligner.sh

    Help message:
    Written by Brian Bushnell
Last modified May 24, 2025

Description:  Aligns a query sequence to a reference using WobblePlusAligner3.
The sequences can be any characters, but N is a special case.
Outputs the identity, rstart, and rstop positions.
Optionally prints a state space exploration map.
This map can be fed to visualizealignment.sh to make an image.

Usage:
wobbleplusaligner.sh <query> <ref>
wobbleplusaligner.sh <query> <ref> <map>
wobbleplusaligner.sh <query> <ref> <map> <iterations> <simd>

Parameters:
query           A literal nucleotide sequence or fasta file.
ref             A literal nucleotide sequence or fasta file.
map             Optional output text file for matrix score space.
                Set to null for benchmarking with no visualization.
iterations      Optional integer for benchmarking multiple iterations.
simd            Add this flag to use simd mode.

Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for wobbleplusaligner.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("wobbleplusaligner.sh", args, capture_output)

def Xcalcmem(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    """
    Wrapper for Xcalcmem.sh

    Help message:
    No help message found.

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for Xcalcmem.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    """
    args = _pack_args(kwargs)
    return _run_command("Xcalcmem.sh", args, capture_output)
