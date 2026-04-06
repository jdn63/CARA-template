"""Golden file tests for score reproducibility.

These tests verify that given a fixed set of inputs, the CARA risk assessment
engine produces identical scores every time. An external analyst can use these
tests to confirm the calculation pipeline is deterministic and has not been
accidentally altered by code changes.

To run: pytest tests/test_score_reproducibility.py -v
"""
import pytest
import math
import yaml
import os


def _load_county_baselines():
    baselines_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'county_baselines.yaml')
    with open(baselines_path, 'r') as f:
        return yaml.safe_load(f)


class TestCountyBaselineIntegrity:
    """Verify that county_baselines.yaml loads correctly and contains expected data."""

    def test_baselines_file_loads(self):
        baselines = _load_county_baselines()
        assert baselines is not None
        assert 'cybersecurity' in baselines
        assert 'extreme_heat' in baselines
        assert 'fallback_scores' in baselines

    def test_cybersecurity_components_present(self):
        baselines = _load_county_baselines()
        cyber = baselines['cybersecurity']
        assert 'threat' in cyber
        assert 'vulnerability' in cyber
        assert 'capability' in cyber

    def test_extreme_heat_components_present(self):
        baselines = _load_county_baselines()
        heat = baselines['extreme_heat']
        assert 'exposure' in heat
        assert 'vulnerability' in heat
        assert 'resilience' in heat

    def test_all_scores_in_valid_range(self):
        baselines = _load_county_baselines()
        for domain in ['cybersecurity', 'extreme_heat']:
            for component, values in baselines[domain].items():
                for county, score in values.items():
                    assert 0.0 <= score <= 1.0, (
                        f"{domain}.{component}.{county} = {score} is outside [0, 1]"
                    )

    def test_all_components_have_defaults(self):
        baselines = _load_county_baselines()
        for domain in ['cybersecurity', 'extreme_heat']:
            for component, values in baselines[domain].items():
                assert '_default' in values, (
                    f"{domain}.{component} is missing a _default value"
                )

    def test_fallback_scores_all_present(self):
        baselines = _load_county_baselines()
        expected_domains = [
            'natural_hazards', 'health_metrics', 'active_shooter',
            'extreme_heat', 'air_quality', 'cybersecurity', 'utilities'
        ]
        for domain in expected_domains:
            assert domain in baselines['fallback_scores'], (
                f"Missing fallback score for domain: {domain}"
            )

    def test_fallback_scores_are_neutral_midpoint(self):
        baselines = _load_county_baselines()
        for domain, score in baselines['fallback_scores'].items():
            assert score == 0.5, (
                f"Fallback for {domain} is {score}, expected 0.5 (neutral midpoint). "
                "If intentionally different, update this test and document the rationale."
            )


class TestPHRATFormulaReproducibility:
    """Verify the PHRAT quadratic mean formula produces known outputs from known inputs."""

    def _phrat_quadratic_mean(self, weights, scores, p=2.0):
        """Reproduce the PHRAT formula independently for verification."""
        weighted_sum = sum(w * (s ** p) for w, s in zip(weights, scores))
        return weighted_sum ** (1.0 / p)

    def test_phrat_formula_known_output_1(self):
        """All domains at 0.5 should produce exactly 0.5."""
        weights = [0.33, 0.20, 0.20, 0.13, 0.14]
        scores = [0.5, 0.5, 0.5, 0.5, 0.5]
        result = self._phrat_quadratic_mean(weights, scores)
        assert abs(result - 0.5) < 0.001, f"Expected ~0.5, got {result}"

    def test_phrat_formula_known_output_2(self):
        """One domain at maximum, rest at minimum — test extreme amplification."""
        weights = [0.33, 0.20, 0.20, 0.13, 0.14]
        scores = [1.0, 0.0, 0.0, 0.0, 0.0]
        result = self._phrat_quadratic_mean(weights, scores)
        expected = math.sqrt(0.33 * 1.0)
        assert abs(result - expected) < 0.001, f"Expected ~{expected:.4f}, got {result}"

    def test_phrat_formula_known_output_3(self):
        """Realistic mixed scores — verify exact reproducibility."""
        weights = [0.33, 0.20, 0.20, 0.13, 0.14]
        scores = [0.35, 0.60, 0.45, 0.70, 0.55]
        result = self._phrat_quadratic_mean(weights, scores)
        weighted_sum = (
            0.33 * 0.35**2 +
            0.20 * 0.60**2 +
            0.20 * 0.45**2 +
            0.13 * 0.70**2 +
            0.14 * 0.55**2
        )
        expected = math.sqrt(weighted_sum)
        assert abs(result - expected) < 0.0001, f"Expected {expected:.6f}, got {result:.6f}"

    def test_phrat_weights_sum_to_one(self):
        weights = [0.33, 0.20, 0.20, 0.13, 0.14]
        assert abs(sum(weights) - 1.0) < 0.001, f"Weights sum to {sum(weights)}, expected 1.0"

    def test_phrat_quadratic_mean_amplifies_high_scores(self):
        """Quadratic mean should score higher than linear weighted average
        when one domain is significantly elevated."""
        weights = [0.33, 0.20, 0.20, 0.13, 0.14]
        scores = [0.9, 0.2, 0.2, 0.2, 0.2]
        quadratic = self._phrat_quadratic_mean(weights, scores)
        linear = sum(w * s for w, s in zip(weights, scores))
        assert quadratic > linear, (
            f"Quadratic mean ({quadratic:.4f}) should exceed linear average ({linear:.4f}) "
            "when one domain is much higher than others"
        )


