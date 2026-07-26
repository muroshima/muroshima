#!/usr/bin/env python3
"""ドット絵ゴリラの SVG を生成する。

1ドット = 1つの <rect>。フレームを複数持ち、CSS の steps() で
切り替えるスプライトアニメーション方式。
グリッド上で組み立てるので左右対称が保証でき、小サイズでも形が崩れない。
"""
import pathlib

W, H = 24, 27

PALETTE = {
    "f": "#453C40",  # 毛（暗）
    "m": "#574C51",  # 毛（中）
    "h": "#6D6065",  # 毛（明）＝腕
    "d": "#2C2527",  # 最暗（眉庇・輪郭）
    "s": "#93807A",  # 素肌（顔・胸）
    "b": "#A28D86",  # 胸のハイライト
    "w": "#F4EFEA",  # 白目
    "k": "#1A1516",  # 瞳・鼻・口
}


class Grid:
    def __init__(self):
        self.g = [["." for _ in range(W)] for _ in range(H)]

    def span(self, y, x0, x1, ch):
        for x in range(x0, x1 + 1):
            if 0 <= x < W and 0 <= y < H:
                self.g[y][x] = ch

    def mspan(self, y, x0, x1, ch):
        """左半分を指定して左右対称に置く"""
        self.span(y, x0, x1, ch)
        self.span(y, W - 1 - x1, W - 1 - x0, ch)

    def px(self, x, y, ch):
        if 0 <= x < W and 0 <= y < H:
            self.g[y][x] = ch

    def mpx(self, x, y, ch):
        self.px(x, y, ch)
        self.px(W - 1 - x, y, ch)

    def copy(self):
        n = Grid()
        n.g = [row[:] for row in self.g]
        return n

    def shift_up(self, n):
        out = Grid()
        for y in range(H):
            src = y + n
            if 0 <= src < H:
                out.g[y] = self.g[src][:]
        return out


HEAD = [(1, 7, 16), (2, 5, 18), (3, 4, 19), (4, 4, 19), (5, 3, 20),
        (6, 3, 20), (7, 3, 20), (8, 4, 19), (9, 4, 19), (10, 5, 18), (11, 7, 16)]
FACE = [(4, 6, 17), (5, 6, 17), (6, 6, 17), (7, 6, 17), (8, 6, 17), (9, 7, 16), (10, 8, 15), (11, 9, 14)]
BODY = [(12, 6, 17), (13, 4, 19), (14, 3, 20), (15, 3, 20), (16, 3, 20),
        (17, 4, 19), (18, 4, 19), (19, 5, 18), (20, 6, 17)]
CHEST = [(14, 9, 14), (15, 8, 15), (16, 8, 15), (17, 8, 15), (18, 9, 14), (19, 10, 13)]


def base(legs=True):
    g = Grid()
    # 頭
    for y, x0, x1 in HEAD:
        g.span(y, x0, x1, "f")
    # 矢状稜
    g.span(0, 9, 14, "m")
    # 耳
    g.mpx(2, 6, "m")
    g.mpx(2, 7, "m")
    # 顔
    for y, x0, x1 in FACE:
        g.span(y, x0, x1, "s")
    # 眉庇（1行だけ。太いと鉢巻きに見える）
    g.span(3, 6, 17, "d")
    # 目（3x2 の白目 + 中央下に瞳。2ドット幅だと瞳が寄り目になる）
    for y in (5, 6):
        g.mspan(y, 7, 9, "w")
    g.mpx(8, 6, "k")
    # 鼻孔（1ドットずつ）
    g.mpx(10, 8, "k")
    # 口
    g.span(10, 10, 13, "k")
    # 胴
    for y, x0, x1 in BODY:
        g.span(y, x0, x1, "f")
    for y, x0, x1 in CHEST:
        g.span(y, x0, x1, "s")
    g.span(16, 10, 13, "b")
    g.span(15, 11, 12, "b")
    if legs:
        # 脚
        for y in (21, 22):
            g.mspan(y, 5, 9, "f")
        g.mspan(23, 4, 9, "f")
        # 足
        g.mspan(24, 3, 9, "s")
    return g


def arms_idle(g):
    for y in range(13, 20):
        g.mspan(y, 3, 5, "h")
    g.mspan(20, 3, 5, "s")   # 手
    return g


def arms_drum(g, left_up):
    """拳を胸に当てた姿勢。left_up=True なら左腕が上・右腕が下"""
    # 上側の腕（拳が胸の上寄り）
    up = [(13, 3, 5), (14, 3, 6), (15, 5, 8)]
    up_fist = (15, 7, 8)
    # 下側の腕（拳が胸の下寄り）
    dn = [(13, 3, 5), (14, 3, 5), (15, 3, 6), (16, 4, 7), (17, 6, 8)]
    dn_fist = (17, 7, 8)

    def put(spans, fist, mirror):
        for y, x0, x1 in spans:
            if mirror:
                g.span(y, W - 1 - x1, W - 1 - x0, "h")
            else:
                g.span(y, x0, x1, "h")
        y, x0, x1 = fist
        if mirror:
            g.span(y, W - 1 - x1, W - 1 - x0, "s")
        else:
            g.span(y, x0, x1, "s")

    put(up if left_up else dn, up_fist if left_up else dn_fist, False)
    put(dn if left_up else up, dn_fist if left_up else up_fist, True)
    return g


def close_eyes(g):
    for y in (5, 6):
        g.mspan(y, 7, 9, "s")
    g.mspan(6, 7, 9, "k")   # 閉じた線
    return g


