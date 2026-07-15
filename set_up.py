import os
import shutil
import subprocess
import sys
from pathlib import Path


VENV_DIR = Path(".venv")
REQUIREMENTS_FILE = Path("requirements.txt")
PROJECT_NAME = "compositionality-chinese-character"
PROJECT_VERSION = "0.1.0"
SUPPORTED_PYTHON = ">=3.11,<3.12"
SOUNDS_DIR = Path("function/utils/sounds")
REQUIRED_SOUND_FILES = (
    "sound_effect.wav",
    "sound_effect_quit.wav",
    "sound_effect_done.wav",
)


def run(cmd):
    print(f"[RUN] {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


def find_python311():
    """Find Python 3.11 on Windows, macOS, or Linux."""
    candidates = []
    if os.name == "nt":
        candidates.append(["py", "-3.11"])
    else:
        if sys.version_info[:2] == (3, 11):
            candidates.append([sys.executable])
        python311 = shutil.which("python3.11")
        if python311:
            candidates.append([python311])

    for candidate in candidates:
        try:
            result = subprocess.run(
                candidate + ["--version"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0 and "Python 3.11" in result.stdout:
                return candidate
        except FileNotFoundError:
            continue

    print("\n[ERROR] Python 3.11이 설치되어 있지 않습니다.")
    print("👉 Python 3.11 설치 후 다시 실행하세요.")
    exit(1)


def create_venv():
    if VENV_DIR.exists():
        print(f"[INFO] 가상환경 이미 존재: {VENV_DIR}")
        return

    py311 = find_python311()

    print("[INFO] Python 3.11로 가상환경 생성 중...")
    run(py311 + ["-m", "venv", str(VENV_DIR)])
    print("[INFO] 가상환경 생성 완료")


def get_python_path():
    if os.name == "nt":
        return VENV_DIR / "Scripts" / "python.exe"
    else:
        return VENV_DIR / "bin" / "python"


def install_requirements():
    if not REQUIREMENTS_FILE.exists():
        print("[WARNING] requirements.txt가 없습니다.")
        return

    python_path = get_python_path()

    run([str(python_path), "-m", "pip", "install", "--upgrade", "pip"])
    run([str(python_path), "-m", "pip", "install", "--upgrade", "setuptools", "wheel"])
    run([str(python_path), "-m", "pip", "install", "-r", str(REQUIREMENTS_FILE)])


def validate_project_assets():
    """Ensure sound assets formerly declared as setup.py package data exist."""
    missing = [
        str(SOUNDS_DIR / filename)
        for filename in REQUIRED_SOUND_FILES
        if not (SOUNDS_DIR / filename).is_file()
    ]
    if missing:
        raise FileNotFoundError(
            "Required sound file(s) missing:\n  " + "\n  ".join(missing)
        )

    print(f"[INFO] Project: {PROJECT_NAME} {PROJECT_VERSION}")
    print(f"[INFO] Python: {SUPPORTED_PYTHON}")
    print(f"[INFO] Sound assets verified: {len(REQUIRED_SOUND_FILES)}")


def main():
    try:
        validate_project_assets()
        create_venv()
        install_requirements()

        print("\n[INFO] 완료!")
        if os.name == "nt":
            print(r".venv\Scripts\activate")
        else:
            print("source .venv/bin/activate")

    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        print("\n[ERROR] 설치 실패")
        print(e)
        exit(1)


if __name__ == "__main__":
    main()