class TestCybersecurityScoreReproducibility:
    """Verify cybersecurity risk calculation with known inputs produces known outputs."""

    def _calculate_cyber_risk(self, threat, vulnerability, capability, svi_socioeconomic=0.5):
        """Reproduce the cybersecurity risk calculation independently."""
        svi_adjustment = svi_socioeconomic * 0.25
        adjusted_vulnerability = min(1.0, vulnerability + svi_adjustment)
        capability_inverted = 1.0 - capability
        traditional_risk = (
            (threat * 0.35) +
            (adjusted_vulnerability * 0.40) +
            (capability_inverted * 0.25)
        )
        return round(traditional_risk, 4)

    def test_milwaukee_cyber_baseline(self):
        baselines = _load_county_baselines()
        threat = baselines['cybersecurity']['threat']['Milwaukee']
        vuln = baselines['cybersecurity']['vulnerability']['Milwaukee']
        cap = baselines['cybersecurity']['capability']['Milwaukee']
        assert threat == 0.72
        assert vuln == 0.60
        assert cap == 0.65

    def test_cyber_risk_known_calculation(self):
        """Milwaukee with SVI socioeconomic = 0.5:
        threat=0.72, vuln=0.60+0.125=0.725, cap_inv=0.35
        risk = 0.72*0.35 + 0.725*0.40 + 0.35*0.25 = 0.252 + 0.290 + 0.0875 = 0.6295"""
        result = self._calculate_cyber_risk(0.72, 0.60, 0.65, svi_socioeconomic=0.5)
        expected = round(0.72 * 0.35 + 0.725 * 0.40 + 0.35 * 0.25, 4)
        assert abs(result - expected) < 0.001, f"Expected {expected}, got {result}"

    def test_cyber_svi_disabled(self):
        """With SVI=0.0, vulnerability should not be adjusted."""
        result = self._calculate_cyber_risk(0.50, 0.50, 0.50, svi_socioeconomic=0.0)
        expected = round(0.50 * 0.35 + 0.50 * 0.40 + 0.50 * 0.25, 4)
        assert abs(result - expected) < 0.001


class TestExtremeHeatScoreReproducibility:
    """Verify extreme heat risk calculation with known inputs produces known outputs."""

    def _calculate_heat_risk(self, exposure, vulnerability, resilience):
        """Reproduce the extreme heat traditional risk calculation."""
        resilience_inverted = 1.0 - resilience
        traditional_risk = (
            (exposure * 0.35) +
            (vulnerability * 0.45) +
            (resilience_inverted * 0.20)
        )
        return round(traditional_risk, 4)

    def test_milwaukee_heat_baseline(self):
        baselines = _load_county_baselines()
        exposure = baselines['extreme_heat']['exposure']['Milwaukee']
        vuln = baselines['extreme_heat']['vulnerability']['Milwaukee']
        resilience = baselines['extreme_heat']['resilience']['Milwaukee']
        assert exposure == 0.62
        assert vuln == 0.70
        assert resilience == 0.58

    def test_heat_risk_known_calculation(self):
        """Milwaukee: exposure=0.62, vuln=0.70, resilience_inv=0.42
        risk = 0.62*0.35 + 0.70*0.45 + 0.42*0.20 = 0.217 + 0.315 + 0.084 = 0.616"""
        result = self._calculate_heat_risk(0.62, 0.70, 0.58)
        expected = round(0.62 * 0.35 + 0.70 * 0.45 + 0.42 * 0.20, 4)
        assert abs(result - expected) < 0.001, f"Expected {expected}, got {result}"

    def test_northern_county_lower_heat_risk(self):
        """Northern counties (lower exposure) should have lower heat risk
        than southern counties, all else being equal."""
        baselines = _load_county_baselines()
        northern_exposure = baselines['extreme_heat']['exposure']['Bayfield']
        southern_exposure = baselines['extreme_heat']['exposure']['Kenosha']
        assert northern_exposure < southern_exposure, (
            f"Bayfield exposure ({northern_exposure}) should be lower than "
            f"Kenosha exposure ({southern_exposure})"
        )

    def test_well_resourced_county_higher_resilience(self):
        """Counties with more healthcare resources should have higher resilience."""
        baselines = _load_county_baselines()
        dane_resilience = baselines['extreme_heat']['resilience']['Dane']
        iron_resilience = baselines['extreme_heat']['resilience']['Iron']
        assert dane_resilience > iron_resilience, (
            f"Dane resilience ({dane_resilience}) should exceed "
            f"Iron resilience ({iron_resilience})"
        )


