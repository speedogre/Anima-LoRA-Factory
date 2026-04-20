# Anima LoRA Factory 🚀

<img src="https://github.com/UNfukashigi/Anima-LoRA-Factory/blob/main/image.png">

Anima LoRA Factory は、次世代画像生成モデル Anima の LoRA 学習を、プログラミングの知識なしで誰でも簡単に行えるように設計された GUI ツールです。 特に最新の NVIDIA RTX 50シリーズ (Blackwell / sm_120) への対応や、複雑な環境構築の自動化にこだわっています。

> Anima LoRA Factory is a user-friendly GUI tool designed for training LoRAs for the next-generation Anima diffusion models. It simplifies the complex setup process and offers native support for the latest NVIDIA RTX 50 Series (Blackwell / sm_120) GPUs.

▼SDXLバージョンも公開しています。SDXL version is also available.<br>
[https://github.com/UNfukashigi/SDXL-LoRA-Factory](https://github.com/UNfukashigi/SDXL-LoRA-Factory)

## 🌟 主な機能 / Key Features
### ✅全自動環境構築 / Auto Setup
start.bat を実行するだけで、必要な学習エンジン (sd-scripts) やハードウェアに最適な PyTorch を自動的にセットアップします。
### ✅ビジュアルタグエディタ / Visual Tag Editor
画像を見ながら直感的にキャプション（タグ）を編集可能。WD14 Tagger による自動タグ付け機能も内蔵しています。
### ✅リアルタイム進捗 / Real-time Progress
学習の進捗状況をプログレスバーとブラウザのタブタイトルでリアルタイムに確認できます。
### ✅Blackwell (RTX 50) 対応 / Blackwell Ready
最新GPUで発生しがちな CUDA エラーを自動検知し、最適な環境（CUDA 13.0 等）を構成します。
### ✅自動シャットダウン / Auto Shutdown
長時間の学習完了後に PC を自動でシャットダウンするオプションを搭載。
### ✅ComfyUI 変換機能 / ComfyUI Conversion
学習完了後、自動的に ComfyUI で即座に使用可能な形式へ変換・出力します。

## 📋 動作要件 / Requirements
- Python: Python 3.10+ (Add to PATH を忘れずに)
- Git: Git for Windows
- GPU: NVIDIA GPU (VRAM 8GB以上推奨)

## 🚀 使い方
1. ダウンロード: このリポジトリを[ダウンロード](https://github.com/UNfukashigi/Anima-LoRA-Factory/archive/refs/heads/main.zip)（または git clone）して展開します。
1. 起動: フォルダ内の start.bat をダブルクリックします。
1. 初期設定: 黒い画面（コマンドプロンプト）で環境構築が始まります。完了すると自動的にブラウザで GUI が開きます。
1. 学習開始: 画像フォルダを指定し、必要に応じてタグを編集します。Anima Base Model, VAE, Qwen3 のパスを指定します。「LoRA学習開始」ボタンを押せばトレーニングが始まります！

## 🚀 How to Use
1. Download: Download or git clone this repository.
1. Launch: Double-click start.bat.
1. Initialization: The terminal will automatically setup the environment. The GUI will open in your browser once ready.
1. Start Training: Set your dataset path, configure model paths, and click "Start Training"!

## 🔗 参考・クレジット / References & Credits
このプロジェクトは、以下の素晴らしいリポジトリおよびモデルの成果に基づいています。

- Anima Model: [circlestone-labs/Anima (HuggingFace)](https://huggingface.co/circlestone-labs/Anima)
- Training Engine: [kohya-ss/sd-scripts](https://github.com/kohya-ss/sd-scripts)
- Anima Training Docs: [sd-scripts/anima_train_network.md](https://github.com/kohya-ss/sd-scripts/blob/main/docs/anima_train_network.md)

## 🔑License
This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 📝 免責事項 / Disclaimer
本ツールを使用して作成されたモデルや、その使用によって生じた損害について、開発者は一切の責任を負いません。 The developer is not responsible for any models created using this tool or any damage caused by its use.

Created by [fukachan.jp](https://fukachan.jp/)
