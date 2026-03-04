import shutil
import zipfile
from pathlib import Path

from django.conf import settings


BUNDLED_MAXQUANT_ZIP = Path(settings.BASE_DIR) / "seed" / "defaults" / "maxquant" / "MaxQuant_v_2.4.12.0.zip"
BUNDLED_MQPAR_TEMPLATE = Path(settings.BASE_DIR) / "seed" / "defaults" / "config" / "mqpar_2.4.12.0.xml"


def default_maxquant_executable_path():
    return Path(settings.DEFAULT_MAXQUANT_EXECUTABLE)


def ensure_bundled_maxquant_installed():
    executable = default_maxquant_executable_path()
    if executable.is_file():
        return executable

    if not BUNDLED_MAXQUANT_ZIP.is_file():
        return None

    install_root = executable.parents[2]
    install_dir = executable.parents[1]
    install_root.mkdir(parents=True, exist_ok=True)

    if install_dir.exists() and not executable.is_file():
        shutil.rmtree(install_dir, ignore_errors=True)

    with zipfile.ZipFile(BUNDLED_MAXQUANT_ZIP, "r") as zip_ref:
        zip_ref.extractall(install_root)

    if executable.is_file():
        return executable
    return None


def ensure_default_mqpar_for_pipeline(pipeline):
    if pipeline.mqpar_path.is_file() or not BUNDLED_MQPAR_TEMPLATE.is_file():
        return

    pipeline.mqpar_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(BUNDLED_MQPAR_TEMPLATE, pipeline.mqpar_path)
