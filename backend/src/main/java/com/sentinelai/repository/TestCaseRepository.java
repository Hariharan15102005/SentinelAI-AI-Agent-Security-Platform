package com.sentinelai.repository;

import com.sentinelai.entity.TestCase;
import com.sentinelai.enums.TestCategory;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface TestCaseRepository extends JpaRepository<TestCase, Long> {
    List<TestCase> findByProjectIdOrderByCreatedAtDesc(Long projectId);
    List<TestCase> findByProjectIdAndCategory(Long projectId, TestCategory category);
    Optional<TestCase> findByIdAndProjectId(Long id, Long projectId);
    long countByProjectId(Long projectId);
}
