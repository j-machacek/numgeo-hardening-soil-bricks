"""Build the versioned documentation into one GitHub Pages site.

Versions follow the numgeo documentation: the branch main is the development
version "dev", every branch release/YYYY-MM is the release "YYYY-MM". The newest
release carries the alias "latest". All versions are built in one run and
published together (GitHub Pages artifact), so the Pages settings stay as they are.

Layout of the site directory:

    versions.json            versions shown by the theme's version selector (mike format)
    <version>/               one complete version: dev, 2026-08, ...
    index.html, <page>.html  redirects to the same page of the latest release, so that
                             links to the former single-version site keep working
    404.html                 not-found page of the latest release

Each version is built from its own docs/ and zensical.toml. The build patches
only a copy of zensical.toml (site_url of the version, version selector, theme
overrides from overrides/ of the checkout that runs this script).

    python scripts/build_docs.py                 # dev from the working tree, local release/* branches
    python scripts/build_docs.py --dev-ref main  # dev from a commit instead of the working tree
    python scripts/build_docs.py --remote origin # release branches of a remote (CI)

A new release: create the branch release/YYYY-MM from main, push it, then run
the workflow "Documentation" (push to main or start it by hand).

10.11.2026, J. Machacek - Versioned documentation (development version and releases).
"""
from __future__ import annotations

import argparse
import html
import io
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import tomllib
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
OVERRIDES = ROOT / 'overrides'
DEV = 'dev'
DEV_TITLE = 'Active development'
RELEASE = re.compile(r'\d{4}-(0[1-9]|1[0-2])')
SOURCES = ('docs', 'zensical.toml')


def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout


def release_branches(remote=None):
    """Map release version -> git ref of its branch (local, or of the remote)."""
    prefix = f'refs/remotes/{remote}/release/' if remote else 'refs/heads/release/'
    refs = git('for-each-ref', '--format=%(refname)', prefix).split()
    releases = {}
    for ref in refs:
        name = ref[len(prefix):]
        if not RELEASE.fullmatch(name):
            raise ValueError(f'Release branches must be named release/YYYY-MM, got {ref}')
        releases[name] = ref
    if not releases:
        raise ValueError(f'No release branch found under {prefix}: the site needs at least one release')
    return releases


def export(ref, target):
    """Copy docs/ and zensical.toml of a commit (ref) or of the working tree (None) to target."""
    target.mkdir(parents=True)
    if ref is None:
        shutil.copytree(ROOT / 'docs', target / 'docs')
        shutil.copy2(ROOT / 'zensical.toml', target / 'zensical.toml')
        return
    archive = subprocess.run(['git', 'archive', '--format=tar', ref, *SOURCES], cwd=ROOT, check=True,
                             capture_output=True).stdout
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        tar.extractall(target, filter='data')


def root_url(config_file):
    """site_url of the unversioned configuration: the root of the versioned site."""
    url = tomllib.loads(config_file.read_text(encoding='utf-8'))['project'].get('site_url')
    if not url:
        raise ValueError(f'{config_file}: site_url is required for the versioned documentation')
    return url if url.endswith('/') else url + '/'


def patch_config(text, info):
    """zensical.toml of one version: its site_url, the output directory, the theme
    overrides and the version selector. Fails instead of guessing if the file does
    not have the expected structure."""
    def toml_string(value):
        return json.dumps(str(value))

    def replace_once(pattern, replacement, what):
        new, count = re.subn(pattern, lambda _: replacement, text, count=1, flags=re.MULTILINE)
        if count != 1:
            raise ValueError(f'zensical.toml: {what} not found')
        return new

    for key in ('site_dir', 'docs_dir', 'custom_dir'):
        if re.search(rf'^\s*{key}\s*=', text, flags=re.MULTILINE):
            raise ValueError(f'zensical.toml: {key} is set; the versioned build sets it itself')
    if re.search(r'^\[project\.extra\.(version|doc_version)\]', text, flags=re.MULTILINE):
        raise ValueError('zensical.toml: [project.extra.version] is set; the versioned build sets it itself')
    text = replace_once(r'^site_url\s*=.*$', f'site_url = {toml_string(info["site_url"])}', 'site_url')
    # zensical requires both directories inside the project (the exported copy).
    text = replace_once(r'^\[project\]\s*$', '[project]\ndocs_dir = "docs"\nsite_dir = "site"', '[project]')
    text = replace_once(r'^\[project\.theme\]\s*$', '[project.theme]\ncustom_dir = "overrides"',
                        '[project.theme]')
    # Cookie consent and colour scheme apply to all versions (scope = site root).
    if re.search(r'^\s*scope\s*=', text, flags=re.MULTILINE):
        raise ValueError('zensical.toml: scope is set; the versioned build sets it itself')
    scope = f'scope = {toml_string(urlsplit(info["root_url"]).path)}'
    if re.search(r'^\[project\.extra\]\s*$', text, flags=re.MULTILINE):
        text = replace_once(r'^\[project\.extra\]\s*$', f'[project.extra]\n{scope}', '[project.extra]')
    else:
        text += f'\n[project.extra]\n{scope}\n'
    text += ('\n# --- Added by scripts/build_docs.py ------------------------------------------\n'
             '[project.extra.version]\nprovider = "mike"\ndefault = "latest"\nalias = true\n\n'
             '[project.extra.doc_version]\n'
             f'id = {toml_string(info["id"])}\ntitle = {toml_string(info["title"])}\n'
             f'development = {"true" if info["development"] else "false"}\n'
             f'root_url = {toml_string(info["root_url"])}\n')
    parsed = tomllib.loads(text)['project']
    if parsed['site_url'] != info['site_url'] or parsed['theme']['custom_dir'] != 'overrides':
        raise ValueError('zensical.toml: patched configuration does not contain the version settings')
    return text


