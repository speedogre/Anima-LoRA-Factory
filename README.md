# Anima LoRA Factory 🚀

<img src="https://github.com/UNfukashigi/Anima-LoRA-Factory/blob/main/image.png">

Anima LoRA Factory は、次世代画像生成モデル Anima の LoRA 学習を、プログラミングの知識なしで誰でも簡単に行えるように設計された GUI ツールです。 特に最新の NVIDIA RTX 50シリーズ (Blackwell / sm_120) への対応や、複雑な環境構築の自動化にこだわっています。

> Anima LoRA Factory is a user-friendly GUI tool designed for training LoRAs for the next-generation Anima diffusion models. It simplifies the complex setup process and offers native support for the latest NVIDIA RTX 50 Series (Blackwell / sm_120) GPUs.

▼リポジトリをダウンロードする - Download the repository<br>
[https://github.com/UNfukashigi/Anima-LoRA-Factory/archive/refs/heads/main.zip](https://github.com/UNfukashigi/Anima-LoRA-Factory/archive/refs/heads/main.zip)

▼SDXLバージョンも公開しています。- SDXL version is also available.<br>
[https://github.com/UNfukashigi/SDXL-LoRA-Factory](https://github.com/UNfukashigi/SDXL-LoRA-Factory)

▼詳しい使い方については、以下の記事をご覧ください。- For detailed instructions on how to use it, please see the article below.<br>
[https://x.com/UNfukashigi/status/2045744319433490449](https://x.com/UNfukashigi/status/2045744319433490449)

---

<code>4/26 更新（Updated）**v2.2**<br>
・エラー報告の多かった原因のsd-scriptsを同梱しました。ZIP形式での配布に変更。Gitは不要になりました。- We've included sd-scripts, which were the cause of many error reports.Distribution format changed to ZIP.Git is no longer needed.</code>

<code>4/26 更新（Updated）**v2.1**<br>
・エラー報告の多かった原因として、PCのグローバル環境で環境変数PYTHONPATHが設定されている場合について、必ずvenv環境のPythonを利用するように更新しました。- Due to a high number of error reports, we have updated the code to always use the Python environment in a venv environment when the environment variable PYTHONPATH is set in the PC's global environment.</code>

<code>4/25 更新（Updated）<br>
・venv環境をツール内に構築する設計にしました。グローバル環境に影響を与えず、より安心してご利用頂けます。- The design now incorporates a venv environment within the tool. This ensures that it does not affect the global environment and can be used with greater peace of mind.<br>
・より安定して使えるようにモジュールチェック機能を強化し、自動インストールの機能も強化しました。- The module check function has been enhanced for greater stability, and the automatic installation function has also been improved.
・Anima版とSDXL版でURL（ポート番号）を分けました。キャッシュが被らないので表示も安定するはず。- I've separated the URLs (port numbers) for the Anima and SDXL versions. This should prevent cache conflicts and improve display stability.</code>

---

<code>Further modifications have been made so that the following people can also use it.
People using an NVIDIA GPU that is not the latest model.
People who already have the CPU version of PyTorch installed on their PC.
People whose torchvision has mysteriously disappeared.
People who do not have a GPU (or have an AMD/Intel GPU).</code>

---

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
- **OS**: Windows 10/11
- **GPU**: NVIDIA GPU (VRAM 8GB 以上推奨)
- **Python**: 3.10 以上

## 🚀 使い方
1. ダウンロード: Anima-LoRA-Factory-v2.2.zipをダウンロードして解凍してください。
1. 起動: フォルダ内の start.bat をダブルクリックします。
1. 初期設定: 黒い画面（コマンドプロンプト）で環境構築が始まります。完了すると自動的にブラウザで GUI が開きます。
1. 学習開始: 画像フォルダを指定し、必要に応じてタグを編集します。Anima Base Model, VAE, Qwen3 のパスを指定します。「LoRA学習開始」ボタンを押せばトレーニングが始まります！

## 🚀 How to Use
1. Download: Download Anima-LoRA-Factory-v2.2.zip.
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