def jump(g):
    """脚を縮めて全体を持ち上げる"""
    g = g.shift_up(-4) if False else g
    # 脚を短くする
    for y in (21, 22, 23, 24):
        g.span(y, 0, W - 1, ".")
    g.mspan(21, 5, 9, "f")
    g.mspan(22, 4, 9, "s")
    return g


FRAMES = {}
FRAMES["idle"] = arms_idle(base())
FRAMES["blink"] = close_eyes(arms_idle(base()))
FRAMES["drumA"] = arms_drum(base(), left_up=True)
FRAMES["drumB"] = arms_drum(base(), left_up=False)
FRAMES["jump"] = jump(arms_drum(base(legs=False), left_up=True))


def emit_frame(g, fid, dy=0):
    # CSS が無効な環境で全フレームが重なって見えないよう idle 以外は opacity=0。
    # CSS 宣言は presentation attribute より優先されるのでアニメには影響しない。
    fallback = "" if fid == "idle" else ' opacity="0"'
    out = [f'  <g id="{fid}"{fallback}>']
    for y in range(H):
        x = 0
        while x < W:
            ch = g.g[y][x]
            if ch == ".":
                x += 1
                continue
            run = 1
            while x + run < W and g.g[y][x + run] == ch:
                run += 1
            out.append(
                f'    <rect x="{x}" y="{y + dy}" width="{run}" height="1" fill="{PALETTE[ch]}"/>'
            )
            x += run
    out.append("  </g>")
    return "\n".join(out)


# 6秒ループ:
#   0-30%  アイドル（20-24% で瞬き）
#   32-58% ドラミング（A/B を交互に4往復）
#   60-76% ジャンプ
#   78-100% アイドル
CSS = """
      #idle, #blink, #drumA, #drumB, #jump { animation-duration: 6s; animation-iteration-count: infinite; animation-timing-function: steps(1, end); }
      #idle  { animation-name: fIdle; }
      #blink { animation-name: fBlink; }
      #drumA { animation-name: fDrumA; }
      #drumB { animation-name: fDrumB; }
      #jump  { animation-name: fJump; }
      #shadow { animation: fShadow 6s steps(1, end) infinite; }

      @keyframes fIdle   { 0%,19%{opacity:1} 20%,24%{opacity:0} 25%,31%{opacity:1} 32%,77%{opacity:0} 78%,100%{opacity:1} }
      @keyframes fBlink  { 0%,19%{opacity:0} 20%,24%{opacity:1} 25%,100%{opacity:0} }
      @keyframes fDrumA  { 0%,31%{opacity:0} 32%,35%{opacity:1} 36%,39%{opacity:0} 40%,43%{opacity:1} 44%,47%{opacity:0} 48%,51%{opacity:1} 52%,100%{opacity:0} }
      @keyframes fDrumB  { 0%,35%{opacity:0} 36%,39%{opacity:1} 40%,43%{opacity:0} 44%,47%{opacity:1} 48%,51%{opacity:0} 52%,58%{opacity:1} 59%,100%{opacity:0} }
      @keyframes fJump   { 0%,59%{opacity:0} 60%,76%{opacity:1} 77%,100%{opacity:0} }
      @keyframes fShadow { 0%,59%{opacity:1} 60%,76%{opacity:0.4} 77%,100%{opacity:1} }

      @media (prefers-reduced-motion: reduce) {
        #idle { animation: none; opacity: 1; }
        #blink, #drumA, #drumB, #jump { animation: none; opacity: 0; }
        #shadow { animation: none; opacity: 1; }
      }
"""

frames_svg = "\n".join(
    emit_frame(g, fid, dy=-4 if fid == "jump" else 0) for fid, g in FRAMES.items()
)

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -4 {W} {H + 4}" width="{W * 12}" height="{(H + 4) * 12}" shape-rendering="crispEdges" role="img" aria-label="A pixel-art gorilla drumming its chest and jumping">
  <title>Pixel Gorilla</title>
  <desc>Hand-authored pixel-art SVG. One rect per pixel run, frames swapped with CSS steps().</desc>

  <defs>
    <style>{CSS}    </style>
  </defs>

  <g id="shadow" fill="#000000" opacity="1">
    <rect x="5" y="25" width="14" height="1" fill-opacity="0.16"/>
    <rect x="7" y="26" width="10" height="1" fill-opacity="0.10"/>
  </g>

{frames_svg}
</svg>
"""

out = pathlib.Path(__file__).resolve().parent.parent / "assets" / "gorilla.svg"
out.write_text(svg)
print(f"生成: {out}  ({len(svg)} bytes)")
print(f"フレーム: {', '.join(FRAMES)}")
rects = svg.count("<rect")
print(f"rect 総数: {rects}")

# 検証用に各フレームを単独で描画できる SVG も吐く
posedir = pathlib.Path(__file__).resolve().parent / "pixel_poses"
posedir.mkdir(exist_ok=True)
for fid, g in FRAMES.items():
    single = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -4 {W} {H + 4}" width="{W * 14}" height="{(H + 4) * 14}" shape-rendering="crispEdges">
  <rect x="0" y="-4" width="{W}" height="{H + 4}" fill="#ffffff"/>
  <g fill="#000" opacity="0.14"><rect x="5" y="25" width="14" height="1"/></g>
{emit_frame(g, fid, dy=-4 if fid == 'jump' else 0)}
</svg>
"""
    (posedir / f"{fid}.svg").write_text(single)
print(f"検証用フレーム: {posedir}/*.svg")
