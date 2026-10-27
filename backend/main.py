"""
GroundTrace FastAPI Server.
Enterprise RAG and Microservices Log Telemetry Platform.
"""
import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from core.ingestion.chunker import SemanticChunker
from core.embeddings.fast_embed import FastEmbedder
from core.indexing.vector_store import VectorStoreIndex
from core.context.context_engine import ContextEngine
from core.diagnostics.log_analyzer import LogTroubleshooter
from core.llmops.evaluator import RAGEvaluator

app = FastAPI(
    title="GroundTrace Enterprise RAG & Log Diagnostics API",
    version="1.0.0",
    description="High-performance RAG pipeline with FastEmbed in-memory vector indexing, grounded citations, and microservice log troubleshooting."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Core Pipeline Components
chunker = SemanticChunker(target_chunk_size=350, chunk_overlap=40)
embedder = FastEmbedder(dimension=128)
vector_store = VectorStoreIndex()

# Seed Enterprise Knowledge Base
ENTERPRISE_DOCS = [
    {
        "doc_id": "doc-k8s-pod-lifecycle",
        "title": "Kubernetes Microservices Architecture & OOM Management",
        "source_type": "infrastructure",
        "content": (
            "Kubernetes orchestrates containerized microservices across worker nodes using Pod specifications.\n\n"
            "When a container exceeds its configured memory limit (resources.limits.memory), the Linux kernel cgroups "
            "subsystem invokes the OOM (Out Of Memory) killer, terminating the container with exit code 137 (OOMKilled).\n\n"
            "To prevent cascading pod evictions, engineers must configure appropriate memory requests and limits based on "
            "P99 profiling, configure horizontal pod autoscalers (HPA) using Prometheus metrics, and set up streaming batch "
            "processing to prevent heap saturation during traffic spikes."
        )
    },
    {
        "doc_id": "doc-pg-connection-pooling",
        "title": "PostgreSQL Connection Pooling and Latency Optimization",
        "source_type": "database",
        "content": (
            "PostgreSQL allocates a dedicated backend worker process for each client connection, consuming ~10MB RAM per session.\n\n"
            "Under high concurrency, unbounded connection spikes lead to pool exhaustion (ERR_PG_CONN_TIMEOUT) and severe context-switching overhead.\n\n"
            "Production architectures must deploy PgBouncer or HikariCP in transaction-pooling mode. Max connections should be capped "
            "using the formula ((CPU_cores * 2) + effective_spindle_count). Application tiers must configure connection acquisition timeouts "
            "and active leak detection to harvest unreturned connections from idle threads."
        )
    },
    {
        "doc_id": "doc-redis-sentinel-quorum",
        "title": "Redis Sentinel Failover and High Availability Guide",
        "source_type": "caching",
        "content": (
            "Redis Sentinel provides high availability, monitoring, and automatic master failover for distributed caching tiers.\n\n"
            "Sentinel nodes monitor master health via continuous HEARTBEAT pings. If a master is unresponsive for down-after-milliseconds, "
            "Sentinels initiate quorum voting to designate a replica as the new master.\n\n"
            "During network partitions, clients encountering ERR_REDIS_CONN_REFUSED must implement exponential backoff retry policies "
            "and circuit breakers to prevent request flooding while Sentinels promote the new primary."
        )
    }
]

# Ingest Seed Docs into In-Memory Vector Store
for doc in ENTERPRISE_DOCS:
    chunks = chunker.chunk_document(doc["doc_id"], doc["title"], doc["content"], doc["source_type"])
    for chunk in chunks:
        vec = embedder.embed_text(chunk.text)
        vector_store.insert(chunk, vec)


class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 3
    min_similarity: Optional[float] = 0.05


class IngestRequest(BaseModel):
    doc_id: str
    title: str
    content: str
    source_type: Optional[str] = "custom"


class LogTroubleshootRequest(BaseModel):
    raw_log: str


SAMPLE_LOG_SCENARIOS = [
    {
        "id": "log-pg-timeout",
        "title": "PostgreSQL Connection Timeout",
        "log": '2026-10-27T10:45:12.304Z ERROR [pool-1-thread-42] service=billing-service trace_id=c4b92e71-9214-419b-a7e8-319a0db14e21 [HikariPool-1] Connection acquisition timed out after 30005ms (active=50, idle=0, waiting=120) ERR_PG_CONN_TIMEOUT: Unable to acquire connection from pool.'
    },
    {
        "id": "log-k8s-oom",
        "title": "Kubernetes Pod OOMKilled",
        "log": '2026-10-27T10:48:02.115Z FATAL pod=recommendation-engine-7c89f5bc-x89zk trace_id=8a1f49e0-f19b-4654-8c01-72901abcf812 container runtime: [cgroup_oom] Container recommendation-engine exceeded memory limit 2048Mi and was terminated. Exit code 137. ERR_K8S_OOMKILLED.'
    },
    {
        "id": "log-redis-failover",
        "title": "Redis Cluster Connection Refused",
        "log": '2026-10-27T10:52:19.882Z WARN service=session-auth trace_id=314b9c10-fa22-498b-9e12-d9812903ab12 [JedisConnectionException] Failed connecting to redis-master.cache.internal:6379; Connection refused. Master failover initiated by Sentinel quorum. ERR_REDIS_CONN_REFUSED.'
    }
]


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "GroundTrace Enterprise RAG & Telemetry Engine",
        "indexed_stats": vector_store.stats()
    }


