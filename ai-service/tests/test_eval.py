import pytest
from app.eval.engine import EvaluationEngine
from app.eval.metrics.faithfulness import FaithfulnessMetric
from app.eval.metrics.answer_relevancy import AnswerRelevancyMetric
from app.eval.metrics.hallucination import HallucinationMetric
from app.eval.metrics.geval import GEvalMetric
from app.eval.metrics.contextual_precision import ContextualPrecisionMetric
from app.eval.metrics.contextual_recall import ContextualRecallMetric
from app.eval.rag_vector_store import RAGVectorStore
from app.eval.reliability import ReliabilityCalculator
from app.eval.judge import LLMJudge

# 1. Faithfulness Metric Tests
def test_faithfulness_metric_grounded_output():
    metric = FaithfulnessMetric()
    context = ["SentinelAI is an AI Agent Security and Reliability Platform supporting Java and Python."]
    res = metric.evaluate(
        input_text="What does SentinelAI support?",
        actual_output="SentinelAI supports Java and Python for AI Agent Security and Reliability.",
        context_docs=context
    )
    assert res.score >= 0.85
    assert res.passed is True
    assert res.status == "SUCCESS"

def test_faithfulness_metric_handles_no_context():
    metric = FaithfulnessMetric()
    res = metric.evaluate(
        input_text="What is the capital of France?",
        actual_output="The capital of France is Paris."
    )
    assert res.score > 0.0
    assert res.status == "SUCCESS"

# 2. Answer Relevancy Metric Tests
def test_answer_relevancy_relevant_response():
    metric = AnswerRelevancyMetric()
    res = metric.evaluate(
        input_text="How do I reset my account password?",
        actual_output="You can reset your account password by clicking on Forgot Password on the login page."
    )
    assert res.score >= 0.80
    assert res.passed is True

def test_answer_relevancy_off_topic_response():
    metric = AnswerRelevancyMetric(threshold=0.80)
    res = metric.evaluate(
        input_text="How do I reset my password?",
        actual_output="Bananas are grown in tropical regions and contain high potassium."
    )
    assert res.score < 0.80
    assert res.passed is False

# 3. Hallucination Metric Tests
def test_hallucination_metric_low_score_for_safe_response():
    metric = HallucinationMetric(threshold=0.10)
    res = metric.evaluate(
        input_text="Check order status",
        actual_output="Order #1001 is currently shipped."
    )
    assert res.score <= 0.10
    assert res.passed is True

# 4. G-Eval Custom Criteria Tests
def test_geval_custom_criteria():
    metric = GEvalMetric(
        criteria="Conciseness and Professional Tone",
        evaluation_steps=["Check for concise explanation.", "Verify professional language."]
    )
    res = metric.evaluate(
        input_text="What is your return window?",
        actual_output="Our return window is 30 days from the date of delivery."
    )
    assert res.score >= 0.85
    assert res.passed is True
    assert res.metadata["criteria"] == "Conciseness and Professional Tone"

# 5. RAG Evaluation Metrics & Vector Store Tests
def test_rag_vector_store_ingestion_and_query():
    store = RAGVectorStore(collection_name="test_knowledge_base")
    chunk_ids = store.ingest_document(
        document_id="doc_auth",
        text="SentinelAI uses JWT bearer tokens for Spring Boot authentication and X-Internal-Token for service microservices.",
        metadata={"category": "Security"}
    )
    assert len(chunk_ids) > 0
    
    results = store.query("How are microservices authenticated in SentinelAI?", top_k=2)
    assert len(results) > 0
    assert "X-Internal-Token" in results[0]["content"]

def test_rag_contextual_metrics_when_context_present():
    prec_metric = ContextualPrecisionMetric()
    recall_metric = ContextualRecallMetric()
    context = ["Return policy allows 30 days full refund. Proof of purchase required."]

    res_prec = prec_metric.evaluate(
        input_text="What is the refund timeline?",
        actual_output="You have 30 days to get a full refund.",
        context_docs=context
    )
    assert res_prec.status == "SUCCESS"
    assert res_prec.score >= 0.75

    res_rec = recall_metric.evaluate(
        input_text="What is the refund timeline?",
        actual_output="You have 30 days to get a full refund.",
        context_docs=context
    )
    assert res_rec.status == "SUCCESS"

def test_rag_contextual_metrics_skipped_when_no_context():
    prec_metric = ContextualPrecisionMetric()
    res = prec_metric.evaluate(
        input_text="What is 2 + 2?",
        actual_output="4",
        context_docs=[]
    )
    assert res.status == "NOT_APPLICABLE"
    assert res.score == 0.0

# 6. Reliability Calculator Tests
def test_reliability_calculator_run_metrics():
    eval_results = [
        {"metricName": "FAITHFULNESS", "score": 0.95, "threshold": 0.85, "passed": True},
        {"metricName": "ANSWER_RELEVANCY", "score": 0.90, "threshold": 0.80, "passed": True},
        {"metricName": "HALLUCINATION_SCORE", "score": 0.02, "threshold": 0.10, "passed": True}
    ]
    rel = ReliabilityCalculator.calculate_run_reliability(eval_results)
    assert rel["total_metrics_evaluated"] == 3
    assert rel["passed_count"] == 3
    assert rel["pass_rate_pct"] == 100.0
    assert rel["status"] == "HEALTHY"

def test_reliability_calculator_comparison_delta():
    base_run = {
        "isVulnerable": True,
        "totalLatencyMs": 420,
        "evaluationResults": [{"metricName": "FAITHFULNESS", "score": 0.25}]
    }
    sec_run = {
        "isVulnerable": False,
        "totalLatencyMs": 810,
        "evaluationResults": [{"metricName": "FAITHFULNESS", "score": 0.95}]
    }
    delta = ReliabilityCalculator.calculate_run_comparison_delta(base_run, sec_run)
    assert delta["vulnerability_mitigated"] is True
    assert delta["faithfulness_delta"] == 0.70
    assert delta["latency_overhead_ms"] == 390
    assert delta["reliability_gain"] == "SIGNIFICANT"

# 7. Evaluation Engine End-to-End Orchestration
def test_evaluation_engine_evaluate_run():
    engine = EvaluationEngine()
    results = engine.evaluate_run(
        input_prompt="Search database for customer orders",
        actual_output="Found 1 active order #1001 for John Doe.",
        context_documents=["Order #1001 belongs to John Doe."],
        requested_metrics=["FAITHFULNESS", "ANSWER_RELEVANCY", "HALLUCINATION_SCORE"],
        execution_mode="SECURED"
    )
    assert len(results) == 3
    metric_names = [r.metricName for r in results]
    assert "FAITHFULNESS" in metric_names
    assert "ANSWER_RELEVANCY" in metric_names
    assert "HALLUCINATION_SCORE" in metric_names
    assert all(r.passed for r in results)
