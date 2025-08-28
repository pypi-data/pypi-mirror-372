# run_qdrant_mcp_server.py  — v5安定ID & テキストフォールバック対応版
# import json
import os
import sys
import uuid
from typing import Any, Dict, List, Optional, cast, Literal

import requests
from fastmcp.server import FastMCP
from qdrant_client import QdrantClient
from qdrant_client.http import models as qm
from qdrant_client.http.exceptions import UnexpectedResponse
from sentence_transformers import SentenceTransformer

# ====== 1) 設定 ======
QDRANT_URL = os.getenv("QDRANT_URL", "http://127.0.0.1:6333")
QDRANT_API = os.getenv("QDRANT_API_KEY", None)
COLLECTION = os.getenv("QDRANT_COLLECTION_NAME", "kakehashi_rag_v2")
VECTOR_NAME = os.getenv("QDRANT_VECTOR_NAME", "fast-all-minilm-l6-v2")  # 例: dense_text にも変更可
EMB_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
EMB_BATCH = int(os.getenv("EMBEDDING_BATCH", "64"))
TRANSPORT = os.getenv("MCP_TRANSPORT", "stdio")

print(f"[init] QDRANT_URL={QDRANT_URL}", file=sys.stderr)
print(f"[init] COLLECTION={COLLECTION}, VECTOR_NAME={VECTOR_NAME}", file=sys.stderr)
print(f"[init] EMB_MODEL={EMB_MODEL}, BATCH={EMB_BATCH}", file=sys.stderr)

# UUIDv5 用の安定名前空間（コレクション単位で固定）
UUID_NS = uuid.uuid5(uuid.NAMESPACE_URL, f"kakehashi:{COLLECTION}")

# ====== 2) クライアント/モデル初期化 ======
qc = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API, timeout=30)
model = SentenceTransformer(EMB_MODEL, device="cpu")  # CPUでOK
try:
    test_vec = model.encode(["test"], batch_size=1, normalize_embeddings=True)[0].tolist()
    print(f"[init] embed dim={len(test_vec)}", file=sys.stderr)
except (ValueError, TypeError, ImportError, OSError) as e:
    print(f"[init] embedding failed: {e}", file=sys.stderr)
    raise

# コレクション整合チェック（存在時のみ）
try:
    info = qc.get_collection(COLLECTION)
    vcfg = info.config.params.vectors
    if isinstance(vcfg, dict):
        assert VECTOR_NAME in vcfg, f"Collection has no vector named '{VECTOR_NAME}'. Available={list(vcfg.keys())}"
        size = vcfg[VECTOR_NAME].size
    else:
        size = getattr(vcfg, "size", None)
        if size is None:
            raise ValueError("Vector config size is None")
        if VECTOR_NAME != "":
            print(
                f"[warn] collection is single-vector. VECTOR_NAME='{VECTOR_NAME}' may not match its actual name.",
                file=sys.stderr,
            )
    assert size == len(test_vec), f"Vector dim mismatch: collection={size}, embed={len(test_vec)}"
    print(f"[init] collection OK (dim={size})", file=sys.stderr)
except (
    ValueError,
    AssertionError,
    ImportError,
    UnexpectedResponse,
    requests.RequestException,
) as e:
    print(f"[init] skip schema check (might be creating later): {e}", file=sys.stderr)


# ====== 3) 共通ユーティリティ ======
def ensure_uuid(given_id: Optional[Any], section_path: Optional[str] = None) -> str:
    """
    IDが未指定/空なら:
      - section_path から UUIDv5 を生成（安定上書き用）
      - section_path も無ければ UUIDv4 にフォールバック（基本はsection_pathがあるのでこれはあまり使わない）
    """
    if given_id not in (None, "", []):
        return given_id
    if section_path:
        return str(uuid.uuid5(UUID_NS, section_path))
    return str(uuid.uuid4())


def pick_text_for_embedding(pl: Dict[str, Any]) -> str:
    """
    埋め込み本文の選択: text → raw_md → headers(join) → '' の順でフォールバック
    """
    txt = pl.get("text")
    if isinstance(txt, str) and txt.strip():
        return txt
    raw = pl.get("raw_md")
    if isinstance(raw, str) and raw.strip():
        return raw
    headers = pl.get("headers")
    if isinstance(headers, list) and headers:
        try:
            j = " / ".join(str(h) for h in headers if h)
            if j.strip():
                return j
        except (TypeError, ValueError):
            pass
    return ""


