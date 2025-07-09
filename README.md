# Vocal Isolater

このプロジェクトは、YouTube動画のダウンロードと、動画からのボーカル分離を自動化するツールです。ボーカル分離にはDockerコンテナ内で`audio-separator`ライブラリを使用します。

## 🚀 実装方法の概要

このツールは、以下の主要なコンポーネントで構成されています。

- **YouTube動画ダウンロード**: `yt-dlp`ライブラリを使用して、指定されたYouTube動画をMP4形式でダウンロードします。
- **ボーカル分離**: `audio-separator`ライブラリをDockerコンテナ内で実行し、ダウンロードした動画ファイルからボーカルと伴奏を分離します。これにより、ローカル環境の依存関係の問題を回避します。
- **コマンドラインインターフェース (CLI)**: `argparse`を使用して、コマンドラインからの操作を可能にします。

## 🛠️ インストールに必要なもの

このプロジェクトを実行するには、以下のものが必要です。

- **Python**: バージョン 3.10 以上
- **uv**: 高速なPythonパッケージインストーラーおよび仮想環境マネージャー
- **Docker**: コンテナ化されたアプリケーションを実行するためのプラットフォーム

## ⚙️ セットアップ手順

以下の手順でプロジェクトをセットアップします。

1.  **リポジトリのクローン**

    ```bash
    git clone https://github.com/your-username/vocal_isolater.git
    cd vocal_isolater
    ```
    (注: `https://github.com/your-username/vocal_isolater.git` はあなたのリポジトリのURLに置き換えてください。)

2.  **Python 仮想環境の作成とアクティベート**

    `uv` を使用してPython 3.10の仮想環境を作成し、アクティベートします。

    ```bash
    uv venv --python python3.10
    source .venv/bin/activate
    ```

3.  **依存関係のインストール**

    `pyproject.toml` に基づいて必要なPythonライブラリをインストールします。

    ```bash
    uv pip install .
    ```

4.  **Docker のインストールと起動**

    まだDockerがインストールされていない場合は、[Docker公式サイト](https://www.docker.com/get-started/) からダウンロードしてインストールしてください。インストール後、Dockerデスクトップアプリケーションを起動し、Dockerデーモンが実行されていることを確認してください。

## 🚀 使い方

`main.py` スクリプトは、コマンドライン引数を受け取ります。

### ボーカル分離

既存の動画ファイルからボーカルを分離します。ファイルパスにスペースが含まれる場合は、パス全体を引用符で囲んでください。

```bash
uv run python main.py -c "/path/to/your/video.mp4"
# 例:
uv run python main.py -c "【歌ってみたコラボ】白い雪のプリンセスは-Re：incarnation- 尾丸ポルカ&小鳩りあ.mp4"
```

### YouTube動画のダウンロード

YouTubeから動画をダウンロードします。ダウンロード後、自動的にボーカル分離処理が開始されます。

```bash
uv run python main.py -d <YouTube_URL_1> <YouTube_URL_2> ...
# 例:
uv run python main.py -d https://www.youtube.com/watch?v=JfQzXhHCmkk
```

## ⚠️ トラブルシューティング

### Docker 関連のエラー

-   **`Unable to find image '...' locally` / `Error response from daemon: pull access denied` / `TLS handshake timeout`**: Dockerイメージのダウンロードに失敗しています。インターネット接続を確認するか、Dockerデーモンを再起動してみてください。ファイアウォールやプロキシの設定も確認してください。
-   **`command 'gcc' failed` / `No such file or directory: 'ffmpeg'`**: Dockerコンテナ内に必要なビルドツールや`ffmpeg`がインストールされていません。`Dockerfile`が正しく設定されているか確認してください。これらのエラーは、通常、Dockerイメージのビルド時に解決されます。

### `audio-separator` 関連のエラー

-   **`ValueError: Model file MDX23C not found in supported model files`**: 指定されたモデル名が`audio-separator`でサポートされていないか、モデルファイル名が正しくありません。`audio-separator`のCLIは`-m MODEL_FILENAME`でモデルファイル名を指定します。利用可能なモデルのリストは、`docker run --rm vocal-isolater-audio-separator audio-separator --list_models` で確認できます。
-   **`unrecognized arguments: --model_name UVR_MDXNET_KARA_2`**: `audio-separator`のCLIは`--model_name`オプションをサポートしていません。`-m MODEL_FILENAME`を使用してください。

## 💡 今後の改善点

-   `audio-separator`のモデル選択をより柔軟にするためのオプション追加。
-   出力ファイル名のカスタマイズオプションの追加。
-   より詳細なログ出力オプションの提供。

