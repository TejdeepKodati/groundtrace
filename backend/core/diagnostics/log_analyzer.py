"""
Microservices Log Analysis, Extraction, Normalization, and Error Code Mapping for GroundTrace.
Troubleshoots distributed system logs, extracts structured telemetry, and maps error codes to remediation playbooks.
"""
import re
from typing import Dict, Any, List, Optional


KNOWN_ERROR_CATALOG = {
    "ERR_PG_CONN_TIMEOUT": {
        "component": "PostgreSQL Database Layer",
        "severity": "CRITICAL",
        "category": "Connection Pool Exhaustion",
        "description": "Database connection pool saturated; active client threads exceeded max_connections limit.",
        "remediation": [
            "Increase max_connections in postgresql.conf or scale PgBouncer connection pooler.",
            "Verify connection leak detection in service data source / ORM session cleanup.",
            "Inspect slow queries locking client connection slots (>5000ms)."
        ]
    },
    "ERR_K8S_OOMKILLED": {
        "component": "Kubernetes Runtime / Pod Eviction",
        "severity": "CRITICAL",
        "category": "Memory Resource Quota Exceeded",
        "description": "Container process exceeded pod memory limit (cgroups cgroup_oom killed).",
        "remediation": [
            "Inspect JVM heap/Node.js buffer allocation settings against pod limits.",
            "Increase deployment resources.limits.memory in Helm / Kubernetes manifest.",
            "Implement streaming batch processing to prevent unbounded memory growth."
        ]
    },
    "ERR_REDIS_CONN_REFUSED": {
        "component": "Redis Sentinel / Distributed Cache",
        "severity": "HIGH",
        "category": "Cache Partition / Connection Drop",
        "description": "Failed to connect to Redis node; replica desynchronization or sentinel failover in progress.",
        "remediation": [
            "Verify Redis Sentinel quorum configuration and cluster health.",
            "Ensure fallback to primary database with circuit breaker pattern (Resilience4j).",
            "Check client connection retry backoff policies."
        ]
    },
    "ERR_KAFKA_OFFSET_OUT_OF_BOUNDS": {
        "component": "Apache Kafka Event Bus",
        "severity": "HIGH",
        "category": "Consumer Lag / Log Retention Expiry",
        "description": "Consumer group offset does not exist on broker (expired by retention or topic recreation).",
        "remediation": [
            "Configure auto.offset.reset to 'earliest' or 'latest' based on idempotency.",
            "Increase topic log.retention.hours to accommodate consumer downtime.",
            "Investigate slow consumer processing loop blocking heartbeat."
        ]
    }
}


class LogTroubleshooter:
    """
    Automated log diagnostic engine performing regex extraction, telemetry normalization,
    error code catalog mapping, and root cause synthesis.
    """

    @staticmethod
    def extract_and_normalize(raw_log: str) -> Dict[str, Any]:
        """
        Parses unstructured log lines into normalized schema.
        """
        # Timestamp extraction
        time_match = re.search(r"\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?", raw_log)
        timestamp = time_match.group(0) if time_match else "UNKNOWN_TIMESTAMP"

        # Log level
        level_match = re.search(r"\b(FATAL|CRITICAL|ERROR|WARN|WARNING|INFO|DEBUG)\b", raw_log, re.IGNORECASE)
        level = level_match.group(0).upper() if level_match else "INFO"

        # Trace ID / Span ID
        trace_match = re.search(r"trace_id=([a-f0-9-]+)|\[([a-f0-9-]{16,36})\]", raw_log, re.IGNORECASE)
        trace_id = trace_match.group(1) or trace_match.group(2) if trace_match else "tr-unknown-uuid"

        # Service name
        service_match = re.search(r"service=([a-zA-Z0-9_-]+)|pod=([a-zA-Z0-9_-]+)|app=([a-zA-Z0-9_-]+)", raw_log)
        service_name = (
            service_match.group(1) or service_match.group(2) or service_match.group(3)
            if service_match else "gateway-service"
        )

        # Error code identification
        error_code = None
        for code in KNOWN_ERROR_CATALOG.keys():
            if code in raw_log:
                error_code = code
                break

        # Fallback error code search
        if not error_code:
            code_match = re.search(r"\b(ERR_[A-Z0-9_]+)\b", raw_log)
            if code_match:
                error_code = code_match.group(1)

        # Lookup catalog
        catalog_info = KNOWN_ERROR_CATALOG.get(error_code or "", {
            "component": "Distributed Microservices Architecture",
            "severity": level,
            "category": "Generic System Error",
            "description": "Unclassified microservice runtime exception.",
            "remediation": [
                "Inspect stack trace line numbers and check dependency health endpoints.",
                "Review recent CI/CD deployments and configuration changes."
            ]
        })

        return {
            "timestamp": timestamp,
            "log_level": level,
            "service_name": service_name,
            "trace_id": trace_id,
            "error_code": error_code or "ERR_GENERIC_UNCLASSIFIED",
            "diagnostics": catalog_info,
            "raw_log_snippet": raw_log.strip()[:300]
        }
