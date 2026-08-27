#!/usr/bin/env python3
"""실물 기기 프레임 PNG(스크린 영역이 alpha=0으로 뚫린 투명 프레임)에서
노치/다이나믹 아일랜드/펀치홀 컷아웃 모양을 SVG path로 추출한다.

파이프라인: 스크린 bbox alpha 스캔 -> 상단 밴드 컷아웃 컨투어 탐지
-> 8배 업스케일 후 스무딩 -> 폴리곤 단순화(약 20~30점) -> screen_w 기준 정규화
-> SVG path 생성 -> 상단 이음새 보정(첫/끝 점 y를 -40으로).

사용 예:
    python3 extract_notch_vector.py iphone-x-frame.png

표준출력으로 다음 JSON을 출력한다:
    {
      "screen_bbox": [x0, y0, x1, y1],
      "screen_w": ..., "screen_h": ...,
      "svg_path": "M ... Z",
      "svg_viewbox_height": ...
    }

의존성: opencv-python-headless, numpy, pillow
"""
import argparse
import json

import cv2
import numpy as np
from PIL import Image


def load_alpha(path):
    img = Image.open(path).convert("RGBA")
    return np.array(img)[..., 3]


def scan_screen_bbox(alpha, threshold=10):
    """노치/카메라를 피한 여러 지점에서 행/열을 스캔해 불투명(베젤)->투명(스크린) 전환 좌표를 찾는다."""
    h, w = alpha.shape
    x_lefts, x_rights = [], []
    for frac in (0.4, 0.5, 0.6, 0.7):  # 노치가 없을 만한 세로 위치
        row = alpha[int(h * frac)] > threshold
        xs = np.where(row)[0]
        if len(xs):
            x_lefts.append(xs.min())
            x_rights.append(xs.max())

    y_tops, y_bottoms = [], []
    for frac in (0.15, 0.2, 0.8, 0.85):  # 노치를 피한 가로 위치
        col = alpha[:, int(w * frac)] > threshold
        ys = np.where(col)[0]
        if len(ys):
            y_tops.append(ys.min())
            y_bottoms.append(ys.max())

    if not (x_lefts and x_rights and y_tops and y_bottoms):
        raise ValueError("스크린 투명 영역을 찾지 못했습니다 — 프레임이 alpha=0으로 뚫려 있는지 확인하세요.")

    x0, x1 = int(np.median(x_lefts)), int(np.median(x_rights))
    y0, y1 = int(np.median(y_tops)), int(np.median(y_bottoms))
    return x0, y0, x1, y1


def extract_cutout_contour(alpha, screen_bbox, top_frac=0.12, upscale=8):
    x0, y0, x1, y1 = screen_bbox
    screen_w, screen_h = x1 - x0, y1 - y0
    top_h = max(int(screen_h * top_frac), 10)

    band = alpha[y0:y0 + top_h, x0:x1]
    mask = (band > 128).astype(np.uint8) * 255

    big = cv2.resize(mask, (mask.shape[1] * upscale, mask.shape[0] * upscale), interpolation=cv2.INTER_CUBIC)
    big = cv2.GaussianBlur(big, (0, 0), sigmaX=upscale)
    _, big = cv2.threshold(big, 127, 255, cv2.THRESH_BINARY)

    contours, _ = cv2.findContours(big, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not contours:
        raise ValueError("컷아웃 컨투어를 찾지 못했습니다.")

    band_w = mask.shape[1] * upscale
    best, best_area = None, 0
    for c in contours:
        x, _, w, _ = cv2.boundingRect(c)
        cx = x + w / 2
        area = cv2.contourArea(c)
        # 화면 가로 중앙 근처(밴드 폭의 30~70%)에 있고 면적이 가장 큰 컨투어만 진짜 컷아웃으로 채택
        # (좌우 끝 모서리에 걸친 둥근 베젤 컨투어는 버린다)
        if band_w * 0.3 < cx < band_w * 0.7 and area > best_area:
            best, best_area = c, area

    if best is None:
        raise ValueError("화면 중앙에 위치한 컷아웃 컨투어를 찾지 못했습니다 (모서리 베젤만 감지됨 — 이 기종은 컷아웃이 없을 수 있음).")

    approx = cv2.approxPolyDP(best, 0.5 * upscale, closed=True)
    points = approx.reshape(-1, 2).astype(np.float64) / upscale  # 원본 해상도로 복원
    return points, screen_w, screen_h


def normalize_and_build_path(points, screen_w):
    # x, y 모두 screen_w로 나눠 동일 비율로 정규화 (세로만 다른 기준으로 정규화하면 컷아웃이 찌그러진다)
    norm = (points / screen_w) * 1000.0
    # 상단 좌우 꼭짓점의 y를 강제로 끌어올려 클리핑 경계에서 잘리게 함 (안티앨리어싱으로 인한 1~2px 흰 이음새 제거)
    norm[0][1] = -40
    norm[-1][1] = -40
    parts = [f"M {norm[0][0]:.1f} {norm[0][1]:.1f}"]
    parts += [f"L {p[0]:.1f} {p[1]:.1f}" for p in norm[1:]]
    parts.append("Z")
    return " ".join(parts), float(norm[:, 1].max())


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("frame_png")
    parser.add_argument("--top-frac", type=float, default=0.12, help="컷아웃이 들어있을 상단 밴드 높이 비율")
    args = parser.parse_args()

    alpha = load_alpha(args.frame_png)
    screen_bbox = scan_screen_bbox(alpha)
    points, screen_w, screen_h = extract_cutout_contour(alpha, screen_bbox, top_frac=args.top_frac)
    svg_path, viewbox_h = normalize_and_build_path(points, screen_w)

    print(json.dumps({
        "screen_bbox": list(screen_bbox),
        "screen_w": screen_w,
        "screen_h": screen_h,
        "svg_path": svg_path,
        "svg_viewbox_height": round(viewbox_h, 1),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
