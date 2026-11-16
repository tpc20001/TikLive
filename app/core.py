from __future__ import annotations

import asyncio
import csv
import json
import os
import queue
import sqlite3
import sys
import threading
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

APP_VERSION = "0.4.94"
SID_CAP = 9000000   # TK_V0.9.79 直播場次編號 < 900 萬；手機錄屏匯入的「沒有紀錄的場次」用 900 萬以上（顯示成 P0001…）
# V0.4.51 layout (fixed, version-free folders so updates never need a data move):
# <ROOT>\TikLiveMonitor.exe   launcher (Python + PySide6 + TikTokLive, rarely rebuilt)
# <ROOT>\app\app.py, core.py  program code (replaced by update packages)
# <ROOT>\UPDATE\*.zip         drop update packages here; applied on next launch
# <ROOT>\Package\...          persistent data (DB, CONFIG, settings, audio)
# <ROOT>\LOG\...              disposable human-readable logs
PACKAGE_FOLDER_NAME = "Package"

if getattr(sys, "frozen", False):
    PACKAGE_ROOT = Path(sys.executable).resolve().parent
else:
    # source run: <ROOT>\app\core.py  (or the legacy <ROOT>\TikLiveMonitor_GUI\core.py)
    PACKAGE_ROOT = Path(__file__).resolve().parent.parent
APP_DIR = PACKAGE_ROOT
# V0.4.94: the data (Package + LOG) may live on another drive. DATA_LOCATION.txt next to the EXE holds
# that folder (e.g. E:\TikLiveMonitor_Data). If the drive is missing we fall back to the install folder
# and report it, instead of crashing.
DATA_LOCATION_FILE = PACKAGE_ROOT / "DATA_LOCATION.txt"
DATA_ROOT = PACKAGE_ROOT
DATA_LOCATION_ERROR = ""
try:
    _loc = DATA_LOCATION_FILE.read_text(encoding="utf-8").strip() if DATA_LOCATION_FILE.exists() else ""
    if _loc:
        if (Path(_loc) / PACKAGE_FOLDER_NAME).is_dir(): DATA_ROOT = Path(_loc)
        else: DATA_LOCATION_ERROR = f"找不到資料位置 {_loc}（磁碟未連接？），暫時使用安裝資料夾"
except Exception as _e:
    DATA_LOCATION_ERROR = f"讀取資料位置失敗：{_e}"
PACKAGE_DATA_DIR = DATA_ROOT / PACKAGE_FOLDER_NAME
LOG_DIR = DATA_ROOT / "LOG"
# V0.6.43 LOG 也放 C 槽（程式資料夾\LOG）：資料在另一顆硬碟時，紀錄檔不要在機械硬碟上一直小筆寫入。
# 設定「LOG 也放在 C 槽 SSD」關掉 → 主程式留一個 _DB_SSD\LOG_ON_DATA_DISK 檔 → 下次啟動回到資料硬碟的 LOG。
try:
    if DATA_ROOT != PACKAGE_ROOT and (Path(PACKAGE_ROOT).drive or "").upper() != (Path(DATA_ROOT).drive or "").upper() \
            and not (PACKAGE_ROOT / "_DB_SSD" / "LOG_ON_DATA_DISK").exists():
        LOG_DIR = PACKAGE_ROOT / "LOG"
except Exception:
    pass
CORE_FILE_MTIME = 0.0
try: CORE_FILE_MTIME = os.path.getmtime(__file__)
except Exception: pass
CORE_FILE_SHA = ""                 # V0.6.45 內容比對（更新包每次都會重寫 core.py，只看時間會誤判）
try:
    import hashlib as _hl
    with open(__file__, "rb") as _f: CORE_FILE_SHA = _hl.sha1(_f.read()).hexdigest()
except Exception: pass
EXPORT_DIR = LOG_DIR  # human-readable session exports stay outside Package


def _version_key(name: str):
    import re as _re
    return tuple(int(x) for x in _re.findall(r"\d+", name))


def migrate_legacy_package(root: Path = None) -> Optional[str]:
    """First launch only: copy the newest legacy 'Package V0.4.xx' folder into 'Package'.
    The legacy folder is left untouched (copy, never move)."""
    root = PACKAGE_ROOT if root is None else root
    target = root / PACKAGE_FOLDER_NAME
    if target.exists() and any(target.iterdir()):
        return None
    legacy = [d for d in root.glob("Package V*") if d.is_dir()]
    if not legacy:
        return None
    src = max(legacy, key=lambda d: _version_key(d.name))
    import shutil as _shutil
    tmp = root / (PACKAGE_FOLDER_NAME + ".migrating")
    if tmp.exists():
        _shutil.rmtree(tmp, ignore_errors=True)
    _shutil.copytree(src, tmp, ignore=_shutil.ignore_patterns("*.sqlite3-wal", "*.sqlite3-shm"))
    # carry any un-checkpointed WAL content: copy the DB through SQLite backup
    db = src / "TikLiveMonitor_History.sqlite3"
    if db.exists():
        try:
            import sqlite3 as _sq
            s_con = _sq.connect(str(db)); d_con = _sq.connect(str(tmp / db.name))
            s_con.backup(d_con); d_con.close(); s_con.close()
        except Exception:
            pass
    if target.exists():
        _shutil.rmtree(target, ignore_errors=True)
    os.replace(tmp, target)
    return src.name


try:
    MIGRATED_FROM = migrate_legacy_package() if DATA_ROOT == PACKAGE_ROOT else None
except Exception:
    MIGRATED_FROM = None
PACKAGE_DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)
# Persistent history belongs to Package so copying the Package folder to a new
# version carries sessions, statistics and all stored history with it.
HISTORY_DB_PATH = PACKAGE_DATA_DIR / "TikLiveMonitor_History.sqlite3"
DB_PATH = HISTORY_DB_PATH

# ---------------------------------------------------------------------------------------------------------
# V0.6.40 資料庫放在 C 槽 SSD（影片、錄音、LOG 照樣留在資料硬碟）
# 機械硬碟上的資料庫：39 個直播間每秒很多筆小寫入 → 硬碟 100% 但不到 1 MB/s。搬到 SSD 就沒有這個問題。
# 只在「程式剛啟動、還沒有任何連線打開資料庫」時搬（主程式按重新啟動、或睡覺時段自動）：
#   完整整理 → SQLite 備份 API 複製 → quick_check ＋ 每個表最後一筆的編號比對 → 通過才切換。
#   舊的那份改名保留（不刪）。任何一步失敗 → 繼續用原本那份，寫進 LOG。
# 這段只在程式啟動時跑一次（熱更新不會重新載入 core.py）。
# ---------------------------------------------------------------------------------------------------------
DB_HDD_PATH = HISTORY_DB_PATH
DB_SSD_DIR = PACKAGE_ROOT / "_DB_SSD"
DB_SSD_PATH = DB_SSD_DIR / "TikLiveMonitor_History.sqlite3"
DB_STATE_FILE = DB_SSD_DIR / "db_location.json"
DB_MOVE_REQUEST = DB_SSD_DIR / "MOVE_REQUEST.json"
DB_BACKUP_DIR = PACKAGE_DATA_DIR / "db_backups_ssd"
DB_MOVE_RESULT = ""


def _dbm_log(msg: str) -> None:
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 資料庫位置：{msg}\n"
    for f in (LOG_DIR / "update_log.txt", LOG_DIR / "db_move.log"):
        try:
            with open(f, "a", encoding="utf-8") as fh: fh.write(line)
        except Exception: pass


def db_same_drive() -> bool:
    try: return (Path(PACKAGE_ROOT).drive or "").upper() == (Path(PACKAGE_DATA_DIR).drive or "").upper()
    except Exception: return True


def db_state() -> dict:
    try: return json.loads(DB_STATE_FILE.read_text(encoding="utf-8")) if DB_STATE_FILE.exists() else {}
    except Exception: return {}


def _db_state_write(st: dict) -> None:
    DB_SSD_DIR.mkdir(parents=True, exist_ok=True)
    tmp = DB_STATE_FILE.with_suffix(".tmp"); tmp.write_text(json.dumps(st, ensure_ascii=False, indent=1), encoding="utf-8"); os.replace(tmp, DB_STATE_FILE)


def _db_last_ids(con) -> dict:
    out = {}
    for t in ("sessions", "comments", "gifts", "joins", "likes"):
        try: out[t] = con.execute(f"SELECT MAX(id) FROM {t}").fetchone()[0] or 0
        except Exception: pass
    return out


def db_copy_verified(src: Path, dst: Path, checkpoint: bool = True) -> dict:
    """Copy a SQLite file safely: full checkpoint (only when nobody else has it open), backup API into dst + '.copying',
    quick_check, compare the last id of the big tables, then rename into place. Raises on any problem (dst untouched)."""
    import shutil as _sh
    src, dst = Path(src), Path(dst); dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_name(dst.name + ".copying")
    for f in (tmp, Path(str(tmp) + "-wal"), Path(str(tmp) + "-shm")):
        try: f.unlink()
        except Exception: pass
    t0 = time.time()
    s = sqlite3.connect(str(src), timeout=120); s.execute("PRAGMA busy_timeout=120000")
    try:
        if checkpoint:
            r = s.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone()
            if r and r[0]: raise RuntimeError("資料庫還被別的程式打開著（整理不完），這次不搬")
        size = src.stat().st_size
        free = _sh.disk_usage(str(dst.parent)).free
        if free < size * 1.3 + 3 * 1024 ** 3: raise RuntimeError(f"目的地空間不夠：需要約 {size * 1.3 / 1e9 + 3:.1f} GB，只剩 {free / 1e9:.1f} GB")
        ids_src = _db_last_ids(s)
        d = sqlite3.connect(str(tmp))
        try:
            s.backup(d, pages=16384)
            try: d.execute("PRAGMA journal_mode=WAL")
            except Exception: pass
            qc = d.execute("PRAGMA quick_check").fetchone()[0]
            if str(qc).lower() != "ok": raise RuntimeError(f"複製後檢查不通過：{qc}")
            ids_dst = _db_last_ids(d)
            if ids_dst != ids_src: raise RuntimeError(f"複製後筆數對不上：{ids_src} → {ids_dst}")
        finally: d.close()
    except Exception:
        for f in (tmp, Path(str(tmp) + "-wal"), Path(str(tmp) + "-shm")):
            try: f.unlink()
            except Exception: pass
        raise
    finally: s.close()
    for f in (Path(str(tmp) + "-wal"), Path(str(tmp) + "-shm")):
        try: f.unlink()
        except Exception: pass
    os.replace(tmp, dst)
    return {"bytes": dst.stat().st_size, "secs": round(time.time() - t0, 1), "ids": ids_src}


def db_copy_raw(src: Path, dst: Path) -> dict:
    """V0.6.42 fastest safe copy when NOBODY has the database open (program start): copy the database file and its -wal
    file byte for byte (one long sequential read of the hard disk – no seeking), then open the copy on the destination,
    finish the WAL there (fast on the SSD), quick_check, rename into place. The source is never opened (so SQLite never
    writes to the slow disk). Raises on any problem (dst untouched)."""
    import shutil as _sh
    src, dst = Path(src), Path(dst); dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_name(dst.name + ".copying"); tw, ts = Path(str(tmp) + "-wal"), Path(str(tmp) + "-shm")
    sw = Path(str(src) + "-wal")
    for f in (tmp, tw, ts):
        try: f.unlink()
        except Exception: pass
    t0 = time.time(); need = src.stat().st_size + (sw.stat().st_size if sw.exists() else 0)
    free = _sh.disk_usage(str(dst.parent)).free
    if free < need * 1.2 + 3 * 1024 ** 3: raise RuntimeError(f"目的地空間不夠：需要約 {need * 1.2 / 1e9 + 3:.1f} GB，只剩 {free / 1e9:.1f} GB")
    # Windows: a file that another program has open cannot be renamed -> proves nobody is using the database right now
    for f in (src, sw):
        if not f.exists(): continue
        probe = f.with_name(f.name + ".lockprobe")
        try: os.replace(f, probe); os.replace(probe, f)
        except Exception as e: raise RuntimeError(f"資料庫還被別的程式打開著（{e}）")
    def cp(a, b):
        with open(a, "rb") as fi, open(b, "wb") as fo:
            while True:
                buf = fi.read(16 * 1024 * 1024)
                if not buf: break
                fo.write(buf)
            fo.flush(); os.fsync(fo.fileno())
        if Path(a).stat().st_size != Path(b).stat().st_size: raise RuntimeError(f"複製後大小不同：{Path(a).name}")
    try:
        cp(src, tmp)
        if sw.exists() and sw.stat().st_size > 0: cp(sw, tw)
        t_copy = time.time() - t0
        d = sqlite3.connect(str(tmp), timeout=30)
        try:
            d.execute("PRAGMA journal_mode=WAL")
            r = d.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone()
            if r and r[0]: raise RuntimeError("整理複製出來的資料庫時被占用")
            qc = d.execute("PRAGMA quick_check").fetchone()[0]
            if str(qc).lower() != "ok": raise RuntimeError(f"複製後檢查不通過：{qc}")
            ids = _db_last_ids(d)
        finally: d.close()
    except Exception:
        for f in (tmp, tw, ts):
            try: f.unlink()
            except Exception: pass
        raise
    for f in (tw, ts):
        try: f.unlink()
        except Exception: pass
    os.replace(tmp, dst)
    return {"bytes": dst.stat().st_size, "read": need, "secs": round(time.time() - t0, 1), "copy_secs": round(t_copy, 1), "ids": ids, "how": "raw"}


