<div align="center">

<p align="center"><b>English</b> | <a href="README.ja.md">日本語</a></p>

<h1 align="center">Othello CLI</h1>

<h3 align="center">Play Othello in your terminal.</h3>

<p align="center">Play Othello (Reversi) against a 5-level AI. Installs as the <code>othello</code> command.</p>

<p align="center">
  <a href="https://github.com/Lapius7/cli-othello/releases"><img alt="Release" src="https://img.shields.io/github/v/release/Lapius7/cli-othello?label=release&style=flat-square&color=e8833a&logo=github"></a>
  <a href="https://www.npmjs.com/package/@lapius/cli-othello"><img alt="npm" src="https://img.shields.io/npm/v/@lapius/cli-othello?style=flat-square&color=cb3837&logo=npm"></a>
  <a href="https://pypi.org/project/cli-othello/"><img alt="PyPI" src="https://img.shields.io/pypi/v/cli-othello?style=flat-square&color=3776ab&logo=pypi&logoColor=white"></a>
  <a href="LICENSE"><img alt="License" src="https://img.shields.io/github/license/Lapius7/cli-othello?style=flat-square&color=97ca00"></a>
  <a href="https://github.com/Lapius7/cli-othello/stargazers"><img alt="Stars" src="https://img.shields.io/github/stars/Lapius7/cli-othello?style=flat-square&color=e3b341&logo=github"></a>
  <a href="https://github.com/Lapius7/cli-othello/commits/main"><img alt="Last commit" src="https://img.shields.io/github/last-commit/Lapius7/cli-othello?label=last%20commit&style=flat-square&color=2f81f7"></a>
</p>

<p align="center"><a href="#install">Install</a> · <a href="#usage">Usage</a> · <a href="#ai-levels">AI levels</a> · <a href="#requirements">Requirements</a></p>

</div>

---

## Install

Use pnpm. Installing with both npm and pnpm registers the same command twice, so use `pnpm add -g` only.

```bash
pnpm add -g @lapius/cli-othello
```

This installs the `othello` command. It needs Node.js 18+ and Python 3.9+.

With pip:

```bash
pip install cli-othello
```

On Windows, curses needs `windows-curses`. pip installs it automatically. If you installed with npm, run `py -m pip install windows-curses`.

## Usage

```bash
othello
```

A screen to choose the AI level (Lv.1 to Lv.5) appears before the game. To skip it:

```bash
othello --level 3     # or -l 3
othello --version     # or -V
```

### Keys

| Key | Action |
| --- | --- |
| Arrow keys (or h/j/k/l) | Move the cursor |
| Enter / Space | Place a disc at the cursor |
| q | Quit |

On the board, the squares where you can play are marked with a green `·`.

## AI levels

| Level | Description |
| --- | --- |
| Lv.1 (beginner) | Highly random; plays almost at will |
| Lv.2 (easy) | Shallow search plus positional weights of the squares |
| Lv.3 (medium) | Also weighs corners, edges and the number of available moves (mobility) |
| Lv.4 (hard) | Looks further ahead while evaluating the board |
| Lv.5 (strongest) | Deepest search of the five levels |

The AI uses minimax with alpha-beta pruning; search depth and evaluation detail grow with the level. In the endgame, Lv.3 to Lv.5 switch to an exact solver once 8, 9 and 10 squares or fewer remain, respectively.

> [!NOTE]
> The old README said Lv.5 searches "up to 6 plies" and that the terminal must be 57x36. Neither matched the code: Lv.5 searches 4 plies in the middle game, and the minimum is 56 columns by 27 rows. Game play itself was not run for this rewrite (unverified).

## Requirements

- Python 3.9+ (and Node.js 18+ if installed with npm)
- A terminal of at least 56 columns by 27 rows. The board is drawn larger when the terminal is at least 56 by 35.

## License

MIT ([LICENSE](LICENSE))
