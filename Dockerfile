# Python の公式イメージをベースにする
FROM python:3.12-slim-bookworm

# 作業ディレクトリを設定
WORKDIR /app

# 依存関係をインストール
RUN apt-get update && apt-get install -y build-essential ffmpeg

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# audio-separator の依存関係をインストール
# audio-separator は onnxruntime に依存するため、CPU版を明示的にインストール
RUN pip install --no-cache-dir "audio-separator[cpu]"

# アプリケーションコードをコピー
COPY . .

# コンテナ起動時に実行されるコマンド (ここでは何も実行しないが、必要に応じて追加)
CMD ["/bin/bash"]