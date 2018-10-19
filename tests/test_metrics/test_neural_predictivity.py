import pytest
from pytest import approx

from brainscore.metrics.neural_predictivity import pls_predictor, linear_predictor, LinearPredictivity
from tests.test_metrics import load_hvm


class TestPlsPredictivity:
    @pytest.mark.parametrize(['region', 'expected_score'], [('IT', 0.826), ('V4', 0.795)])
    def test_hvm_region(self, region, expected_score):
        hvm = load_hvm()
        hvm = hvm.sel(region=region)
        metric = pls_predictor()
        score = metric(source_train=hvm, target_train=hvm, source_test=hvm, target_test=hvm)
        score = metric.aggregate(score)
        expected_score = expected_score
        assert score == approx(expected_score, abs=0.01)


class TestLinearPredictivity:
    @pytest.mark.parametrize('subregion', ['V4', 'pIT', 'cIT', 'aIT'])
    def test_hvm_subregion(self, subregion):
        hvm = load_hvm()
        hvm = hvm.sel(subregion=subregion)
        metric = linear_predictor()
        score = metric(source_train=hvm, target_train=hvm, source_test=hvm, target_test=hvm)
        assert len(score['neuroid']) == len(hvm['neuroid'])
        assert all(score == approx(1, abs=0.01))

    def test_crossvalidated(self):
        hvm = load_hvm()
        hvm = hvm.sel(subregion='V4')
        metric = LinearPredictivity()
        score = metric(hvm, hvm)
        assert len(score.attrs['raw']['split']) == 10
        assert score.sel(aggregation='center') == approx(1, rel=0.01)
        assert score.sel(aggregation='error') == approx(0, rel=0.01)
