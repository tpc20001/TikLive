"""V0.6.01 網頁版電腦介面 — server side (the page itself is in webpc_page.py).

Every function gets the running MainWindow `win`; the names of app.py (THEMES, DB_PATH, _HddLane …) come from
the module the window was created from, so a hot update always uses the matching code. Handlers run on the
window's thread; slow work goes to a worker thread and answers through win._ui_call.
"""
import json, os, re, sys, time, threading, sqlite3, traceback
from pathlib import Path
from datetime import datetime, timedelta


def _G(win):
    return sys.modules[type(win).__module__].__dict__


def QTimer_single(win, ms, fn):
    G = _G(win); G['QTimer'].singleShot(ms, fn)


def _send(win, sock, obj, code='200 OK'):
    G = _G(win)
    try: b = json.dumps(G['_json_safe'](obj), ensure_ascii=False, allow_nan=False)
    except Exception as ex: b = json.dumps({'error': f'{type(ex).__name__}: {ex}'}, ensure_ascii=False)
    win._phone_send(sock, code, b, 'application/json; charset=utf-8')


def _encode(win, sock, obj, code='200 OK'):
    """TK_V0.8.34.019 在工作執行緒把回應整包做好（JSON → 壓縮 → HTTP 標頭）：畫面執行緒只剩把位元組寫出去（大回應不會卡住主程式）."""
    G = _G(win)
    try: b = json.dumps(G['_json_safe'](obj), ensure_ascii=False, allow_nan=False)
    except Exception as ex: b = json.dumps({'error': f'{type(ex).__name__}: {ex}'}, ensure_ascii=False)
    body = b.encode('utf-8'); extra = ''
    try:
        if len(body) > 2048 and 'gzip' in str((getattr(sock, '_hdr', {}) or {}).get('accept-encoding', '')):
            import gzip
            body = gzip.compress(body, 6); extra = 'Content-Encoding: gzip\r\nVary: Accept-Encoding\r\n'
    except Exception: pass
    head = f'HTTP/1.1 {code}\r\nContent-Type: application/json; charset=utf-8\r\nContent-Length: {len(body)}\r\nCache-Control: no-store\r\n{extra}Connection: close\r\n\r\n'.encode('ascii')
    return head + body


def _write_raw(sock, data):
    try: sock.write(data); sock.flush(); sock.disconnectFromHost()
    except Exception: pass


def _img_bg(win, sock, getter, cache=86400, ctype='image/jpeg'):
    """TK_V0.9.12 圖片：工作執行緒找檔＋讀檔＋做好整包 HTTP 回應（含 ETag，瀏覽器問「有沒有變」就回 304 不再傳一次），
    畫面執行緒只負責把位元組寫出去（以前讀檔也在畫面執行緒，主程式一忙圖就慢）."""
    hdr = getattr(sock, '_hdr', {}) or {}
    def work():
        data = None
        try:
            p = getter()
            if p is not None and p.exists():
                st = p.stat(); et = f'"{int(st.st_mtime)}-{st.st_size}"'; cc = cache(p) if callable(cache) else cache
                if hdr.get('if-none-match') == et:
                    data = f'HTTP/1.1 304 Not Modified\r\nETag: {et}\r\nCache-Control: private, max-age={int(cc)}\r\nConnection: close\r\n\r\n'.encode('ascii')
                else:
                    body = p.read_bytes()
                    data = (f'HTTP/1.1 200 OK\r\nContent-Type: {ctype}\r\nContent-Length: {len(body)}\r\nCache-Control: private, max-age={int(cc)}\r\nETag: {et}\r\nConnection: close\r\n\r\n').encode('ascii') + body
        except Exception: data = None
        if data is None: win._ui_call.emit(lambda: win._phone_send(sock, '404 Not Found', 'not found'))
        else: win._ui_call.emit(lambda d=data: _write_raw(sock, d))
    threading.Thread(target=work, name='TikLiveImg', daemon=True).start()


class _DaemonPool:
    """TK_V0.8.34.021 網頁請求共用的工作執行緒（daemon：關程式／重開時不會被卡住；ThreadPoolExecutor 的不是 daemon）."""
    def __init__(self, n=6):
        import queue
        self.q = queue.Queue(); self.n = n; self.busy = 0; self.lk = threading.Lock()
        for i in range(n): threading.Thread(target=self._run, name=f'TikLiveWebPc{i}', daemon=True).start()
    def _run(self):
        while True:
            fn = self.q.get()
            with self.lk: self.busy += 1
            try: fn()
            except Exception: pass
            finally:
                with self.lk: self.busy -= 1
    def free(self):
        return self.n - self.busy - self.q.qsize()
    def submit(self, fn): self.q.put(fn)


def _pool():
    """TK_V0.8.34.019 網頁請求共用最多 6 條工作執行緒（不再每個請求開一條）；都在忙時改開新的，不會讓網頁等不到."""
    try:
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
    except Exception: app = None
    p = getattr(app, '_tlm_webpool2', None) if app is not None else None
    if p is None:
        try:                                                                # 0.8.34.019～.020 的舊執行緒池（不是 daemon）：收掉
            old = getattr(app, '_tlm_webpool', None)
            if old is not None: old.shutdown(wait=False); setattr(app, '_tlm_webpool', None)
        except Exception: pass
        p = _DaemonPool(6)
        try: setattr(app, '_tlm_webpool2', p)
        except Exception: pass
    return p


def _bg(win, sock, fn):
    """Run fn() on a worker thread and send its result as JSON."""
    def work():
        try: r = fn()
        except Exception as ex:
            r = {'error': f'{type(ex).__name__}: {ex}'}
            try: (Path(_G(win)['LOG_DIR']) / 'web_error_log.txt').open('a', encoding='utf-8').write(f'[{time.strftime("%Y-%m-%d %H:%M:%S")}] webpc\n{traceback.format_exc()}\n')
            except Exception: pass
        try: data = _encode(win, sock, r)
        except Exception:
            win._ui_call.emit(lambda r=r, s=sock: _send(win, s, r)); return
        win._ui_call.emit(lambda d=data, s=sock: _write_raw(s, d))
    try:
        p = _pool()
        if p.free() > 0: p.submit(work); return                             # 有空的就給它；都在忙：直接另開一條（慢的請求不會擋住其他頁）
    except Exception: pass
    threading.Thread(target=work, name='TikLiveWebPc', daemon=True).start()


def _body(body):
    try: return json.loads(body.decode('utf-8') or '{}')
    except Exception: return {}


def _pw_ok(win, sock, d):
    """Writes need the web password when one is set (same rule as 設定 on the phone)."""
    if not win._web_pw_set(): return True
    peer = sock.peerAddress().toString(); fails = win.__dict__.setdefault('_web_fails', {}); n, t = fails.get(peer, (0, 0))
    if n >= 5 and time.time() - t < 300: _send(win, sock, {'ok': False, 'message': '錯太多次，請 5 分鐘後再試', 'pw': True}, '429 Too Many'); return False
    if not win._web_pw_check(str(d.get('pw', ''))):
        fails[peer] = (n + 1, time.time()); _send(win, sock, {'ok': False, 'message': '需要網頁密碼（或密碼不對）', 'pw': True}, '401 Unauthorized'); return False
    fails.pop(peer, None); return True


def _color_of(label):
    m = re.search(r'color:\s*(#[0-9a-fA-F]{3,8})', label.styleSheet() or '')
    return m.group(1) if m else ''


def _side(win):
    try: return [list(r) for r in win._side_rows()]          # V0.6.03 same rows as the desktop's 左下角
    except Exception: return []


# ------------------------------------------------------------------ state (sidebar, tabs, pending) every 2 s
def state(win):
    G = _G(win); now = time.time()
    wl = win._web_live(); rooms = wl['rooms']
    sm = getattr(win, 'sysmon', None); d = dict(sm.data) if sm else {}
    disks = []
    for k, v in list((d.get('disks') or {}).items()):
        L = Path(k).drive.upper() or str(k).rstrip('\\').upper()
        disks.append({'d': L, 'used': v[0], 'free': v[1], 'busy': (d.get('disk_busy') or {}).get(L)})
    try: today = win._net_day()[0]
    except Exception: today = 0
    cats = win._cats(); of = win._cat_of()
    return {'ver': G['APP_VERSION'], 'mode': G['THEME_MODE'].get('mode', 'dark'), 'time': datetime.now().strftime('%H:%M:%S'),
            'count_text': '● {0} / {1} 直播間'.format(*(getattr(win, '_count_pair', None) or (0, len(win.engines), 0))[:2]),
            'cnt': list(getattr(win, '_count_pair', None) or (0, len(win.engines), 0)), 'running': bool(win.engines), 'stopping': bool(getattr(win, '_stopping_engines', None)),
            'status_text': win.side_status.text(), 'status_color': _color_of(win.side_status),
            'sys': {'cpu': d.get('cpu'), 'ram': d.get('ram'), 'ram_used': d.get('ram_used'), 'ram_total': d.get('ram_total'), 'gpus': d.get('gpus') or [],
                    'temps': d.get('temps') or {}, 'disks': disks, 'disk_temps': d.get('disk_temps') or {}},
            'qs': (lambda v: dict(v, text=win._q_text(v)))(win._q_summary()) if hasattr(win, '_q_summary') else None,   # V0.6.38
            'net': {'rx': getattr(win, '_net_rx_rate', 0.0), 'tx': getattr(win, '_net_tx_rate', 0.0), 'today': today, 'nrec': len(getattr(win, 'video_recorders', {}) or {})},
            'side': _side(win),
            'rooms': rooms, 'tier_days': wl.get('tier_days') or [3, 7], 'tab_order': list(getattr(win, 'tab_order', []) or []), 'cats': cats, 'of': of,
            'statusbar': win.statusBar().currentMessage()}


# ------------------------------------------------------------------ one session: cards + rows after the given cursors
_TABLES = {
    'c': ("SELECT rowid,ts,live_sec,username,nickname,comment FROM comments WHERE session_id=? AND rowid>? ORDER BY rowid LIMIT ?", 40000),
    'g': ("SELECT rowid,ts,live_sec,username,nickname,gift_name,count,diamond_each,diamonds,COALESCE(gift_id,'') FROM gifts WHERE session_id=? AND rowid>? ORDER BY rowid LIMIT ?", 20000),   # V0.6.46 [9]=gift_id
    'j': ("SELECT rowid,ts,live_sec,username,nickname FROM joins WHERE session_id=? AND rowid>? ORDER BY rowid LIMIT ?", 40000),
    'l': ("SELECT rowid,ts,live_sec,username,nickname,count,room_total FROM likes WHERE session_id=? AND rowid>? ORDER BY rowid LIMIT ?", 60000),
    's': ("SELECT rowid,ts,live_sec,username,nickname,song FROM songs WHERE session_id=? AND rowid>? ORDER BY rowid LIMIT ?", 5000),
    'v': ("SELECT rowid,ts,viewers,total_viewers FROM viewer_samples WHERE session_id=? AND rowid>? ORDER BY rowid LIMIT ?", 20000),
}


def _rows(con, sql, args):
    try: return [list(r) for r in con.execute(sql, args).fetchall()]
    except Exception: return []


_SUMC = {}                                                                # TK_V0.8.34.019 結束場次的摘要卡片快取 {sid: (ended_at, cards)}


def sess(win, q, live_info):
    """live_info: read on the window thread {u, sid, live, stats, room_id, time_source, live_start}."""
    G = _G(win); sid = int(live_info.get('sid') or 0)
    if not sid: return {'sid': 0}
    con = sqlite3.connect(G['DB_PATH'], timeout=3); con.execute('PRAGMA busy_timeout=2000')
    try:
        s = con.execute('SELECT username,room_id,started_at,ended_at,live_start_epoch,time_source,status,COALESCE(last_viewers,0),COALESCE(last_total_viewers,0),COALESCE(peak_viewers,0),COALESCE(streamer_name,"") FROM sessions WHERE id=?', (sid,)).fetchone()
        if not s: return {'sid': 0}
        u, room, st, en, lse, tsrc, status, lv, ltv, peak, sname = s
        out = {'sid': sid, 'u': u, 'name': win.streamer_names.get(u, sname or u), 'room_id': live_info.get('room_id') or room or '-', 'time_source': live_info.get('time_source') or tsrc or '-',
               'status': status, 'started': st, 'ended': en, 'live': bool(live_info.get('live')), 'live_start': float(lse) if lse else None, 'cur': {}}
        try: st_ep = datetime.fromisoformat(str(st)).timestamp() if st else None
        except Exception: st_ep = None
        try: en_ep = datetime.fromisoformat(str(en)).timestamp() if en else None
        except Exception: en_ep = None
        out['started_ep'] = st_ep; out['ended_ep'] = en_ep
        for k, (sql, lim) in _TABLES.items():
            try: after = int(q.get(k, '0') or 0)
            except Exception: after = 0
            if after < 0: out[k] = []; continue                     # the page does not need this table
            if after == 0:                                        # first load: the newest rows (a very long live keeps its oldest in the DB)
                rows = _rows(con, sql.replace('ORDER BY rowid LIMIT ?', 'ORDER BY rowid DESC LIMIT ?'), (sid, 0, lim))[::-1]
            else: rows = _rows(con, sql, (sid, after, lim))
            out[k] = rows; out['cur'][k] = rows[-1][0] if rows else after
        # cards: live = the engine's own counters; history = the same totals the desktop computes
        stx = live_info.get('stats') or {}
        if out['live'] and stx:
            cards = {'viewers': stx.get('viewers', 0), 'total_viewers': stx.get('total_viewers', 0), 'peak': stx.get('peak_viewers', 0),
                     'unique_observed': stx.get('unique_observed', 0), 'comments': stx.get('comments', 0), 'gifts': stx.get('gifts', 0),
                     'diamonds': stx.get('gift_diamonds', 0), 'likes': stx.get('like_room_total') if stx.get('like_room_total') is not None else stx.get('likes', 0),
                     'shares': stx.get('shares', 0), 'follows': stx.get('follows', 0)}
        elif en and _SUMC.get(sid) and _SUMC[sid][0] == str(en):              # TK_V0.8.34.019 已經結束的場次：摘要數字不會變，算過就記住（網頁每 5 秒問一次）
            cards = dict(_SUMC[sid][1])
        else:
            one = lambda sql: (con.execute(sql, (sid,)).fetchone() or [0])[0] or 0
            g = con.execute('SELECT COALESCE(SUM(count),0),COALESCE(SUM(diamonds),0) FROM gifts WHERE session_id=?', (sid,)).fetchone() or (0, 0)
            lr = one('SELECT MAX(room_total) FROM likes WHERE session_id=? AND room_total IS NOT NULL')
            cards = {'viewers': lv, 'total_viewers': ltv, 'peak': peak, 'comments': one('SELECT COUNT(*) FROM comments WHERE session_id=?'), 'gifts': g[0], 'diamonds': g[1],
                     'likes': lr or one('SELECT COALESCE(SUM(count),0) FROM likes WHERE session_id=?'), 'shares': one('SELECT COUNT(*) FROM shares WHERE session_id=?'),
                     'follows': one('SELECT COUNT(*) FROM follows WHERE session_id=?'),
                     'unique_observed': one('SELECT COUNT(DISTINCT username) FROM (SELECT username FROM comments WHERE session_id=?1 UNION SELECT username FROM joins WHERE session_id=?1 UNION SELECT username FROM gifts WHERE session_id=?1 UNION SELECT username FROM likes WHERE session_id=?1 UNION SELECT username FROM follows WHERE session_id=?1 UNION SELECT username FROM shares WHERE session_id=?1)')}
            cards['repeat'] = one('SELECT COUNT(*) FROM (SELECT username FROM joins WHERE session_id=? GROUP BY username HAVING COUNT(*)>=2)')
            if en and not out['live']:
                if len(_SUMC) > 300: _SUMC.clear()
                _SUMC[sid] = (str(en), dict(cards))
        out['cards'] = cards
        if q.get('top') == '1':
            out['top'] = _rows(con, 'SELECT username,MAX(nickname),SUM(count),SUM(diamonds) FROM gifts WHERE session_id=? GROUP BY username ORDER BY SUM(diamonds) DESC,SUM(count) DESC LIMIT 20', (sid,))
        if out['live'] and live_info.get('live_start'): out['elapsed'] = time.time() - float(live_info['live_start'])
        else:
            a = float(lse) if lse else st_ep; b = en_ep or a
            out['elapsed'] = max(0.0, (b or 0) - (a or 0)) if a else 0
        return out
    finally:
        con.close()