def _db_copy_best(src: Path, dst: Path) -> dict:
    """Raw copy first (fast); if that fails for any reason other than space, fall back to the SQLite backup API (slow, safe)."""
    try: return db_copy_raw(src, dst)
    except Exception as e:
        if "空間不夠" in str(e): raise
        _dbm_log(f"快速複製沒有成功（{e}），改用 SQLite 備份方式再試一次")
        r = db_copy_verified(src, dst); r["how"] = "backup"; return r


def _db_stamp() -> str:
    return time.strftime("%Y%m%d_%H%M%S")


def _db_choose_location() -> None:
    global DB_PATH, HISTORY_DB_PATH, DB_MOVE_RESULT
    st = db_state()
    req = None
    try:
        if DB_MOVE_REQUEST.exists():
            req = json.loads(DB_MOVE_REQUEST.read_text(encoding="utf-8") or "{}")
            DB_MOVE_REQUEST.unlink()            # handled once, even if something below crashes (never a restart loop)
    except Exception as e:
        _dbm_log(f"讀取搬移要求失敗：{e}")
    if req:
        to = req.get("to")
        try:
            if to == "ssd" and st.get("active") != "ssd":
                if db_same_drive(): raise RuntimeError("程式和資料在同一顆硬碟，不用搬")
                if not DB_HDD_PATH.exists(): raise RuntimeError(f"找不到資料庫 {DB_HDD_PATH}")
                _dbm_log(f"開始搬到 C 槽 SSD（{req.get('why', '')}）：{DB_HDD_PATH} → {DB_SSD_PATH}")
                r = _db_copy_best(DB_HDD_PATH, DB_SSD_PATH)
                old = DB_HDD_PATH.with_name(DB_HDD_PATH.name + f".moved_to_SSD_{_db_stamp()}")
                os.replace(DB_HDD_PATH, old)
                for ext in ("-wal", "-shm"):
                    f = Path(str(DB_HDD_PATH) + ext)
                    if f.exists():
                        try: os.replace(f, Path(str(old) + ext))
                        except Exception: pass
                st = {"active": "ssd", "since": time.time(), "ssd": str(DB_SSD_PATH), "hdd_old": str(old), "copy": r}
                _db_state_write(st)
                DB_MOVE_RESULT = f"✔ 資料庫已搬到 C 槽 SSD（{r['bytes'] / 1e9:.2f} GB，{r['secs']} 秒{'，快速複製' if r.get('how') == 'raw' else ''}）；舊的保留在 {old.name}"
                _dbm_log(DB_MOVE_RESULT)
            elif to == "hdd" and st.get("active") == "ssd":
                if not DB_SSD_PATH.exists(): raise RuntimeError(f"找不到 C 槽的資料庫 {DB_SSD_PATH}")
                _dbm_log(f"開始搬回資料硬碟（{req.get('why', '')}）：{DB_SSD_PATH} → {DB_HDD_PATH}")
                if DB_HDD_PATH.exists(): os.replace(DB_HDD_PATH, DB_HDD_PATH.with_name(DB_HDD_PATH.name + f".old_{_db_stamp()}"))
                r = _db_copy_best(DB_SSD_PATH, DB_HDD_PATH)
                old = DB_SSD_PATH.with_name(DB_SSD_PATH.name + f".moved_to_HDD_{_db_stamp()}")
                os.replace(DB_SSD_PATH, old)
                st = {"active": "hdd", "since": time.time(), "ssd_old": str(old), "copy": r}
                _db_state_write(st)
                DB_MOVE_RESULT = f"✔ 資料庫已搬回資料硬碟（{r['bytes'] / 1e9:.2f} GB，{r['secs']} 秒）；C 槽那份保留在 {old.name}"
                _dbm_log(DB_MOVE_RESULT)
        except Exception as e:
            DB_MOVE_RESULT = f"✖ 資料庫搬移沒有成功，繼續用原本那份：{e}"
            _dbm_log(DB_MOVE_RESULT)
            try:
                st = dict(st); st["fail_t"] = time.time(); st["fail_msg"] = str(e)[:300]; _db_state_write(st)
            except Exception: pass
    if st.get("active") == "ssd":
        if DB_SSD_PATH.exists():
            DB_PATH = HISTORY_DB_PATH = DB_SSD_PATH
        else:
            # never start on an empty database: take the newest copy we have (daily backup on the data disk, or the old HDD file)
            cands = [Path(x) for x in [st.get("hdd_old", "")] if x] + (sorted(DB_BACKUP_DIR.glob("*.sqlite3")) if DB_BACKUP_DIR.exists() else [])
            cands = [c for c in cands if c.exists()]
            if cands:
                best = max(cands, key=lambda c: c.stat().st_mtime)
                try:
                    db_copy_verified(best, DB_SSD_PATH, checkpoint=False)
                    DB_PATH = HISTORY_DB_PATH = DB_SSD_PATH
                    DB_MOVE_RESULT = f"⚠ C 槽的資料庫不見了，已用最新的一份備份接回來：{best.name}"
                except Exception as e:
                    DB_MOVE_RESULT = f"⚠ C 槽的資料庫不見了，備份也接不回來（{e}），暫時用資料硬碟的位置"
            else:
                DB_MOVE_RESULT = "⚠ C 槽的資料庫不見了，也找不到備份，暫時用資料硬碟的位置"
            _dbm_log(DB_MOVE_RESULT)


try:
    _db_choose_location()
except Exception as _e:
    DB_MOVE_RESULT = f"✖ 選擇資料庫位置時出錯，用原本的位置：{_e}"
    _dbm_log(DB_MOVE_RESULT)


# V0.6.42 重新啟動主程式前，正在直播的場次記在 resume_handoff.json；新程式連回同一個直播間就「續寫同一場」
# （跟斷線 10 分鐘內重連一樣），不會變成新的一場。只用一次、超過 15 分鐘就不算。
RESUME_HANDOFF_FILE = DB_SSD_DIR / "resume_handoff.json"
RESUME_HANDOFF: dict = {}
try:
    if RESUME_HANDOFF_FILE.exists():
        _h = json.loads(RESUME_HANDOFF_FILE.read_text(encoding="utf-8") or "{}")
        RESUME_HANDOFF_FILE.unlink()
        if time.time() - float(_h.get("t") or 0) <= 900:
            RESUME_HANDOFF = {str(k): dict(v, t=float(_h.get("t") or 0)) for k, v in (_h.get("rooms") or {}).items() if v.get("sid")}
        _dbm_log(f"重新啟動接續：{len(RESUME_HANDOFF)} 個直播中的場次等著續寫")
except Exception as _e:
    _dbm_log(f"讀取重新啟動接續資料失敗：{_e}")


def _take_handoff(username: str):
    try: return RESUME_HANDOFF.pop(str(username), None)
    except Exception: return None
SCHEMA_INIT_LOCK = threading.Lock()


def now_iso(ts: Optional[float] = None) -> str:
    value = time.time() if ts is None else float(ts)
    try:
        return datetime.fromtimestamp(value).astimezone().isoformat(timespec="milliseconds")
    except OSError:
        # Windows can reject very old epoch values during local-time conversion.
        return datetime.utcfromtimestamp(value).isoformat(timespec="milliseconds") + "Z"


def fmt_elapsed(sec: Optional[float]) -> str:
    if sec is None:
        return "--:--:--"
    sec = max(0, int(sec))
    return f"{sec//3600:02d}:{(sec%3600)//60:02d}:{sec%60:02d}"


def fmt_ms(sec: Optional[float]) -> str:
    if sec is None:
        return "00:00:00,000"
    ms = max(0, int(sec * 1000))
    return f"{ms//3600000:02d}:{(ms%3600000)//60000:02d}:{(ms%60000)//1000:02d},{ms%1000:03d}"


def fmt_real(ts: Optional[float]) -> str:
    if not ts:
        return "--:--:--.---"
    return datetime.fromtimestamp(ts).strftime("%H:%M:%S.%f")[:-3]


def nested(obj: Any, *names: str, default=None):
    for name in names:
        if obj is None:
            return default
        if isinstance(obj, dict):
            obj = obj.get(name)
        else:
            obj = getattr(obj, name, None)
    return default if obj is None else obj


def user_info(user: Any) -> dict:
    return {
        "id": str(getattr(user, "user_id", getattr(user, "id", "")) or ""),
        "unique_id": str(getattr(user, "unique_id", "") or ""),
        "nickname": str(getattr(user, "nickname", getattr(user, "unique_id", "")) or ""),
    }


def image_url(img: Any) -> str:
    """First http URL of a TikTok Image message (field names changed between TikTokLive versions)."""
    if img is None:
        return ""
    for attr in ("m_urls", "url_list", "urls", "url", "uri"):
        v = getattr(img, attr, None) if not isinstance(img, dict) else img.get(attr)
        if isinstance(v, (list, tuple)):
            for x in v:
                if str(x or "").startswith("http"):
                    return str(x)
        elif isinstance(v, str) and v.startswith("http"):
            return v
    return ""


def gift_image_url(gift: Any) -> str:
    """V0.6.46 the official picture of a gift (PNG/WebP on TikTok's CDN) as sent inside the gift event."""
    for attr in ("image", "icon", "gift_label_icon"):
        try:
            u = image_url(getattr(gift, attr, None) if not isinstance(gift, dict) else gift.get(attr))
        except Exception:
            u = ""
        if u:
            return u
    return ""


def event_id(event: Any) -> str:
    # TikTokLive 7.x has used several names over its history.
    for name in ("msg_id", "message_id", "event_id", "transaction_id"):
        value = getattr(event, name, None)
        if value:
            return str(value)
    common = getattr(event, "common", None)
    value = nested(common, "msg_id", default=None)
    return str(value) if value else ""


def event_create_time(event: Any) -> Optional[float]:
    """Return TikTok supplied event creation time when available."""
    candidates = [
        getattr(event, "create_time", None),
        nested(event, "common", "create_time", default=None),
        nested(event, "common", "createTime", default=None),
        nested(event, "message", "create_time", default=None),
    ]
    for raw in candidates:
        if raw is None:
            continue
        try:
            value = float(raw)
            if value > 10_000_000_000:
                value /= 1000.0
            # Reject obviously bogus proto values.
            if 946684800 <= value <= time.time() + 120:
                return value
        except Exception:
            pass
    return None


def parse_song_comment(text: Any) -> str:
    """點歌: a comment starting with # (whole rest is the song, as before), or V0.6.51 a # in the middle of the
    comment ("可以點歌嗎 #淚橋 謝謝") → the song is the text right after # up to the next space."""
    raw = str(text or "").strip()
    if not raw:
        return ""
    if raw[0] in ("#", "＃"):
        return raw[1:].strip()
    import re as _re
    for m in _re.finditer(r"[#＃]+([^\s#＃,，。!！?？~～、:：;；]+)", raw):
        song = m.group(1).strip(" .")
        before = raw[m.start() - 1] if m.start() > 0 else " "
        if not song or song.isdigit() or (song[0].isdigit() and not before.isspace()):   # 「第#1名」不是點歌
            continue
        return song
    return ""


def _to_int(value: Any) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    try:
        if isinstance(value, str):
            m = __import__("re").search(r"-?\d+", value)
            if not m:
                return None
            return int(m.group(0))
        return int(value)
    except Exception:
        return None


def _enum_text(value: Any) -> str:
    try:
        return str(value or "").upper()
    except Exception:
        return ""