def embed_texts(texts: List[str]) -> List[List[float]]:
    # Cosine 前提→正規化ONで安定化
    embs = model.encode(texts, batch_size=EMB_BATCH, normalize_embeddings=True)
    return [e.tolist() for e in embs]


def build_filter(f: Optional[Dict[str, Any]]) -> Optional[qm.Filter]:
    if not f:
        return None

    def _build_clause(clause: List[Dict[str, Any]]) -> List[qm.Condition]:
        out = []
        for cond in clause:
            key = cond.get("key")
            if key is None:
                continue

            if "match" in cond:
                out.append(qm.FieldCondition(key=key, match=qm.MatchValue(value=cond["match"]["value"])))
            elif "in" in cond:
                out.append(qm.FieldCondition(key=key, match=qm.MatchAny(any=cond["in"])))
            elif "range" in cond:
                out.append(qm.FieldCondition(key=key, range=qm.Range(**cond["range"])))
            else:
                raise ValueError(f"Unsupported condition: {cond}")
        return out

    return qm.Filter(
        must=_build_clause(f.get("must", [])),
        should=_build_clause(f.get("should", [])),
        must_not=_build_clause(f.get("must_not", [])),
    )


# ====== 4) MCP アプリ ======
app = FastMCP()


@app.tool(name="qdrant_recreate_collection", description="コレクションを削除→作成（named vector対応 / 既存は削除）")
def recreate_collection(collection_name: Optional[str] = None, dim: int = 384, distance: str = "COSINE") -> str:
    name = collection_name or COLLECTION
    try:
        try:
            qc.delete_collection(name)
            print(f"[recreate] deleted {name}", file=sys.stderr)
        except (UnexpectedResponse, requests.RequestException):
            pass
        qc.create_collection(
            collection_name=name,
            vectors_config={VECTOR_NAME: qm.VectorParams(size=dim, distance=getattr(qm.Distance, distance))},
            on_disk_payload=True,
        )
        return f"Recreated '{name}' with named vector '{VECTOR_NAME}' dim={dim} distance={distance}"
    except (ValueError, UnexpectedResponse, requests.RequestException) as e:
        return f"Error: {e}"


@app.tool(name="qdrant_create_payload_indexes", description="payload index をまとめて作成（keyword/datetime/integer）")
def create_payload_indexes(fields: Dict[str, str], collection_name: Optional[str] = None) -> str:
    """
    fields 例:
      {"doc_type":"keyword","section_path":"keyword","tags":"keyword","lang":"keyword","ingested_at":"datetime","authority":"integer"}
    """
    name = collection_name or COLLECTION
    try:
        for k, typ in fields.items():
            if typ == "keyword":
                schema = qm.PayloadSchemaType.KEYWORD
            elif typ == "datetime":
                schema = qm.PayloadSchemaType.DATETIME
            elif typ == "integer":
                schema = qm.PayloadSchemaType.INTEGER
            else:
                raise ValueError(f"Unsupported index type: {typ}")
            qc.create_payload_index(name, field_name=k, field_schema=schema)
            print(f"[index] {k} -> {typ}", file=sys.stderr)
        return f"Indexed {len(fields)} fields on '{name}'"
    except (ValueError, UnexpectedResponse, requests.RequestException) as e:
        return f"Error: {e}"


