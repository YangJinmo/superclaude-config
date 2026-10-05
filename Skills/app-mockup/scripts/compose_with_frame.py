#!/usr/bin/env python3
"""투명 기기 프레임 PNG + 스크린샷 N장 → 1920x1080 투명 배경 목업 한 장.

화면 영역은 프레임 중앙 픽셀에서 flood fill(alpha<=10 연결영역)로 자동 탐지하므로
둥근 모서리/노치/펀치홀이 있는 프레임도 별도 좌표 없이 쓸 수 있다.

사용법:
  python3 compose_with_frame.py --frame assets/frames/iphone-8-silver.png \
      --out out.png shot1.png shot2.png ...
스크린샷은 인자로 준 순서대로 왼쪽→오른쪽 배치한다.
의존성: pillow, numpy, opencv-python-headless
"""
import argparse
import cv2
import numpy as np
from PIL import Image

CANVAS_W, CANVAS_H = 1920, 1080


def find_screen(alpha):
    h, w = alpha.shape
    transparent = (alpha <= 10).astype(np.uint8)
    _, labels, stats, _ = cv2.connectedComponentsWithStats(transparent, connectivity=4)
    label = labels[h // 2, w // 2]
    if label == 0:
        raise SystemExit("프레임 중앙이 투명하지 않다 — 화면 영역이 뚫린 프레임이 아님")
    x, y, bw, bh, _ = stats[label]
    return int(x), int(y), int(bw), int(bh)


def cover(img, tw, th):
    """비율 유지로 tw x th를 꽉 채우도록 리사이즈 후 중앙 크롭."""
    if abs(img.width / img.height - tw / th) / (tw / th) > 0.03:
        print(f"경고: 스크린샷 비율({img.width}x{img.height})이 화면 영역({tw}x{th})과 달라 가장자리가 잘린다 — 기종 선택 재확인", flush=True)
    s = max(tw / img.width, th / img.height)
    img = img.resize((max(tw, round(img.width * s)), max(th, round(img.height * s))), Image.LANCZOS)
    l, t = (img.width - tw) // 2, (img.height - th) // 2
    return img.crop((l, t, l + tw, t + th))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--gap", type=int, default=16)
    ap.add_argument("--margin", type=int, default=24)
    ap.add_argument("--vmargin", type=int, default=20)
    ap.add_argument("shots", nargs="+")
    a = ap.parse_args()

    frame = Image.open(a.frame).convert("RGBA")
    sx, sy, sw, sh = find_screen(np.array(frame)[:, :, 3])
    l, t, r, b = frame.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
    frame = frame.crop((l, t, r, b))
    sx, sy = sx - l, sy - t
    fw, fh = frame.size

    n = len(a.shots)
    w = (CANVAS_W - 2 * a.margin - (n - 1) * a.gap) / n
    s = min(w / fw, (CANVAS_H - 2 * a.vmargin) / fh)
    W, H = round(fw * s), round(fh * s)
    fr = frame.resize((W, H), Image.LANCZOS)
    L, T = round(sx * s), round(sy * s)
    R, B = round((sx + sw) * s), round((sy + sh) * s)

    x0 = (CANVAS_W - (n * W + (n - 1) * a.gap)) // 2
    y0 = (CANVAS_H - H) // 2
    canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    for i, path in enumerate(a.shots):
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        layer.paste(cover(Image.open(path).convert("RGBA"), R - L, B - T), (L, T))
        layer.alpha_composite(fr)
        canvas.alpha_composite(layer, (x0 + i * (W + a.gap), y0))
    canvas.save(a.out)
    print(f"saved {a.out}  phone={W}x{H} screen=({L},{T},{R-L}x{B-T}) n={n}")


if __name__ == "__main__":
    main()
