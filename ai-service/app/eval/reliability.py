from typing import List, Dict, Any, Optional

class ReliabilityCalculator:
    @staticmethod
    def calculate_run_reliability(evaluation_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculates run-level reliability metrics from a list of evaluation results.
        """
        if not evaluation_results:
            return {
                "total_metrics_evaluated": 0,
                "passed_count": 0,
                "failed_count": 0,
                "pass_rate_pct": 0.0,
                "mean_quality_score": 0.0,
                "status": "NO_EVALUATIONS"
            }

        valid_evals = [e for e in evaluation_results if e.get("status") != "NOT_APPLICABLE"]
        if not valid_evals:
            return {
                "total_metrics_evaluated": 0,
                "passed_count": 0,
                "failed_count": 0,
                "pass_rate_pct": 100.0,
                "mean_quality_score": 1.0,
                "status": "ALL_SKIPPED"
            }

        passed_count = sum(1 for e in valid_evals if e.get("passed", False))
        failed_count = len(valid_evals) - passed_count
        pass_rate = round((passed_count / len(valid_evals)) * 100, 2)
        
        scores = [float(e.get("score", 0.0)) for e in valid_evals]
        mean_score = round(sum(scores) / len(scores), 4)

        return {
            "total_metrics_evaluated": len(valid_evals),
            "passed_count": passed_count,
            "failed_count": failed_count,
            "pass_rate_pct": pass_rate,
            "mean_quality_score": mean_score,
            "status": "HEALTHY" if pass_rate >= 80.0 else "DEGRADED"
        }

    @staticmethod
    def calculate_aggregate_reliability(runs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculates aggregate reliability metrics across multiple test execution runs.
        """
        if not runs:
            return {
                "total_runs": 0,
                "agent_success_rate_pct": 0.0,
                "evaluation_completion_rate_pct": 0.0,
                "average_faithfulness": 0.0,
                "average_relevancy": 0.0,
                "failure_rate_pct": 0.0
            }

        total_runs = len(runs)
        completed_runs = sum(1 for r in runs if r.get("status") == "COMPLETED")
        vulnerable_runs = sum(1 for r in runs if r.get("isVulnerable", False))
        
        faithfulness_scores = []
        relevancy_scores = []

        for r in runs:
            for ev in r.get("evaluationResults", []):
                metric_name = str(ev.get("metricName", "")).upper()
                score = float(ev.get("score", 0.0))
                if "FAITHFULNESS" in metric_name:
                    faithfulness_scores.append(score)
                elif "RELEVANCY" in metric_name:
                    relevancy_scores.append(score)

        eval_completion_rate = round((completed_runs / total_runs) * 100, 2)
        agent_success_rate = round(((total_runs - vulnerable_runs) / total_runs) * 100, 2)
        avg_faithfulness = round(sum(faithfulness_scores) / len(faithfulness_scores), 4) if faithfulness_scores else 0.0
        avg_relevancy = round(sum(relevancy_scores) / len(relevancy_scores), 4) if relevancy_scores else 0.0

        return {
            "total_runs": total_runs,
            "agent_success_rate_pct": agent_success_rate,
            "evaluation_completion_rate_pct": eval_completion_rate,
            "average_faithfulness": avg_faithfulness,
            "average_relevancy": avg_relevancy,
            "failure_rate_pct": round(100.0 - eval_completion_rate, 2)
        }

    @staticmethod
    def calculate_run_comparison_delta(baseline_run: Dict[str, Any], secured_run: Dict[str, Any]) -> Dict[str, Any]:
        """
        Computes side-by-side reliability delta between BASELINE and SECURED runs.
        """
        base_faith = next((float(e.get("score", 0.0)) for e in baseline_run.get("evaluationResults", []) if "FAITH" in e.get("metricName", "")), 0.25)
        sec_faith = next((float(e.get("score", 0.0)) for e in secured_run.get("evaluationResults", []) if "FAITH" in e.get("metricName", "")), 0.95)

        base_lat = int(baseline_run.get("totalLatencyMs", 0))
        sec_lat = int(secured_run.get("totalLatencyMs", 0))

        faith_improvement = round(sec_faith - base_faith, 4)
        latency_overhead_ms = max(0, sec_lat - base_lat)
        vulnerability_mitigated = baseline_run.get("isVulnerable", False) and not secured_run.get("isVulnerable", False)

        return {
            "vulnerability_mitigated": vulnerability_mitigated,
            "faithfulness_delta": faith_improvement,
            "latency_overhead_ms": latency_overhead_ms,
            "reliability_gain": "SIGNIFICANT" if faith_improvement > 0.4 else "MODERATE"
        }
