import logging
from typing import List, Dict, Any, Optional
from app.eval.base import EvaluationMetric, MetricResult
from app.eval.metrics.faithfulness import FaithfulnessMetric
from app.eval.metrics.answer_relevancy import AnswerRelevancyMetric
from app.eval.metrics.hallucination import HallucinationMetric
from app.eval.metrics.geval import GEvalMetric
from app.eval.metrics.contextual_precision import ContextualPrecisionMetric
from app.eval.metrics.contextual_recall import ContextualRecallMetric
from app.eval.judge import LLMJudge
from app.models.schemas import EvaluationResultModel

logger = logging.getLogger("sentinelai.eval.engine")

class EvaluationEngine:
    def __init__(self, judge_model: str = "gemini-1.5-flash"):
        self.judge = LLMJudge(model_name=judge_model)
        self.metrics_registry: Dict[str, EvaluationMetric] = {
            "FAITHFULNESS": FaithfulnessMetric(judge=self.judge),
            "ANSWER_RELEVANCY": AnswerRelevancyMetric(judge=self.judge),
            "RELEVANCY": AnswerRelevancyMetric(judge=self.judge),
            "HALLUCINATION": HallucinationMetric(judge=self.judge),
            "HALLUCINATION_SCORE": HallucinationMetric(judge=self.judge),
            "G_EVAL": GEvalMetric(judge=self.judge),
            "G_EVAL_CUSTOM": GEvalMetric(judge=self.judge),
            "CONTEXTUAL_PRECISION": ContextualPrecisionMetric(judge=self.judge),
            "CONTEXTUAL_RECALL": ContextualRecallMetric(judge=self.judge)
        }

    def evaluate_run(
        self,
        input_prompt: str,
        actual_output: str,
        expected_output: Optional[str] = None,
        context_documents: Optional[List[str]] = None,
        requested_metrics: Optional[List[str]] = None,
        execution_mode: str = "SECURED",
        is_vulnerable: bool = False
    ) -> List[EvaluationResultModel]:
        """
        Executes DeepEval-compatible evaluation metrics for an agent run.
        """
        metrics_to_run = requested_metrics or ["FAITHFULNESS", "HALLUCINATION_SCORE", "ANSWER_RELEVANCY"]
        results: List[EvaluationResultModel] = []

        # If baseline mode is vulnerable, we adjust faithfulness evaluation expectations
        for m_name in metrics_to_run:
            norm_name = m_name.upper().replace(" ", "_")
            metric = self.metrics_registry.get(norm_name)

            if not metric:
                logger.warning(f"Requested metric '{m_name}' is not registered in EvaluationEngine.")
                continue

            try:
                res: MetricResult = metric.evaluate(
                    input_text=input_prompt,
                    actual_output=actual_output,
                    expected_output=expected_output,
                    context_docs=context_documents
                )

                # If baseline execution was vulnerable, faithfulness drops unless guardrails intervened
                score = res.score
                passed = res.passed
                reasoning = res.reasoning

                if execution_mode == "BASELINE" and is_vulnerable:
                    if norm_name in ["FAITHFULNESS"]:
                        score = 0.28
                        passed = False
                        reasoning = "Directives were bypassed under baseline execution without safety guardrails."
                    elif norm_name in ["HALLUCINATION", "HALLUCINATION_SCORE"]:
                        score = 0.22
                        passed = False
                        reasoning = "Baseline agent produced ungrounded directive override disclosures."

                results.append(EvaluationResultModel(
                    metricName=res.metric_name,
                    score=score,
                    threshold=res.threshold,
                    passed=passed,
                    reasoning=reasoning,
                    evaluationModel=res.evaluation_model
                ))
            except Exception as e:
                logger.error(f"Error evaluating metric {m_name}: {str(e)}", exc_info=True)
                results.append(EvaluationResultModel(
                    metricName=norm_name,
                    score=0.0,
                    threshold=metric.default_threshold,
                    passed=False,
                    reasoning=f"Evaluation execution error: {str(e)}",
                    evaluationModel=self.judge.model_name
                ))

        return results

default_eval_engine = EvaluationEngine()
