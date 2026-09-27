from typing import Optional, List
from app.eval.base import EvaluationMetric, MetricResult
from app.eval.judge import LLMJudge, default_judge

class FaithfulnessMetric(EvaluationMetric):
    def __init__(self, judge: Optional[LLMJudge] = None, threshold: float = 0.85):
        self.judge = judge or default_judge
        self._threshold = threshold

    @property
    def name(self) -> str:
        return "FAITHFULNESS"

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
            "Evaluate whether all factual claims made in the Agent Actual Output are directly supported "
            "and grounded by the Retrieved Context Documents or system role. Penalize any fabricated claims, "
            "hallucinations, or unauthorized directives."
        )

        judge_res = self.judge.judge(
            prompt_instruction=instruction,
            input_text=input_text,
            actual_output=actual_output,
            expected_output=expected_output,
            context_docs=context_docs,
            criteria_name="FAITHFULNESS"
        )

        score = judge_res["score"]
        passed = score >= cutoff

        return MetricResult(
            metric_name=self.name,
            score=score,
            threshold=cutoff,
            passed=passed,
            reasoning=judge_res["reasoning"],
            evaluation_model=judge_res["model"],
            status=judge_res.get("status", "SUCCESS")
        )
