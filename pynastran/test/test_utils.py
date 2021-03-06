from __future__ import print_function
from six import PY2
from six.moves import zip
#import os
import unittest

from pyNastran.bdf.utils import parse_patran_syntax, parse_patran_syntax_dict
from numpy import array, array_equal, setdiff1d


class TestBdfUtils(unittest.TestCase):
    def test_bdf_utils_01(self):
        msg = '1:10  14:20:2  50:40:-1'
        output = parse_patran_syntax(msg, pound=None)
        expected = array(
            [1, 2, 3, 4, 5, 6, 7, 8,9 , 10,
             14, 16, 18, 20,
             40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50]
        )
        error_msg = 'expected equal; A-B=%s; B-A=%s' % (
            setdiff1d(output, expected), setdiff1d(expected, output))
        assert array_equal(output, expected), error_msg

        msg = '1:#'
        output = parse_patran_syntax(msg, pound=5)
        assert array_equal(output, [1, 2, 3, 4, 5])

        msg = '#:1'
        with self.assertRaises(ValueError):
            output = parse_patran_syntax(msg, pound=None)
        #assert array_equal(output, [1, 2, 3, 4, 5])

        msg = '1:#'
        output = parse_patran_syntax(msg, pound='5')
        assert array_equal(output, [1, 2, 3, 4, 5])

        # should this raise an error?
        msg = '#:1'
        #with self.assertRaises(ValueError):
        output = parse_patran_syntax(msg, pound='5')

    def test_bdf_utils_02(self):
        msg = 'n 1:10  14:20:2  50:40:-1 e 10 20'
        expected_nodes = array(
            [1, 2, 3, 4, 5, 6, 7, 8,9 , 10,
             14, 16, 18, 20,
             40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50]
        )
        expected_elements = array([10, 20])

        output_dict = parse_patran_syntax_dict(msg, pound_dict=None)
        assert array_equal(output_dict['n'], expected_nodes)
        assert array_equal(output_dict['e'], expected_elements)


        # messing with the order a bit
        msg = 'n 1:#  e 2:#:4 junk 1 7 12:#:2 3'
        expected_nodes = array([1, 2, 3, 4, 5])
        expected_elements = array([2, 6, 10, 14])
        expected_junk = array([1, 3, 7, 12, 14, 16, 18, 20])
        pound_dict = {
            'n' : 5,
            'e' : 14,
            'junk' : 20.,
        }

        output_dict = parse_patran_syntax_dict(msg, pound_dict=pound_dict)
        assert array_equal(output_dict['n'], expected_nodes)
        assert array_equal(output_dict['e'], expected_elements)

        error_msg = 'expected equal; A-B=%s; B-A=%s' % (
            setdiff1d(expected_junk, output_dict['junk']), setdiff1d(output_dict['junk'], expected_junk))
        assert array_equal(output_dict['junk'], expected_junk), error_msg


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
