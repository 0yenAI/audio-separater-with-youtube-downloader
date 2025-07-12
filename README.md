# Audio Separator, YouTube Downloader, and MIDI Converter

YouTube動画からお気に入りの音楽をダウンロードして、ボーカルと伴奏をきれいに分離したいと思ったことはありませんか？さらに、その音声からMIDIを生成できたら？このツールがあれば、そんな願いが簡単に叶います！YouTube動画のダウンロードから、高精度なボーカル分離、そしてMIDI変換までを自動化する、あなたのための強力なアシスタントです。ボーカル分離には`audio-separator`、MIDI変換には`basic-pitch`をそれぞれDockerコンテナ内で活用しています。

## 🚀 このツールでできること

*   **YouTube動画をサクッとダウンロード**: `yt-dlp`の力で、お気に入りのYouTube動画をMP4形式で手軽にダウンロードできます。
*   **驚きのボーカル分離**: ダウンロードした動画や、お手持ちの動画ファイルから、ボーカルと伴奏を魔法のように分離します。`MDX23C-8KFFT-InstVoc_HQ.ckpt`という高精度なモデルを使っているので、その仕上がりにはきっと満足いただけるはずです！
*   **音声からMIDIを生成**: 分離したボーカルや伴奏、または任意の音声ファイルから、`basic-pitch`を使ってMIDIファイルを生成します。
*   **親切なユーザー体験**:
    *   処理中は、コンソールにクールなローディングアニメーションが表示されるので、進捗が一目でわかります。
    *   ダウンロードや処理が終わったら、心地よいベルの音（`bell.mp3`）でお知らせします。もう、いつ終わるか画面を睨む必要はありません！
*   **コマンドラインで簡単操作**: `argparse`を使っているので、コマンドラインから直感的に操作できます。複雑な設定は一切不要です！

## 🛠️ 必要なもの

このツールを使うために、以下の準備をお願いします。

*   **Python**: 3.10 以上
*   **uv**: 超高速なPythonパッケージインストーラー
*   **Docker**: コンテナ実行プラットフォーム（ボーカル分離とMIDI変換に必須です）

## ⚙️ セットアップ手順

さあ、ツールを使い始めるための準備をしましょう！

1.  **リポジトリをクローン**:
    ```bash
    git clone <repository_url>
    cd audio-separater-with-youtube-downloader
    ```

2.  **Python仮想環境の作成と有効化**:
    ```bash
    uv venv
    source .venv/bin/activate
    ```

3.  **必要なライブラリをインストール**:
    ```bash
    uv pip install -r requirements.txt
    ```

4.  **Dockerを起動**:
    Docker Desktopを起動して、Dockerデーモンがちゃんと動いていることを確認してくださいね。

5.  **Dockerイメージのビルド**:
    ボーカル分離とMIDI変換には、それぞれ専用のDockerイメージが必要です。以下のコマンドでビルドしてください。

    ```bash
    docker build -t vocal-isolater-audio-separator .
    docker build -t my-basic-pitch-app -f Dockerfile.basic-pitch .
    ```

## 🚀 使い方

準備ができたら、あとはコマンドを実行するだけ！

### YouTube動画をダウンロードしたい場合

```bash
uv run python main.py -d <YouTube_URL>
```

### ローカルの動画ファイルからボーカルを分離したい場合

```bash
uv run python main.py -c "/path/to/your/video.mp4"
```

### 音声ファイルからMIDIを生成したい場合

```bash
uv run python main.py -m "/path/to/your/audio.mp3"
```

## ⚠️ もし困ったら（トラブルシューティング）

*   **Docker関連のエラー**: Dockerが起動しているか、`Dockerfile`が正しく設定されているか、もう一度確認してみてください。特に、`basic-pitch`のDockerイメージはNumPyのバージョンに敏感です。もしエラーが発生した場合は、`Dockerfile.basic-pitch`の内容を確認し、`numpy<2`の制約が正しく適用されているか確認してください。
*   **モデルファイルが見つからないエラー**: `audio-separator`や`basic-pitch`がモデルファイルをダウンロードできない場合は、インターネット接続が安定しているか確認してみましょう。