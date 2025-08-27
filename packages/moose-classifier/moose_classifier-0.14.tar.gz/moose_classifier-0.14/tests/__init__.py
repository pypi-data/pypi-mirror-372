import sys
import logging
import os
import shutil
import unittest

# set up logging for unit tests
verbosity_flag = [x for x in sys.argv if x.startswith('-v')]
verbosity = (verbosity_flag[0] if verbosity_flag else '').count('v')

loglevel = {
    0: logging.WARNING,
    1: logging.INFO,
    2: logging.DEBUG,
}.get(verbosity, logging.DEBUG)

if verbosity > 1:
    logformat = '%(levelname)s %(module)s %(lineno)s %(message)s'
else:
    logformat = '%(message)s'

logging.basicConfig(stream=sys.stdout, format=logformat, level=loglevel)
log = logging.getLogger(__name__)

# module data
datadir = 'testfiles'
outputdir = 'test_output'

if not os.path.isdir(outputdir):
    os.mkdir(outputdir)


class TestBase(unittest.TestCase):
    """
    Base class for unit tests with methods for defining output
    directories based on method name.
    """

    outputdir = outputdir

    def mkoutdir(self, clobber=True):
        """
        Create outdir as outpudir/module.class.method (destructively
        if clobber is True).
        """

        funcname = '.'.join(self.id().split('.')[-3:])
        outdir = os.path.join(self.outputdir, funcname)

        if clobber:
            shutil.rmtree(outdir, ignore_errors=True)
            os.mkdir(outdir)
        elif not os.path.isdir(outdir):
            os.mkdir(outdir)

        return outdir

    def data(self, fname):
        return os.path.join(datadir, fname)
