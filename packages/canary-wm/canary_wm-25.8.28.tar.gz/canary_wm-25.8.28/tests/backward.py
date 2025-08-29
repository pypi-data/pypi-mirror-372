# Copyright NTESS. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: MIT

from _canary import finder
from _canary.util.filesystem import working_dir


def test_backward_names(tmpdir):
    workdir = tmpdir.strpath
    with working_dir(workdir):
        with open("a.pyt", "w") as fh:
            fh.write("import canary\ncanary.directives.keywords('a', 'b', 'c', 'd', 'e')")
    f = finder.Finder()
    f.add(workdir)
    assert len(f.roots) == 1
    assert workdir in f.roots
    f.prepare()
    files = f.discover()
    [case] = finder.generate_test_cases(files)
    case.work_tree = tmpdir.strpath
    assert case.exec_path == case.path
    assert case.exec_root == case.work_tree
