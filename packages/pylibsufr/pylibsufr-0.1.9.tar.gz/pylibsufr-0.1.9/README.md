# pylibsufr
Pyo3 bindings for the Rust crate libsufr: https://github.com/TravisWheelerLab/sufr/tree/main/libsufr

Implements the `libsufr::suffix_array::SuffixArray` API.

Suffix arrays can be created and loaded into memory, and used to retrieve various information about query strings.

```
# Create a suffix array and read it into memory
sequence_delimiter = ord('%')
seq_data = read_sequence_file("data/inputs/3.fa", sequence_delimiter)
outfile = "3.sufr"
builder_args = SufrBuilderArgs(
    text = seq_data.seq(),
    path = outfile,
    sequence_starts = seq_data.start_positions(),
    sequence_names= seq_data.sequence_names(),
    low_memory = True,
    max_query_len = None,
    is_dna = True,
    allow_ambiguity = False,
    ignore_softmask = True,
    num_partitions = 16,
    seed_mask = None,
    random_seed = 42,
)
suffix_array = SuffixArray(builder_args)
```

```
# Write a suffix array, then read it afterwards
sequence_delimeter = ord('%')
seq_data = read_sequence_file("data/inputs/3.fa", sequence_delimeter)
outfile = "3.sufr"
builder_args = SufrBuilderArgs(
    text = seq_data.seq(),
    path = outfile,
    sequence_starts = seq_data.start_positions(),
    sequence_names= seq_data.sequence_names(),
    low_memory = True,
    max_query_len = None,
    is_dna = True,
    allow_ambiguity = False,
    ignore_softmask = True,
    num_partitions = 16,
    seed_mask = None,
    random_seed = 42,
)
outpath = SuffixArray.write(builder_args)
assert outpath == outfile
# ...
suffix_array = SuffixArray.read(outpath)
```

Once a `SuffixArray` object has been created, it can be queried using the `*Options` types.

```
# Count the occurrences of queries in the suffix array
count_args = CountOptions(
    queries = ["AC", "GG", "CG"],
    max_query_len = None,
    low_memory = True
)
res = [(r.query_num, r.query, r.count) for r in suffix_array.count(count_args)] 
```

```
# Extract the suffixes matching given queries
extract_args = ExtractOptions(
    queries = ["CGT", "GG"],
    max_query_len = None,
    low_memory = True,
    prefix_len = 1,
    suffix_len = None,
)
results = [(r.query_num, r.query, r.sequences) for r in suffix_array.extract(extract_args)]
result_seqs = [[(s.suffix, s.rank, s.sequence_name, s.sequence_start, s.sequence_range, s.suffix_offset) 
    for s in r_sequences] for (_, __, r_sequences) in res]
```

```
# Locate the suffixes matching given queries
locate_opts = LocateOptions(
    queries = ["ACG", "GGC"],
    max_query_len = None,
    low_memory = True,
)
results = [(r.query_num, r.query, [(p.suffix, p.rank, p.sequence_name, p.sequence_position)
    for p in r.positions]) for r in suffix_array.locate(locate_opts)]
```

See the libsufr docs for more information: https://docs.rs/libsufr/latest/libsufr
