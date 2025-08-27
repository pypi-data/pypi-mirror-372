"""
Test classifier
"""
import classify
import filecmp
import logging
import os
import sys

from tests import TestBase, datadir as datadir


class TestClassify(TestBase):

    def main(self, arguments):
        classify.main(str(a) for a in arguments)

    log_info = 'classify {}'

    copy_numbers = os.path.join(datadir, 'rrnDB_16S_copy_num.csv.bz2')
    rank_thresholds = os.path.join(datadir, 'rank_thresholds.csv')

    thisdatadir = os.path.join(datadir, 'TestClassify')

    def test01(self):
        """
        Minimal inputs.
        """

        this_test = sys._getframe().f_code.co_name

        thisdatadir = self.thisdatadir

        taxonomy = os.path.join(thisdatadir, 'taxonomy.csv.bz2')
        seq_info = os.path.join(thisdatadir, 'seq_info.csv.bz2')
        blast = os.path.join(thisdatadir, 'blast.csv.bz2')

        outdir = self.mkoutdir()

        classify_out = os.path.join(outdir, 'classifications.csv.bz2')
        details_out = os.path.join(outdir, 'details.csv.bz2')

        classify_ref = os.path.join(
            thisdatadir, this_test, 'classifications.csv.bz2')
        details_ref = os.path.join(
            thisdatadir, this_test, 'details.csv.bz2')

        args = [
            '--columns', 'qseqid,sseqid,pident,qstart,qend,qlen,qcovs',
            '--details-out', details_out,
            '--lineages', taxonomy,
            '--out', classify_out,
            '--rank-thresholds', self.rank_thresholds,
            '--seq-info', seq_info,
            blast]

        logging.info(self.log_info.format(' '.join(map(str, args))))

        self.main(args)

        self.assertTrue(filecmp.cmp(classify_ref, classify_out))
        self.assertTrue(filecmp.cmp(details_ref, details_out))

    def test16(self):
        """
        test [no blast result] for missing sequences in specimen_map
        """

        this_test = sys._getframe().f_code.co_name

        thisdatadir = self.thisdatadir

        taxonomy = os.path.join(thisdatadir, 'taxonomy.csv.bz2')
        seq_info = os.path.join(thisdatadir, 'seq_info.csv.bz2')
        blast = os.path.join(thisdatadir, 'blast.csv.bz2')
        specimen_map = os.path.join(thisdatadir, 'map_single.csv.bz2')

        outdir = self.mkoutdir()

        classify_out = os.path.join(outdir, 'classifications.csv.bz2')
        details_out = os.path.join(outdir, 'details.csv.bz2')

        classify_ref = os.path.join(
            thisdatadir, this_test, 'classifications.csv.bz2')
        details_ref = os.path.join(
            thisdatadir, this_test, 'details.csv.bz2')

        args = [
            '--columns', 'qseqid,sseqid,pident,qstart,qend,qlen,qcovs',
            '--details-out', details_out,
            '--lineages', taxonomy,
            '--out', classify_out,
            '--rank-thresholds', self.rank_thresholds,
            '--seq-info', seq_info,
            '--specimen-map', specimen_map,
            blast]

        logging.info(self.log_info.format(' '.join(map(str, args))))

        self.main(args)

        self.assertTrue(filecmp.cmp(classify_ref, classify_out))
        self.assertTrue(filecmp.cmp(details_ref, details_out))

    def test02(self):
        """
        Include weights.
        """

        this_test = sys._getframe().f_code.co_name

        thisdatadir = self.thisdatadir

        taxonomy = os.path.join(thisdatadir, 'taxonomy.csv.bz2')
        seq_info = os.path.join(thisdatadir, 'seq_info.csv.bz2')
        blast = os.path.join(thisdatadir, 'blast.csv.bz2')
        specimen_map = os.path.join(
            thisdatadir, this_test, 'map_single.csv.bz2')

        outdir = self.mkoutdir()

        classify_out = os.path.join(outdir, 'classifications.csv.bz2')
        details_out = os.path.join(outdir, 'details.csv.bz2')

        classify_ref = os.path.join(
            thisdatadir, this_test, 'classifications.csv.bz2')
        details_ref = os.path.join(
            thisdatadir, this_test, 'details.csv.bz2')

        args = [
            '--columns', 'qseqid,sseqid,pident,qstart,qend,qlen,qcovs',
            '--details-out', details_out,
            '--out', classify_out,
            '--lineages', taxonomy,
            '--rank-thresholds', self.rank_thresholds,
            '--seq-info', seq_info,
            '--specimen-map', specimen_map,
            blast]

        logging.info(self.log_info.format(' '.join(map(str, args))))

        self.main(args)

        self.assertTrue(filecmp.cmp(classify_ref, classify_out))
        self.assertTrue(filecmp.cmp(details_ref, details_out))

    def test03(self):
        """
        Include specimen-map.
        """

        this_test = sys._getframe().f_code.co_name

        thisdatadir = self.thisdatadir

        specimen_map = os.path.join(thisdatadir, 'map.csv.bz2')
        taxonomy = os.path.join(thisdatadir, 'taxonomy.csv.bz2')
        seq_info = os.path.join(thisdatadir, 'seq_info.csv.bz2')
        blast = os.path.join(thisdatadir, 'blast.csv.bz2')

        outdir = self.mkoutdir()

        classify_out = os.path.join(outdir, 'classifications.csv.bz2')
        details_out = os.path.join(outdir, 'details.csv.bz2')

        classify_ref = os.path.join(
            thisdatadir, this_test, 'classifications.csv.bz2')
        details_ref = os.path.join(
            thisdatadir, this_test, 'details.csv.bz2')

        args = [
            '--columns', 'qseqid,sseqid,pident,qstart,qend,qlen,qcovs',
            '--details-out', details_out,
            '--lineages', taxonomy,
            '--out', classify_out,
            '--rank-thresholds', self.rank_thresholds,
            '--seq-info', seq_info,
            '--specimen-map', specimen_map,
            blast]

        logging.info(self.log_info.format(' '.join(map(str, args))))

        self.main(args)

        self.assertTrue(filecmp.cmp(classify_ref, classify_out))
        self.assertTrue(filecmp.cmp(details_ref, details_out))

    def test06(self):
        """
        All together
        """

        this_test = sys._getframe().f_code.co_name

        thisdatadir = self.thisdatadir

        specimen_map = os.path.join(thisdatadir, this_test, 'map.csv.bz2')
        taxonomy = os.path.join(thisdatadir, 'taxonomy.csv.bz2')
        seq_info = os.path.join(thisdatadir, 'seq_info.csv.bz2')
        blast = os.path.join(thisdatadir, 'blast.csv.bz2')

        outdir = self.mkoutdir()

        classify_out = os.path.join(outdir, 'classifications.csv.bz2')
        details_out = os.path.join(outdir, 'details.csv.bz2')

        classify_ref = os.path.join(
            thisdatadir, this_test, 'classifications.csv.bz2')
        details_ref = os.path.join(
            thisdatadir, this_test, 'details.csv.bz2')

        args = [
            '--columns', 'qseqid,sseqid,pident,qstart,qend,qlen,qcovs',
            # '--weights', weights,
            '--copy-numbers', self.copy_numbers,
            '--details-out', details_out,
            '--lineages', taxonomy,
            '--out', classify_out,
            '--rank-thresholds', self.rank_thresholds,
            '--seq-info', seq_info,
            '--specimen-map', specimen_map,
            blast]

        logging.info(self.log_info.format(' '.join(map(str, args))))

        self.main(args)

        self.assertTrue(filecmp.cmp(classify_ref, classify_out))
        self.assertTrue(filecmp.cmp(details_ref, details_out))

    def test07(self):
        """
        Test validation of type strains
        """

        thisdatadir = self.thisdatadir

        this_test = sys._getframe().f_code.co_name

        blast = os.path.join(thisdatadir, this_test, 'blast.csv.bz2')
        taxonomy = os.path.join(thisdatadir, this_test, 'taxonomy.csv.bz2')
        seq_info = os.path.join(thisdatadir, this_test, 'seq_info.csv.bz2')
        specimen_map = os.path.join(thisdatadir, this_test, 'map.csv.bz2')

        outdir = self.mkoutdir()

        classify_out = os.path.join(outdir, 'classifications.csv.bz2')
        details_out = os.path.join(outdir, 'details.csv.bz2')

        classify_ref = os.path.join(
            thisdatadir, this_test, 'classifications.csv.bz2')
        details_ref = os.path.join(
            thisdatadir, this_test, 'details.csv.bz2')

        args = [
            '--columns', 'qseqid,sseqid,pident,qstart,qend,qlen,qcovs',
            '--details-out', details_out,
            '--lineages', taxonomy,
            '--out', classify_out,
            '--rank-thresholds', self.rank_thresholds,
            '--specimen-map', specimen_map,
            '--seq-info', seq_info,
            blast]

        logging.info(self.log_info.format(' '.join(map(str, args))))

        self.main(args)

        self.assertTrue(filecmp.cmp(classify_ref, classify_out))
        self.assertTrue(filecmp.cmp(details_ref, details_out))

    def test08(self):
        """
        Test empty blast_results file
        """
        thisdatadir = self.thisdatadir

        this_test = sys._getframe().f_code.co_name

        outdir = self.mkoutdir()

        classify_out = os.path.join(outdir, 'classifications.csv.bz2')
        details_out = os.path.join(outdir, 'details.csv.bz2')

        classify_ref = os.path.join(
            thisdatadir, this_test, 'classifications.csv.bz2')
        details_ref = os.path.join(
            thisdatadir, this_test, 'details.csv.bz2')

        # create blank blast.csv file
        blast = os.path.join(outdir, 'blast.csv')
        open(blast, 'w').close()
        taxonomy = os.path.join(thisdatadir, this_test, 'taxonomy.csv.bz2')
        seq_info = os.path.join(thisdatadir, this_test, 'seq_info.csv.bz2')

        args = [
            '--columns', 'qseqid,sseqid,pident,qstart,qend,qlen,qcovs',
            '--details-out', details_out,
            '--out', classify_out,
            '--lineages', taxonomy,
            '--rank-thresholds', self.rank_thresholds,
            '--seq-info', seq_info,
            blast]

        logging.info(self.log_info.format(' '.join(map(str, args))))

        self.main(args)

        self.assertTrue(filecmp.cmp(classify_ref, classify_out))
        self.assertTrue(filecmp.cmp(details_ref, details_out))

        # --- Scenario 2: empty bz2 file ---
        blast_bz2 = os.path.join(outdir, 'blast.csv.bz2')
        import bz2
        with bz2.open(blast_bz2, 'wt') as f:
            pass  # creates a valid, but empty bz2 file
        args[-1] = blast_bz2
        logging.info(self.log_info.format(' '.join(map(str, args))))
        self.main(args)
        self.assertTrue(filecmp.cmp(classify_ref, classify_out))
        self.assertTrue(filecmp.cmp(details_ref, details_out))

    def test09(self):
        """
        Test all [no blast results] classification with hits
        """

        thisdatadir = self.thisdatadir

        this_test = sys._getframe().f_code.co_name

        blast = os.path.join(thisdatadir, this_test, 'blast.csv.bz2')
        specimen_map = os.path.join(thisdatadir, this_test, 'map.csv.bz2')
        taxonomy = os.path.join(thisdatadir, 'taxonomy.csv.bz2')
        seq_info = os.path.join(thisdatadir, 'seq_info.csv.bz2')

        outdir = self.mkoutdir()

        classify_out = os.path.join(outdir, 'classifications.csv.bz2')
        details_out = os.path.join(outdir, 'details.csv.bz2')

        classify_ref = os.path.join(
            thisdatadir, this_test, 'classifications.csv.bz2')
        details_ref = os.path.join(
            thisdatadir, this_test, 'details.csv.bz2')

        args = [
            '--columns', 'qseqid,sseqid,pident,qstart,qend,qlen,qcovs',
            # '--weights', weights,
            '--details-out', details_out,
            '--lineages', taxonomy,
            '--out', classify_out,
            '--rank-thresholds', self.rank_thresholds,
            '--seq-info', seq_info,
            '--specimen-map', specimen_map,
            blast]

        logging.info(self.log_info.format(' '.join(map(str, args))))

        self.main(args)

        self.assertTrue(filecmp.cmp(classify_ref, classify_out))
        self.assertTrue(filecmp.cmp(details_ref, details_out))

    def test10(self):
        """
        Parse non-default blast result files that have headers
        """

        thisdatadir = self.thisdatadir

        this_test = sys._getframe().f_code.co_name

        outdir = self.mkoutdir()

        classify_out = os.path.join(outdir, 'classifications.csv')

        blast = os.path.join(thisdatadir, 'blast_extrafields.csv.bz2')
        specimen_map = os.path.join(thisdatadir, 'map_single.csv.bz2')
        taxonomy = os.path.join(thisdatadir, 'taxonomy.csv.bz2')
        seq_info = os.path.join(thisdatadir, 'seq_info.csv.bz2')

        outdir = self.mkoutdir()

        classify_out = os.path.join(outdir, 'classifications.csv.bz2')

        classify_ref = os.path.join(
            thisdatadir, this_test, 'classifications.csv.bz2')

        args = [
            '--lineages', taxonomy,
            '--out', classify_out,
            '--rank-thresholds', self.rank_thresholds,
            '--seq-info', seq_info,
            '--specimen-map', specimen_map,
            blast]

        logging.info(self.log_info.format(' '.join(map(str, args))))

        self.main(args)

        self.assertTrue(filecmp.cmp(classify_ref, classify_out))

    def test11(self):
        """
        Test dynamic thresholding

        github issue #32
        """

        thisdatadir = self.thisdatadir

        this_test = sys._getframe().f_code.co_name

        blast = os.path.join(thisdatadir, this_test, 'blast.csv.bz2')
        taxonomy = os.path.join(thisdatadir, this_test, 'taxonomy.csv.bz2')
        seq_info = os.path.join(thisdatadir, this_test, 'seq_info.csv.bz2')

        outdir = self.mkoutdir()

        classify_out = os.path.join(outdir, 'classifications.csv.bz2')
        details_out = os.path.join(outdir, 'details.csv.bz2')

        classify_ref = os.path.join(
            thisdatadir, this_test, 'classifications.csv.bz2')
        details_ref = os.path.join(
            thisdatadir, this_test, 'details.csv.bz2')

        args = [
            '--columns', 'qseqid,sseqid,pident,qstart,qend,qlen,qcovs',
            '--details-out', details_out,
            '--lineages', taxonomy,
            '--out', classify_out,
            '--rank-thresholds', self.rank_thresholds,
            '--seq-info', seq_info,
            blast]

        logging.info(self.log_info.format(' '.join(map(str, args))))

        self.main(args)

        self.assertTrue(filecmp.cmp(classify_ref, classify_out))
        self.assertTrue(filecmp.cmp(details_ref, details_out))

    def test13(self):
        """
        Test ordering of assignment_id

        Note: This test was inspired by a case when upgrading
        from numpy 1.9.2 to 1.10.1 where, with sort_index we were using
        an "unstable" sort on a field (specimen) with only one value, and
        our classifications became unsorted.  Data here is derived from that
        test, previously would have failed this test, and subsequently passes
        """
        thisdatadir = self.thisdatadir

        this_test = sys._getframe().f_code.co_name

        blast = os.path.join(thisdatadir, this_test, 'blast.csv.bz2')
        taxonomy = os.path.join(datadir, 'taxonomy.csv.bz2')
        seq_info = os.path.join(thisdatadir, this_test, 'seq_info.csv.bz2')
        weights = os.path.join(thisdatadir, this_test, 'weights.csv.bz2')

        outdir = self.mkoutdir()

        classify_out = os.path.join(outdir, 'classifications.csv.bz2')

        classify_ref = os.path.join(
            thisdatadir, this_test, 'classifications.csv.bz2')

        args = [
            '--columns', 'qseqid,sseqid,pident,qstart,qend,qlen,qcovs',
            '--out', classify_out,
            '--lineages', taxonomy,
            '--rank-thresholds', self.rank_thresholds,
            '--seq-info', seq_info,
            '--specimen-map', weights,
            blast]

        logging.info(self.log_info.format(' '.join(map(str, args))))

        self.main(args)

        self.assertTrue(filecmp.cmp(classify_ref, classify_out))

    def test14(self):
        """
        Test --hits-below-threshold
        """
        thisdatadir = self.thisdatadir

        this_test = sys._getframe().f_code.co_name

        blast = os.path.join(thisdatadir, 'blast.csv.bz2')
        taxonomy = os.path.join(thisdatadir, 'taxonomy.csv.bz2')
        seq_info = os.path.join(thisdatadir, 'seq_info.csv.bz2')
        specimen_map = os.path.join(thisdatadir, 'map_single.csv.bz2')

        outdir = self.mkoutdir()

        classify_out = os.path.join(outdir, 'classifications.csv.bz2')
        details_out = os.path.join(outdir, 'details.csv.bz2')

        classify_ref = os.path.join(
            thisdatadir, this_test, 'classifications.csv.bz2')
        details_ref = os.path.join(
            thisdatadir, this_test, 'details.csv.bz2')

        args = [
            '--columns', 'qseqid,sseqid,pident,qstart,qend,qlen,qcovs',
            '--details-out', details_out,
            '--hits-below-threshold',
            '--lineages', taxonomy,
            '--out', classify_out,
            '--rank-thresholds', self.rank_thresholds,
            '--seq-info', seq_info,
            '--specimen-map', specimen_map,
            blast]

        logging.info(self.log_info.format(' '.join(map(str, args))))

        self.main(args)

        self.assertTrue(filecmp.cmp(classify_ref, classify_out))
        self.assertTrue(filecmp.cmp(details_ref, details_out))

    def test15(self):
        """
        --include-ref-rank not present in blast lineages
        """

        this_test = sys._getframe().f_code.co_name

        thisdatadir = self.thisdatadir

        taxonomy = os.path.join(thisdatadir, 'taxonomy.csv.bz2')
        seq_info = os.path.join(thisdatadir, 'seq_info.csv.bz2')
        blast = os.path.join(thisdatadir, 'blast.csv.bz2')

        outdir = self.mkoutdir()

        classify_out = os.path.join(outdir, 'classifications.csv.bz2')
        details_out = os.path.join(outdir, 'details.csv.bz2')

        classify_ref = os.path.join(
            thisdatadir, this_test, 'classifications.csv.bz2')
        details_ref = os.path.join(
            thisdatadir, this_test, 'details.csv.bz2')

        args = [
            '--columns', 'qseqid,sseqid,pident,qstart,qend,qlen,qcovs',
            '--details-out', details_out,
            '--lineages', taxonomy,
            '--include-ref-rank', 'forma',
            '--out', classify_out,
            '--rank-thresholds', self.rank_thresholds,
            '--seq-info', seq_info,
            blast]

        logging.info(self.log_info.format(' '.join(map(str, args))))

        self.main(args)

        self.assertTrue(filecmp.cmp(classify_ref, classify_out))
        self.assertTrue(filecmp.cmp(details_ref, details_out))