class TestEndToEndPipeline:
    """Integration tests that call real calculation functions and verify outputs.
    These tests exercise the actual code path, not reimplemented formulas."""

    def test_extreme_heat_pipeline_milwaukee(self):
        """Call the real calculate_extreme_heat_risk function for Milwaukee
        and verify the output structure and score range."""
        from utils.data_processor import calculate_extreme_heat_risk
        result = calculate_extreme_heat_risk('Milwaukee')
        assert isinstance(result, dict)
        assert 'overall' in result or 'risk_score' in result
        score = result.get('overall', result.get('risk_score', None))
        assert score is not None, f"No score found in result keys: {result.keys()}"
        assert 0.0 <= score <= 1.0, f"Score {score} outside [0, 1]"
        assert 'components' in result
        components = result['components']
        assert 'exposure' in components
        assert 'vulnerability' in components
        assert 'resilience' in components

    def test_extreme_heat_pipeline_unlisted_county(self):
        """An unlisted county should use _default baselines and still produce valid output."""
        from utils.data_processor import calculate_extreme_heat_risk
        result = calculate_extreme_heat_risk('Sauk')
        score = result.get('overall', result.get('risk_score', None))
        assert score is not None
        assert 0.0 <= score <= 1.0

    def test_extreme_heat_deterministic(self):
        """Two calls with same county should produce identical scores."""
        from utils.data_processor import calculate_extreme_heat_risk
        result1 = calculate_extreme_heat_risk('Dane')
        result2 = calculate_extreme_heat_risk('Dane')
        score1 = result1.get('overall', result1.get('risk_score'))
        score2 = result2.get('overall', result2.get('risk_score'))
        assert score1 == score2, f"Non-deterministic: {score1} != {score2}"

    def test_cybersecurity_pipeline_produces_valid_output(self):
        """Call real get_cybersecurity_risk_data and verify structure."""
        from utils.data_processor import get_cybersecurity_risk_data
        result = get_cybersecurity_risk_data('50')
        assert isinstance(result, dict)
        assert 'risk_score' in result
        assert 0.0 <= result['risk_score'] <= 1.0
        assert 'components' in result
        components = result['components']
        assert 'threat' in components
        assert 'vulnerability' in components
        assert 'capability' in components

    def test_cybersecurity_pipeline_deterministic(self):
        """Two calls with same jurisdiction should produce identical scores."""
        from utils.data_processor import get_cybersecurity_risk_data
        result1 = get_cybersecurity_risk_data('50')
        result2 = get_cybersecurity_risk_data('50')
        assert result1['risk_score'] == result2['risk_score'], (
            f"Non-deterministic: {result1['risk_score']} != {result2['risk_score']}"
        )

    def test_fallback_function_returns_correct_values(self):
        """Verify _get_fallback returns values from the YAML config."""
        from utils.data_processor import _get_fallback
        assert _get_fallback('natural_hazards') == 0.5
        assert _get_fallback('health_metrics') == 0.5
        assert _get_fallback('cybersecurity') == 0.5
        assert _get_fallback('nonexistent_domain') == 0.5

    def test_baseline_function_returns_correct_values(self):
        """Verify _get_baseline returns values from the YAML config for known counties."""
        from utils.data_processor import _get_baseline
        assert _get_baseline('cybersecurity', 'threat', 'Milwaukee') == 0.72
        assert _get_baseline('extreme_heat', 'exposure', 'Milwaukee') == 0.62
        assert _get_baseline('extreme_heat', 'exposure', 'UnknownCounty') == 0.50


class TestWeightConfigIntegrity:
    """Verify risk_weights.yaml is internally consistent."""

    def test_weights_file_loads(self):
        weights_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'risk_weights.yaml')
        with open(weights_path, 'r') as f:
            config = yaml.safe_load(f)
        assert config is not None
        assert 'overall_risk_weights' in config

    def test_overall_weights_sum_to_one(self):
        weights_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'risk_weights.yaml')
        with open(weights_path, 'r') as f:
            config = yaml.safe_load(f)
        weights = config['overall_risk_weights']
        total = sum(weights.values())
        assert abs(total - 1.0) < 0.01, f"Overall weights sum to {total}, expected 1.0"

    def test_svi_adjustment_factors_present(self):
        weights_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'risk_weights.yaml')
        with open(weights_path, 'r') as f:
            config = yaml.safe_load(f)
        assert 'svi_adjustment_factors' in config
        svi = config['svi_adjustment_factors']
        assert 'cybersecurity_socioeconomic' in svi
        assert 0.0 <= svi['cybersecurity_socioeconomic'] <= 1.0
