"""雲端打包用（GitHub Actions 會叫）：做出 Release 要放的檔案.

python tools/make_release.py --version     → 印出程式版本（app/app.py 的 APP_VERSION，例如 1.1.13）
python tools/make_release.py --launcher    → 印出啟動器版本（build/launcher.py 的 LAUNCHER_VERSION）
python tools/make_release.py --dist work/dist/TikLiveMonitor --out out --repo tpc20001/TikLive

產生：
  TK_V<版本>_Update.zip     程式更新包（manifest.json＋app\\*），跟以前手動給的格式一樣；程式裡「☁ 更新」下載的就是這個（熱更新）
  TK_Shell_L<啟動器>.zip    EXE 外殼（TikLiveMonitor.exe＋_internal），啟動器版本變大才會用到
  TikLive_Full_V<版本>.zip  第一次安裝用（外殼＋程式＋空的 UPDATE／LOG／Package；FFmpeg、資料不在裡面）
  update.json               給程式讀：版本、啟動器版本、下載網址、SHA-256、大小、更新說明
  notes.md                  Release 頁面上的說明
"""
import argparse, hashlib, json, re, sys, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / 'app'
OK_EXT = ('.py', '.json')          # 跟程式裡 _upd_parse 認得的一樣（app/ 底下一層的檔）


def app_version():
    return re.search(r'^APP_VERSION\s*=\s*["\']([^"\']+)["\']', (APP / 'app.py').read_text(encoding='utf-8'), re.M).group(1)


def launcher_version():
    return int(re.search(r'LAUNCHER_VERSION\s*=\s*(\d+)', (ROOT / 'build' / 'launcher.py').read_text(encoding='utf-8')).group(1))


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()


def app_files():
    return sorted(f for f in APP.iterdir() if f.is_file() and f.suffix.lower() in OK_EXT)


def zip_dir(zf, src, prefix=''):
    for p in sorted(Path(src).rglob('*')):
        if p.is_file() and '__pycache__' not in p.parts: zf.write(p, prefix + p.relative_to(src).as_posix())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--version', action='store_true'); ap.add_argument('--launcher', action='store_true')
    ap.add_argument('--dist', default=''); ap.add_argument('--out', default='out'); ap.add_argument('--repo', default='tpc20001/TikLive')
    a = ap.parse_args()
    ver = app_version(); L = launcher_version()
    if a.version: print(ver); return
    if a.launcher: print(L); return
    for f in app_files():
        if f.suffix == '.py': compile(f.read_text(encoding='utf-8'), str(f), 'exec')
        else: json.loads(f.read_text(encoding='utf-8'))
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    tag = f'v{ver}'; base = f'https://github.com/{a.repo}/releases/download/{tag}/'

    zp = out / f'TK_V{ver}_Update.zip'
    with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('manifest.json', json.dumps({'app': 'TikLive', 'version': ver, 'requires_launcher': 1}))
        for f in app_files(): zf.write(f, 'app/' + f.name)
    files = {'zip': zp}
    if a.dist:
        d = Path(a.dist)
        if not (d / 'TikLiveMonitor.exe').exists(): sys.exit(f'找不到 {d / "TikLiveMonitor.exe"}')
        sp = out / f'TK_Shell_L{L}.zip'
        with zipfile.ZipFile(sp, 'w', zipfile.ZIP_DEFLATED) as zf: zip_dir(zf, d)
        fp = out / f'TikLive_Full_V{ver}.zip'
        with zipfile.ZipFile(fp, 'w', zipfile.ZIP_DEFLATED) as zf:
            zip_dir(zf, d, 'TikLiveMonitor/')
            for f in app_files(): zf.write(f, 'TikLiveMonitor/app/' + f.name)
            ico = ROOT / 'TikLiveMonitor.ico'
            if ico.exists(): zf.write(ico, 'TikLiveMonitor/TikLiveMonitor.ico')
            for n in ('UPDATE', 'LOG', 'Package'): zf.writestr(f'TikLiveMonitor/{n}/', '')
        files.update(shell=sp, full=fp)

    try: C = json.loads((APP / 'CHANGELOG.json').read_text(encoding='utf-8'))
    except Exception: C = []
    cur = next((e for e in C if str(e.get('version')) == ver), None) or {}
    info = {'app': 'TikLive', 'version': ver, 'launcher': L, 'date': cur.get('date', ''), 'tag': tag, 'notes': list(cur.get('items') or []),
            'zip': base + files['zip'].name, 'zip_sha256': sha(files['zip']), 'zip_size': files['zip'].stat().st_size}
    if 'shell' in files:
        info.update(shell=base + files['shell'].name, shell_sha256=sha(files['shell']), shell_size=files['shell'].stat().st_size,
                    full=base + files['full'].name, full_sha256=sha(files['full']), full_size=files['full'].stat().st_size)
    (out / 'update.json').write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding='utf-8')
    md = [f'## TikLive Monitor V{ver}', '']
    md += [f'- {x}' for x in info['notes']] or ['- （這版沒有寫更新說明）']
    md += ['', '### 檔案', f'- `TK_V{ver}_Update.zip`：程式更新包（程式裡按「☁ 更新」會自己下載，熱更新、不中斷錄影）',
           f'- `TK_Shell_L{L}.zip`：EXE 外殼（第 {L} 版啟動器），換 EXE 才用', f'- `TikLive_Full_V{ver}.zip`：第一次安裝用（不含 FFmpeg、資料）',
           '- `update.json`：給程式讀的版本資訊']
    (out / 'notes.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in info.items() if k != 'notes'}, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
