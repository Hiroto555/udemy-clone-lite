# DeepWiki: Udemy Clone Lite

このドキュメントは、Udemy Clone Liteプロジェクトの技術的な詳細、アーキテクチャ、セットアップ方法について解説するものです。

## 1. プロジェクト概要

このプロジェクトは、オンライン学習プラットフォームであるUdemyの主要な機能を模倣したフルスタックアプリケーションです。バックエンドはPythonのフレームワークである**FastAPI**、フロントエンドはReactのフレームワークである**Next.js**を使用して構築されています。

### 主な機能

-   **ユーザー認証:** JWT（JSON Web Token）を利用した登録・ログイン・トークンリフレッシュ機能。
-   **コース管理:** 講師によるコースの作成、読み取り、更新、削除（CRUD）。
-   **コース検索とフィルタリング:** 公開されているコースをキーワード、タグ、価格帯で検索・絞り込み。
-   **受講登録:** 生徒は興味のあるコースに登録できます。
-   **レビュー機能:** 受講登録したユーザーはコースに対して評価とコメントを投稿できます。
-   **ダッシュボード:** ユーザーは自身が作成したコースや受講中のコースを確認できます。

---

## 2. アーキテクチャと技術スタック

このアプリケーションは、バックエンドAPIとフロントエンドUIが明確に分離された構成になっています。

### アーキテクチャ図（テキストベース）

```
+-----------------+      +----------------------+      +----------------+
|   Web Browser   | <--> |  Frontend (Next.js)  | <--> | Backend (FastAPI)|
+-----------------+      +----------------------+      +----------------+
       |                                                    |
       | (HTTP/S)                                           | (SQL)
       |                                                    v
       +-----------------------------------------------> +----------------+
                                                         |   Database     |
                                                         |   (SQLite)     |
                                                         +----------------+
```

### 技術スタック

#### バックエンド

