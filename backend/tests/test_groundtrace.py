"""
Unit and Integration Tests for GroundTrace RAG and Log Diagnostics Engine.
"""
from core.ingestion.chunker import SemanticChunker
from core.embeddings.fast_embed import FastEmbedder
from core.indexing.vector_store import VectorStoreIndex
from core.context.context_engine import ContextEngine
from core.diagnostics.log_analyzer import LogTroubleshooter
from core.llmops.evaluator import RAGEvaluator


def test_semantic_chunker():
    chunker = SemanticChunker(target_chunk_size=100, chunk_overlap=20)
    text = "Section 1: Distributed microservices.\n\nSection 2: High throughput messaging.\n\nSection 3: Database pooling."
    chunks = chunker.chunk_document("doc-test", "Test Doc", text, "test")

    assert len(chunks) > 0
    assert chunks[0].doc_id == "doc-test"
    assert "Section 1" in chunks[0].text


def test_fast_embedder_normalization():
    embedder = FastEmbedder(dimension=64)
    vec1 = embedder.embed_text("Kubernetes container runtime OOM")
    assert len(vec1) == 64
    # Check L2 norm is approximately 1.0
    norm = sum(x * x for x in vec1) ** 0.5
    assert abs(norm - 1.0) < 0.05


def test_vector_store_indexing_and_retrieval():
    embedder = FastEmbedder(dimension=64)
    vector_store = VectorStoreIndex()
    chunker = SemanticChunker(target_chunk_size=200, chunk_overlap=20)

    chunks = chunker.chunk_document(
        "doc-k8s", "Kubernetes Guide",
        "Kubernetes pods are terminated by cgroup OOM killer when memory limit is exceeded.",
        "infra"
    )
    for c in chunks:
        vector_store.insert(c, embedder.embed_text(c.text))

    query_vec = embedder.embed_text("cgroup memory limit OOM killer")
    results = vector_store.search(query_vec, top_k=1, min_threshold=0.01)

    assert len(results) == 1
    assert results[0]["chunk_id"].startswith("doc-k8s")
    assert results[0]["score"] > 0


def test_context_engine_synthesis():
    chunks = [{
        "chunk_id": "c1",
        "score": 0.88,
        "text": "PostgreSQL connection pool exhaustion occurs when max_connections is reached.",
        "metadata": {"doc_title": "Postgres Pool Guide"}
    }]
    res = ContextEngine.synthesize_grounded_answer("How does connection pool exhaustion occur?", chunks)

    assert res["grounded"] is True
    assert len(res["citations"]) == 1
    assert "PostgreSQL connection pool" in res["answer"]


def test_log_troubleshooter_pg_timeout():
    raw_log = '2026-10-27T10:45:12.304Z ERROR service=billing-service trace_id=c4b92e71-9214-419b-a7e8-319a0db14e21 [HikariPool-1] Connection acquisition timed out after 30005ms ERR_PG_CONN_TIMEOUT.'
    parsed = LogTroubleshooter.extract_and_normalize(raw_log)

    assert parsed["log_level"] == "ERROR"
    assert parsed["service_name"] == "billing-service"
    assert parsed["error_code"] == "ERR_PG_CONN_TIMEOUT"
    assert parsed["diagnostics"]["category"] == "Connection Pool Exhaustion"
    assert len(parsed["diagnostics"]["remediation"]) > 0


def test_log_troubleshooter_k8s_oom():
    raw_log = '2026-10-27T10:48:02.115Z FATAL pod=analytics-worker trace_id=8a1f49e0-f19b-4654-8c01-72901abcf812 Container exceeded memory limit 2048Mi. ERR_K8S_OOMKILLED.'
    parsed = LogTroubleshooter.extract_and_normalize(raw_log)

    assert parsed["log_level"] == "FATAL"
    assert parsed["service_name"] == "analytics-worker"
    assert parsed["error_code"] == "ERR_K8S_OOMKILLED"
    assert parsed["diagnostics"]["category"] == "Memory Resource Quota Exceeded"


def test_rag_evaluator_faithfulness():
    context = "Redis Sentinel coordinates quorum voting during automatic master failover."
    answer = "Redis Sentinel coordinates quorum voting during master failover."
    eval_res = RAGEvaluator.evaluate_faithfulness(answer, context)

    assert eval_res["score"] >= 80.0
    assert eval_res["status"] == "GROUNDED"
