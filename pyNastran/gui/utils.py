from __future__ import print_function
from six.moves import urllib
import os

import numpy as np
from numpy import loadtxt
import pyNastran

def check_for_newer_version():
    """
    Checks to see if a newer version of pyNastran has been released.
    Only checks this for the GUI.
    """
    is_newer = False
    version_current = pyNastran.__version__
    target_url = 'https://raw.githubusercontent.com/SteveDoyle2/pyNastran/master/README.md'
    try:
        # it's a file like object and works just like a file
        # import urllib2
        # data = urllib.request.urlopen(target_url)
        data = urllib.request.urlopen(target_url)
    except: #  urllib2.URLError
        #print(help(urllib))
        #raise
        return None, None, False
    for btye_line in data: # files are iterable
        line_lower = btye_line.lower().decode('utf-8')
        if 'has been released' in line_lower:
            sline = line_lower.split()
            version_latest = [slot for slot in sline if slot.startswith('v')][0][1:]
            break

    is_dev = False
    if 'dev' in version_current:
        is_dev = True

    major, minor, rev = version_current.split('+')[0].split('.')
    major = int(major)
    minor = int(minor)
    rev = int(rev)
    tuple_current_version = (major, minor, rev)

    major, minor, rev = version_latest.split('_')[0].split('.')
    major = int(major)
    minor = int(minor)
    rev = int(rev)
    tuple_latest_version = (major, minor, rev)
    #print('tuple_latest_version = %s' % str(tuple_latest_version))  # (0,7,2)
    #print('tuple_current_version = %s' % str(tuple_current_version))  # (0,8,0)

    #is_newer = True
    if tuple_current_version < tuple_latest_version or (is_dev and tuple_current_version <= tuple_latest_version):
        print('pyNastran %s is now availible; current=%s' % (version_latest, version_current))
        is_newer = True
    #print('*pyNastran %s is now availible; current=%s' % (version_latest, version_current))
    return version_latest, version_current, is_newer


def load_csv(out_filename):
    """
    The GUI CSV loading function.

    Considers:
      - extension in determining how to load a file (e.g. commas or not)
      - header line of file for information regarding data types
    """
    ext = os.path.splitext(out_filename)[1].lower()
    if ext not in ['.csv', '.dat', '.txt']:
        raise NotImplementedError('extension=%r is not supported (use .dat, .txt, or .csv)' % ext)

    with open(out_filename, 'r') as file_obj:
        header_line = file_obj.readline().strip()
        if not header_line.startswith('#'):
            msg = 'Expected file of the form:\n'
            if ext in ['.dat', '.txt']:
                msg += '# var1 var2\n'
                msg += '1 2\n'
                msg += '3 4\n'
            elif ext == '.csv':
                msg += '# var1, var2\n'
                msg += '1, 2\n'
                msg += '3, 4\n'
            else:
                msg = 'extension=%r is not supported (use .dat, .txt, or .csv)' % ext
                raise NotImplementedError(msg)
            raise SyntaxError(msg)

        header_line = header_line.lstrip('# \t').strip()
        if ext in ['.dat', '.txt']:
            headers = header_line.split(' ')
        elif ext == '.csv':
            headers = header_line.split(',')
        else:
            msg = 'extension=%r is not supported (use .dat, .txt, or .csv)' % ext
            raise NotImplementedError(msg)


        fmt_dict = {}
        names = []
        dtype_fmts = []
        for iheader, header in enumerate(headers):
            # TODO: works for making a \n, but screws up the sidebar
            #       and scale
            header2 = header.strip()#.replace('\\n', '\n')
            dtype_fmt = 'float'

            str_fmt = '%.3f'
            if header2.endswith(')') and '%' in header2:
                header2_temp, fmt_temp = header2[:-1].rsplit('(', 1)
                header2_temp = header2_temp.strip()
                fmt = fmt_temp.strip()
                print('fmt_temp = %r' % fmt_temp)
                #('S1', 'i4', 'f4')
                if '%' in fmt:
                    #fmt_temp = fmt_temp.replace('%', '%%')
                    if 'i' in fmt:
                        fmt % 5
                        dtype_fmt = 'int32'
                        str_fmt = '%i'

                    elif 'g' in fmt or 'e' in fmt or 'f' in fmt or 's' in fmt:
                        dtype_fmt = 'float32'
                        str_fmt = fmt
                    else:
                        raise TypeError('iheader=%s header=%r fmt=%r' % (iheader, header2, fmt))
                else:
                    # default to float32
                    dtype_fmt = 'float32'
            else:
                dtype_fmt = 'float32'
                header2_temp = header2
                print('header2 = %r' % header2)

            names.append(header2_temp)
            dtype_fmts.append(dtype_fmt)
            fmt_dict[header2_temp] = str_fmt

        if ext in ['.dat', '.txt']:
            delimiter = None
        elif ext == '.csv':
            delimiter = ','
        else:
            raise NotImplementedError('extension=%r is not supported (use .dat, .txt, or .csv)' % ext)

        dtype = {
            'names': tuple(names),
            'formats': tuple(dtype_fmts)
        }
        A = loadtxt(file_obj, dtype=dtype, delimiter=delimiter)

    return A, fmt_dict, names


def load_user_geom(fname):
    with open(fname, 'r') as f:
        lines = f.readlines()

    grid_ids = []
    xyz = []
    bars = []
    tris = []
    quads = []
    lines2 = []
    for line in lines:
        line2 = line.strip().split('#')[0].upper()
        if line2:
            sline = line2.split(',')
            if line2.startswith('GRID'):
                assert len(sline) == 5, sline
                grid_ids.append(sline[1])
                xyz.append(sline[2:])
            elif line2.startswith('BAR'):
                assert len(sline) == 4, sline
                bars.append(sline[1:])
            elif line2.startswith('TRI'):
                assert len(sline) == 5, sline
                tris.append(sline[1:])
            elif line2.startswith('QUAD'):
                assert len(sline) == 6, sline
                quads.append(sline[1:])

    grid_ids = np.array(grid_ids, dtype='int32')
    xyz = np.array(xyz, dtype='float32')
    tris = np.array(tris, dtype='int32')
    quads = np.array(quads, dtype='int32')
    bars = np.array(bars, dtype='int32')
    return grid_ids, xyz, bars, tris, quads

if __name__ == '__main__':
    check_for_newer_version(window=None)