def _live_info(win, q):
    """Which session a request means (window thread): ?id= history session, or ?u= the streamer's current live."""
    sid = int(q.get('id', '0') or 0); u = str(q.get('u', '') or '').lstrip('@')
    info = {'sid': sid, 'live': False}
    if not sid and u:
        e = win.engines.get(u)
        sid = win.engine_sessions.get(u) or (getattr(e, 'session_id', None) if e else None)
        if not sid:
            r = win._web_db('SELECT id FROM sessions WHERE username=? AND id<9000000 ORDER BY id DESC LIMIT 1', (u,)); sid = r[0][0] if r else 0
        info['sid'] = int(sid or 0)
    if info['sid']:
        for uu, e in list(win.engines.items()):
            if getattr(e, 'session_id', None) == info['sid'] and win.engine_status.get(uu) == 'LIVE':
                info.update(live=True, stats=dict(getattr(e, 'stats', {}) or {}), room_id=str(getattr(e, 'room_id', '') or ''),
                            time_source=str(getattr(e, 'time_source', '') or ''), live_start=win.stream_live_start.get(uu) or getattr(e, 'live_start', None))
                break
    return info


# ------------------------------------------------------------------ history lists
def sessions(win, uf, q='', cat=''):
    rows = win._query_sessions_rows(uf=uf or None, q=q or '', cat=cat or '') or []
    try: ed = {str(k): v for k, v in win._edit_counts().items()}                 # V0.6.76 已剪輯（共 N 段）
    except Exception: ed = {}
    try: srt = sorted(_G(win)['_stt_sub_sids']())
    except Exception: srt = []
    return {'rows': [list(r) for r in rows], 'of': win._cat_of(), 'cats': win._cats(), 'q': q or '', 'ed': ed, 'srt': srt}


def gifters(win):
    return {'rows': [list(r) for r in win._gifters_page(0, 500)['rows']]}      # V0.6.17 舊頁面：只給前 500 位


def gifter(win, u):
    G = _G(win)
    rows = win._web_db("SELECT g.ts,g.gift_name,g.count,g.diamonds,s.username,COALESCE(s.streamer_name,''),s.started_at,g.session_id FROM gifts g LEFT JOIN sessions s ON s.id=g.session_id WHERE g.username=? ORDER BY g.ts ASC, g.rowid ASC", (u,))
    out = []
    for ts, gift, cnt, dia, su, sname, st, sid in rows:
        out.append([ts, int(sid or 0), win.streamer_names.get(su, sname or su or ''), gift, cnt, dia])
    nick = win._web_db('SELECT nickname FROM user_profiles WHERE username=? LIMIT 1', (u,))
    try: names = win._gifter_names(u)                     # V0.6.16 暱稱變更紀錄
    except Exception: names = []
    return {'u': u, 'nick': nick[0][0] if nick else '', 'rows': out, 'names': names}


def _prof_plus(win, d):
    """TK_V0.9.52 主播特性：每位加上分類（cat）、等級（g），再附分類清單（每次回應時才查，等級改了馬上看得到；不改快取那份）."""
    try:
        if not isinstance(d, dict) or not isinstance(d.get('rows'), list): return d
        of = win._cat_of(); GR = win._rv_grades() or {}; rows = []
        for r in d['rows']:
            u = r.get('u'); g_ = GR.get(u); rows.append(dict(r, cat=of.get(u, '') or '', g=(g_.get('g') if isinstance(g_, dict) else '') or ''))
        return dict(d, rows=rows, cats=[{'id': c.get('id'), 'name': c.get('name') or c.get('folder')} for c in win._cats()])
    except Exception: return d

def profiles(win):
    return {'rows': [list(r) for r in (win._query_profiles_rows() or [])]}


# ------------------------------------------------------------------ 錄音／錄影 (reuses the desktop tables, window thread)
def rec(win):
    try: win._experiment_refresh_tables(force=True)
    except Exception: pass
    clean = lambda rows: [list(r) for r in rows if any(str(x) for x in r)]
    return {'live_state': win.exp_live_state.text(), 'video_state': win.exp_video_state.text() if hasattr(win, 'exp_video_state') else '',
            'active': clean(win.exp_active.model.rows), 'done': clean(win.exp_done.model.rows),
            'log': win.exp_status_text.toPlainText()[-12000:]}


# ------------------------------------------------------------------ FLV 待處理
def flv_status(win):
    G = _G(win); J = G['_flv_jobs'](); lane = G['_HddLane'].get(); pub, fet = lane.waiting(); act = None
    if any(j.get('state') == 'convert' for j in J.values()):
        try: act = next((x for x in win._merge_estimates()['items'] if x.get('state') == 'active'), None)
        except Exception: act = None
    hdd, conv = win._flv_speeds()
    return {'jobs': {k: dict(v, text=win._flv_state_text(v, act)) for k, v in list(J.items())}, 'paused': lane.paused, 'cur': list(lane.cur) if lane.cur else None,
            'prog': dict(lane.prog) if lane.prog else None, 'pub': len(pub), 'fetch': len(fet), 'hdd': hdd, 'conv': conv, 'limit': lane.limit, 'io_pct': round(G['_IoThrottle'].get().pct), 'io_rate': round(G['_IoThrottle'].get().rate()), 'io_now': round(G['_IoThrottle'].get().speed()),
            'busy': G['_IoGovernor'].get().busy, 'ssd': str(win._ssd_dir()) if win._ssd_root() else '', 'ssd_free': win._ssd_free(),
            'ssd_off': '' if win._ssd_root() else ('設定裡關掉了' if not win.cfg('rec.ssd_stage') else '主程式和影片庫在同一顆硬碟')}


# ------------------------------------------------------------------ 連線診斷：快速檢查 / 完整診斷（網頁自己的一份）
def quick_start(win, users):
    G = _G(win); P = win.__dict__.setdefault('_webpc_quick', {})
    if P.get('running'): return False
    users = [str(u).lstrip('@') for u in users if str(u).strip()][:60]
    P.clear(); P.update(running=True, t=time.time(), lines=[f'=== 快速檢查 {len(users)} 位 · 同時 8 路 ==='], results=[])
    def work():
        from concurrent.futures import ThreadPoolExecutor, as_completed
        t0 = time.time()
        try:
            with ThreadPoolExecutor(max_workers=8) as ex:
                futs = {ex.submit(G['quick_live_probe_tl'], u, ''): u for u in users}
                for f in as_completed(futs):
                    try: r = f.result()
                    except Exception as e: r = {'user': futs[f], 'code': 'NET', 'reason': str(e), 'ms': 0, 'steps': []}
                    P['results'].append(r)
                    P['lines'].append(f"{win.QUICK_LABEL.get(r['code'], r['code']):<8} @{r['user']:<24} {r['ms']:>6.0f}ms  {r['reason']}")
                    P['lines'].append('      ' + ' | '.join(r.get('steps', [])))
            from collections import Counter
            cnt = Counter(r['code'] for r in P['results'])
            P['lines'].append(f"=== 完成：{len(P['results'])} 位 · 共 {time.time() - t0:.1f} 秒 · " + '，'.join(f"{win.QUICK_LABEL.get(k, k)} {v}" for k, v in cnt.most_common()) + ' ===')
        finally: P['running'] = False
    threading.Thread(target=work, daemon=True).start(); return True


def diag_start(win, users):
    G = _G(win); D = win.__dict__.setdefault('_webpc_diag', {})
    if D.get('worker') is not None and D['worker'].is_alive(): return False
    core = sys.modules.get('core')
    users = [str(u).lstrip('@') for u in users if str(u).strip()][:40]
    w = core.DiagnosticWorker(users, timeout=20, attempts=3, retry_delay=5)
    D.clear(); D.update(worker=w, lines=[f'=== TikLive Monitor V{G["APP_VERSION"]} DIAGNOSTIC（網頁版） ===', f'主播：{", ".join("@" + u for u in users)}'], t=time.time())
    w.start()
    def pump():
        while True:
            D['lines'].extend(w.poll(500))
            if not w.is_alive():
                D['lines'].extend(w.poll(2000)); D['lines'].append('=== DIAGNOSTIC COMPLETE ==='); break
            time.sleep(0.3)
    threading.Thread(target=pump, daemon=True).start(); return True


# ------------------------------------------------------------------ 網路用量 / 升級資訊
def net(win):
    from datetime import date
    t = date.today(); wd = '一二三四五六日'; days = []
    for i in range(31):
        d = t - timedelta(days=i); v = (list(getattr(win, '_net_days', {}).get(d.isoformat(), [])) + [0, 0, 0])[:3]
        days.append([f'{d:%m-%d}（{wd[d.weekday()]}）'] + v)
    return {'periods': [[n] + list(v) for n, v in win._net_period_totals()], 'days': days}


def changelog(win):
    try: log = json.loads((win._app_code_dir() / 'CHANGELOG.json').read_text(encoding='utf-8-sig'))
    except Exception: log = []
    try: log.sort(key=lambda e: win._version_tuple(str(e.get('version'))), reverse=True)
    except Exception: pass
    try: seen = win._chv_seen()                                            # V0.7.42.042 上次看到哪一版（之後的標 🆕）
    except Exception: seen = ''
    return {'current': _G(win)['APP_VERSION'], 'items': log, 'seen': seen}


