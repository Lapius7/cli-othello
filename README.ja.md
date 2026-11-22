<div align="center">

<p align="center">
  <img src="docs/images/banner.png" alt="Othello CLI" width="100%">
</p>

<p align="center"><a href="README.md">English</a> | <b>日本語</b></p>

<h1 align="center">Othello CLI</h1>

<h3 align="center">ターミナルでオセロ(リバーシ)を遊べる CLI。</h3>

<p align="center">5段階の強さから選べる AI と対局できます。<code>othello</code> コマンドとして入ります。</p>

<p align="center">
  <a href="https://github.com/Lapius7/cli-othello/releases"><img alt="Release" src="https://img.shields.io/github/v/release/Lapius7/cli-othello?label=release&style=flat-square&color=e8833a&logo=github"></a>
  <a href="https://www.npmjs.com/package/@lapius/cli-othello"><img alt="npm" src="https://img.shields.io/npm/v/@lapius/cli-othello?style=flat-square&color=cb3837&logo=npm"></a>
  <a href="https://pypi.org/project/cli-othello/"><img alt="PyPI" src="https://img.shields.io/pypi/v/cli-othello?style=flat-square&color=3776ab&logo=pypi&logoColor=white"></a>
  <a href="LICENSE"><img alt="License" src="https://img.shields.io/github/license/Lapius7/cli-othello?style=flat-square&color=97ca00"></a>
  <a href="https://github.com/Lapius7/cli-othello/stargazers"><img alt="Stars" src="https://img.shields.io/github/stars/Lapius7/cli-othello?style=flat-square&color=e3b341&logo=github"></a>
  <a href="https://github.com/Lapius7/cli-othello/commits/main"><img alt="Last commit" src="https://img.shields.io/github/last-commit/Lapius7/cli-othello?label=last%20commit&style=flat-square&color=2f81f7"></a>
</p>

<p align="center"><a href="#インストール">インストール</a> · <a href="#使い方">使い方</a> · <a href="#ai-の強さ">AI の強さ</a> · <a href="#必要環境">必要環境</a></p>

</div>

---

## インストール

pnpm を使ってください。npm と pnpm の両方に入れると同じコマンドが二重に登録されるため、`pnpm add -g` だけを使います。

```bash
pnpm add -g @lapius/cli-othello
```

`othello` コマンドが入ります。Node.js 18 以上と Python 3.9 以上が必要です。

pip の場合:

```bash
pip install cli-othello
```

Windows では curses を使うために `windows-curses` が必要です。pip で入れた場合は自動で入ります。npm で入れた場合は `py -m pip install windows-curses` で入れてください。

## 使い方

```bash
othello
```

起動すると、対局前に AI の強さ(Lv.1〜Lv.5)を選ぶ画面が表示されます。選択画面を飛ばすときは次のようにします。

```bash
othello --level 3     # -l 3 でも可
othello --version     # -V でも可
```

### 操作方法

| キー | 動作 |
| --- | --- |
| ↑ / ↓ / ← / →(または h/j/k/l) | カーソル移動 |
| Enter / Space | カーソル位置に着手 |
| q | 終了 |

盤面では、自分が置ける場所が緑色の `·` でハイライトされます。

## AI の強さ

| レベル | 特徴 |
| --- | --- |
| Lv.1 入門 | ランダム性が高く、ほぼ気の向くままに着手 |
| Lv.2 初級 | 浅い探索と、盤面の位置評価を考慮 |
| Lv.3 中級 | 角・辺の重要度や着手可能数(機動力)も評価 |
| Lv.4 上級 | より深く先読みしつつ盤面を評価 |
| Lv.5 最強 | 5段階のうち最も深い探索で着手を選択 |

内部ではミニマックス法とアルファベータ枝刈りを使い、レベルごとに探索の深さと評価関数の細かさを変えています。終盤は、Lv.3〜Lv.5 で空きマスがそれぞれ 8・9・10 以下になると完全読みに切り替わります。

> [!NOTE]
> 旧 README の「Lv.5 は最大6手先」と「端末は 57列 x 36行 以上」は、コードと合っていませんでした。Lv.5 の中盤の探索は 4 手先、必要な端末の大きさは 56列 x 27行 以上です。実際の対局は今回実行しておらず、未検証です。

## 必要環境

- Python 3.9 以上(npm で入れる場合は Node.js 18 以上も)
- 端末は 56列 x 27行 以上。56列 x 35行 以上あると盤面が大きく表示されます。

## ライセンス

MIT([LICENSE](LICENSE))
