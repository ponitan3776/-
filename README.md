# まるばつゲーム

Python (Flask) + JavaScript で作ったまるばつゲーム。Render にデプロイできます。

## 特徴

- CPU 対戦（3段階の強さ / ミニマックス法）と 2人対戦
- サーバーはステートレス（盤面はクライアントが保持）なので Render の無料プランでも安定
- 依存は Flask と gunicorn のみ

## ローカルで動かす

```bash
git clone https://github.com/<your-name>/marubatsu.git
cd marubatsu

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python app.py