-   **フレームワーク:** [FastAPI](https://fastapi.tiangolo.com/)
-   **ORM:** [SQLModel](https://sqlmodel.tiangolo.com/) (SQLAlchemy + Pydantic)
-   **データベース:** [SQLite](https://www.sqlite.org/index.html) (開発用)
-   **認証:** [JWT (python-jose)](https://github.com/mpdavis/python-jose)
-   **非同期サーバー:** [Uvicorn](https://www.uvicorn.org/)
-   **パッケージ管理:** [Poetry](https://python-poetry.org/)
-   **データベースマイグレーション:** [Alembic](https://alembic.sqlalchemy.org/en/latest/)
-   **テスト:** [Pytest](https://docs.pytest.org/)

#### フロントエンド

-   **フレームワーク:** [Next.js](https://nextjs.org/) (App Router)
-   **UIライブラリ:** [React](https://react.dev/)
-   **スタイリング:** [Tailwind CSS](https://tailwindcss.com/)
-   **UIコンポーネント:** [shadcn/ui](https://ui.shadcn.com/) (Radix UI + Tailwind CSS)
-   **アイコン:** [Lucide React](https://lucide.dev/)
-   **認証:** [js-cookie](https://github.com/js-cookie/js-cookie) でJWTを管理
-   **テスト:** [Vitest](https://vitest.dev/) + [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)

---

## 3. プロジェクト構造

リポジトリは`backend`と`frontend`の2つの主要なディレクトリで構成されています。

```
.
├── backend/         # FastAPIバックエンド
├── frontend/        # Next.jsフロントエンド
├── docker-compose.yml # Dockerによるフルスタック起動設定
└── DEEPWIKI.md      # このドキュメント
```

---

## 4. バックエンド詳解

### ディレクトリ構造

```
backend/
├── app/
│   ├── api/
│   │   ├── deps/      # 依存性注入（DBセッション、認証ユーザー取得など）
│   │   └── v1/        # API v1のエンドポイント定義
│   ├── core/        # 設定、セキュリティ関連
│   ├── crud/        # データベースのCRUD操作
│   ├── db/          # データベースのセッション管理、初期化
│   ├── models/      # SQLModelのモデル定義
│   └── schemas/     # Pydanticのスキーマ定義
├── tests/           # テストコード
├── alembic.ini      # Alembicの設定ファイル
└── pyproject.toml   # Poetryの依存関係・プロジェクト設定
```

### データベーススキーマ

`SQLModel`を使用して、Pythonのクラスとしてスキーマが定義されています。

-   **User:** ユーザーモデル。`is_superuser`フラグを持つ。
    -   `id`, `email`, `full_name`, `hashed_password`, `is_active`, `is_superuser`
-   **Course:** コースモデル。`User`と`instructor`としてリレーションを持つ。
    -   `id`, `title`, `description`, `price`, `instructor_id`, `is_published`
-   **Enrollment:** 受講登録モデル。`User`と`Course`の中間テーブル。
    -   `id`, `user_id`, `course_id`, `enrolled_at`, `progress`
-   **Review:** レビューモデル。`User`と`Course`に紐づく。
    -   `id`, `course_id`, `user_id`, `rating`, `comment`
-   **Tag:** タグモデル。`Course`と多対多のリレーションを持つ。
    -   `id`, `name`, `slug`

### APIエンドポイント

APIは`/api/v1`プレフィックスを持ちます。

-   **`/auth`**: ユーザー認証
    -   `POST /register`: 新規ユーザー登録
    -   `POST /login`: ログイン（JWT発行）
    -   `POST /refresh`: アクセストークンのリフレッシュ
-   **`/courses`**: コース関連
    -   `GET /`: 公開コース一覧（検索・フィルタ可能）
    -   `GET /my`: 自分が作成したコース一覧
    -   `POST /`: 新規コース作成 (要認証)
    -   `GET /{course_id}`: コース詳細
    -   `PUT /{course_id}`: コース更新 (要認証/作成者のみ)
    -   `DELETE /{course_id}`: コース削除 (要認証/作成者のみ)
-   **`/enrollments`**: 受講登録関連
    -   `POST /`: コースへの登録 (要認証)
    -   `GET /my`: 自分が受講中のコース一覧
-   **`/tags`**: タグ関連
    -   `GET /`: タグ一覧
    -   `GET /{slug}/courses`: 特定タグのコース一覧

---

## 5. フロントエンド詳解

### ディレクトリ構造

Next.jsのApp Routerに基づいた構造です。

```
frontend/
└── src/
    ├── app/               # ルーティングとページ
    │   ├── (auth)/        # 認証関連ページ（レイアウトグループ）
    │   ├── courses/
    │   │   └── [id]/      # 動的ルーティング（コース詳細）
    │   └── layout.tsx     # ルートレイアウト
    ├── components/        # 再利用可能なコンポーネント
    │   └── ui/            # shadcn/uiのコンポーネント
    ├── contexts/          # グローバルな状態管理（認証など）
    ├── lib/               # ヘルパー関数、APIクライアント
    │   └── api.ts         # バックエンドAPIとの通信クライアント
    └── middleware.ts      # 認証ミドルウェア
```

### API通信 (`lib/api.ts`)

-   `ApiClient`クラスがバックエンドとの通信をすべて担当します。
-   **自動トークンリフレッシュ:** APIリクエストで401エラー（認証切れ）が発生した場合、リフレッシュトークンを使って新しいアクセストークンを自動で再取得し、リクエストを再試行します。
-   **認証情報管理:** JWTはブラウザのCookieに保存され、リクエスト時に自動で`Authorization`ヘッダーが付与されます。

---

## 6. セットアップと実行方法

### Docker Compose (推奨)

プロジェクトのルートディレクトリで以下のコマンドを実行するだけで、バックエンドとフロントエンドが同時に起動します。

```bash
# .envファイルの作成
cp backend/.env.example backend/.env

# Dockerコンテナのビルドとバックグラウンド起動
docker-compose up --build -d
```

-   フロントエンド: `http://localhost:3000`
-   バックエンドAPI (Swagger UI): `http://localhost:8000/docs`

### 個別セットアップ

#### バックエンド

```bash
cd backend

# .envファイルの作成
cp .env.example .env

# 依存関係のインストール
poetry install

# データベースのマイグレーション
poetry run alembic upgrade head

# 開発サーバーの起動
poetry run uvicorn app.main:app --reload
```

#### フロントエンド

```bash
cd frontend

# .env.localファイルを作成し、APIのURLを設定
# NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# 依存関係のインストール
npm install

# 開発サーバーの起動
npm run dev
```
