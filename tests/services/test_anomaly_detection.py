# tests/services/test_anomaly_detection.py
import pytest
from decimal import Decimal
from app.services.anomaly_detection import AnomalyDetector


class TestAnomalyDetector:
    """Tests for AnomalyDetector service."""
    
    def test_detect_warning_level(self):
        """Transaction > 2x average should be warning"""
        detector = AnomalyDetector(
            warning_threshold=2.0,
            anomaly_threshold=3.0,
            large_transaction_threshold=10000
        )
        # amount=200, average=100 -> 2x = warning
        result = detector.detect(Decimal("200"), Decimal("100"), Decimal("5000"))
        assert result["level"] == "warning"

    def test_detect_anomaly_level(self):
        """Transaction > 3x average should be anomaly"""
        detector = AnomalyDetector()
        # amount=400, average=100 -> 4x = anomaly
        result = detector.detect(Decimal("400"), Decimal("100"), Decimal("5000"))
        assert result["level"] == "anomaly"

    def test_detect_alert_level(self):
        """Transaction > large_transaction_threshold should always be alert"""
        detector = AnomalyDetector()
        # amount=15000 > 10000 = alert
        result = detector.detect(Decimal("15000"), Decimal("100"), Decimal("15000"))
        assert result["level"] == "alert"

    def test_no_anomaly(self):
        """Transaction within normal range should be normal"""
        detector = AnomalyDetector()
        # amount=100, average=100 -> 1x = normal
        result = detector.detect(Decimal("100"), Decimal("100"), Decimal("100"))
        assert result["level"] is None
    
    def test_zero_average(self):
        """Zero average should not trigger anomaly"""
        detector = AnomalyDetector()
        result = detector.detect(Decimal("100"), Decimal("0"), Decimal("100"))
        assert result["level"] is None
    
    def test_custom_thresholds(self):
        """Custom thresholds should be respected"""
        detector = AnomalyDetector(
            warning_threshold=1.5,
            anomaly_threshold=2.5,
            large_transaction_threshold=5000
        )
        # amount=200, average=100 -> 2x
        # With warning=1.5, anomaly=2.5, should be warning
        result = detector.detect(Decimal("200"), Decimal("100"), Decimal("200"))
        assert result["level"] == "warning"
        
        # amount=300, average=100 -> 3x
        # With anomaly=2.5, should be anomaly
        result = detector.detect(Decimal("300"), Decimal("100"), Decimal("300"))
        assert result["level"] == "anomaly"
        
        # amount=6000 > 5000 = alert
        result = detector.detect(Decimal("6000"), Decimal("100"), Decimal("6000"))
        assert result["level"] == "alert"
