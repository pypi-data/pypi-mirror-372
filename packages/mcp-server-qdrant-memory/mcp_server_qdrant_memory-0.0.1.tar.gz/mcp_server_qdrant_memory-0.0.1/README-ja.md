# MCP Qdrant Memory Server

QdrantベクトルデータベースとSentenceTransformer埋め込みを使用して、持続的メモリとセマンティック検索機能を提供するModel Context Protocol（MCP）サーバーです。FastMCPで構築されています。

## 機能

### メモリ操作
- セマンティック検索を使用した文書の保存と取得
- 複数のテキストソース（テキスト、raw markdown、ヘッダー）のサポート
- SentenceTransformerモデルを使用した自動テキスト埋め込み
- メタデータベースのフィルタリングと検索機能

### コレクション管理
- 動的なコレクション作成と再作成
- 設定可能な次元での名前付きベクトルサポート
- 効率的なメタデータクエリのためのペイロードインデックス作成
- 自動スキーマ検証と互換性チェック

### 検索機能
- **ベクトル検索**: テキスト埋め込みを使用したセマンティック類似度検索
- **ハイブリッド検索**: ベクトルとメタデータフィルタリングの組み合わせ
- **フィルターのみ検索**: ベクトル検索なしの純粋なメタデータベースクエリ
- **バッチ操作**: 効率的な一括アップサートと削除

### トランスポートプロトコル
- **STDIO**（デフォルト）- ローカルツールとClaude Desktopの統合用
- **SSE**（Server-Sent Events）- Webベースデプロイメント用
- **Streamable HTTP** - モダンなHTTPベースプロトコル

## アーキテクチャ

サーバーはクリーンでスケーラブルなアーキテクチャを使用しています：

- **FastMCP統合**: マルチトランスポートサポートを備えたモダンなMCPサーバーフレームワーク
- **Qdrantベクトルデータベース**: 高性能ベクトルストレージと検索
- **SentenceTransformer**: 最先端のテキスト埋め込み生成
- **安定ID生成**: UUIDv5ベースの一貫した文書識別
- **柔軟なテキストソース**: 様々な文書形式と構造のサポート

## インストール

### PyPIからのクイックインストール

PyPIに公開された後、簡単にインストールして実行できます：

```bash
# uvでインストール（推奨）
uvx mcp-server-qdrant-memory  # インストールなしで直接実行

# またはpipでインストール
pip install mcp-server-qdrant-memory
```

### ソースからのインストール

#### 前提条件

仮想環境を作成してアクティブ化します：

```bash
python -m venv venv

# Windows の場合
.\venv\Scripts\Activate.ps1

# Linux/macOS の場合
source venv/bin/activate
```

### 基本インストール

プロジェクトを編集可能モードでインストールします：

#### 本番環境用

```bash
pip install -e "."
```

#### 開発環境用

開発ツールを含めてインストールします：

```bash
pip install -e ".[dev]"
```

### 依存関係

**コア依存関係**（自動的にインストールされます）:
- `mcp>=1.9.4` - Model Context Protocolライブラリ
- `fastmcp>=2.3.0` - モダンなMCPサーバーフレームワーク
- `qdrant_client>=1.14.3` - Qdrantベクトルデータベースクライアント
- `sentence-transformers>=5.0.0` - テキスト埋め込みモデル

**開発依存関係**（`[dev]`でインストールされます）:
- `pylint` - コードリンティング
- `pylint-plugin-utils` - Pylintユーティリティ
- `pylint-mcp` - MCP固有のリンティングルール
- `black` - コードフォーマッティング

### インストール例

#### クイックスタート（本番環境）
```bash
# クローンとインストール
git clone <repository-url>
cd mcp-server-qdrant-memory
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
pip install -e "."
```

#### 開発者セットアップ
```bash
# クローンと開発環境のセットアップ
git clone <repository-url>
cd mcp-server-qdrant-memory
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
pip install -e ".[dev]"

# 開発ツールの実行
black src/
pylint src/
```

## 設定

サーバーは環境変数を通じて設定されます：

### 必要なセットアップ

1. **Qdrantサーバー**: Qdrantインスタンスを開始
```bash
# Dockerを使用
docker run -p 6333:6333 qdrant/qdrant
```

2. **環境変数**（オプション、デフォルト値あり）:
```bash
export QDRANT_URL="http://127.0.0.1:6333"           # QdrantサーバーURL
export QDRANT_API_KEY=""                             # APIキー（必要な場合）
export QDRANT_COLLECTION_NAME="kakehashi_rag_v2"    # コレクション名
export QDRANT_VECTOR_NAME="fast-all-minilm-l6-v2"   # 名前付きベクトル識別子
export EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"  # 埋め込みモデル
export EMBEDDING_BATCH="64"                         # 埋め込みのバッチサイズ
export MCP_TRANSPORT="stdio"                        # トランスポートプロトコル
```

## 使用方法

### コマンドラインオプション

```bash
mcp-server-qdrant-memory --help
```

### 開発モード

FastMCPのインスペクター付き開発モードを使用：
```bash
fastmcp dev src/qdrant_memory_server/main.py
```

### MCP Inspector

MCP Inspectorを使用してMCPサーバーをインタラクティブにテストとデバッグできます：

```bash
# MCP Inspectorをインストールして実行
npx @modelcontextprotocol/inspector
```

MCP Inspectorは次の機能を提供するWebベースインターフェースです：
- 利用可能なすべてのツールのテスト
- ツールスキーマとドキュメントの表示
- サーバーレスポンスのデバッグ
- サーバーログの監視

## 統合例

### Claude Desktop統合

Claude DesktopのMCP設定に追加：

```json
{
  "mcpServers": {
    "qdrant-memory": {
      "command": "mcp-server-qdrant-memory",
      "args": [],
      "env": {
        "QDRANT_URL": "http://localhost:6333",
        "QDRANT_COLLECTION_NAME": "claude_memory"
      }
    }
  }
}
```

またはPyPI公開後は、自動インストールのためにuvxを使用：

```json
{
  "mcpServers": {
    "qdrant-memory": {
      "command": "uvx",
      "args": ["mcp-server-qdrant-memory"],
      "env": {
        "QDRANT_URL": "http://localhost:6333",
        "QDRANT_COLLECTION_NAME": "claude_memory"
      }
    }
  }
}
```
