import unittest
import os

from pylibsufr import *

class TestSuffixArray(unittest.TestCase):

    def test_create(self):
        sequence_delimiter = ord('%')
        seq_data = read_sequence_file("data/inputs/3.fa", sequence_delimiter)
        outfile = "data/inputs/3.sufr"
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
        meta = suffix_array.metadata()
        self.assertEqual(meta.text_len, 113)
        self.assertEqual(meta.len_suffixes, 101)

    def test_bisect(self):
        suffix_array = SuffixArray.read("data/inputs/3.sufr", True)
        # subtest 1 - a single query without a prefix result should search the whole array for suffixes beginning with A.
        opt_sans_pfx = BisectOptions(
            queries = ['A'],
            max_query_len = None,
            low_memory = False,
            prefix_result = None,
        )
        
        res_sans_pfx = suffix_array.bisect(opt_sans_pfx)
        
        observed_res = [
            (r.query_num, r.query, r.count, r.first_position, r.last_position, r.lcp)
            for r in res_sans_pfx
        ]
        expected_res = [
            (0, 'A', 27, 1, 27, 1),
        ]
        self.assertEqual(observed_res, expected_res)

        # subtest 2 - recursively, search for suffixes AC and AT within the range of the first result.
        opt_with_pfx = BisectOptions(
            queries = ['C','T'],
            max_query_len = None,
            low_memory = False,
            prefix_result = res_sans_pfx[0],
        )
        
        res_with_pfx = suffix_array.bisect(opt_with_pfx)
        
        observed_res = [
            (r.query_num, r.query, r.count, r.first_position, r.last_position, r.lcp)
            for r in res_with_pfx
        ]
        expected_res = [
            (0, 'C', 4, 12, 15, 2),
            (1, 'T', 5, 23, 27, 2),
        ]
        self.assertEqual(observed_res, expected_res)

        # subtest 3 - with secondary prefix, search for suffixes ACG, ACA.
        opt_with_pfx2 = BisectOptions(
            queries = ['G','A'],
            max_query_len = None,
            low_memory = False,
            prefix_result = res_with_pfx[0],
        )
        
        res_with_pfx2 = suffix_array.bisect(opt_with_pfx2)
        
        observed_res = [
            (r.query_num, r.query, r.count, r.first_position, r.last_position, r.lcp)
            for r in res_with_pfx2
        ]
        expected_res = [
            (0, 'G', 1, 13, 13, 3),
            (1, 'A', 0, 0, 0, 0,),
        ]
        self.assertEqual(observed_res, expected_res)

    def test_bisect2(self):
        suffix_array = SuffixArray.read("data/inputs/test.sufr", True)
        full_query = "ILEKL"
        counts = [64,10,2,1,0]
        prefix_result = None
        for i in range(len(full_query)):
            query_chr = full_query[i]
            query_pfx = full_query[:i + 1]
            bisect_result = suffix_array.bisect(BisectOptions(queries=[query_chr], prefix_result=prefix_result))[0]
            count_result = suffix_array.count(CountOptions([query_pfx]))[0]
            # print(f"[{i}]:\n{query_pfx} => {count_result.count}\n{query_chr} => {bisect_result.count} {bisect_result.lcp}")
            self.assertEqual(
                count_result.count,
                bisect_result.count)
            self.assertEqual(
                counts[i],
                bisect_result.count)
            if not(prefix_result is None):
                self.assertLessEqual(bisect_result.count, prefix_result.count)
            prefix_result = bisect_result

    def test_count(self):
        suffix_array = SuffixArray.read("data/inputs/1.sufr", True)
        count_args = CountOptions(
            queries = ["AC", "GG", "CG"],
            max_query_len = None,
            low_memory = True
        )
        res = [(r.query_num, r.query, r.count) for r in suffix_array.count(count_args)]
        expected = [
            (0, "AC", 2),
            (1, "GG", 0),
            (2, "CG", 2),
        ]
        self.assertEqual(res, expected)

    def test_extract(self):
        suffix_array = SuffixArray.read("data/inputs/1.sufr", True)
        extract_args = ExtractOptions(
            queries = ["CGT", "GG"],
            max_query_len = None,
            low_memory = True,
            prefix_len = 1,
            suffix_len = None,
        )
        res = [(r.query_num, r.query, [(s.suffix, s.rank, s.sequence_name, s.sequence_start, s.sequence_range, s.suffix_offset) 
            for s in r.sequences]) for r in suffix_array.extract(extract_args)]
        expected = [
            (0, "CGT", [
                (7, 3, "1", 0, (6, 11), 1),
                (1, 4, "1", 0, (0,11), 1)]),
            (1, "GG", [])
        ]
        self.assertEqual(res, expected)

    def test_list(self):
        suffix_array = SuffixArray.read("data/inputs/1.sufr", True)
        outfile = ".list.out"
        list_opts = ListOptions(
            ranks = [],
            show_rank = True,
            show_suffix = True,
            show_lcp = True,
            len = None,
            number = None,
            output = outfile
        )
        suffix_array.list(list_opts)
        expected = '\n'.join([
            " 0 10  0 $",
            " 1  6  0 ACGT$",
            " 2  0  4 ACGTNNACGT$",
            " 3  7  0 CGT$",
            " 4  1  3 CGTNNACGT$",
            " 5  8  0 GT$",
            " 6  2  2 GTNNACGT$",
            " 7  9  0 T$",
            " 8  3  1 TNNACGT$",
            "",
        ])
        with open(outfile, 'r') as f:
            res = f.read()
        self.assertEqual(res, expected)
        os.remove(outfile)

    def test_locate(self):
        suffix_array = SuffixArray.read("data/inputs/1.sufr", True)
        locate_opts = LocateOptions(
            queries = ["ACG", "GGC"],
            max_query_len = None,
            low_memory = True,
        )
        res = [(r.query_num, r.query, [(p.suffix, p.rank, p.sequence_name, p.sequence_position)
            for p in r.positions]) for r in suffix_array.locate(locate_opts)]
        expected = [
            (0, "ACG", [
                (6, 1, "1", 6),
                (0, 2, "1", 0)]),
            (1, "GGC", [])
        ]
        self.assertEqual(res, expected)

    def test_metadata(self):
        suffix_array = SuffixArray.read("data/inputs/1.sufr", True)
        meta = suffix_array.metadata()
        self.assertEqual(meta.filename, "data/inputs/1.sufr")
        self.assertEqual(meta.file_size, 172)
        self.assertEqual(meta.file_version, 6)
        self.assertEqual(meta.is_dna, True)
        self.assertEqual(meta.allow_ambiguity, False)
        self.assertEqual(meta.ignore_softmask, False)
        self.assertEqual(meta.text_len, 11)
        self.assertEqual(meta.len_suffixes, 9)
        self.assertEqual(meta.num_sequences, 1)
        self.assertEqual(meta.sequence_starts, [0])
        self.assertEqual(meta.sequence_names, ["1"])
        self.assertEqual(meta.sort_type, "MaxQueryLen(0)")
        
    def test_read(self):
        suffix_array = SuffixArray.read("data/inputs/1.sufr", True)
        
    def test_write_and_read(self):
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
        suffix_array = SuffixArray.read(outpath)
        meta = suffix_array.metadata()
        self.assertEqual(outpath, outfile)
        self.assertEqual(meta.text_len, 113)
        self.assertEqual(meta.len_suffixes, 101)
        os.remove(outfile)

    def test_string_at(self):
        """deprecated."""
        pass

if __name__ == '__main__':
    unittest.main()