def extract_levelup_info(event: Any) -> Optional[dict]:
    """Extract TikTok Barrage USERUPGRADE payload without guessing missing data."""
    event_kind = getattr(event, "event", None)
    kind_text = _enum_text(event_kind)
    is_upgrade = ("USERUPGRADE" in kind_text or "UPGRADE" in kind_text or event_kind == 8)
    if not is_upgrade:
        return None
    param = getattr(event, "user_grade_param", None)
    if param is None:
        return None
    new_level = _to_int(getattr(param, "current_grade", getattr(param, "currentGrade", None)))
    if new_level is None:
        new_level = _to_int(getattr(param, "new_level", getattr(param, "newLevel", None)))
    if new_level is None:
        return None
    grade_user = getattr(param, "user", None)
    user = getattr(event, "user", None) or grade_user
    ui = user_info(user)
    if not ui.get("unique_id") and grade_user is not None:
        ui = user_info(grade_user)
    common = getattr(event, "common", None)
    eid = event_id(event) or str(getattr(param, "user_id", "") or "")
    if eid and not event_id(event):
        eid = f"upgrade:{eid}:{new_level}"
    raw_summary = f"{kind_text or 'USERUPGRADE'} current_grade={new_level}"
    privilege_key = str(getattr(event, "privilege_key", "") or "")
    action = str(getattr(event, "action", "") or "")
    return {
        "event_id": eid, "username": ui.get("unique_id", ""), "nickname": ui.get("nickname", ""), "id": ui.get("id", ""),
        "new_level": new_level, "event_type": kind_text or "USERUPGRADE",
        "privilege_key": privilege_key, "action": action, "raw_summary": raw_summary,
    }


@dataclass(slots=True)
class MonitorEvent:
    kind: str
    ts: float
    data: dict


LOG_FLUSH_SECONDS = 1.0


class LiveLogWriter:
    """Crash-resistant, append-only human-readable logs for one LIVE session."""

    FILES = {
        "dashboard": "00_Dashboard.txt",
        "chat": "01_Chat.txt",
        "chat_srt": "01_Chat.srt",
        "gifts": "02_Gifts.txt",
        "gifters": "03_Gifters.txt",
        "joins": "04_Joins.txt",
        "likes": "05_Likes.txt",
        "analytics": "06_Analytics.txt",
        "sessions": "07_Sessions.txt",
        "profiles": "08_Profiles.txt",
        "viewers": "09_Viewers.txt",
        "songs": "10_Songs.txt",
        "levelups": "11_LevelUp.txt",
    }

    def __init__(self, username: str, sid: int, room_id: str = ""):
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_user = "".join(c for c in (username or "unknown") if c.isalnum() or c in "._-") or "unknown"
        self.path = LOG_DIR / f"{safe_user}_session{sid}_{stamp}"
        self.path.mkdir(parents=True, exist_ok=True)
        self.files = {}
        self.srt_index = 0
        self._lock = threading.RLock()
        for key, filename in self.FILES.items():
            f = (self.path / filename).open("a", encoding="utf-8-sig")
            self.files[key] = f
        # V0.4.51: buffered writes, flushed at most once per second (was flush+fsync per line).
        self._last_flush = 0.0
        self._last_stat_line = {"analytics": 0.0, "dashboard": 0.0}
        self.write("dashboard", f"TikLive Monitor V{APP_VERSION}\n主播: @{username}\nRoom ID: {room_id}\n建立時間: {now_iso()}\n\n")
        self.write("chat", f"TikLive Monitor Chat Log V{APP_VERSION}\n時間 | 直播時間 | 暱稱 | 留言\n" + "-" * 80 + "\n")
        self.write("gifts", f"TikLive Monitor Gifts Log V{APP_VERSION}\n時間 | 直播時間 | 送禮者 | 禮物 | 數量 | Diamonds/件 | Diamonds合計\n" + "-" * 110 + "\n")
        self.write("gifters", f"TikLive Monitor Gifters Log V{APP_VERSION}\n時間 | 送禮者 | 禮物 | 累計數量 | 累計Diamonds\n" + "-" * 90 + "\n")
        self.write("joins", f"TikLive Monitor Join Log V{APP_VERSION}\n時間 | 直播時間 | 暱稱 | 本場Join次數\n" + "-" * 80 + "\n")
        self.write("likes", f"TikLive Monitor Like Log V{APP_VERSION}\n時間 | 直播時間 | 暱稱 | 本次按讚 | 房間累計讚\n" + "-" * 90 + "\n")
        self.write("analytics", f"TikLive Monitor Analytics Log V{APP_VERSION}\n時間 | 留言 | Join | Gifts | Diamonds | Likes | Shares | Follows | 觀眾 | 峰值\n" + "-" * 110 + "\n")
        self.write("sessions", f"Session {sid}\n主播: @{username}\nRoom ID: {room_id}\n開始: {now_iso()}\n")
        self.write("profiles", f"TikLive Monitor Profiles Activity Log V{APP_VERSION}\n時間 | 類型 | 使用者 | 暱稱 | 本次數值\n" + "-" * 90 + "\n")
        self.write("songs", f"TikLive Monitor Song Request Log V{APP_VERSION}\n時間 | 直播時間 | 暱稱 | 歌曲 | 原留言\n" + "-" * 100 + "\n")
        self.write("levelups", f"TikLive Monitor Level Up Log V{APP_VERSION}\n時間 | 直播時間 | 暱稱 | 升級 | 類型\n" + "-" * 90 + "\n")

    def write(self, key: str, text: str):
        with self._lock:
            f = self.files.get(key)
            if not f:
                return
            f.write(text)
            now = time.monotonic()
            if now - self._last_flush >= LOG_FLUSH_SECONDS:
                self._last_flush = now
                for fh in self.files.values():
                    try:
                        fh.flush()
                    except Exception:
                        pass

    def _stat_line_due(self, key, seconds=4.5):
        """analytics/dashboard snapshot lines: at most one every 5 s (was one per event)."""
        now = time.monotonic()
        if now - self._last_stat_line.get(key, 0.0) < seconds:
            return False
        self._last_stat_line[key] = now
        return True

    def chat(self, real_ts, live_sec, nickname, username, comment):
        who = nickname or username or ""
        self.write("chat", f"[{fmt_real(real_ts)[:8]}] [{fmt_elapsed(live_sec)}] {who}: {comment}\n")
        self.srt_index += 1
        start = float(live_sec or 0); end = start + 3
        self.write("chat_srt", f"{self.srt_index}\n{fmt_ms(start)} --> {fmt_ms(end)}\n{who}: {comment}\n\n")

    def gift(self, real_ts, live_sec, nickname, username, gift_name, count, diamond_each, diamonds):
        who = nickname or username or ""
        stamp = f"[{fmt_real(real_ts)[:8]}] [{fmt_elapsed(live_sec)}]"
        self.write("gifts", f"{stamp} {who} -> {gift_name} x{count} | {diamond_each} | {diamonds}\n")
        self.write("gifters", f"{stamp} {who} -> {gift_name} x{count} | {diamonds}\n")

    def join(self, real_ts, live_sec, nickname, username, count):
        who = nickname or username or ""
        self.write("joins", f"[{fmt_real(real_ts)[:8]}] [{fmt_elapsed(live_sec)}] {who} | 本場第 {count} 次\n")

    def like(self, real_ts, live_sec, nickname, username, count, total):
        who = nickname or username or ""
        total_text = str(total) if total is not None else "-"
        self.write("likes", f"[{fmt_real(real_ts)[:8]}] [{fmt_elapsed(live_sec)}] {who} | +{count} | {total_text}\n")

    def song(self, real_ts, live_sec, nickname, username, song, raw_comment=""):
        who = nickname or username or ""
        self.write("songs", f"[{fmt_real(real_ts)[:8]}] [{fmt_elapsed(live_sec)}] {who} | {song} | {raw_comment}\n")

    def level_up(self, real_ts, live_sec, nickname, username, old_level, new_level, event_type="USERUPGRADE"):
        who = nickname or username or ""
        if old_level is None:
            label = f"→ Lv.{int(new_level)}"
        else:
            label = f"Lv.{int(old_level)} → Lv.{int(new_level)}"
        self.write("levelups", f"[{fmt_real(real_ts)[:8]}] [{fmt_elapsed(live_sec)}] {who} | {label} | {event_type}\n")

    def profile_activity(self, real_ts, kind, username, nickname, value=""):
        self.write("profiles", f"[{fmt_real(real_ts)[:8]}] | {kind} | {username or ''} | {nickname or ''} | {value}\n")

    def analytics(self, real_ts, stats):
        if not self._stat_line_due("analytics"):
            return
        self.write("analytics", f"[{fmt_real(real_ts)[:8]}] | {stats.get('comments',0)} | {stats.get('joins',0)} | {stats.get('gifts',0)} | {stats.get('gift_diamonds',0)} | {stats.get('likes',0)} | {stats.get('shares',0)} | {stats.get('follows',0)} | {stats.get('viewers',0)} | {stats.get('total_viewers',0)} | {stats.get('peak_viewers',0)}\n")

    def dashboard(self, real_ts, stats):
        if not self._stat_line_due("dashboard"):
            return
        self.write("dashboard", f"[{fmt_real(real_ts)[:8]}] LIVE | 留言 {stats.get('comments',0)} | Join {stats.get('joins',0)} | Gifts {stats.get('gifts',0)} | Diamonds {stats.get('gift_diamonds',0)} | Likes {stats.get('likes',0)} | Shares {stats.get('shares',0)} | Follows {stats.get('follows',0)} | 觀眾 {stats.get('viewers',0)} | 累積觀眾 {stats.get('total_viewers',0)} | 累積Join {stats.get('joins',0)} | 觀測使用者 {stats.get('unique_observed',0)} | 峰值 {stats.get('peak_viewers',0)}\n")

    def viewer_sample(self, real_ts, live_sec, viewers, bucket):
        self.write("viewers", f"[{fmt_real(real_ts)[:8]}] [{fmt_elapsed(live_sec)}] viewers={int(viewers):,} | K={bucket}\n")
        self.analytics(real_ts, self._stats_for_log if hasattr(self, "_stats_for_log") else {"viewers":viewers,"peak_viewers":viewers})

    def session_end(self, real_ts, status):
        self.write("sessions", f"結束: {now_iso(real_ts)}\n狀態: {status}\n")
        self.write("dashboard", f"[{fmt_real(real_ts)[:8]}] SESSION {status}\n")

    def close(self):
        with self._lock:
            for f in list(self.files.values()):
                try:
                    f.flush(); os.fsync(f.fileno())
                except OSError:
                    pass
                try:
                    f.close()
                except Exception:
                    pass
            self.files.clear()