# ------------------------------------------------------------------ router: rest = 'api/pc/...'
def route(win, sock, method, rest, q, body):
    G = _G(win); name = rest[len('api/pc/'):]
    J = lambda o: _send(win, sock, o)
    if name == 'state': J(state(win)); return True
    if (name.startswith('hl/') or name.startswith('reel/')) and win.cfg('hl.pause'):    # V0.7.42.050 精選暫停：精選、每日精選影片、分享全部回「暫停中」
        J({'ok': False, 'off': True, 'segs': [], 'message': '精選目前暫停中（先處理 FLV 轉檔與搬檔）'}); return True
    if name == 'mini': J(win._mini_stats()); return True
    if name.startswith('gfx'):                                                # V0.6.46 送禮動畫：目錄／圖示／自備動畫檔
        if gfx_route(win, sock, method, name, q, body): return True
    if name == 'streamer/purge_info':                                    # V0.6.21 刪除主播（全部）：先看會刪掉什麼
        u = q.get('u', ''); _bg(win, sock, lambda: win._purge_info(u)); return True
    if name == 'issues': J(win._issues_info()); return True
    if name == 'cg': J(win._cg_info()); return True                         # V0.6.47 連線管控
    if name == 'cg/roster': J(win._roster_review()); return True            # V0.6.47 主播縮編建議               # V0.6.28 LOG 與問題：自我檢查、網路狀態、自動處理紀錄、異常
    if name == 'logx/list': J({'items': win._logx_list(), 'now': time.time()}); return True           # V0.6.23 匯出 LOG
    if name == 'logx/make':
        now = time.time(); t1 = float(q.get('to') or now); t0 = float(q.get('from') or (t1 - float(q.get('min') or 30) * 60))
        _bg(win, sock, lambda: win._logx_build(t0, t1)); return True
    if name == 'logx/dl':
        f = Path(win._logx_dir()) / Path(str(q.get('f') or '')).name
        if not re.fullmatch(r'TikLive_LOG_[\w\-]+\.zip', f.name) or not f.exists():
            J({'ok': False, 'message': '找不到這個檔案'}, ); return True
        from urllib.parse import quote
        win._phone_send(sock, '200 OK', f.read_bytes(), 'application/zip', extra=f"Content-Disposition: attachment; filename=\"{f.name}\"; filename*=UTF-8''{quote(f.name)}\r\n")
        return True
    if name == 'streamer/media_info':                                    # V0.6.22 刪除選單：這場影片／全部影片／全部紀錄
        u = q.get('u', ''); sid = int(q.get('sid', '0') or 0); _bg(win, sock, lambda: win._media_info(u, sid)); return True
    if name == 'streamer/purge_status':
        st = dict(win._purge_state()); st.pop('t0', None); J(st); return True          # V0.6.17 歷史紀錄右上角的電腦數值
    if name == 'sess':
        info = _live_info(win, q); qq = dict(q); _bg(win, sock, lambda: sess(win, qq, info)); return True
    if name == 'sessions': uf = q.get('u', ''); sq = q.get('q', ''); sc = q.get('cat', ''); _bg(win, sock, lambda: sessions(win, uf, sq, sc)); return True
    if name == 'hostrank' and method == 'GET':                           # TK_V0.9.56 主播收禮排行（只讀）
        _bg(win, sock, lambda: win._hosts_rank(q.get('sort', 'dia'), q.get('q', ''), q.get('scope', 'all'), q.get('min', 0))); return True
    if name == 'gifters':
        if 'n' in q or 'off' in q or 'q' in q or 'sort' in q:       # V0.6.17 分頁：一次 500 位，排序在資料庫做，搜尋找全部
            qq = dict(q)
            _bg(win, sock, lambda: (lambda r: dict(r, rows=[list(x) for x in r['rows']]))(win._gifters_page(qq.get('off', 0), qq.get('n', 500), qq.get('sort', 'dia'), qq.get('desc', '1') != '0', qq.get('q', ''), qq.get('scope', 'all'), qq.get('min', 0))))
            return True
        _bg(win, sock, lambda: gifters(win)); return True
    if name == 'gifter':
        u = q.get('u', '')
        if q.get('names') == '1': _bg(win, sock, lambda: {'u': u, 'names': win._gifter_names(u)}); return True
        _bg(win, sock, lambda: gifter(win, u)); return True
    if name == 'profiles': _bg(win, sock, lambda: profiles(win)); return True
    if name == 'uact':                                                   # V0.6.52 使用者全部活動
        u = q.get('u', ''); k = q.get('k', 'comments'); off = int(q.get('off', '0') or 0); n = int(q.get('n', '500') or 500)
        _bg(win, sock, lambda: win._user_activity(u, k, off, n)); return True
    if name == 'uact/sum':
        u = q.get('u', ''); _bg(win, sock, lambda: win._user_activity_sum(u)); return True
    if name == 'uact/export':                                            # 給 AI 分析的純文字檔
        u = q.get('u', '')
        def work():
            try:
                txt, S = win._user_export_text(u); body = txt.encode('utf-8-sig')
                fn = re.sub(r'[^\w.\-]+', '_', f'TikLive_使用者_{S.get("nick") or u}_{u}.txt')[:120]
                from urllib.parse import quote
                win._ui_call.emit(lambda b=body, f=fn: win._phone_send(sock, '200 OK', b, 'text/plain; charset=utf-8', extra=f"Content-Disposition: attachment; filename=\"export.txt\"; filename*=UTF-8''{quote(f)}\r\n"))
            except Exception as ex:
                win._ui_call.emit(lambda m=str(ex): _send(win, sock, {'ok': False, 'message': m}))
        threading.Thread(target=work, name='TikLiveUserExport', daemon=True).start(); return True
    if name == 'stt': J(win._stt_info(int(float(q.get('since', '0') or 0)))); return True          # V0.6.52 語音轉字幕（BETA）
    if name == 'stt/sessions': sq = q.get('q', ''); _bg(win, sock, lambda: win._stt_sessions(sq)); return True
    if name == 'stt/sub':
        sid = int(q.get('id', '0') or 0); v = str(q.get('v', '') or ''); _bg(win, sock, lambda: win._stt_sub(sid, v)); return True
    if name == 'stt/vers':                                               # V0.6.81 同一場的字幕版本
        sid = int(q.get('id', '0') or 0); _bg(win, sock, lambda: {'sid': sid, 'vers': G['_stt_versions'](sid)}); return True
    if name == 'stt/srt':
        sid = int(q.get('id', '0') or 0); f = G['_stt_subs_dir']() / f'{sid}.srt'
        if not sid or not f.exists(): win._phone_send(sock, '404 Not Found', 'not found'); return True
        win._phone_send(sock, '200 OK', f.read_bytes(), 'application/x-subrip; charset=utf-8', extra=f'Content-Disposition: attachment; filename="TikLive_{sid:05d}.srt"\r\n')
        return True
    if name == 'sanom': J(win._sanom_info()); return True                    # V0.6.53 場次時長異常
    if name == 'novideo': ro = win._roster_ids(); _bg(win, sock, lambda: win._novideo_info(ro)); return True      # V0.6.59 只錄聲音的主播
    if name == 'edit/all' and method == 'GET':                           # TK_V0.9.16 所有剪好的片段（只讀）
        so_ = q.get('sum') == '1'; _bg(win, sock, lambda: win._edit_all(so_)); return True
    if name == 'diag/vb': J(win._diag_vb()); return True                  # TK_V0.9.09 清單卡在哪（只讀）
    if name == 'diag/mem' and method == 'GET': _bg(win, sock, win._mem_diag); return True     # TK_V0.9.32 主程式記憶體用在哪（只讀）
    if name == 'vb/kinds' and method == 'GET':                           # TK_V0.9.80 檔案總管四種：數量／大小（只讀）
        _bg(win, sock, lambda: win._vb_kinds()); return True
    if name == 'vb':                                                     # V0.6.60 影片快速瀏覽
        qq = dict(q); us = [x for x in str(qq.get('us', '')).split(',') if x.strip()]
        if qq.get('vg') == '1':                                           # V0.7.28 檔案總管：記住排序（背景照這個順序先做預覽圖）
            try: win._vgi_pref(qq.get('order', 'new'), qq.get('cat', ''), qq.get('skiplv') == '1'); win._vgi_touch()
            except Exception: pass
        _bg(win, sock, lambda: (lambda r_: (win._vg_ready_rows(r_.get('rows') or []) if qq.get('pr') == '1' else None, win._vg_edit_counts(r_.get('rows') or []) if qq.get('ne') == '1' else None, r_)[2])(win._vb_kind_wrap(win._vb_list(qq.get('q', ''), qq.get('cat', ''), us or None, qq.get('order', 'new'), qq.get('hidenv') == '1'), qq.get('kind', ''), qq.get('order', 'new')))); return True   # TK_V0.9.08 回到 0.8.97 的載入方式（直接算；索引已經改成只看有變動的資料夾） pr=1：每場預覽圖做好幾成
    if name == 'snap/info' and method == 'GET':                          # V0.7.09 照片：版面（幾列×幾欄）、能不能重新截圖、重新截圖的進度、最新清單
        sid = int(q.get('sid', '0') or 0)
        def si():
            try: live = float(win._web_replay_files(sid)[0] or 0)          # 跟回放同一個開播時間
            except Exception: live = 0
            try: L = [[round(t - live, 1), n] for t, n, _p in win._snap_list(sid)]
            except Exception: L = []
            st = dict(win._shot_regen_state().get(sid) or {})
            if st.get('pick'):                                             # TK_V0.9.91 等你挑的：每張開播第幾秒
                PL = []
                for n_ in st['pick']:
                    m_ = win._SNAP_RE.match(n_)
                    try: PL.append([round(datetime.strptime(m_.group(1) + m_.group(2), '%Y%m%d%H%M%S').timestamp() - live, 1), 'pk_' + n_])
                    except Exception: pass
                if win._shot_pick_dir(sid).is_dir(): st['pickL'] = PL
                st.pop('pick', None)
            try: u = str((win._web_db('SELECT username FROM sessions WHERE id=?', (sid,)) or [['']])[0][0] or '')
            except Exception: u = ''
            return {'ok': True, 'sid': sid, 'u': u, 'layout': win._shot_layout(sid), 'mp4': bool(win._shot_full_mp4(sid)[0]), 'mp4why': win._shot_full_mp4(sid)[1], 'regen': st, 'snaps': L}
        _bg(win, sock, si); return True
    if name == 'shp' and method == 'GET': _bg(win, sock, win._shp_info); return True       # V0.7.06 批量截 20 張
    if name == 'bg/status' and method == 'GET': _bg(win, sock, win._bg_status); return True     # V0.6.92 後台狀態
    if name == 'lv/rows' and method == 'GET': _bg(win, sock, win._lv_rows); return True       # V0.6.91 等級整理
    if name == 'prof' and method == 'GET':                               # V0.7.42.008 主播特性
        try: dd = int(q.get('days') or 30)
        except Exception: dd = 30
        _bg(win, sock, lambda: _prof_plus(win, win._prof_build(max(7, min(90, dd)), bool(q.get('f')) and time.time() - float(win.__dict__.get('_prof_ft', 0) or 0) > 60 and not win.__dict__.__setitem__('_prof_ft', time.time())))); return True   # 強制重算最多 1 分鐘一次
    if name == 'reel/info' and method == 'GET': _bg(win, sock, lambda: win._reel_info(str(q.get('d') or ''))); return True       # V0.7.42.007 每日精選影片
    if name == 'reel/file' and method == 'GET':
        p_ = win._reel_path(str(q.get('d') or ''))
        fq_ = str(q.get('f') or '')                                            # V0.7.42.035 收藏影片指定檔名（播放中重新做好一支也不會換檔）
        if str(q.get('d') or '') == 'fav' and re.fullmatch(r'fav_\d{8}_\d{4}\.mp4', fq_): p_ = win._reel_dir() / fq_
        if not (re.fullmatch(r'\d{4}-\d{2}-\d{2}', str(q.get('d') or '')) or str(q.get('d') or '') == 'fav') or not p_.exists(): win._phone_send(sock, '404 Not Found', 'not found'); return True   # V0.7.42.034 fav
        win._web_send_file(sock, p_, 'video/mp4'); return True                # V0.7.42.016 在畫面執行緒送（Qt 的連線只能在這裡用）
    if name == 'phr/usb' and method == 'GET': J(win._phr_usb_info()); return True      # TK_V0.9.90 外接硬碟有新的手機錄屏（只讀、讀快取）
    if name == 'yt/auth' and method == 'GET': J(win._yt_auth_info()); return True      # TK_V0.9.86 開頁面檢查 YouTube 授權快到期（只讀、很輕）
    if name == 'yt/info' and method == 'GET': _bg(win, sock, win._yt_info); return True             # V0.7.42.005 YouTube 上傳
    if name == 'ytc/info' and method == 'GET': J(win._ytc_info()); return True        # V0.8.24
    if name == 'cul/info' and method == 'GET': J(win._cul_info()); return True        # V0.8.25 🌐 Chrome 上傳限速
    if name == 'hl/day' and method == 'GET': _bg(win, sock, lambda: win._hl_day(q.get('d', ''))); return True     # V0.7.42.002 ✨ 精選
    if name == 'hl/fb' and method == 'GET' and str(q.get('k') or '') == 'seen':   # V0.7.42.019 開始播＝看過（只記場次和秒數）
        sid_, a_ = q.get('sid') or 0, q.get('a') or -1                 # V0.7.42.020 背景做（不卡畫面）；只收真的有的片段
        _bg(win, sock, lambda: win._hl_seen(sid_, a_)); return True
    if name == 'hl/fb' and method == 'GET':                              # V0.7.42.011 看完／跳掉（只記次數，給精選排序用）
        J(win._hl_fb(str(q.get('u') or ''), [x for x in str(q.get('t') or '').split(',') if x][:10], str(q.get('k') or ''))); return True
    if name == 'hl/info' and method == 'GET': J(win._hl_info()); return True
    if name == 'disk/eta' and method == 'GET':                            # V0.7.42.022 硬碟幾天會滿（背景算：建議要讀 MP4 清單）
        _bg(win, sock, win._dkf_info); return True
    if name == 'soon' and method == 'GET':                                # V0.7.42.021 接下來幾小時可能開播（只讀記憶體）
        try: hh_ = int(q.get('h') or 3)
        except Exception: hh_ = 3
        J(win._soon(hh_)); return True
    if name == 'hl/sess' and method == 'GET':
        try: sid_ = int(q.get('sid') or 0)
        except Exception: sid_ = 0
        _bg(win, sock, lambda: {k: v for k, v in (win._hl_get(sid_) or {'segs': []}).items() if k != '_vis'}); return True
    if name == 'hl/share/st' and method == 'GET': J(win._shr_info()); return True                    # V0.7.42.038
    if name == 'hl/share/file' and method == 'GET':
        p_ = win._shr_path(str(q.get('f') or ''))
        if not p_: win._phone_send(sock, '404 Not Found', 'not found'); return True
        win._web_send_file(sock, p_, 'video/mp4'); return True
    if name == 'weekly/list' and method == 'GET': _bg(win, sock, win._wkr_list); return True          # V0.7.42.036 每週報告
    if name == 'weekly/get' and method == 'GET':
        w_ = str(q.get('w') or ''); _bg(win, sock, lambda: win._wkr_get(w_)); return True
    if name == 'smart/sum' and method == 'GET':                          # V0.7.42.026 智慧功能狀態卡（只讀、背景）
        _bg(win, sock, win._smt_sum); return True
    if name == 'lend' and method == 'GET': _bg(win, sock, win._lend_info); return True       # V0.8.12 借用空間（只讀）
    if name == 'emg' and method == 'GET': _bg(win, sock, win._emg_info); return True       # V0.8.04 🚨 緊急處理（只讀）
    if name == 'exp/list' and method == 'GET': _bg(win, sock, win._exp_list); return True        # TK_V0.8.18.002 🧪 實驗工作區（只讀）
    if name == 'rv/list' and method == 'GET':                             # V0.8.13 🗂 主播審核（只讀）
        ro_ = win._roster_ids(); _bg(win, sock, lambda: win._rv_list(ro_)); return True
    if name == 'rv/tl' and method == 'GET':                               # V0.8.13 這位主播每場每 2 分鐘一張（只讀，只用已經做好的預覽圖）
        u_ = str(q.get('u', '') or ''); st_ = q.get('step', '120')
        def tl_():
            r = win._rv_tl(u_, step=st_)
            return dict(r, sessions=[{k: v for k, v in x.items() if k != 'p'} for x in (r.get('sessions') or [])]) if isinstance(r, dict) else r
        _bg(win, sock, tl_); return True
    if name == 'rv/pre' and method == 'GET':                              # V0.8.14 預先讀取：照清單順序先讀好（只在記憶體排順序，不改任何資料）
        qs_ = [x for x in str(q.get('q', '') or '').split(',') if x.strip()]
        try: J(dict(win._rv_pre_set(qs_ + win._roster_ids()), ok=True))
        except Exception as ex: J({'ok': False, 'message': str(ex)})
        return True
    if name == 'rv/batch' and method == 'GET':                            # V0.8.15 一次拿一批預覽圖（只讀已經做好的）
        ks_ = [x for x in str(q.get('k', '') or '').split(',') if x.strip()][:40]; _bg(win, sock, lambda: win._rv_batch(ks_)); return True
    if name == 'rv/img' and method == 'GET':                              # V0.8.13 讀已經做好的預覽圖／截圖（不產生新的）
        k_ = str(q.get('k', '') or '')
        def work():
            try:
                pp = win._rv_img_path(k_); data = pp.read_bytes() if pp is not None else None
            except Exception: data = None
            def send(b=data):
                if not b: win._phone_send(sock, '404 Not Found', 'not found'); return
                try: win._phone_send(sock, '200 OK', b, 'image/jpeg', cache=7 * 86400)
                except Exception: pass
            win._ui_call.emit(send)
        threading.Thread(target=work, name='TikLiveRvImgWeb', daemon=True).start(); return True
    if name == 'cg/rescue' and method == 'GET':                          # V0.7.42.044 漏錄補救（只讀、背景）
        try: dd = int(q.get('days') or 14)
        except Exception: dd = 14
        _bg(win, sock, lambda: win._rsq_info(max(1, min(60, dd)))); return True
    if name == 'cg/today' and method == 'GET':                           # V0.7.42.024 今天漏開頭（只讀資料庫）
        _bg(win, sock, win._rec_today); return True
    if name == 'cg/review' and method == 'GET':                          # V0.7.42.001 錄製檢討
        try: dd = int(q.get('days') or 14)
        except Exception: dd = 14
        _bg(win, sock, lambda: win._rec_review(max(1, min(60, dd)))); return True
    if name == 'lv/sum' and method == 'GET': _bg(win, sock, win._lv_sum); return True        # V0.7.37 上面「分類」浮窗
    if name == 'lv/status' and method == 'GET':
        st = win._lv_state(); J({k: (list(v) if isinstance(v, list) else v) for k, v in st.items()}); return True
    if name == 'vb/thumb' and method == 'GET':                           # V0.6.90 影片快速瀏覽的縮圖時間軸
        sid = int(q.get('sid', '0') or 0); k_ = int(q.get('k', '0') or 0); t_ = int(float(q.get('t', '0') or 0))
        def work():
            try:
                pv = win._vb_path(sid, k_, cached=True) or win._vb_path(sid, k_)
                pp = win._edit_thumb(sid, pv.name, t_) if pv is not None else None
            except Exception: pp = None
            def send(p=pp):
                if p is None or not p.exists(): win._phone_send(sock, '404 Not Found', 'not found'); return
                try: win._phone_send(sock, '200 OK', p.read_bytes(), 'image/jpeg', cache=86400)
                except Exception: win._phone_send(sock, '404 Not Found', 'not found')
            win._ui_call.emit(send)
        threading.Thread(target=work, daemon=True).start(); return True
    if name == 'vg/info' and method == 'GET':                            # V0.6.98 影片快速瀏覽 v2（格狀）
        sid = int(q.get('sid', '0') or 0); _bg(win, sock, lambda: win._vg_info(sid)); return True
    if name == 'vg/ping':                                                 # V0.7.28 檔案總管開著：背景先別做預覽圖（V0.7.32 改成照清單順序做）
        win._vgi_touch()
        qs = [int(x) for x in str(q.get('q', '') or '').split(',') if x.strip().isdigit()]
        if qs:                                                            # TK_V0.9.08 在背景做（不讓網頁伺服器等）
            def _pg(qs=qs):
                try: win._vgi_fxq_set(qs); win._vgi_tick()
                except Exception: pass
            threading.Thread(target=_pg, name='TikLiveVgPing', daemon=True).start()
        J({'ok': True}); return True
    if name == 'vg/done':                                                 # V0.7.30 這場看完／預載完：檢查 30 秒預覽圖夠不夠，夠就打勾
        sid_ = int(q.get('sid', '0') or 0); _bg(win, sock, lambda: win._vgi_check(sid_)); return True
    if name == 'vg/dups' and method == 'GET':                            # V0.7.35 預覽圖連續 3 張以上一模一樣（MP4 後面跳不過去）
        sid_ = int(q.get('sid', '0') or 0); _bg(win, sock, lambda: win._vg_dups(sid_)); return True
    if name == 'vg/pv' and method == 'GET':                               # V0.7.28 清單左邊的「預覽圖做好了沒」
        try: J({'ok': True, 'pv': {str(k): v for k, v in win._vgi_pv().items()}})
        except Exception: J({'ok': False}); return True
        return True
    if name == 'vg/batch' and method == 'GET':                           # V0.7.33 做好的縮圖一次拿一批（捲動更順）
        sid_ = int(q.get('sid', '0') or 0); h_ = int(q.get('h', '360') or 360); ts_ = [x for x in str(q.get('ts', '') or '').split(',') if x.strip()]
        _bg(win, sock, lambda: win._vg_batch(sid_, ts_, h_)); return True
    if name == 'vg/s2' and method == 'GET':                               # TK_V0.8.34.017 這場有沒有每 2 秒圖（只讀）
        sid_ = int(q.get('sid', '0') or 0); _bg(win, sock, lambda: win._vg_s2_info(sid_)); return True
    if name == 'vg/thumb' and method == 'GET':
        sid = int(q.get('sid', '0') or 0); t_ = float(q.get('t', '0') or 0); h_ = int(q.get('h', '360') or 360); p_ = int(q.get('p', '0') or 0); s_ = int(q.get('s', '0') or 0)
        nr_ = max(0, min(60, int(q.get('near', '0') or 0)))                   # TK_V0.8.18.007 精選卡片：附近有做好的就用
        _img_bg(win, sock, lambda: win._vg_thumb(sid, t_, 720 if h_ >= 720 else 360 if h_ >= 360 else 240, p_, s_, nr_), 60 * 86400); return True
    if name == 'vg/sheetinfo' and method == 'GET':                        # TK_V0.8.88 預覽圖大張（只讀）
        sid_ = int(q.get('sid', '0') or 0); _bg(win, sock, lambda: win._vg_sheet_info(sid_)); return True
    if name == 'feat' and method == 'GET': _bg(win, sock, win._feat); return True     # TK_V0.8.93 精選／審核開關（只讀）
    if name == 'vg/sheetpre' and method == 'GET':                          # TK_V0.8.93 連續分級：接下來的幾場大圖先拼好（只寫 SSD 快取）
        try: qs_ = [int(x) for x in str(q.get('q', '') or '').split(',') if x.strip().isdigit()][:30]   # V1.1.44 12 → 30 場
        except Exception: qs_ = []
        _bg(win, sock, lambda: win._vg_sheet_pre(qs_)); return True
    if name == 'vg/cover' and method == 'GET':                            # TK_V0.8.89 連續分級的小圖（只讀）；TK_V0.9.12 直接從預覽圖資料夾挑一張
        sid_ = int(q.get('sid', '0') or 0); _img_bg(win, sock, lambda: win._vg_cover_fast(sid_), 86400); return True
    if name == 'vg/sheet' and method == 'GET':
        sid_ = int(q.get('sid', '0') or 0); ri_ = int(q.get('ri', '0') or 0); si_ = int(q.get('i', '0') or 0)
        _img_bg(win, sock, lambda: win._vg_sheet(sid_, ri_, si_), lambda p: (lambda m_: 30 * 86400 if m_ and m_.group(1) == m_.group(2) else 120)(re.search(r'_(\d+)of(\d+)_', p.name))); return True
    if name == 'tkd' and method == 'GET':                                    # TK_V0.8.79 📥 TKDownloader（只讀）；TK_V1.0.82 src=ig → IGDownloader
        s_ = 'ig' if q.get('src') == 'ig' else 'tk'; _bg(win, sock, lambda: win._tkd_list(s_)); return True
    if name == 'tkd/thumb' and method == 'GET':
        f_ = str(q.get('f', '') or ''); s_ = 'ig' if q.get('src') == 'ig' else 'tk'; _img_bg(win, sock, lambda: win._tkd_thumb(f_, s_), 30 * 86400); return True
    if name == 'tkd/file' and method == 'GET':
        p_ = win._tkd_file(str(q.get('f', '') or ''), 'ig' if q.get('src') == 'ig' else 'tk')
        if p_ is None: win._phone_send(sock, '404 Not Found', 'not found'); return True
        ct_ = {'.mp4': 'video/mp4', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.png': 'image/png'}.get(p_.suffix.lower(), 'application/octet-stream')
        win._web_send_file(sock, p_, ct_, dlname=(p_.name if q.get('dl') == '1' else '')); return True
    if name == 'igck' and method == 'GET': J(win._ig_cookie_info()); return True     # TK_V1.0.80 只回「有沒有存」，不回內容
    if name == 'ttdl' and method == 'GET': J(win._ttdl_info()); return True      # TK_V0.8.34.044 影片下載進度（只讀）
    if name == 'htb' and method == 'GET':                                    # TK_V0.8.35 🖼 歷史縮圖（只讀）
        u_ = str(q.get('u', '') or ''); _bg(win, sock, lambda: win._htb_info(u_)); return True
    if name in ('htb/img', 'htb/full') and method == 'GET':
        u_ = str(q.get('u', '') or '').lstrip('@').lower(); sid_ = int(q.get('sid', '0') or 0); L_ = float(q.get('L', '0') or 0); dl_ = q.get('dl') == '1'
        def work():
            try:
                if name == 'htb/img': pp = win._htb_dir() / f'{u_}_grid.jpg' if re.fullmatch(r'[\w.\-]+', u_ or '') else None
                else: pp = win._htb_full(sid_, L_)
            except Exception: pp = None
            def send(p=pp):
                if p is None or not p.exists(): win._phone_send(sock, '404 Not Found', 'not found'); return
                try:
                    ex_ = f'Content-Disposition: attachment; filename="TikLive_{u_}_history.jpg"\r\n' if dl_ else ''
                    win._phone_send(sock, '200 OK', p.read_bytes(), 'image/jpeg', extra=ex_) if ex_ else win._phone_send(sock, '200 OK', p.read_bytes(), 'image/jpeg', cache=(0 if name == 'htb/img' else 30 * 86400))
                except Exception: win._phone_send(sock, '404 Not Found', 'not found')
            win._ui_call.emit(send)
        threading.Thread(target=work, daemon=True).start(); return True
    if name == 'diskhist' and method == 'GET':                          # V0.7.27 各槽容量變化曲線
        dy = float(q.get('days', '30') or 30); dv = str(q.get('d', '') or ''); _bg(win, sock, lambda: win._disk_hist(dy, dv)); return True
    if name == 'edit/badge' and method == 'GET': _bg(win, sock, win._edit_badge); return True      # V0.7.36 轉檔按鈕的小數字
    if name == 'edit/jobs' and method == 'GET': _bg(win, sock, win._edit_jobs); return True      # V0.7.20 「轉檔」浮動視窗
    if name == 'edit/list' and method == 'GET':                          # V0.6.98 回放頁左右滑的剪輯成品
        sid = int(q.get('sid', '0') or 0); _bg(win, sock, lambda: {'sid': sid, 'projects': win._edit_projects_cx(sid)}); return True
    if name == 'vb/note' and method == 'GET': J(win._snote_get(int(q.get('sid', '0') or 0))); return True      # V0.6.66 這場的備註
    if name == 'vb/stats':                                               # V0.6.66 清單像歷史紀錄：畫面上那幾場的鑽石、留言、錄到 %
        ids = [x for x in str(q.get('ids', '')).split(',') if x.strip()]; _bg(win, sock, lambda: win._vb_stats(ids)); return True
    if name.startswith('split/') and method == 'GET':                    # V0.6.74 批量剪輯
        if name == 'split/list':
            def lst():
                P = win._split_projects()
                for p in P:
                    p.pop('dirs', None)
                    for it in p['items']: it.pop('dir', None)
                return {'projects': P}
            _bg(win, sock, lst); return True
        if name == 'split/users': _bg(win, sock, win._split_users); return True
        if name == 'split/gifts':
            us = [x for x in str(q.get('users', '')).split(',') if x.strip()]; fr = q.get('from', ''); to = q.get('to', '')
            _bg(win, sock, lambda: win._split_gifts(us, fr, to)); return True
        if name == 'split/giftocc':                                      # TK_V0.9.66 長按禮物：這個禮物出現在哪幾場、第幾秒（只讀）
            us = [x for x in str(q.get('users', '')).split(',') if x.strip()]; fr = q.get('from', ''); to = q.get('to', ''); g_ = str(q.get('g', '') or '')
            _bg(win, sock, lambda: win._gift_occ(us, fr, to, g_)); return True
        if name == 'split/status':
            st = dict(win._split_state()); J({k: st.get(k) for k in ('running', 'pid', 'done', 'total', 'msg', 'result')}); return True
        if name == 'split/file':
            pid = str(q.get('id', '')); f = str(q.get('f', ''))
            def work():
                p = win._split_file(pid, f)
                def send(p=p):
                    if p is None or not p.exists(): win._phone_send(sock, '404 Not Found', 'not found'); return
                    win._web_send_file(sock, p, 'video/mp4')
                win._ui_call.emit(send)
            threading.Thread(target=work, daemon=True).start(); return True
    if name.startswith('vb/clip/') and method == 'GET':                  # V0.6.69 禮物片段
        sid = int(q.get('sid', '0') or 0)
        if name == 'vb/clip/list':
            _bg(win, sock, lambda: {'sid': sid, 'items': [{k: v for k, v in it.items() if k != 'path'} for it in win._clip_list(sid)], 'cfg': win._clip_cfg()}); return True
        if name == 'vb/clip/status':
            st = dict(win._clip_state()); J({k: st.get(k) for k in ('running', 'sid', 'done', 'total', 'msg', 'result', 'why')}); return True
        if name == 'vb/clip/cfg': J(win._clip_cfg()); return True
        if name == 'vb/clip/file':
            f = str(q.get('f', ''))
            def work():
                p = next((Path(it['path']) for it in win._clip_list(sid) if it['f'] == f), None)
                def send(p=p):
                    if p is None or not p.exists(): win._phone_send(sock, '404 Not Found', 'not found'); return
                    win._web_send_file(sock, p, 'video/mp4')
                win._ui_call.emit(send)
            threading.Thread(target=work, daemon=True).start(); return True
    if name in ('hist/strip', 'hist/thumb') and method == 'GET':          # V0.6.85 歷史回放的縮圖時間軸
        sid = int(q.get('sid', '0') or 0)
        if name == 'hist/strip':
            def strip():
                try: return {'ok': True, 'ranges': [r[:2] for r in win._hist_ranges(sid)]}
                except Exception as ex: return {'ok': False, 'ranges': [], 'message': str(ex)}
            _bg(win, sock, strip); return True
        t_ = float(q.get('t', '0') or 0)
        def work():
            try: pp = win._hist_thumb(sid, t_)
            except Exception: pp = None
            def send(p=pp):
                if p is None or not p.exists(): win._phone_send(sock, '404 Not Found', 'not found'); return
                try: win._phone_send(sock, '200 OK', p.read_bytes(), 'image/jpeg', cache=86400)
                except Exception: win._phone_send(sock, '404 Not Found', 'not found')
            win._ui_call.emit(send)
        threading.Thread(target=work, daemon=True).start(); return True
    if name.startswith('edit/') and method == 'GET':                     # V0.6.76 剪輯器
        if name == 'edit/info':
            sid = int(q.get('sid', '0') or 0)
            def info():
                d = win._edit_info(sid)
                for x in d.get('src') or []: x.pop('path', None)                # 網頁不用電腦上的路徑
                return d
            _bg(win, sock, info); return True
        if name == 'edit/status':
            st = win._edit_state()
            with st['lock']: cur = dict(st.get('cur') or {}); qq = [{'eid': j['eid'], 'sid': j['sid']} for j in st['q']]; dn = {k: dict(v) for k, v in st['done'].items()}
            J({'running': bool(st.get('running')), 'cur': cur, 'q': qq, 'done': dn}); return True
        if name == 'edit/src':                                           # 剪輯器播放：用檔名找（清單順序可能變了）
            sid = int(q.get('sid', '0') or 0); n_ = str(q.get('n', '')); px_ = str(q.get('p', '')) == '1'
            def work():
                pp = None
                if px_:                                                      # V0.6.85 流暢版
                    try:
                        x_ = win._edit_proxy_path(sid, n_) if n_ and '/' not in n_ and '\\' not in n_ and '..' not in n_ else None
                        if x_ is not None and x_.exists(): pp = x_
                    except Exception: pp = None
                for fr in ((False, True) if pp is None else ()):                                     # 先用快取（影片每一小段都會來要），找不到才重掃
                    try: pp = next((p_ for p_ in win._edit_src_files(sid, fresh=fr) if p_.name == n_ and p_.exists()), None)
                    except Exception: pp = None
                    if pp is not None: break
                def send(p=pp):
                    if p is None or not p.exists(): win._phone_send(sock, '404 Not Found', 'not found'); return
                    win._web_send_file(sock, p, 'video/quicktime' if p.suffix.lower() == '.mov' else 'video/mp4')
                win._ui_call.emit(send)
            threading.Thread(target=work, daemon=True).start(); return True
        if name == 'edit/mp4': _bg(win, sock, win._edit_mp4_rows); return True
        if name == 'edit/proxy':                                         # V0.6.85 流暢版（沒有就開始做）
            J(win._edit_proxy(int(q.get('sid', '0') or 0), str(q.get('n', '')), str(q.get('want', '1')) != '0')); return True
        if name == 'edit/thumb':                                         # V0.6.83 時間軸縮圖
            sid = int(q.get('sid', '0') or 0); n_ = str(q.get('n', '')); t_ = int(float(q.get('t', '0') or 0))
            def work():
                try: pp = win._edit_thumb(sid, n_, t_)
                except Exception: pp = None
                def send(p=pp):
                    if p is None or not p.exists(): win._phone_send(sock, '404 Not Found', 'not found'); return
                    try: win._phone_send(sock, '200 OK', p.read_bytes(), 'image/jpeg', cache=86400)
                    except Exception: win._phone_send(sock, '404 Not Found', 'not found')
                win._ui_call.emit(send)
            threading.Thread(target=work, daemon=True).start(); return True
        if name == 'edit/file':
            eid = str(q.get('id', '')); f = str(q.get('f', ''))
            def work():
                p = win._edit_file(eid, f)
                def send(p=p):
                    if p is None or not p.exists(): win._phone_send(sock, '404 Not Found', 'not found'); return
                    win._web_send_file(sock, p, 'video/mp4')
                win._ui_call.emit(send)
            threading.Thread(target=work, daemon=True).start(); return True
    if name == 'gift/meta' and method == 'GET': J(G['_gift_meta']()); return True          # V0.6.76 官方中文名稱＋互動禮物
    if name == 'vb/gifts':                                               # V0.6.66 影片快速瀏覽：這場的禮物（點了跳到影片那一刻）
        sid = int(q.get('sid', '0') or 0); _bg(win, sock, lambda: win._vb_gifts(sid)); return True
    if name == 'vb/file':
        sid = int(q.get('sid', '0') or 0); k = int(q.get('k', '0') or 0)
        def send(p):
            if p is None or not p.exists(): win._phone_send(sock, '404 Not Found', 'not found'); return
            win._web_send_file(sock, p, 'video/quicktime' if p.suffix.lower() == '.mov' else 'video/mp4')
        p = win._vb_path(sid, k, cached=True)                            # 不在畫面執行緒掃硬碟
        if p is not None: send(p); return True
        def work():
            try: pp = win._vb_path(sid, k)
            except Exception: pp = None
            win._ui_call.emit(lambda pp=pp: send(pp))
        threading.Thread(target=work, daemon=True).start(); return True
    if name == 'rec': J(rec(win)); return True
    if name == 'flv':
        act = set(win._active_rec_dirs()); _bg(win, sock, lambda: {'rows': win._flv_rows_scan(act), **flv_status(win)}); return True
    if name == 'flv/status': _bg(win, sock, lambda: flv_status(win)); return True          # TK_V0.8.34.019 背景算（會看硬碟上的 FLV）
    if name == 'net': J(net(win)); return True
    if name == 'changelog': J(changelog(win)); return True
    if name == 'quick': J(dict(win.__dict__.get('_webpc_quick') or {}, results=None)); return True
    if name == 'diag':
        D = win.__dict__.get('_webpc_diag') or {}; i = int(q.get('from', '0') or 0)
        J({'lines': (D.get('lines') or [])[i:], 'n': len(D.get('lines') or []), 'running': bool(D.get('worker') is not None and D['worker'].is_alive())}); return True
    if name == 'deep': J(win._deep_payload()); return True              # V0.6.04 深度連線測試
    if name == 'cleanup':                                                # V0.6.11 清理工具（只看；刪除要在電腦本機）
        def cl():
            r = win._clean_scan()
            return {'t': r['t'], 'txt_n': len(r['txt']), 'txt_b': sum(x['bytes'] for x in r['txt']), 'logs': r['logs'],
                    'ws': [{k: x[k] for k in ('dev', 'ip', 't0', 'last')} for x in r['ws']], 'av_n': len(r['avatars']), 'av_b': sum(a['bytes'] for a in r['avatars'])}
        _bg(win, sock, cl); return True
    if name == 'store/old' and method == 'GET':                          # TK_V0.9.55 🗃 舊的（還沒分資料夾）（只讀）
        fr_ = q.get('fresh') == '1'; _bg(win, sock, lambda: win._old_info(fr_)); return True
    if name == 'store/oldpv' and method == 'GET':                        # 10 秒一張的預覽：進度（只讀）
        f_ = str(q.get('id', '') or ''); _bg(win, sock, lambda: win._old_pv_info(f_)); return True
    if name == 'store/oldsheet' and method == 'GET':                     # 預覽大圖（只讀 SSD 快取，不碰影片）
        f_ = str(q.get('id', '') or ''); i_ = max(1, min(999, int(q.get('i', '1') or 1)))
        def gs_(f_=f_, i_=i_):
            d_ = win._old_pv_dir(f_); p2 = d_ / f's_{i_:03d}.jpg'
            return p2 if p2.exists() and ((d_ / 'done.json').exists() or (d_ / f's_{i_ + 1:03d}.jpg').exists()) else None
        _img_bg(win, sock, gs_, 3600); return True
    if name == 'phr' and method == 'GET':                                # TK_V0.9.78 手機錄屏：匯入／比對進度、清單（只讀）
        J(win._phr_info()); return True
    if name == 'phr/thumb' and method == 'GET':                          # TK_V0.9.87 待歸檔錄屏的 3 張小圖（只讀）
        id_ = str(q.get('id', '')); k_ = int(q.get('k', '0') or 0); _img_bg(win, sock, lambda: win._phr_thumb(id_, k_), cache=86400 * 30); return True
    if name == 'phr/file' and method == 'GET':                           # 手機錄屏檔（只讀，可以跳）
        p_ = win._phr_file(str(q.get('id', '')))
        if not p_: J({'ok': False, 'message': 'not found'}); return True
        win._web_send_file(sock, p_, 'video/mp4'); return True
    if name == 'sysfiles' and method == 'GET':                           # TK_V0.9.77 系統檔案清單（只讀，讀上次掃描的結果）
        d_ = str(q.get('d', '') or ''); _bg(win, sock, lambda: win._sysf_info(d_)); return True
    if name == 'nvtmp' and method == 'GET':                              # TK_V0.9.75 只錄聲音暫存 5 天：這場的狀態（只讀）
        sid_ = int(q.get('sid', '0') or 0); J(win._nvt_info(sid_)); return True
    if name == 'garr' and method == 'GET':                               # TK_V0.9.69 禮物陣列：這場的互動禮物（只讀）
        sid_ = int(q.get('sid', '0') or 0); _bg(win, sock, lambda: win._garr_list(sid_)); return True
    if name == 'g20' and method == 'GET':                                # TK_V1.0.73 GIF 進度＋做好的（只讀）
        _bg(win, sock, win._g20_info); return True
    if name == 'g20/file' and method == 'GET':
        nm_ = Path(str(q.get('f', '') or '')).name; p_ = win._g20_dir() / nm_
        if not nm_.lower().endswith('.gif') or not p_.is_file(): J({'ok': False, 'message': '找不到'}); return True
        win._web_send_file(sock, p_, 'image/gif', dlname=('' if q.get('pv') == '1' else nm_)); return True
    if name == 'mosaic' and method == 'GET':                             # TK_V0.9.64 動態拼貼進度（只讀）
        sid_ = int(q.get('sid', '0') or 0); _bg(win, sock, lambda: win._mos_info(sid_)); return True
    if name == 'mosaic/file' and method == 'GET':                        # 下載做好的動態拼貼
        nm_ = Path(str(q.get('f', '') or '')).name; p_ = win._mos_dir() / nm_
        if not nm_ or not p_.is_file(): J({'ok': False, 'message': '找不到'}); return True
        win._web_send_file(sock, p_, 'image/gif' if nm_.lower().endswith('.gif') else 'video/mp4', dlname=('' if q.get('pv') == '1' else nm_)); return True
    if name == 'store/orphans' and method == 'GET':                      # TK_V0.9.60 檔案總管冗餘檔模式（只讀）
        dd_ = q.get('days', '14'); fr_ = q.get('fresh') == '1'; _bg(win, sock, lambda: win._orph_list(dd_, fr_)); return True
    if name == 'store/orphhold' and method == 'GET': _bg(win, sock, win._orph_hold_info); return True   # TK_V1.0.20 暫放區有多少（只讀）
    if name == 'store/orphmove' and method == 'GET':
        _bg(win, sock, lambda: dict(win.__dict__.get('_orphmv') or {})); return True
    if name == 'store/oldfile' and method == 'GET':                      # 冗餘檔：播放（讀檔在背景執行緒，支援拖曳）
        p_ = (win.__dict__.get('_old_ids') or {}).get(str(q.get('id', '') or ''))
        if not p_: J({'ok': False, 'message': '找不到'}); return True
        win._web_send_file(sock, Path(p_), 'video/mp4'); return True
    if name == 'store/oldtidy' and method == 'GET':
        _bg(win, sock, lambda: {k: v for k, v in (win.__dict__.get('_oldtd') or {}).items() if k != 'res'}); return True
    if name == 'libtidy':                                                # V0.6.06 影片庫重整（只看）
        fresh = q.get('fresh') == '1'
        def lt():
            r = win.__dict__.get('_tidy_last') if not fresh else None
            if not r: r = win._tidy_scan()
            K = win.TIDY_KINDS
            rows = [{'kind': x['kind'], 'kname': K.get(x['kind'], (x['kind'],))[0], 'user': x.get('user', ''), 'name': x.get('name', ''), 'sid': x.get('sid', 0),
                     'src': x.get('src', ''), 'dst': x.get('dst', ''), 'note': x.get('note', ''), 'ok': x.get('ok', True)} for x in r.get('rows', [])]
            return {'t': r.get('t'), 'rows': rows, 'top': r.get('top', []), 'v2': r.get('v2'), 'root': r.get('root'), 'default_cat': r.get('default_cat')}
        _bg(win, sock, lt); return True
    if name == 'pup' and method == 'GET': _bg(win, sock, win._pup_info); return True          # TK_V0.9.94 手機上傳：清單、空間、最近的場次（只讀）
    if name == 'pup/ask' and method == 'GET': _bg(win, sock, win._pup_ask); return True       # 開 App 時問「有沒有錄」
    if name == 'sbk' and method == 'GET': _bg(win, sock, win._sbk_info); return True          # TK_V1.0.16 小檔備份清單（只讀）
    if name == 'hevc' and method == 'GET': _bg(win, sock, win._hevc_info); return True        # TK_V1.0.32 HEVC 試算結果（只讀）
    if name == 'hevc/img' and method == 'GET':                           # TK_V1.0.32 試算的比較圖（只認 orig／hevc）
        f_ = 'hevc.jpg' if q.get('f') == 'hevc' else 'orig.jpg'; p_ = win._hevc_path() / f_
        _img_bg(win, sock, lambda: p_ if p_.is_file() else None, cache=0); return True
    if name == 'dhist' and method == 'GET':                              # TK_V1.0.40 硬碟健康歷史（只讀）
        d_ = q.get('days', '30'); _bg(win, sock, lambda: win._dhh_info(d_)); return True
    if name == 'export/sessions' and method == 'GET':                   # TK_V1.0.51 場次表 CSV（只讀；背景做好再送）
        d_ = q.get('days', '30'); u_ = str(q.get('u', ''))
        def work_():
            try: fp_ = win._csv_sessions(d_, u_)
            except Exception as ex: win._ui_call.emit(lambda s=sock, m=str(ex): _send(win, s, {'ok': False, 'message': m})); return
            win._ui_call.emit(lambda s=sock, f=fp_: win._web_send_file(s, f, 'text/csv; charset=utf-8', touch=False, dlname=f.name))
        threading.Thread(target=work_, daemon=True, name='TikLiveCsv').start(); return True
    if name == 'daytl' and method == 'GET':                              # TK_V1.0.49 一天的時間軸（只讀）
        d_ = str(q.get('day', '')); _bg(win, sock, lambda: win._day_tl(d_)); return True
    if name == 'hostgift' and method == 'GET':                           # TK_V1.0.61 主播總覽：禮物（只讀）
        u_ = str(q.get('u', '')); _bg(win, sock, lambda: win._host_gift(u_)); return True
    if name == 'host' and method == 'GET':                               # TK_V1.0.42 主播總覽（只讀）
        u_ = str(q.get('u', '')); _bg(win, sock, lambda: win._host_info(u_)); return True
    if name == 'yt/holdlist' and method == 'GET': _bg(win, sock, win._yt_hold_list); return True   # TK_V1.0.97 隔離區抽查（只讀）
    if name == 'yt/holdfile' and method == 'GET':
        p_ = win._yt_hold_file(str(q.get('f', '') or ''))
        if p_ is None: win._phone_send(sock, '404 Not Found', 'not found'); return True
        win._web_send_file(sock, p_, 'video/mp4'); return True
    if name == 'rv/gdefs' and method == 'GET': J({'ok': True, 'gdefs': win._rv_gdefs()}); return True   # TK_V1.0.93（只讀、讀設定檔很快）
    if name == 'host/sum' and method == 'GET':                           # TK_V1.0.90 主播小視窗統計（只讀）
        u_ = str(q.get('u', '') or ''); _bg(win, sock, lambda: win._host_sum(u_)); return True
    if name == 'mig' and method == 'GET': J(win._mig_info()); return True
    if name == 'merge' and method == 'GET': J(win._web_merge_status()); return True
    if name == 'capsim' and method == 'GET': _bg(win, sock, lambda: win._capsim_data()); return True   # V1.1.42 容量預測（只讀）
    if name == 'rules/vals' and method == 'GET': J(win._rules_vals([s_ for s_ in str(q.get('k', '') or '').split(',') if s_][:60])); return True   # V1.1.35 規則頁的數字（只讀）                     # V1.1.25 合併重複場次（只讀）
    if name == 'merge/scan' and method == 'GET': J(win._web_merge_scan(force=bool(q.get('force')))); return True
    if name == 'cloud' and method == 'GET': J(win._cu_info()); return True      # V1.1.13 ☁ 雲端更新狀態（只讀）      # V1.1.07 搬硬碟狀態（只讀）
    if name == 'th' and method == 'GET':                                           # TK_V1.0.100 控溫狀態（只讀）
        J(dict(_th_mod(win)._Thermal.get().info(), ok=True)); return True
    if name == 'gpusd' and method == 'GET':                              # TK_V1.0.84 顯示卡供需（只讀）
        d_ = q.get('days', '14'); _bg(win, sock, lambda: win._gsd_info(d_)); return True
    if name == 'health' and method == 'GET':                             # TK_V1.0.69 一頁健檢（只讀）
        _bg(win, sock, win._health_page); return True
    if name == 'pfx' and method == 'GET': J(win._pfx_info_web()); return True          # V1.1.63 手機錄特效狀態（只讀）
    if name == 'pfx/gifts' and method == 'GET': J(win._pfx_gifts(q.get('sid', '0'), int(q.get('min', '10') or 10))); return True   # V1.1.66 這場送禮的人（只讀）
    if name == 'pfx/gtiles' and method == 'GET': J(win._pfx_gtiles(int(q.get('sid', '0') or 0), 'big' if q.get('mode') == 'big' else 'user', q.get('u', ''), int(q.get('min', '10') or 10))); return True   # V1.1.67 禮物格子（只讀）
    if name == 'pfx/has' and method == 'GET':                                    # V1.1.67 這場有沒有手機特效版（剪刀先選版本用）
        J({'ok': True, 'files': [Path(x['f']).name for x in win._pfx_idx() if str(x.get('sid')) == str(q.get('sid', '')) and Path(x['f']).is_file()]}); return True
    if name == 'pfx/shot' and method == 'GET':                                   # V1.1.69 手機最近一張畫面（只讀）
        p_ = win._pfx_shot_file()
        if p_ is None: win._phone_send(sock, '404 Not Found', 'not found'); return True
        win._web_send_file(sock, p_, 'image/jpeg' if p_.suffix == '.jpg' else 'image/png'); return True
    if name == 'pfx/thumbs' and method == 'GET': J(win._pfx_thumbs(q.get('i', '-1'))); return True   # V1.1.71 手機特效預覽圖（只讀）
    if name == 'pfx/thumb' and method == 'GET':
        p_ = win._pfx_thumb(q.get('i', '-1'), q.get('t', '0'))
        if p_ is None: win._phone_send(sock, '404 Not Found', 'not found'); return True
        win._web_send_file(sock, p_, 'image/jpeg'); return True
    if name == 'pfx/mix' and method == 'GET': J(win._mix_info(int(q.get('sid', '0') or 0))); return True   # V1.1.75 手機版合併（只讀）
    if name == 'pfx/gfile' and method == 'GET':
        p_ = win._pfx_gfile(q.get('f', ''))
        if p_ is None: win._phone_send(sock, '404 Not Found', 'not found'); return True
        win._web_send_file(sock, p_, 'video/mp4'); return True
    if name == 'pfx/file' and method == 'GET':
        p_ = win._pfx_file(q.get('i', '-1'))
        if p_ is None: win._phone_send(sock, '404 Not Found', 'not found'); return True
        win._web_send_file(sock, p_, 'video/mp4' if p_.suffix.lower() == '.mp4' else 'video/x-matroska'); return True
    if name == 'livenow' and method == 'GET':                            # TK_V1.0.38 開播提醒（只讀，很小）
        J(win._live_now()); return True
    if name == 'sttq' and method == 'GET':                               # TK_V1.0.46 字幕全文搜尋（只讀）
        q_ = str(q.get('q', '')); _bg(win, sock, lambda: win._sttx_find(q_)); return True
    if name == 'qs' and method == 'GET':                                 # TK_V1.0.35 快速找（只讀）
        q_ = str(q.get('q', '')); _bg(win, sock, lambda: win._qs(q_)); return True
    if name == 'actlog' and method == 'GET':                             # TK_V1.0.23 自動處理紀錄（只讀）
        c_ = str(q.get('cat', '')); q_ = str(q.get('q', '')); d_ = q.get('days', '3'); _bg(win, sock, lambda: win._act_log(c_, q_, d_)); return True
    if name == 'sbk/file' and method == 'GET':                           # TK_V1.0.16 下載備份（只收這個資料夾裡 TK_state_*.zip 的檔名）
        f_ = str(q.get('f', '')); p_ = win._sbk_dir() / f_
        if not re.fullmatch(r'TK_state_\d{8}_\d{6}\.zip', f_) or not p_.is_file(): J({'ok': False, 'message': '找不到這個備份'}); return True
        win._web_send_file(sock, p_, 'application/zip', dlname=f_); return True
    if name == 'pup/guess' and method == 'GET':                          # TK_V1.0.08 上傳前猜是哪一場（只讀）
        lm_ = q.get('lm', '0'); du_ = q.get('dur', '0'); u_ = q.get('u', ''); _bg(win, sock, lambda: win._pup_guess(lm_, du_, u_)); return True
    if method != 'POST': return False
    if name == 'pup/chunk':                                              # TK_V0.9.94 分塊上傳（原始資料；密碼在 X-Pw）
        hdr = getattr(sock, '_hdr', {}) or {}
        if not _pw_ok(win, sock, {'pw': str(hdr.get('x-pw', '') or q.get('pw', ''))}): return True
        iid_ = str(q.get('id') or ''); off_ = int(q.get('off') or 0); b_ = body
        _bg(win, sock, lambda: win._pup_chunk(iid_, off_, b_)); return True
    d = _body(body)
    # ---------- writes (web password when one is set)
    if not _pw_ok(win, sock, d): return True
    if name == 'pup/plan':
        fl_ = [x for x in (d.get('files') or []) if isinstance(x, dict)][:300]; _bg(win, sock, lambda: win._pup_plan(fl_)); return True
    if name == 'pup/start':
        J(win._pup_start(str(d.get('name') or ''), int(d.get('size') or 0), str(d.get('dest') or 'ssd'), str(d.get('u') or ''), bool(d.get('over')), float(d.get('lm') or 0))); return True
    if name == 'pup/hint': J(win._pup_hint(str(d.get('id') or ''), str(d.get('u') or ''))); return True
    if name == 'pup/cancel': J(win._pup_cancel(str(d.get('id') or ''))); return True
    if name == 'pup/none': J(win._pup_none([int(x) for x in (d.get('sids') or []) if str(x).isdigit()][:500])); return True
    if name == 'store/oldpv':                                            # TK_V0.9.55 開始做 10 秒一張的預覽（背景、一次一部）
        J(win._old_pv_start(str(d.get('id') or ''))); return True
    if name == 'store/oldtidy':                                          # 照影片庫重整整理選定的檔案（只搬移，有紀錄可還原）
        J(win._old_tidy_start([str(x) for x in (d.get('ids') or [])][:5000])); return True
    if name == 'store/oldauto':                                          # TK_V0.9.59 舊檔自動整理開關
        try: win.ui_settings.setValue('old_auto', '1' if d.get('on') else '0'); J({'ok': True, 'message': '自動整理：' + ('開' if d.get('on') else '關')})
        except Exception as ex: J({'ok': False, 'message': str(ex)})
        return True
    if name == 'phr/drives':                                             # TK_V0.9.78 手機錄屏：列出磁碟／資料夾（只讀，但要密碼）
        _bg(win, sock, lambda: win._phr_drives()); return True
    if name == 'phr/browse':
        p_ = str(d.get('path') or ''); _bg(win, sock, lambda: win._phr_browse(p_)); return True
    if name == 'phr/import':                                             # 選的檔排進限速複製
        J(win._phr_import([str(x) for x in (d.get('paths') or [])][:2000])); return True
    if name == 'phr/cfg':
        J(win._phr_cfg_set(d)); return True
    if name == 'phr/pick':
        J(win._phr_pick(str(d.get('id') or ''), int(d.get('sid') or 0))); return True
    if name == 'phr/mksess':                                             # TK_V0.9.79 沒有紀錄的手機錄屏：建成手機場次（P 編號）
        J(win._phr_mksess([str(x) for x in (d.get('ids') or [])][:500], str(d.get('u') or ''), bool(d.get('yt', True)))); return True
    if name == 'phr/usbimport':                                          # TK_V0.9.90 外接硬碟 TIKLIVE ScreenRecord Files 裡新的全部匯入
        J(win._phr_usb_import(str(d.get('root') or ''))); return True
    if name == 'phr/setu':                                               # TK_V0.9.90 未指定主播的手機場次：選主播
        J(win._phr_setu([str(x) for x in (d.get('ids') or [])][:2000], str(d.get('u') or ''))); return True
    if name == 'phr/sretry':
        J(win._phr_sess_retry(str(d.get('id') or ''))); return True
    if name == 'phr/retry':
        J(win._phr_retry(str(d.get('id') or ''))); return True
    if name == 'sysfiles':                                               # 重新掃描（背景、只讀）
        J(win._sysf_start(str(d.get('d') or ''))); return True
    if name == 'nvtmp':                                                  # 📌 留下／取消留下
        if d.get('ext'): J(win._nvt_extend(int(d.get('sid') or 0), d.get('ext'))); return True   # TK_V1.0.06 多留幾天
        J(win._nvt_keep(int(d.get('sid') or 0), bool(d.get('keep')))); return True
    if name == 'garr':                                                   # 禮物陣列：存爆點／前後秒數
        J(win._garr_save(d)); return True
    if name == 'igck':                                                   # TK_V1.0.80 存／刪 IG 登入 Cookie（要密碼的寫入）
        J(win._ig_cookie_set(d.get('v', ''))); return True
    if name == 'g20':                                                    # TK_V1.0.73 開始做 GIF（背景一次一件）
        J(win._g20_start(d)); return True
    if name == 'mosaic':                                                 # 開始做動態拼貼（背景一次一件）
        J(win._mos_start(d)); return True
    if name == 'store/orphmark':                                         # 冗餘檔：標 −2／+2／清除
        J(win._orph_mark(str(d.get('id') or ''), d.get('v'))); return True
    if name == 'store/orphpurge':                                        # TK_V1.0.20 永久刪除暫放區（sig 要跟看到的一樣）
        J(win._orph_hold_purge(str(d.get('sig') or ''))); return True
    if name == 'store/orphmove':                                         # 標 −2 的移到 _冗餘暫放（不刪）
        J(win._orph_move([str(x) for x in (d.get('ids') or [])][:5000])); return True
    if name == 'store/oldfix':                                           # 馬上跑一次分類整理
        try: win._cats_kick(0.2); J({'ok': True, 'message': '開始整理（背景），幾分鐘後重新整理看看'})
        except Exception as ex: J({'ok': False, 'message': str(ex)})
        return True
    if name == 'monitor':
        if d.get('on'):
            if not win.stream_list.count(): J({'ok': False, 'message': '請先新增至少一位主播。'}); return True
            win.start_monitor(auto=True); J({'ok': True})
        else: win.stop_monitor(); J({'ok': True})
        return True
    if name == 'streamer/priority':
        u = str(d.get('u') or '')
        if bool(d.get('on')) != (u in win.priority_streamers): win.toggle_priority_streamer(u); win.rebuild_streamer_manager_page()
        J({'ok': True, 'priority': u in win.priority_streamers}); return True
    if name == 'streamer/edit':
        old = str(d.get('old') or ''); uid = str(d.get('uid') or '').lstrip('@').strip(); nm = str(d.get('name') or '').strip()
        if not uid: J({'ok': False, 'message': '帳號不能為空白。'}); return True
        if not win._unique_streamer_username(uid, ignore=old): J({'ok': False, 'message': '這個 @帳號已經存在。'}); return True
        if not win._find_stream_item(old): J({'ok': False, 'message': '找不到這位主播，請重新整理'}); return True
        win.apply_streamer_edit(old, nm, uid, True, bool(d.get('priority'))); J({'ok': True}); return True
    if name == 'streamer/delete':
        u = str(d.get('u') or '')
        if not win._find_stream_item(u): J({'ok': False, 'message': '找不到這位主播'}); return True
        win._remove_streamer_from_roster(u); win._wd_log(f'網頁版刪除主播：@{u}'); J({'ok': True}); return True
    if name == 'streamer/order':
        ids = [str(x) for x in d.get('order') or []]
        if ids: win._apply_roster_order(ids)
        J({'ok': True}); return True
    if name == 'streamer/nick':
        u = str(d.get('u') or ''); win._nick_pending.add(u); win._fetch_nicknames([u], force=True); J({'ok': True}); return True
    if name == 'net/diag':                                               # V0.6.28 網路處理（手動）
        def nd():
            win._nf_act('手動按「診斷」', auto=False); return {'ok': True, 'diag': win._net_diag_run('手動')}
        _bg(win, sock, nd); return True
    if name == 'net/flushdns':
        def fd_():                                                        # TK_V0.8.34.019 ipconfig 最多等 15 秒：放背景，畫面不等
            try: ok, msg = win._net_flush_dns()
            except Exception as ex: ok, msg = False, str(ex)
            win._ui_call.emit(lambda ok=ok, msg=msg: win._nf_act(f'手動清 DNS 快取：{"成功" if ok else "失敗 " + msg}', auto=False))
            return {'ok': ok, 'message': msg}
        _bg(win, sock, fd_); return True
    if name == 'net/rebuild':
        n = win._net_rebuild_start('manual'); win._nf_act(f'手動重建這支程式的連線：{n} 位沒在直播的主播，每分鐘 12 位（直播中的不動）', auto=False)
        J({'ok': True, 'n': n, 'message': f'{n} 位會在接下來約 {max(1, -(-n // 12))} 分鐘內慢慢重建'}); return True
    if name == 'db/move':                                                # V0.6.40 資料庫立即搬到 C 槽 SSD／搬回資料硬碟（會重新啟動主程式）
        to = 'hdd' if str(d.get('to') or '') == 'hdd' else 'ssd'; B = win._dbloc_info()
        if B.get('same_drive'): J({'ok': False, 'message': '程式和資料在同一顆硬碟，不需要搬'}); return True
        win._ui_call.emit(lambda: win._dbmove_do(to, '網頁／手機按鈕'))
        J({'ok': True, 'message': '主程式幾秒後重新啟動，啟動時搬資料庫（大約 1～3 分鐘），完成後自動繼續監控'}); return True
    if name == 'app/restart':                                            # V0.6.27 遠端重新啟動主程式（要網頁密碼）
        w = win._cg_restart_warning() if hasattr(win, '_cg_restart_warning') else ''
        if w and not d.get('force'): J({'ok': False, 'guard': True, 'message': w + '\n\n還是要重新啟動嗎？'}); return True     # V0.6.47 重開沒有幫助時先提醒
        if w: win._wd_log('重新啟動主程式：網頁／手機看過「多半沒有幫助」的提醒仍決定重開')
        J({'ok': True, 'message': '主程式會在幾秒內關閉，大約 20 秒後自動重新開啟'})
        win._ui_call.emit(lambda: QTimer_single(win, 1500, lambda: win._restart_app_hard('網頁／手機要求')))
        return True
    if name == 'streamer/del_videos':                                    # V0.6.22 只刪影片（紀錄、錄音保留）
        J(win.delete_videos(str(d.get('u') or ''), int(d.get('sid') or 0), allow_fav=bool(int(d.get('sid') or 0)))); return True   # V0.7.42.035 指定那一場照刪；整位主播跳過 ⭐
    if name == 'streamer/purge':                                         # V0.6.21 刪除主播＋全部紀錄並移除監控
        J(win.purge_streamer(str(d.get('u') or ''))); return True
    if name == 'sessions/delete':
        ids = [int(x) for x in d.get('ids') or []]
        busy = win._busy_session_ids() & set(ids)
        if busy: J({'ok': False, 'message': '直播中／錄音中的場次不能刪除：' + '、'.join(f'#{i:05d}' for i in sorted(busy))}); return True
        ok = win.delete_sessions(ids, confirm=False); J({'ok': bool(ok) or ok is None, 'message': '背景刪除中（先備份資料庫），完成後清單會更新' if ok else '沒有刪（可能空間不夠備份或上一批還在處理）'}); return True
    if name == 'flv/go': J({'ok': True, 'n': win._flv_go(d.get('dirs') or [])}); return True
    if name == 'flv/cancel': J({'ok': True, 'n': win._flv_cancel(d.get('dirs') or None) or 0}); return True
    if name == 'flv/pause':
        lane = G['_HddLane'].get(); lane.set_paused(bool(d.get('on'))); J({'ok': True, 'paused': lane.paused}); return True
    if name == 'quick/start': J({'ok': quick_start(win, d.get('users') or [])}); return True
    if name == 'diag/start': J({'ok': diag_start(win, d.get('users') or [])}); return True
    if name == 'diag/stop':
        D = win.__dict__.get('_webpc_diag') or {}
        try: D['worker'].stop()
        except Exception: pass
        J({'ok': True}); return True
    if name == 'diskhelper':                                  # V0.6.02 硬碟溫度小工具（Windows 會在電腦上問一次管理員權限）
        ok, msg = win._disk_helper_install(bool(d.get('on', True))); J({'ok': ok, 'message': msg}); return True
    if name == 'deep/start':
        users = win._deep_targets() if d.get('all') else [str(x) for x in d.get('users') or []]
        J({'ok': True, 'n': win._deep_start(users)}); return True
    if name == 'deep/stop': G['_deep_state']()['stop'] = True; J({'ok': True}); return True
    if name == 'pwcheck': J({'ok': True}); return True
    if name == 'sanom/scan': J(win._sanom_scan()); return True
    if name == 'sanom/fix':
        sids = [int(x) for x in (d.get('sids') or []) if str(x).isdigit()][:2000]; _bg(win, sock, lambda: win._sanom_fix(sids)); return True
    if name == 'sanom/undo':
        sid = int(d.get('sid') or 0); _bg(win, sock, lambda: win._sanom_undo(sid)); return True
    if name == 'gift/ia':                                                # V0.6.76 標記／取消互動禮物（影片裡看得到動畫）
        g_ = str(d.get('g') or '').strip(); ok = G['_gift_ia_set'](g_, bool(d.get('on')), (bool(d.get('no')) if 'no' in d else None))
        if ok: win._wd_log(f'互動禮物：{"標記" if d.get("on") else ("確認不是" if d.get("no") else "取消")} {g_}')
        J({'ok': ok, 'meta': G['_gift_meta']()}); return True
    if name == 'edit/make': J(win._edit_make_bg(d)); return True
    if name == 'edit/sub': _bg(win, sock, lambda: win._edit_sub_save(int(d.get('sid') or 0), d.get('segs') or [])); return True               # V0.6.76 剪輯器
    if name == 'edit/fix': _bg(win, sock, lambda: win._edit_fix_add(str(d.get('id') or ''), str(d.get('f') or ''), force=bool(d.get('force')))); return True     # TK_V0.8.34.005 轉成手機能播的格式（要密碼）
    if name == 'hl/now': _bg(win, sock, lambda: win._hl_now(int(d.get('sid') or 0), d.get('next') or [])); return True     # TK_V0.8.34.017 這場先做每 2 秒圖（要密碼）
    if name == 'edit/del': _bg(win, sock, lambda: win._edit_delete(str(d.get('id') or ''), str(d.get('f') or ''))); return True
    if name == 'edit/delmp4': J(win._edit_del_mp4([int(x) for x in (d.get('sids') or []) if str(x).isdigit()])); return True
    if name == 'split/make': J(win._split_make_bg(d)); return True
    if name == 'split/cancel': win._split_state()['cancel'] = True; J({'ok': True, 'message': '會在這一段剪完後停下'}); return True
    if name == 'split/del':
        pid = str(d.get('id') or ''); fs = d.get('files'); fs = None if fs is None else [str(x) for x in fs][:5000]
        _bg(win, sock, lambda: win._split_delete(pid, fs)); return True
    if name == 'vb/clip/make':
        sid = int(d.get('sid') or 0)
        if d.get('cfg'): win._clip_set_cfg(d['cfg'])
        J(win._clip_make_bg(sid) if sid else {'ok': True, 'message': '設定已儲存'}); return True
    if name == 'vb/clip/cfg': J(dict(win._clip_set_cfg(d.get('cfg') or {}), ok=True)); return True
    if name == 'vb/clip/star': J(win._clip_star(int(d.get('sid') or 0), str(d.get('f') or ''), bool(d.get('on')))); return True
    if name == 'vb/clip/del':
        sid = int(d.get('sid') or 0); fs = [str(x) for x in (d.get('files') or [])][:5000]; _bg(win, sock, lambda: win._clip_delete(sid, fs)); return True
    if name == 'vb/note':
        try: J(win._snote_set(int(d.get('sid') or 0), d.get('text') if 'text' in d else None, d.get('level') if 'level' in d else 'keep', bool(d.get('auto'))))
        except Exception as ex: J({'ok': False, 'message': f'備註沒有存成功：{ex}'})
        return True
    if name == 'vb/del':
        sid = int(d.get('sid') or 0); _bg(win, sock, lambda: win._vb_delete(sid)); return True
    if name == 'snap/del': J(win._snap_delete(int(d.get('sid') or 0), str(d.get('name') or ''))); return True       # V0.6.93 回放時刪掉這一張截圖
    if name == 'bg/cancel': J(win._bg_cancel(d.get('key'), d.get('id'))); return True
    if name == 'lend/use': J(win._lend_use(d.get('d'))); return True                       # V0.8.12 借用空間（要密碼）
    if name == 'lend/stop': J(win._lend_stop()); return True
    if name == 'lend/snooze':
        try: h_ = max(0.25, min(24.0, float(d.get('h') or 1)))
        except Exception: h_ = 1.0
        win._lend_snooze = time.time() + h_ * 3600; J({'ok': True, 'message': f'{h_:g} 小時內不再提醒'}); return True
    if name == 'emg/set': J(win._emg_set(str(d.get('k') or ''), d.get('v'))); return True          # V0.8.04 緊急處理的開關（要密碼）
    if name == 'exp/set': J(win._exp_set(str(d.get('id') or ''), str(d.get('mode') or ''))); return True   # TK_V0.8.18.002 實驗切換（要密碼）
    if name == 'htb/save': J(win._htb_save(d.get('u'), d.get('items'), d.get('skip'))); return True     # TK_V0.8.35 🖼 歷史縮圖（要密碼）
    if name == 'htb/render': J(win._htb_render(d.get('u'))); return True
    if name == 'rv/order': J(win._rv_order(d.get('order'), d.get('base'), d.get('moved'), bool(d.get('unpin')))); return True     # TK_V0.8.34 主播審核：調整直播間序號（要密碼）
    if name == 'rv/gdefs': J(win._rv_gedit(d)); return True
    if name == 'mig/set': J(win._mig_set(d)); return True
    if name == 'cloud/set': J(win._cu_set(d)); return True
    if name == 'merge/run': J(win._web_merge_run(d)); return True
    if name == 'capsim/apply': J(win._capsim_apply(d)); return True
    if name == 'pfx/set': J(win._pfx_set(d)); return True                      # V1.1.63 手機錄特效（要密碼）
    if name == 'host/pause': J(win._host_pause(d.get('u'), bool(d.get('on')), src=str(d.get('src') or '網頁')[:20])); return True     # V1.1.45 ⏸ 暫停監控並封存／恢復（要密碼）                  # V1.1.42 容量預測套用（要密碼）
    if name == 'rules/set': J(win._rules_set(d)); return True                        # V1.1.35 規則頁改數字（要密碼）                    # V1.1.25 合併重複場次（要密碼）                      # V1.1.13 ☁ 雲端更新：檢查／更新／略過（要密碼）                      # V1.1.07 搬硬碟（要密碼）
    if name == 'th/alert':                                                         # TK_V1.0.100 解除斷電警報（要密碼）
        if str(d.get('op') or '') == 'clear': J(_th_mod(win)._Thermal.get().clear_alert()); return True
        J({'ok': False, 'message': '不認得'}); return True                        # TK_V1.0.93 等級設定（要密碼）
    if name == 'rv/set': J(win._rv_set(d.get('u'), d.get('g'))); return True                     # V0.8.13 主播審核：分級（要密碼）
    if name == 'rv/purge': J(win._rv_purge_start(str(d.get('only') or ''))); return True                                  # V0.8.13 處置 F（要密碼）
    if name == 'rv/purge_cancel': J(win._rv_purge_cancel()); return True
    if name == 'emg/gpu':                                                    # V0.8.04 重新檢查顯示卡（背景）
        threading.Thread(target=win._emg_gpu_diag, name='TikLiveGpuDiag', daemon=True).start(); J({'ok': True, 'message': '開始檢查顯示卡（約 10～30 秒）'}); return True
    if name == 'changelog/seen': J(win._chv_mark()); return True          # V0.7.42.042 版本說明看過了
    if name == 'hl/share':                                                # V0.7.42.038 分享這段（要密碼）：YouTube 網址或剪小 MP4
        sid_, a_, b_ = d.get('sid'), d.get('a'), d.get('b')
        _bg(win, sock, lambda: win._shr_make(sid_, a_, b_)); return True
    if name == 'hl/fav':                                                  # V0.7.42.032 ⭐ 我的最愛（要密碼）
        sid_, a_, on_, ks_ = d.get('sid'), d.get('a0'), bool(d.get('on')), d.get('ks') if isinstance(d.get('ks'), list) else None
        _bg(win, sock, lambda: win._hlf_set(sid_, a_, on_, ks_)); return True
    if name == 'hl/adj':                                                  # V0.7.42.027 精選片段前後微調（要密碼）
        sid_, a_, w_, dl_ = d.get('sid'), d.get('a0'), str(d.get('which') or ''), d.get('delta')
        _bg(win, sock, lambda: win._hla_set(sid_, a_, w_, dl_)); return True
    if name == 'hl/block': J(win._hl_block(str(d.get('kind') or ''), str(d.get('key') or ''), bool(d.get('on')))); return True     # V0.7.42.017 不要看這位／這一類
    if name == 'reel/build':
        dd = str(d.get('d') or '')
        J(win._reel_start(dd) if (re.fullmatch(r'\d{4}-\d{2}-\d{2}', dd) or dd == 'fav') else {'ok': False, 'message': '日期不對'}); return True   # V0.7.42.034 fav＝把收藏做成一支
    if name == 'yt/client': J(win._yt_client_set(d.get('id'), d.get('secret'))); return True       # V0.7.42.005 YouTube（要網頁密碼）
    if name == 'yt/link': _bg(win, sock, win._yt_link_start); return True       # V0.7.42.016 連 Google 可能慢：背景做，不卡畫面
    if name == 'yt/unlink': _bg(win, sock, win._yt_unlink); return True
    if name == 'yt/on': J(win._cfg_set_one('yt.on', bool(d.get('on')))); return True
    if name == 'diag/memfree': threading.Thread(target=win._mem_reclaim, name='TikLiveMemReclaim', daemon=True).start(); J({'ok': True, 'started': True, 'message': '開始整理：約 2 分鐘後再按「🔍 量一下」看結果'}); return True          # TK_V0.9.32 放掉熱更新舊視窗留下的快取
    if name == 'feat/set': J(win._feat_set(str(d.get('k') or ''), bool(d.get('on')))); return True   # TK_V0.8.93
    if name == 'yt/set':
        k_ = str(d.get('k') or '')
        if k_ not in ('yt.level', 'yt.mbps', 'yt.daily', 'yt.auto_delete', 'yt.order', 'yt.hours', 'yt.hold_new_days'): J({'ok': False, 'message': '不能改這個'}); return True
        J(win._cfg_set_one(k_, d.get('v'))); return True
    if name == 'yt/add':
        sids_ = [int(x) for x in (d.get('sids') or []) if str(x).strip().isdigit()] or None
        _bg(win, sock, lambda: win._yt_enqueue(sids_, 'manual')); return True
    if name == 'yt/back': J(win._yt_back(int(d.get('sid') or 0))); return True     # TK_V0.9.39 YouTube 排隊的這場退回分類
    if name == 'hevc':                                                   # TK_V1.0.32 開始 HEVC 試算（背景）
        J(win._hevc_run(int(d.get('sid') or 0))); return True
    if name == 'sbk':                                                    # TK_V1.0.16 現在備份一份（背景）
        _bg(win, sock, lambda: win._sbk_make('手動')); return True
    if name == 'yt/pri': J(win._yt_pri(int(d.get('sid') or 0), bool(d.get('on', True)))); return True   # TK_V1.0.10 下一個傳這場
    if name == 'yt/del':                                                  # V0.8.20 背景做（要拿上傳的鎖，不卡畫面）
        sids_ = [int(x) for x in (d.get('sids') or []) if str(x).strip().isdigit()] or None; _bg(win, sock, lambda: win._yt_delete_ready(sids_)); return True
    if name == 'yt/retry': _bg(win, sock, win._yt_retry); return True
    if name == 'yt/refind': _bg(win, sock, lambda: win._yt_refind_gone(manual=True)); return True    # TK_V0.9.83 「檔案不見了」的重新找
    if name == 'ytc/add': J(win._ytc_add(d.get('sid'), d.get('a'), d.get('b'), d.get('name') or '')); return True      # V0.8.24 從 YouTube 抓片段
    if name == 'ytc/install': J(win._ytdlp_install()); return True
    if name == 'cul/set': J(win._cul_set(d)); return True                             # V0.8.25（要網頁密碼）
    if name == 'cul/launch': J(win._cul_launch()); return True
    if name == 'cul/learn_reset': J(win._cul_learn_reset()); return True               # V0.8.30
    if name == 'ytc/update': _bg(win, sock, win._ytdlp_update); return True
    if name == 'yt/verified': _bg(win, sock, lambda: (win._yt_retry(), win._yt_long_ok(force=True)) and {'ok': True, 'message': '已重新檢查帳號；可以傳長影片的話，被拒的會自動重傳'}); return True   # V0.8.21
    if name == 'yt/hold_purge':
        up_ = d.get('upto'); _bg(win, sock, lambda: win._yt_hold_purge(up_)); return True        # V0.8.20 暫放資料夾：確認後一次刪（要網頁密碼）
    if name == 'yt/hold_restore': _bg(win, sock, win._yt_hold_restore); return True
    if name == 'lv/out':                                                  # V0.7.22 整理 MP4：+1／+2 轉出到 TIKTOK LIVE OUTPUT（先確認 20 張圖）
        J(win._lv_export([int(x) for x in (d.get('sids') or []) if str(x).strip()])); return True
    if name == 'mp4/fix':                                                 # V0.7.35 搶救（重新整理時間軸）／切掉後面重複的
        J(win._mp4fix(int(d.get('sid') or 0), 'cut' if d.get('mode') == 'cut' else 'remux', str(d.get('nm') or ''), float(d.get('at') or 0))); return True
    if name == 'lv/del':                                                  # V0.6.91 等級整理：-2／-1 刪 MP4（先截 20 張圖）
        J(win._lv_delete([int(x) for x in (d.get('sids') or []) if str(x).strip()])); return True
    if name == 'novideo/set':                                                # V1.1.38 只錄聲音改照審核等級 G：這裡不再手動改
        J({'ok': False, 'message': '只錄聲音現在照「主播審核」的等級：標 G＝只錄聲音，改成別的等級就恢復錄影片'}); return True
    if name == 'novideo/set_old':
        us = [str(x) for x in (d.get('users') or []) if str(x).strip()][:2000]
        if not us: J({'ok': False, 'message': '還沒有勾選主播'}); return True
        J(win._set_novideo(us, bool(d.get('on')), bool(d.get('delete')))); return True
    if name == 'stt/install': J(win._stt_install(str(d.get('model') or '') or None)); return True
    if name == 'stt/cuda': J(win._stt_install_cuda()); return True
    if name == 'stt/vers/use': J(win._stt_ver_use(int(d.get('sid') or 0), str(d.get('v') or ''))); return True
    if name == 'stt/vers/del': J(win._stt_ver_del(int(d.get('sid') or 0), str(d.get('v') or ''))); return True                  # V0.6.79 NVIDIA 顯示卡加速
    if name == 'stt/add': J(win._stt_add([int(x) for x in (d.get('sids') or []) if str(x).isdigit()][:200])); return True
    if name == 'snap/regen': J(win._shot_regen(int(d.get('sid') or 0), int(d.get('rows') or 4), int(d.get('cols') or 5), int(d.get('mult') or 1))); return True
    if name == 'snap/pick':                                              # TK_V0.9.91 挑好的截圖換上去
        sid_ = int(d.get('sid') or 0); nm_ = [str(x) for x in (d.get('names') or [])][:600]; c_ = int(d.get('cols') or 0); _bg(win, sock, lambda: win._shot_pick_apply(sid_, nm_, c_)); return True
    if name == 'snap/pickx': J(win._shot_pick_cancel(int(d.get('sid') or 0))); return True    # V0.7.09 重新截圖
    if name == 'shp/add':                                                 # V0.7.22 整理 MP4：20 張還沒截好的先排到最前面
        n_ = win._shp_add([int(x) for x in (d.get('sids') or []) if str(x).strip()][:500], front=True); J({'ok': True, 'n': n_}); return True
    if name == 'shp/start': J(win._shp_start()); return True                # V0.7.06 批量截 20 張
    if name == 'shp/pause': J(win._shp_pause()); return True
    if name == 'shp/auto': J(win._cfg_set_one('rec.shot_auto', bool(d.get('on')))); return True
    if name == 'stt/plan':                                                # V0.6.97 背景轉字幕：每場最慢幾小時、最多排幾場
        k = {'hours': 'stt.bg_hours', 'max': 'stt.bg_max', 'min': 'stt.bg_min'}.get(str(d.get('k') or ''))
        J(win._cfg_set_one(k, int(d.get('v') or 0)) if k else {'ok': False, 'message': '不認得的設定'}); return True
    if name == 'stt/auto': J(win._cfg_set_one('stt.auto_cpu' if d.get('cpu') else 'stt.auto', bool(d.get('on')))); return True      # V0.6.94 下播後自動轉字幕
    if name == 'stt/cancel': J(win._stt_cancel(int(d.get('sid') or 0))); return True
    if name == 'cg/key':
        ok, msg = win._cg_key_set(str(d.get('key') or '')); J({'ok': ok, 'message': msg, 'info': win._cg_info()}); return True
    if name == 'cg/remove':
        us = [str(x) for x in (d.get('users') or []) if str(x)][:400]
        if not us: J({'ok': False, 'message': '沒有勾選任何主播'}); return True
        J(win._roster_remove_many(us, '網頁／手機')); return True
    return False


# ------------------------------------------------------------------ V0.6.46 送禮動畫（禮物目錄、官方圖示、自備動畫檔／連結）
def gfx_info(win):
    G = _G(win)
    return G['_gfx_info'](win._gfx_cfg())


def _gfx_file_ok(win, rel):
    """A file inside gift_fx (or its _dl folder) by its relative name, or None."""
    G = _G(win); root = G['_gfx_fx_dir']().resolve()
    rel = str(rel or '').replace('\\', '/').strip('/')
    if not rel or '..' in rel.split('/') or rel.count('/') > 1: return None
    p = (root / rel)
    try:
        rp = p.resolve()
        if rp != root and root not in rp.parents: return None
    except Exception: return None
    return p if p.is_file() and p.suffix.lower() in G['_GFX_EXTS'] else None


def gfx_route(win, sock, method, name, q, body):
    G = _G(win); J = lambda o: _send(win, sock, o)
    if name == 'gfx' and method == 'GET': J(gfx_info(win)); return True
    if name == 'gfx/icon' and method == 'GET':                                # the official picture (cached on the SSD); 404 → the page shows 🎁
        k = str(q.get('k', '') or ''); p = G['_gfx_icon_path'](k)
        if p is None and k and k not in G['_gfx_store']()['cat']:                  # V0.6.76 用禮物名稱找（批量剪輯、剪輯器）
            k = G['_gfx_resolve_key'](k); p = G['_gfx_icon_path'](k)
        if p is None:
            e = G['_gfx_store']()['cat'].get(k)
            if e and e.get('u'): G['_gfx_want'](k)
            win._phone_send(sock, '404 Not Found', 'not found'); return True
        try: win._phone_send(sock, '200 OK', p.read_bytes(), G['_GFX_CTYPE'].get(p.suffix.lower(), 'application/octet-stream'), cache=86400)
        except Exception: win._phone_send(sock, '404 Not Found', 'not found')
        return True
    if name == 'gfx/file' and method == 'GET':                                # your own animation file (byte ranges for <video>)
        p = _gfx_file_ok(win, q.get('f', ''))
        if p is None: win._phone_send(sock, '404 Not Found', 'not found'); return True
        win._web_send_file(sock, p, G['_GFX_CTYPE'].get(p.suffix.lower(), 'application/octet-stream'), touch=False, cache=86400); return True
    if method != 'POST': return False
    if name == 'gfx/upload':                                                  # raw file body; password in the X-Pw header (when one is set)
        hdr = getattr(sock, '_hdr', {}) or {}
        if not _pw_ok(win, sock, {'pw': str(hdr.get('x-pw', '') or q.get('pw', ''))}): return True
        k = str(q.get('k', '') or '').strip(); fname = str(q.get('name', '') or '')
        ext = os.path.splitext(fname)[1].lower() or G['_gfx_img_ext'](body)
        if ext not in G['_GFX_EXTS']: J({'ok': False, 'message': '只接受 webm / mp4 / gif / png / webp（還有 jpg / apng / svg / mov）'}); return True
        if len(body) < 16 or len(body) > 40_000_000: J({'ok': False, 'message': '檔案太大（上限 40 MB）或是空的'}); return True
        sniff = G['_gfx_img_ext'](body)
        if sniff and sniff != ext and not (sniff == '.mp4' and ext in ('.mov', '.m4v')): ext = sniff
        cat = G['_gfx_store']()['cat'].get(k) or {}
        stem = '_default' if k == '_default' else (k if k and not k.startswith('n:') and k.isdigit() else G['_gfx_safe'](cat.get('n') or k or os.path.splitext(fname)[0]))
        try:
            d = G['_gfx_fx_dir'](); d.mkdir(parents=True, exist_ok=True)
            for old in d.glob(stem + '.*'):
                if old.suffix.lower() in G['_GFX_EXTS']:
                    try: old.unlink()
                    except Exception: pass
            p = d / (stem + ext); tmp = p.with_suffix(p.suffix + '.tmp'); tmp.write_bytes(body); os.replace(tmp, p)
        except Exception as ex: J({'ok': False, 'message': f'存檔失敗：{ex}'}); return True
        G['_gfx_store']()['fxmap'] = None
        try: win._wd_log(f'送禮動畫：上傳 {p.name}（{len(body):,} bytes）給 {k or "預設"}')
        except Exception: pass
        J({'ok': True, 'file': p.name, 'info': gfx_info(win)}); return True
    d = _body(body)
    if not _pw_ok(win, sock, d): return True
    if name == 'gfx/link':                                                    # paste a link → downloaded into gift_fx\_dl
        k = str(d.get('k') or '').strip(); url = str(d.get('url') or '').strip()
        if not k: J({'ok': False, 'message': '沒有指定禮物'}); return True
        if url and not url.lower().startswith(('http://', 'https://')): J({'ok': False, 'message': '連結要以 http:// 或 https:// 開頭'}); return True
        G['_gfx_link_set'](k, url)
        J({'ok': True, 'info': gfx_info(win), 'message': '開始下載，幾秒後重新整理看結果' if url else '已移除連結'}); return True
    if name == 'gfx/del':                                                     # remove your own file(s) for a gift (the official picture stays)
        k = str(d.get('k') or '').strip(); G2 = G['_gfx_store'](); n = 0
        root = G['_gfx_fx_dir'](); nm = str((G2['cat'].get(k) or {}).get('n') or '').strip()
        stems = {'_default'} if k == '_default' else {x for x in (k.lower(), G['_gfx_safe'](k).lower(), nm.lower(), nm.lower().replace(' ', '_'), G['_gfx_safe'](nm).lower() if nm else '') if x}
        for sub in ('', '_dl'):
            dd = root / sub if sub else root
            if not dd.is_dir(): continue
            for p in list(dd.iterdir()):
                if p.is_file() and p.suffix.lower() in G['_GFX_EXTS'] and p.stem.lower() in stems:
                    try: p.unlink(); n += 1
                    except Exception: pass
        G2['links'].pop(k, None); G2['dirty'] = True; G2['fxmap'] = None; G['_gfx_save'](force=True)
        J({'ok': True, 'n': n, 'info': gfx_info(win)}); return True
    if name == 'gfx/forget':                                                  # drop a catalog entry (it comes back the next time that gift is sent)
        k = str(d.get('k') or '').strip(); G2 = G['_gfx_store']()
        G2['cat'].pop(k, None); G2['dirty'] = True; G['_gfx_save'](force=True); J({'ok': True, 'info': gfx_info(win)}); return True
    return False


def _th_mod(win):
    import sys as _s
    return _s.modules[win.__class__.__module__]
