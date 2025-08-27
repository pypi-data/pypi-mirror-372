# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function

import os
import sys

import unittest
import shutil

# temporary solution for relative imports in case TDC is not installed
# if TDC is installed, no need to use the following line
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
# TODO: add verification for the generation other than simple integration


class TestDataloader(unittest.TestCase):

    def setUp(self):
        print(os.getcwd())
        pass

    def test_single_pred(self):
        from tdc_ml.single_pred import TestSinglePred

        data = TestSinglePred(name="Test_Single_Pred")
        split = data.get_split()

    def test_multi_pred(self):
        from tdc_ml.multi_pred import TestMultiPred

        data = TestMultiPred(name="Test_Multi_Pred")
        split = data.get_split()

    def test_brown(self):
        # TODO: factor out into specialized test suites for individual datasets
        # this test serves as an integration test of the data processing, data configs, and existing tdc pipeline. leave here for now.
        from tdc_ml.multi_pred import ProteinPeptide
        data = ProteinPeptide(name="brown_mdm2_ace2_12ca5")
        assert "protein_or_rna_sequence" in data.get_data(
        ).columns  # brown protein<>peptide dataset uses a data config inserting this column
        data.get_split()

    @unittest.skip(
        "test is taking up too much memory"
    )  #FIXME: should probably create much smaller version and use that for the test. This test does pass locally, please rerun if changing anndata code.
    def test_h5ad_dataloader(self):
        from tdc_ml.multi_pred.perturboutcome import PerturbOutcome
        from pandas import DataFrame
        test_loader = PerturbOutcome(
            name="scperturb_drug_AissaBenevolenskaya2021")
        testdf = test_loader.get_data()
        assert isinstance(testdf, DataFrame)
        test_loader.get_split()

    def test_generation(self):
        from tdc_ml.generation import MolGen

        data = MolGen(name="ZINC")
        split = data.get_split()

    def test_resource_dataverse_dataloader(self):
        import pandas as pd
        from tdc_ml.resource.dataloader import DataLoader

        data = DataLoader(name="opentargets_dti")
        df = data.get_data()
        assert "Y" in df.columns
        split = data.get_split()
        assert "train" in split
        assert len(split["train"]) > 0
        assert len(split["test"]) > 0
        assert isinstance(split["train"], pd.DataFrame)

    def test_resource_dataverse_dataloader_raw_splits(self):
        import pandas as pd
        from tdc_ml.resource.dataloader import DataLoader
        data = DataLoader(name="tchard")
        df = data.get_data()
        assert isinstance(df, pd.DataFrame)
        assert "Y" in df.columns
        assert "splits" in data
        splits = data.get_split()
        assert "train" in splits
        assert "dev" in splits
        assert "test" in splits
        assert isinstance(
            splits["train"]["tchard_pep_cdr3b_only_neg_assays"][0],
            pd.DataFrame)
        assert isinstance(splits["test"]["tchard_pep_cdr3b_only_neg_assays"][2],
                          pd.DataFrame)
        assert not splits["dev"]

    def test_mpc(self):
        from tdc_ml.single_pred.mpc import MPC
        Xs = MPC(
            name=
            "https://raw.githubusercontent.com/bidd-group/MPCD/main/dataset/ADMET/DeepDelta_benchmark/Caco2.csv"
        )
        Xs_split = Xs.get_split()
        Xs_train = Xs_split["train"]
        Xs_test = Xs_split["test"]
        y_train_pIC50 = Xs_train["Y"]
        y_test_pIC50 = Xs_test["Y"]

    def tearDown(self):
        try:
            print(os.getcwd())
            shutil.rmtree(os.path.join(os.getcwd(), "data"))
        except:
            pass


if __name__ == "__main__":
    unittest.main()