@app.tool(
    name="qdrant_upsert_with_metadata",
    description=(
        "points=[{id?, payload{ text か raw_md（無ければ headers）, 任意のメタ }}] を upsert。\n" "id未指定なら section_path から UUIDv5 を生成（安定上書き）。"
    ),
)
def upsert_with_metadata(points: List[Dict[str, Any]], collection_name: Optional[str] = None) -> str:
    name = collection_name or COLLECTION
    try:
        texts, ids, payloads = [], [], []
        for p in points:
            pl = p.get("payload") or {}

            # 埋め込み本文を選択（chunk: text / doc: raw_md / 最後に headers）
            txt = pick_text_for_embedding(pl)
            if not txt:
                return "Error: payload.text も raw_md も headers も見つかりません。埋め込み用の本文が必要です。"
            texts.append(txt)

            # section_path を優先（chunk で未設定なら chunk_of + chunk_index から擬似生成）
            sp = pl.get("section_path")
            if not sp and pl.get("doc_type") == "chunk":
                base = pl.get("chunk_of", "")
                idx = pl.get("chunk_index", None)
                if base and idx is not None:
                    try:
                        sp = f"{base}.c{int(idx):04d}"
                    except (ValueError, TypeError):
                        sp = None

            ids.append(ensure_uuid(p.get("id"), section_path=sp))
            payloads.append(pl)

        vectors = embed_texts(texts)
        qpoints = [qm.PointStruct(id=i, vector={VECTOR_NAME: v}, payload=pl) for i, v, pl in zip(ids, vectors, payloads)]
        qc.upsert(collection_name=name, points=qpoints, wait=True)
        return f"Upserted {len(qpoints)} points into '{name}'."
    except (
        ValueError,
        TypeError,
        UnexpectedResponse,
        requests.RequestException,
    ) as e:
        print(f"[upsert] {e}", file=sys.stderr)
        return f"Error: {e}"


@app.tool(name="qdrant_advanced_search", description="ベクトル＋payload filter 検索。query_text を埋め込み、limit件返す。")
def advanced_search(
    query_text: str, metadata_filter: Optional[Dict[str, Any]] = None, limit: int = 8, collection_name: Optional[str] = None
) -> List[Dict[str, Any]]:
    name = collection_name or COLLECTION
    try:
        qv = embed_texts([query_text])[0]
        flt = build_filter(metadata_filter)
        print(f"[search] name={name} limit={limit} filter={metadata_filter}", file=sys.stderr)
        hits = qc.search(collection_name=name, query_vector=(VECTOR_NAME, qv), query_filter=flt, with_payload=True, limit=limit)
        return [h.model_dump() for h in hits]
    except (
        ValueError,
        TypeError,
        UnexpectedResponse,
        requests.RequestException,
    ) as e:
        print(f"[search] {e}", file=sys.stderr)
        return [{"error": str(e)}]


@app.tool(name="qdrant_filter_only_search", description="ベクトル検索を行わず、metadata_filterのみで全ての条件に一致するポイントを取得します。")
def filter_only_search(metadata_filter: Dict[str, Any], limit: int = 100, collection_name: Optional[str] = None) -> List[Dict[str, Any]]:
    name = collection_name or COLLECTION
    try:
        flt = build_filter(metadata_filter)
        if flt is None:
            return [{"error": "metadata_filter is required for this tool."}]

        print(f"[scroll] name={name} limit={limit} filter={metadata_filter}", file=sys.stderr)

        scroll_response, _ = qc.scroll(collection_name=name, scroll_filter=flt, with_payload=True, limit=limit)
        return [h.model_dump() for h in scroll_response]
    except (
        ValueError,
        TypeError,
        UnexpectedResponse,
        requests.RequestException,
    ) as e:
        print(f"[scroll] {e}", file=sys.stderr)
        return [{"error": str(e)}]


@app.tool(name="qdrant_delete_by_filter", description="Filter 条件でポイントを削除")
def delete_by_filter(metadata_filter: Optional[Dict[str, Any]] = None, collection_name: Optional[str] = None) -> str:
    name = collection_name or COLLECTION
    try:
        flt = build_filter(metadata_filter)
        if flt is None:
            return "Error: metadata_filter is required for this tool."
        qc.delete(name, points_selector=qm.FilterSelector(filter=flt), wait=True)
        return f"Deleted points in '{name}' by filter."
    except (
        ValueError,
        TypeError,
        UnexpectedResponse,
        requests.RequestException,
    ) as e:
        return f"Error: {e}"


def main():
    print(f"[run] starting MCP via {TRANSPORT}", file=sys.stderr)
    app.run(transport=cast(Literal["stdio", "sse", "streamable-http"], TRANSPORT))


if __name__ == "__main__":
    main()
