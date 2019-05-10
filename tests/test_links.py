# -*- coding: utf-8 -*-

# This file is part of Exdir, the Experimental Directory Structure.
#
# Copyright 2019 Mikkel Lepperød
#
# License: MIT, see "LICENSE" file for the full license terms.
#
# This file contains code from h5py, a Python interface to the HDF5 library,
# licensed under a standard 3-clause BSD license
# with copyright Andrew Collette and contributors.
# See http://www.h5py.org and the "3rdparty/h5py-LICENSE" file for details.

import exdir
import pytest
import numpy as np
try:
    import ruamel_yaml as yaml
except ImportError:
    import ruamel.yaml as yaml


def test_softlinks(setup_teardown_file):
    """ Broken softlinks are contained, but their members are not """
    f = setup_teardown_file[3]
    g = exdir.File(setup_teardown_file[2] / 'mongoose.exdir')
    f.create_group('mongoose')
    g.create_group('mongoose')
    f.create_group('grp')
    f['/grp/soft'] = exdir.SoftLink('/mongoose')
    f['/grp/external'] = exdir.ExternalLink('mongoose.exdir', '/mongoose')
    assert '/grp/soft' in f
    assert '/grp/soft/something' not in f
    assert '/grp/external' in f
    assert '/grp/external/something' not in f


# def test_get_link(setup_teardown_file):
#     """ Get link values """
#     f = setup_teardown_file[3]
#     g = exdir.File(setup_teardown_file[0] / 'mongoose.exdir')
#     f.create_group('mongoose')
#     g.create_group('mongoose')
#     sl = SoftLink('/mongoose')
#     el = ExternalLink('somewhere.hdf5', 'mongoose')
#
#     f['soft'] = sl
#     f['external'] = el
#
#     out_sl = f.get('soft', getlink=True)
#     out_el = f.get('external', getlink=True)
#
#     #TODO: redo with SoftLink/ExternalLink built-in equality
#     assertIsInstance(out_sl, SoftLink)
#     assert out_sl == sl
#     assertIsInstance(out_el, ExternalLink)
#     assert out_el == el
#
#
# Feature: Create and manage soft links with the high-level interface
def test_spath(setup_teardown_file):
    """ SoftLink directory attribute """
    sl = exdir.SoftLink('/foo')
    assert sl.path == '/foo'


# def test_srepr(setup_teardown_file):
#     """ SoftLink path repr """
#     sl = SoftLink('/foo')
#     assertIsInstance(repr(sl), six.string_types)


def test_create(setup_teardown_file):
    """ Create new soft link by assignment """
    f = setup_teardown_file[3]
    g = f.create_group('new')
    sl = exdir.SoftLink('/new')
    f['alias'] = sl
    g2 = f['alias']
    assert g == g2


def test_exc(setup_teardown_file):
    """ Opening dangling soft link results in KeyError """
    f = setup_teardown_file[3]
    f['alias'] = exdir.SoftLink('new')
    with pytest.raises(KeyError):
        f['alias']
#
#
# # Feature: Create and manage external links
# def test_epath(setup_teardown_file):
#     """ External link paths attributes """
#     el = ExternalLink('foo.hdf5', '/foo')
#     assertEqual(el.filename, 'foo.hdf5')
#     assertEqual(el.path, '/foo')
#
# def test_erepr(setup_teardown_file):
#     """ External link repr """
#     el = ExternalLink('foo.hdf5','/foo')
#     assertIsInstance(repr(el), six.string_types)
#
# def test_create(setup_teardown_file):
#     """ Creating external links """
#     f['ext'] = ExternalLink(ename, '/external')
#     grp = f['ext']
#     ef = grp.file
#     assertNotEqual(ef, f)
#     assertEqual(grp.name, '/external')
#
# def test_exc(setup_teardown_file):
#     """ KeyError raised when attempting to open broken link """
#     f['ext'] = ExternalLink(ename, '/missing')
#     with assertRaises(KeyError):
#         f['ext']
#
# # I would prefer IOError but there's no way to fix this as the exception
# # class is determined by HDF5.
# def test_exc_missingfile(setup_teardown_file):
#     """ KeyError raised when attempting to open missing file """
#     f['ext'] = ExternalLink('mongoose.hdf5','/foo')
#     with assertRaises(KeyError):
#         f['ext']
#
# def test_close_file(setup_teardown_file):
#     """ Files opened by accessing external links can be closed
#     Issue 189.
#     """
#     f['ext'] = ExternalLink(ename, '/')
#     grp = f['ext']
#     f2 = grp.file
#     f2.close()
#     assertFalse(f2)
#
#
# def test_unicode_encode(setup_teardown_file):
#     """
#     Check that external links encode unicode filenames properly
#     Testing issue #732
#     """
#     ext_filename = os.path.join(mkdtemp(), u"α.hdf5")
#     with File(ext_filename, "w") as ext_file:
#         ext_file.create_group('external')
#     f['ext'] = ExternalLink(ext_filename, '/external')
#
#
# def test_unicode_decode(setup_teardown_file):
#     """
#     Check that external links decode unicode filenames properly
#     Testing issue #732
#     """
#     ext_filename = os.path.join(mkdtemp(), u"α.hdf5")
#     with File(ext_filename, "w") as ext_file:
#         ext_file.create_group('external')
#         ext_file["external"].attrs["ext_attr"] = "test"
#     f['ext'] = ExternalLink(ext_filename, '/external')
#     assertEqual(f["ext"].attrs["ext_attr"], "test")
#
#
# def test_unicode_hdf5_path(setup_teardown_file):
#     """
#     Check that external links handle unicode hdf5 paths properly
#     Testing issue #333
#     """
#     ext_filename = os.path.join(mkdtemp(), "external.hdf5")
#     with File(ext_filename, "w") as ext_file:
#         ext_file.create_group(u'α')
#         ext_file[u"α"].attrs["ext_attr"] = "test"
#     f['ext'] = ExternalLink(ext_filename, u'/α')
#     assertEqual(f["ext"].attrs["ext_attr"], "test")