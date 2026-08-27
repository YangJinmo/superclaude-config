#!/usr/bin/env python3
"""iOS 화면 녹화 상단 빨간 캡슐(녹화 표시)을 감지해 인페인팅으로 제거한다.

파이프라인: 빨간 픽셀 마스크 탐지 -> bbox 패딩 -> cv2.inpaint -> 경계 페더링
-> (옵션) 시간 텍스트 복원.

사용 예:
    python3 remove_recording_indicator.py input.png output.png --time "9:41"
    python3 remove_recording_indicator.py input.png output.png --time "9:41" --text-color white

--time을 생략하면 감지/인페인팅/페더링까지만 하고 시간 텍스트는 그리지 않는다.
같은 세트의 다른 스크린샷에서 시간 값을 먼저 확인한 뒤 --time으로 넘겨줄 것
(아이콘만 있고 시간이 안 보이는 녹화 시작 직후 프레임이 흔하다).

의존성: opencv-python-headless, numpy, pillow
시스템 파이썬이 PEP 668로 pip install을 막는 경우:
    python3 -m venv venv --system-site-packages
    ./venv/bin/pip install opencv-python-headless numpy pillow
    ./venv/bin/python3 remove_recording_indicator.py ...
"""
import argparse
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONT_CANDIDATES = [
    "/Library/Fonts/SF-Pro-Text-Medium.otf",
    "/System/Library/Fonts/SFCompact.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
]


def find_red_capsule_mask(img_bgr, search_region=(0, 0, 140, 60)):
    """상태바 좌측 영역에서 R>130 and (R-G)>40 and (R-B)>40 조건의 빨간 픽셀을 마스크로 만든다."""
    x0, y0, x1, y1 = search_region
    x1, y1 = min(x1, img_bgr.shape[1]), min(y1, img_bgr.shape[0])
    roi = img_bgr[y0:y1, x0:x1].astype(np.int16)
    b, g, r = roi[..., 0], roi[..., 1], roi[..., 2]
    red = (r > 130) & ((r - g) > 40) & ((r - b) > 40)
    mask = np.zeros(img_bgr.shape[:2], dtype=np.uint8)
    mask[y0:y1, x0:x1] = red.astype(np.uint8) * 255
    return mask


def bbox_from_mask(mask, pad=8):
    ys, xs = np.where(mask > 0)
    if len(xs) == 0:
        return None
    x0, x1 = max(int(xs.min()) - pad, 0), min(int(xs.max()) + pad, mask.shape[1])
    y0, y1 = max(int(ys.min()) - pad, 0), min(int(ys.max()) + pad, mask.shape[0])
    return x0, y0, x1, y1


def inpaint_and_feather(img_bgr, mask):
    kernel = np.ones((5, 5), np.uint8)
    dilated = cv2.dilate(mask, kernel, iterations=2)
    inpainted = cv2.inpaint(img_bgr, dilated, inpaintRadius=6, flags=cv2.INPAINT_TELEA)
    soft = cv2.GaussianBlur(dilated, (15, 15), 0).astype(np.float32)[..., None] / 255.0
    blended = inpainted.astype(np.float32) * soft + img_bgr.astype(np.float32) * (1 - soft)
    return blended.astype(np.uint8)


def sample_background_color(img_rgb, x, y, radius=6):
    h, w = img_rgb.shape[:2]
    x0, x1 = max(x - radius, 0), min(x + radius, w)
    y0, y1 = max(y - radius, 0), min(y + radius, h)
    patch = img_rgb[y0:y1, x0:x1].reshape(-1, 3)
    return patch.mean(axis=0)


def load_font(size):
    for path in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def find_status_bar_icon_center_y(img_rgb, x_start_frac=0.85):
    """우측 와이파이/배터리 아이콘 영역에서 배경과 다른(=아이콘) 행들의 세로 중심을 근사로 찾는다."""
    h, w = img_rgb.shape[:2]
    x0 = int(w * x_start_frac)
    band = img_rgb[0:60, x0:w]
    gray = band.mean(axis=2)
    row_var = gray.std(axis=1)
    if row_var.max() < 1e-3:
        return 30
    rows = np.where(row_var > row_var.mean())[0]
    return int(rows.mean()) if len(rows) else 30


def draw_time_text(img_rgb, text, capsule_x0, text_color_mode="auto"):
    pil_img = Image.fromarray(img_rgb)
    draw = ImageDraw.Draw(pil_img)
    font = load_font(15)
    center_y = find_status_bar_icon_center_y(img_rgb)
    bg = sample_background_color(img_rgb, capsule_x0 + 20, center_y)
    is_light_bg = bg.mean() > 150

    if text_color_mode == "dark" or (text_color_mode == "auto" and is_light_bg):
        color = (20, 20, 22)
    else:
        color = (255, 255, 255)

    bbox = draw.textbbox((0, 0), text, font=font)
    text_h = bbox[3] - bbox[1]
    y = center_y - text_h // 2

    if color == (255, 255, 255):
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            draw.text((capsule_x0 + dx, y + dy), text, font=font, fill=(0, 0, 0, 160))

    draw.text((capsule_x0, y), text, font=font, fill=color)
    return np.array(pil_img)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--time", default=None, help="복원할 시간 텍스트 (예: '9:41'). 생략하면 텍스트 없이 인페인팅만 한다.")
    parser.add_argument("--text-color", choices=["auto", "dark", "white"], default="auto")
    args = parser.parse_args()

    img_bgr = cv2.imread(args.input, cv2.IMREAD_COLOR)
    if img_bgr is None:
        print(f"이미지를 읽을 수 없습니다: {args.input}", file=sys.stderr)
        sys.exit(1)

    mask = find_red_capsule_mask(img_bgr)
    bbox = bbox_from_mask(mask)
    if bbox is None:
        print("빨간 녹화 캡슐이 감지되지 않았습니다. 원본을 그대로 복사합니다.")
        cv2.imwrite(args.output, img_bgr)
        return

    result_bgr = inpaint_and_feather(img_bgr, mask)
    result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)

    if args.time:
        x0, _, _, _ = bbox
        result_rgb = draw_time_text(result_rgb, args.time, capsule_x0=x0, text_color_mode=args.text_color)

    cv2.imwrite(args.output, cv2.cvtColor(result_rgb, cv2.COLOR_RGB2BGR))
    print(f"완료: {args.output} (감지된 캡슐 bbox: {bbox})")


if __name__ == "__main__":
    main()
