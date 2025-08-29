# Copyright 2019 StreamSets Inc.

import pytest

from streamsets.sdk.utils import Version


# Version Parameter: version string, tuple of expected parsed values
@pytest.mark.parametrize('version', (['3.0.0.0', (None, None, [3, 0, 0, 0], None, None)],
                                     ['3.0.1', (None, None, [3, 0, 1, 0], None, None)],
                                     ['12.0', (None, None, [12, 0, 0, 0], None, None)],
                                     ['0.0.0', (None, None, [0, 0, 0, 0], None, None)],
                                     ['1.12.24', (None, None, [1, 12, 24, 0], None, None)],
                                     ['3.0.1-SNAPSHOT', (None, None, [3, 0, 1, 0], '-', 'SNAPSHOT')],
                                     ['3.8.2-RC2', (None, None, [3, 8, 2, 0], '-', 'RC2')],
                                     ['3.8.2RC2', (None, None, [3, 8, 2, 0], None, 'RC2')],
                                     ['3.8.2SNAPSHOT', (None, None, [3, 8, 2, 0], None, 'SNAPSHOT')],
                                     [3.8, (None, None, [3, 8, 0, 0], None, None)],
                                     [3, (None, None, [3, 0, 0, 0], None, None)]))
def test_version_parser(version):
    version_string, values = version
    assert values == Version(version_string)._tuple


# Version Parameter: result, version string 1, version string 2
@pytest.mark.parametrize('version', ([True, '3.0.0.0', '3.0'],
                                     [True, '3.0.1', '3.0.1.0'],
                                     [True, '3.0.1', '3.0.1.0'],
                                     [False, '3.1.0', '3.0.1'],
                                     [True, '3.8.0-latest', '3.8-SNAPSHOT']))
def test_version_equals(version):
    result, version_string1, version_string2 = version
    assert (Version(version_string1) == Version(version_string2)) == result


# Version Parameter: result, version string 1, version string 2
@pytest.mark.parametrize('version', ([True, '3.0.0.0', '3.0.0.1'],
                                     [True, '3.0.1', '3.0.2.0'],
                                     [True, '3.0.0', '12.0.1.0'],
                                     [False, '3.5.1', '3.5.0'],
                                     [True, '3.8-latest', '3.8.1-SNAPSHOT'],))
def test_version_lt(version):
    result, version_string1, version_string2 = version
    assert (Version(version_string1) < Version(version_string2)) == result
