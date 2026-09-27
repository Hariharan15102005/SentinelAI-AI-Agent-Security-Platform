package com.sentinelai.repository;

import com.sentinelai.entity.SecurityFinding;
import com.sentinelai.enums.Severity;
import com.sentinelai.enums.ThreatType;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface SecurityFindingRepository extends JpaRepository<SecurityFinding, Long> {
    List<SecurityFinding> findByTestRunIdOrderByCreatedAtDesc(Long testRunId);

    @Query("SELECT sf FROM SecurityFinding sf JOIN sf.testRun tr WHERE tr.project.id = :projectId ORDER BY sf.createdAt DESC")
    List<SecurityFinding> findByProjectId(@Param("projectId") Long projectId);

    @Query("SELECT COUNT(sf) FROM SecurityFinding sf JOIN sf.testRun tr WHERE tr.project.id = :projectId")
    long countByProjectId(@Param("projectId") Long projectId);

    @Query("SELECT sf.severity, COUNT(sf) FROM SecurityFinding sf JOIN sf.testRun tr WHERE tr.project.id = :projectId GROUP BY sf.severity")
    List<Object[]> countBySeverityForProject(@Param("projectId") Long projectId);

    @Query("SELECT sf.threatType, COUNT(sf) FROM SecurityFinding sf JOIN sf.testRun tr WHERE tr.project.id = :projectId GROUP BY sf.threatType")
    List<Object[]> countByThreatTypeForProject(@Param("projectId") Long projectId);
}
