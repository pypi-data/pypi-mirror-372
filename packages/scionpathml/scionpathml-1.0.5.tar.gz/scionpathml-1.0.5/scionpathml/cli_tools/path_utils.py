# File to have path for every folder from anywhere
from __future__ import annotations
import importlib
from functools import lru_cache
from pathlib import Path


@lru_cache
def _pkg_dir(pkg: str) -> Path:
    """Return the directory of an installed package."""
    mod = importlib.import_module(pkg)
    return Path(mod.__file__).resolve().parent


@lru_cache
def scionpathml_dir() -> Path:
    return _pkg_dir("scionpathml")


@lru_cache
def collector_dir() -> Path:
    # Try as its own installed package; fall back to sibling folder
    try:
        return _pkg_dir("scionpathml/collector")
    except ModuleNotFoundError:
        p = scionpathml_dir().parent / "scionpathml/collector"
        return p.resolve()


@lru_cache
def runner_dir() -> Path:
    try:
        return _pkg_dir("scionpathml/runner")
    except ModuleNotFoundError:
        p = scionpathml_dir().parent / "scionpathml/runner"
        return p.resolve()


@lru_cache
def transformers_dir() -> Path:
    try:
        return _pkg_dir("scionpathml/transformers")
    except ModuleNotFoundError:
        p = scionpathml_dir().parent / "scionpathml/transformers"
        return p.resolve()


@lru_cache
def data_dir() -> Path:
    # Prefer Data inside scionpathml package; fall back to sibling Data/
    p1 = scionpathml_dir() / "Data"
    if p1.exists():
        return p1.resolve()
    p2 = scionpathml_dir().parent / "Data"
    return p2.resolve()


@lru_cache
def logs_dir() -> Path:
    p3 = scionpathml_dir() / "Data/Logs"
    if p3.exists():
        return p3.resolve()
    p4 = scionpathml_dir().parent / "Data/Logs"
    return p4.resolve()




def pipeline_script() -> Path:
    return (runner_dir() / "pipeline.sh").resolve()


def collector_config() -> Path:
    return (collector_dir() / "config.py").resolve()


def ensure_file(p: Path) -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.touch(exist_ok=True)
    return p