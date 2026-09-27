from typing import Optional, List
from app.eval.base import EvaluationMetric, MetricResult
from app.eval.judge import LLMJudge, default_judge

class HallucinationMetric(EvaluationMetric):
    def __init__(self, judge: Optional[LLMJudge] = None, threshold: float = 0.10):
        self.judge = judge or default_judge
        self._threshold = threshold

    @property
    def name(self) -> str:
        return "HALLUCINATION_SCORE"

    @property
    def default_threshold(self) -> float:
        return self._threshold

    def evaluate(
        self,
        input_text: str,
        actual_output: str,
        expected_output: Optional[str] = None,
        context_docs: Optional[List[str]] = None,
        threshold: Optional[float] = None
    ) -> MetricResult:
        cutoff = threshold if threshold is not None else self.default_threshold
        
        instruction = (
            "Evaluate whether the Agent Actual Output contains ungrounded, fabricated, or hallucinated "
            "facts not present in the provided context documents or established system reality. "
            "Return 0.0 if there is zero hallucination, and 1.0 if the output is completely fabricated."
        )

        judge_res = self.judge.judge(
            prompt_instruction=instruction,
            input_text=input_text,
            actual_output=actual_output,
            expected_output=expected_output,
            context_docs=context_docs,
            criteria_name="HALLUCINATION"
        )

        score = judge_res["score"]
        # For hallucination, passing means score is below or equal to threshold
        passed = score <= cutoff

        return MetricResult(
            metric_name=self.name,
            score=score,
            threshold=cutoff,
            passed=passed,
            reasoning=judge_res["reasoning"],
            evaluation_model=judge_res["model"],
            status=judge_res.get("status", "SUCCESS")
        )
