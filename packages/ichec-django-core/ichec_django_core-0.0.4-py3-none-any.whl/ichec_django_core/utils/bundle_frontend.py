import logging
import argparse
import os
import shutil
import tarfile
import urllib.request
import urllib.parse
from html.parser import HTMLParser

from pathlib import Path

logger = logging.getLogger(__name__)

_PROJECT_URL = "https://git.ichec.ie/api/v4/projects/592"
_FRONTEND_URL = f"{_PROJECT_URL}/releases/permalink/latest/downloads/frontend.tar.gz"
_DJANGO_APP = "angular_frontend"


class MyHTMLParser(HTMLParser):

    def __init__(self):
        super().__init__()
        self.replacements = []
        self.link_prefixes = ["assets", "styles-", "chunk-"]
        self.script_prefixes = ["polyfills-", "main-"]

    def handle_starttag(self, tag, attrs):
        if tag == "link":
            for attr in attrs:
                if attr[0] == "href":
                    self.on_link(attr[1])
        elif tag == "script":
            for attr in attrs:
                if attr[0] == "src":
                    self.on_script(attr[1])

    def on_link(self, attr: str):
        for prefix in self.link_prefixes:
            if attr.startswith(prefix):
                self.replacements.append(("href", attr))

    def on_script(self, attr: str):
        for prefix in self.script_prefixes:
            if attr.startswith(prefix):
                self.replacements.append(("src", attr))


def _get_charset(response):
    charset = response.headers.get_content_charset()
    if not charset:
        charset = "utf-8"
    return charset


def get_static_dir():
    return f"src/{_DJANGO_APP}/static/{_DJANGO_APP}"


def get_template_dir():
    return f"src/{_DJANGO_APP}/templates/{_DJANGO_APP}"


def extract_archive(path: Path, output_path: Path):
    logger.info("Extracting archive at %s", path)
    with tarfile.open(path, "r:gz") as t:
        t.extractall(output_path)
    logger.info("Finished extraction")


def download(url: str, dst: Path):
    logger.info("Downloading from %s to %s", url, dst)
    with open(dst, "wb") as f:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            if response.status >= 300:
                body = response.read().decode(_get_charset(response))
                msg = (
                    f"code {response.status}, reason {response.reason}, and body {body}"
                )
                raise RuntimeError(f"Http Request failed with: {msg}")
            f.write(response.read())
    logger.info("Download complete")


def make_angular_django_substitutions(template_dir: Path):
    logger.info("Making Django substitutions")

    parser = MyHTMLParser()
    with open(template_dir / "index_template.html", "r") as f:
        content = f.read()
    parser.feed(content)

    replacement_pairs = []
    for rep in parser.replacements:
        attr_type, body = rep
        replacement_pairs.append(
            (
                f'{attr_type}="{body}"',
                f"{attr_type}={{% static '{_DJANGO_APP}/{body}' %}}",
            )
        )

    for src, tgt in replacement_pairs:
        content = content.replace(src, tgt)

    content = "{% load static %}\n" + content
    with open(template_dir / "index.html", "w") as f:
        f.write(content)

    logger.info("Finished Django substitutions")


def copy_frontend_to_backend(frontend_dir: Path, backend_dir: Path):

    logger.info(
        "Copying frontend files at %s to backend at %s", frontend_dir, backend_dir
    )
    backend_static_dir = backend_dir / get_static_dir()
    if (backend_static_dir).exists():
        shutil.rmtree(backend_static_dir)
    shutil.copytree(frontend_dir, backend_static_dir)
    os.remove(backend_static_dir / "index.html")

    backend_template_dir = backend_dir / get_template_dir()
    shutil.copy(
        frontend_dir / "index.html", backend_template_dir / "index_template.html"
    )
    logger.info("Finished copying frontend to backend")


def bundle(frontend_path: str, backend_dir: Path, work_dir: Path):

    bundle_dir = work_dir / "_bundle"
    os.makedirs(bundle_dir, exist_ok=True)

    if not frontend_path:
        download(_FRONTEND_URL, bundle_dir / "frontend.tar.gz")
        extract_archive(bundle_dir / "frontend.tar.gz", bundle_dir)
    elif frontend_path.startswith("http"):
        download(frontend_path, bundle_dir)
        extract_archive(bundle_dir / "frontend.tar.gz", bundle_dir)
    else:
        path = Path(frontend_path)
        if not path.is_dir():
            extract_archive(path, bundle_dir)
        else:
            if not bundle_dir.exists():
                shutil.copytree(path, bundle_dir)
    working_frontend = bundle_dir / "browser"
    copy_frontend_to_backend(working_frontend, backend_dir)

    make_angular_django_substitutions(backend_dir / get_template_dir())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--frontend",
        type=str,
        default="",
        help="Path (or url) to the frontend build directory."
        "Default to the latest release if empty.",
    )
    parser.add_argument(
        "--backend_dir",
        type=Path,
        default=Path(os.getcwd()),
        help="Path to the local backend source repo",
    )
    parser.add_argument(
        "--work_dir",
        type=Path,
        default=Path(os.getcwd()),
        help="Temporary working directory",
    )
    args = parser.parse_args()

    fmt = "%(asctime)s%(msecs)03d | %(filename)s:%(lineno)s:%(funcName)s | %(message)s"
    logging.basicConfig(
        format=fmt,
        datefmt="%Y%m%dT%H:%M:%S:",
        level=logging.INFO,
    )

    bundle(args.frontend, args.backend_dir.resolve(), args.work_dir.resolve())
