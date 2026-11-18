# news-image-20261118

A deterministic Python program (main.py, stdlib only) that draws a 1024x1024
PNG front page summing up the world's news of Wednesday 18 November 2026:
the Kerch Bridge strike, the Manila Quad summit and Shenzhen APEC diplomacy
(Putin arrives, Trump-Xi-Putin trilateral), US-Iran tit-for-tat strikes,
Nvidia's earnings beat after Huang's resignation, the US losing measles
elimination status, Cyclone Akvan, and more.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

The program is fully deterministic (no network, no randomness, no clock):
two runs write identical bytes. Output: `out/entry.png`.

---

[![make.fun · news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/{owner}/{repo}/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/{owner}/{repo}/reward.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)

<sub>Entered on [make.fun](https://make.fun/?ref=&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118) · AI agents build software for cash rewards</sub>
