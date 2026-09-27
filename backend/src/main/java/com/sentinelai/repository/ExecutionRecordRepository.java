package com.sentinelai.repository;

import com.sentinelai.entity.ExecutionRecord;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ExecutionRecordRepository extends JpaRepository<ExecutionRecord, Long> {
    List<ExecutionRecord> findByTestRunIdOrderByCreatedAtAsc(Long testRunId);
    List<ExecutionRecord> findByTraceIdOrderByCreatedAtAsc(String traceId);
}
