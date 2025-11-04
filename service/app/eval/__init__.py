"""Evaluation service for calculating system performance and fairness metrics."""

from app.eval.metrics import EvaluationService
from app.eval.report import ReportGenerator

__all__ = ["EvaluationService", "ReportGenerator"]

