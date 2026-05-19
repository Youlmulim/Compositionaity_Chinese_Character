from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


# ============================================================
# 설정
# ============================================================

PROJECT_ROOT = Path("/Users/youlimkim/Downloads/Compositionaity_Chinese_Character-feature/stimuli")

FONT_PATH = PROJECT_ROOT / "FandolKai-Regular.otf"
OUT_DIR = PROJECT_ROOT / "image_regular"

OUT_DIR.mkdir(parents=True, exist_ok=True)

# 사용할 기본 한자
chars = [
    "月", "日", "人", "木", "土", "又", "心",
    "王", "中", "子", "大", "女", "不"
]

CANVAS_SIZE = 512
FONT_SIZE = 360

BACKGROUND = "white"
TEXT_COLOR = "black"


# ============================================================
# 폰트 로드
# ============================================================

font = ImageFont.truetype(str(FONT_PATH), FONT_SIZE)


# ============================================================
# 한 글자씩 PNG 생성
# ============================================================

for i, char in enumerate(chars, start=1):
    img = Image.new("RGBA", (CANVAS_SIZE, CANVAS_SIZE), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # 글자의 실제 bounding box 계산
    bbox = draw.textbbox((0, 0), char, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    # 중앙 정렬
    x = (CANVAS_SIZE - text_w) / 2 - bbox[0]
    y = (CANVAS_SIZE - text_h) / 2 - bbox[1]

    draw.text((x, y), char, font=font, fill=(255, 255, 255, 255))

    # 파일명은 유니코드 코드포인트로 저장하면 안전함
    codepoint = f"U+{ord(char):04X}"
    out_path = OUT_DIR / f"{i:02d}_{codepoint}.png"

    img.save(out_path)

print(f"Saved {len(chars)} images to: {OUT_DIR}")