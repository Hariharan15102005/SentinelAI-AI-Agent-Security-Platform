package com.sentinelai.repository;

import com.sentinelai.entity.EvaluationResult;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface EvaluationResultRepository extends JpaRepository<EvaluationResult, Long> {
    List<EvaluationResult> findByTestRunId(Long testRunId);

    @Query("SELECT er FROM EvaluationResult er JOIN er.testRun tr WHERE tr.project.id = :projectId ORDER BY er.createdAt DESC")
    List<EvaluationResult> findByProjectId(@Param("projectId") Long projectId);

    @Query("SELECT er.metricName, AVG(er.score) FROM EvaluationResult er JOIN er.testRun tr WHERE tr.project.id = :projectId GROUP BY er.metricName")
    List<Object[]> findAverageScoresByMetricForProject(@Param("projectId") Long projectId);
}
