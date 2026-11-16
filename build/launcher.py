"""TikLive Monitor 啟動器（TikLiveMonitor.exe）.

EXE 裡只有 Python、PySide6、TikTokLive（雲端用 PyInstaller 打包）。真正的程式在 <ROOT>\\app\\*.py，更新只換那裡：
- 熱更新：程式裡「☁ 更新」／線上更新／手機上傳 → 不關程式、監控錄影不中斷。
- 放進 <ROOT>\\UPDATE\\*.zip → 下次開程式時由這裡套用（先備份 app_backup，新版開不起來自動退回）。
TikLive 24 小時錄影：這裡不跳會擋住的視窗（沒人按「確定」就開不起來），全部寫進 LOG\\update_log.txt。
"""
import os, sys, json, shutil, zipfile, runpy, time, traceback, re
from pathlib import Path

# 程式會用到的模組列在 build/_deps.py，打包時用 --hidden-import _deps 包進 EXE（執行時不先全部載入）

LAUNCHER_VERSION = 2          # V1.1.13 雲端自動更新：設環境變數 TK_LAUNCHER，程式才知道 EXE 要不要換
EXE_NAME = "TikLiveMonitor.exe"
ROOT = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent.parent
APP_DIR = ROOT / "app"
UPDATE_DIR = ROOT / "UPDATE"
BACKUP_DIR = ROOT / "app_backup"
LOG_DIR = ROOT / "LOG"


def log(msg):
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with (LOG_DIR / "update_log.txt").open("a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [啟動器 L{LAUNCHER_VERSION}] {msg}\n")
    except Exception:
        pass


def note(text, title="TikLive Monitor", error=False, secs=20):
    """會自己關掉的提示（Windows MessageBoxTimeout）：沒人在電腦前也不會卡住開機."""
    try:
        import ctypes
        f = ctypes.windll.user32.MessageBoxTimeoutW
        f(None, str(text), title, 0x10 if error else 0x40, 0, int(secs * 1000))
    except Exception:
        print(title, text)


def vkey(name):
    return tuple(int(x) for x in re.findall(r"\d+", name)) or (0,)


def apply_updates():
    """UPDATE\\*.zip 照版本順序套用；回傳 (第一個備份, 套用了哪些版本)."""
    if not UPDATE_DIR.exists():
        return None, []
    zips = sorted(UPDATE_DIR.glob("*.zip"), key=lambda p: vkey(p.stem))
    first_backup = None; applied = []
    for z in zips:
        backup = None
        try:
            with zipfile.ZipFile(z) as zf:
                manifest = {}
                if "manifest.json" in zf.namelist():
                    manifest = json.loads(zf.read("manifest.json").decode("utf-8-sig"))
                if str(manifest.get("app") or "TikLive") != "TikLive":
                    raise RuntimeError("這不是 TikLive 的更新包")
                need = int(manifest.get("requires_launcher", 1))
                if need > LAUNCHER_VERSION:
                    log(f"SKIP {z.name}: 要第 {need} 版啟動器（現在 {LAUNCHER_VERSION}），等換新 EXE 再套用")
                    continue
                members = [m for m in zf.namelist() if m.startswith("app/") and not m.endswith("/")]
                for m in members:
                    if ".." in Path(m).parts or Path(m).is_absolute():
                        raise RuntimeError(f"不安全的路徑：{m}")
                if not members:
                    raise RuntimeError("更新包裡沒有 app/ 的檔案")
                for m in members:
                    if m.endswith(".py"): compile(zf.read(m).decode("utf-8"), m, "exec")
                stamp = time.strftime("%Y%m%d_%H%M%S")
                backup = BACKUP_DIR / f"{stamp}_before_{z.stem}"
                if APP_DIR.exists():
                    shutil.copytree(APP_DIR, backup, ignore=shutil.ignore_patterns("__pycache__"))
                first_backup = first_backup or backup
                for m in members:
                    dest = ROOT / m
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    tmp = dest.with_suffix(dest.suffix + ".new")
                    tmp.write_bytes(zf.read(m))
                    os.replace(tmp, dest)
                shutil.rmtree(APP_DIR / "__pycache__", ignore_errors=True)
            done = UPDATE_DIR / "applied"; done.mkdir(exist_ok=True)
            os.replace(z, done / z.name)
            applied.append(manifest.get("version") or z.stem)
            log(f"APPLIED {z.name}（備份 {first_backup}）")
        except Exception as e:
            log(f"FAILED {z.name}: {e}")
            if backup is not None and backup.exists():
                try: restore(backup); log(f"RESTORED {backup}（{z.name} 套用失敗）")
                except Exception as e2: log(f"RESTORE FAILED: {e2}")
            try:
                bad = UPDATE_DIR / "failed"; bad.mkdir(exist_ok=True); os.replace(z, bad / z.name)
            except Exception: pass
    try:
        for d in sorted([p for p in BACKUP_DIR.iterdir() if p.is_dir()], key=lambda p: p.name)[:-5]: shutil.rmtree(d, ignore_errors=True)
    except Exception:
        pass
    return first_backup, applied


