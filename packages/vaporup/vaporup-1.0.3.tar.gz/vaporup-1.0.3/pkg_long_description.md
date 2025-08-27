VaporUp is an actively developed and maintained version of [Vapor](https://bio.tools/vapor), a tool for classification of Influenza samples from raw short read sequence data. From a fasta file of (preferably thousands of) full-length viral reference sequences for a given segment, and a set of reads, VaporUp attempts to identify the reference that is closest to the sample strain.


**Example usage**

Test inputs are provided in the tests folder of the [development repo](https://github.com/wm75/vaporup), which also has more detailed usage instructions.

With VaporUp installed you can run:

    vapor.py -fq tests/test_reads.fq -fa tests/HA_sample.fa

which should yield:

    0.9782480893592005  186719.0    1701    109.77013521457965  1000    >cds:ADO12563 A/Chile/3935/2009 2009/07/07 HA H1N1 Human

Where the tab-delimited fields correspond to: approximate fraction of query bases found in reads; total score; query length; mean score; number of reads surviving culling; query description.


**Acknowledgments**

Original author of VAPOR: Joel Southgate