class Database:
    """Single-thread-owned SQLite connection. GUI never shares this connection."""

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA synchronous=NORMAL")
        self.conn.execute("PRAGMA busy_timeout=10000")
        # TK_V0.8.34.025 🧪 db_quick（實驗工作區開了才有 _DB_SSD\\db_quick.on，要重新啟動才生效）：
        # 留言／進場／禮物／按讚這些事件寫入時，資料庫被別的工作鎖住最多只等 1.5 秒（原本 10 秒，會卡住整個直播間的連線迴圈），
        # 等不到就先放在記憶體，下一次寫入時補寫（INSERT OR IGNORE，不會重複）；最多暫存 20000 筆。
        self._quick = False; self._retry = []; self._retry_t = 0.0
        try: self._quick = (Path(PACKAGE_ROOT) / "_DB_SSD" / "db_quick.on").exists()
        except Exception: self._quick = False
        with SCHEMA_INIT_LOCK:
            self.init_schema()

    def init_schema(self):
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS sessions(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              username TEXT NOT NULL, streamer_name TEXT DEFAULT '', room_id TEXT, started_at TEXT, ended_at TEXT,
              live_start_epoch REAL, time_source TEXT, status TEXT DEFAULT 'RUNNING',
              last_viewers INTEGER DEFAULT 0, last_total_viewers INTEGER DEFAULT 0, peak_viewers INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS comments(
              id INTEGER PRIMARY KEY AUTOINCREMENT, session_id INTEGER NOT NULL,
              event_id TEXT, ts REAL, live_sec REAL, username TEXT, nickname TEXT, comment TEXT,
              UNIQUE(session_id,event_id)
            );
            CREATE INDEX IF NOT EXISTS idx_comments_session_ts ON comments(session_id, ts);
            CREATE TABLE IF NOT EXISTS joins(
              id INTEGER PRIMARY KEY AUTOINCREMENT, session_id INTEGER NOT NULL,
              event_id TEXT, ts REAL, live_sec REAL, username TEXT, nickname TEXT,
              UNIQUE(session_id,event_id)
            );
            CREATE INDEX IF NOT EXISTS idx_joins_session_ts ON joins(session_id, ts);
            CREATE TABLE IF NOT EXISTS gifts(
              id INTEGER PRIMARY KEY AUTOINCREMENT, session_id INTEGER NOT NULL,
              event_id TEXT, ts REAL, live_sec REAL, username TEXT, nickname TEXT,
              gift_id TEXT, gift_name TEXT, count INTEGER, diamond_each INTEGER,
              diamonds INTEGER, streak_final INTEGER DEFAULT 1,
              UNIQUE(session_id,event_id)
            );
            CREATE INDEX IF NOT EXISTS idx_gifts_session_ts ON gifts(session_id, ts);
            CREATE TABLE IF NOT EXISTS likes(
              id INTEGER PRIMARY KEY AUTOINCREMENT, session_id INTEGER, event_id TEXT,
              ts REAL, live_sec REAL, username TEXT, nickname TEXT, count INTEGER, room_total INTEGER
            );
            CREATE INDEX IF NOT EXISTS idx_likes_session_ts ON likes(session_id, ts);
            CREATE TABLE IF NOT EXISTS follows(
              id INTEGER PRIMARY KEY AUTOINCREMENT, session_id INTEGER, event_id TEXT,
              ts REAL, live_sec REAL, username TEXT, nickname TEXT
            );
            CREATE TABLE IF NOT EXISTS shares(
              id INTEGER PRIMARY KEY AUTOINCREMENT, session_id INTEGER, event_id TEXT,
              ts REAL, live_sec REAL, username TEXT, nickname TEXT
            );
            CREATE TABLE IF NOT EXISTS songs(
              id INTEGER PRIMARY KEY AUTOINCREMENT, session_id INTEGER NOT NULL,
              event_id TEXT, ts REAL, live_sec REAL, username TEXT, nickname TEXT, song TEXT, raw_comment TEXT,
              UNIQUE(session_id,event_id)
            );
            CREATE INDEX IF NOT EXISTS idx_songs_session_ts ON songs(session_id, ts);
            CREATE TABLE IF NOT EXISTS level_ups(
              id INTEGER PRIMARY KEY AUTOINCREMENT, session_id INTEGER NOT NULL,
              event_id TEXT, ts REAL, live_sec REAL, username TEXT, nickname TEXT,
              old_level INTEGER, new_level INTEGER, privilege_key TEXT, action TEXT, event_type TEXT, raw_summary TEXT,
              UNIQUE(session_id,event_id)
            );
            CREATE INDEX IF NOT EXISTS idx_levelups_session_ts ON level_ups(session_id, ts);
            CREATE TABLE IF NOT EXISTS viewer_samples(
              id INTEGER PRIMARY KEY AUTOINCREMENT, session_id INTEGER, ts REAL, live_sec REAL, viewers INTEGER, total_viewers INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS user_profiles(
              username TEXT PRIMARY KEY, nickname TEXT, first_seen TEXT, last_seen TEXT,
              sessions INTEGER DEFAULT 0, comments INTEGER DEFAULT 0, joins INTEGER DEFAULT 0,
              gifts INTEGER DEFAULT 0, diamonds INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS user_sessions(
              username TEXT, session_id INTEGER, first_seen TEXT, last_seen TEXT,
              PRIMARY KEY(username,session_id)
            );
            CREATE TABLE IF NOT EXISTS gifter_gifts(
              username TEXT, gift_id TEXT, gift_name TEXT, count INTEGER DEFAULT 0,
              diamonds INTEGER DEFAULT 0, last_seen TEXT,
              PRIMARY KEY(username,gift_id,gift_name)
            );
            CREATE INDEX IF NOT EXISTS idx_likes_session_event ON likes(session_id, event_id);
            CREATE INDEX IF NOT EXISTS idx_viewer_samples_session_ts ON viewer_samples(session_id, ts);
            CREATE INDEX IF NOT EXISTS idx_follows_session ON follows(session_id);
            CREATE INDEX IF NOT EXISTS idx_shares_session ON shares(session_id);
            CREATE INDEX IF NOT EXISTS idx_comments_user_ts ON comments(username, ts);
            CREATE INDEX IF NOT EXISTS idx_gifts_user_ts ON gifts(username, ts);
            CREATE INDEX IF NOT EXISTS idx_joins_user_ts ON joins(username, ts);
            CREATE INDEX IF NOT EXISTS idx_likes_user_ts ON likes(username, ts);
            CREATE INDEX IF NOT EXISTS idx_follows_user_ts ON follows(username, ts);
            CREATE INDEX IF NOT EXISTS idx_shares_user_ts ON shares(username, ts);
            CREATE TABLE IF NOT EXISTS gift_catalog(
              gift_id TEXT PRIMARY KEY, gift_name TEXT, diamond_each INTEGER,
              first_seen TEXT, last_seen TEXT
            );
            """
        )
        # Lightweight migration for databases made by V0.2.x.
        for sql in (
            "ALTER TABLE likes ADD COLUMN live_sec REAL",
            "ALTER TABLE likes ADD COLUMN room_total INTEGER",
            "ALTER TABLE follows ADD COLUMN live_sec REAL",
            "ALTER TABLE shares ADD COLUMN live_sec REAL",
            "ALTER TABLE viewer_samples ADD COLUMN live_sec REAL",
            "ALTER TABLE viewer_samples ADD COLUMN total_viewers INTEGER DEFAULT 0",
            "ALTER TABLE sessions ADD COLUMN streamer_name TEXT DEFAULT ''",
            "ALTER TABLE sessions ADD COLUMN last_viewers INTEGER DEFAULT 0",
            "ALTER TABLE sessions ADD COLUMN last_total_viewers INTEGER DEFAULT 0",
            "ALTER TABLE sessions ADD COLUMN peak_viewers INTEGER DEFAULT 0",
        ):
            try:
                self.conn.execute(sql)
            except sqlite3.OperationalError:
                pass
        self.conn.commit()

    def session_start(self, username, room_id, live_start, time_source, streamer_name=''):
        """TK_V0.9.79 場次編號一律自己算（< SID_CAP）：手機錄屏匯入的場次用 SID_CAP 以上的編號，直播場次照舊 1、2、3… 往上，不會被拉到 900 萬."""
        last = None
        for k in range(12):
            try:
                cur = self.conn.execute(
                    "INSERT INTO sessions(id,username,streamer_name,room_id,started_at,live_start_epoch,time_source,status) "
                    "VALUES((SELECT COALESCE(MAX(id),0)+1 FROM sessions WHERE id<?),?,?,?,?,?,?,?)",
                    (SID_CAP, username, streamer_name or username, room_id, now_iso(), live_start, time_source, "LIVE"),
                )
                self.conn.commit()
                return cur.lastrowid
            except (sqlite3.IntegrityError, sqlite3.OperationalError) as ex:   # 兩個主播同時開播搶到同一個編號／資料庫忙：等一下再算一次
                last = ex
                try: self.conn.rollback()
                except Exception: pass
                time.sleep(0.05 * (k + 1))
        raise last

    def update_session_viewers(self, sid, viewers, total_viewers, peak_viewers):
        if sid:
            self.conn.execute(
                "UPDATE sessions SET last_viewers=?,last_total_viewers=?,peak_viewers=? WHERE id=?",
                (int(viewers or 0), int(total_viewers or 0), int(peak_viewers or 0), sid),
            )
            self.conn.commit()

    def session_end(self, sid, status="ENDED"):
        self._ev_drain()
        if sid:
            self.conn.execute("UPDATE sessions SET ended_at=?,status=? WHERE id=?", (now_iso(), status, sid))
            self.conn.commit()

    # V0.4.63: a dropped room is held open for RESUME_GRACE_SECONDS. ended_at is stamped at the
    # moment of the drop, so a session that never comes back still ends at the real time.
    def session_pause(self, sid, ts=None):
        self._ev_drain()
        if sid:
            self.conn.execute("UPDATE sessions SET ended_at=?,status='RECONNECTING' WHERE id=?", (now_iso(ts), sid))
            self.conn.commit()

    def session_resume(self, sid):
        if sid:
            self.conn.execute("UPDATE sessions SET ended_at=NULL,status='LIVE' WHERE id=?", (sid,))
            self.conn.commit()

    def session_finalize(self, sid, status):
        self._ev_drain()
        if sid:
            self.conn.execute("UPDATE sessions SET status=? WHERE id=?", (status, sid))
            self.conn.commit()

    def close_orphan_reconnecting(self):
        """Sessions left in RECONNECTING by a crash / forced exit become DISCONNECTED."""
        try:
            self.conn.execute("UPDATE sessions SET status='DISCONNECTED' WHERE status='RECONNECTING'")
            self.conn.commit()
        except Exception:
            pass

    def _ev(self, name, *a):
        """TK_V0.8.34.025 db_quick：事件寫入（只在實驗開著時才走這裡）.
        TK_V0.8.34.026 剛遇到鎖住的 2 秒內直接先放記憶體（不再每筆都等 1.5 秒）；有事件編號的回 False（真的寫進去時才算新的，不會重複計算）."""
        fn = getattr(self, "_ev_" + name); now = time.time()
        if now < getattr(self, "_busy_until", 0.0):
            return self._ev_buffer(name, a)
        if self._retry and now - self._retry_t > 2.0: self._ev_flush()
        if time.time() < getattr(self, "_busy_until", 0.0):
            return self._ev_buffer(name, a)
        try:
            self.conn.execute("PRAGMA busy_timeout=1500")
            return fn(*a)
        except sqlite3.OperationalError as ex:
            if "locked" not in str(ex) and "busy" not in str(ex): raise
            try: self.conn.rollback()
            except Exception: pass
            self._busy_until = time.time() + 2.0
            return self._ev_buffer(name, a)
        finally:
            try: self.conn.execute("PRAGMA busy_timeout=10000")
            except Exception: pass

    def _ev_buffer(self, name, a):
        if len(self._retry) < 20000: self._retry.append((name, a))
        elif not getattr(self, "_cap_warned", False):
            self._cap_warned = True
            try: print("[TikLive] db_quick：暫存已滿 20000 筆，之後的事件先不記", file=sys.stderr)
            except Exception: pass
        self._retry_t = time.time()
        if name in ("comment", "join", "gift", "like") and len(a) > 1 and a[1]: return False   # 有事件編號：等真的寫進去才算新的
        return True

    def _ev_flush(self):
        self._retry_t = time.time(); todo, self._retry = self._retry[:300], self._retry[300:]
        for k, (name, a) in enumerate(todo):
            try:
                self.conn.execute("PRAGMA busy_timeout=1500"); getattr(self, "_ev_" + name)(*a)
            except sqlite3.OperationalError as ex:
                try: self.conn.rollback()
                except Exception: pass
                if "locked" in str(ex) or "busy" in str(ex):
                    self._retry = todo[k:] + self._retry; self._busy_until = time.time() + 2.0; break
                try: print(f"[TikLive] db_quick：補寫失敗、丟掉一筆（{ex}）", file=sys.stderr)
                except Exception: pass
            except Exception:
                try: self.conn.rollback()
                except Exception: pass
        try: self.conn.execute("PRAGMA busy_timeout=10000")
        except Exception: pass

    def _ev_drain(self, tries=5):
        """TK_V0.8.34.026 場次結束／暫停／關閉前把暫存的補寫完（用正常的等待時間）."""
        if not getattr(self, "_retry", None): return
        for _i in range(tries):
            if not self._retry: break
            self._busy_until = 0.0; n0 = len(self._retry); self._ev_flush()
            if len(self._retry) >= n0: time.sleep(0.5)

    def _touch_user(self, session_id, ui, field=None, count=0, diamonds=0, ts=None):
        u = ui.get("unique_id") or ui.get("nickname") or ui.get("id")
        if not u or not session_id:
            return
        stamp = now_iso(ts)
        row = self.conn.execute(
            "SELECT 1 FROM user_sessions WHERE username=? AND session_id=?", (u, session_id)
        ).fetchone()
        if not row:
            self.conn.execute(
                "INSERT INTO user_sessions(username,session_id,first_seen,last_seen) VALUES(?,?,?,?)",
                (u, session_id, stamp, stamp),
            )
            self.conn.execute(
                """INSERT INTO user_profiles(username,nickname,first_seen,last_seen,sessions)
                   VALUES(?,?,?,?,1)
                   ON CONFLICT(username) DO UPDATE SET nickname=excluded.nickname,last_seen=excluded.last_seen,sessions=sessions+1""",
                (u, ui.get("nickname", ""), stamp, stamp),
            )
        else:
            self.conn.execute("UPDATE user_sessions SET last_seen=MAX(COALESCE(last_seen,''),?) WHERE username=? AND session_id=?", (stamp, u, session_id))
            # TK_V0.8.34.032 暱稱、最後出現、次數、鑽石合成一句（以前 2～3 句；每筆事件佔住寫入鎖的時間變短）
            sets = ["nickname=?", "last_seen=MAX(COALESCE(last_seen,''),?)"]; args = [ui.get("nickname", ""), stamp]
            if field: sets.append(f"{field}={field}+?"); args.append(count)
            if diamonds: sets.append("diamonds=diamonds+?"); args.append(diamonds)
            self.conn.execute("UPDATE user_profiles SET " + ",".join(sets) + " WHERE username=?", (*args, u))
            return
        if field or diamonds:
            sets = []; args = []
            if field: sets.append(f"{field}={field}+?"); args.append(count)
            if diamonds: sets.append("diamonds=diamonds+?"); args.append(diamonds)
            self.conn.execute("UPDATE user_profiles SET " + ",".join(sets) + " WHERE username=?", (*args, u))

    def comment(self, sid, eid, ts, live, ui, text):
        if self._quick: return self._ev("comment", sid, eid, ts, live, ui, text)
        return self._ev_comment(sid, eid, ts, live, ui, text)

    def _ev_comment(self, sid, eid, ts, live, ui, text):
        cur = self.conn.execute(
            "INSERT OR IGNORE INTO comments(session_id,event_id,ts,live_sec,username,nickname,comment) VALUES(?,?,?,?,?,?,?)",
            (sid, eid, ts, live, ui["unique_id"], ui["nickname"], text),
        )
        if cur.rowcount:
            self._touch_user(sid, ui, "comments", 1, ts=ts)
        self.conn.commit()
        return bool(cur.rowcount)

    def join(self, sid, eid, ts, live, ui):
        if self._quick: return self._ev("join", sid, eid, ts, live, ui)
        return self._ev_join(sid, eid, ts, live, ui)

    def _ev_join(self, sid, eid, ts, live, ui):
        cur = self.conn.execute(
            "INSERT OR IGNORE INTO joins(session_id,event_id,ts,live_sec,username,nickname) VALUES(?,?,?,?,?,?)",
            (sid, eid, ts, live, ui["unique_id"], ui["nickname"]),
        )
        if cur.rowcount:
            self._touch_user(sid, ui, "joins", 1, ts=ts)
        self.conn.commit()
        return bool(cur.rowcount)

    def gift(self, sid, eid, ts, live, ui, gift_id, name, count, diamond_each, diamonds):
        if self._quick: return self._ev("gift", sid, eid, ts, live, ui, gift_id, name, count, diamond_each, diamonds)
        return self._ev_gift(sid, eid, ts, live, ui, gift_id, name, count, diamond_each, diamonds)

    def _ev_gift(self, sid, eid, ts, live, ui, gift_id, name, count, diamond_each, diamonds):
        cur = self.conn.execute(
            """INSERT OR IGNORE INTO gifts(session_id,event_id,ts,live_sec,username,nickname,gift_id,gift_name,count,diamond_each,diamonds,streak_final)
               VALUES(?,?,?,?,?,?,?,?,?,?,?,1)""",
            (sid, eid, ts, live, ui["unique_id"], ui["nickname"], str(gift_id), name, count, diamond_each, diamonds),
        )
        if not cur.rowcount:
            self.conn.commit()
            return False
        u = ui["unique_id"] or ui["nickname"]
        self._touch_user(sid, ui, "gifts", count, diamonds, ts)
        stamp = now_iso(ts)
        self.conn.execute(
            """INSERT INTO gifter_gifts(username,gift_id,gift_name,count,diamonds,last_seen) VALUES(?,?,?,?,?,?)
               ON CONFLICT(username,gift_id,gift_name) DO UPDATE SET count=count+excluded.count,diamonds=diamonds+excluded.diamonds,last_seen=excluded.last_seen""",
            (u, str(gift_id), name, count, diamonds, stamp),
        )
        self.conn.execute(
            """INSERT INTO gift_catalog(gift_id,gift_name,diamond_each,first_seen,last_seen) VALUES(?,?,?,?,?)
               ON CONFLICT(gift_id) DO UPDATE SET gift_name=excluded.gift_name,
               diamond_each=CASE WHEN excluded.diamond_each>0 THEN excluded.diamond_each ELSE gift_catalog.diamond_each END,
               last_seen=excluded.last_seen""",
            (str(gift_id), name, diamond_each, stamp, stamp),
        )
        self.conn.commit()
        return True

    def song(self, sid, eid, ts, live, ui, song, raw_comment=""):
        cur = self.conn.execute(
            "INSERT OR IGNORE INTO songs(session_id,event_id,ts,live_sec,username,nickname,song,raw_comment) VALUES(?,?,?,?,?,?,?,?)",
            (sid, eid, ts, live, ui["unique_id"], ui["nickname"], song, raw_comment),
        )
        self.conn.commit()
        return bool(cur.rowcount)

    def level_up(self, sid, eid, ts, live, ui, old_level, new_level, privilege_key="", action="", event_type="USERUPGRADE", raw_summary=""):
        cur = self.conn.execute(
            "INSERT OR IGNORE INTO level_ups(session_id,event_id,ts,live_sec,username,nickname,old_level,new_level,privilege_key,action,event_type,raw_summary) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
            (sid, eid, ts, live, ui["unique_id"], ui["nickname"], old_level, new_level, privilege_key, action, event_type, raw_summary),
        )
        self.conn.commit()
        return bool(cur.rowcount)

    def like(self, sid, eid, ts, live, ui, count, room_total):
        if self._quick: return self._ev("like", sid, eid, ts, live, ui, count, room_total)
        return self._ev_like(sid, eid, ts, live, ui, count, room_total)

    def _ev_like(self, sid, eid, ts, live, ui, count, room_total):
        if eid:
            exists=self.conn.execute("SELECT 1 FROM likes WHERE session_id=? AND event_id=? LIMIT 1", (sid,eid)).fetchone()
            if exists:
                return False
        self.conn.execute(
            "INSERT INTO likes(session_id,event_id,ts,live_sec,username,nickname,count,room_total) VALUES(?,?,?,?,?,?,?,?)",
            (sid, eid, ts, live, ui["unique_id"], ui["nickname"], count, room_total),
        )
        self._touch_user(sid, ui, None, ts=ts)
        self.conn.commit()
        return True

    def social(self, table, sid, eid, ts, live, ui):
        if self._quick: return self._ev("social", table, sid, eid, ts, live, ui)
        return self._ev_social(table, sid, eid, ts, live, ui)

    def _ev_social(self, table, sid, eid, ts, live, ui):
        self.conn.execute(
            f"INSERT INTO {table}(session_id,event_id,ts,live_sec,username,nickname) VALUES(?,?,?,?,?,?)",
            (sid, eid, ts, live, ui["unique_id"], ui["nickname"]),
        )
        self._touch_user(sid, ui, None, ts=ts)
        self.conn.commit()

    def viewer(self, sid, ts, live, viewers, total_viewers=0):
        if self._quick: return self._ev("viewer", sid, ts, live, viewers, total_viewers)
        return self._ev_viewer(sid, ts, live, viewers, total_viewers)

    def _ev_viewer(self, sid, ts, live, viewers, total_viewers=0):
        self.conn.execute("INSERT INTO viewer_samples(session_id,ts,live_sec,viewers,total_viewers) VALUES(?,?,?,?,?)", (sid, ts, live, viewers, total_viewers))
        self.conn.commit()

    def export_session(self, sid):
        if not sid:
            return None
        row = self.conn.execute("SELECT username,room_id,started_at,ended_at FROM sessions WHERE id=?", (sid,)).fetchone()
        if not row:
            return None
        username, room_id, started_at, ended_at = row
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base = EXPORT_DIR / f"{username}_session{sid}_{stamp}"
        comments = self.conn.execute("SELECT ts,live_sec,username,nickname,comment FROM comments WHERE session_id=? ORDER BY ts", (sid,)).fetchall()
        gifts = self.conn.execute("SELECT ts,live_sec,username,nickname,gift_name,count,diamond_each,diamonds FROM gifts WHERE session_id=? ORDER BY ts", (sid,)).fetchall()
        joins = self.conn.execute("SELECT ts,live_sec,username,nickname FROM joins WHERE session_id=? ORDER BY ts", (sid,)).fetchall()
        likes = self.conn.execute("SELECT ts,live_sec,username,nickname,count,room_total FROM likes WHERE session_id=? ORDER BY ts", (sid,)).fetchall()
        songs = self.conn.execute("SELECT ts,live_sec,username,nickname,song,raw_comment FROM songs WHERE session_id=? ORDER BY ts", (sid,)).fetchall()
        levelups = self.conn.execute("SELECT ts,live_sec,username,nickname,old_level,new_level,event_type FROM level_ups WHERE session_id=? ORDER BY ts", (sid,)).fetchall()
        txt = base.with_suffix(".txt")
        with txt.open("w", encoding="utf-8-sig") as f:
            f.write(f"TikLive Monitor V{APP_VERSION}\n主播: @{username}\nRoom ID: {room_id}\n開始: {started_at}\n結束: {ended_at or ''}\n\n")
            f.write("=== CHAT ===\n")
            for ts, live, u, n, c in comments:
                f.write(f"[{now_iso(ts)}] [{fmt_elapsed(live)}] {n or u}: {c}\n")
            f.write("\n=== GIFTS ===\n")
            for ts, live, u, n, g, c, de, ds in gifts:
                f.write(f"[{now_iso(ts)}] [{fmt_elapsed(live)}] {n or u} -> {g} x{c} | {de} diamonds/件 | {ds} diamonds\n")
            f.write("\n=== JOINS ===\n")
            for ts, live, u, n in joins:
                f.write(f"[{now_iso(ts)}] [{fmt_elapsed(live)}] {n or u}\n")
            f.write("\n=== LIKES ===\n")
            for ts, live, u, n, c, total in likes:
                f.write(f"[{now_iso(ts)}] [{fmt_elapsed(live)}] {n or u} +{c} | room total {total if total is not None else '-'}\n")
            f.write("\n=== SONG REQUESTS ===\n")
            for ts, live, u, n, song, raw in songs:
                f.write(f"[{now_iso(ts)}] [{fmt_elapsed(live)}] {n or u} | {song} | {raw}\n")
            f.write("\n=== LEVEL UP ===\n")
            for ts, live, u, n, old, new, et in levelups:
                label = f"Lv.{old} -> Lv.{new}" if old is not None else f"Lv.{new}"
                f.write(f"[{now_iso(ts)}] [{fmt_elapsed(live)}] {n or u} | {label} | {et}\n")
        srt = base.with_suffix(".srt")
        with srt.open("w", encoding="utf-8-sig") as f:
            for i, (ts, live, u, n, c) in enumerate(comments, 1):
                start = float(live or 0); end = start + 3
                f.write(f"{i}\n{fmt_ms(start)} --> {fmt_ms(end)}\n{n or u}: {c}\n\n")
        for name, headers, rows in [
            ("gifts.csv", ["real_ts", "live_sec", "username", "nickname", "gift_name", "count", "diamond_each", "diamonds"], gifts),
            ("joins.csv", ["real_ts", "live_sec", "username", "nickname"], joins),
            ("likes.csv", ["real_ts", "live_sec", "username", "nickname", "count", "room_total"], likes),
            ("songs.csv", ["real_ts", "live_sec", "username", "nickname", "song", "raw_comment"], songs),
            ("levelups.csv", ["real_ts", "live_sec", "username", "nickname", "old_level", "new_level", "event_type"], levelups),
        ]:
            p = base.parent / (base.name + "_" + name)
            with p.open("w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f); writer.writerow(headers); writer.writerows(rows)
        return txt.parent

    def session_rows(self, limit=500):
        return self.conn.execute("SELECT id,username,room_id,started_at,ended_at,time_source,status FROM sessions ORDER BY id DESC LIMIT ?", (limit,)).fetchall()

    def close(self):
        try:
            self._ev_drain(tries=30)
            self.conn.commit()
            try:
                self.conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            except Exception:
                pass
        finally:
            self.conn.close()




class DiagnosticWorker:
    """Independent connection diagnostics with up to 3 attempts per streamer."""
    def __init__(self, usernames, timeout=20, attempts=3, retry_delay=5):
        self.usernames=[str(x).lstrip('@').strip() for x in usernames if str(x).strip()]
        self.timeout=int(timeout); self.attempts=max(1,int(attempts)); self.retry_delay=max(0,int(retry_delay))
        self.events=queue.Queue(); self.stop_flag=threading.Event(); self.worker=None
    def emit(self,text): self.events.put(str(text))
    def poll(self,limit=200):
        out=[]
        for _ in range(limit):
            try: out.append(self.events.get_nowait())
            except queue.Empty: break
        return out
    def start(self):
        if self.worker and self.worker.is_alive(): return
        self.stop_flag.clear(); self.worker=threading.Thread(target=self._thread_main,name='TikLiveDiagnostic',daemon=True); self.worker.start()
    def stop(self): self.stop_flag.set()
    def is_alive(self): return bool(self.worker and self.worker.is_alive())
    @staticmethod
    def classify(exc):
        s=str(exc).lower()
        if any(x in s for x in ('not found','user not found','invalid unique','invalid username','does not exist','could not find')): return 'D-ID-404','可能是主播 ID 已變更、帳號不存在或 ID 無效'
        if any(x in s for x in ('sign','signature','sig server')): return 'D-SIGN','Sign／簽名服務異常'
        if '429' in s or 'rate limit' in s or 'too many' in s: return 'D-RATE','HTTP 429／請求頻率受限'
        if '403' in s or 'forbidden' in s: return 'D-403','HTTP 403／伺服器拒絕請求'
        if '400' in s or 'bad request' in s: return 'D-400','HTTP 400／請求或 WebSocket 連線被拒絕'
        if any(x in s for x in ('websocket','connection','timeout','timed out','network','dns','ssl')): return 'D-NET','網路／WebSocket／DNS／SSL／逾時問題'
        return 'D-UNKNOWN','未分類例外，請看 RAW 原始錯誤'
    async def _one(self,username,attempt):
        from TikTokLive import TikTokLiveClient
        from TikTokLive.events import ConnectEvent,DisconnectEvent
        self.emit(f'[{username}] [A{attempt}/3] [D001] 建立 TikTokLiveClient')
        client=TikTokLiveClient(unique_id=username); connected=asyncio.Event(); task=None; success=False
        @client.on(ConnectEvent)
        async def on_connect(event):
            self.emit(f'[{username}] [A{attempt}/3] [D104] ConnectEvent 收到 · Room ID={getattr(client,"room_id","") or "-"}')
            connected.set()
        @client.on(DisconnectEvent)
        async def on_disconnect(event): self.emit(f'[{username}] [A{attempt}/3] [D109] DisconnectEvent 收到')
        try:
            self.emit(f'[{username}] [A{attempt}/3] [D002] start(fetch_room_info=True, fetch_live_check=True)')
            try: task=await client.start(fetch_room_info=True,fetch_gift_info=False,fetch_live_check=True)
            except TypeError: task=await client.start()
            try:
                await asyncio.wait_for(connected.wait(),timeout=self.timeout)
            except asyncio.TimeoutError:
                self.emit(f'[{username}] [A{attempt}/3] [D105] {self.timeout} 秒內沒有 ConnectEvent → 初始連線／直播狀態判斷未完成')
                return False
            self.emit(f'[{username}] [A{attempt}/3] [D108] 初始連線成功 · 可建立正式監控'); success=True; return True
        except Exception as e:
            code,msg=self.classify(e); self.emit(f'[{username}] [A{attempt}/3] [{code}] {msg}'); self.emit(f'[{username}] [A{attempt}/3] [RAW] {type(e).__name__}: {e}'); return False
        finally:
            try: await client.disconnect()
            except Exception: pass
            if task and not task.done(): task.cancel()
            self.emit(f'[{username}] [A{attempt}/3] [D110] 診斷連線結束'+(' · SUCCESS' if success else ' · FAILED'))
    async def _run(self):
        try:
            import TikTokLive
            self.emit(f'[SYSTEM] TikTokLive={getattr(TikTokLive,"__version__","unknown")} · 每位最多 {self.attempts} 次 · 失敗間隔 {self.retry_delay} 秒')
        except Exception as e: self.emit(f'[SYSTEM] [D-PKG] TikTokLive 載入失敗: {e}'); return
        for u in self.usernames:
            if self.stop_flag.is_set(): break
            self.emit(f'--- {u} ---')
            success=False
            for attempt in range(1,self.attempts+1):
                if self.stop_flag.is_set(): break
                success=await self._one(u,attempt)
                if success: break
                if attempt < self.attempts and not self.stop_flag.is_set():
                    self.emit(f'[{u}] [A{attempt}/3] 失敗，5 秒後進行第 {attempt+1} 次診斷…')
                    try: await asyncio.wait_for(asyncio.sleep(self.retry_delay), timeout=self.retry_delay+1)
                    except asyncio.CancelledError: break
            self.emit(f'[{u}] RESULT: '+('PASS · 至少一次連線成功' if success else 'FAIL · 3 次皆未成功'))
    def _thread_main(self):
        try: asyncio.run(self._run())
        except Exception as e: self.emit(f'[SYSTEM] [D-FATAL] {type(e).__name__}: {e}')


def extract_stream_pull_url(room_info):
    """Best-effort public pull URL extraction used only by V0.4.50 experiment."""
    try:
        raw=nested(room_info,'stream_url','live_core_sdk_data','pull_data','stream_data',default=None)
        if not raw: raw=nested(room_info,'live_core_sdk_data','pull_data','stream_data',default=None)
        data=json.loads(raw) if isinstance(raw,str) else raw
        if not isinstance(data,dict): return ''
        def walk(x):
            if isinstance(x,dict):
                for k in ('hls','hls_url','m3u8','mp4','flv','url'):
                    v=x.get(k)
                    if isinstance(v,str) and v.startswith(('http://','https://')): return v
                for v in x.values():
                    r=walk(v)
                    if r: return r
            elif isinstance(x,list):
                for v in x:
                    r=walk(v)
                    if r: return r
            return ''
        return walk(data)
    except Exception:
        return ''

# ---------------------------------------------------------------- V0.4.69 league probe
# TikTok LIVE League (A1..D5) + percentile: the field is not documented, so first record
# every rank/league-looking value the room exposes, then read it from LOG/_league_probe.
LEAGUE_PROBE_DIR = LOG_DIR / "_league_probe"
_LEAGUE_KEY_RE = None


def _league_hits(obj, path="", out=None, depth=0):
    import re as _re
    global _LEAGUE_KEY_RE
    if _LEAGUE_KEY_RE is None:
        _LEAGUE_KEY_RE = _re.compile(r"league|rank|grade|tier|division|percent|class_level|anchor_level", _re.I)
    if out is None: out = []
    if depth > 12 or len(out) > 400: return out
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{path}.{k}" if path else str(k)
            if _LEAGUE_KEY_RE.search(str(k)):
                try: txt = json.dumps(v, ensure_ascii=False, default=str)
                except Exception: txt = repr(v)
                out.append({"path": p, "value": txt[:1500]})
            if isinstance(v, (dict, list)): _league_hits(v, p, out, depth + 1)
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:50]):
            _league_hits(v, f"{path}[{i}]", out, depth + 1)
    return out


def _event_to_obj(event):
    for m in ("to_dict", "to_pydict"):
        fn = getattr(event, m, None)
        if callable(fn):
            try: return fn()
            except Exception: pass
    try: return {k: v for k, v in vars(event).items() if not k.startswith("_")}
    except Exception: return {"repr": repr(event)[:3000]}


def write_league_probe(username, kind, payload):
    try:
        LEAGUE_PROBE_DIR.mkdir(parents=True, exist_ok=True)
        safe = "".join(c for c in username if c.isalnum() or c in "._-") or "unknown"
        with (LEAGUE_PROBE_DIR / f"{safe}.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": now_iso(), "kind": kind, "data": payload}, ensure_ascii=False, default=str)[:20000] + "\n")
    except Exception:
        pass


CONNECT_EVENT_TIMEOUT = 20.0   # V0.4.78: tunable from 設定 (the GUI writes these module globals)
VIEWER_SAMPLE_SECONDS = 5
DEDUP_SECONDS = 60
LEAGUE_PROBE_ENABLED = True
RESUME_GRACE_SECONDS = 600      # V0.4.63: reconnect within 10 min -> same session continues
GRACE_RETRY_SECONDS = 15        # retry cadence while a dropped room is waiting to come back
_ORPHANS_CLOSED = False


class LiveEngine:
    """TikTok connection worker. Network + persistence stay off the Qt GUI thread."""

    def __init__(self, username: str, retry_seconds=60, initial_delay=0, display_name=''):
        self.username = username.lstrip("@").strip()
        self.display_name = str(display_name or self.username)
        self.retry_seconds=max(1,int(retry_seconds))
        self.initial_delay=max(0.0,float(initial_delay))
        self.priority_mode=False
        self._priority_failures=0
        self.events: queue.Queue[MonitorEvent] = queue.Queue()
        self.stop_flag = threading.Event()
        self.worker: Optional[threading.Thread] = None
        self.loop = None
        self.client = None
        self.db: Optional[Database] = None
        self.session_id = None
        self.live_start = None
        self.time_source = "WAITING"
        self.connection_wall = None
        self.join_counts = Counter()
        self.stats = {"comments":0,"preconnect":0,"joins":0,"gifts":0,"gift_diamonds":0,"likes":0,"shares":0,"follows":0,"viewers":0,"total_viewers":0,"peak_viewers":0,"gift_types":0,"like_room_total":None,"unique_observed":0}
        self._ended_sent = False
        self._seen_ids = {"comment":{}, "join":{}, "gift":{}}
        self._seen_lock = threading.Lock()
        self.log: Optional[LiveLogWriter] = None
        self.observed_users = set()
        self.user_levels = {}
        self.levelup_keys = set()
        self.viewer_sampler_task = None
        self.cache_pause_requested = False
        self.cache_pause_event = threading.Event()
        self.cache_resume_reconnect = False
        self.cache_paused = False
        self._grace = None              # held session while the room is dropped (see _enter_grace)
        self.room_id = ""

    def _observe_user(self, ui):
        key = ui.get("unique_id") or ui.get("id") or ui.get("nickname")
        if key and key not in self.observed_users:
            self.observed_users.add(key)
            self.stats["unique_observed"] = len(self.observed_users)

    def set_retry_seconds(self, seconds):
        self.retry_seconds=max(1,int(seconds))

    def set_priority_mode(self, enabled):
        self.priority_mode=bool(enabled)
        if self.priority_mode:
            self._priority_failures=0
        else:
            self._priority_failures=0

    def _next_retry_delay(self):
        # V0.4.21 retry cadence restored. Priority rooms remain fast, while
        # ordinary rooms return to the proven 60-second baseline.
        if self._grace is not None:
            return min(GRACE_RETRY_SECONDS, self.retry_seconds) if not self.priority_mode else min(GRACE_RETRY_SECONDS, 6)
        if not self.priority_mode:
            return self.retry_seconds
        schedule=(3,6,12,20,35,60)
        idx=min(self._priority_failures,len(schedule)-1)
        return min(self.retry_seconds if self.retry_seconds < 60 else 60, schedule[idx])

    def emit(self, kind, **data):
        self.events.put(MonitorEvent(kind, time.time(), data))

    def poll(self, limit=1000):
        out=[]
        for _ in range(limit):
            try: out.append(self.events.get_nowait())
            except queue.Empty: break
        return out

    def _dedup(self, bucket, key, window=None):
        if not key: return False
        if window is None: window = DEDUP_SECONDS
        now=time.monotonic()
        with self._seen_lock:
            old=self._seen_ids[bucket].get(key)
            self._seen_ids[bucket][key]=now
            if len(self._seen_ids[bucket]) > 5000:
                cutoff=now-window
                self._seen_ids[bucket]={k:v for k,v in self._seen_ids[bucket].items() if v>=cutoff}
        return old is not None and now-old < window

    def _live_sec(self, ts=None):
        if self.live_start is None: return None
        return max(0.0, (ts or time.time()) - self.live_start)

    def _set_live_start(self, client):
        info=getattr(client, "room_info", None)
        ct=nested(info, "create_time", default=None)
        if ct is None: ct=nested(info, "room_info", "create_time", default=None)
        try:
            if ct is not None:
                value=float(ct); value=value/1000 if value>10_000_000_000 else value
                if 946684800 <= value <= time.time()+120:
                    self.live_start=value; self.time_source="TIKTOK create_time"; return
        except Exception: pass
        self.live_start=time.time(); self.time_source="CONNECTION FALLBACK"

    def _real_ts(self, event):
        return event_create_time(event) or time.time()

    def _bucket_label(self, live_sec):
        if live_sec <= 30*60: return "30秒"
        if live_sec <= 120*60: return "1分鐘"
        if live_sec <= 6*3600: return "5分鐘"
        return "15分鐘"

    async def _sample_viewers_loop(self):
        while not self.stop_flag.is_set() and self.session_id:
            try:
                await asyncio.sleep(max(1.0, float(VIEWER_SAMPLE_SECONDS)))
            except asyncio.CancelledError:
                return
            if not self.session_id or self.live_start is None:
                continue
            ts=time.time(); live=self._live_sec(ts); viewers=int(self.stats.get("viewers",0) or 0); bucket=self._bucket_label(live or 0)
            try:
                self.db.viewer(self.session_id,ts,live,viewers,int(self.stats.get("total_viewers",0) or 0))
                if self.log:
                    self.log._stats_for_log=self.stats
                    self.log.viewer_sample(ts,live,viewers,bucket)
                    self.log.dashboard(ts,self.stats)
                self.emit("viewer_sample",ts=ts,live_sec=live,viewers=viewers,bucket=bucket)
            except Exception as e:
                self.emit("warning",message="觀眾取樣寫入失敗："+str(e))

    def _seed_stats_from_db(self, sid):
        """V0.6.42 after a program restart the same session continues: load the counters from the database."""
        con=sqlite3.connect(str(DB_PATH), timeout=2)
        try:
            con.execute("PRAGMA busy_timeout=1500"); one=lambda q: (con.execute(q,(sid,)).fetchone() or [0])
            self.stats["comments"]=int(one("SELECT COUNT(*) FROM comments WHERE session_id=?")[0] or 0)
            self.stats["joins"]=int(one("SELECT COUNT(*) FROM joins WHERE session_id=?")[0] or 0)
            g=one("SELECT COUNT(*),COALESCE(SUM(diamonds),0) FROM gifts WHERE session_id=?")
            self.stats["gifts"]=int(g[0] or 0); self.stats["gift_diamonds"]=int(g[1] or 0)
            r=con.execute("SELECT COALESCE(last_total_viewers,0),COALESCE(peak_viewers,0) FROM sessions WHERE id=?",(sid,)).fetchone()
            if r: self.stats["total_viewers"]=max(int(self.stats.get("total_viewers") or 0),int(r[0] or 0)); self.stats["peak_viewers"]=max(int(self.stats.get("peak_viewers") or 0),int(r[1] or 0))
        finally: con.close()

    def _reset_live_state(self):
        self.join_counts.clear(); self.observed_users.clear(); self.user_levels.clear(); self.levelup_keys.clear()
        self.stats={"comments":0,"preconnect":0,"joins":0,"gifts":0,"gift_diamonds":0,"likes":0,"shares":0,"follows":0,"viewers":0,"total_viewers":0,"peak_viewers":0,"gift_types":0,"like_room_total":None,"unique_observed":0}
        self._ended_sent=False

    def _enter_grace(self, reason):
        """Room dropped (network change / TikTok end signal). Keep the session open for
        RESUME_GRACE_SECONDS; a reconnect to the same room continues it, otherwise it is finalized."""
        sid=self.session_id
        if not sid: return
        if self.viewer_sampler_task:
            try: self.viewer_sampler_task.cancel()
            except Exception: pass
            self.viewer_sampler_task=None
        now=time.time()
        try:
            if self.db: self.db.session_pause(sid, now)
        except Exception: pass
        if self.log:
            try:
                self.log.write("sessions", f"中斷: {now_iso(now)}（{reason}）· {RESUME_GRACE_SECONDS//60} 分鐘內重新連上同一個直播間會續寫本場\n")
                self.log.write("dashboard", f"[{fmt_real(now)[:8]}] SIGNAL LOST ({reason}) · waiting up to {RESUME_GRACE_SECONDS//60} min\n")
            except Exception: pass
        self._grace={"sid":sid,"log":self.log,"reason":reason,"since":now,"until":now+RESUME_GRACE_SECONDS,
                     "live_start":self.live_start,"time_source":self.time_source,"room_id":self.room_id}
        self.session_id=None; self.log=None; self._ended_sent=True
        self.emit("grace", session_id=sid, reason=reason, since=now, until=now+RESUME_GRACE_SECONDS)
        try:   # expire even if the websocket lingers after TikTok's end signal
            asyncio.get_running_loop().create_task(self._grace_watchdog(sid))
        except RuntimeError:
            pass

    async def _grace_watchdog(self, sid):
        try:
            while self._grace is not None and self._grace.get("sid")==sid:
                await asyncio.sleep(1)
                self._check_grace_expiry()
        except asyncio.CancelledError:
            pass

    def _finalize_grace(self, status=None):
        g=self._grace
        if not g: return
        self._grace=None
        status=status or ("ENDED" if g["reason"]=="ENDED" else "DISCONNECTED")
        try:
            if self.db: self.db.session_finalize(g["sid"], status)
        except Exception: pass
        lg=g.get("log")
        if lg:
            try: lg.session_end(g["since"], status); lg.close()
            except Exception: pass
        self.emit("ended", session_id=g["sid"], status=status, since=g["since"])

    def _check_grace_expiry(self):
        if self._grace is not None and time.time() > self._grace["until"]:
            self._finalize_grace()

    async def _one_connection(self):
        from TikTokLive import TikTokLiveClient
        from TikTokLive.events import ConnectEvent, DisconnectEvent, LiveEndEvent, CommentEvent, JoinEvent, GiftEvent, LikeEvent, FollowEvent, ShareEvent, RoomUserSeqEvent
        # V0.4.51: level-up capture disabled (never produced data in 205 sessions); saves
        # parsing every Barrage message. Re-enable by importing BarrageEvent here.
        BarrageEvent = None
        import re as _re
        _re_rank = _re.compile(r"Rank|League|Grade|Battle|Unknown|Hourly|Leaderboard|RoomVerify|InRoomBanner", _re.I)
        client=TikTokLiveClient(unique_id=self.username)
        self.client=client; self.loop=asyncio.get_running_loop()
        cache_reconnect = bool(self.cache_resume_reconnect and self.session_id)
        self._check_grace_expiry()
        if not cache_reconnect:
            self.session_id=None
            if self._grace is None:          # keep the held session's counters while it may resume
                self._reset_live_state()
        self.emit("connecting")
        connected_event = asyncio.Event()

        @client.on(ConnectEvent)
        async def on_connect(event):
            self.connection_wall=time.time(); self._set_live_start(client)
            room_id = str(getattr(client,"room_id", ""))
            resumed=False; gap=0.0
            if not cache_reconnect and self._grace is None and RESUME_HANDOFF:     # V0.6.42 程式重新啟動前這場還在直播 → 當作斷線重連
                h=_take_handoff(self.username)
                if h and time.time()-float(h.get("t") or 0)<=RESUME_GRACE_SECONDS:
                    lg=None
                    try: lg=LiveLogWriter(self.username, int(h["sid"]), str(h.get("room_id") or ""))
                    except Exception: pass
                    self._grace={"sid":int(h["sid"]),"log":lg,"reason":"RESTART","since":float(h.get("t") or time.time()),"until":time.time()+60,
                                 "live_start":h.get("live_start"),"time_source":h.get("time_source"),"room_id":str(h.get("room_id") or "")}
                    self._seed_after_restart=True
            if not cache_reconnect:
                g=self._grace
                if g and time.time()<=g["until"] and (not g["room_id"] or not room_id or g["room_id"]==room_id):
                    # V0.4.63: same live came back within the grace window -> continue the session
                    self._grace=None; resumed=True; gap=time.time()-g["since"]
                    self.session_id=g["sid"]; self.log=g["log"]; self.live_start=g["live_start"] or self.live_start; self.time_source=g["time_source"] or self.time_source
                    self._ended_sent=False
                    try: self.db.session_resume(self.session_id)
                    except Exception: pass
                    if getattr(self,"_seed_after_restart",False):        # V0.6.42 數字從資料庫接回來（重新啟動後不會從 0 開始）
                        self._seed_after_restart=False
                        try: self._seed_stats_from_db(self.session_id)
                        except Exception: pass
                    if self.log:
                        self.log.write("sessions", f"重新連線: {now_iso()} · 中斷 {fmt_elapsed(gap)} · 續寫同一場\n")
                        self.log.write("dashboard", f"[{fmt_real(time.time())[:8]}] RECONNECTED after {fmt_elapsed(gap)} · same session\n")
                else:
                    if g: self._finalize_grace()      # expired, or TikTok opened a new room = a new live
                    self._reset_live_state()
                    self.session_id=self.db.session_start(self.username, room_id, self.live_start, self.time_source, self.display_name)
                    self.log = LiveLogWriter(self.username, self.session_id, room_id)
                    self.log.write("dashboard", f"時間來源: {self.time_source}\n直播開始: {now_iso(self.live_start)}\n觀眾取樣: 每 5 秒\n\n")
            else:
                self.cache_resume_reconnect=False
            self.room_id=room_id
            self.viewer_sampler_task = asyncio.create_task(self._sample_viewers_loop())
            connected_event.set()
            try:   # V0.4.69 league probe: what does the room expose about rank / league?
                if LEAGUE_PROBE_ENABLED: write_league_probe(self.username, "room_info", _league_hits(getattr(client, "room_info", None) or {}))
            except Exception: pass
            self.emit("connected", room_id=room_id, time_source=self.time_source, live_start=self.live_start, session_id=self.session_id, stream_url=extract_stream_pull_url(getattr(client,"room_info",None)), resumed=resumed, gap=gap)

        # V0.4.69 league probe: rank-type messages (first few of each per connection)
        import TikTokLive.events as _ev_mod
        _probe_counts = Counter()
        def _make_probe(name):
            async def _probe(event):
                if not LEAGUE_PROBE_ENABLED or _probe_counts[name] >= 5: return
                _probe_counts[name] += 1
                obj = _event_to_obj(event)
                write_league_probe(self.username, name, {"hits": _league_hits(obj), "raw": json.dumps(obj, ensure_ascii=False, default=str)[:6000]})
            return _probe
        for _name in dir(_ev_mod):
            if _name.endswith("Event") and _re_rank.search(_name):
                _cls = getattr(_ev_mod, _name, None)
                try: client.on(_cls)(_make_probe(_name))
                except Exception: pass

        @client.on(DisconnectEvent)
        async def on_disconnect(event):
            self.emit("disconnected")

        @client.on(LiveEndEvent)
        async def on_end(event):
            # V0.4.63: TikTok also sends this when a streamer's network drops; hold the session
            # for RESUME_GRACE_SECONDS instead of ending it right away.
            self._enter_grace("ENDED")

        @client.on(CommentEvent)
        async def on_comment(event):
            ui=user_info(getattr(event,"user",None)); self._observe_user(ui); text=str(getattr(event,"comment","") or ""); real=self._real_ts(event); live=self._live_sec(real); eid=event_id(event)
            if not text or not self.session_id: return
            if self._dedup("comment", eid): return
            # Pre-connect history is kept, but marked as such. It is not fabricated into a live timeline.
            is_pre = self.connection_wall is not None and real < self.connection_wall - 0.5
            if is_pre: self.stats["preconnect"] += 1
            if not self.db.comment(self.session_id,eid,real,live,ui,text): return
            self.stats["comments"] += 1
            song = parse_song_comment(text)
            song_saved = False
            if song:
                try:
                    song_eid = eid or f"song:{ui.get('unique_id','') or ui.get('nickname','')}:{int(real*1000)}"
                    song_saved = self.db.song(self.session_id, song_eid, real, live, ui, song, text)
                    if song_saved and self.log:
                        self.log.song(real, live, ui.get("nickname"), ui.get("unique_id"), song, text)
                except Exception:
                    song_saved = False
            if self.log:
                self.log.chat(real, live, ui.get("nickname"), ui.get("unique_id"), text)
                self.log.profile_activity(real, "COMMENT", ui.get("unique_id"), ui.get("nickname"), 1)
                self.log.analytics(real, self.stats); self.log.dashboard(real, self.stats)
            self.emit("comment", real_ts=real, live_sec=live, preconnect=is_pre, **ui, comment=text, event_id=eid)
            if song_saved:
                self.emit("song", real_ts=real, live_sec=live, **ui, song=song, raw_comment=text, event_id=eid)

        if BarrageEvent is not None:
            @client.on(BarrageEvent)
            async def on_barrage(event):
                info = extract_levelup_info(event)
                if not info or not self.session_id:
                    return
                real = self._real_ts(event); live = self._live_sec(real)
                user_key = info.get("id") or info.get("username") or info.get("nickname")
                new_level = _to_int(info.get("new_level"))
                if new_level is None or not user_key:
                    return
                previous = self.user_levels.get(str(user_key))
                # Only keep a genuine increase. Avoid duplicate notices and backwards/stale frames.
                if previous is not None and new_level <= int(previous):
                    return
                if previous is not None:
                    old_level = int(previous)
                else:
                    old_level = None
                self.user_levels[str(user_key)] = new_level
                eid = str(info.get("event_id") or f"upgrade:{user_key}:{new_level}:{int(real*1000)}")
                dedup_key = f"{user_key}:{new_level}"
                if dedup_key in self.levelup_keys:
                    return
                self.levelup_keys.add(dedup_key)
                ui = {"id": str(info.get("id") or ""), "unique_id": str(info.get("username") or ""), "nickname": str(info.get("nickname") or "")}
                if not self.db.level_up(self.session_id,eid,real,live,ui,old_level,new_level,info.get("privilege_key",""),info.get("action",""),info.get("event_type","USERUPGRADE"),info.get("raw_summary","")):
                    return
                if self.log:
                    self.log.level_up(real, live, ui.get("nickname"), ui.get("unique_id"), old_level, new_level, info.get("event_type","USERUPGRADE"))
                    self.log.profile_activity(real, "LEVEL_UP", ui.get("unique_id"), ui.get("nickname"), new_level)
                    self.log.analytics(real, self.stats); self.log.dashboard(real, self.stats)
                self.emit("level_up", real_ts=real, live_sec=live, old_level=old_level, new_level=new_level, event_type=info.get("event_type","USERUPGRADE"), event_id=eid, **ui)

        @client.on(JoinEvent)
        async def on_join(event):
            ui=user_info(getattr(event,"user",None)); self._observe_user(ui); real=self._real_ts(event); live=self._live_sec(real); eid=event_id(event)
            if not self.session_id: return
            if self._dedup("join", eid): return
            key=ui["unique_id"] or ui["nickname"]; self.join_counts[key]+=1
            if not self.db.join(self.session_id,eid,real,live,ui): return
            self.stats["joins"] += 1
            if self.log:
                self.log.join(real, live, ui.get("nickname"), ui.get("unique_id"), self.join_counts[key])
                self.log.profile_activity(real, "JOIN", ui.get("unique_id"), ui.get("nickname"), self.join_counts[key])
                self.log.analytics(real, self.stats); self.log.dashboard(real, self.stats)
            self.emit("join", real_ts=real, live_sec=live, count=self.join_counts[key], **ui, event_id=eid)

        @client.on(GiftEvent)
        async def on_gift(event):
            gift=getattr(event,"gift",None); ui=user_info(getattr(event,"user",None)); self._observe_user(ui)
            if gift is None or not self.session_id: return
            # TikTokLive 7.x: streaking intermediate events are ignored; final event carries repeat_count.
            if bool(getattr(event,"streaking",False)): return
            real=self._real_ts(event); live=self._live_sec(real); eid=event_id(event)
            if self._dedup("gift", eid): return
            name=str(getattr(gift,"name","Unknown Gift") or "Unknown Gift")
            gid=str(getattr(gift,"id",getattr(gift,"gift_id","")) or "")
            count=int(getattr(event,"repeat_count",1) or 1)
            diamond_each=int(getattr(gift,"diamond_count",nested(gift,"info","diamond_count",default=0)) or 0)
            diamonds=diamond_each*count
            try: icon=gift_image_url(gift)                                   # V0.6.46 official gift picture (for the 送禮動畫)
            except Exception: icon=""
            if not self.db.gift(self.session_id,eid,real,live,ui,gid,name,count,diamond_each,diamonds): return
            self.stats["gifts"] += count; self.stats["gift_diamonds"] += diamonds
            if self.log:
                self.log.gift(real, live, ui.get("nickname"), ui.get("unique_id"), name, count, diamond_each, diamonds)
                self.log.profile_activity(real, "GIFT", ui.get("unique_id"), ui.get("nickname"), f"{name} x{count} / {diamonds}")
                self.log.analytics(real, self.stats); self.log.dashboard(real, self.stats)
            self.emit("gift", real_ts=real, live_sec=live, **ui, gift_id=gid, gift_name=name, count=count, diamond_each=diamond_each, diamonds=diamonds, event_id=eid, gift_icon=icon)

        @client.on(LikeEvent)
        async def on_like(event):
            ui=user_info(getattr(event,"user",None)); real=self._real_ts(event); live=self._live_sec(real); self._observe_user(ui)
            count=int(getattr(event,"count",getattr(event,"like_count",1)) or 1)
            total=getattr(event,"total",getattr(event,"total_likes",None))
            try: total=int(total) if total is not None else None
            except Exception: total=None
            if self.session_id and not self.db.like(self.session_id,event_id(event),real,live,ui,count,total):
                return
            self.stats["likes"] += count
            if total is not None: self.stats["like_room_total"]=max(self.stats.get("like_room_total") or 0,total)
            if self.log:
                self.log.like(real, live, ui.get("nickname"), ui.get("unique_id"), count, total)
                self.log.profile_activity(real, "LIKE", ui.get("unique_id"), ui.get("nickname"), count)
                self.log.analytics(real, self.stats); self.log.dashboard(real, self.stats)
            self.emit("like", real_ts=real, live_sec=live, **ui, count=count, total=total)

        @client.on(FollowEvent)
        async def on_follow(event):
            ui=user_info(getattr(event,"user",None)); real=self._real_ts(event); live=self._live_sec(real); self._observe_user(ui)
            if self.session_id: self.db.social("follows",self.session_id,event_id(event),real,live,ui)
            self.stats["follows"]+=1
            if self.log:
                self.log.profile_activity(real, "FOLLOW", ui.get("unique_id"), ui.get("nickname"), 1)
                self.log.analytics(real, self.stats); self.log.dashboard(real, self.stats)
            self.emit("follow",real_ts=real,live_sec=live,**ui)

        @client.on(ShareEvent)
        async def on_share(event):
            ui=user_info(getattr(event,"user",None)); real=self._real_ts(event); live=self._live_sec(real); self._observe_user(ui)
            if self.session_id: self.db.social("shares",self.session_id,event_id(event),real,live,ui)
            self.stats["shares"]+=1
            if self.log:
                self.log.profile_activity(real, "SHARE", ui.get("unique_id"), ui.get("nickname"), 1)
                self.log.analytics(real, self.stats); self.log.dashboard(real, self.stats)
            self.emit("share",real_ts=real,live_sec=live,**ui)

        @client.on(RoomUserSeqEvent)
        async def on_viewers(event):
            raw=getattr(event,"total",0) or 0
            cumulative=getattr(event,"total_user",0) or 0
            try: viewers=int(raw)
            except Exception: viewers=0
            try: total_viewers=int(cumulative)
            except Exception: total_viewers=0
            real=time.time(); live=self._live_sec(real)
            self.stats["viewers"]=viewers; self.stats["total_viewers"]=total_viewers; self.stats["peak_viewers"]=max(self.stats["peak_viewers"],viewers)
            if self.session_id and self.db:
                try: self.db.update_session_viewers(self.session_id,viewers,total_viewers,self.stats["peak_viewers"])
                except Exception: pass
            if self.log:
                self.log.analytics(real, self.stats); self.log.dashboard(real, self.stats)
            self.emit("viewers",viewers=viewers,total_viewers=total_viewers,peak=self.stats["peak_viewers"])

        try:
            # TikTokLive 7.x exposes start() as the non-blocking primitive.
            # We wait only for the initial ConnectEvent, then keep the websocket
            # task alive for the entire livestream. The old implementation wrapped
            # client.connect() in a short global timeout, which could tear down a
            # healthy connection and create the connect/disconnect/retry loop seen
            # in V0.4.9.
            try:
                task = await client.start(fetch_room_info=True, fetch_gift_info=False, fetch_live_check=True)
            except TypeError:
                task = await client.start()
            try:
                await asyncio.wait_for(connected_event.wait(), timeout=float(CONNECT_EVENT_TIMEOUT))
            except asyncio.TimeoutError as e:
                raise RuntimeError("已取得直播連線但 20 秒內未收到 ConnectEvent") from e
            await task
            if self.cache_pause_requested and not self.stop_flag.is_set():
                self.cache_paused = True
                self.emit("cache_paused", username=self.username)
                while self.cache_pause_requested and not self.stop_flag.is_set():
                    await asyncio.sleep(0.05)
                if not self.stop_flag.is_set():
                    self.cache_resume_reconnect=True
                    self.cache_paused=False
        finally:
            if self.viewer_sampler_task:
                self.viewer_sampler_task.cancel(); self.viewer_sampler_task=None
            if self.cache_pause_requested or self.cache_resume_reconnect:
                # Cache cycle: keep the live session open. The GUI will resume the
                # same session after the package snapshot is complete. Recording is
                # independent and is never touched here.
                pass
            elif self.session_id:
                self._enter_grace("DISCONNECTED")
            elif self.log:
                self.log.close(); self.log = None
            self.client=None; self.loop=None

    async def _run(self):
        try:
            import TikTokLive  # noqa
        except Exception as e:
            self.emit("error",message="TikTokLive 套件載入失敗："+str(e)); return
        self.emit("waiting")
        try:
            waited=0.0
            while not self.stop_flag.is_set():
                while not self.stop_flag.is_set() and waited < self.initial_delay:
                    await asyncio.sleep(min(0.5,self.initial_delay-waited)); waited += 0.5
                if self.stop_flag.is_set(): break
                waited=0.0
                try:
                    if self.db is None:
                        self.db=Database()
                        global _ORPHANS_CLOSED
                        if not _ORPHANS_CLOSED:
                            _ORPHANS_CLOSED=True; self.db.close_orphan_reconnecting()
                except Exception as e:
                    delay=self._next_retry_delay(); self.emit("retry",message="SQLite 初始化失敗："+str(e),retry=delay)
                    self._priority_failures += 1
                    await asyncio.sleep(delay)
                    continue
                try:
                    await self._one_connection()
                    self._priority_failures=0
                    if self.stop_flag.is_set(): break
                    if self.cache_resume_reconnect:
                        continue
                    if self._grace is None:
                        self.emit("waiting",message="目前離線，持續等待下一次開播…")
                except Exception as e:
                    delay=self._next_retry_delay()
                    self.emit("retry",message=str(e),retry=delay,grace=self._grace is not None)
                    self._priority_failures += 1
                delay=self._next_retry_delay()
                while not self.stop_flag.is_set() and waited < delay:
                    await asyncio.sleep(1); waited += 1
                    if self._grace is not None:
                        self._check_grace_expiry()
                        if self._grace is None:   # just finalized -> back to the normal cadence
                            self.emit("waiting",message="目前離線，持續等待下一次開播…"); delay=min(delay,self._next_retry_delay())
                waited=0.0
        finally:
            self._finalize_grace()
            if self.log:
                self.log.session_end(time.time(), "STOPPED")
                self.log.close(); self.log = None
            if self.db:
                self.db.close(); self.db=None
            self.emit("stopped")

    def start(self):
        if self.worker and self.worker.is_alive(): return
        self.stop_flag.clear()
        self.worker=threading.Thread(target=self._thread_main,name="TikLiveEngine",daemon=True)
        self.worker.start()

    def _thread_main(self):
        try: asyncio.run(self._run())
        except Exception as e: self.emit("error",message=str(e))

    def request_cache_pause(self):
        """Temporarily disconnect a LIVE room for a consistent cache snapshot.
        The live session/database stay open, and audio recording is untouched.
        """
        if not self.client or not self.loop:
            return False
        self.cache_pause_requested=True
        self.cache_paused=False
        self.cache_pause_event.clear()
        try:
            asyncio.run_coroutine_threadsafe(self.client.disconnect(), self.loop)
            return True
        except Exception:
            return False

    def resume_cache(self):
        self.cache_pause_requested=False
        self.cache_pause_event.set()

    def stop(self):
        self.stop_flag.set()
        if self.loop and self.client:
            try: asyncio.run_coroutine_threadsafe(self.client.disconnect(), self.loop)
            except Exception: pass

    def close(self):
        self.stop()
        if self.worker and self.worker.is_alive(): self.worker.join(timeout=1.5)
