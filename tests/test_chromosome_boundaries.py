"""Regression tests for chromosome boundaries in 3D-DNA assembly layouts.

Run from the repository root (standard library only):
    python -m unittest discover -s tests -p 'test_chromosome_boundaries.py'
"""

import hashlib
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

# This test exercises the real assembly file operations. Model inference and
# contact-map I/O are unused; mock their imports so no ML stack is required.
spec = importlib.util.spec_from_file_location(
    "autohic_boundary_module",
    Path(__file__).resolve().parents[1] / "src/utils/get_chr_data.py",
)
get_chr_data = importlib.util.module_from_spec(spec)
with patch.dict(
    sys.modules,
    {
        "PIL": Mock(),
        "mmdet.apis": Mock(),
        "src.utils.get_cfg": Mock(),
    },
):
    spec.loader.exec_module(get_chr_data)


class ChromosomeBoundaryTests(unittest.TestCase):
    def test_boundary_cuts_preserve_all_fragments_and_groups(self):
        cases = [
            (
                "reverse_end",
                ">a 1 10\n>b 2 8\n-1\n2\n",
                [10],
                1,
                [10, 8],
                [[-1], [2]],
                None,
            ),
            (
                "forward_end",
                ">a 1 10\n>b 2 8\n1\n2\n",
                [10],
                1,
                [10, 8],
                [[1], [2]],
                None,
            ),
            (
                "existing_join_and_eof",
                ">a 1 10\n>b 2 8\n1 -2\n",
                [10, 18],
                1,
                [10, 8],
                [[1], [-2]],
                None,
            ),
            (
                "forward_internal",
                ">a 1 10\n>b 2 8\n1 2\n",
                [4, 18],
                1,
                [4, 14],
                [[1], [2, 3]],
                [4, 6, 8],
            ),
            (
                "reverse_internal",
                ">a 1 10\n>b 2 8\n-1 2\n",
                [4, 18],
                1,
                [4, 14],
                [[-2], [-1, 3]],
                [6, 4, 8],
            ),
            (
                "repeated_reverse_cuts",
                ">a 1 10\n>b 2 8\n-1 2\n",
                [2, 7, 10],
                1,
                [2, 5, 3, 8],
                [[-3], [-2], [-1], [4]],
                [3, 5, 2, 8],
            ),
            (
                "scaled_map",
                ">a 1 10\n>b 2 8\n1 -2\n",
                [3, 9],
                2,
                [6, 12],
                [[1], [2, -3]],
                [6, 4, 8],
            ),
        ]
        for (
            name,
            assembly,
            ends,
            ratio,
            expected_lengths,
            expected_orders,
            expected_fragments,
        ) in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as work:
                root = Path(work)
                source = root / "source.assembly"
                source.write_text(assembly)
                digest = hashlib.sha256(source.read_bytes()).hexdigest()
                boundaries = root / "chr.txt"
                boundaries.write_text(
                    "Chr\tStart\tEnd\n"
                    + "".join(f"{i + 1}\t0\t{end}\n" for i, end in enumerate(ends))
                )
                output = root / "result.assembly"
                with patch.object(get_chr_data, "get_ratio", return_value=ratio):
                    get_chr_data.divide_chr(
                        str(boundaries),
                        "unused.hic",
                        str(source),
                        str(output),
                        ends[-1],
                    )
                self.assertEqual(
                    hashlib.sha256(source.read_bytes()).hexdigest(), digest
                )
                headers, groups = {}, []
                for line in output.read_text().splitlines():
                    fields = line.split()
                    if line.startswith(">"):
                        headers[int(fields[1])] = int(fields[2])
                    elif fields:
                        groups.append([int(value) for value in fields])
                ids = [abs(value) for group in groups for value in group]
                self.assertEqual(len(ids), len(set(ids)))
                self.assertEqual(set(ids), set(headers))
                self.assertTrue(all(length > 0 for length in headers.values()))
                self.assertEqual(sum(headers.values()), 18)
                self.assertEqual(
                    [sum(headers[abs(v)] for v in group) for group in groups],
                    expected_lengths,
                )
                self.assertEqual(groups, expected_orders)
                if expected_fragments is not None:
                    self.assertEqual(list(headers.values()), expected_fragments)


if __name__ == "__main__":
    unittest.main()
