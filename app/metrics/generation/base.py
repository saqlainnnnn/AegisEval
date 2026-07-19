from __future__ import annotations

import re
import string

from app.domain.evaluation import EvaluationSampleResult
from app.metrics.base import BaseMetric


class BaseGenerationMetric(BaseMetric):
    """
    Base class for text generation metrics.
    """

    def _prediction_text(
        self,
        sample: EvaluationSampleResult,
    ) -> str:
        if sample.prediction is None:
            return ""

        return sample.prediction.answer

    def _reference_text(
        self,
        sample: EvaluationSampleResult,
    ) -> str:
        return sample.question.expected_answer

    def _normalize(
        self,
        text: str,
    ) -> str:
        text = text.lower()

        text = text.translate(
            str.maketrans("", "", string.punctuation)
        )

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()

    def _normalized_prediction(
        self,
        sample: EvaluationSampleResult,
    ) -> str:
        return self._normalize(
            self._prediction_text(sample)
        )

    def _normalized_reference(
        self,
        sample: EvaluationSampleResult,
    ) -> str:
        return self._normalize(
            self._reference_text(sample)
        )

    def _prediction_tokens(
        self,
        sample: EvaluationSampleResult,
    ) -> list[str]:
        return self._normalized_prediction(sample).split()

    def _reference_tokens(
        self,
        sample: EvaluationSampleResult,
    ) -> list[str]:
        return self._normalized_reference(sample).split()