# Audio Separator with YouTube Downloader

このプロジェクトは、YouTube動画のダウンロードと、動画からのボーカル分離を自動化するツールです。ボーカル分離にはDockerコンテナ内で`audio-separator`ライブラリを使用します。

## 🚀 機能

- **YouTube動画ダウンロード**: `yt-dlp`ライブラリを使用して、指定されたYouTube動画をMP4形式でダウンロードします。
- **ボーカル分離**: `audio-separator`ライブラリをDockerコンテナ内で実行し、ダウンロードした動画ファイルからボーカルと伴奏を分離します。
  - **モデル**: `MDX23C-8KFFT-InstVoc_HQ.ckpt` を使用して高精度なボーカル分離を実現します。
- **UI/UX**:
  - ヴォーカル分離処理中には、コンソールにローディングアニメーションが表示されます。
  - 各処理（ダウンロード、ヴォーカル分離）の完了時にベル (`bell.mp3`) が鳴り、処理の完了を通知します。
- **CLI**: `argparse`を使用して、コマンドラインからの簡単な操作が可能です。

## 🛠️ 必要なもの

- **Python**: 3.10 以上
- **uv**: 高速なPythonパッケージインストーラー
- **Docker**: コンテナ実行プラットフォーム

## ⚙️ セットアップ

1.  **リポジトリのクローン**:
    ```bash
    git clone <repository_url>
    cd audio-separater-with-youtube-downloader
    ```

2.  **Python仮想環境の作成と有効化**:
    ```bash
    uv venv
    source .venv/bin/activate
    ```

3.  **依存関係のインストール**:
    ```bash
    uv pip install -r requirements.txt
    ```

4.  **Dockerの起動**:
    Docker Desktopを起動し、Dockerデーモンが実行されていることを確認してください。

## 🚀 使い方

### YouTube動画をダウンロード

```bash
python main.py -d <YouTube_URL>
```
### ローカルの動画ファイルからボーカルを分離

```bash
python main.py -c "/path/to/your/video.mp4"
```


## ⚠️ トラブルシューティング

- **Docker関連のエラー**: Dockerが起動しているか、`Dockerfile`が正しく設定されているか確認してください。
- **モデルファイルが見つからないエラー**: `audio-separator`がモデルファイルをダウンロードできない場合、インターネット接続を確認してください。