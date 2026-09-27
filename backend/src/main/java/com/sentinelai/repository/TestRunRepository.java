package com.sentinelai.repository;

import com.sentinelai.entity.TestRun;
import com.sentinelai.enums.ExecutionMode;
import com.sentinelai.enums.RunStatus;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface TestRunRepository extends JpaRepository<TestRun, Long> {
    List<TestRun> findByProjectIdOrderByCreatedAtDesc(Long projectId);
    Page<TestRun> findByProjectId(Long projectId, Pageable pageable);
    Optional<TestRun> findByIdAndProjectId(Long id, Long projectId);
    List<TestRun> findByProjectIdAndExecutionMode(Long projectId, ExecutionMode mode);
    long countByProjectId(Long projectId);
    long countByProjectIdAndIsVulnerable(Long projectId, Boolean isVulnerable);
    long countByProjectIdAndExecutionMode(Long projectId, ExecutionMode mode);

    @Query("SELECT AVG(tr.latencyMs) FROM TestRun tr WHERE tr.project.id = :projectId AND tr.status = 'COMPLETED'")
    Double findAverageLatencyByProjectId(@Param("projectId") Long projectId);

    @Query("SELECT AVG(tr.overallScore) FROM TestRun tr WHERE tr.project.id = :projectId AND tr.status = 'COMPLETED'")
    Double findAverageScoreByProjectId(@Param("projectId") Long projectId);

    List<TestRun> findTop5ByProjectIdOrderByCreatedAtDesc(Long projectId);
}