def restore(backup):
    shutil.rmtree(APP_DIR, ignore_errors=True)
    shutil.copytree(backup, APP_DIR)


def run_app():
    os.environ["TK_LAUNCHER"] = str(LAUNCHER_VERSION)
    sys.path.insert(0, str(APP_DIR))
    for mod in ("app", "core", "webpc_api", "webpc_page"):
        sys.modules.pop(mod, None)
    runpy.run_path(str(APP_DIR / "app.py"), run_name="__main__")


def cleanup_shell():
    """上次換 EXE 留下的舊檔（換好、開得起來就不需要了）."""
    # _internal_old、.old 留給換 EXE 的 BAT：程式開起來回報（UPDATE/shell_ok.flag）它才刪；開不起來它會換回舊的
    shutil.rmtree(ROOT / "UPDATE" / "shell_new", ignore_errors=True)


def selftest():
    """雲端打包完試一下這個 EXE：模組都在、Qt 能開（不開主程式）."""
    import importlib
    bad = []; prog = ROOT / "selftest_step.txt"
    def step(s):
        try:
            with prog.open("a", encoding="utf-8") as f: f.write(f"{time.strftime('%H:%M:%S')} {s}\n")
        except Exception: pass
    step("開始")
    for m in ("_deps", "PySide6.QtCore", "PySide6.QtGui", "PySide6.QtWidgets", "PySide6.QtMultimedia", "PySide6.QtNetwork", "httpx", "TikTokLive",
              "TikTokLive.events", "TikTokLive.client.web.web_client", "sqlite3", "ssl", "zlib", "wave", "ctypes.wintypes"):
        step("載入 " + m)
        try: importlib.import_module(m)
        except BaseException as e: bad.append(f"{m}: {type(e).__name__}: {e}")
    try:   # 不開視窗（雲端沒有螢幕，Qt 出錯會跳對話框卡住）：只確認畫面外掛（qwindows.dll）有打包進來
        from PySide6.QtCore import QLibraryInfo
        pl = Path(QLibraryInfo.path(QLibraryInfo.LibraryPath.PluginsPath)) / "platforms"
        if not any(pl.glob("qwindows*.dll")): bad.append(f"找不到 Qt 畫面外掛 qwindows.dll（{pl}）")
        mm = Path(QLibraryInfo.path(QLibraryInfo.LibraryPath.PluginsPath)) / "multimedia"
        if not mm.exists(): bad.append(f"找不到 Qt 多媒體外掛（{mm}）")
    except Exception as e: bad.append(f"Qt 外掛: {e}")
    try:
        import TikTokLive; v = getattr(TikTokLive, "__version__", "?")
    except Exception: v = "?"
    step("完成")
    out = {"ok": not bad, "launcher": LAUNCHER_VERSION, "tiktoklive": v, "bad": bad}
    (ROOT / "selftest.json").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    try:
        if sys.stdout: print(json.dumps(out, ensure_ascii=False))
    except Exception: pass
    return 0 if not bad else 2


def main():
    if "--selftest" in sys.argv: return selftest()
    os.chdir(ROOT)
    log(f"啟動 {sys.executable}")
    backup, applied = apply_updates()
    if not (APP_DIR / "app.py").exists():
        log("找不到 app\\app.py")
        note(f"找不到程式檔：\n{APP_DIR / 'app.py'}\n\n請重新安裝或放入更新檔。", error=True, secs=60)
        return 1
    if applied: log("已套用：" + "、".join(applied))
    cleanup_shell()
    try:
        run_app()
    except SystemExit as e:
        return e.code or 0
    except Exception:
        err = traceback.format_exc(); log("START FAILED\n" + err)
        if backup is not None:
            restore(backup); log(f"ROLLED BACK to {backup}（新版開不起來，退回更新前的版本再開一次）")
            if getattr(sys, "frozen", False): os.execv(sys.executable, [sys.executable] + sys.argv[1:])
        else:
            note("程式啟動失敗，詳細錯誤記錄在 LOG\\update_log.txt。\n\n" + err[-800:], error=True, secs=60)
        return 1
    return 0


if __name__ == "__main__":
    try: rc = main()
    except BaseException:
        log("啟動器出錯\n" + traceback.format_exc()); rc = 3
    sys.exit(rc)