@app.get("/api/documents")
def get_documents():
    return {
        "documents": ENTERPRISE_DOCS,
        "index_stats": vector_store.stats()
    }


@app.get("/api/sample-logs")
def get_sample_logs():
    return {"samples": SAMPLE_LOG_SCENARIOS}


@app.post("/api/query")
def run_rag_query(req: QueryRequest):
    if not req.query or not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    t_start = time.perf_counter()

    # Step 1: Embed Query with FastEmbed
    t_embed_start = time.perf_counter()
    query_vector = embedder.embed_text(req.query)
    embed_ms = round((time.perf_counter() - t_embed_start) * 1000, 2)

    # Step 2: Vector Search & Retrieval
    t_retrieval_start = time.perf_counter()
    retrieved_chunks = vector_store.search(
        query_vector=query_vector,
        top_k=req.top_k or 3,
        min_threshold=req.min_similarity or 0.05
    )
    retrieval_ms = round((time.perf_counter() - t_retrieval_start) * 1000, 2)

    # Step 3: Context Engineering & Grounded Synthesis
    t_synth_start = time.perf_counter()
    grounded_result = ContextEngine.synthesize_grounded_answer(req.query, retrieved_chunks)
    synth_ms = round((time.perf_counter() - t_synth_start) * 1000, 2)

    total_latency_ms = round((time.perf_counter() - t_start) * 1000, 2)

    # Step 4: LLMOps Quality Evaluation
    faithfulness = RAGEvaluator.evaluate_faithfulness(
        answer=grounded_result["answer"],
        context_block=grounded_result.get("context_block", "")
    )
    relevance = RAGEvaluator.evaluate_context_relevance(
        query=req.query,
        retrieved_chunks=retrieved_chunks
    )

    # Token Accounting & Cost Estimator (~4 chars per token)
    prompt_tokens = len(req.query + grounded_result.get("context_block", "")) // 4
    completion_tokens = len(grounded_result["answer"]) // 4
    total_tokens = prompt_tokens + completion_tokens
    est_cost_usd = round(((prompt_tokens / 1_000_000) * 3.00) + ((completion_tokens / 1_000_000) * 15.00), 6)

    return {
        "query": req.query,
        "answer": grounded_result["answer"],
        "citations": grounded_result["citations"],
        "retrieved_chunks": retrieved_chunks,
        "evaluations": {
            "faithfulness": faithfulness,
            "context_relevance": relevance,
        },
        "telemetry": {
            "total_latency_ms": total_latency_ms,
            "breakdown_ms": {
                "embedding": embed_ms,
                "retrieval": retrieval_ms,
                "synthesis": synth_ms
            },
            "tokens": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens
            },
            "estimated_cost_usd": est_cost_usd
        }
    }


@app.post("/api/troubleshoot-log")
def troubleshoot_log(req: LogTroubleshootRequest):
    if not req.raw_log or not req.raw_log.strip():
        raise HTTPException(status_code=400, detail="Raw log text cannot be empty")

    t_start = time.perf_counter()
    parsed_telemetry = LogTroubleshooter.extract_and_normalize(req.raw_log)
    analysis_ms = round((time.perf_counter() - t_start) * 1000, 2)

    return {
        "status": "SUCCESS",
        "telemetry": parsed_telemetry,
        "analysis_latency_ms": analysis_ms
    }


@app.post("/api/ingest")
def ingest_document(req: IngestRequest):
    chunks = chunker.chunk_document(req.doc_id, req.title, req.content, req.source_type or "custom")
    for chunk in chunks:
        vec = embedder.embed_text(chunk.text)
        vector_store.insert(chunk, vec)

    return {
        "status": "SUCCESS",
        "doc_id": req.doc_id,
        "chunks_created": len(chunks),
        "total_indexed": vector_store.stats()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