def build_version(version, ref, root, work, site):
    info = {'id': version, 'title': DEV_TITLE if version == DEV else version,
            'development': version == DEV, 'site_url': f'{root}{version}/', 'root_url': root}
    source = work / version
    export(ref, source)
    # The theme overrides of this checkout apply to every version.
    shutil.copytree(OVERRIDES, source / 'overrides')
    config = source / 'zensical.toml'
    config.write_text(patch_config(config.read_text(encoding='utf-8'), info), encoding='utf-8')
    print(f'Building {version} from {ref or "the working tree"}', flush=True)
    subprocess.run([sys.executable, '-m', 'zensical', 'build', '--clean', '-f', str(config)], cwd=source,
                   check=True)
    output = site / version
    shutil.move(source / 'site', output)
    if not (output / 'index.html').is_file():
        raise ValueError(f'{version}: the build produced no index.html')
    # The version selector keeps the current page when switching versions only if
    # the version root itself is listed in the sitemap.
    sitemap = output / 'sitemap.xml'
    if sitemap.is_file():
        xml = sitemap.read_text(encoding='utf-8')
        loc = f'<loc>{info["site_url"]}</loc>'
        if loc not in xml:
            sitemap.write_text(xml.replace('<url>', f'<url>\n        {loc}\n      </url>\n      <url>', 1),
                               encoding='utf-8')
    return info


def redirect_page(target):
    """Small page that forwards to target, keeping query and anchor."""
    url = html.escape(target, quote=True)
    script = json.dumps(target)
    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<title>Redirecting</title>\n<meta name="robots" content="noindex">\n'
            f'<script>location.replace({script} + location.search + location.hash)</script>\n'
            f'<meta http-equiv="refresh" content="0; url={url}">\n</head>\n'
            f'<body><a href="{url}">Redirecting to {url}</a></body>\n</html>\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('--dev-ref', help='commit of the development version (default: the working tree)')
    parser.add_argument('--remote', help='take the release branches from this remote (default: local branches)')
    parser.add_argument('--site', default=str(ROOT / 'site'), help='output directory (default: site/)')
    args = parser.parse_args()

    site = Path(args.site).resolve()
    if site.exists():
        shutil.rmtree(site)
    site.mkdir(parents=True)
    releases = release_branches(args.remote)
    latest = max(releases)
    with tempfile.TemporaryDirectory(prefix='build-docs-') as tmp:
        work = Path(tmp)
        export(args.dev_ref, work / '_root')
        root = root_url(work / '_root' / 'zensical.toml')
        versions = [build_version(DEV, args.dev_ref, root, work, site)]
        for version in sorted(releases, reverse=True):
            versions.append(build_version(version, releases[version], root, work, site))

    (site / 'versions.json').write_text(json.dumps(
        [{'version': v['id'], 'title': v['title'], 'aliases': ['latest'] if v['id'] == latest else []}
         for v in versions], indent=2) + '\n', encoding='utf-8')
    # Pages of the former single-version site lead to the same page of the latest release.
    redirects = 0
    for page in sorted((site / latest).rglob('*.html')):
        relative = page.relative_to(site / latest).as_posix()
        if relative == '404.html':
            continue
        depth = relative.count('/')
        target = site / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(redirect_page('../' * depth + f'{latest}/{relative}'), encoding='utf-8')
        redirects += 1
    shutil.copy2(site / latest / '404.html', site / '404.html')
    (site / '.nojekyll').touch()
    print(f'Site: {site}\nVersions: {", ".join(v["id"] for v in versions)} (latest: {latest}); '
          f'{redirects} redirect pages', flush=True)


if __name__ == '__main__':
    main()
