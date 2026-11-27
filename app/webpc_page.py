"""V0.6.01 網頁版電腦介面 — the page (HTML/CSS/JS in one string). Served at <網址>/pc. Server side: webpc_api.py."""
import json, re


def page(win, base, G):
    themes = json.dumps(G['THEMES'], ensure_ascii=False)
    return (_sh_html(G).replace('__BASE__', base).replace('__THEMES__', themes).replace('__MODE__', G['THEME_MODE'].get('mode', 'dark'))
            .replace('__PCNAME__', win.pc_role_name()).replace('__APPVER__', str(G.get('APP_VERSION', ''))))


HTML = r'''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>TikLive Monitor · 網頁版</title><link rel="icon" href="__BASE__/icon-192.png"><style>*{box-sizing:border-box}html,body{margin:0;height:100%;overflow:hidden}
body{background:var(--bg);color:var(--text);font:13px "Yu Gothic UI","Microsoft JhengHei","PingFang TC","Noto Sans TC",sans-serif;-webkit-font-smoothing:antialiased}
button,input,select,textarea{font:inherit;color:inherit}
button{background:var(--button);border:1px solid var(--border_strong);border-radius:8px;padding:5px 9px;cursor:pointer;color:var(--text)}
button:hover{background:var(--button_hover)}button:disabled{opacity:.45;cursor:default}
button.start,button.sstart{background:#e51e63;border:0;color:#fff;font-weight:800}button.start:hover,button.sstart:hover{background:#f0306f}
input,select,textarea{background:var(--input);border:1px solid var(--border_strong);border-radius:7px;padding:4px 7px;color:var(--text_strong)}
input[type=checkbox],input[type=range]{padding:0}
::-webkit-scrollbar{width:8px;height:8px}::-webkit-scrollbar-thumb{background:var(--scroll);border-radius:4px}::-webkit-scrollbar-track{background:transparent}
#app{display:grid;grid-template-columns:var(--sidew,210px) minmax(0,1fr);grid-template-rows:100vh;height:100vh;overflow:hidden}
#side{background:var(--side);border-right:1px solid var(--border);display:flex;flex-direction:column;padding:10px 10px 10px;gap:5px;min-width:0;min-height:0;overflow:hidden}
.vav{width:18px;height:18px;border-radius:50%;object-fit:cover;vertical-align:middle;margin-top:2px}.vav.big{width:34px;height:34px;margin:0 6px 0 0}
#sdCount{color:var(--subtext);font-size:13px;line-height:1.1;white-space:nowrap}#sdCount{display:flex;align-items:flex-end;gap:5px;margin:-2px 0 -2px}#sdCount .cDot{flex:none;width:10px;height:10px;border-radius:50%;align-self:flex-end;margin-bottom:8px}#sdCount .cBig{color:#45d483;font-size:39px;font-weight:900;letter-spacing:-.5px;line-height:1}#sdCount .cSm{align-self:flex-end;margin-bottom:4px}#sdStatus{display:none!important}#sdCount .cSm{font-weight:700;color:var(--text)}.ss{display:flex;gap:4px}.ss button{flex:1;min-height:28px;padding:3px 4px;font-size:12px}
.sstop{font-weight:800}#sdStatus{font-weight:800;color:var(--sub_accent);font-size:13px}
#nav{flex:1;min-height:0;overflow-y:auto;background:var(--nav);border-radius:9px;padding:4px 0;margin-top:4px}
.nh{display:flex;align-items:flex-end;gap:6px;padding:9px 10px 3px;font-size:10.5px;font-weight:800;letter-spacing:.08em;cursor:pointer;user-select:none}.nh em{font-style:normal;font-size:10px;opacity:.75;letter-spacing:0;margin-left:auto}.nh.shut{opacity:.8}.nh:hover{filter:brightness(1.2)}.nh i{flex:1;height:1px;opacity:.28;background:currentColor;margin-bottom:5px}
.ni{position:relative;display:flex;align-items:center;margin:1px 4px;padding:6px 6px 6px 0;border-radius:7px;cursor:pointer;color:var(--nav_text)}
.ni b{width:28px;text-align:center;font-weight:400;color:var(--muted);flex:none}.ni:hover{background:var(--hover);color:var(--text)}
.ni.on{color:var(--text_strong);font-weight:800}.ni.on:before{content:'';position:absolute;left:1px;top:5px;bottom:5px;width:3.5px;border-radius:2px;background:var(--gc)}
.ni.on{background:color-mix(in srgb,var(--gc) 15%,transparent)}.ni.on b{color:var(--gc)}
#sysBox{background:var(--card);border:1px solid var(--border);border-radius:9px;padding:5px 8px;cursor:pointer;font-size:11px}#sysBox:hover{border-color:var(--border_strong)}
.sp{display:grid;grid-template-columns:34px 1fr 46px 26px;align-items:center;gap:4px;height:19px}.sp b{color:var(--subtext);font-size:10.5px}.sp em{font-style:normal;font-weight:700;color:var(--text_strong);text-align:right;font-size:11px;white-space:nowrap}.sp small{text-align:right;font-size:10.5px}
.spb{position:relative;height:6px;border-radius:3px;background:var(--track)}.spb i{position:absolute;left:0;top:0;bottom:0;border-radius:3px}.spb u{position:absolute;left:0;top:8px;height:2px;border-radius:1px}
#netBtn{text-align:left;padding:5px 8px;font-size:11.5px;white-space:pre-line;line-height:1.35}
#qBtn{text-align:left;padding:5px 8px;font-size:11.5px;line-height:1.35;margin-top:4px;white-space:pre-line}
main{display:flex;flex-direction:column;min-width:0;min-height:0}
#tabsRow{display:flex;align-items:stretch;gap:6px;padding:4px 6px 2px;border-bottom:1px solid var(--border);background:var(--bg);min-height:56px}
#tabMode{font-size:10.5px;font-weight:700;padding:2px 6px;white-space:pre;line-height:1.2;border-color:#2b3440}#tabMode.on{border-color:#45d483}
#tabs{flex:1;display:flex;gap:2px;overflow-x:auto;overflow-y:hidden;align-items:stretch;padding-bottom:2px}
#topRight{display:flex;flex-direction:column;align-items:flex-end;justify-content:center;gap:3px;font-size:11px;color:var(--subtext);white-space:nowrap}
#topRight button{font-size:11.5px;padding:3px 8px}
.tb{position:relative;display:flex;align-items:center;gap:6px;flex:none;border:1px solid var(--tab_border);background:var(--tab_bg);border-radius:6px;padding:4px 8px 4px 6px;cursor:pointer;min-width:0;user-select:none}
.tb.on{background:var(--tab_active);border:2px solid var(--tab_active_border);padding:3px 7px 3px 5px}.tb.alert{background:var(--tab_alert);border:2px solid #ff4d6d}
.tb .av{width:40px;height:40px}.tb .tx{display:flex;flex-direction:column;min-width:0;line-height:1.25}
.tb .tx b{color:var(--tab_text);font-size:13px;white-space:nowrap;overflow:hidden;max-width:150px}.tb .tx .dl{font-size:11.5px;white-space:nowrap}
.dia{color:#4dc9ff}.lik{color:#ff5c8a}.grn{color:#45d483}.tsub{color:var(--tab_sub)}
.tb.col{flex-direction:column;gap:1px;padding:6px 4px 3px;align-items:center}.tb.col .av{width:50px;height:50px}.tb.col .pill{position:absolute;top:3px;left:50%;transform:translateX(-50%);background:rgba(20,120,70,.92);color:#fff;font-size:10px;border-radius:5px;padding:0 4px;white-space:nowrap}
.tb.col .t1{font-size:11px}.tb.col .t2{font-size:10.5px;white-space:nowrap}
.tb.stk{padding:2px;border:0;background:transparent;margin-right:-8px}.tb.stk .av{width:34px;height:34px;box-shadow:0 0 0 2px var(--bg)}
.tb.stk .pop{display:none;position:fixed;z-index:50;box-shadow:2px 3px 12px rgba(0,0,0,.4)}.tb.stk:hover .pop{display:flex}
.tb.hist{background:var(--hist_bg);border:2px solid var(--hist_border);padding:3px 22px 3px 8px;flex-direction:column;align-items:flex-start;gap:0;min-width:110px}
.tb.hist.on{background:var(--hist_active);border-color:var(--hist_active_border)}.tb.hist b{color:var(--hist_text);font-size:12px;white-space:nowrap}.tb.hist small{color:var(--hist_sub);font-size:10.5px}
.tb.hist .x{position:absolute;right:3px;top:3px;font-size:11px;color:var(--hist_sub);padding:0 3px;border-radius:4px}.tb.hist .x:hover{background:rgba(255,255,255,.12)}
.tb.ph{color:#f0ad4e;font-weight:800;font-size:13px;padding:8px 14px}
.av{border-radius:50%;object-fit:cover;flex:none;border:2px solid var(--border_strong);background:#334}.av.live{border-color:#45d483}.av.pri{border-color:#ff4d6d}
.avf{display:inline-flex;align-items:center;justify-content:center;color:#fff;font-weight:800;border-radius:50%;flex:none;border:2px solid var(--border_strong)}
#page{flex:1;min-height:0;position:relative;overflow:hidden}
.pg{position:absolute;inset:0;overflow:auto;padding:8px 10px 10px}.pg.fill{display:flex;flex-direction:column;gap:8px;overflow:hidden}
#statusBar{display:flex;align-items:center;gap:10px;padding:2px 10px;border-top:1px solid var(--border);font-size:11.5px;color:var(--subtext);min-height:24px;background:var(--bg)}
#sbMsg{flex:1;overflow:hidden;white-space:nowrap;text-overflow:ellipsis}#statusBar button{font-size:11px;padding:1px 7px}
.title{font-size:24px;font-weight:850;color:var(--text);margin:0}.sub{color:var(--subtext);font-size:12px}
.sec{font-size:14px;font-weight:800;color:var(--text)}
.panel{background:var(--panel);border:1px solid var(--border);border-radius:9px;padding:8px 10px}.hero{background:var(--card);border:1px solid var(--border_strong);border-radius:13px;padding:6px 10px}
.card{background:var(--card);border:1px solid var(--border);border-radius:11px;display:flex;flex-direction:column;align-items:center;justify-content:center;overflow:hidden;transition:background .15s,border-color .15s}
.card .ct{font-size:11px;color:var(--subtext)}.card .cvv{font-weight:800;color:var(--text_strong);line-height:1.1;white-space:nowrap}.card.flash{background:var(--flash_bg);border-color:var(--flash_border)}
.row{display:flex;align-items:center;gap:6px}.row.wrap{flex-wrap:wrap}.grow{flex:1;min-width:0}.right{margin-left:auto}
.cv{position:relative;flex:1;min-height:0}.blk{position:absolute;padding:2px;display:flex;flex-direction:column;min-height:0;min-width:0}
.blk>.panel{flex:1;display:flex;flex-direction:column;min-height:0;padding:6px}.bt{display:flex;align-items:center;gap:6px;margin-bottom:4px;font-weight:800;font-size:13px}
/* virtual table */
.vt{display:flex;flex-direction:column;min-height:0;flex:1;background:var(--panel);border:1px solid var(--border);border-radius:8px;overflow:hidden;font-size:12.5px}
.vtbar{display:flex;align-items:center;gap:8px;padding:0 0 4px}.vtbar input{width:120px;padding:2px 6px}.vtbar .h{color:var(--subtext);font-size:11px}
.vth{display:flex;background:var(--header_bg);color:var(--header_text);font-weight:700;font-size:11.5px;flex:none;overflow:hidden;user-select:none}
.vth div{position:relative;padding:4px 15px 4px 5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;flex:none;cursor:pointer;border-right:1px solid var(--grid)}
.vth div:after{content:'▲▼';position:absolute;right:3px;top:5px;font-size:7px;letter-spacing:-1px;opacity:.25}.vth div.sd:after{content:'▼';opacity:1;color:#ff3b4f;font-size:9px}.vth div.sa:after{content:'▲';opacity:1;color:#ff3b4f;font-size:9px}
.vth .rz{position:absolute;right:0;top:0;bottom:0;width:6px;cursor:col-resize}
.vtb{flex:1;overflow:auto;position:relative}.vtsp{position:relative}
.vr{position:absolute;left:0;display:flex;white-space:nowrap;border-bottom:1px solid var(--grid)}.vr:nth-child(even){background:var(--alt_row)}
.vr div{padding:0 5px;overflow:hidden;text-overflow:ellipsis;flex:none}.vr.sel{background:var(--selection)!important;color:var(--selection_text)}
.vr.sep{color:var(--subtext);justify-content:center}.vr.div{background:var(--divider_bg)!important;color:#2b9be0;border:1px solid #2b8ab8;justify-content:center;font-size:12px;z-index:2}
.al-r{text-align:right}.al-c{text-align:center}
/* menus / dialogs */
.menu{position:fixed;z-index:200;background:var(--panel);border:1px solid var(--border_strong);border-radius:8px;padding:4px;min-width:200px;box-shadow:0 8px 28px rgba(0,0,0,.45)}
.menu div{padding:6px 12px;border-radius:5px;cursor:pointer;white-space:nowrap}.menu div:hover{background:var(--selection)}.menu div.dis{opacity:.45;cursor:default}.menu div.dis:hover{background:none}
.menu hr{border:0;border-top:1px solid var(--border);margin:4px 2px}.menu .big{background:#d6283c;color:#fff;font-weight:800;font-size:15px;margin:2px 2px 6px}.menu .big:hover{background:#ef3a50}
.dlgbg{position:fixed;inset:0;background:rgba(0,0,0,.45);z-index:300;display:flex;align-items:center;justify-content:center}
.dlg{background:var(--panel);border:1px solid var(--border_strong);border-radius:12px;padding:14px 16px;min-width:340px;max-width:min(92vw,980px);max-height:88vh;overflow:auto;box-shadow:0 16px 48px rgba(0,0,0,.5)}
.dlg h3{margin:0 0 10px;font-size:16px}.dlg .btns{display:flex;gap:8px;justify-content:flex-end;margin-top:14px}.dlg .del{background:#d6283c;color:#fff;border:0;font-weight:800}
.form{display:grid;grid-template-columns:auto 1fr;gap:8px 10px;align-items:center}
.toast{position:fixed;left:50%;bottom:40px;transform:translateX(-50%);background:var(--card);border:1px solid var(--border_strong);padding:8px 16px;border-radius:9px;z-index:400;box-shadow:0 6px 20px rgba(0,0,0,.4)}
/* dashboard specifics */
.heroRow{display:flex;align-items:center;gap:18px;height:100%}.heroRow .hu{font-size:17px;font-weight:800;color:var(--text_strong)}
.pend{display:flex;flex-direction:column;gap:3px;overflow:auto;flex:1}.pend button{text-align:left;min-height:25px;padding:2px 8px;background:var(--tile_bg);border:1px solid var(--tile_border);color:var(--tile_text);font-size:12px;border-radius:6px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.pend button.pri{background:var(--prio_bg);border-color:#ff4d6d;font-weight:800}
.chartw{position:relative;flex:1;min-height:0}.chartw canvas{position:absolute;inset:0;width:100%;height:100%}
.giftrow{display:flex;gap:10px;font-size:11px;color:var(--subtext);align-items:center;margin-top:3px}.giftrow input[type=range]{flex:1;min-width:40px}
.tl{position:relative;height:28px;cursor:pointer;flex:1;min-width:120px}.tl canvas{width:100%;height:100%}
video.hv{width:100%;height:100%;background:#000;object-fit:contain;border-radius:6px}
.ph2{flex:1;display:flex;align-items:center;justify-content:center;color:var(--subtext);background:var(--chart_bg);border-radius:6px}
/* grids */
.sgrid{display:grid;grid-template-columns:repeat(var(--cols,5),minmax(0,1fr));gap:8px}
.scard{position:relative;display:flex;gap:8px;align-items:center;background:var(--card);border:1px solid var(--border_strong);border-radius:9px;padding:7px 8px 26px;min-height:82px;cursor:default;overflow:hidden}
.scard.live{border:2px solid #45d483}.scard.pri{border:2px solid #ff4d6d}.scard.stale{border:2px solid #9b6dff}.scard.grace{border:2px solid #f0ad4e}
.scard .nm{font-weight:800;color:var(--text_strong);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.scard .no{color:var(--subtext);font-size:11px;margin-right:4px}
.scard .band{position:absolute;left:0;right:0;bottom:0;height:20px;font-size:11px;display:flex;align-items:center;padding:0 8px;background:rgba(127,127,127,.12);color:var(--subtext);white-space:nowrap;overflow:hidden}
.scard.live .band{background:rgba(69,212,131,.16);color:#45d483}.scard.grace .band{background:rgba(240,173,78,.16);color:#f0ad4e}
.scard .dot{width:9px;height:9px;border-radius:50%;flex:none}.scard.drag{opacity:.4}.scard.over{outline:2px dashed var(--flash_border)}
.shead{display:flex;align-items:baseline;gap:8px;margin:12px 0 6px;font-weight:800;border-bottom:1px solid var(--border);padding-bottom:3px}
.cdot{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:4px;vertical-align:-1px}
.kv{display:grid;grid-template-columns:auto 1fr auto 1fr;gap:3px 14px;font-size:12.5px}.kv span{color:var(--subtext)}.kv b{color:var(--text_strong);font-weight:700}
.tiles{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:6px}.ptile{display:flex;gap:8px;align-items:center;border:1px solid var(--tile_border);background:var(--tile_bg);border-radius:8px;padding:6px 8px;cursor:pointer}
.ptile.on{border-color:var(--flash_border);background:var(--tile_hover)}.ptile canvas{width:84px;height:46px;flex:none}.ptile b{display:block}.ptile .v{display:block;font-size:17px;font-weight:800}.ptile small{display:block;color:var(--subtext);font-size:11px;line-height:1.3}
.bar{height:12px;background:var(--track);border-radius:3px;overflow:hidden}.bar i{display:block;height:100%}
.log{font-family:Consolas,monospace;font-size:12px;background:#080b0f;color:#b8f7cf;border:1px solid #26313b;border-radius:6px;padding:6px;white-space:pre;overflow:auto}
.setl{width:190px;flex:none;overflow:auto}.setl div{padding:7px 10px;border-radius:7px;cursor:pointer}.setl div.on{background:var(--selection);font-weight:800}
.srow{border:1px solid var(--border);background:var(--panel);border-radius:9px;padding:8px 10px;margin-bottom:6px}.srow.dirty{border-color:#f0ad4e}
.srow .r0{display:flex;align-items:center;gap:8px}.srow .r0 b{flex:1}.srow .r1{color:var(--subtext);font-size:11.5px;margin-top:3px}
.num{display:inline-flex;align-items:center;gap:3px}.num input{width:76px;text-align:center}.num button{width:30px;padding:3px 0}
.chg{background:var(--card);border:1px solid var(--border);border-radius:9px;padding:8px 12px;margin-bottom:8px}.chg.first{border-color:#4dc9ff}
.drop{border:2px dashed var(--border_strong);border-radius:10px;padding:18px;text-align:center;color:var(--subtext)}.drop.over{border-color:var(--flash_border);color:var(--text)}
.hm{display:grid;grid-template-columns:44px repeat(24,minmax(0,1fr));gap:1px;font-size:10px}.hm span{color:var(--subtext);align-self:center}.hm i{height:18px;border-radius:2px;font-style:normal;display:flex;align-items:center;justify-content:center;border:1px solid var(--grid);color:var(--text_strong)}

#miniW{flex:none;align-self:center;margin:0 10px;max-width:58vw;overflow:hidden}

.ssec.isu{border:1px solid var(--border);border-radius:10px;padding:10px 12px;margin-top:8px;background:var(--panel)}.ssec.isu h3{margin:0 0 6px;font-size:14px}

@@SH0@@

@@SH1@@

@@SH2@@

@@SH3@@

@@SH4@@

/* NV-CSS-BEGIN */
/* V0.6.59 只錄聲音的主播（用 p_sanom.css 的彈出視窗樣式） */
/* NV-CSS-END */

@@SH5@@

@@SH6@@

@@SH7@@

@@SH8@@

@@SH9@@

/* HT-CSS-BEGIN */
/* V0.6.85 歷史回放的縮圖時間軸 */
.htl{position:relative;height:104px;min-height:56px;flex:none;display:flex;flex-direction:column;background:rgba(0,0,0,.18);border-radius:10px;margin:4px 0;user-select:none;-webkit-user-select:none;overflow:hidden}
.htl canvas{flex:1;min-height:0;width:100%;display:block;touch-action:none;cursor:grab}
.htl canvas:active{cursor:grabbing}
.htlZ{position:absolute;right:6px;top:2px;display:flex;gap:4px}
.htlZ button{width:26px;height:20px;border-radius:6px;border:1px solid rgba(140,150,165,.35);background:rgba(20,24,32,.75);color:#e6eaf0;font-size:13px;line-height:1;padding:0;cursor:pointer}
.htlGrip{flex:none;height:18px;display:flex;align-items:center;justify-content:center;cursor:ns-resize;touch-action:none}
.htlGrip i{width:56px;height:5px;border-radius:2px;background:rgba(140,150,165,.55)}
/* HT-CSS-END */

/* HA-CSS-BEGIN */
/* V0.6.86 回放頁的保存等級／只錄聲音／刪除 */
.haBar{display:flex;align-items:center;gap:6px;flex-wrap:wrap;padding:6px 8px;margin:2px 0;border-radius:10px;background:rgba(128,128,128,.08);font-size:13px}
.haBar .haT{color:var(--sub,#8b95a5);font-size:12px}
.haLv{display:flex;gap:4px}
.haLv button{min-width:34px;height:28px;padding:0 6px;border-radius:999px;border:2px solid var(--c);background:transparent;color:var(--c);font-weight:800;font-size:13px;cursor:pointer}
.haLv button.on{background:var(--c);color:#111}
.haBar .haN{font-weight:800;font-size:12.5px;min-width:64px}
.haBar .haG{flex:1}
.haBar .haB{height:30px;padding:0 12px;border-radius:999px;border:1px solid var(--line,rgba(140,150,165,.35));background:var(--btn,transparent);color:var(--text,#e6eaf0);font-size:13px;font-weight:700;cursor:pointer;white-space:nowrap}
.haBar .haB.bad{color:#ff6577;border-color:rgba(255,101,119,.5)}
@media (max-width:520px){.haBar{gap:4px;padding:5px 6px}.haBar .haSel{max-width:30vw;padding:0 6px;font-size:12px}.haBar .haB{padding:0 9px;font-size:12px}.haBar .haG{display:none}}
.haBar .haSel{height:30px;max-width:min(30vw,240px);min-width:0;flex:0 1 auto;border-radius:999px;border:1px solid var(--line,rgba(140,150,165,.35));background:var(--btn,var(--card,#1c222c));color:var(--text,#e6eaf0);padding:0 10px;font-size:13px;font-weight:700}
/* HA-CSS-END */

@@SH10@@

@@SH11@@

@@SH12@@

/* SH-CSS-BEGIN */
.shp{display:flex;flex-direction:column;gap:8px;font-size:13.5px}
.shpC{border:1px solid var(--line,rgba(140,150,165,.3));border-radius:12px;padding:10px 12px;background:var(--card,rgba(127,127,127,.05));display:flex;flex-direction:column;gap:8px}
.shpRow{display:flex;align-items:center;gap:8px;flex-wrap:wrap}.shpRow b{font-size:15px}.shpRow .grow{flex:1}
.shpSt{font-size:12px;padding:2px 8px;border-radius:999px;background:rgba(150,150,150,.2)}.shpSt.on{background:rgba(60,207,142,.18);color:#3ccf8e}
.shpGo{background:#1f8ef1;border-color:#1f8ef1;color:#fff;font-weight:800}
.shpNums{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:6px}.shpNums div{background:rgba(127,127,127,.08);border-radius:9px;padding:6px 8px}.shpNums b{display:block;font-size:18px}.shpNums small{font-size:11.5px;opacity:.75}
.shpCur{color:#3fb6f2;font-weight:700}
.shpChk{display:flex;align-items:center;gap:6px;font-size:13px}
.shpH{font-size:12.5px;max-height:150px;overflow:auto;border-top:1px solid rgba(140,150,165,.2);padding-top:4px}.shpH small{opacity:.7}
.shpN{font-size:12px;opacity:.7;line-height:1.6}
/* SH-CSS-END */

@@SH13@@

@@SH14@@

@@SH15@@

/* SOON-CSS-BEGIN */
.soonBar{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin:4px 0 8px;padding:6px 10px;border-radius:12px;border:1px solid rgba(240,173,78,.35);background:rgba(240,173,78,.06);font-size:13px}
.soonBar>b{white-space:nowrap}.soonL{display:flex;gap:6px;flex-wrap:wrap;min-width:0}
.soonP{border:1px solid rgba(140,150,165,.35);background:rgba(140,150,165,.1);color:inherit;border-radius:999px;padding:3px 10px;font-size:12.5px;cursor:pointer;white-space:nowrap;max-width:100%;overflow:hidden;text-overflow:ellipsis}
.soonP small{opacity:.7}.soonP.soonPri{border-color:rgba(255,77,109,.55)}.soonP.soonNow{background:rgba(240,173,78,.18);border-color:rgba(240,173,78,.6)}.soonM{opacity:.6;font-size:12px;align-self:center}
/* SOON-CSS-END */

/* SMT-CSS-BEGIN */
.smtC{border:1px solid rgba(31,142,241,.35);border-radius:12px;padding:8px 10px;margin:4px 0 10px;background:rgba(31,142,241,.05);display:flex;flex-direction:column;gap:2px}
.smtH{display:flex;align-items:baseline;gap:8px;margin-bottom:2px}.smtH small{opacity:.6;font-size:11.5px}
.smtR{display:grid;grid-template-columns:22px minmax(80px,auto) minmax(0,1fr) 12px;gap:6px;align-items:center;text-align:left;background:none;border:0;border-top:1px solid rgba(140,150,165,.15);color:inherit;padding:5px 2px;font-size:13px;cursor:pointer;width:100%}
.smtR:first-of-type{border-top:0}.smtR span{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;opacity:.9}.smtR s{text-decoration:none;opacity:.5}.smtR i{font-style:normal}
.smtR.smt-ok span{color:#45d483}.smtR.smt-warn span{color:#f0ad4e}.smtR.smt-bad span{color:#ff6577;font-weight:700}.smtR.smt-off span{opacity:.55}
@media(max-width:520px){.smtR{grid-template-columns:22px minmax(0,1fr) 12px}.smtR span{grid-column:2;white-space:normal;font-size:12px}.smtR s{grid-row:1;grid-column:3}}
/* SMT-CSS-END */

@@SH16@@

@@SH17@@

@@SH18@@

/* LEND-CSS-BEGIN */
#lendBn{position:fixed;left:50%;top:8px;transform:translateX(-50%);z-index:100000;width:min(720px,calc(100vw - 16px));max-height:80vh;overflow:auto;padding:12px 14px;border-radius:14px;
  background:#2a1418;color:#fff;border:2px solid #ff6577;box-shadow:0 10px 30px rgba(0,0,0,.55);font-size:13.5px;display:flex;flex-direction:column;gap:6px}
.lendH{font-size:15px;font-weight:bold}.lendW{margin:0;padding-left:18px;line-height:1.6}.lendN{opacity:.8;font-size:12.5px}
.lendC{display:flex;flex-wrap:wrap;gap:8px;align-items:center;padding:6px 8px;border-radius:10px;background:rgba(255,255,255,.06)}.lendC.no{opacity:.6}.lendC b{min-width:28px}.lendC span{font-size:12.5px}
.lendC button,.lendA button{margin-left:auto;width:auto!important;padding:5px 12px!important;border-radius:9px}.lendC em{margin-left:auto;font-style:normal;color:#45d483}
.lendA{display:flex;gap:6px;flex-wrap:wrap;justify-content:flex-end}.lendA button{margin-left:0}
.emgLend{display:flex;flex-direction:column;gap:6px}
/* LEND-CSS-END */

@@SH19@@

/* EXP-CSS-BEGIN */
.exp{display:flex;flex-direction:column;gap:10px}.expH{display:flex;flex-direction:column;gap:3px}.expH b{font-size:18px}.expH span{opacity:.75;font-size:13px}.expE{opacity:.7;padding:14px 4px}
.expC{display:flex;flex-direction:column;gap:6px;padding:12px;border-radius:12px;background:rgba(140,150,165,.08);border:1px solid rgba(140,150,165,.25)}
.expC>b{font-size:15px}.expC small{opacity:.6}.expG{font-size:12px;color:#b48cff}.expC ul{margin:0;padding-left:18px;font-size:13px;line-height:1.6}.expD{font-size:13px;opacity:.85}
.expM{display:flex;gap:6px;flex-wrap:wrap}.expM button{border:1px solid rgba(180,140,255,.6);background:transparent;color:inherit;border-radius:9px;padding:6px 10px;font:inherit;font-size:13px;cursor:pointer}
.expM button.on{background:#b48cff;color:#111;border-color:transparent;font-weight:700}.expS{font-size:13px;padding:6px 8px;border-radius:8px;background:rgba(77,201,255,.08)}
/* EXP-CSS-END */

@@SH20@@

@@SH21@@

/* TKD-CSS-BEGIN */
.tkdEmpty{padding:30px;text-align:center;color:var(--subtext,#8a93a3)}
.tkdTop{display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.tkdTop input{flex:1 1 140px;min-width:0;padding:8px 10px;border-radius:10px;border:1px solid var(--border,#2b313c);background:var(--panel,#1b1f27);color:inherit;font-size:14px}
.tkdTop select{padding:7px 6px;border-radius:10px;border:1px solid var(--border,#2b313c);background:var(--panel,#1b1f27);color:inherit;font-size:13.5px;max-width:48%}
.tkdTop button{flex:0 0 auto;padding:7px 14px;border-radius:10px;border:1px solid var(--border,#2b313c);background:var(--panel,#1b1f27);color:inherit;font-size:15px}
.tkdSub{font-size:11.5px;color:var(--subtext,#8a93a3);margin:6px 0}
.tkdG{display:grid;grid-template-columns:repeat(3,1fr);gap:6px}
@media (min-width:700px){.tkdG{grid-template-columns:repeat(6,1fr)}}
.tkdC{cursor:pointer;min-width:0}.tkdC b{display:block;font-size:12.5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-top:3px}.tkdC small{display:block;font-size:10.5px;color:var(--subtext,#8a93a3)}
.tkdIm{position:relative;height:0;padding-top:177.78%;background:#14171d;border-radius:8px;overflow:hidden}.tkdIm img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block}
@@SH22@@

.verBar{position:fixed;left:10px;right:10px;margin:0 auto;width:fit-content;top:calc(env(safe-area-inset-top,0px) + 6px);z-index:2147483100;display:flex;align-items:center;gap:8px;padding:8px 10px;border-radius:12px;background:#1d2a3a;border:1px solid #4dc9ff;color:#e8ecf1;font-size:13px;box-shadow:0 6px 18px rgba(0,0,0,.5);max-width:calc(100vw - 20px)}.verBar span{flex:1 1 auto;min-width:0}.verBar button{width:auto!important;margin:0;height:32px;padding:0 10px;border-radius:9px;border:1px solid #4dc9ff;background:#4dc9ff;color:#06202b;font-weight:800;font-size:12.5px;cursor:pointer;flex:none}.verBar button[data-vx]{background:transparent;color:#9aa3b2;border-color:#3a4250}   /* TK_V1.0.27 */
.actT{display:flex;gap:6px;margin-bottom:6px}.actT input{flex:1;min-width:0}.actT select{width:auto}.actC{display:flex;gap:6px;overflow-x:auto;padding-bottom:4px}.actC button{flex:none;width:auto!important;margin:0;height:32px;padding:0 10px;border-radius:16px;border:1px solid var(--line,rgba(127,127,127,.3));background:transparent;color:inherit;font-size:12.5px;white-space:nowrap}.actC button.on{background:#4dc9ff;color:#06202b;border-color:#4dc9ff}.actC small{opacity:.7}.actN{font-size:12px;opacity:.65;margin:4px 0}.actR{display:flex;gap:8px;padding:6px 0;border-bottom:1px solid var(--line,rgba(127,127,127,.3));font-size:12.5px;line-height:1.5}.actR small{flex:none;opacity:.6;font-variant-numeric:tabular-nums}.actR span{word-break:break-all}   /* TK_V1.0.23 */
.sbkN{font-size:13px;line-height:1.6;margin-bottom:8px}.sbkN small{opacity:.6;word-break:break-all}.sbkGo{margin:4px 0 10px!important}.sbkR{display:flex;align-items:center;gap:10px;padding:7px 0;border-bottom:1px solid var(--line,rgba(127,127,127,.3))}.sbkR b{flex:1}.sbkR span{opacity:.7;font-size:12.5px}.sbkE{opacity:.7;font-size:13px;padding:8px 0}   /* TK_V1.0.16 */
.lvaW{position:fixed;top:calc(env(safe-area-inset-top,0px) + 40px);right:10px;z-index:2147483240;display:flex;flex-direction:column;gap:6px;max-width:min(360px,calc(100vw - 20px))}   /* TK_V1.0.38 開播提醒 */
.gfsH{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:6px}.gfsH b{font-size:16px;flex:1 1 auto}.gfsH select{max-width:100%;padding:7px 8px;border-radius:9px;background:var(--card,#151a21);color:inherit;border:1px solid var(--line,#2a3340)}   /* TK_V1.0.75 GIF 製作 */
.gfsN{font-size:12.5px;opacity:.8;line-height:1.55;margin:4px 0 8px}.gfsTb,.gfsR,.gfsFine{display:flex;gap:6px;align-items:center;flex-wrap:wrap;margin:6px 0}.gfsTb span,.gfsR span,.gfsFine span{font-size:12.5px;opacity:.75;min-width:56px}
.gfsTb button,.gfsR button,.gfsFine button{padding:7px 10px;border-radius:9px;border:1px solid var(--line,#2a3340);background:var(--card,#151a21);color:inherit;font:inherit;font-size:13px;font-weight:600;cursor:pointer}.gfsTb button.on,.gfsR button.on{background:rgba(77,201,255,.2);border-color:#4dc9ff;color:#bfeaff}
.gfsG{display:grid;gap:3px;margin:6px 0;user-select:none;-webkit-user-select:none}.gfsC{position:relative;height:0;padding-top:177.78%;overflow:hidden;border-radius:6px;background:#000;touch-action:pan-y;cursor:ew-resize;outline:2px solid transparent}.gfsC.on{outline-color:#4dc9ff}
.gfsC img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;pointer-events:none;-webkit-touch-callout:none}.gfsC b{position:absolute;left:0;right:0;bottom:0;text-align:center;font-size:11.5px;background:rgba(0,0,0,.6);color:#fff;padding:2px 0}.gfsC i{position:absolute;left:4px;top:3px;font-style:normal;font-size:11px;color:#fff;text-shadow:0 0 3px #000}
.gfsFine{position:sticky;bottom:0;background:var(--panel,#11151b);padding:8px 4px;border-top:1px solid var(--line,#2a3340);z-index:2}.gfsFine button{flex:1 1 0;min-width:0}
.gfsO{border:1px solid var(--line,#2a3340);border-radius:12px;padding:8px 10px;margin-top:10px}.gfsGo{width:100%;margin-top:6px;padding:12px;border-radius:12px;border:0;background:#ff3d63;color:#fff;font:inherit;font-weight:800;font-size:16px;cursor:pointer}
.gfsL{margin-top:10px}.gfsJ{border:1px solid var(--line,#2a3340);border-radius:10px;padding:8px 10px;margin:6px 0}.gfsJ.done{border-color:rgba(46,204,113,.5)}.gfsJ.fail{border-color:rgba(255,77,109,.6)}.gfsJ>b{display:block;font-size:13.5px}.gfsJ>small{display:block;font-size:12px;opacity:.75;margin:2px 0}
.gfsF{display:flex;gap:10px;align-items:center;margin-top:6px}.gfsF img{width:120px;border-radius:6px;background:#000}.gfsF b{display:block;font-size:13px}.gfsF small{display:block;font-size:11.5px;opacity:.7;margin:2px 0 6px}.gfsF a.pill{text-decoration:none;color:inherit}
.vgPvH .pill{flex:none!important;width:auto!important;max-width:none!important;min-width:0!important;white-space:nowrap!important;overflow:visible!important;text-overflow:clip!important;padding:6px 10px!important}.vgPvH .vgPvT{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.g20B{max-height:86vh;overflow:auto}.g20B .lvsOptT small{font-size:11.5px;opacity:.7;font-weight:400}.g20R{grid-column:1/-1;display:flex;align-items:center;gap:6px;flex-wrap:wrap}.g20R span{font-size:12.5px;opacity:.75;min-width:52px}   /* TK_V1.0.73 GIF */
.g20R button{padding:7px 10px!important;font-size:13px!important;font-weight:600!important;border-radius:9px!important}.g20R button.on{background:rgba(77,201,255,.2)!important;border-color:#4dc9ff!important;color:#bfeaff!important}
.g20Cap{grid-column:1/-1;display:flex;gap:8px;align-items:center;font-size:13.5px;padding:4px 2px}.g20Cap input{width:20px;height:20px}
.g20L{grid-column:1/-1}.g20St{font-size:13px;padding:8px 10px;border-radius:9px;background:rgba(63,182,242,.1);margin-top:4px}.g20St.bad{background:rgba(255,77,109,.12);color:#ff9fb0}
.g20Ok{display:flex;gap:10px;align-items:center;margin-top:6px}.g20Ok img{width:110px;border-radius:8px;background:#000}.g20Ok b{display:block}.g20Ok small{display:block;font-size:11.5px;opacity:.7;margin:2px 0 6px;word-break:break-all}.g20Ok a.pill{text-decoration:none;color:inherit}
.g20H{font-size:12px;opacity:.65;margin:10px 0 4px}.g20F{display:grid;grid-template-columns:repeat(auto-fill,minmax(72px,1fr));gap:4px}.g20F img{width:100%;border-radius:6px;display:block;background:#000}
.lvsOpt{position:fixed;inset:0;z-index:2147483100;background:rgba(0,0,0,.35);display:flex;align-items:flex-end;justify-content:center}   /* TK_V1.0.71 */
.lvsOptB{width:min(520px,100%);background:var(--panel,#171a21);border:1px solid var(--line,#2a3340);border-radius:16px 16px 0 0;padding:12px 12px calc(14px + env(safe-area-inset-bottom,0px));display:grid;grid-template-columns:1fr 1fr;gap:8px;animation:lvaIn .18s ease-out}
.lvsOptT{grid-column:1/-1;font-size:13.5px;opacity:.85;padding:2px 2px 4px}.lvsOptB button{padding:13px 8px;border-radius:12px;border:1px solid var(--line,#2a3340);background:var(--card,#151a21);color:inherit;font:inherit;font-weight:700;font-size:15px}.lvsOptB button.pri{grid-column:1/-1;background:#ff3d63;border-color:#ff3d63;color:#fff;font-size:16px}
.lvsT{-webkit-user-select:none;user-select:none;-webkit-touch-callout:none}
.dtlT{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:8px}.dtlT b{font-size:16px}.dtlT .pill{width:auto!important;flex:none;white-space:nowrap;padding:4px 10px!important;min-height:0}.dtlT span{font-size:12px;opacity:.7}   /* TK_V1.0.49 一天的時間軸 */
.dtlG{font-size:12px}.dtlH,.dtlR{display:grid;grid-template-columns:92px 1fr;gap:6px;align-items:center}.dtlH>div,.dtlR>div{position:relative;height:22px}.dtlH u{position:absolute;text-decoration:none;opacity:.55;font-size:10.5px;transform:translateX(-2px)}
.dtlR{border-top:1px solid var(--line,rgba(150,160,175,.15))}.dtlR>i{font-style:normal;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;cursor:pointer;opacity:.9}.dtlR>div{background:repeating-linear-gradient(90deg,transparent 0 calc(12.5% - 1px),rgba(127,127,127,.15) calc(12.5% - 1px) 12.5%)}
.dtlR s{position:absolute;top:4px;height:14px;border-radius:4px;background:rgba(255,77,109,.35);overflow:hidden;cursor:pointer;box-shadow:inset 0 -3px 0 var(--lc,transparent)}.dtlR s.on{outline:1.5px solid #ff4d6d}.dtlR s b{position:absolute;right:0;top:0;bottom:0;margin-left:auto;display:block;left:auto}
.dtlR s{display:flex}.dtlR s b{position:static;flex:none;background:transparent}.dtlR s::after{content:"";flex:1;background:#4dc9ff;opacity:.85}
.dtlR em{position:absolute;top:0;bottom:0;width:2px;background:#ff4d6d;z-index:2}.dtlR .pd{border:1.5px dashed rgba(180,140,255,.85);background:rgba(180,140,255,.15)!important;box-shadow:none!important;cursor:default}.dtlP i{opacity:.65;font-style:italic}.dtlN .k3{display:inline-block;width:14px;height:8px;border:1.5px dashed rgba(180,140,255,.85);margin:0 3px;vertical-align:middle}   .dtlR .pd::after{display:none}   /* TK_V1.0.60 */
.dtlN{font-size:11.5px;opacity:.7;margin-top:10px;line-height:1.6}.dtlN b{display:inline-block;width:14px;height:8px;border-radius:2px;vertical-align:middle;margin:0 3px}.dtlN .k1{background:#4dc9ff}.dtlN .k2{background:rgba(255,77,109,.35)}
.hoH{display:flex;gap:12px;align-items:center;margin:4px 0 10px}.hoH img{width:56px;height:56px;border-radius:50%;object-fit:cover;background:rgba(127,127,127,.2)}.hoH b{font-size:18px;display:block}.hoH small{font-size:12px;opacity:.7}.hoLive{font-size:12px;color:#ff4d6d}   /* TK_V1.0.42 主播總覽 */
.hoNx{margin:10px 0 0;padding:8px 10px;border-radius:10px;background:rgba(180,140,255,.1);border:1px solid rgba(180,140,255,.35);font-size:13px;line-height:1.55}.hoNx small{display:block;font-size:11.5px;opacity:.75}   /* TK_V1.0.48 */
.pf2Ho{cursor:pointer;text-decoration:underline dotted;text-underline-offset:3px}
.hoWk{display:grid;grid-template-columns:repeat(8,1fr);gap:4px;align-items:end;height:76px}.hoWk div{display:flex;flex-direction:column;align-items:center;justify-content:flex-end;gap:2px}.hoWk s{display:block;width:70%;border-radius:4px 4px 0 0;background:#ffb547}.hoWk small{font-size:9.5px;opacity:.6}   /* TK_V1.0.61 */
.hoGs{font-size:12px;opacity:.8;margin:8px 0 2px}.hoGf{display:flex;align-items:center;gap:8px;width:100%;padding:6px 4px;border:0;border-bottom:1px solid var(--line,rgba(150,160,175,.15));background:transparent;color:inherit;font:inherit;text-align:left;cursor:pointer}.hoGf i{font-style:normal;width:18px;opacity:.6;font-size:12px}.hoGf b{flex:1;font-size:13px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.hoGf small{font-size:11px;opacity:.6}.hoGf em{font-style:normal;font-size:12px;color:#ffb547;min-width:70px;text-align:right}
.hoNt span{white-space:normal;line-height:1.45}
.hoPq{width:100%;padding:9px 12px;margin:6px 0 10px;border-radius:10px;border:1px solid var(--line,rgba(150,160,175,.35));background:transparent;color:inherit;font-size:15px}.hoPk{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:6px}.hoPk button{display:flex;flex-direction:column;align-items:center;gap:3px;padding:10px 6px;border-radius:12px;border:1px solid var(--line,rgba(150,160,175,.25));background:rgba(127,127,127,.06);color:inherit;font:inherit;cursor:pointer}.hoPk img{width:44px;height:44px;border-radius:50%;object-fit:cover}.hoPk b{font-size:13px;max-width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.hoPk small{font-size:11px;opacity:.6}   /* TK_V1.0.66 */
.hoCal{display:grid;grid-template-columns:repeat(7,1fr);gap:3px;max-width:420px}.hoCal u{text-decoration:none;font-size:10.5px;opacity:.55;text-align:center}.hoCal s{text-decoration:none;font-size:10.5px;text-align:center;padding:5px 0;border-radius:5px;background:rgba(127,127,127,.08)}.hoCal s.fu{opacity:.25}.hoCal s.td{outline:1.5px solid #ff4d6d}   /* TK_V1.0.68 */
@@SH23@@
.hpTop{padding:12px 14px;border-radius:12px;margin:4px 0 10px;border:1px solid}.hpTop b{display:block;font-size:17px}.hpTop small{font-size:12px;opacity:.7}.hpTop.ok{border-color:rgba(46,204,113,.55);background:rgba(46,204,113,.1)}.hpTop.warn{border-color:rgba(255,181,71,.6);background:rgba(255,181,71,.1)}.hpTop.bad{border-color:rgba(255,77,109,.65);background:rgba(255,77,109,.12)}   /* TK_V1.0.69 */
.hpI{display:flex;align-items:center;gap:10px;width:100%;padding:9px 6px;border:0;border-bottom:1px solid var(--line,rgba(150,160,175,.18));background:transparent;color:inherit;font:inherit;text-align:left;cursor:pointer}.hpI>span{width:24px;text-align:center;font-size:17px}.hpI div{flex:1;min-width:0}.hpI b{display:block;font-size:14px}.hpI small{display:block;font-size:12px;opacity:.75;line-height:1.45}.hpI i{font-style:normal;opacity:.4}.hpI.bad b{color:#ff8c9f}.hpI.warn b{color:#ffc46b}
.hpX{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:6px}.hpX div{border:1px solid var(--line,rgba(150,160,175,.25));border-radius:10px;padding:8px 10px}.hpX small{display:block;font-size:11px;opacity:.65}.hpX b{font-size:14px}
.hoK{display:grid;grid-template-columns:repeat(4,1fr);gap:6px}.hoK div{border:1px solid var(--line,rgba(150,160,175,.3));border-radius:10px;padding:8px 4px;text-align:center}.hoK b{display:block;font-size:18px}.hoK small{font-size:11px;opacity:.7}
.hoT{font-size:13px;font-weight:700;margin:14px 0 6px;opacity:.9;cursor:pointer;user-select:none}.hoT::after{content:" ▾";opacity:.5;font-weight:400}.hoT.hoTc::after{content:" ▸ 已收合（點一下打開）";font-size:11px}.hoHm{max-width:560px;display:grid;grid-template-columns:18px repeat(24,1fr);gap:2px;font-size:10px}.hoHm i{font-style:normal;opacity:.6;text-align:center}.hoHm u{text-decoration:none;opacity:.5;font-size:9.5px}.hoHm s{display:block;aspect-ratio:1;border-radius:2px;background:#4dc9ff}
.hoLv{display:flex;height:22px;border-radius:7px;overflow:hidden;font-size:11px;font-weight:700;color:#111}.hoLv span{display:flex;align-items:center;justify-content:center;white-space:nowrap;overflow:hidden}
.hoChip{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}.hoChip span{font-size:12px;padding:3px 9px;border-radius:12px;background:rgba(127,127,127,.14)}
.hoS{display:flex;align-items:center;gap:8px;width:100%;padding:8px 4px;border:0;border-bottom:1px solid var(--line,rgba(150,160,175,.2));background:transparent;color:inherit;font:inherit;text-align:left;cursor:pointer}.hoS b{font-size:13px;min-width:56px}.hoS span{flex:1;font-size:12.5px;opacity:.85}.hoS small{font-size:12px;opacity:.7}.hoS em{font-style:normal;font-size:11px;font-weight:800;color:#111;padding:1px 6px;border-radius:6px;min-width:30px;text-align:center}.hoB{margin:12px 0;display:flex;flex-wrap:wrap;gap:6px}.hoB a.pill{text-decoration:none;color:inherit}.hoB .pill{flex:1 1 44%;min-width:0;width:auto;max-width:none;white-space:normal;overflow:visible;text-overflow:clip;height:auto;min-height:36px;padding:8px 10px;text-align:center;line-height:1.3}
.dhhD{border:1px solid var(--line,rgba(150,160,175,.3));border-radius:12px;padding:10px 12px;margin:8px 0}.dhhH{display:flex;justify-content:space-between;font-size:14px;margin-bottom:4px}.dhhH span{font-size:12px;opacity:.7}   /* TK_V1.0.40 */
.dhhR{display:flex;align-items:center;gap:10px;justify-content:space-between;padding:3px 0}.dhhR small{font-size:12px;opacity:.85}.dhhR .bad{color:#ff4d6d}.dhhSv{width:220px;max-width:55%;height:40px}.dhhNo{font-size:12px;opacity:.5}
.dhhA{font-size:13px;padding:7px 10px;border-radius:9px;margin:6px 0;background:rgba(255,181,71,.12);border:1px solid rgba(255,181,71,.5)}.dhhA.bad{background:rgba(255,77,109,.12);border-color:rgba(255,77,109,.6)}.dhhW{font-size:12px;color:#ffb547;margin-left:8px}
.khpBox{width:min(720px,100%)}.khpT{display:flex;justify-content:space-between;align-items:center;font-weight:800;font-size:16px;padding:12px 16px;border-bottom:1px solid var(--line,rgba(150,160,175,.3))}.khpT button{background:transparent;border:0;color:inherit;font-size:15px;cursor:pointer}   /* TK_V1.0.39 */
.khpL{overflow:auto;padding:8px 16px 14px;display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:4px 22px}.khpG>b{display:block;font-size:13px;opacity:.75;margin:10px 0 4px}.khpR{display:flex;gap:10px;align-items:baseline;padding:3px 0;font-size:13px}.khpR kbd{flex:none;min-width:118px;font:600 12px ui-monospace,monospace;padding:2px 7px;border-radius:6px;border:1px solid var(--line,rgba(150,160,175,.4));background:rgba(127,127,127,.12)}
.lvaI{display:flex;align-items:center;gap:8px;padding:9px 10px 9px 12px;border-radius:12px;background:rgba(20,24,32,.95);border:1px solid #ff4d6d;color:#fff;box-shadow:0 6px 20px rgba(0,0,0,.5);cursor:pointer;animation:lvaIn .25s ease-out}
.lvaI b{font-size:14px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:46vw}.lvaI small{font-size:12px;opacity:.75;flex:1;white-space:nowrap}.lvaI button{background:transparent;border:0;color:#aaa;font-size:14px;cursor:pointer;padding:0 2px;width:auto;min-height:0}
@keyframes lvaIn{from{transform:translateY(-8px);opacity:0}to{transform:none;opacity:1}}

.qsOv{position:fixed;inset:0;z-index:2147483250;background:rgba(0,0,0,.55);display:flex;justify-content:center;align-items:flex-start;padding:8vh 12px 12px}   /* TK_V1.0.35 快速找 */
.qsBox{width:min(620px,100%);max-height:80vh;display:flex;flex-direction:column;background:var(--panel,#171a21);border:1px solid var(--line,rgba(150,160,175,.3));border-radius:14px;box-shadow:0 12px 40px rgba(0,0,0,.6);overflow:hidden}
.qsBox input{font-size:16px;padding:14px 16px;border:0;border-bottom:1px solid var(--line,rgba(150,160,175,.3));background:transparent;color:inherit;outline:none}
.qsL{overflow:auto;padding:4px 0}.qsH{font-size:11.5px;opacity:.6;padding:8px 16px 3px}.qsE{opacity:.65;font-size:13px;padding:14px 16px;line-height:1.6}
.qsI{display:flex;align-items:center;gap:10px;width:100%;text-align:left;padding:9px 16px;border:0;background:transparent;color:inherit;cursor:pointer;font:inherit}.qsI span{width:22px;text-align:center}.qsI b{font-weight:600;font-size:14px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:60%}.qsI small{opacity:.6;font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;flex:1}
.qsI.on,.qsI:hover{background:rgba(77,201,255,.14)}.qsF{font-size:11px;opacity:.5;padding:6px 16px;border-top:1px solid var(--line,rgba(150,160,175,.2))}
.qsBtnPc{display:flex;justify-content:space-between;align-items:center;width:100%;margin:0 0 8px;padding:7px 10px;border-radius:9px;border:1px solid var(--line,rgba(150,160,175,.3));background:rgba(127,127,127,.08);color:var(--subtext,#9aa3b2);font:inherit;font-size:13px;cursor:pointer}.qsBtnPc small{opacity:.6;font-size:11px}
.qsBtn{background:transparent;border:0;color:inherit;font-size:17px;padding:2px 6px;cursor:pointer}

.hvSt{font-size:12.5px;opacity:.8;margin:4px 0 8px}.hvR{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin:6px 0}.hvR div{border:1px solid var(--line);border-radius:10px;padding:8px;display:flex;flex-direction:column;align-items:center}.hvR b{font-size:16px}.hvR small{font-size:11px;opacity:.7}.hvE{font-size:13px;line-height:1.6;margin:6px 0}.hvI{display:grid;grid-template-columns:1fr 1fr;gap:6px}.hvI figure{margin:0}.hvI img{width:100%;border-radius:8px;background:#000}.hvI figcaption{text-align:center;font-size:12px;opacity:.75}   /* TK_V1.0.32 */
/* LVS-CSS-BEGIN */
.lvsPage{display:flex;flex-direction:column;min-height:0}
@@SH24@@
.lvsKindOv{position:fixed;inset:0;z-index:9700;background:rgba(0,0,0,.55);display:flex;align-items:center;justify-content:center;padding:14px}
.lvsKindW{background:var(--panel,#161a21);color:var(--text,#e8ecf1);border-radius:16px;width:min(520px,100%);max-height:92vh;overflow:auto;padding:14px;display:flex;flex-direction:column;gap:10px;box-shadow:0 20px 60px rgba(0,0,0,.5)}
.lvsKindH{display:flex;align-items:center;justify-content:space-between;gap:8px}.lvsKindH b{font-size:16px}.lvsKindH .pill{flex:none;width:auto}
.lvsKindI{display:flex;gap:12px;align-items:center;text-align:left;padding:12px 14px;border-radius:12px;border:1.5px solid var(--border,#2b313c);border-left:5px solid var(--c);background:var(--bg,#0f1115);color:inherit;cursor:pointer}
.lvsKindI:hover,.lvsKindI.on{border-color:var(--c)}.lvsKindI i{font-style:normal;font-size:26px;flex:none}.lvsKindI b{display:block;font-size:15px;color:var(--c)}.lvsKindI small{display:block;font-size:12px;color:var(--subtext,#8a93a3);line-height:1.45;margin-top:2px}.lvsKindI .lvsKn{color:var(--text,#e8ecf1);font-weight:700}
.lvsKindB{flex:none;height:34px;padding:0 10px;border-radius:9px;border:1.5px solid var(--c);background:transparent;color:var(--c);font-weight:800;font-size:13px;white-space:nowrap;cursor:pointer;margin-right:6px}   /* TK_V0.9.80 */
.lvpTop{flex-wrap:wrap}.lvpTop>b{white-space:nowrap}.lvpTop>#lvsCnt{flex-basis:100%}
.lvsPage [data-orph]{display:none!important}   /* TK_V0.9.81 冗餘改從「要看哪一種」進去 */
/* LVS-CSS-END */

/* LVP-CSS-BEGIN */
.lvpPage{height:100%;min-height:0}
.lvp{display:grid;grid-template-columns:minmax(360px,32%) 8px 1fr;gap:0 4px;height:100%;min-height:0}
.lvpL{display:flex;flex-direction:column;gap:6px;min-height:0;overflow:hidden;border-right:1px solid var(--border,#2b313c);padding-right:8px}
.lvpTop{display:flex;align-items:center;gap:8px}.lvpTop b{font-size:15px}.lvpTop small{color:var(--subtext,#8a93a3);font-size:11.5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.lvpTree{max-height:150px;overflow:auto;font-size:12.5px;border:1px solid var(--border,#2b313c);border-radius:8px;padding:3px}
.lvpTi{padding:3px 6px;border-radius:6px;cursor:pointer;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.lvpTi.sub{padding-left:18px}
.lvpTi b{color:var(--text,#e8ecf2)}.lvpTi small{color:var(--subtext,#8a93a3)}.lvpTi:hover{background:rgba(127,127,127,.12)}.lvpTi.on{background:rgba(77,201,255,.18);outline:1px solid #4dc9ff}
.lvpChips{display:grid;grid-template-columns:repeat(4,1fr);gap:4px}
.lvpChips button{display:flex;flex-direction:column;align-items:center;padding:4px 2px;border-radius:8px;border:1.5px solid var(--c);background:transparent;color:var(--c);cursor:pointer;line-height:1.15}
.lvpChips button b{font-size:12px}.lvpChips button small{font-size:10.5px;opacity:.85}.lvpChips button.on{background:var(--c);color:#111}
.lvpProg{position:relative;height:14px;border-radius:7px;background:rgba(127,127,127,.18);overflow:hidden}.lvpProg i{position:absolute;left:0;top:0;bottom:0;background:#45d483}
.lvpProg span{position:absolute;inset:0;text-align:center;font-size:10.5px;line-height:14px;color:var(--text,#e8ecf2)}
.lvpRow{display:flex;gap:6px;align-items:center;flex-wrap:wrap}.lvpRow select{padding:4px 6px;border-radius:8px;border:1px solid var(--border,#2b313c);background:var(--panel,#1b1f27);color:inherit}
.lvpQ{flex:0 0 auto;width:100%;box-sizing:border-box}
.lvpCards{flex:1 1 0;min-height:0;overflow-y:auto;overflow-x:hidden;display:grid;grid-template-columns:repeat(auto-fill,minmax(104px,1fr));grid-auto-rows:max-content;gap:6px;align-content:start;align-items:start;padding:2px}
.lvsSI.lvpC{height:auto;min-height:0;flex:none;width:auto;display:block;border:2px solid var(--lc,transparent);border-radius:8px;background:var(--panel,#161a21);opacity:1;overflow:hidden}
.lvsSI.lvpC.graded{opacity:.62}.lvsSI.lvpC.cur{border-color:#4dc9ff;opacity:1;box-shadow:0 0 0 2px rgba(77,201,255,.35)}
.lvpIm{position:relative;height:0;padding-bottom:133%;background:#14171d;overflow:hidden}.lvpIm img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block}   /* TK_V0.8.98 固定比例（不靠 aspect-ratio，場次很多也不會被擠扁） */
.lvpIm .lvsSG{top:3px;right:3px;font-size:10px}
.lvpE{position:absolute;right:3px;top:22px;font-style:normal;font-size:10px;padding:0 4px;border-radius:5px;background:rgba(0,0,0,.6);color:#bbb}.lvpE.on{background:#2ecc71;color:#111;font-weight:800}
.lvpDu{position:absolute;right:3px;bottom:3px;font-size:10px;padding:0 4px;border-radius:4px;background:rgba(0,0,0,.65);color:#fff}
.lvpNm{font-size:11.5px;font-weight:700;padding:2px 4px 0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.lvpC small{display:block;font-size:10px;color:var(--subtext,#8a93a3);padding:0 4px 3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.lvpC small u{text-decoration:none;color:#ffc94d;font-weight:800}
.lvpFoot{font-size:11.5px;color:var(--subtext,#8a93a3);padding:2px}
.lvpR{display:flex;flex-direction:column;min-width:0;min-height:0}
.lvpHd b{font-size:16px}.lvpHd small{color:var(--subtext,#8a93a3)}.lvpHd div{font-size:12px;color:var(--subtext,#8a93a3)}
.lvpTb{display:flex;flex-wrap:wrap;gap:5px;align-items:center;padding:6px 0;font-size:12.5px}
.lvpTb button{padding:5px 10px;border-radius:8px;border:1px solid var(--border,#2b313c);background:var(--panel,#1b1f27);color:inherit;cursor:pointer;font-weight:700;font-size:12.5px}
.lvpTb button.pri{background:#ff2d55;border-color:#ff2d55;color:#fff}.lvpTb button:disabled{opacity:.45;cursor:default}
.lvpTb .lvpLv{border:2px solid var(--c);color:var(--c);background:transparent;min-width:44px}.lvpTb .lvpLv.on{background:var(--c);color:#111}
.lvpTb select{padding:4px 6px;border-radius:8px;border:1px solid var(--border,#2b313c);background:var(--panel,#1b1f27);color:inherit}
.lvpTb .lvsDef{margin-left:0;font-size:11.5px;display:flex;align-items:center;gap:3px}.lvpSp{width:8px}
.lvpHint{font-size:11.5px;color:var(--subtext,#8a93a3);padding-bottom:4px}
.lvpBox{flex:1;min-height:0}
.lvpPage .lvsH{background:var(--bg,#0f1115)}
.lvpE.run{background:#ff8c42;color:#111;font-weight:800}
.lvsSI.lvpC.eRun{border-color:#ff8c42}.lvsSI.lvpC.eOk{border-color:#2ecc71}.lvsSI.lvpC.cur{border-color:#4dc9ff}
.lvpIm .lvsSG{left:auto}
.lvpTop small{white-space:normal!important;overflow:visible!important;line-height:1.3}
.lvpTop .lvsBk{display:none}label:has(#lvsDef){display:none}
.lvpSplit{cursor:col-resize;display:flex;align-items:center;justify-content:center;touch-action:none;user-select:none;border-radius:4px}.lvpSplit i{display:block;width:3px;height:48px;border-radius:2px;background:rgba(140,150,165,.45)}
.lvpSplit:hover i,.lvpSplit.on i{background:#4dc9ff;height:100%}.lvpSplit:hover,.lvpSplit.on{background:rgba(77,201,255,.08)}   /* TK_V0.9.43 */
.lvpL{border-right:0!important;padding-right:2px!important}
/* LVP-CSS-END */

/* CLP-CSS-BEGIN */
.clpPage{display:flex;flex-direction:column}
.clpG{display:grid;grid-template-columns:repeat(auto-fill,minmax(104px,1fr));grid-auto-rows:max-content;gap:6px;padding:2px}
.clpC{border-radius:8px;overflow:hidden;background:var(--panel,#161a21);border:1px solid var(--border,#2b313c);cursor:pointer}
.clpIm{position:relative;height:0;padding-bottom:133%;background:#14171d;overflow:hidden}.clpIm img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.clpIm i{position:absolute;left:3px;top:3px;font-style:normal;font-size:10px;padding:0 4px;border-radius:5px;background:#2ecc71;color:#111;font-weight:800}
.clpIm b{position:absolute;right:3px;bottom:3px;font-size:10px;padding:0 4px;border-radius:4px;background:rgba(0,0,0,.65);color:#fff}
.clpNm{font-size:11.5px;font-weight:700;padding:2px 4px 0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.clpC small{display:block;font-size:10px;color:var(--subtext,#8a93a3);padding:0 4px 3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.clpC small u{text-decoration:none;color:#ffc94d;font-weight:800}
.clpMore{grid-column:1/-1;text-align:center;padding:14px;color:var(--subtext,#8a93a3)}
/* CLP-CSS-END */

@@SH25@@

@@SH26@@

@@SH27@@
.rvGPa{display:flex;gap:6px;margin-top:9px;flex-wrap:wrap}.rvGPz{margin-top:7px}.rvGPa .rvGPpz{color:#f0ad4e;border-color:#f0ad4e66}.rvGPpzs{color:#f0ad4e;font-weight:700;margin-bottom:3px}.rvC.rvPz{filter:grayscale(1);opacity:.62}.rvC.rvPz:hover{opacity:.85}.rvPzH{margin-top:14px;border-top:1px dashed #8a93a366;padding-top:10px}.rvGPpzl{font-size:11.5px;opacity:.85;margin:2px 0 4px;line-height:1.5}.rvGPa button{flex:1;padding:8px 10px;border-radius:10px;border:1px solid var(--border,#3a414d);background:transparent;color:inherit;font-size:13px;white-space:nowrap}.rvGPa .rvGPdel{color:#ff6b81;border-color:#ff6b8166}.rvGPa .rvGPclip{color:#ffc94d;border-color:#ffc94d66}.rvGPh small{opacity:.7}   /* TK_V1.0.88 */
.rvGPs{font-size:12px;line-height:1.55;padding:6px 6px 4px;margin:0 0 4px;border-radius:9px;background:rgba(255,255,255,.04);max-width:360px}.rvGPs b{font-size:13px}
.rvGPl{display:flex;flex-wrap:wrap;gap:4px 10px;margin-top:3px}.rvGPl span{color:var(--c)}.rvGPm{display:flex;flex-wrap:wrap;gap:3px 10px;margin-top:3px}.rvGPm .rvGPd{color:#ff6b81;font-weight:700;flex:1 1 100%}.rvGPm span{min-width:0}.rvGPm span:not(.rvGPd){white-space:nowrap}   /* TK_V1.0.94 原本 class="d" 撞到全域的狀態小圓點（寬高 9px）→ 被擠成一個字一行；改名＋自己一整行 */.rvGPm small{font-weight:400;opacity:.8}.rvGPe{opacity:.85;margin-top:3px}   /* TK_V1.0.90 */
@@SH28@@
.cuBox{padding:10px 12px;border:1px solid #3a7bd5;border-radius:12px;background:rgba(58,123,213,.08);line-height:1.55}.cuS{opacity:.7;font-size:12px}.cuT{margin-top:4px}.cuN{margin-top:4px;font-size:13px;opacity:.9}.cuW{color:#f0ad4e}.cuR{display:flex;gap:6px;flex-wrap:wrap;justify-content:flex-end;margin-top:8px}.cuBar{height:6px;border-radius:3px;background:rgba(127,127,127,.25);margin:6px 0 4px;overflow:hidden}.cuBar i{display:block;height:100%;background:#3a7bd5}
#migFab{position:fixed;left:10px;bottom:14px;z-index:9680;max-width:min(92vw,420px);padding:8px 14px;border-radius:14px;background:#1d4f7a;color:#fff;box-shadow:0 6px 22px rgba(0,0,0,.45);cursor:pointer;display:flex;flex-direction:column;gap:2px;font-size:14px}#migFab small{opacity:.85;font-size:12px}#migFab.ok{background:#1f7a4a}
.mrgHead{margin-bottom:10px}.mrgBox{padding:10px 12px;border-radius:12px;background:rgba(127,127,127,.12);margin:8px 0}.mrgBox.ok{background:rgba(69,212,131,.14)}.mrgBox.bad{background:rgba(255,80,80,.14)}.mrgBar{display:flex;gap:6px;align-items:center;flex-wrap:wrap;margin:8px 0}.mrgBar span{flex:1 1 100%}.mrgBar .btn{flex:0 0 auto;width:auto;max-width:none;min-width:0;white-space:nowrap;overflow:visible;padding:6px 12px}.mrgBar .btn.start{margin-left:auto}.mrgG{display:flex;gap:10px;align-items:flex-start;padding:10px 12px;border:1px solid rgba(127,127,127,.25);border-radius:12px;margin:6px 0;cursor:pointer}.mrgG.on{border-color:#3a7bd5;background:rgba(58,123,213,.08)}.mrgG input{margin-top:4px;transform:scale(1.3)}.mrgT{line-height:1.5}.mrgS{display:flex;flex-wrap:wrap;gap:4px 12px;font-size:12.5px;opacity:.85;margin-top:3px}
.ruHead{margin-bottom:10px}.ruQ{width:100%;box-sizing:border-box;margin:8px 0;padding:9px 12px;border-radius:12px;border:1px solid var(--line,rgba(127,127,127,.3));background:transparent;color:inherit;font:inherit}
.ruToc{display:flex;flex-wrap:wrap;gap:6px}.ruToc button{border:1px solid var(--c);background:transparent;color:inherit;border-radius:16px;padding:4px 10px;font:inherit;font-size:13px;cursor:pointer}
.ruC{border:1px solid rgba(127,127,127,.25);border-left:4px solid var(--c);border-radius:12px;margin:10px 0;overflow:hidden;scroll-margin-top:8px}
.ruC h3{margin:0;padding:10px 12px;display:flex;gap:8px;align-items:center;cursor:pointer;font-size:16px;background:rgba(127,127,127,.06)}.ruC h3 em{margin-left:auto;font-style:normal;font-size:12px;opacity:.6}.ruC h3 i{font-style:normal;opacity:.6}
.ruB{display:none;padding:2px 12px 10px}.ruC.on .ruB{display:block}
.ruI{padding:8px 0;border-bottom:1px dashed rgba(127,127,127,.2)}.ruI:last-child{border-bottom:0}.ruI h4{margin:4px 0 6px;font-size:14.5px;color:var(--c)}
.ruI ul{margin:4px 0;padding-left:20px;line-height:1.65}.ruI li{margin:2px 0}
.ruFlow{display:flex;flex-wrap:wrap;align-items:center;gap:4px;margin:6px 0 8px}.ruChip{border:1px solid var(--c,#888);background:color-mix(in srgb,var(--c,#888) 14%,transparent);border-radius:10px;padding:5px 9px;font-size:13px;font-weight:700}.ruAr{font-style:normal;opacity:.6}
.ruBar{display:flex;border-radius:10px;overflow:hidden;margin:6px 0 8px;font-size:12px;font-weight:700}.ruBar span{background:color-mix(in srgb,var(--c) 35%,transparent);padding:6px 8px;text-align:center;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ruT{border-collapse:collapse;width:100%;font-size:13px;margin:6px 0}.ruT th,.ruT td{border:1px solid rgba(127,127,127,.25);padding:5px 7px;text-align:left;vertical-align:top}.ruT th{background:rgba(127,127,127,.1)}
.ruG{display:inline-block;min-width:26px;text-align:center;border-radius:7px;padding:1px 5px;margin-right:6px;background:var(--c);color:#111;font-weight:900}
.ruLv{display:flex;gap:6px;flex-wrap:wrap;margin:6px 0}.ruLv span{border:2px solid var(--c);border-radius:10px;padding:5px 12px;font-weight:800}
.ruQuad{display:grid;grid-template-columns:1fr 1fr;gap:4px;max-width:300px;margin:6px 0}.ruQuad span{border:1px solid rgba(127,127,127,.35);border-radius:8px;padding:8px;text-align:center;font-size:12.5px}
.ruNone{padding:20px;text-align:center;opacity:.7}
.ruV{display:inline-flex;align-items:center;gap:3px;border-bottom:1px dashed var(--c,#888);cursor:pointer;padding:0 2px;border-radius:4px}.ruV:hover{background:rgba(127,127,127,.15)}.ruV i{font-style:normal;font-size:11px;opacity:.55}.ruV small{font-size:11px;opacity:.6;font-weight:400}.ruV.ed{background:rgba(58,123,213,.15);padding:2px 6px;border-bottom:0;cursor:default}.ruV.done{background:rgba(69,212,131,.3)}.ruIn{width:84px;padding:3px 6px;border-radius:6px;border:1px solid #3a7bd5;background:transparent;color:inherit;font:inherit;font-weight:800}.ruCk{display:inline-flex;align-items:center;gap:3px;font-size:12.5px;opacity:.5;white-space:nowrap}.ruCk.go{opacity:1;color:#45d483;font-weight:800}.ruCk input{transform:scale(1.25)}.ruX{border:0;background:transparent;color:inherit;cursor:pointer;opacity:.6}
.ytInf{margin:8px 0;padding:8px 12px;border-radius:10px;border:1px solid rgba(77,201,255,.4);background:rgba(77,201,255,.07);line-height:1.6}.ytInf small{opacity:.7}.ytInf .w,.ytEta .w{color:#f0ad4e}
.ruWarn{border:2px solid #ff4d6d;background:rgba(255,77,109,.1);border-radius:10px;padding:8px 12px;margin:6px 0 8px;line-height:1.6}
.lvsColW{display:inline-flex;align-items:center;gap:4px;white-space:nowrap}.lvsColW input[type=range]{width:120px}.lvsColW input[type=number]{width:52px;padding:2px 4px;border-radius:6px;border:1px solid var(--line,#444);background:transparent;color:inherit;font:inherit;text-align:center}.lvsColB{padding:2px 8px}
.lvsDense .lvsT span{font-size:9px;transform:scale(.85);transform-origin:left bottom}.lvsDense2 .lvsT span{display:none}
</style></head>
<body><div id="app"><aside id="side"><div id="sdCount">● 0 / 0 直播間</div><div class="ss"><button class="sstart" id="btnStart">▶ 開始監控</button><button class="sstop" id="btnStop">■ 停止監控</button></div><div id="sdStatus">● 連線中...</div><nav id="nav"></nav><div id="sysBox">電腦狀態讀取中…</div><button id="netBtn">⬇ —
本日 — MB</button><button id="qBtn" title="排隊轉檔的數量、還要搬到 HDD 的 MP4 大小、全部處理完（轉檔＋搬檔）預估還要多久。點一下看轉檔排隊">🎬 轉檔排隊：讀取中…</button></aside>
<main><div id="tabsRow"><button id="tabMode" title="點一下切換：展開＝完整直播小卡；收合＝照片＋時長＋鑽石愛心；堆疊＝頭像疊在一起"></button><div id="tabs"></div><div id="miniW"></div><div id="topRight"><span><span id="ver"></span> · 網頁版 · __PCNAME__</span><button id="toPhone" title="切回手機版介面">📱 手機版</button></div></div><section id="page"></section>
<footer id="statusBar"><span id="sbMsg"></span><button id="themeBtn" title="這個瀏覽器自己的深色／淺色">◐ 深色／淺色</button><button id="whS" title="滾輪絲滑（緩進緩出）開／關（只影響這個瀏覽器）">滾輪</button><button id="whM" title="滾輪捲慢一點">－</button><span id="whV">×1</span><button id="whP" title="滾輪捲快一點">＋</button><span>介面大小</span><button id="zoomM">－</button><span id="zoomV">100%</span><button id="zoomP">＋</button></footer></main></div>
<script>const THEMES=__THEMES__;const THEME0="__MODE__";
"use strict";
/* ================= V0.6.01 TikLive Monitor 網頁版（電腦版介面） ================= */
const B="__BASE__";
/* V1.1.49 🚀 圖片快速通道：同一個區網、http 時，截圖／預覽大圖／縮圖改從「網頁的埠 +1」那個多執行緒小伺服器拿（不排主程式的隊）；連不到就照原本 */
window.FASTB=window.FASTB||"";function imgB(b){return window.FASTB||b;}
/* V1.1.60 主程式重開後快速通道換了鑰匙：圖片 404 → 重新拿一次鑰匙（10 秒最多一次），這張改用新的（拿不到就走原本的） */
let FASTFIX=null,FASTFT=0;function fastFix(){if(FASTFIX)return FASTFIX;if(Date.now()-FASTFT<10000)return Promise.resolve();FASTFT=Date.now();
  FASTFIX=(async()=>{try{const b=typeof B==="string"?B:"";const j=await fetch(b+"/api/pc/fastimg",{cache:"no-store"}).then(r=>r.json());let nb="";if(j&&j.ok&&j.on&&j.port&&j.key){const fb=`http://${location.hostname}:${j.port}/${j.key}`;for(let i=0;i<7&&!nb;i++){try{const p=await fetch(fb+"/ping",{cache:"no-store"});if(p.ok)nb=fb;}catch(e){}}}window.FASTB=nb;}catch(e){window.FASTB="";}})().finally(()=>{FASTFIX=null;});return FASTFIX;}   /* 舊連線會回 503 並關掉：多試幾次就連到新的 */
window.addEventListener("error",e=>{const t=e.target;try{if(!t||t.tagName!=="IMG"||(t._fr||0)>=2)return;const src=t.getAttribute("src")||"",m=/^https?:\/\/[^/]+:\d+\/[A-Za-z0-9_-]{16,}(\/(?:snap|avatar|media|api)\/.*)$/.exec(src);if(!m||!window.FASTP)return;
  t._fr=(t._fr||0)+1;const rest=m[1],n=t._fr;fastFix().then(()=>{t.src=(n<2&&window.FASTB?window.FASTB:(typeof B==="string"?B:""))+rest;});}catch(x){}},true);   /* 第二次還不行就走原本的 */
(function(){if(window._fjw)return;window._fjw=1;const of0=window.fetch.bind(window),FJ=/\/api\/(replay\?id=|sessions\?|pc\/vg\/sheetinfo\?|pc\/vg\/info\?|pc\/hist\/strip\?|pc\/edit\/list\?|pc\/vb\/note\?|pc\/stt\/sub\?id=\d+$)/;   /* V1.1.50 唯讀資料走快速通道 */
  window.fetch=function(u,o){try{const url=typeof u==="string"?u:"",m=String((o&&o.method)||"GET").toUpperCase(),b=typeof B==="string"?B:"";
    if(m==="GET"&&!window.FASTB&&window.FASTP&&!window.FASTD&&url&&FJ.test(url))return Promise.race([window.FASTP,new Promise(r=>setTimeout(r,700))]).then(()=>{window.FASTD=1;return window.fetch(u,o);});
    if(m==="GET"&&window.FASTB&&url&&FJ.test(url)&&(url.startsWith(b+"/api/")||url.startsWith("/api/"))){const p=url.slice(url.indexOf("/api/"));return of0(window.FASTB+p,{cache:"no-store"}).then(r=>r.ok?r:of0(u,o)).catch(()=>of0(u,o));}}catch(e){}return of0(u,o);};})();
@@SH29@@
setTimeout(()=>{const sd=document.getElementById("side");if(sd&&!document.getElementById("qsBtn")){const b=document.createElement("button");b.id="qsBtn";b.className="qsBtnPc";b.innerHTML="🔍 快速找 <small>Ctrl+K · ? 快速鍵</small>";b.onclick=qsOpen;sd.insertBefore(b,sd.firstChild);}},0);
/* QSK-END */
/* LVA-BEGIN TK_V1.0.38 開播提醒：重點主播（或全部）開播時跳一條提示＋震動；頁面開著就會提醒（在別的分頁也會） */
const LVA={prev:null,t:0};
function lvaMode(){try{return localStorage.getItem("lva_mode")||"pri";}catch(e){return "pri";}}
async function lvaTick(){clearTimeout(LVA.t);LVA.t=setTimeout(lvaTick,document.hidden?90000:30000);const md=lvaMode();if(md==="off"){LVA.prev=null;return;}
  let j=null;try{const r=await fetch(B+"/api/pc/livenow",{cache:"no-store"});j=r.ok?await r.json():null;}catch(e){}if(!j||!j.live)return;
  const now=new Set(j.live.map(x=>x[0]));if(LVA.prev===null){LVA.prev=now;return;}
  const nw=j.live.filter(x=>!LVA.prev.has(x[0])&&(md==="all"||x[2]));LVA.prev=now;if(!nw.length)return;
  try{if(navigator.vibrate)navigator.vibrate([120,60,120]);}catch(e){}
  for(const x of nw.slice(0,3))lvaShow(x);}
function lvaShow(x){let w=document.getElementById("lvaW");if(!w){w=document.createElement("div");w.id="lvaW";w.className="lvaW";document.body.appendChild(w);}
  const d=document.createElement("div");d.className="lvaI";d.innerHTML=`<span>🔴</span><b>${esc(x[1]||x[0])}</b><small>${x[2]?"⭐ 重點主播 · ":""}開播了</small><button data-x="1">✕</button>`;
  d.onclick=e=>{d.remove();if(e.target.closest("[data-x]"))return;if(typeof PAGES!=="undefined"&&typeof go==="function")go(0);else location.hash="live";};w.appendChild(d);setTimeout(()=>d.remove(),20000);}
document.addEventListener("visibilitychange",()=>{if(!document.hidden)lvaTick();});setTimeout(lvaTick,3000);
/* LVA-END */
/* TK_V1.0.55 電腦網頁：分頁標題前面顯示待處理數（跟手機紅點同一套） */
const PC_TODO_K=["nvexp","orphm","pup","ytauth","mem","guard","err","dhealth","pfx"];
async function pcTodo(){clearTimeout(window._pcTodoT);window._pcTodoT=setTimeout(pcTodo,300000);if(document.hidden)return;let j=null;try{j=await api("/api/pc/smart/sum");}catch(e){}if(!j||!j.items)return;
  const n=j.items.filter(x=>PC_TODO_K.includes(x.k)&&(x.lv==="warn"||x.lv==="bad")).length;const b0=document.title.replace(/^\(\d+\) /,"");document.title=n?`(${n}) ${b0}`:b0;}
setTimeout(pcTodo,9000);document.addEventListener("visibilitychange",()=>{if(!document.hidden)setTimeout(pcTodo,1500);});
/* KHP-BEGIN TK_V1.0.39 按 ? 看所有快速鍵 */
const KHP=[["整個網頁",[["Ctrl+K 或 /","🔍 快速找：頁面、工具、主播、場次、設定"],["?","這張快速鍵表"],["Esc","關掉視窗"]]],
 ["檔案總管（連續分級）",[["1 2 3 4 5","標 −2 −1 0 +1 +2"],["→ / PageDown","下一場"],["← / PageUp","上一場"],["Esc","清掉選取"]]],
 ["影片瀏覽（大圖播放）",[["空白鍵","播放／暫停"],["→ ←","快轉／倒退 10 秒"],["↑ ↓","快轉／倒退 1 分鐘"],["PageDown / PageUp","下一支／上一支"],["Ctrl+PageDown","跳過這支"],["Delete","刪掉這支（會先問）"]]],
 ["片段播放視窗",[["→ ↓ / ← ↑","下一段／上一段"],["空白鍵","播放／暫停"],["Esc","關掉"]]]];
function khpOpen(){if(document.getElementById("khpOv"))return;const o=document.createElement("div");o.id="khpOv";o.className="qsOv";
  o.innerHTML=`<div class="qsBox khpBox"><div class="khpT">⌨ 快速鍵<button data-x="1">✕</button></div><div class="khpL">${KHP.map(([g,L])=>`<div class="khpG"><b>${g}</b>${L.map(([k,t])=>`<div class="khpR"><kbd>${k}</kbd><span>${t}</span></div>`).join("")}</div>`).join("")}</div></div>`;
  o.onclick=e=>{if(e.target===o||e.target.closest("[data-x]"))o.remove();};document.body.appendChild(o);}
document.addEventListener("keydown",e=>{const t=e.target,ed=t&&(t.isContentEditable||/^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName));if(ed)return;
  if(e.key==="?"&&!e.ctrlKey&&!e.altKey){e.preventDefault();const o=document.getElementById("khpOv");if(o)o.remove();else khpOpen();}else if(e.key==="Escape"){const o=document.getElementById("khpOv");if(o)o.remove();}});
/* KHP-END */
/* TK_V1.0.27 電腦已經熱更新、這頁還是舊版：上方出現提示（不自動重新整理，免得中斷上傳／播放） */
const PAGEV="__APPVER__";
async function verWatch(){clearTimeout(window._verT);window._verT=setTimeout(verWatch,60000);if(document.hidden||PAGEV.startsWith("__"))return;let j=null;
  try{const r=await fetch(B+"/api/update/status",{cache:"no-store"});if(!r.ok)return;j=await r.json();}catch(e){return;}
  if(!j||!j.current||j.current===PAGEV)return;let b=document.getElementById("verBar");
  if(!b){b=document.createElement("div");b.id="verBar";b.className="verBar";document.body.appendChild(b);
    b.onclick=e=>{if(e.target.closest("[data-vx]")){b.remove();clearTimeout(window._verT);window._verT=setTimeout(verWatch,30*60000);return;}
      if(typeof PUP!=="undefined"&&PUP.run&&!confirm("手機還在上傳，重新整理會中斷（之後再選一次檔案會接著傳）。確定要重新整理？"))return;location.reload();};}
  b.innerHTML=`<span>🆕 電腦已經更新到 <b>V${j.current}</b>（這頁還是 V${PAGEV}）</span><button>重新整理</button><button data-vx="1" title="30 分鐘後再提醒">✕</button>`;}
setTimeout(verWatch,20000);document.addEventListener("visibilitychange",()=>{if(!document.hidden)setTimeout(verWatch,2000);});

const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];
const esc=s=>String(s==null?"":s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const p2=n=>String(Math.floor(n)).padStart(2,"0");
const fmtE=s=>{s=Math.max(0,Math.floor(+s||0));return p2(s/3600)+":"+p2(s%3600/60)+":"+p2(s%60);};
const fmtClk=ts=>{if(!ts)return"";const d=new Date(ts*1000);return p2(d.getHours())+":"+p2(d.getMinutes())+":"+p2(d.getSeconds());};
const fmtHM=ts=>{if(!ts)return"";const d=new Date(ts*1000),t=new Date();return (d.toDateString()===t.toDateString()?"":(d.getMonth()+1)+"/"+d.getDate()+" ")+p2(d.getHours())+":"+p2(d.getMinutes());};
const kf=n=>{n=+n||0;if(n<1000)return n.toLocaleString();if(n<999950)return (n/1000).toFixed(1).replace(/\.0$/,"")+"K";return (n/1e6).toFixed(2).replace(/0+$/,"").replace(/\.$/,"")+"M";};
const num=n=>(+n||0).toLocaleString();
const fmtB=b=>{b=+b||0;return b>=1e12?(b/1e12).toFixed(2)+" TB":b>=1e9?(b/1e9).toFixed(2)+" GB":b>=1e8?(b/1e6).toFixed(0)+" MB":b>=1e6?(b/1e6).toFixed(1)+" MB":b>=1e3?(b/1e3).toFixed(0)+" KB":b.toFixed(0)+" B";};
const fmtR=b=>{b=+b||0;return b<1024?b.toFixed(0)+" B/s":b<1048576?(b/1024).toFixed(0)+" KB/s":(b/1048576).toFixed(1)+" MB/s";};
const fmtMb=b=>{const v=(+b||0)*8/1e6;return (v>=100?v.toFixed(0):v.toFixed(1))+" Mbps";};
const fmtDur=s=>{s=Math.max(0,Math.round(+s||0));const h=s/3600|0,m=(s%3600)/60|0;return h?`${h} 小時 ${m} 分`:m?`${m} 分 ${p2(s%60)} 秒`:`${s} 秒`;};
const LS={get(k,d){try{const v=localStorage.getItem("tlmpc_"+k);return v==null?d:JSON.parse(v);}catch(e){return d;}},set(k,v){try{localStorage.setItem("tlmpc_"+k,JSON.stringify(v));}catch(e){}}};
async function api(p){const r=await fetch(B+p,{cache:"no-store"});if(r.status===401){location.href=B+"/";throw new Error("login");}return r.json();}
let PW=sessionStorage.getItem("tlmpc_pw")||"";
async function post(p,data,raw){
  for(let i=0;i<2;i++){
    const r=await fetch(B+p,{method:"POST",cache:"no-store",headers:{"Content-Type":raw?"text/plain;charset=utf-8":"application/json"},body:raw?data:JSON.stringify(Object.assign({pw:PW},data||{}))});
    let j={};try{j=await r.json();}catch(e){}
    if(r.status===401&&i===0&&(j.pw||/密碼/.test(j.message||""))){const v=await askPw();if(v==null)return {ok:false,message:"已取消"};PW=v;sessionStorage.setItem("tlmpc_pw",v);continue;}
    if(!r.ok&&j.ok===undefined)j.ok=false;return j;}
  return {ok:false,message:"密碼不對"};}
function askPw(){return new Promise(res=>{dialog("需要網頁密碼",`<div class="sub" style="margin-bottom:8px">這個動作會改動電腦上的程式，請輸入網頁密碼（只記在這個分頁，關掉就忘記）。</div><input type="password" id="pwI" style="width:100%">`,[["取消",()=>res(null)],["確定",()=>res($("#pwI").value),"start"]]);setTimeout(()=>{const i=$("#pwI");if(i){i.focus();i.onkeydown=e=>{if(e.key==="Enter"){closeDlg();res(i.value);}};}},30);});}
function toast(m,ms=2600){const t=document.createElement("div");t.className="toast";t.textContent=m;document.body.appendChild(t);setTimeout(()=>t.remove(),ms);}
function sb(m){$("#sbMsg").textContent=m;S.sbT=Date.now();}
/* ---------- menus & dialogs ---------- */
function closeMenu(){$$(".menu").forEach(m=>m.remove());}
function menu(items,x,y){closeMenu();const m=document.createElement("div");m.className="menu";
  items.forEach(it=>{if(!it)return;if(it.sep){m.appendChild(document.createElement("hr"));return;}const d=document.createElement("div");
    d.innerHTML=it.html||esc(it.label);if(it.cls)d.className=it.cls;if(it.dis)d.classList.add("dis");
    if(it.sub){d.innerHTML+=" ▸";d.onclick=e=>{e.stopPropagation();const r=d.getBoundingClientRect();menu(it.sub,r.right-4,r.top);};}
    else if(!it.dis)d.onclick=e=>{e.stopPropagation();closeMenu();it.act&&it.act();};m.appendChild(d);});
  document.body.appendChild(m);const r=m.getBoundingClientRect();m.style.left=Math.min(x,innerWidth-r.width-6)+"px";m.style.top=Math.min(y,innerHeight-r.height-6)+"px";}
document.addEventListener("click",closeMenu);document.addEventListener("keydown",e=>{if(e.key==="Escape"){closeMenu();}});
function closeDlg(){$$(".dlgbg").forEach(d=>d.remove());}
function dialog(title,html,btns){closeDlg();const bg=document.createElement("div");bg.className="dlgbg";
  bg.innerHTML=`<div class="dlg"><h3>${esc(title)}</h3><div class="db">${html}</div><div class="btns"></div></div>`;
  const bx=bg.querySelector(".btns");(btns||[["關閉"]]).forEach(([t,fn,cls])=>{const b=document.createElement("button");b.textContent=t;if(cls)b.className=cls;b.onclick=()=>{if(fn&&fn()===false)return;bg.remove();};bx.appendChild(b);});
  document.body.appendChild(bg);return bg;}
const confirmDlg=(title,msg,okText="確定",cls="start")=>new Promise(res=>dialog(title,`<div style="white-space:pre-line">${esc(msg)}</div>`,[["取消",()=>res(false)],[okText,()=>res(true),cls]]));
async function confirmSteps(steps){for(const [t,m,order] of steps){const ok=await new Promise(res=>{const b=order.map(k=>k==="del"?["確定刪除",()=>res(true),"del"]:k==="keep"?["先保留",()=>res(false)]:["取消",()=>res(false)]);dialog(t,`<div style="white-space:pre-line">${esc(m)}</div>`,b);});if(!ok){sb("已取消刪除");return false;}}return true;}
/* ---------- avatar ---------- */
function avHtml(u,has,av,size,cls=""){
  if(has)return `<img class="av ${cls}" src="${imgB(B)}/avatar/${encodeURIComponent(u)}?v=${av||0}" style="width:${size}px;height:${size}px" loading="lazy" onerror="this.replaceWith(avFb('${esc(u)}',${size},'${cls}'))">`;
  return avFbHtml(u,size,cls);}
function avFbHtml(u,size,cls){let h=0;for(const c of String(u))h+=c.codePointAt(0);const light=S.mode==="light";
  return `<span class="avf ${cls}" style="width:${size}px;height:${size}px;background:hsl(${h%360} 47% ${light?72:37}%);font-size:${size*0.42|0}px;color:${light?"#1d2430":"#fff"}">${esc((String(u)[0]||"?").toUpperCase())}</span>`;}
function avFb(u,size,cls){const t=document.createElement("template");t.innerHTML=avFbHtml(u,size,cls);return t.content.firstChild;}
/* ---------- virtual table (same behaviour as the desktop tables: filter, click title to sort, drag to resize) ---------- */
class VT{
  constructor(host,o){this.o=Object.assign({rowH:22,filter:true,blank:2},o);this.cols=o.cols;this.rows=[];this.view=[];this.sort=o.sort||null;this.q="";this.div=null;this.follow=true;this.sel=new Set();
    const key="vt_"+(o.key||"");this.wkey=key;const ws=LS.get(key,null);if(ws&&ws.length===this.cols.length)this.cols.forEach((c,i)=>c.w=ws[i]);
    const al=LS.get("al_"+(o.key||""),null);if(al)this.cols.forEach((c,i)=>{c.al0=c.al0||c.al||"l";if(al[i])c.al=al[i];});else this.cols.forEach(c=>c.al0=c.al0||c.al||"l");
    host.innerHTML="";this.host=host;
    if(o.filter||o.title){const bar=document.createElement("div");bar.className="vtbar";bar.innerHTML=(o.title?`<span class="sec">${esc(o.title)}</span>`:"")+`<span class="grow"></span>`+(o.filter?`<input placeholder="篩選…"><span class="h">點欄位標題排序</span>`:"");host.appendChild(bar);
      const inp=bar.querySelector("input");if(inp)inp.oninput=()=>{this.q=inp.value.trim().toLowerCase();this.refresh();};this.bar=bar;}
    const t=document.createElement("div");t.className="vt";t.innerHTML=`<div class="vth"></div><div class="vtb"><div class="vtsp"></div></div>`;host.appendChild(t);
    this.el=t;this.head=t.querySelector(".vth");this.body=t.querySelector(".vtb");this.sp=t.querySelector(".vtsp");
    this.body.onscroll=()=>{this.head.scrollLeft=this.body.scrollLeft;this.paint();if(this.o.onScroll)this.o.onScroll(this);};
    this.body.addEventListener("dblclick",e=>{const r=e.target.closest(".vr");if(r&&this.o.onDbl&&r.dataset.i)this.o.onDbl(this.rows[+r.dataset.i],e);});
    this.body.addEventListener("contextmenu",e=>{const r=e.target.closest(".vr");if(r&&r.dataset.i&&this.o.onCtx){e.preventDefault();this.o.onCtx(this.rows[+r.dataset.i],e,+r.dataset.i);}});
    this.body.addEventListener("click",e=>{const r=e.target.closest(".vr");if(!r||!r.dataset.i)return;const i=+r.dataset.i;if(e.ctrlKey||e.metaKey){this.sel.has(i)?this.sel.delete(i):this.sel.add(i);}else{this.sel=new Set([i]);}this.paint();if(this.o.onClick)this.o.onClick(this.rows[i],e);});
    new ResizeObserver(()=>this.paint()).observe(this.body);this.header();}
  header(){this._wk="";this.head.innerHTML=this.cols.map((c,i)=>`<div data-c="${i}" style="width:${c.w}px" class="${this.sort&&this.sort[0]===i?(this.sort[1]?"sd":"sa"):""}">${esc(c.t)}<span class="rz"></span></div>`).join("");
    this.head.querySelectorAll("div").forEach(d=>{const i=+d.dataset.c;
      d.onclick=e=>{if(e.target.classList.contains("rz"))return;this.sort=this.sort&&this.sort[0]===i?[i,!this.sort[1]]:[i,true];this.header();if(this.o.onSort&&this.o.onSort(this.sort[0],this.sort[1])){this._srv=true;return;}this._srv=false;this.refresh();};
      d.oncontextmenu=e=>{e.preventDefault();const c=this.cols[i],cur=c.al||"l",set=v=>{this.cols.forEach((x,j)=>{if(v==="all")x.al=cur;else if(j===i)x.al=v==="def"?x.al0:v;});      // V0.6.09 右鍵欄位標題：對齊方式（同電腦版）
          LS.set("al_"+(this.o.key||""),this.cols.map(x=>x.al||"l"));this.paint(true);};
        menu([{label:`「${c.t}」對齊方式`,dis:true},{sep:1},...[["l","靠左"],["c","置中"],["r","靠右"]].map(([v,t])=>({label:(cur===v?"✔ ":"　")+t,act:()=>set(v)})),{sep:1},{label:"回復預設",act:()=>set("def")},{label:"這張表全部欄位都用目前選擇",act:()=>set("all")}],e.clientX,e.clientY);};
      d.querySelector(".rz").onmousedown=e=>{e.preventDefault();e.stopPropagation();const x0=e.clientX,w0=this.cols[i].w;
        const mv=ev=>{this.cols[i].w=Math.max(45,w0+ev.clientX-x0);d.style.width=this.cols[i].w+"px";this.paint(true);};
        const up=()=>{removeEventListener("mousemove",mv);removeEventListener("mouseup",up);LS.set(this.wkey,this.cols.map(c=>c.w));};addEventListener("mousemove",mv);addEventListener("mouseup",up);};});}
  setRows(rows){this.rows=rows;this.sel.clear();this.refresh();}
  push(rows){if(!rows.length)return;const atEnd=this.body.scrollTop+this.body.clientHeight>=this.body.scrollHeight-30;const base=this.rows.length;for(const r of rows)this.rows.push(r);
    if(!this.sort&&!this.q){for(let i=0;i<rows.length;i++)this.view.push(base+i);this.paint(true);if(atEnd&&this.o.stick!==false)this.body.scrollTop=1e9;}else this.refresh();}
  refresh(){const q=this.q,cols=this.cols;let v=[];const R=this.rows;
    for(let i=0;i<R.length;i++){const r=R[i];if(r&&r.__sep){if(!q&&!this.sort)v.push(i);continue;}if(q&&!cols.some(c=>String(this.val(r,c)).toLowerCase().includes(q)))continue;v.push(i);}
    if(this.sort&&!this._srv){const [ci,desc]=this.sort,c=cols[ci];const key=i=>{const x=this.raw(R[i],c);if(typeof x==="number")return x;const s=String(x==null?"":x);if(s==="轉檔中")return -1;const m=s.trim().match(/^(-?[\d,]*\.?\d+)\s*(%|B|KB|MB|GB|TB)?$/i);if(m){const n=parseFloat(m[1].replace(/,/g,""));return n*({KB:1e3,MB:1e6,GB:1e9,TB:1e12}[(m[2]||"").toUpperCase()]||1);}return s;};
      v.sort((a,b)=>{const A=key(a),Bb=key(b),ea=A===""||A==null,eb=Bb===""||Bb==null;if(ea||eb)return ea===eb?0:ea?1:-1;
        let r=(typeof A==="number"&&typeof Bb==="number")?A-Bb:String(A).localeCompare(String(Bb),"zh-Hant");return desc?-r:r;});}
    this.view=v;this.paint(true);}
  raw(r,c){return c.k!=null?r[c.k]:c.v?c.v(r):"";}
  val(r,c){const x=this.raw(r,c);return c.f?c.f(x,r):(x==null?"":x);}
  fitW(){const W=(this.body&&this.body.clientWidth)||0,ws=this.cols.map(c=>c.w),tw=ws.reduce((a,b)=>a+b,0);     /* V0.6.50 欄位總寬不到表格寬：最寬那一欄自動補滿，不留一大塊空白 */
    if(this.o.fill!==false&&W>tw+4){let j=0;ws.forEach((w,i)=>{if(w>ws[j])j=i;});ws[j]+=W-tw-2;}return ws;}
  paint(force){const H=this.o.rowH,n=this.view.length+(this.o.blank||0)+(this.div?1:0),ws=this.fitW(),tw=ws.reduce((a,b)=>a+b,0),wk=ws.join(",");
    if(wk!==this._wk){this._wk=wk;force=true;this.head.querySelectorAll(":scope>div").forEach((d,i)=>{if(ws[i]!=null)d.style.width=ws[i]+"px";});}
    this.sp.style.height=n*H+"px";this.sp.style.width=tw+"px";const st=this.body.scrollTop,vh=this.body.clientHeight||400,a=Math.max(0,Math.floor(st/H)-4),z=Math.min(n,Math.ceil((st+vh)/H)+4);
    if(!force&&this._a===a&&this._z===z&&this._n===n)return;this._a=a;this._z=z;this._n=n;const out=[],dv=this.div;
    for(let k=a;k<z;k++){let vi=k;if(dv){if(k===dv.at){out.push(`<div class="vr div" style="top:${k*H}px;height:${H}px;width:${Math.max(tw,this.body.clientWidth)}px;line-height:${H-2}px">${esc(dv.text)}</div>`);continue;}if(k>dv.at)vi=k-1;}
      if(vi>=this.view.length){out.push(`<div class="vr" style="top:${k*H}px;height:${H}px;width:${tw}px"></div>`);continue;}
      const i=this.view[vi],r=this.rows[i];
      if(r&&r.__sep){out.push(`<div class="vr sep" style="top:${k*H}px;height:${H}px;line-height:${H}px;width:${Math.max(tw,this.body.clientWidth)}px">${esc(r.text)}</div>`);continue;}
      const cls=(this.sel.has(i)?" sel":"")+(this.o.rowCls?" "+(this.o.rowCls(r)||""):"");
      out.push(`<div class="vr${cls}" data-i="${i}" style="top:${k*H}px;height:${H}px;line-height:${H}px">`+this.cols.map((c,ci)=>`<div class="al-${c.al||"l"}" style="width:${ws[ci]}px${c.css?";"+c.css(r):""}">${c.html?c.html(this.raw(r,c),r):esc(this.val(r,c))}</div>`).join("")+"</div>");}
    this.sp.innerHTML=out.join("");}
  setDivider(at,text){this.div=at==null?null:{at,text};this.paint(true);}
  scrollToK(k,pos){const H=this.o.rowH,vh=this.body.clientHeight;this.body.scrollTop=pos==="2nd-last"?Math.max(0,(k+2)*H-vh):Math.max(0,k*H-vh/2);}
  selected(){return [...this.sel].map(i=>this.rows[i]).filter(Boolean);}
}
/* ---------- state, polling, sidebar, nav ---------- */
const S={page:(p=>p===6?0:p===28?29:p===26?31:p)(LS.get("page",0)),tab:null,hist:LS.get("hist",[]),tabMode:LS.get("tabMode","expanded"),pins:LS.get("pins",[]),st:null,mode:"dark",sbT:0,data:{}};
const NAV=[["緊急事件","#ff4d6d",[[37,"緊急處理","🚨"]]],["總覽","#4dc9ff",[[0,"直播總覽","⌂"],[31,"檔案總管","▦"],[38,"主播審核","🗂"],[33,"精選","✨"],[30,"後台狀態","🖥"]]],["目前直播","#45d4b0",[[1,"即時聊天室","◌"],[2,"禮物","◈"],[4,"進入紀錄","↳"],[5,"按讚","♥"]]],
  ["歷史資料","#b48cff",[[7,"歷史直播場次","▤"],[3,"送禮者","◇"],[8,"使用者","◎"]]],["影片工具","#f0ad4e",[[27,"批量剪輯","✂"],[29,"整理 MP4","🗂"],[32,"批量截 20 張","📸"],[34,"YouTube 上傳","▶"],[45,"手機錄屏","📱"],[40,"Chrome 上傳限速","🌐"],[25,"語音轉字幕","🎙"]]],
  ["電腦與檔案","#45d483",[[43,"精選／審核 開關","⏯"],[16,"電腦效能","▦"],[39,"🧪 實驗工作區","🧪"],[17,"開播統計","↗"],[35,"主播特性","🧭"],[36,"每週報告","📰"],[12,"錄音／錄影","◉"],[19,"FLV 待處理","▧"],[20,"影片庫重整","⊞"],[21,"清理工具","✧"],[22,"LOG 與問題","⇪"],[59,"規則說明","📖"],[60,"手機錄特效","📲"],[61,"禮物陣列影片","🎛"],[46,"自動處理紀錄","🕘"],[47,"小檔備份","🗂"],[48,"HEVC 壓縮試算","🧪"],[49,"硬碟健康紀錄","🩺"],[50,"主播總覽","👤"],[53,"一頁健檢","🩺"],[57,"E → R 搬硬碟","💽"],[58,"合併重複場次","⧉"],[55,"顯示卡供需","🎛"],[56,"YouTube 隔離區抽查","🗑"],[51,"一天的時間軸","📅"],[52,"匯出場次表","📤"],[15,"LIVE 時移（BETA）","◷"]]],
  ["設定","#9aa5b3",[[11,"設定","⚙"],[10,"主播清單","☷"],[18,"主播分類","◐"],[24,"連線管控／縮編","⛽"],[23,"送禮動畫","❋"],[9,"連線診斷","⌁"],[14,"線上更新","⟳"],[13,"升級資訊","✦"]]]];
const NAV_OPEN0=["總覽","目前直播","歷史資料","影片工具"];   /* V0.6.95 左邊選單分組可以收合：預設只打開常用的，其他按標題展開（目前這頁所在的組一定打開） */
function applyTheme(mode){S.mode=mode;const t=THEMES[mode]||THEMES.dark,r=document.documentElement.style;for(const k in t)r.setProperty("--"+k,t[k]);document.documentElement.dataset.mode=mode;}
function drawNav(){const op=[...LS.get("navOpen",NAV_OPEN0),"緊急事件"];   /* V0.8.13 緊急事件預設不顯示（設定 →「🚨 顯示緊急處理工具」打開才出現） */
  const FO=window.FEAT_OFF||{};   /* TK_V0.8.93 暫停的精選／審核不顯示 */
  $("#nav").innerHTML=NAV.map(([g,c,items])=>[g,c,items.filter(x=>!((x[0]===33&&FO.hl)||(x[0]===38&&FO.rv))||x[0]===S.page)]).filter(([g,,items])=>items.length&&(g!=="緊急事件"||window.EMG_SHOW||items.some(x=>x[0]===S.page))).map(([g,c,items])=>{const has=items.some(x=>x[0]===S.page),open=has||op.includes(g);
    return `<div class="nh${open?" open":" shut"}" style="color:${c}" data-g="${esc(g)}">${esc(g)}<i></i><em>${open?"▾":"▸ "+items.length}</em></div>`+(open?items.map(([id,t,ic])=>`<div class="ni${S.page===id?" on":""}" data-p="${id}" style="--gc:${c}"><b>${ic}</b>${esc(t)}</div>`).join(""):"");}).join("");
  $$("#nav .ni").forEach(d=>d.onclick=()=>go(+d.dataset.p));
  $$("#nav .nh").forEach(d=>d.onclick=()=>{const g=d.dataset.g,o=LS.get("navOpen",NAV_OPEN0).slice(),i=o.indexOf(g);if(NAV.find(x=>x[0]===g)[2].some(x=>x[0]===S.page))return;if(i>=0)o.splice(i,1);else o.push(g);LS.set("navOpen",o);drawNav();});}
function go(p,arg){S.page=p;LS.set("page",p);drawNav();renderPage(arg);miniSync();}
function sysHtml(rows){if(!rows||!rows.length)return `<div class="sub" style="text-align:center">電腦狀態讀取中…</div>`;   // V0.6.03 和電腦版同樣的列：名稱、彩色進度條、數值、溫度
  const tc=t=>t>=85?"#ff5c5c":t>=70?"#f0ad4e":"#45d483";
  return rows.map(([lab,pct,val,temp,col,busy])=>`<div class="sp"><b>${esc(lab)}</b><span class="spb">${pct!=null?`<i style="width:${Math.max(3,Math.min(100,pct))}%;background:${col}"></i>`:""}${busy!=null?`<u style="width:${Math.max(1.5,Math.min(100,busy))}%;background:${busy>=60?"#f0ad4e":"#4dc9ff"}"></u>`:""}</span><em>${esc(val)}</em><small style="color:${temp?tc(temp):"transparent"}">${temp?Math.round(temp)+"°":"·"}</small></div>`).join("");}
function drawSide(){const s=S.st;if(!s)return;{const el=$("#sdCount");if(s.cnt){const h=`<span class="cDot" style="background:${s.status_color||(s.running?"#45d483":"#7f8a99")}"></span><b class="cBig">${s.cnt[0]}</b><span class="cSm"> / ${s.cnt[1]} 直播間</span>`;if(el._h!==h){el._h=h;el.innerHTML=h;}el.title=`${s.status_text||""}\n目前開播 ${s.cnt[0]} 位 · 監控中 ${s.cnt[1]} 位 · 主播名單 ${s.cnt[2]} 位`.trim();}else el.textContent=s.count_text;}const st=$("#sdStatus");st.textContent=s.status_text||"";st.style.color=s.status_color||"";
  $("#btnStart").disabled=s.stopping;$("#btnStop").disabled=s.stopping;$("#sysBox").innerHTML=sysHtml(s.side);miniSync();
  const n=s.net;$("#netBtn").textContent=`⬇ ${fmtR(n.rx)}　⬆ ${fmtR(n.tx)}\n本日 ${num(Math.round(n.today/1048576))} MB`+(n.nrec?`　錄影 ${n.nrec} 路`:"");{const qb=$("#qBtn"),Q=s.qs;if(qb&&Q){if(qb.textContent!==Q.text)qb.textContent=Q.text;qb.title=`排隊轉檔 ${Q.n} 個 · 還要搬到 HDD 的 MP4 約 ${Q.gb} GB · 全部處理完（轉檔＋搬檔）約還要 ${fmtDur(Q.left)}`+(Q.ssd?`\n（依目前 SSD → HDD 速度約 ${fmtR(Q.rate)} 推算）`:"\n（沒用 SSD 暫存：直接在 HDD 轉檔，不用另外搬）")+"\n點一下看轉檔排隊";}}
  $("#ver").textContent="V"+s.ver;if(s.statusbar&&Date.now()-S.sbT>8000)$("#sbMsg").textContent=s.statusbar;}
async function pollState(){try{const s=await api("/api/pc/state");if(!s||!Array.isArray(s.rooms)){S.stBad=(S.stBad||0)+1;throw new Error("state");}S.stBad=0;S.st=s;   /* TK_V1.0.45 電腦端回錯誤（熱更新中）時保留上一次的狀態，不要整頁壞掉 */
  if(!S.modeSet){applyTheme(LS.get("theme",s.mode));S.modeSet=1;}drawSide();drawTabs();if(PAGES[S.page]&&PAGES[S.page].state)PAGES[S.page].state();}catch(e){S.stBad=(S.stBad||0)+(e&&e.message==="state"?0:1);}
  {let w=document.getElementById("stBad");if(S.stBad>=5&&!w){w=document.createElement("div");w.id="stBad";w.className="verBar";w.style.background="#5a3a12";w.innerHTML="<span>⏳ 電腦端暫時沒有回應（可能在熱更新或很忙），畫面先顯示上一次的資料，好了會自己恢復</span>";document.body.appendChild(w);}else if(S.stBad<5&&w)w.remove();}   /* TK_V1.0.45 */
  clearTimeout(S.stT);S.stT=setTimeout(pollState,document.hidden?6000:2000);}
/* ---------- top tabs (live / history), same three modes as the desktop ---------- */
const liveRooms=()=>{const s=S.st;if(!s)return [];const live=(s.rooms||[]).filter(r=>r.live);const ord=s.tab_order||[];const pins=S.pins;
  live.sort((a,b)=>{const pa=pins.includes(a.u)?0:1,pb=pins.includes(b.u)?0:1;if(pa!==pb)return pa-pb;const ia=ord.indexOf(a.u),ib=ord.indexOf(b.u);return (ia<0?1e4+a.n:ia)-(ib<0?1e4+b.n:ib);});return live;};
function tabTarget(){const live=liveRooms();let t=S.tab;
  if(t&&t.k==="hist"&&S.hist.some(h=>h.sid===t.sid))return t;if(t&&t.k==="live"&&live.some(r=>r.u===t.u))return t;
  if(live.length)return S.tab={k:"live",u:live[0].u};if(S.hist.length)return S.tab={k:"hist",sid:S.hist[0].sid};return S.tab=null;}
function cardHtml(r,cls=""){const ring=r.priority?"pri":"live";return `${avHtml(r.u,r.avatar,r.av,40,ring)}<div class="tx"><b>${esc(r.name)}</b><span class="dl"><span class="dia">💎 ${kf(r.diamonds)}</span>  <span class="lik">♥ ${kf(r.likes)}</span></span><span class="dl grn">${num(r.viewers)} 人 · ${esc(r.elapsed||"--:--:--")}</span></div>`;}
function drawTabs(){const box=$("#tabs");const live=liveRooms(),cur=tabTarget(),m=S.tabMode;let h="";
  for(const r of live){const on=cur&&cur.k==="live"&&cur.u===r.u?" on":"";const pin=S.pins.includes(r.u);
    if(m==="collapsed")h+=`<div class="tb col${on}" data-u="${esc(r.u)}" title="${esc(r.name)}">${avHtml(r.u,r.avatar,r.av,50,r.priority?"pri":"live")}<span class="pill">${num(r.viewers)} 人</span><span class="t1 grn">${esc(r.elapsed||"")}</span><span class="t2"><span class="dia">💎${kf(r.diamonds)}</span> <span class="lik">♥${kf(r.likes)}</span></span></div>`;
    else if(m==="stacked"&&!pin&&!on)h+=`<div class="tb stk" data-u="${esc(r.u)}">${avHtml(r.u,r.avatar,r.av,34,r.priority?"pri":"live")}<div class="tb pop">${cardHtml(r)}</div></div>`;
    else h+=`<div class="tb${on}" data-u="${esc(r.u)}">${cardHtml(r)}</div>`;}
  for(const x of S.hist){const on=cur&&cur.k==="hist"&&cur.sid===x.sid?" on":"";h+=`<div class="tb hist${on}" data-sid="${x.sid}" title="場次 ${String(x.sid).padStart(5,"0")}"><b>${esc(x.name)}</b><small>${liveRooms().some(r=>+r.sid===+x.sid)?'<span style="color:#ff4d6d">● 直播中 · 時移</span>':"已結束 · "+esc(x.dur||"")}</small><span class="x" title="關閉歷史分頁">✕</span></div>`;}
  if(!h)h=`<div class="tb ph">${S.st&&S.st.running?"連線中...":"目前沒有在監控"}</div>`;
  if(box._h!==h){box._h=h;box.innerHTML=h;
    $$(".tb[data-u]",box).forEach(t=>{t.onclick=()=>{S.tab={k:"live",u:t.dataset.u};drawTabs();onTab();};t.oncontextmenu=e=>{e.preventDefault();tabMenu(t.dataset.u,e);};
      const pop=t.querySelector(".pop");if(pop)t.onmouseenter=()=>{const r=t.getBoundingClientRect();pop.style.left=r.left+"px";pop.style.top=(r.top-2)+"px";};});
    $$(".tb.hist",box).forEach(t=>{t.onclick=e=>{if(e.target.classList.contains("x")){closeHist(+t.dataset.sid);return;}S.tab={k:"hist",sid:+t.dataset.sid};drawTabs();onTab();};
      t.oncontextmenu=e=>{e.preventDefault();menu([{label:"關閉歷史分頁",act:()=>closeHist(+t.dataset.sid)}],e.clientX,e.clientY);};});}
  const tm=$("#tabMode");tm.textContent={expanded:"▤\n展開",collapsed:"▣\n收合",stacked:"◎\n堆疊"}[m];tm.classList.toggle("on",m!=="expanded");
  const k=cur?(cur.k+":"+(cur.u||cur.sid)):"";if(k!==S.lastTabKey){S.lastTabKey=k;onTab();}}
function onTab(){const p=PAGES[S.page];if(p&&p.tab)p.tab();miniSync();}
function tabMenu(u,e){const r=(S.st.rooms||[]).find(x=>x.u===u)||{u,name:u};const pin=S.pins.includes(u);
  menu([{html:"▶&nbsp; 觀看直播",cls:"big",act:()=>{go(15,u);}},{label:pin?"📌 取消置頂":"📌 置頂（移到最左邊並固定展開）",act:()=>{S.pins=pin?S.pins.filter(x=>x!==u):[u].concat(S.pins);LS.set("pins",S.pins);drawTabs();}},{sep:1},
    {label:"編輯主播資訊",act:()=>editStreamer(u)},{label:"前往主播清單",act:()=>go(10)},{label:"切換至此直播",act:()=>{S.tab={k:"live",u};go(0);}},catSub(u)],e.clientX,e.clientY);}
function openHist(sid,name,dur,at,how){sid=+sid;S.histAt=at?{sid,at:+at,how:how||""}:null;/* V0.6.15 at = epoch of a gift: play from there +3 s */if(!S.hist.some(h=>h.sid===sid)){S.hist.push({sid,name:name||("場次 "+String(sid).padStart(5,"0")),dur:dur||""});LS.set("hist",S.hist);}S.tab={k:"hist",sid};if(![0,1,2,4,5,6].includes(S.page))go(0);else{drawTabs();onTab();}}
function closeHist(sid){S.hist=S.hist.filter(h=>h.sid!==sid);LS.set("hist",S.hist);if(S.tab&&S.tab.k==="hist"&&S.tab.sid===sid)S.tab=null;drawTabs();onTab();}
/* ---------- categories (shared by tabs, history list, streamer list) ---------- */
function catSub(u){const cats=(S.st&&S.st.cats)||[],cur=(S.st&&S.st.of||{})[u]||"";const c=cats.find(x=>x.id===cur);
  return {label:"🗂 分類"+(c?"："+c.name:""),sub:[{label:(cur?"":"✔ ")+"○ 未分類",act:()=>catAssign(u,"")}].concat(cats.map(x=>({html:`${cur===x.id?"✔ ":""}<span class="cdot" style="background:${x.color}"></span>${esc(x.name)}（📁 ${esc(x.folder)}）`,act:()=>catAssign(u,x.id)}))).concat([{sep:1},{label:"⚙ 新增／修改分類…",act:()=>go(18)}])};}
async function catAssign(u,id){const r=await fetch(B+"/api/cats/assign",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({u,id})}).then(r=>r.json()).catch(()=>({ok:false}));
  if(!r.ok){toast("✖ "+(r.message||"沒有成功"));return;}if(S.st)S.st.of=r.of;toast("✔ 分類已更新（檔案在背景搬移）");}
/* ---------- edit streamer dialog (same fields as the desktop) ---------- */
function editStreamer(u){const r=((S.st&&S.st.rooms)||[]).find(x=>x.u===u)||{u,name:u,priority:false};
  dialog("編輯主播資訊",`<div class="form"><span>主播名稱</span><input id="esN" value="${esc(r.name)}"><span>@帳號</span><input id="esU" value="@${esc(u)}"><span></span><label><input type="checkbox" id="esP"${r.priority?" checked":""}> ★ 重點（優先連線）</label></div>`,
   [["取消"],["套用",()=>{(async()=>{const j=await post("/api/pc/streamer/edit",{old:u,name:$("#esN").value,uid:$("#esU").value,priority:$("#esP").checked});if(!j.ok)dialog("套用失敗",esc(j.message||"沒有成功"));else{toast("✔ 已套用");pollState();}})();},"start"]]);}
/* ---------- page router ---------- */
const PAGES={};
function renderPage(arg){const pg=$("#page");if(S.cur&&S.cur.leave)S.cur.leave();pg.innerHTML="";const p=PAGES[S.page]||PAGES[0];S.cur=p;p.render(pg,arg);}
function boot(){applyTheme(THEME0);drawNav();
  $("#btnStart").onclick=async()=>{const j=await post("/api/pc/monitor",{on:true});if(!j.ok)toast("✖ "+(j.message||"沒有成功"));else sb("已送出：開始監控");pollState();};
  $("#btnStop").onclick=async()=>{if(!await confirmDlg("停止監控","確定要停止監控？\n\n停止後所有主播都不會再自動連線，直到你再按「開始監控」。","停止監控"))return;const j=await post("/api/pc/monitor",{on:false});if(!j.ok)toast("✖ "+(j.message||"沒有成功"));else sb("正在停止監控並保存資料…");pollState();};
  $("#netBtn").onclick=()=>go(11,"network");{const qb=$("#qBtn");if(qb)qb.onclick=()=>go(16);}$("#sysBox").onclick=()=>go(16);
  $("#tabMode").onclick=()=>{S.tabMode={expanded:"collapsed",collapsed:"stacked",stacked:"expanded"}[S.tabMode];LS.set("tabMode",S.tabMode);$("#tabs")._h="";drawTabs();};
  $("#toPhone").onclick=()=>{try{localStorage.setItem("tlm_view","phone");}catch(e){}location.href=B+"/?m=1";};
  $("#themeBtn").onclick=()=>{const m=S.mode==="dark"?"light":"dark";applyTheme(m);LS.set("theme",m);$("#tabs")._h="";drawTabs();renderPage();};
  applyZoom(LS.get("zoom",100));addEventListener("resize",()=>applyZoom(LS.get("zoom",100)));
  $("#zoomM").onclick=()=>setZoom(-10);$("#zoomP").onclick=()=>setZoom(10);
  /* V1.1.29 滾輪倍數（每個瀏覽器自己記）：×0.5～×8。有自己處理滾輪的地方（剪輯時間軸、Ctrl＋滾輪縮放、欄數選單）照舊 */
  {const WS=[0.5,0.75,1,1.5,2,2.5,3,4,5,6,8];let wm=1;try{wm=parseFloat(localStorage.getItem("tlm_pc_wheel"))||1;}catch(e){}
   const show=()=>{$("#whV").textContent="×"+wm;};const step=d=>{let i=WS.indexOf(wm);if(i<0)i=WS.findIndex(x=>x>=wm);i=Math.max(0,Math.min(WS.length-1,(i<0?2:i)+d));wm=WS[i];try{localStorage.setItem("tlm_pc_wheel",String(wm));}catch(e){}show();toast("滾輪 ×"+wm+(wm===1?"（原本的速度）":""),1500);};
   $("#whM").onclick=()=>step(-1);$("#whP").onclick=()=>step(1);show();
   const canY=(el,dy)=>{const cs=getComputedStyle(el),o=cs.overflowY;if(!(o==="auto"||o==="scroll"||(el===document.scrollingElement)))return false;if(el.scrollHeight<=el.clientHeight+1)return false;return dy>0?el.scrollTop+el.clientHeight<el.scrollHeight-1:el.scrollTop>0;};
   const canX=(el,dx)=>{const cs=getComputedStyle(el),o=cs.overflowX;if(!(o==="auto"||o==="scroll"))return false;if(el.scrollWidth<=el.clientWidth+1)return false;return dx>0?el.scrollLeft+el.clientWidth<el.scrollWidth-1:el.scrollLeft>0;};
   /* V1.1.31 絲滑：每個捲動區自己一條動畫，停著時緩進緩出，連續滾動中途換目標只緩出（不會一頓一頓）；預設開 */
   let sm=true;try{sm=localStorage.getItem("tlm_pc_wheel_smooth")!=="0";}catch(e){}
   const shS=()=>{const b=$("#whS");b.textContent=sm?"滾輪 ∿":"滾輪";b.style.opacity=sm?"1":".6";};shS();
   $("#whS").onclick=()=>{sm=!sm;try{localStorage.setItem("tlm_pc_wheel_smooth",sm?"1":"0");}catch(e){}shS();toast(sm?"滾輪絲滑：開（緩進緩出）":"滾輪絲滑：關",1500);};
   const AN=new Map(),ioq=t=>t<.5?2*t*t:1-Math.pow(-2*t+2,2)/2,oc=t=>1-Math.pow(1-t,3);
   const glide=(el,ax,d)=>{const k=ax==="y"?"scrollTop":"scrollLeft",mx=ax==="y"?el.scrollHeight-el.clientHeight:el.scrollWidth-el.clientWidth,key=el;let A=AN.get(key);const now=performance.now();
     if(A&&A.ax===ax&&now-A.t0<A.dur){A.from=el[k];A.to=Math.max(0,Math.min(mx,A.to+d));A.t0=now;A.dur=260;A.ease=oc;}
     else{A={ax,from:el[k],to:Math.max(0,Math.min(mx,el[k]+d)),t0:now,dur:340,ease:ioq,raf:0};AN.set(key,A);}
     if(!A.raf){const tick=()=>{const B=AN.get(key);if(!B){return;}const t=Math.min(1,(performance.now()-B.t0)/B.dur);el[k]=B.from+(B.to-B.from)*B.ease(t);if(t<1)B.raf=requestAnimationFrame(tick);else{B.raf=0;AN.delete(key);}};A.raf=requestAnimationFrame(tick);}};
   window.addEventListener("wheel",e=>{if((wm===1&&!sm)||e.defaultPrevented||e.ctrlKey||e.metaKey)return;const t=e.target;if(t&&t.closest&&t.closest("select,input[type=range],textarea,video,audio"))return;
     const k=e.deltaMode===1?40:e.deltaMode===2?600:1,horiz=e.shiftKey||Math.abs(e.deltaX)>Math.abs(e.deltaY);let dy=(horiz?0:e.deltaY)*k,dx=(horiz?(e.deltaX||e.deltaY):0)*k;if(!dx&&!dy)return;
     for(let el=t&&t.nodeType===1?t:t&&t.parentElement;el&&el!==document.documentElement;el=el.parentElement){if(dy?canY(el,dy):canX(el,dx)){e.preventDefault();if(sm)glide(el,dy?"y":"x",(dy||dx)*wm);else if(dy)el.scrollTop+=dy*wm;else el.scrollLeft+=dx*wm;return;}}},{passive:false});
   ["pointerdown","keydown"].forEach(ev=>window.addEventListener(ev,()=>{AN.forEach(A=>{if(A.raf)cancelAnimationFrame(A.raf);});AN.clear();},{passive:true}));}
  try{localStorage.setItem("tlm_view","pc");}catch(e){}
  pollState();renderPage();}
function setZoom(d){const z=Math.max(60,Math.min(150,LS.get("zoom",100)+d));LS.set("zoom",z);applyZoom(z);}
/* V0.6.50 介面大小：整個畫面永遠填滿視窗（以前縮小時下面整塊變黑），上方分頁、左邊側欄、下方狀態列只縮一半（不會小到沒質感） */
function applyZoom(z){const f=Math.max(.6,Math.min(1.5,(+z||100)/100)),app=$("#app");S.zf=f;document.body.style.zoom=f;$("#zoomV").textContent=Math.round(f*100)+"%";
  const t=Math.sqrt(1/f);for(const id of ["tabsRow","side","statusBar"]){const e=document.getElementById(id);if(e)e.style.zoom=f===1?"":t;}
  document.documentElement.style.setProperty("--zf",f);
  if(!app)return;app.style.setProperty("--sidew",(f===1?210:210*t)+"px");app.style.width=(innerWidth/f)+"px";app.style.height=(innerHeight/f)+"px";app.style.gridTemplateRows=(innerHeight/f)+"px";
  requestAnimationFrame(()=>{const r=app.getBoundingClientRect();if(r.height>0&&Math.abs(r.height-innerHeight)>2){const k=innerHeight/r.height,h=parseFloat(app.style.height)*k,w=parseFloat(app.style.width)*(innerWidth/Math.max(1,r.width));
    app.style.height=h+"px";app.style.gridTemplateRows=h+"px";app.style.width=w+"px";}
    try{const P=PAGES[S.page];if(P&&P.fitCards)P.fitCards();if(P&&P.chart)P.chart();}catch(e){}});}
/* TK_V0.9.47 網頁版右上角：下載資料夾有新的更新包（跟 VS 一樣每 15 秒看一次） */
function pcUpdFab(){const chk=async()=>{if(document.hidden)return;let d=null;try{d=await api("/api/update/dl");}catch(e){}const f=d&&d.found;let b=document.getElementById("updFab");
    let skip="";try{skip=localStorage.getItem("tlm_updfab_skip")||"";}catch(e){}
    if(!f||skip===f.name+"|"+f.mtime){if(b)b.remove();return;}
    if(!b){b=document.createElement("div");b.id="updFab";b.style.cssText="position:fixed;top:44px;right:12px;z-index:9700;display:flex;gap:4px";document.body.appendChild(b);}
    b.innerHTML=`<button type="button" class="start" style="display:flex;flex-direction:column;align-items:flex-start;padding:6px 14px;border-radius:12px;box-shadow:0 6px 20px rgba(0,0,0,.45)">⬆ 有新版 V${esc(f.ver)}<small style="font-weight:600;opacity:.9">下載資料夾 · 按一下更新</small></button><button type="button" title="這個先不要提醒" style="border-radius:12px">✕</button>`;
    const [go_,x_]=b.querySelectorAll("button");x_.onclick=()=>{try{localStorage.setItem("tlm_updfab_skip",f.name+"|"+f.mtime);}catch(e){}b.remove();};
    go_.onclick=()=>{b.remove();S.updDlGo=1;go(14);};};
  chk();setInterval(chk,15000);}
setTimeout(()=>{try{pcUpdFab();}catch(e){}},2000);


@@SH30@@

@@SH31@@

/* V0.6.17 歷史紀錄右上角：24/7 電腦的即時數值，V0.6.20 精簡成三列、只顯示 %（手機版與電腦網頁版共用） */
(function(){if(document.getElementById("minicss"))return;const st=document.createElement("style");st.id="minicss";
st.textContent=".pcst{display:grid;grid-auto-flow:column;grid-auto-columns:max-content;justify-content:end;gap:0 10px;font-size:11px;line-height:1.45;font-variant-numeric:tabular-nums;white-space:nowrap;color:var(--sub,var(--subtext,#8b98a8));flex:none}.pcst>span{display:flex;align-items:baseline;gap:3px}.pcst i{font-style:normal;font-size:10px;letter-spacing:.3px;opacity:.85}.pcst b{display:inline;font-size:11.5px;font-weight:800;color:var(--strong,var(--text,#e8eef5));overflow:visible}.pcst small{font-size:9.5px;color:var(--sub,var(--subtext,#8b98a8));opacity:.8;margin-left:1px}.pcst .w{color:#f0ad4e}.pcst .x{color:#ff5c5c}.pcst .pg1{color:#45d483}#miniS:empty{display:none}.pcst.one{grid-template-columns:none;grid-auto-flow:column;grid-auto-columns:max-content;gap:0 9px}.pcst.one>span{min-width:0;gap:3px}.pcst.one>span:empty{display:none}.rpdel{flex:none;width:34px;height:34px;border-radius:10px;border:1px solid #c62845;background:transparent;color:#ff6577;font-size:16px;margin-left:6px}.rph .pcst{margin-left:auto;padding-left:8px;border-left:1px solid var(--line,#2a3340)}";
document.head.appendChild(st);})();
const MINI={t:null,busy:false,h:""};
function miniHtml(m){const c=(p,w,x)=>p==null?"":p>=x?"x":p>=w?"w":"",cell=(k,v,cls)=>`<span><i>${k}</i><b class="${cls||""}">${v}</b></span>`,T=[];   // V0.6.21 只留 5 項、一列
  for(const r of m.rows||[]){if(/^(CPU|RAM|GPU)$/.test(r.k))T.push(cell(r.k,r.p!=null?r.p+"%":"—",c(r.p,70,90)));
    else T.push(cell(String(r.k).replace(":","")+"忙",r.busy!=null?r.busy+"%":"—",c(r.busy,60,90)));}
  return T.join("");}
function miniTick(){clearTimeout(MINI.t);MINI.t=null;const el=document.getElementById("miniS");if(!el)return;
  if(MINI.h&&!el.innerHTML)el.innerHTML=MINI.h;
  if(!document.hidden&&!MINI.busy){MINI.busy=true;(typeof api==="function"?api:J)("/api/pc/mini").then(m=>{if(m&&m.rows){MINI.h=miniHtml(m);const e=document.getElementById("miniS");if(e)e.innerHTML=MINI.h;}}).catch(()=>{}).finally(()=>{MINI.busy=false;});}
  MINI.t=setTimeout(miniTick,3000);}
function miniStart(){if(!MINI.t)miniTick();else{const el=document.getElementById("miniS");if(el&&!el.innerHTML&&MINI.h)el.innerHTML=MINI.h;}}
function miniSync(){const w=document.getElementById("miniW");if(!w)return;const on=S.page===7||!!(S.tab&&S.tab.k==="hist");
  if(on&&!document.getElementById("miniS")){w.innerHTML='<div id="miniS" class="pcst"></div>';miniStart();}else if(!on&&w.innerHTML)w.innerHTML="";}

/* V0.6.27 自我檢查狀態＋重新啟動主程式（手機與電腦網頁版共用） */
function healthHtml(H){if(!H||!H.t)return '<div style="opacity:.7;margin-bottom:6px">🩺 自我檢查：第一次檢查中…</div>';
  const db=H.ok?`<b style="color:#45d483">資料庫寫入正常</b>（${H.ms} ms）`:`<b style="color:#ff4d6d">資料庫寫不進去 ${H.blocked_min} 分鐘</b>（${esc(H.err||"")}）`;
  const cn=H.conn==="bad"?`<b style="color:#f0ad4e">連線一直失敗</b>：${esc(H.conn_msg||"")}`:`<b style="color:#45d483">連線正常</b>`;
  const t=new Date(H.t*1000),hm=String(t.getHours()).padStart(2,"0")+":"+String(t.getMinutes()).padStart(2,"0");
  return `<div style="margin-bottom:8px;line-height:1.6">🩺 自我檢查（每分鐘，${hm}）：${db} · ${cn}${H.cg?`<div>${cgLine(H.cg)}</div>`:""}${(H.actions||[]).length?`<div style="font-size:.88em;opacity:.8">`+H.actions.slice(-3).map(a=>{const d=new Date(a.t*1000);return `${String(d.getHours()).padStart(2,"0")}:${String(d.getMinutes()).padStart(2,"0")} ${esc(a.msg)}`;}).join("<br>")+`</div>`:""}
<div style="margin-top:6px"><button class="pill" data-restart="1" style="border-color:#c62845;color:#ff6577">🔄 重新啟動主程式</button> <span style="font-size:.85em;opacity:.7">卡住時用，效果跟重開機一樣；大約 20 秒後自動開回來${H.restart_min>0?`（資料庫寫不進去 ${H.restart_min} 分鐘會自動做）`:""}</span></div></div>`;}
document.addEventListener("click",async e=>{const b=e.target.closest("[data-restart]");if(!b)return;
  if(!confirm("確定要重新啟動主程式嗎？\n\n監控和錄影會中斷約 20～30 秒，之後自動開回來並繼續監控。"))return;
  const pf=typeof post==="function"?(u,d)=>post(u,d):(u,d)=>deepPost(u,d);let j=await pf("/api/pc/app/restart",{});
  if(j&&j.guard){if(!confirm(j.message))return;j=await pf("/api/pc/app/restart",{force:1});}   // V0.6.47 重開沒有幫助時先提醒
  (typeof toast==="function"?toast:alert)(j&&j.ok?"🔄 "+(j.message||"重新啟動中"):"✖ "+((j&&j.message)||"沒有成功"));});

/* V0.6.47 連線管控一行摘要（自我檢查、側欄共用） */
function cgLine(I){if(!I)return "";const col=["#45d483","#f0ad4e","#ff6577"][I.level]||"#45d483",S=I.sign||{};
  return `🚦 連線管控：<b style="color:${col}">${I.on?esc(I.level_name):"關閉"}</b> · 每分鐘 ${I.att_min}/${I.rate_now} 次檢查 · TikTok 拒絕 ${I.block_pct}% · 排隊 ${(I.q||[]).reduce((a,b)=>a+b,0)}`+
    (S.limited?` · <b style="color:#ff6577">簽章額度用完</b>`:` · 今天簽章 ${S.n||0} 次`)+` <a href="javascript:void(0)" onclick="cgOpen()" style="color:var(--vline,#4dc9ff)">詳細 →</a>`;}

@@SH32@@

@@SH33@@

@@SH34@@

@@SH35@@

@@SH36@@

@@SH37@@

@@SH38@@

@@SH39@@

/* KIT-BEGIN */
/* ================= V0.6.76 共用小工具（手機／網頁版）：禮物官方中文名稱、禮物圖示、長按／右鍵的場次選單 ================= */
const KIT={gm:null,gmT:0,lp:null,swallow:false,swT:0};
const kB=()=>(typeof B==="string"?B:"");
const kE=s=>String(s==null?"":s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const kToast=m=>(typeof toast==="function"?toast(m):alert(m));
async function kGet(p){const r=await fetch(kB()+p,{cache:"no-store"});return r.json();}
async function kPost(p,d){if(typeof post==="function")return await post(p,d);if(typeof deepPost==="function")return await deepPost(p,d);return {};}
async function kGiftMeta(force){if(!force&&KIT.gm&&Date.now()-KIT.gmT<300e3)return KIT.gm;try{KIT.gm=await kGet("/api/pc/gift/meta");KIT.gmT=Date.now();}catch(e){KIT.gm=KIT.gm||{zh:{},ia:[]};}return KIT.gm;}
function kGN(n){const z=KIT.gm&&KIT.gm.zh;const k=String(n||"").trim().toLowerCase();return (z&&z[k])||String(n||"");}
function kIA(n){const a=KIT.gm&&KIT.gm.ia;return !!(a&&a.indexOf(String(n||"").trim().toLowerCase().replace(/\s+/g," "))>=0);}
function kGIcon(n,cls){return `<span class="${cls||"tkGi"}"><img src="${kB()}/api/pc/gfx/icon?k=${encodeURIComponent(n)}" alt="" loading="lazy" onerror="this.parentNode.textContent='🎁'"></span>`;}
kGiftMeta();
/* 長按（手機）或右鍵（電腦）任何認得出場次的格子 → 選單：✂ 剪輯這一場 */
function kSidOf(t){if(!t||!t.closest)return 0;if(t.closest("#edOv,.tkMenu,input,textarea,select,video,.lvsT,#lvsOpt"))return 0;   /* TK_V1.0.71 檔案總管的縮圖：按住是圈選／預覽，不要跳「剪輯這一場」選單 */
  const a=t.closest("[data-sid]");if(a&&+a.dataset.sid>0)return +a.dataset.sid;const h=t.closest(".hr[data-id]");if(h&&+h.dataset.id>0)return +h.dataset.id;return 0;}
function kMenu(items,x,y){document.querySelectorAll(".tkMenu").forEach(m=>m.remove());const m=document.createElement("div");m.className="tkMenu tk";
  m.innerHTML=items.map((it,i)=>it.hd?`<div class="hd">${kE(it.hd)}</div>`:`<button data-i="${i}">${kE(it.label)}</button>`).join("");document.body.appendChild(m);
  const W=window.innerWidth,H=window.innerHeight,r=m.getBoundingClientRect();m.style.left=Math.max(8,Math.min(x,W-r.width-8))+"px";m.style.top=Math.max(8,Math.min(y,H-r.height-8))+"px";
  const close=()=>{m.remove();document.removeEventListener("pointerdown",out,true);};const out=e=>{if(!m.contains(e.target))close();};
  setTimeout(()=>document.addEventListener("pointerdown",out,true),0);
  m.onclick=e=>{const b=e.target.closest("button[data-i]");if(!b)return;close();const it=items[+b.dataset.i];if(it&&it.act)it.act();};}
function kSidMenu(sid,x,y){kMenu([{hd:`場次 #${String(sid).padStart(5,"0")}`},{label:"✂ 剪輯這一場",act:()=>{if(typeof edOpen==="function")edOpen(sid);}}],x,y);}
document.addEventListener("contextmenu",e=>{if(e.defaultPrevented)return;const sid=kSidOf(e.target);if(!sid)return;e.preventDefault();clearTimeout(KIT.lp);KIT.lp=null;if(KIT.swT&&Date.now()-KIT.swT<1500&&document.querySelector(".tkMenu"))return;if(e.pointerType==="touch"){KIT.swallow=true;KIT.swT=Date.now();}kSidMenu(sid,e.clientX,e.clientY);});
document.addEventListener("pointerdown",e=>{if(KIT.swallow&&Date.now()-KIT.swT>400)KIT.swallow=false;if(e.pointerType==="mouse")return;const sid=kSidOf(e.target);if(!sid)return;const x=e.clientX,y=e.clientY;clearTimeout(KIT.lp);
  KIT.lp=setTimeout(()=>{KIT.lp=null;KIT.swallow=true;KIT.swT=Date.now();if(navigator.vibrate)navigator.vibrate(15);kSidMenu(sid,x,y);},600);
  const mv=ev=>{if(Math.abs(ev.clientX-x)>10||Math.abs(ev.clientY-y)>10)stop();};const stop=()=>{clearTimeout(KIT.lp);document.removeEventListener("pointermove",mv,true);};
  document.addEventListener("pointermove",mv,true);document.addEventListener("pointerup",stop,{once:true,capture:true});document.addEventListener("pointercancel",stop,{once:true,capture:true});},true);
document.addEventListener("click",e=>{if(KIT.swallow){KIT.swallow=false;if(Date.now()-KIT.swT<1500){e.preventDefault();e.stopPropagation();}}},true);   /* 長按後放開的那一下不要當成點擊（Android 不會送，下一次按下就清掉） */
/* KIT-END */

@@SH40@@

@@SH41@@

@@SH42@@

@@SH43@@

@@SH44@@

@@SH45@@

@@SH46@@

@@SH47@@

@@SH48@@

@@SH49@@

@@SH50@@
<div class="ytRow"><button class="pill ytDel" data-yt="hpurge">🗑 刪除暫放資料夾（${ytGB(H.bytes)}）</button><button class="pill" data-yt="hrestore">↩ 全部放回原位</button><button class="pill" onclick="go(56)">🔍 逐項抽查</button></div></div>`;}
@@SH51@@

@@SH52@@

@@SH53@@

/* SMT-BEGIN */
/* V0.7.42.026 智慧功能狀態卡：智慧排程、錄製檢討、今天漏開頭、精選、每日精選影片、YouTube、硬碟，一行一項；點一行跳到那一頁（各介面自己定義 smtGo）. 只讀，1 分鐘更新 */
const smtE=s=>String(s==null?"":s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
async function smtLoad(el){if(!el)return;if(!el._smt){el._smt=1;el.addEventListener("click",e=>{const r=e.target.closest("[data-smt]");if(!r)return;if(typeof tapGuard==="function"&&tapGuard())return;if(typeof smtGo==="function")smtGo(r.dataset.smt);});}
  if(!el.innerHTML)el.innerHTML='<div class="smtC"><b>🤖 智慧功能狀態</b> <small>讀取中…</small></div>';let d=null;
  try{const r=await fetch((typeof B==="string"?B:"")+"/api/pc/smart/sum",{cache:"no-store"});d=await r.json();}catch(e){}
  if(!el.isConnected)return;clearTimeout(el._tm);el._tm=setTimeout(()=>{if(el.isConnected)smtLoad(el);},60000);   /* V0.7.42.030 失敗也 1 分鐘後再試 */
  if(!d||!Array.isArray(d.items)){if(!el._ok)el.innerHTML="";return;}el._ok=1;
  el.innerHTML=`<div class="smtC"><div class="smtH"><b>🤖 智慧功能狀態</b><small>點一行看詳細</small></div>${d.items.map(x=>`<button type="button" class="smtR smt-${smtE(x.lv||"n")}" data-smt="${smtE(x.k)}"><i>${smtE(x.ic)}</i><b>${smtE(x.t)}</b><span>${smtE(x.v)}</span><s>›</s></button>`).join("")}</div>`;}
/* SMT-END */

@@SH54@@

@@SH55@@

@@SH56@@

@@SH57@@

@@SH58@@
<label class="rvOpt">每格<select data-rs="step">${[[120,"2 分"],[60,"1 分"],[30,"30 秒"]].map(([v,t])=>`<option value="${v}"${RV.step===v?" selected":""}>${t}</option>`).join("")}</select></label><label class="rvOpt">一列<select data-rs="cols">${[0,2,3,4,5,6,8,10,12,15].map(n=>`<option value="${n}"${RV.cols===n?" selected":""}>${n?n+" 張":"自動"}</option>`).join("")}</select></label><label class="rvOpt"><input type="checkbox" data-rs="auto"${RV.auto?" checked":""}>選完跳下一位</label></div>`;}
@@SH59@@
async function rvClick(e){const t=e.target;if(t.closest("[data-gset]")){rvGset();return;}
@@SH60@@

@@SH61@@

@@SH62@@

@@SH63@@

@@SH64@@

@@SH65@@
function lvsFSet(f){try{localStorage.setItem("lvs_f",JSON.stringify(f));}catch(e){}}
async function lvsMount(root,opt){if(opt&&opt.pc&&typeof lvpMount==="function")return lvpMount(root);   /* TK_V0.8.97 網頁版：照 VideoSift 檔案總管的版面 */
  LVS.pc=false;LVS.root=root;LVS.auto=0;LVS.autoL=[];LVS.cur=-1;root.classList.add("lvsPage");const F=lvsF();LVS.F=F;
  root.innerHTML=`<div class="lvsTop lvsTopM"><button class="lvsNav" data-a="prev" title="上一場">◀</button><button class="lvsCurN" id="lvsCurN" title="點開看全部場次"><b>讀取中…</b><small></small></button><button class="lvsNav orpB" data-orph="1" title="只看放超過 14 天、沒有場次資料的純 MP4（冗餘檔）">冗餘</button><button class="lvsNav" data-a="next" title="下一場">▶</button><span class="lvsAuto" id="lvsAuto"></span></div>
<div class="lvsTool lvsToolM"><input id="lvsQ" class="lvsQ" placeholder="🔍 直播間名稱" value="${lvsE(F.q)}"><select id="lvsO">${LVS_ORD.map(([v,t])=>`<option value="${v}"${(LVS.kind==="nv"&&(F.o==="new"||!F.o)?"exp":F.o)===v?" selected":""}>${t}</option>`).join("")}</select><select id="lvsCat"><option value="*">📁 全部資料夾</option></select></div>
<div class="lvsTool lvsToolM"><span class="lvsGr" id="lvsGr">${LVS_GR.map(([v,t])=>`<button data-g="${v}" class="${F.g.includes(v)?"on":""}">${t}</button>`).join("")}</span><button class="lvsPv${F.pv?" on":""}" id="lvsPv" title="還沒做好預覽圖的場次先不列（背景照樣在做，做好就會出現）">✔ 跳過沒好的</button><select id="lvsStep" title="間隔">${LVS_STEPS.map(([v,t])=>`<option value="${v}"${+lvsPref("step",0)===v?" selected":""}>⏱ ${t}</option>`).join("")}</select><select id="lvsCols" title="一列幾張">${[3,4,5,6,7,8,10,12,14,16,18,20,24,30,36].map(n=>`<option value="${n}"${lvsColsN()===n?" selected":""}>▦ ${n}</option>`).join("")}</select><small id="lvsCnt" class="lvsCntM">讀取中…</small></div>
<div class="lvsStrip" id="lvsStrip"></div><div class="lvsCurB" id="lvsCurB">${["-2","0","1","2"].map(k=>`<button data-v="${k}" style="--c:${LVSC[k][2]}"><span><b>${LVSC[k][0]}</b> ${LVSC[k][1]}</span><small data-gb="${k}">…</small></button>`).join("")}<button data-clip="1" class="clipB" style="--c:#9aa3b2"><span>✂ 初剪</span><small id="lvsClipGB">…</small></button></div><div class="lvsBox" id="lvsBox"></div><div class="lvsSel" id="lvsSel" hidden></div>`;   /* TK_V0.9.15 手機版：名字放最上面、等級一排放在場次小圖下面，上面盡量壓扁 */
  root.querySelector("[data-a=prev]").onclick=()=>lvsGoTo(LVS.cur-1);root.querySelector("[data-a=next]").onclick=()=>lvsGoTo(LVS.cur+1);root.querySelector("#lvsCurN").onclick=lvsList;   /* TK_V0.9.17 名字＝下拉選場次；◀ ▶＝上一場／下一場 */
  root.querySelector("#lvsCurB").onclick=e=>{if(e.target.closest("[data-clip]")){location.hash="clips";return;}const b=e.target.closest("[data-v]");if(!b)return;const s=LVS.box&&LVS.box.querySelector(`.lvsS[data-i="${LVS.cur}"]`);if(s)lvsSet(s,+b.dataset.v,false);};
  if(root.querySelector("#lvsSum"))root.querySelector("#lvsSum").onclick=e=>{const b=e.target.closest("[data-k]");if(!b)return;F.lvf=F.lvf===b.dataset.k?"":b.dataset.k;lvsFSet(F);lvsApply(0);};   /* TK_V0.9.14 點等級＝只看那一種，再點一次取消 */
  await lvsWire(root,F);}
/* 兩種版面共用：篩選、捲動、選取、背景補圖 */
async function lvsWire(root,F){const $r=s=>root.querySelector(s);
  LVS.box=root.querySelector("#lvsBox");LVS.strip=root.querySelector("#lvsStrip");
  if($r("[data-a=back]"))root.querySelector("[data-a=back]").onclick=()=>{window.lvsList=true;if(typeof PAGES==="undefined")location.hash="fx";else if(typeof go==="function")go(31);};   /* 回一般檔案總管（這次開著就不再自動跳回來） */
  root.querySelector("#lvsStep").onchange=e=>{lvsPrefSet("step",e.target.value);lvsRebuild();};lvsColWire(root);
@@SH66@@
  const L=(LVS.all||[]).filter(r=>qs?String(r.sid)===qs:(!sk||!lvsGd(r))&&(!q||String(r.name||"").toLowerCase().includes(q)||String(r.u||"").toLowerCase().includes(q)||String(r.sid)===q.replace(/^#0*/,""))
@@SH67@@
@@SH68@@
  g.innerHTML=H.join("");lvsSheets(g);if(LVS.box){const c_=lvsColsN();LVS.box.classList.toggle("lvsDense",c_>24);LVS.box.classList.toggle("lvsDense2",c_>40);}}
@@SH69@@
/* V1.1.37 一列 4～64 張：拉桿／－＋／打數字／方向鍵；邊拉邊看（等手停 0.25 秒才重排，不卡） */
function lvsColWire(root){const R=root.querySelector("#lvsColR"),N=root.querySelector("#lvsCols");if(!N)return;
  if(!R){N.onchange=e=>{lvsPrefSet("cols",e.target.value);lvsColApply();};return;}   /* 窄版工具列（下拉選單） */
  let tm=0;
  const set=(v,now)=>{v=Math.max(4,Math.min(64,Math.round(+v||lvsColsN())));R.value=v;N.value=v;lvsPrefSet("cols",v);clearTimeout(tm);tm=setTimeout(()=>{lvsColApply();},now?0:250);};
  R.oninput=()=>set(R.value);N.onchange=()=>set(N.value,1);N.onkeydown=e=>{if(e.key==="Enter")set(N.value,1);};
  [R,N].forEach(el=>el.addEventListener("keydown",e=>{if(e.key==="ArrowUp"||e.key==="ArrowRight"||e.key==="ArrowDown"||e.key==="ArrowLeft"){e.preventDefault();e.stopPropagation();const d=(e.key==="ArrowUp"||e.key==="ArrowRight"?1:-1)*(e.shiftKey?4:1);set(lvsColsN()+d);}}));
  root.querySelectorAll(".lvsColB").forEach(b=>b.onclick=e=>{set(lvsColsN()+(+b.dataset.cd)*(e.shiftKey?4:1));});}
function lvsColApply(){const c=lvsColsN();if(!LVS.box)return;LVS.box.classList.toggle("lvsDense",c>24);LVS.box.classList.toggle("lvsDense2",c>40);
  LVS.box.querySelectorAll(".lvsG").forEach(g=>{g.style.gridTemplateColumns=`repeat(${c},1fr)`;});}
function lvsColsN(){const v=Math.min(64,+lvsPref("cols",0));return v>0?v:((typeof VG!=="undefined"&&VG.cols)||((window.innerWidth<700)?4:8));}
@@SH70@@

/* LVP-BEGIN */
/* TK_V0.8.97 網頁版連續分級：照 VideoSift 檔案總管的版面——左邊資料夾樹＋等級格子（場數、GB）＋場次卡片；右邊現在這場的工具列＋一場接一場往下滑。
   等級是 −2 −1 0 +1（待剪輯）+2；滑過去沒標＝自動 −2，那一場有選的片段就合併輸出成 1 部；卡片上顯示剪好幾部（✔／−）。 */
const LVP_LV=[["-2","−2 可丟","#ff4d6d"],["0","0 未分類","#f0c419"],["1","+1 待剪輯","#9ad94a"],["2","+2 保存","#2ecc71"]];
/* TK_V0.9.43 左右中間那條可以拖：調整左邊清單和右邊大圖的寬度（記住） */
function lvpSplitInit(root){const sp=root.querySelector("#lvpSplit"),G=root.querySelector(".lvp");if(!sp||!G)return;
  const set=w=>{if(w)G.style.gridTemplateColumns=`${w}px 8px 1fr`;else G.style.gridTemplateColumns="";};let w0=0;try{w0=+localStorage.getItem("tlm_lvpw")||0;}catch(e){}
  if(w0)set(Math.max(240,Math.min(w0,window.innerWidth-420)));let d=null;
  sp.onpointerdown=e=>{d={x:e.clientX,w:root.querySelector(".lvpL").getBoundingClientRect().width};sp.setPointerCapture(e.pointerId);sp.classList.add("on");e.preventDefault();};
  sp.onpointermove=e=>{if(!d)return;const W=G.getBoundingClientRect().width;const w=Math.round(Math.max(240,Math.min(W-420,d.w+e.clientX-d.x)));d.cur=w;set(w);};
  sp.onpointerup=sp.onpointercancel=()=>{if(!d)return;sp.classList.remove("on");if(d.cur)try{localStorage.setItem("tlm_lvpw",String(d.cur));}catch(e){}d=null;try{window.dispatchEvent(new Event("resize"));}catch(e){}};
  sp.ondblclick=()=>{try{localStorage.removeItem("tlm_lvpw");}catch(e){}set(0);try{window.dispatchEvent(new Event("resize"));}catch(e){}};}
function lvpCc(){const v=+lvsPref("ccols",4);return v>=2&&v<=8?v:4;}
function lvpCcApply(){const c=LVS.root&&LVS.root.querySelector("#lvsStrip");if(c)c.style.gridTemplateColumns=`repeat(${lvpCc()},minmax(0,1fr))`;}   /* TK_V0.8.98 左邊卡片一列幾部 */
const lvpGB=mb=>(mb/1000).toFixed(1)+"GB";   /* TK_V0.9.03 一律小數第一位 */
async function lvpMount(root){LVS.pc=true;LVS.root=root;LVS.auto=0;LVS.autoL=[];LVS.cur=-1;root.classList.add("lvsPage","lvpPage");const F=lvsF();LVS.F=F;
  root.innerHTML=`<div class="lvp"><aside class="lvpL">
<div class="lvpTop"><button class="lvsBk" data-a="back" title="回一般檔案總管">‹</button><b>▦ 檔案總管</b><small id="lvsCnt">讀取中…</small><button class="lvsBk orpB" data-orph="1" title="只看放超過 14 天、沒有場次資料的純 MP4（冗餘檔）">冗餘檔</button></div>
<div class="lvpTree" id="lvpTree"></div>
<div class="lvpChips" id="lvpChips"></div>
<div class="lvpProg"><i id="lvpProgI"></i><span id="lvpProgT"></span></div>
<div class="lvpRow"><select id="lvsO">${LVS_ORD.map(([v,t])=>`<option value="${v}"${(LVS.kind==="nv"&&(F.o==="new"||!F.o)?"exp":F.o)===v?" selected":""}>${t}</option>`).join("")}</select><select id="lvpCc" title="左邊卡片一列幾部">${[2,3,4,5,6,7,8].map(n=>`<option value="${n}"${lvpCc()===n?" selected":""}>一列 ${n} 部</option>`).join("")}</select><span class="lvsGr" id="lvsGr">${LVS_GR.map(([v,t])=>`<button data-g="${v}" class="${F.g.includes(v)?"on":""}" title="審核等級">${t}</button>`).join("")}</span></div>
<input id="lvsQ" class="lvsQ lvpQ" placeholder="🔍 搜尋直播間名稱／#序號" value="${lvsE(F.q)}">
<div class="lvpCards" id="lvsStrip"></div>
<div class="lvpFoot" id="lvpFoot"></div></aside><div class="lvpSplit" id="lvpSplit" title="左右拖：調整左右寬度（點兩下恢復）"><i></i></div>
<main class="lvpR"><div class="lvpHd" id="lvpHd"></div>
<div class="lvpTb" id="lvpTb"><button data-t="prev">◀ 上一則</button>${["-2","0","1","2"].map(k=>`<button class="lvpLv" data-t="lv" data-v="${k}" style="--c:${LVSC[k][2]}">${LVSC[k][0]} ${LVSC[k][1]}</button>`).join("")}<button class="lvpLv" data-t="lv" data-v="" style="--c:#8a93a3" title="清除保存等級">—</button><button data-t="next">下一則 ▶</button>
<span class="lvpSp"></span><button data-t="cut" class="pri" id="lvpCut">✂ 輸出初剪（0 段）</button><button data-t="pv">▶ 預覽選的片段</button><button data-t="clr">清除選取</button><button data-t="rp">▶ 播放</button><button data-t="clips" title="所有剪好的片段">✂ 初剪片段</button>
<label>間隔 <select id="lvsStep">${LVS_STEPS.map(([v,t])=>`<option value="${v}"${+lvsPref("step",0)===v?" selected":""}>${t}</option>`).join("")}</select></label><span class="lvsColW" title="一列幾張（4～64）：拉桿、－／＋、直接打數字，或點拉桿後用方向鍵；Shift＋方向鍵一次 4">一列 <button class="pill lvsColB" data-cd="-1">－</button><input type="range" id="lvsColR" min="4" max="64" step="1" value="${lvsColsN()}"><input type="number" id="lvsCols" min="4" max="64" step="1" value="${lvsColsN()}"><button class="pill lvsColB" data-cd="1">＋</button> 張</span>
<button data-t="undo" id="lvpUndo" hidden>↩ 復原自動 −2（0）</button><label class="lvsDef" title="往下滑的時候，已經標過 −2／−1／+1／+2 的場次直接跳過（0 不算標過）"><input type="checkbox" id="lvpSkipG"${lvsSkipG()?" checked":""}> 滑動跳過已標記</label><label class="lvsDef"><input type="checkbox" id="lvsDef"${lvsDefOn()?" checked":""}> 預設開這頁</label><span class="lvsAuto" id="lvsAuto"></span></div>
<div class="lvpHint">點一格＝選；再點＝取消；按住拖曳＝圈一段；Shift＋點＝連選；長按 1.5 秒＝播放。滑到下一部＝上一部沒標的自動 −2（有選的片段會合併輸出成 1 部）</div>
<div class="lvsBox lvpBox" id="lvsBox"></div></main></div>`;
  lvpSplitInit(root);root.querySelector("#lvpTb").onclick=lvpTbClick;root.querySelector("#lvpSkipG").onchange=e=>{lvsPrefSet("skipg",e.target.checked?"1":"0");lvsToast(e.target.checked?"✔ 往下滑會跳過已標記的場次":"往下滑每一場都會出現");lvsJump(Math.max(0,LVS.cur));};lvpCcApply();root.querySelector("#lvpCc").onchange=e=>{lvsPrefSet("ccols",e.target.value);lvpCcApply();};
  root.querySelector("#lvpTree").onclick=e=>{const x=e.target.closest("[data-cat]");if(!x)return;F.cat=x.dataset.cat;lvsFSet(F);lvsApply(0);};
  root.querySelector("#lvpChips").onclick=e=>{const x=e.target.closest("[data-k]");if(!x)return;const k=x.dataset.k;
    if(k==="ready"){F.pv=!F.pv;lvsFSet(F);if(F.pv&&!(LVS.all||[]).some(r=>r.pr!=null)){lvsToast("檢查每場的預覽圖…");lvsLoad(0);}else lvsApply(0);return;}
    F.lvf=k==="all"?"":(F.lvf===k?"":k);lvsFSet(F);lvsApply(0);};
  addEventListener("keydown",lvpKey);
  await lvsWire(root,F);}
function lvpKey(e){if(!LVS.pc||!LVS.root||!LVS.root.isConnected){removeEventListener("keydown",lvpKey);return;}if(/INPUT|SELECT|TEXTAREA/.test((e.target&&e.target.tagName)||""))return;
  const s=lvpCurS();const m={"1":-2,"2":-1,"3":0,"4":1,"5":2};if(m[e.key]!=null&&s){e.preventDefault();lvsSet(s,m[e.key],false);return;}
  if(e.key==="ArrowRight"||e.key==="PageDown"){e.preventDefault();lvpGo(LVS.cur+1);}else if(e.key==="ArrowLeft"||e.key==="PageUp"){e.preventDefault();lvpGo(LVS.cur-1);}else if(e.key==="Escape")lvsSelClear();}
function lvpCurS(){return LVS.box&&LVS.box.querySelector(`.lvsS[data-i="${LVS.cur}"]`);}
function lvpGo(i){if(i<0||i>=LVS.L.length)return;const s=LVS.box.querySelector(`.lvsS[data-i="${i}"]`);if(s){LVS.quiet=true;LVS.box.scrollTo({top:s.offsetTop,behavior:"smooth"});setTimeout(()=>{LVS.quiet=false;lvsCurCheck();},600);}else lvsJump(i);}
async function lvpTbClick(e){const b=e.target.closest("[data-t]");if(!b)return;const t=b.dataset.t,s=lvpCurS();
  if(t==="prev")lvpGo(LVS.cur-1);else if(t==="next")lvpGo(LVS.cur+1);
  else if(t==="lv"){if(s)lvsSet(s,b.dataset.v===""?null:+b.dataset.v,false);}
  else if(t==="cut")lvsCut();else if(t==="clr")lvsSelClear();
  else if(t==="pv"){const S=LVS.sel,G=lvsSegs();if(!S||!G.length){lvsToast("先點圖片選取片段");return;}lvsPlayAt(S.sid,S.info,G[0].ri,G[0].s,null);}
  else if(t==="rp"){const r=LVS.L[LVS.cur];if(r)window.open(`${lvsB()}/#rp/${r.sid}/0`,"_blank");}
  else if(t==="undo")lvpUndo();else if(t==="clips"&&typeof go==="function")go(44);}
/* 復原這次自動標的 −2（改回原本的等級） */
async function lvpUndo(){const A=(LVS.autoL||[]).slice();if(!A.length)return;if(!confirm(`把這次自動標成 −2 的 ${A.length} 場改回原本的等級？`))return;let n=0;
  for(const a of A){const j=await lvsPost("/api/pc/vb/note",{sid:a.sid,level:a.prev});if(j&&j.ok!==false){n++;const r=(LVS.all||[]).find(x=>x.sid===a.sid);if(r)r.lv=a.prev;
    const s=LVS.box.querySelector(`.lvsS[data-sid="${a.sid}"]`);if(s){s._lv=false;s.classList.remove("done");s.querySelectorAll("[data-lv]").forEach(x=>x.classList.toggle("on",a.prev!=null&&+x.dataset.lv===a.prev));}const i=LVS.L.findIndex(x=>x.sid===a.sid);if(i>=0)lvsStripPaint(i);}}
  LVS.autoL=[];LVS.auto=0;const au=document.getElementById("lvsAuto");if(au)au.textContent="";lvpSum();lvpCur(LVS.cur);lvsToast(`↩ 改回 ${n} 場`);}
/* 左邊卡片 */
function lvpCard(r,i){return `<div class="lvsSI lvpC" data-i="${i}"><div class="lvpIm"><img loading="lazy" alt="" src="${imgB(lvsB())}/api/pc/vg/cover?sid=${r.sid}" onerror="this.style.visibility='hidden'"><em class="lvsSG"></em><i class="lvpE"></i><b class="lvpDu">${lvsT(r.dur).replace(/^0:/,"")}</b></div><div class="lvpNm">${lvsE(r.name)}</div>${lvsNvl(r)}<small>${lvsSidL(r.sid)} · ${lvsD(r.t)} · ${lvpGB(r.mb)}${r.g?` · <u>${lvsE(r.g)}</u>`:""}</small></div>`;}
function lvpCardEx(it,r){const e=it.querySelector(".lvpE");if(!e)return;const n=+r.ne||0,p=+r.nep||0;e.textContent=n?`✂ 初剪 ${n} ${p?"−":"✔"}`:"✂ −";e.classList.toggle("on",n>0&&!p);e.classList.toggle("run",p>0);   /* TK_V0.9.03 輸出中＝橘色 −；好了＝綠色 ✔ */
  it.classList.toggle("eRun",p>0);it.classList.toggle("eOk",n>0&&!p);it.style.setProperty("--lc",r.lv==null?"transparent":LVSC[String(r.lv)][2]);}
/* 有在輸出的：每 6 秒問一次，做完就改成綠色 ✔ */
function lvpPoll(){if(LVS.pt)return;const go=async()=>{LVS.pt=0;if(!LVS.pc||!LVS.root||!LVS.root.isConnected)return;const R=(LVS.all||[]).filter(r=>r.nep>0);if(!R.length)return;
  let s=null;try{s=await lvsGet("/api/pc/edit/status");}catch(e){}if(s){const P=new Set([(s.cur||{}).sid].concat((s.q||[]).map(x=>x.sid)).filter(Boolean).map(Number));
    R.forEach(r=>{if(!P.has(+r.sid)){r.nep=0;const i=LVS.L.indexOf(r);if(i>=0)lvsStripPaint(i);}});}
  if((LVS.all||[]).some(r=>r.nep>0))LVS.pt=setTimeout(go,6000);};LVS.pt=setTimeout(go,6000);}
/* 等級格子＋資料夾樹＋進度＋總計（都有 GB） */
function lvpSum(){if(!LVS.pc||!LVS.root)return;const F=LVS.F,all=LVS.all||[],sk=(typeof vgLS!=="undefined"&&vgLS.get("skiplv",false)),q=(F.q||"").toLowerCase();
  const base=all.filter(r=>(!q||String(r.name||"").toLowerCase().includes(q)||String(r.u||"").toLowerCase().includes(q)||String(r.sid)===q.replace(/^#0*/,""))&&(!F.g.length||F.g.includes(r.g||"-")));
  const sum=L=>[L.length,L.reduce((a,r)=>a+(+r.mb||0),0)],rdy=r=>r.prx!=null?r.prx>=80:r.pr!=null?r.pr>=80:(r.pv===1||r.s2===1),hasPr=all.some(r=>r.pr!=null);
  /* 資料夾樹 */
  const inCat=c=>base.filter(r=>c==="*"||(r.cat||"")===c);const cats=[["*","全部"],["","未分類"]].concat((LVS.cats||[]).map(x=>[x.id,x.name]));
  LVS.root.querySelector("#lvpTree").innerHTML=cats.map(([id,nm],k)=>{const L=inCat(id);if(k>0&&!L.length)return "";const [n,mb]=sum(L),rd=L.filter(rdy).length;
    return `<div class="lvpTi${F.cat===id?" on":""}${k?" sub":""}" data-cat="${lvsE(id)}">${k?"📁":"🗂"} ${lvsE(nm)} <b>${n}</b><small>${hasPr?`（預覽好 ${rd}）`:""} ${lvpGB(mb)}</small></div>`;}).join("");
  /* 等級格子 */
  const B=base.filter(r=>F.cat==="*"||(r.cat||"")===F.cat),[na,mba]=sum(B),Rd=B.filter(r=>rdy(r)&&lvsLvKey(r)==="0"),[nr,mbr]=sum(Rd);   /* TK_V0.9.48 「可以看」＝預覽好、而且還沒標等級的（標一場就少一場） */
  const chip=(k,t,c,L,on)=>{const [n,mb]=sum(L);return `<button data-k="${k}" class="${on?"on":""}" style="--c:${c}"><b>${t} ${n}</b><small>${lvpGB(mb)}</small></button>`;};
  LVS.root.querySelector("#lvpChips").innerHTML=chip("all","全部","#4dc9ff",B,!F.lvf)+chip("ready",hasPr?"✔ 可以看":"✔ 可以看","#45d483",Rd,F.pv)+
    LVP_LV.map(([k,t,c])=>chip(k,t,c,B.filter(r=>lvsLvKey(r)===k),F.lvf===k)).join("");
  const g=B.filter(lvsGd).length;LVS.root.querySelector("#lvpProgI").style.width=(na?g*100/na:0)+"%";LVS.root.querySelector("#lvpProgT").textContent=`已分級 ${g} / ${na}`;
  const L=LVS.L||[],[nl,mbl]=sum(L),du=L.reduce((a,r)=>a+(+r.dur||0),0),ne=L.reduce((a,r)=>a+(+r.ne||0),0);
  LVS.root.querySelector("#lvpFoot").innerHTML=`${nl} 部 · ${lvpGB(mbl)} · ${Math.floor(du/3600)}:${String(Math.floor(du%3600/60)).padStart(2,"0")} 小時 · 初剪 ${ne} 段${nr!==na&&hasPr?` · 預覽好 ${nr}`:""}`;
  const u=LVS.root.querySelector("#lvpUndo");if(u){const n=(LVS.autoL||[]).length;u.hidden=!n;u.textContent=`↩ 復原自動 −2（${n}）`;}}
/* 右上：現在這場 */
function lvpCur(i){const r=LVS.L[i],h=LVS.root&&LVS.root.querySelector("#lvpHd");if(!h)return;if(!r){h.innerHTML="";return;}
  const cat=(LVS.cats||[]).find(x=>x.id===r.cat);
  h.innerHTML=`<b>${lvsE(r.name)}</b> <small>@${lvsE(r.u)}</small><div>${lvsSidL(r.sid)} · ${lvsD(r.t)} 開播 · ${lvsT(r.dur)} · ${lvpGB(r.mb)} · 📁 ${lvsE(cat?cat.name:"未分類")}${r.g?` · 審核 ${lvsE(r.g)}`:""}${r.ne?` · ✂ 初剪 ${r.ne} 段`:""} · ${i+1} / ${LVS.L.length}</div>`;
  LVS.root.querySelectorAll("#lvpTb .lvpLv").forEach(b=>b.classList.toggle("on",b.dataset.v===""?r.lv==null:(r.lv!=null&&String(r.lv)===b.dataset.v)));}
function lvpSelPaint(){const b=LVS.root&&LVS.root.querySelector("#lvpCut");if(!b)return;const G=lvsSegs(),n=LVS.sel?LVS.sel.set.size:0,tot=G.reduce((a,g)=>a+(g.e-g.s),0);
  b.textContent=`✂ 輸出初剪（${G.length} 段${n?` · ${n} 張 · ${lvsDur(tot)}`:""}）`;b.disabled=!n;}
/* LVP-END */

@@SH71@@


@@SH72@@

@@SH73@@

@@SH74@@

/* SN-BEGIN */
/* ================= V0.6.62 只錄聲音的快照：放在影片的位置，跟著播放時間換；‹ › 翻上一張／下一張（手機回放、網頁版歷史回放共用） ================= */
const SN={L:[],sid:0,box:null,seek:null,clk:null,cur:-1,t:0,view:0,lay:[4,5],mp4:false,time:true,fy:0,u:""};
const snB=()=>(typeof B==="string"?B:"");
const snHms=s=>{s=Math.max(0,Math.floor(+s||0));const p=n=>String(n).padStart(2,"0");return `${Math.floor(s/3600)}:${p(Math.floor(s%3600/60))}:${p(s%60)}`;};
function snUrl(i){const x=SN.L[i];return x?`${imgB(snB())}/snap/${SN.sid}/${x[1]}`:"";}
/* V1.1.51 總覽格子用縮小版（快速通道才有；原圖留給放大看、下載） */
function snW(){const c=(SN.lay&&SN.lay[1])||5,px=(window.innerWidth||800)/c*(window.devicePixelRatio||1);return px<=260?240:px<=380?360:px<=520?480:720;}
function snUrlS(i){const u=snUrl(i);return u&&window.FASTB?u+"?w="+snW():u;}
function snIdx(t){const L=SN.L;let lo=0,hi=L.length;while(lo<hi){const m=(lo+hi)>>1;if(L[m][0]<=t+1)lo=m+1;else hi=m;}return Math.max(0,lo-1);}
function snMount(box,sid,L,seek,clk,lay){SN.L=(L||[]).slice();SN.sid=sid;SN.seek=seek;SN.clk=clk;SN.cur=-1;SN.t=0;SN.box=box;SN.view=0;SN.lay=(lay&&lay.length===2)?lay:[4,5];SN.mp4=false;if(!box)return false;
  try{const t=localStorage.getItem("tlm_sntime");SN.lab=t==="0"||t==="n"?"n":t==="x"?"x":"t";SN.gap=+(localStorage.getItem("tlm_sngap")??2);if(!isFinite(SN.gap))SN.gap=2;SN.zh=localStorage.getItem("tlm_snzh")||"r";SN.zv=localStorage.getItem("tlm_snzv")||"d";}catch(e){SN.lab="t";SN.gap=2;SN.zh="r";SN.zv="d";}
  SN.time=SN.lab==="t";
  let w=box.querySelector(".snv");if(!SN.L.length){if(w)w.remove();   /* TK_V0.9.93 這場沒有截圖：也給一個「截圖」入口（有完整 MP4 才能截），不然 MP4/JPG 按鈕不見、找不到地方截 */
    w=document.createElement("div");w.className="snv snEmpty";box.insertBefore(w,box.firstChild);
    w.innerHTML=`<div class="snEm"><b>📷 這場目前沒有截圖</b><span class="snEmT">檢查中…</span><button class="snPkGo" data-st="regen" hidden>▦ 從影片截圖</button></div>`;
    w.querySelector("[data-st=regen]").onclick=e=>{e.stopPropagation();snPick();};snInfo(sid);return true;}
  if(!w){w=document.createElement("div");w.className="snv";box.insertBefore(w,box.firstChild);}
  /* V0.6.98 照片／影片切換：照片第一頁是全覽（一列 5 張），往右滑一張一張看、下載；影片＝這場剪好的（含初剪） */
  w.innerHTML=`<div class="snTabs" hidden><button data-sm="p" class="on">📷 照片 <b class="snNP">${SN.L.length}</b></button><button data-sm="v" hidden>✂ 剪輯 <b class="snNV">0</b></button></div>
<div class="snPg"></div><div class="snVid" hidden></div><button class="snBack" title="回到照片">📷 回到照片</button><button class="snHome" hidden title="回到全覽（最前面那一頁）">▦ 回總覽</button><div class="snGrip" title="上下拖：調整照片大小（點兩下恢復）"><i></i></div><button class="snb snp" title="上一張">‹</button><button class="snb snn" title="下一張">›</button><div class="snl" hidden></div>
<div class="snTool"><span class="snFy" title="臉偏上／偏下：每一格的中心一起往上／往下移（▲▼ 一次 1、▴▾ 一次 0.1；這位主播會記住）"><button data-st="up">▲</button><button data-st="up1">▴</button><em class="snFyV">0</em><button data-st="dn1">▾</button><button data-st="dn">▼</button></span><button data-st="strip" title="確定這個裁切可以：每一張照全覽現在的比例、▲▼ 位置，一張一張往右滑著看">↔ 展開</button><button data-st="clips" hidden title="這場剪好的影片">✂ <span class="snNV2">0</span></button><button data-st="swap" title="欄列對調（例如 6×10 ⇄ 10×6）">⇄</button><button data-st="opt" title="版面：每格下面顯示什麼（時間／編號／不顯示）、圖跟圖的間距（可以負數重疊）、誰疊在誰上面">⚙ 版面</button><button data-st="regen" title="重新截圖：選幾列 × 幾欄（新的截好才換掉現在的照片；要有完整的原檔 MP4）">▦ <span class="snLay"></span></button><button data-st="dl" title="把現在看到的全覽合成一張大圖下載（原圖大小）">⬇ 下載</button><button data-st="mos" title="照現在的排版，每一格播那一刻往後幾秒、同時播放，做成 MP4 或 GIF">🎞 動圖</button><button data-st="nvk" class="snNvk" hidden></button></div>`;
  w.querySelector(".snTool").onclick=e=>{const b=e.target.closest("[data-st]");if(!b)return;e.stopPropagation();const a=b.dataset.st;
    if(a==="up"||a==="dn"||a==="up1"||a==="dn1"){snFySet(SN.fy+({up:1,dn:-1,up1:0.1,dn1:-0.1})[a]);return;}
    if(a==="strip"){snCrop(true);snGo(1);return;}   /* V0.7.13 展開：照全覽現在的裁切，一張一張往右滑 */
    if(a==="opt"){snOpt(b);return;}if(a==="swap"){const LY=snLayEff();snLaySet([LY[1],LY[0]]);return;}if(a==="clips"){snMode("v");return;}if(a==="nvk"){snNvtKeep(b);return;}
    if(a==="regen")snPick();else if(a==="dl")snMerge();else if(a==="mos")snMosOpen();};
  snInfo(sid);
  w.querySelector(".snp").onclick=e=>{e.stopPropagation();snGo(SN.view-1);};w.querySelector(".snn").onclick=e=>{e.stopPropagation();snGo(SN.view+1);};
  w.querySelector(".snBack").onclick=e=>{e.stopPropagation();snMode("p");};
  {const hm=w.querySelector(".snHome");["pointerdown","touchstart","mousedown"].forEach(ev=>hm.addEventListener(ev,e=>e.stopPropagation()));hm.onclick=e=>{e.stopPropagation();e.preventDefault();snGo(0);};}   /* V0.7.21 單張左上角：回到全覽 */
  w.querySelector(".snTabs").onclick=e=>{const b=e.target.closest("[data-sm]");if(b){e.stopPropagation();snMode(b.dataset.sm);}};
  const pg=w.querySelector(".snPg");snBuild();snGripInit(w);
  pg.addEventListener("scroll",()=>{clearTimeout(SN.st);SN.st=setTimeout(()=>{const v=Math.round(pg.scrollLeft/Math.max(1,pg.clientWidth));if(v!==SN.view){SN.view=v;snLabel();snLoadNear();
    if(v>0&&SN.user){const x=SN.L[v-1];if(x&&SN.seek){SN.lock=Date.now();SN.seek(Math.max(0,x[0]));}}}SN.user=false;},120);},{passive:true});
  pg.addEventListener("pointerdown",()=>{SN.user=true;},{passive:true});pg.addEventListener("touchstart",()=>{SN.user=true;},{passive:true});pg.addEventListener("wheel",()=>{SN.user=true;},{passive:true});
  pg.onclick=e=>{const g=e.target.closest("[data-gi]");if(g){if(SN.strip){const x=SN.L[+g.dataset.gi];if(x&&SN.seek)SN.seek(Math.max(0,x[0]));return;}SN.user=true;snCrop(false);snGo(+g.dataset.gi+1,true);return;}const d=e.target.closest("[data-sd]");if(d){e.stopPropagation();snDel();return;}
    const dl=e.target.closest("a.snDl");if(dl&&SN.crop){e.preventDefault();e.stopPropagation();snCropDl(SN.view-1);}};   /* 展開（裁切）時下載：照畫面上的裁切、原圖解析度 */
  if(typeof clMount==="function"){const vb=w.querySelector(".snVid");clMount(vb,{sid,always:true,pause:()=>{},after:n=>{const t=w.querySelector("[data-st=clips]");if(!t)return;t.hidden=!n;t.querySelector(".snNV2").textContent=n;   /* V0.7.12 上面的「照片／剪輯」拿掉：剪好的改成右下角一顆按鈕 */
    }});}   /* V0.7.08 一律先看照片 */
  snLabel();return true;}
/* V0.7.08 照片可以上下拖放大縮小：全覽每張一列 5 張、左右一定填滿；放大到夠高就是完整的 9:16，縮小時圖片置中裁切 */
function snVis(c,r,C,R,cw,th,gp){const x=c*(cw+gp),y=r*(th+gp);let vx=x,vw=cw,vy=y,vh=th;   /* 疊在一起時，這張沒被蓋住的那一塊 */
  if(gp<0){if(SN.zh==="r"){if(c<C-1)vw=cw+gp;}else{if(c>0){vx=x-gp;vw=cw+gp;}}if(SN.zv==="d"){if(r<R-1)vh=th+gp;}else{if(r>0){vy=y-gp;vh=th+gp;}}}
  return {x:vx,y:vy,w:Math.max(8,vw),h:Math.max(8,vh)};}
function snCrop(on){SN.crop=!!on;const w=SN.box&&SN.box.querySelector(".snv");if(w)w.querySelector(".snPg").classList.toggle("crop",SN.crop);}
function snCropDl(i){const x=SN.L[i];if(!x)return;const im=new Image();if(window.FASTB)im.crossOrigin="anonymous";im.onload=()=>{const ar=(SN.cw||9)/(SN.th||16),nw=im.naturalWidth,nh=im.naturalHeight;let cw,ch;if(nw/nh>ar){ch=nh;cw=Math.round(nh*ar);}else{cw=nw;ch=Math.round(nw/ar);}
  const sx=(nw-cw)/2,sy=(nh-ch)*(50-SN.fy)/100,cv=document.createElement("canvas");cv.width=cw;cv.height=ch;cv.getContext("2d").drawImage(im,sx,sy,cw,ch,0,0,cw,ch);
  cv.toBlob(b=>{const a=document.createElement("a");a.href=URL.createObjectURL(b);a.download=(x[1]||"snap.jpg").split("/").pop().replace(/\.jpg$/i,"_裁切.jpg");document.body.appendChild(a);a.click();setTimeout(()=>{URL.revokeObjectURL(a.href);a.remove();},4000);},"image/jpeg",0.92);};im.src=snUrl(i);}
function snZ(c,r){return 1+(SN.zv==="d"?r:500-r)*200+(SN.zh==="r"?c:199-c);}   /* 誰疊在誰上面：下搭上／上搭下、右搭左／左搭右 */
function snFit(){const w=SN.box&&SN.box.querySelector(".snv");if(!w)return;const pg=w.querySelector(".snPg"),g=w.querySelector(".snGrid");if(!pg||!g)return;
  const N=SN.L.length,gp=+SN.gap||0,W=pg.clientWidth||300,H=pg.clientHeight||300;let C,R,cw,th;   /* V0.7.12 自己排位置：間距可以負數（重疊） */
  if(SN.strip){R=1;C=Math.max(1,N);th=Math.max(30,H-2);cw=Math.max(20,th/(SN.ratio||16/9));}
  else{const LY=snLayEff();C=Math.max(1,LY[1]);R=Math.max(1,Math.ceil(N/C));const Rv=Math.max(1,Math.min(LY[0],R));cw=Math.max(10,(W-(C-1)*gp)/C);th=Math.max(28,Math.min(cw*16/9,(H-(Rv-1)*gp)/Rv));}
  SN.th=th;SN.cw=cw;const T=g.children;
  for(let i=0;i<T.length;i++){const el=T[i];if(!el.classList.contains("snG"))continue;const c=i%C,r=Math.floor(i/C);el.style.left=(c*(cw+gp))+"px";el.style.top=(r*(th+gp))+"px";el.style.width=cw+"px";el.style.height=th+"px";el.style.zIndex=snZ(c,r);}
  g.querySelectorAll(".snLb").forEach(el=>{const i=+el.dataset.li,c=i%C,r=Math.floor(i/C),v=snVis(c,r,C,R,cw,th,gp);   /* 字一律浮在最上面，放在這張「露出來」的那一塊的下緣 */
    el.style.left=(SN.lab==="t"?v.x+v.w/2:v.x+3)+"px";el.style.top=(v.y+v.h-3)+"px";});
  const tw=C*cw+(C-1)*gp,thh=R*th+(R-1)*gp;g.style.width=(SN.strip?tw:W)+"px";g.style.height=Math.max(0,thh)+"px";g.style.marginTop=(!SN.strip&&thh<H)?((H-thh)/2)+"px":"0";
  {const ar=cw/th,bw=Math.min(W,H*ar);pg.style.setProperty("--snbw",bw+"px");pg.style.setProperty("--snbh",(bw/ar)+"px");pg.style.setProperty("--snfy",(50-SN.fy)+"%");}
  const ly=w.querySelector(".snLay");if(ly){const LY=snLayEff();ly.textContent=`${LY[0]}×${LY[1]}`;}const rg=w.querySelector("[data-st=regen]");if(rg)rg.hidden=!SN.mp4;
  const vd=w.querySelector(".snVid");if(vd&&!w.closest(".snHost"))vd.style.minHeight=H+"px";}
/* TK_V0.9.23 看的排列（不用重新截圖）：照張數列出剛好排滿的組合（60 張＝2×30、3×20、4×15、5×12、6×10…），也可以欄列對調；這台裝置記住（照張數分開記） */
function snLayEff(){const N=SN.L.length,ex=snLayPairs(N).length>0;try{const v=JSON.parse(localStorage.getItem("tlm_snlay_"+N)||"null");if(v&&v.length===2&&v[0]>0&&v[1]>0&&(ex?v[0]*v[1]===N:v[0]*v[1]>=N))return v;}catch(e){}   /* TK_V0.9.92 排得滿的張數：只用剛好排滿的版面（42 張不會變 6×8 空 6 格） */
  const L=SN.lay;if(ex&&L[0]*L[1]!==N){const P=snLayPairs(N);return P.reduce((a,b)=>Math.abs(b[1]-L[1])<Math.abs(a[1]-L[1])?b:a);}return L;}
function snLaySet(v){try{localStorage.setItem("tlm_snlay_"+SN.L.length,JSON.stringify(v));}catch(e){}snFit();const o=document.getElementById("snOpt");if(o&&o._draw)o._draw();}
function snLayPairs(N){const P=[];for(let r=2;r<=N/2;r++)if(N%r===0&&N/r>=2&&N/r<=30&&r<=40)P.push([r,N/r]);return P;}
function snOpt(btn){let ov=document.getElementById("snOpt");if(ov){ov.remove();return;}ov=document.createElement("div");ov.id="snOpt";
  const seg=(k,L)=>`<div class="snOS">${L.map(([v,t])=>`<button data-k="${k}" data-v="${v}"${String(SN[k])===String(v)?' class="on"':""}>${t}</button>`).join("")}</div>`;
  const draw=()=>{ov.innerHTML=`<div class="snOR"><b>每格下面</b>${seg("lab",[["t","時間"],["n","編號"],["x","不顯示"]])}</div>
<div class="snOR"><b>間距</b><div class="snOS"><button data-g="-5">−5</button><button data-g="-1">−1</button><em>${SN.gap}</em><button data-g="1">＋1</button><button data-g="5">＋5</button><button data-g="0r">預設</button></div></div><div class="snOH">負數＝圖跟圖疊在一起</div>
${(()=>{const N=SN.L.length,LY=snLayEff(),P=snLayPairs(N);return P.length?`<div class="snOR"><b>排列</b><div class="snOS snOLy">${P.map(([r,c])=>`<button data-ly="${r}x${c}"${LY[0]===r&&LY[1]===c?' class="on"':""}>${r}×${c}</button>`).join("")}<button data-ly="swap">⇄ 欄列對調</button></div></div><div class="snOH">${N} 張剛好排滿的組合（列×欄）；只換看的方式，不用重新截圖</div>`:"";})()}
<div class="snOR"><b>左右疊</b>${seg("zh",[["r","右搭左"],["l","左搭右"]])}</div><div class="snOR"><b>上下疊</b>${seg("zv",[["d","下搭上"],["u","上搭下"]])}</div>`;};
  ov._draw=draw;draw();document.body.appendChild(ov);const rc=btn.getBoundingClientRect();ov.style.right=Math.max(6,window.innerWidth-rc.right)+"px";ov.style.bottom=Math.max(6,window.innerHeight-rc.top+6)+"px";
  ov.onclick=e=>{e.stopPropagation();const b=e.target.closest("button");if(!b)return;
    if(b.dataset.ly){if(b.dataset.ly==="swap"){const LY=snLayEff();snLaySet([LY[1],LY[0]]);}else{const [r,c]=b.dataset.ly.split("x").map(Number);snLaySet([r,c]);}draw();return;}
    if(b.dataset.g){SN.gap=b.dataset.g==="0r"?2:Math.max(-80,Math.min(40,SN.gap+(+b.dataset.g)));try{localStorage.setItem("tlm_sngap",SN.gap);}catch(x){}snFit();draw();return;}
    const k=b.dataset.k,v=b.dataset.v;if(!k)return;SN[k]=v;try{localStorage.setItem(k==="lab"?"tlm_sntime":k==="zh"?"tlm_snzh":"tlm_snzv",v);}catch(x){}if(k==="lab"){SN.time=v==="t";snBuild();}else snFit();draw();};
  const off=e=>{if(!ov.isConnected){document.removeEventListener("pointerdown",off,true);return;}if(!ov.contains(e.target)&&!btn.contains(e.target)){ov.remove();document.removeEventListener("pointerdown",off,true);}};setTimeout(()=>document.addEventListener("pointerdown",off,true),0);}
function snGripInit(w){const gr=w.querySelector(".snGrip"),pg=w.querySelector(".snPg");if(!gr||!pg)return;
  try{const h=+localStorage.getItem("tlm_snh");if(h>=140&&!w.closest(".snHost"))pg.style.height=Math.min(window.innerHeight*0.92,h)+"px";}catch(e){}
  let d=null;gr.onpointerdown=e=>{gr.setPointerCapture(e.pointerId);d={y:e.clientY,h:pg.getBoundingClientRect().height};e.preventDefault();gr.classList.add("on");e.stopPropagation();};
  gr.onpointermove=e=>{if(!d)return;const h=Math.max(140,Math.min(window.innerHeight*0.92,d.h+e.clientY-d.y));pg.style.height=h+"px";d.nh=h;snFit();};
  gr.onpointerup=gr.onpointercancel=()=>{gr.classList.remove("on");if(d&&d.nh)try{localStorage.setItem("tlm_snh",Math.round(d.nh));}catch(e){}d=null;snGo(SN.view,false,true);};
  gr.ondblclick=()=>{pg.style.height="";try{localStorage.removeItem("tlm_snh");}catch(e){}snFit();snGo(SN.view,false,true);};
  try{SN.ro&&SN.ro.disconnect();SN.ro=new ResizeObserver(()=>snFit());SN.ro.observe(pg);}catch(e){}}
/* ---------- V0.7.09 版面、重新截圖、合成一張大圖 ---------- */
/* TK_V0.9.75 只錄聲音的場次：MP4 暫存 5 天（沒按「📌 留下」到期自動刪） */
async function snNvt(sid){let j=null;try{j=await fetch(`${snB()}/api/pc/nvtmp?sid=${sid}`,{cache:"no-store"}).then(r=>r.json());}catch(e){}if(SN.sid!==sid)return;const b=SN.box&&SN.box.querySelector(".snv [data-st=nvk]");if(!b)return;
  if(!j||!j.on||!j.has){b.hidden=true;return;}b.hidden=false;b.classList.toggle("on",!!j.keep);
  b.textContent=j.keep?"📌 已留下":`🕔 暫存 剩 ${j.left<1?Math.max(0,Math.round(j.left*24))+" 小時":Math.ceil(j.left)+" 天"} · 📌 留下`;b.title=j.keep?"這場只錄聲音的 MP4 已經留下，不會自動刪（點一下取消留下）":`只錄聲音的場次：MP4 暫存 ${j.days} 天，到期沒留下就自動刪（截圖照留）。點一下留下這場的 MP4`;}
async function snNvtKeep(b){const keep=!b.classList.contains("on");const P_=typeof kPost==="function"?kPost:(typeof post==="function"?post:null);let j=null;try{j=P_?await P_("/api/pc/nvtmp",{sid:SN.sid,keep:keep?1:0}):null;}catch(e){}
  if(j&&j.message)(typeof toast==="function"?toast:alert)(j.message);snNvt(SN.sid);}
async function snInfo(sid){let j=null;try{j=await fetch(`${snB()}/api/pc/snap/info?sid=${sid}`,{cache:"no-store"}).then(r=>r.json());}catch(e){}if(!j||!j.ok||SN.sid!==sid)return;
  const ch=JSON.stringify(j.layout)!==JSON.stringify(SN.lay);SN.lay=j.layout||SN.lay;SN.mp4=!!j.mp4;SN.mp4why=j.mp4why||"";const R=j.regen||{};
  {const em=SN.box&&SN.box.querySelector(".snEmpty");if(em){if((j.snaps||[]).length&&!R.running&&!(R.pickL&&R.pickL.length)){SN.L=j.snaps.slice();em.remove();snMount(SN.box,sid,SN.L,SN.seek,SN.clk,j.layout);return;}
    const t=em.querySelector(".snEmT"),bt=em.querySelector("[data-st=regen]");if(R.running){t.textContent=`截圖中 ${R.done||0}/${R.total||0}…`;clearTimeout(SN.rt);SN.rt=setTimeout(()=>snInfo(sid),1500);SN.regenOn=true;}
    else{t.textContent=SN.mp4?"按下面的按鈕從影片截（可以多截一倍讓你挑）":((SN.mp4why||"這場沒有完整的原檔 MP4")+"，沒辦法截");bt.hidden=!SN.mp4;}
    if(R.pickL&&R.pickL.length&&!document.getElementById("snSel"))snSelOpen(sid,R);return;}}
  if(!SN._nvq||SN._nvq!==sid){SN._nvq=sid;snNvt(sid);}
  if(j.u&&j.u!==SN.u){SN.u=j.u;try{const v=localStorage.getItem("tlm_snfy_"+SN.u);SN.fy=v==null?0:+v||0;}catch(e){}snFyApply();}
  const b=SN.box&&SN.box.querySelector(".snv [data-st=regen]");
  if(R.running){if(b)b.innerHTML=`⏳ ${R.done||0}/${R.total||0}`;clearTimeout(SN.rt);SN.rt=setTimeout(()=>snInfo(sid),1500);SN.regenOn=true;return;}
  if(R.pickL&&R.pickL.length){if(b)b.innerHTML=`▦ <span class="snLay">${snLayEff().join("×")}</span>`;SN.regenOn=false;if(!document.getElementById("snSel"))snSelOpen(sid,R);return;}   /* TK_V0.9.91 截好了：等你挑 */
  if(SN.regenOn){SN.regenOn=false;SN.L=(j.snaps||[]).slice();SN.view=0;snBuild();(typeof toast==="function"?toast:alert)((R.ok?"✔ ":"✖ ")+(R.msg||""));}
  if(b)b.innerHTML=`▦ <span class="snLay">${snLayEff().join("×")}</span>`;if(ch)snBuild();else snFit();}
const SN_LAYS=[[6,10],[10,6],[5,12],[4,15],[3,20],[2,5],[3,5],[4,5],[5,5],[6,5],[8,5],[10,5],[3,4],[4,4],[6,4],[8,4],[3,6],[4,6],[5,6],[6,6],[8,6],[10,6],[3,7],[4,7],[6,7],[8,7],[4,8],[6,8],[8,8],[12,8],[5,10],[8,10],[10,10],[12,10],[10,15],[12,15],[10,20],[15,20]];
/* V0.7.10 臉偏上／偏下：每一格的中心點一起往上／下移（正數＝往上看多一點），這位主播記住 */
function snFySet(v){SN.fy=Math.round(Math.max(-50,Math.min(50,v))*10)/10;try{if(SN.u)localStorage.setItem("tlm_snfy_"+SN.u,SN.fy);}catch(e){}snFyApply();}
function snFyApply(){const w=SN.box&&SN.box.querySelector(".snv");if(!w)return;const g=w.querySelector(".snGrid");if(g)g.style.setProperty("--snfy",(50-SN.fy)+"%");const pg0=w.querySelector(".snPg");if(pg0){pg0.style.setProperty("--snfy",(50-SN.fy)+"%");pg0.classList.toggle("crop",!!SN.crop);}
  const e=w.querySelector(".snFyV");if(e)e.textContent=(SN.fy>0?"+":"")+(Number.isInteger(SN.fy)?SN.fy:SN.fy.toFixed(1));}
function snPick(){if(!SN.mp4){(typeof toast==="function"?toast:alert)((SN.mp4why||"這場已經沒有完整的原檔 MP4")+"，不能重新截圖（現在的照片只能換版面）");return;}let ov=document.getElementById("snPick");if(ov)ov.remove();ov=document.createElement("div");ov.id="snPick";
  ov.innerHTML=`<div class="snPkW"><div class="snPkH"><b>重新截圖：幾列 × 幾欄</b><button data-pk="x">✕</button></div><div class="snPkN">剛好排滿：一列幾張＝欄。重新截圖會<b>清掉這場現在的 ${SN.L.length} 張照片</b>（挑剩的也一起清），再從 MP4 平均截。</div>
<div class="snPkG">${SN_LAYS.map(([r,c])=>`<button data-r="${r}" data-c="${c}"${r===SN.lay[0]&&c===SN.lay[1]?' class="on"':""}>${r}×${c}<small>${r*c} 張</small></button>`).join("")}</div>
<div class="snPkC">自訂：<input type="number" id="snPkR" min="1" max="40" value="${SN.lay[0]}"> 列 × <input type="number" id="snPkCo" min="1" max="30" value="${SN.lay[1]}"> 欄 <span id="snPkT"></span><button data-pk="go" class="snPkGo">重新截圖</button></div>
<label class="snPkM"><input type="checkbox" id="snPkM" checked> 多截一倍讓我挑（例如要 20 張就截 40 張，有擋住、拍糊的不要選；挑好之前現在的照片都不動）</label></div>`;
  document.body.appendChild(ov);const r_=ov.querySelector("#snPkR"),c_=ov.querySelector("#snPkCo"),t_=ov.querySelector("#snPkT");const upd=()=>{const n=(+r_.value||0)*(+c_.value||0);t_.textContent=`＝ ${n} 張`;};upd();r_.oninput=c_.oninput=upd;
  ov.onclick=async e=>{if(e.target===ov||e.target.closest("[data-pk=x]")){ov.remove();return;}const b=e.target.closest("[data-r]");if(b){r_.value=b.dataset.r;c_.value=b.dataset.c;upd();ov.querySelectorAll(".snPkG .on").forEach(x=>x.classList.remove("on"));b.classList.add("on");return;}
    if(e.target.closest("[data-pk=go]")){const R=Math.max(1,Math.min(40,+r_.value||4)),C=Math.max(1,Math.min(30,+c_.value||5));if(R*C>600){(typeof toast==="function"?toast:alert)("最多 600 張");return;}   /* TK_V0.8.95 欄上限 12→30、總數 240→600 */
      const M=ov.querySelector("#snPkM").checked?2:1;   /* TK_V0.9.91 */
      if(M===1&&!confirm(`重新截 ${R}×${C}＝${R*C} 張？\n\n這場現在的 ${SN.L.length} 張照片會全部清掉，不能復原。`))return;
      const P=typeof kPost==="function"?kPost:(typeof post==="function"?post:(typeof deepPost==="function"?deepPost:null));if(!P)return;const j=await P("/api/pc/snap/regen",{sid:SN.sid,rows:R,cols:C,mult:M});
      (typeof toast==="function"?toast:alert)((j&&j.ok?"✔ ":"✖ ")+((j&&j.message)||"沒有成功"));if(j&&j.ok){ov.remove();SN.regenOn=true;SN.lay=[R,C];setTimeout(()=>snInfo(SN.sid),800);}}};}
async function snMerge(){const w=SN.box&&SN.box.querySelector(".snv");if(!w||!SN.L.length)return;const T=m=>(typeof toast==="function"?toast(m):0);T("合成中…");
  const N=SN.L.length,C=SN.strip?N:Math.max(1,snLayEff()[1]),R=Math.ceil(N/C),ratio=(SN.th||100)/(SN.cw||56);   /* 跟畫面上一樣：比例、間距（負數重疊）、誰疊誰、▲▼、時間／編號，原圖大小 */
  const imgs=await Promise.all(SN.L.map((x,i)=>new Promise(res=>{const im=new Image();if(window.FASTB)im.crossOrigin="anonymous";im.onload=()=>res(im);im.onerror=()=>res(null);im.src=snUrl(i);})));
  const nat=imgs.find(Boolean);if(!nat){T("✖ 讀不到照片");return;}let tw=nat.naturalWidth||720,k=tw/(SN.cw||56),gs=(+SN.gap||0)*k,th=Math.round(tw*ratio);
  let CW=C*tw+(C-1)*gs,CH=R*th+(R-1)*gs;const f=Math.min(1,16000/Math.max(CW,CH));if(f<1){tw*=f;th*=f;gs*=f;CW*=f;CH*=f;}
  const cv=document.createElement("canvas");cv.width=Math.max(1,Math.round(CW));cv.height=Math.max(1,Math.round(CH));const g=cv.getContext("2d");g.fillStyle="#000";g.fillRect(0,0,cv.width,cv.height);
  const ord=imgs.map((im,i)=>({im,i,c:i%C,r:Math.floor(i/C)})).sort((a,b)=>snZ(a.c,a.r)-snZ(b.c,b.r));
  for(const {im,i,c,r} of ord){const x=c*(tw+gs),y=r*(th+gs);if(im){const s=Math.max(tw/im.naturalWidth,th/im.naturalHeight),dw=im.naturalWidth*s,dh=im.naturalHeight*s;g.save();g.beginPath();g.rect(x,y,tw,th);g.clip();g.drawImage(im,x+(tw-dw)/2,y+(th-dh)*(50-SN.fy)/100,dw,dh);g.restore();}
  }
  if(SN.lab!=="x")for(let i=0;i<N;i++){const c=i%C,r=Math.floor(i/C),v=snVis(c,r,C,R,tw,th,gs),tx=SN.lab==="t"?(SN.clk?SN.clk(SN.L[i][0]):snHms(SN.L[i][0])):String(i+1),fs=Math.max(14,Math.round(Math.min(tw,th)*0.07));g.font=`700 ${fs}px system-ui,sans-serif`;
      const mw=g.measureText(tx).width+fs*0.8,bx=SN.lab==="t"?v.x+(v.w-mw)/2:v.x+fs*0.3,by=v.y+v.h-fs*1.6;g.fillStyle="rgba(0,0,0,.55)";g.fillRect(bx,by,mw,fs*1.3);g.fillStyle="#fff";g.textBaseline="middle";g.fillText(tx,bx+fs*0.4,by+fs*0.65);}
  cv.toBlob(b=>{if(!b){T("✖ 合成失敗（圖太大）");return;}const a=document.createElement("a");a.href=URL.createObjectURL(b);a.download=`#${String(SN.sid).padStart(5,"0")}_${SN.strip?"展開":"全覽"}_${R}x${C}.jpg`;document.body.appendChild(a);a.click();setTimeout(()=>{URL.revokeObjectURL(a.href);a.remove();},4000);T(`✔ 已合成 ${C}×${R}（${cv.width}×${cv.height}）`);},"image/jpeg",0.9);}
function snImgErr(im){const k=+(im.dataset.r||0);if(k>=3)return;im.dataset.r=k+1;setTimeout(()=>{if(im.isConnected)im.src=im.src.split("?")[0]+"?r="+Date.now();},2000*(k+1));if(k===1&&SN.sid)snRefresh(SN.sid);}
async function snRefresh(sid){if(SN._rf&&Date.now()-SN._rf<5000)return;SN._rf=Date.now();let j=null;try{j=await fetch(`${snB()}/api/pc/snap/info?sid=${sid}`,{cache:"no-store"}).then(r=>r.json());}catch(e){}
  if(!j||!j.ok||SN.sid!==sid)return;const L=j.snaps||[];if(JSON.stringify(L.map(x=>x[1]))!==JSON.stringify(SN.L.map(x=>x[1]))){SN.L=L.slice();SN.lay=j.layout||SN.lay;SN.view=0;if(L.length)snBuild();}}   /* TK_V0.9.92 截圖資料夾剛被搬走／換掉：自己再讀一次 */
function snBuild(){const w=SN.box&&SN.box.querySelector(".snv");if(!w)return;const pg=w.querySelector(".snPg"),L=SN.L,lab=x=>{const pm=/_p(\d+)\.jpg$/.exec(x[1]||"");return `${SN.clk?SN.clk(x[0]):snHms(x[0])}${pm?" · "+pm[1]+"%":""}`;};
  pg.innerHTML=`<div class="snSl snAll${SN.strip?" strip":""}"><div class="snGrid${SN.strip?" strip":""}">${L.map((x,i)=>`<div class="snG" data-gi="${i}"><img alt="" loading="lazy" src="${snUrlS(i)}" onerror="snImgErr(this)"></div>`).join("")}${SN.lab==="x"?"":L.map((x,i)=>`<b class="snLb${SN.lab==="t"?" tm":""}" data-li="${i}">${SN.lab==="t"?(SN.clk?SN.clk(x[0]):snHms(x[0])):i+1}</b>`).join("")}</div></div>`
    +(SN.strip?"":L.map((x,i)=>`<div class="snSl"><div class="snCrop"><img alt="" draggable="false" data-src="${snUrl(i)}"></div><div class="snSB"><span>📷 ${lab(x)} · ${i+1} / ${L.length}</span><a class="snDl" href="${snUrl(i)}" download="${(x[1]||"snap.jpg").split("/").pop()}" title="下載這一張">⬇ 下載</a><button class="snDl bad" data-sd="1" title="刪除這一張（不用確認）">🗑</button></div></div>`).join(""))   /* V0.7.11 展開時：只留往右排開的那一排 */;
  const n=w.querySelector(".snNP");if(n)n.textContent=L.length;snLabel();snGo(Math.min(SN.view,L.length),false,true);snFit();snFyApply();}
function snLoadNear(){const w=SN.box&&SN.box.querySelector(".snv");if(!w)return;const sl=w.querySelectorAll(".snPg .snSl");for(let k=SN.view-1;k<=SN.view+1;k++){const im=sl[k]&&sl[k].querySelector("img[data-src]");if(im&&!im.src)im.src=im.dataset.src;}}
function snLabel(){const w=SN.box&&SN.box.querySelector(".snv");if(!w)return;const l=w.querySelector(".snl"),vid=!w.querySelector(".snVid").hidden;
  l.hidden=true;const tl=w.querySelector(".snTool");if(tl)tl.hidden=vid||SN.view>0;const hm=w.querySelector(".snHome");if(hm)hm.hidden=vid||SN.view<=0;w.querySelector(".snp").hidden=vid||SN.view<=0;w.querySelector(".snn").hidden=vid||SN.strip||SN.view>=SN.L.length;}
function snGo(v,seek,inst){const w=SN.box&&SN.box.querySelector(".snv");if(!w)return;v=Math.max(0,Math.min(SN.L.length,v));const pg=w.querySelector(".snPg");SN.view=v;
  pg.scrollTo({left:v*pg.clientWidth,behavior:inst?"auto":"smooth"});snLoadNear();snLabel();if(seek&&v>0&&SN.seek){const x=SN.L[v-1];SN.lock=Date.now();SN.seek(Math.max(0,x[0]));}if(v>0)SN.cur=v-1;}
function snMode(m,auto){const w=SN.box&&SN.box.querySelector(".snv");if(!w)return;const v=m==="v";w.querySelectorAll(".snTabs [data-sm]").forEach(b=>b.classList.toggle("on",b.dataset.sm===m));
  w.querySelector(".snPg").hidden=v;w.querySelector(".snVid").hidden=!v;w.classList.toggle("vid",v);if(!auto)try{localStorage.setItem("tlm_snmode",m);}catch(e){}
  if(!v){w.querySelectorAll(".snVid video").forEach(x=>{try{x.pause();}catch(e){}});snGo(SN.view,false,true);}snLabel();}
function snPaint(t){SN.t=+t||0;if(!SN.L.length||!SN.box)return;SN.cur=snIdx(SN.t);}   /* V0.7.08 看照片不受時間軸影響（不會自己換張） */
function snStep(d){if(!SN.L.length)return;snGo(SN.view+d,true);}
/* V0.6.93 刪掉目前看的這一張（不用確認），接著顯示下一張 */
async function snDel(){const i=SN.view-1;if(i<0||!SN.L[i])return;const x=SN.L[i],sid=SN.sid;
  const P=typeof kPost==="function"?kPost:(typeof post==="function"?post:(typeof deepPost==="function"?deepPost:null));if(!P)return;
  const j=await P("/api/pc/snap/del",{sid,name:x[1]});const T=m=>(typeof toast==="function"?toast(m):0);
  if(!j||j.ok===false){T("✖ "+((j&&j.message)||"沒有刪掉"));return;}if(SN.sid!==sid)return;
  const k=SN.L.indexOf(x);if(k>=0)SN.L.splice(k,1);const w=SN.box&&SN.box.querySelector(".snv");
  if(!SN.L.length){if(w)w.remove();T("已刪除，這場沒有截圖了");return;}
  SN.view=Math.min(k+1,SN.L.length);SN.cur=-1;snBuild();T(`已刪除（剩 ${SN.L.length} 張）`);}
function snStop(){SN.L=[];SN.box=null;SN.cur=-1;SN.t=0;SN.view=0;}
/* TK_V0.9.64 🎞 動態拼貼：照現在全覽的排版（欄列、比例、間距、▲▼、誰疊誰），每一格播那一刻往後 N 秒，同時播放；背景做成 MP4／GIF */
function snMosParams(){const N=SN.L.length,C=SN.strip?N:Math.max(1,snLayEff()[1]),R=Math.ceil(N/C),ratio=(SN.th||100)/(SN.cw||56),gap=(+SN.gap||0)/(SN.cw||56);
  const ord=SN.L.map((x,i)=>({i,c:i%C,r:Math.floor(i/C)})).sort((a,b)=>snZ(a.c,a.r)-snZ(b.c,b.r)).map(o=>o.i);return {N,C,R,ratio,gap,ord};}
function snMosSize(P,long){const gw=P.C+(P.C-1)*P.gap,gh=P.R*P.ratio+(P.R-1)*P.gap,k=long/Math.max(gw,gh),cw=Math.max(16,Math.round(k/2)*2),ch=Math.max(16,Math.round(k*P.ratio/2)*2),gp=Math.round(P.gap*k);
  return [Math.floor((P.C*cw+(P.C-1)*gp)/2)*2,Math.floor((P.R*ch+(P.R-1)*gp)/2)*2,cw,ch];}
function gifCap(){try{return localStorage.getItem("tlm_gifcap")==="1";}catch(e){return false;}}   /* TK_V1.0.75 LINE 上限 */
function gifCapSet(v){try{localStorage.setItem("tlm_gifcap",v?"1":"0");}catch(e){}}
function snMosOpen(){if(!SN.L.length)return;const P=snMosParams();let ov=document.getElementById("snMos");if(ov)ov.remove();ov=document.createElement("div");ov.id="snMos";ov.className="snMos";
  let sv={};try{sv=JSON.parse(localStorage.getItem("tlm_mos")||"{}")||{};}catch(e){}const st={dur:sv.dur||5,f:new Set(sv.f||["mp4"]),long:sv.long||1280,spd:sv.spd||1};
  const save=()=>{try{localStorage.setItem("tlm_mos",JSON.stringify({dur:st.dur,f:[...st.f],long:st.long,spd:st.spd}));}catch(e){}};
  const draw=()=>{const [W,H,cw,ch]=snMosSize(P,st.long);ov.querySelector(".snMosInfo").innerHTML=`${P.C} 欄 × ${P.R} 列、${P.N} 格 → 輸出 <b>${W}×${H}</b>（每格 ${cw}×${ch}）· 每格播 <b>${st.dur} 秒</b>${st.spd>1?`（×${st.spd} 加速＝每格 ${st.dur*st.spd} 秒的實際畫面）`:""} · ${[...st.f].map(x=>x.toUpperCase()).join("＋")||"（至少選一種格式）"}${st.f.has("gif")&&st.long>1280?"<br>⚠ GIF 檔會很大，建議長邊 960 以下":""}<br><small>同一個排版做過「一樣大或更大」的，會直接縮，不用重抓；要更大才重抓每一格。</small>`;
    ov.querySelectorAll("[data-md]").forEach(b=>b.classList.toggle("on",+b.dataset.md===st.dur));ov.querySelectorAll("[data-mf]").forEach(b=>b.classList.toggle("on",st.f.has(b.dataset.mf)));
    ov.querySelectorAll("[data-ml]").forEach(b=>b.classList.toggle("on",+b.dataset.ml===st.long));{const cb=ov.querySelector("[data-mcap]");if(cb){cb.classList.toggle("on",gifCap());cb.textContent=(gifCap()?"☑":"☐")+" LINE 用（GIF ≤ 19.9 MB）";}}ov.querySelectorAll("[data-ms]").forEach(b=>b.classList.toggle("on",+b.dataset.ms===st.spd));save();};
  ov.innerHTML=`<div class="snMosB"><div class="snMosH"><b>🎞 輸出動圖</b><span style="flex:1"></span><button class="pill snGaB" data-mga="1">🎁 禮物陣列</button><button class="pill" data-mx="1">✕</button></div>
<div class="snMosN">照現在全覽的排版（欄列、比例、間距、▲▼ 位置、誰疊誰）做；每一格從那張照片的時間開始播，全部一起播。很吃電腦，所以在背景一件一件做（電腦忙會先等），做好在下面預覽、下載，也存到剪輯資料夾的「動態拼貼」。</div>
<div class="snMosR"><span>每格幾秒</span>${[3,5,8,10].map(d=>`<button data-md="${d}">${d} 秒</button>`).join("")}</div>
<div class="snMosR"><span>加速</span>${[1,2,4,8].map(v=>`<button data-ms="${v}">${v===1?"原速":"×"+v}</button>`).join("")}</div>
<div class="snMosR"><span>格式（可複選）</span><button data-mf="mp4">MP4</button><button data-mf="gif">GIF</button><button data-mcap="1" title="打勾：GIF 超過 19.9 MB 會自動降每秒張數和尺寸（顏色不減、紅色保住），直到放得下（LINE 上限 20 MB）">☐ LINE 用（GIF ≤ 19.9 MB）</button></div>
<div class="snMosR"><span>長邊</span>${[720,960,1280,1920,2560].map(v=>`<button data-ml="${v}">${v}</button>`).join("")}</div>
<div class="snMosInfo"></div><div class="snMosR"><button class="snMosGo" data-mgo="1">▶ 開始輸出</button></div><div class="snMosL"></div></div>`;
  document.body.appendChild(ov);draw();
  ov.onclick=async e=>{const t=e.target;if(t===ov||t.closest("[data-mx]")){clearTimeout(ov._pt);ov.remove();return;}
    const pv=t.closest("[data-mpv]");if(pv){snMosPv(pv.dataset.mpv);return;}
    if(t.closest("[data-mga]")){clearTimeout(ov._pt);ov.remove();gaOpen(SN.sid);return;}
    const d=t.closest("[data-md]");if(d){st.dur=+d.dataset.md;draw();return;}const sp=t.closest("[data-ms]");if(sp){st.spd=+sp.dataset.ms;draw();return;}
    const f=t.closest("[data-mf]");if(f){const k=f.dataset.mf;if(st.f.has(k)){if(st.f.size>1)st.f.delete(k);}else st.f.add(k);draw();return;}const l=t.closest("[data-ml]");if(l){st.long=+l.dataset.ml;draw();return;}if(t.closest("[data-mcap]")){gifCapSet(!gifCap());draw();return;}
    if(t.closest("[data-mgo]")){const P2=snMosParams(),body={sid:SN.sid,C:P2.C,R:P2.R,ts:SN.L.map(x=>x[0]),dur:st.dur,spd:st.spd,fmts:[...st.f],long:st.long,ratio:P2.ratio,gap:P2.gap,fy:SN.fy||0,ord:P2.ord,cap:gifCap()?1:0};
      const P_=typeof kPost==="function"?kPost:(typeof post==="function"?post:null);let j=null;try{j=P_?await P_("/api/pc/mosaic",body):null;}catch(x){}(typeof toast==="function"?toast:alert)((j&&j.ok?"✔ ":"✖ ")+((j&&j.message)||"沒有送出"));snMosPoll(ov);}};
  snMosPoll(ov);}
function snMosUrl(f){return `${typeof B==="string"?B:""}/api/pc/mosaic/file?f=${encodeURIComponent(f)}`;}
function snMosPv(f){const d=document.createElement("div");d.className="snMosPv";const gif=/\.gif$/i.test(f);
  d.innerHTML=`<div class="snMosPvB">${gif?`<img alt="" src="${snMosUrl(f)}&pv=1">`:`<video src="${snMosUrl(f)}&pv=1" autoplay loop muted playsinline controls></video>`}<div class="snMosPvT"><span>${f}</span><button class="pill">✕ 關閉</button></div></div>`;
  document.body.appendChild(d);const cl=()=>{const v=d.querySelector("video");if(v){try{v.pause();v.removeAttribute("src");v.load();}catch(e){}}d.remove();};d.querySelector("button").onclick=cl;d.onclick=e=>{if(e.target===d)cl();};}
function snMosFile(x){return `<div class="snMosF"><span>${String(x.fmt||"").toUpperCase()} · ${x.w}×${x.h} · ${(x.size/1e6).toFixed(1)} MB</span><button class="pill" data-mpv="${x.file}">▶ 預覽</button><a class="pill" href="${snMosUrl(x.file)}" download="${x.file}">⬇ 下載</a></div>`;}
async function snMosPoll(ov){clearTimeout(ov._pt);if(!ov.isConnected)return;let j=null;try{j=await fetch((typeof B==="string"?B:"")+"/api/pc/mosaic?sid="+SN.sid,{cache:"no-store"}).then(r=>r.json());}catch(e){}
  const el=ov.querySelector(".snMosL");if(!el)return;const L=(j&&j.jobs)||[],O=(j&&j.old)||[];
  el.innerHTML=(L.length?L.map(x=>`<div class="snMosJ ${x.state}"><b>${x.state==="done"?"✔":x.state==="fail"?"✖":"⏳"} ${x.C}×${x.R} · ${x.dur} 秒${x.spd>1?` ×${x.spd}`:""} · ${(x.fmts||[]).map(f=>f.toUpperCase()).join("＋")} · ${x.w}×${x.h}</b><small>${x.msg||""}${x.state==="run"&&x.total>1?`（${x.done}/${x.total}）`:""}</small>${(x.files||[]).map(snMosFile).join("")}</div>`).join(""):"")
    +(O.length?`<div class="snMosN">這場以前做的：</div>`+O.map(x=>`<div class="snMosJ done"><b>${x.C}×${x.R} · ${x.dur} 秒${x.spd>1?` ×${x.spd}`:""}</b>${snMosFile(x)}</div>`).join(""):"")||'<div class="snMosN">這場還沒做過動圖</div>';
  if(L.some(x=>x.state==="run"||x.state==="wait"))ov._pt=setTimeout(()=>snMosPoll(ov),2500);}
/* TK_V0.9.69 🎁 禮物陣列：這場標成互動禮物的每一次，一格一格；每格對齊「爆點」（動畫最精彩那一下），取爆點前 X 秒～後 Y 秒，同時播放輸出（用動態拼貼的引擎） */
const GA={sid:0,d:null,cur:0,C:0,st:null};
function gaB(){return typeof B==="string"?B:"";}
function gaE(s){return String(s==null?"":s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));}
function gaT(s){s=Math.max(0,+s||0);const h=Math.floor(s/3600),m=Math.floor(s%3600/60),x=(s%60).toFixed(1).padStart(4,"0");return (h?h+":"+String(m).padStart(2,"0"):m)+":"+x;}
function gaMap(L){const R=GA.d.rng||[];const r=R.find(x=>L>=x[0]-1&&L<=x[1]+1)||null;return r&&r[2]>=0?{k:r[2],pos:Math.max(0,L-r[0]+r[3]),r}:null;}
/* TK_V0.9.70 預設不放的禮物種類（例如 Heart Me）：記在這台；那幾格放到「湊數用」，要用再一格一格勾 */
function gaOffSet(){try{const v=JSON.parse(localStorage.getItem("tlm_ga_off")||"null");if(Array.isArray(v))return new Set(v);}catch(e){}return new Set(["heart me"]);}
function gaOffSave(S){try{localStorage.setItem("tlm_ga_off",JSON.stringify([...S]));}catch(e){}}
function gaUse(it){const u=(GA.d.use||{})[it.id];return u!=null?!!u:!gaOffSet().has(String(it.g).toLowerCase());}
function gaUsed(){const I=GA.d.items||[],off=gaOffSet(),main=I.filter(it=>gaUse(it)&&!off.has(String(it.g).toLowerCase())),fill=I.filter(it=>gaUse(it)&&off.has(String(it.g).toLowerCase()));return main.concat(fill);}   /* 湊數用的排在最後 */
function gaHit(it){return it.hit!=null?it.hit:(GA.d.off!=null?it.L0+GA.d.off:it.L0);}
async function gaPost(body){const P_=typeof kPost==="function"?kPost:(typeof post==="function"?post:null);try{return P_?await P_("/api/pc/garr",body):null;}catch(e){return null;}}
async function gaOpen(sid){GA.sid=sid;let ov=document.getElementById("gaOv");if(ov)ov.remove();ov=document.createElement("div");ov.id="gaOv";ov.className="snMos gaOv";
  ov.innerHTML=`<div class="snMosB gaB"><div class="snMosH"><b>🎁 禮物陣列</b><span style="flex:1"></span><button class="pill" data-gx="1">✕</button></div><div class="snMosN">讀取這場的互動禮物…</div></div>`;document.body.appendChild(ov);
  let d=null;try{d=await fetch(gaB()+"/api/pc/garr?sid="+sid,{cache:"no-store"}).then(r=>r.json());}catch(e){}
  if(!ov.isConnected)return;if(!d||!d.ok){ov.querySelector(".snMosN").textContent="讀取失敗";return;}GA.d=d;GA.cur=0;
  ov.onclick=gaClick;gaDraw();}
function gaLayouts(N){const o=[];for(let C=2;C<=10;C++){const R=Math.ceil(N/C);if(R<1)continue;o.push({C,R,fill:C*R-N});}return o.sort((a,b)=>a.fill-b.fill||Math.abs(a.C-a.R*0.6)-Math.abs(b.C-b.R*0.6)).slice(0,6);}
function gaLay(){let v={};try{v=JSON.parse(localStorage.getItem("tlm_ga_lay")||"null")||{};}catch(e){}   /* TK_V0.9.71 排版：間距（負＝交疊）、誰疊誰、▲▼，預設照截圖全覽的設定 */
  const cw=SN.cw||56;return {gap:v.gap!=null?v.gap:(+SN.gap||0)/cw,zh:v.zh||SN.zh||"r",zv:v.zv||SN.zv||"d",fy:v.fy!=null?v.fy:(SN.fy||0),ratio:v.ratio||16/9};}   /* TK_V0.9.72 格子形狀：預設直式 9:16，可以拉 */
function gaRt(r){return r>=1?`寬 1：高 ${r.toFixed(2)}`:`寬 ${(1/r).toFixed(2)}：高 1`;}
function gaLaySet(o){const L=Object.assign(gaLay(),o);try{localStorage.setItem("tlm_ga_lay",JSON.stringify({gap:L.gap,zh:L.zh,zv:L.zv,fy:L.fy,ratio:L.ratio}));}catch(e){}return L;}
function gaZ(c,r,L){return 1+(L.zv==="d"?r:500-r)*200+(L.zh==="r"?c:199-c);}
function gaDraw(){const ov=document.getElementById("gaOv"),d=GA.d;if(!ov||!d)return;const I=d.items||[],N=I.length;
  let sv={};try{sv=JSON.parse(localStorage.getItem("tlm_mos")||"{}")||{};}catch(e){}GA.st=GA.st||{f:new Set(sv.f||["mp4"]),long:sv.long||1280,spd:1};
  const U=gaUsed(),NU=U.length,OFF=gaOffSet();
  if(!N){ov.querySelector(".gaB").innerHTML=`<div class="snMosH"><b>🎁 禮物陣列</b><span style="flex:1"></span><button class="pill" data-gx="1">✕</button></div><div class="snMosN">這場沒有標成「互動禮物」的禮物。<br>到「批量剪輯」點禮物左上角 🎬 看畫面、標記互動禮物後再來。</div>`;return;}
  if(!ov.querySelector(".gaPl")){   /* 播放器只建一次（之後只換下面），兩個 video：一個在播、一個先把下一格讀好 */
    ov.querySelector(".gaB").innerHTML=`<div class="snMosH"><b class="gaTi"></b><span style="flex:1"></span><button class="pill" data-gx="1">✕</button></div>
<div class="gaPl"><div class="vgPvS gaV"><video class="gaVa act" playsinline controls preload="auto"></video><video class="gaVa" playsinline preload="auto" muted></video>${typeof LVS_SWH!=="undefined"?LVS_SWH:""}</div>
<div class="gaPI" id="gaPI"></div>
<div class="snMosR gaCtl"><button data-gj="-1">−1 秒</button><button data-gj="-0.2">−0.2</button><button data-gp="1">▶／⏸</button><button data-gj="0.2">+0.2</button><button data-gj="1">+1 秒</button><button class="gaSet" data-gset="1">📍 設為爆點</button><button data-gnx="1">下一個 ▶</button></div></div><div class="gaBody"></div>`;
    const VP=new Proxy({},{get:(o,k)=>{const v=gaVid();const x=v[k];return typeof x==="function"?x.bind(v):x;},set:(o,k,val)=>{gaVid()[k]=val;return true;}});
    if(typeof lvsSwipe==="function")lvsSwipe(ov.querySelector(".gaPl"),VP,null);ov.querySelectorAll(".gaVa").forEach(v=>v.addEventListener("timeupdate",()=>{if(v===gaVid())gaInfo();}));
    GA.needLoad=true;}
  ov.querySelector(".gaTi").textContent=`🎁 禮物陣列 · ${d.name} · ${N} 個`;
  const L=gaLayouts(Math.max(1,NU));if(!GA.C||!L.some(x=>x.C===GA.C))GA.C=L[0].C;const al=I.filter(x=>x.hit!=null&&gaUse(x)).length;
  const types={};I.forEach(it=>{const k=String(it.g).toLowerCase();(types[k]=types[k]||{g:it.g,zh:it.zh,n:0}).n++;});
  const card=(it)=>{const i=I.indexOf(it),use=gaUse(it);return `<div class="gaC${i===GA.cur?" on":""}${it.hit!=null?" ok":""}${use?"":" off"}" data-gi="${i}"><span class="gaU${use?" y":""}" data-gu="${i}" title="${use?"放進陣列（點一下拿掉）":"沒放進陣列（點一下加進去，排在最後湊數）"}">${use?"✓":"＋"}</span>${typeof kGIcon==="function"?kGIcon(it.g):"🎁"}<b>${gaE(it.zh||it.g)}</b><small>${gaE(it.user)}${it.cnt>1?" ×"+it.cnt:""}</small><small>${gaT(gaHit(it))}${it.hit!=null?" ✔":d.off!=null?" ≈":" ?"}</small></div>`;};
  const mainI=I.filter(it=>!OFF.has(String(it.g).toLowerCase())),fillI=I.filter(it=>OFF.has(String(it.g).toLowerCase()));
  const body=ov.querySelector(".gaBody"),sy=body.parentElement.scrollTop;
  body.innerHTML=`<div class="snMosR"><span>每格</span>爆點前 <input class="gaIn" id="gaPre" type="number" step="0.5" min="0" max="8" value="${d.pre}"> 秒，後 <input class="gaIn" id="gaPost" type="number" step="0.5" min="0.5" max="12" value="${d.post}"> 秒</div>
<div class="snMosR gaTy"><span>禮物種類</span>${Object.entries(types).map(([k,t])=>`<button data-gty="${gaE(k)}" class="${OFF.has(k)?"off":"on"}" title="${OFF.has(k)?"預設不放（點一下改成預設要放）":"預設要放（點一下改成預設不放、只拿來湊數）"}">${gaE(t.zh||t.g)} ${t.n}</button>`).join("")}</div>
<div class="snMosR"><span>對齊</span><b class="gaAl">陣列 ${NU} 格 · ${al} 個已手動對齊</b>${al?`<button data-gavg="1">套用平均延遲到沒對齊的${d.off!=null?`（現在 ${d.off>=0?"+":""}${d.off.toFixed(1)} 秒）`:""}</button>`:`<small>先對齊兩三個，就能把平均延遲套到其他格</small>`}</div>
<div class="gaGrid">${mainI.map(card).join("")}</div>${fillI.length?`<div class="snMosN gaFillH">🧩 湊數用（${fillI.length} 個，預設不放；點右上角 ＋ 挑幾個放進去，會排在最後）</div><div class="gaGrid">${fillI.map(card).join("")}</div>`:""}
<div class="snMosR"><span>加速</span>${[1,2,4].map(v=>`<button data-gs="${v}" class="${GA.st.spd===v?"on":""}">${v===1?"原速":"×"+v}</button>`).join("")}<span style="min-width:0;margin-left:8px">格式</span><button data-gf="mp4" class="${GA.st.f.has("mp4")?"on":""}">MP4</button><button data-gf="gif" class="${GA.st.f.has("gif")?"on":""}">GIF</button><button data-gau="1" class="${GA.st.aud!==false?"on":""}" title="每格的聲音全部疊在一起（GIF 沒有聲音）">${GA.st.aud!==false?"🔊 有聲音":"🔇 無聲"}</button><button data-gcap="1" class="${gifCap()?"on":""}" title="GIF 超過 19.9 MB 自動縮（LINE 上限 20 MB）">${gifCap()?"☑":"☐"} LINE 用 ≤19.9MB</button></div>
<div class="snMosR"><span>長邊</span>${[720,960,1280,1920].map(v=>`<button data-gl="${v}" class="${GA.st.long===v?"on":""}">${v}</button>`).join("")}</div>
<div class="snMosN">先按「👁 預覽排版」：每格用爆點那一張圖排出來，可以比較 3×6、6×3、交疊方式；確定後再輸出影片（回原影片用原畫質重抓）。空的格子先放黑畫面。</div>
<div class="snMosR"><button data-gpv="1">👁 預覽排版</button><button class="snMosGo" data-ggo="1">▶ 輸出禮物陣列</button></div>`;
  body.parentElement.scrollTop=sy;
  ov.querySelector("#gaPre").onchange=e=>{d.pre=Math.max(0,Math.min(8,+e.target.value||0));gaPost({sid:GA.sid,pre:d.pre});};ov.querySelector("#gaPost").onchange=e=>{d.post=Math.max(0.5,Math.min(12,+e.target.value||4));gaPost({sid:GA.sid,post:d.post});};
  if(GA.needLoad){GA.needLoad=false;gaLoad();}}
function gaVid(){const ov=document.getElementById("gaOv");return ov&&ov.querySelector(".gaVa.act");}
function gaNext(i){const I=GA.d.items;for(let j=i+1;j<I.length;j++)if(gaUse(I[j]))return j;return Math.min(I.length-1,i+1);}   /* 下一個要放進陣列的 */
function gaTarget(i){const it=GA.d.items[i];if(!it)return null;const m=gaMap(gaHit(it)-1.5);if(!m)return null;return {m,src:`${gaB()}/api/pc/vb/file?sid=${GA.sid}&k=${m.k}`};}
function gaLoad(){const ov=document.getElementById("gaOv");if(!ov)return;const it=GA.d.items[GA.cur],T=gaTarget(GA.cur);if(!it)return;
  if(!T){ov.querySelector("#gaPI").textContent="這一格找不到影片（MP4 刪了？）";return;}GA.m=T.m;
  const V=[...ov.querySelectorAll(".gaVa")],a=V.find(v=>v.classList.contains("act")),o=V.find(v=>v!==a);
  let v=a;if(o&&o.dataset.src===T.src&&Math.abs(+o.dataset.pos-T.m.pos)<0.6&&o.readyState>=2){v=o;a.classList.remove("act");a.pause();a.muted=true;a.controls=false;o.classList.add("act");o.controls=true;}   /* 下一格已經讀好：直接換上 */
  v.muted=false;v.controls=true;
  if(v.dataset.src!==T.src){v.dataset.src=T.src;v.src=T.src;v.addEventListener("loadedmetadata",()=>{try{v.currentTime=T.m.pos;}catch(e){}v.play().catch(()=>{});},{once:true});}
  else{if(Math.abs(v.currentTime-T.m.pos)>0.3){try{v.currentTime=T.m.pos;}catch(e){}}v.play().catch(()=>{});}
  v.dataset.pos=T.m.pos;
  ov.querySelectorAll(".gaC").forEach(b=>b.classList.toggle("on",+b.dataset.gi===GA.cur));const b=ov.querySelector(`.gaC[data-gi="${GA.cur}"]`);if(b)b.scrollIntoView({block:"nearest"});gaInfo();
  const nx=gaNext(GA.cur),N=nx!==GA.cur?gaTarget(nx):null,ob=V.find(x=>x!==v);   /* 下一格先讀：另一個 video 先跳到那裡（靜音、不播） */
  if(N&&ob){ob.muted=true;ob.pause();const go=()=>{try{ob.currentTime=N.m.pos;}catch(e){}ob.dataset.pos=N.m.pos;};if(ob.dataset.src!==N.src){ob.dataset.src=N.src;ob.src=N.src;ob.addEventListener("loadedmetadata",go,{once:true});}else go();}}
function gaNowL(){const v=gaVid();if(!v||!GA.m)return null;const r=GA.m.r;return v.currentTime-r[3]+r[0];}
function gaInfo(){const ov=document.getElementById("gaOv");if(!ov)return;const it=GA.d.items[GA.cur],el=ov.querySelector("#gaPI");if(!it||!el)return;const L=gaNowL();
  el.innerHTML=`第 ${GA.cur+1}/${GA.d.items.length} 格 · <b>${gaE(it.zh||it.g)}</b> · ${gaE(it.user)} · 送出 ${gaT(it.L0)} · 爆點 ${gaT(gaHit(it))}${it.hit!=null?" ✔":""}${L!=null?` · 現在 <b>${gaT(L)}</b>（${L-it.L0>=0?"+":""}${(L-it.L0).toFixed(1)} 秒）`:""}`;}
async function gaClick(e){const t=e.target,ov=document.getElementById("gaOv"),d=GA.d;if(!ov)return;
  if(t===ov||t.closest("[data-gx]")){ov.querySelectorAll("video").forEach(v=>{try{v.pause();v.removeAttribute("src");v.load();}catch(x){}});ov.remove();return;}
  const v=gaVid();
  if(t.closest("[data-gpv]")){gaPv();return;}
  const gu=t.closest("[data-gu]");if(gu){const it=d.items[+gu.dataset.gu];if(!it)return;const nv=!gaUse(it),def=!gaOffSet().has(String(it.g).toLowerCase());d.use=d.use||{};const U={};
    if(nv===def){delete d.use[it.id];U[it.id]=null;}else{d.use[it.id]=nv;U[it.id]=nv;}gaPost({sid:GA.sid,use:U});gaDraw();return;}
  const gty=t.closest("[data-gty]");if(gty){const S=gaOffSet(),k=gty.dataset.gty;S.has(k)?S.delete(k):S.add(k);gaOffSave(S);gaDraw();return;}
  const gi=t.closest("[data-gi]");if(gi){GA.cur=+gi.dataset.gi;gaLoad();return;}
  const gj=t.closest("[data-gj]");if(gj&&v){try{v.pause();v.currentTime=Math.max(0,v.currentTime+(+gj.dataset.gj));}catch(x){}return;}
  if(t.closest("[data-gp]")&&v){v.paused?v.play().catch(()=>{}):v.pause();return;}
  if(t.closest("[data-gnx]")){GA.cur=gaNext(GA.cur);gaLoad();return;}
  if(t.closest("[data-gset]")){const L=gaNowL(),it=d.items[GA.cur];if(L==null||!it)return;it.hit=+L.toFixed(2);const H={};H[it.id]=it.hit;const j=await gaPost({sid:GA.sid,hit:H});
    if(!j||j.ok===false){ov.querySelector("#gaPI").innerHTML='<b style="color:#ff4d6d">✖ 沒存到（可能要網頁密碼）</b>';return;}GA.cur=gaNext(GA.cur);gaDraw();gaLoad();return;}
  if(t.closest("[data-gavg]")){const A=d.items.filter(x=>x.hit!=null).map(x=>x.hit-x.L0).sort((a,b)=>a-b);if(!A.length)return;const med=A[Math.floor(A.length/2)];d.off=+med.toFixed(2);await gaPost({sid:GA.sid,off:d.off});gaDraw();return;}
  const gs=t.closest("[data-gs]");if(gs){GA.st.spd=+gs.dataset.gs;gaDraw();return;}
  if(t.closest("[data-gau]")){GA.st.aud=GA.st.aud===false;gaDraw();return;}if(t.closest("[data-gcap]")){gifCapSet(!gifCap());gaDraw();return;}
  const gf=t.closest("[data-gf]");if(gf){const k=gf.dataset.gf;if(GA.st.f.has(k)){if(GA.st.f.size>1)GA.st.f.delete(k);}else GA.st.f.add(k);gaDraw();return;}
  const gl=t.closest("[data-gl]");if(gl){GA.st.long=+gl.dataset.gl;gaDraw();return;}
  if(t.closest("[data-ggo]")){const I=gaUsed();if(!I.length){ov.querySelector("#gaPI").innerHTML="<b>沒有要放的格子</b>";return;}const C=GA.C,R=Math.ceil(I.length/C),dur=Math.max(1,Math.min(15,(+d.pre||0)+(+d.post||4)));
    const body={sid:GA.sid,C,R,ts:I.map(it=>+(gaHit(it)-(+d.pre||0)).toFixed(1)),dur,spd:GA.st.spd,aud:GA.st.aud!==false?1:0,fmts:[...GA.st.f],cap:gifCap()?1:0,long:GA.st.long,ratio:gaLay().ratio,gap:gaLay().gap,fy:gaLay().fy,ord:I.map((x,i)=>({i,z:gaZ(i%C,Math.floor(i/C),gaLay())})).sort((a,b)=>a.z-b.z).map(o=>o.i)};   /* TK_V0.9.71 跟預覽一樣的交疊 */
    const P_=typeof kPost==="function"?kPost:(typeof post==="function"?post:null);let j=null;try{j=P_?await P_("/api/pc/mosaic",body):null;}catch(x){}
    const msg=(j&&j.ok?"✔ ":"✖ ")+((j&&j.message)||"沒有送出");ov.querySelector("#gaPI").innerHTML=`<b>${gaE(msg)}</b>`;
    if(j&&j.ok){setTimeout(()=>{ov.querySelectorAll("video").forEach(vv=>{try{vv.pause();vv.removeAttribute("src");vv.load();}catch(x){}});ov.remove();const pv=document.getElementById("gaPvOv");if(pv)pv.remove();snMosOpen();},1500);}return;}}
/* TK_V0.9.71 👁 預覽排版：每格用爆點那一張圖（電腦先做好縮圖），照設定的間距／交疊／▲▼ 排出來，可以切換欄列比較；確定後直接輸出 */
function gaPv(){const I=gaUsed();if(!I.length)return;let pv=document.getElementById("gaPvOv");if(pv)pv.remove();pv=document.createElement("div");pv.id="gaPvOv";pv.className="gaPvOv";document.body.appendChild(pv);
  const draw=()=>{const L=gaLay(),N=I.length,LY=gaLayouts(N);if(!LY.some(x=>x.C===GA.C))GA.C=LY[0].C;const C=GA.C,R=Math.ceil(N/C);
    const W=Math.min(innerWidth-44,900),cw=W/(C+(C-1)*L.gap),ch=cw*L.ratio,gp=L.gap*cw,TW=C*cw+(C-1)*gp,TH=R*ch+(R-1)*gp;
    pv.innerHTML=`<div class="gaPvB"><div class="gaPvH"><b>👁 ${C}×${R}</b><span style="flex:1"></span><button class="gaPvGo" data-pgo="1">▶ 就這樣輸出</button><button class="pill" data-px="1">✕</button></div>
<div class="gaPvC" style="width:${TW}px;height:${TH}px">${I.map((it,i)=>{const c=i%C,r=Math.floor(i/C);return `<div class="gaPvT" style="left:${c*(cw+gp)}px;top:${r*(ch+gp)}px;width:${cw}px;height:${ch}px;z-index:${gaZ(c,r,L)}"><img loading="lazy" alt="" style="object-position:50% ${50-L.fy}%" src="${imgB(gaB())}/api/pc/vg/thumb?sid=${GA.sid}&t=${gaHit(it).toFixed(1)}&h=360&p=1"></div>`;}).join("")}</div><div class="gaPvDr" data-pdrag="1">⇕ 按住上下拉調高矮（${gaRt(L.ratio)}）</div>
<div class="gaPvK"><div class="snMosR"><span>排版</span>${LY.map(x=>`<button data-pc="${x.C}" class="${x.C===C?"on":""}">${x.C}×${x.R}${x.fill?`（空 ${x.fill}）`:""}</button>`).join("")}</div>
<div class="snMosR"><span>形狀</span>${[[16/9,"直 9:16"],[4/3,"3:4"],[1,"1:1"],[3/4,"4:3"],[9/16,"橫 16:9"]].map(([v,t])=>`<button data-prt="${v}" class="${Math.abs(L.ratio-v)<0.02?"on":""}">${t}</button>`).join("")}</div>
<div class="snMosR"><span>間距</span><input type="range" min="-40" max="20" step="1" value="${Math.round(L.gap*100)}" data-pg="1"><b>${Math.round(L.gap*100)}%</b><small>負的＝交疊</small></div>
<div class="snMosR"><span>交疊</span><button data-pz="zh" class="on">${L.zh==="r"?"右疊左":"左疊右"}</button><button data-pz="zv" class="on">${L.zv==="d"?"下疊上":"上疊下"}</button></div><div class="snMosR"><span>構圖</span><button data-pf="1" title="全部一起往上 1">▲</button><button data-pf="0.1" title="微調 0.1">˄</button><b class="gaPvFy">${L.fy>0?"+":""}${L.fy}</b><button data-pf="-0.1" title="微調 0.1">˅</button><button data-pf="-1" title="全部一起往下 1">▼</button><button data-pf="0">置中</button><small>或在圖上按住上下拖</small></div>
</div></div>`;
    /* TK_V0.9.74 整個預覽縮到一個畫面內（下面的按鈕永遠按得到）：量出其他東西的高度，剩下的給格子 */
    const Bx=pv.querySelector(".gaPvB"),G=pv.querySelector(".gaPvC"),other=Bx.scrollHeight-G.offsetHeight,avail=Math.max(120,innerHeight*0.96-other-6);
    if(TH>avail){const k=avail/TH,cw2=cw*k,ch2=ch*k,gp2=gp*k;G.style.width=(C*cw2+(C-1)*gp2)+"px";G.style.height=(R*ch2+(R-1)*gp2)+"px";
      G.querySelectorAll(".gaPvT").forEach((t,i)=>{const c=i%C,r=Math.floor(i/C);t.style.left=c*(cw2+gp2)+"px";t.style.top=r*(ch2+gp2)+"px";t.style.width=cw2+"px";t.style.height=ch2+"px";});}};
  draw();
  pv.addEventListener("input",e=>{if(e.target.dataset.pg){gaLaySet({gap:(+e.target.value)/100});const b=e.target.nextElementSibling;if(b)b.textContent=e.target.value+"%";clearTimeout(pv._t);pv._t=setTimeout(draw,150);}});
  pv.addEventListener("pointerdown",e=>{const gC=e.target.closest(".gaPvC");if(gC){e.preventDefault();   /* TK_V0.9.73 在圖上按住上下拖＝全部一起調構圖（跟截圖全覽一樣） */
      const y0=e.clientY,f0=gaLay().fy,ims=[...gC.querySelectorAll("img")],im=ims.find(x=>x.naturalWidth),T=gC.querySelector(".gaPvT");let f=f0,mv2=false;
      const sl=im&&T?Math.max(30,im.naturalHeight*T.offsetWidth/im.naturalWidth-T.offsetHeight):T?T.offsetHeight:100;   /* 能上下移動的空間（px） */
      const mv=ev=>{const dy=ev.clientY-y0;if(Math.abs(dy)>3)mv2=true;f=Math.round(Math.max(-50,Math.min(50,f0+dy/sl*100))*10)/10;ims.forEach(x=>x.style.objectPosition=`50% ${50-f}%`);const b=pv.querySelector(".gaPvFy");if(b)b.textContent=(f>0?"+":"")+f;};
      const up=()=>{removeEventListener("pointermove",mv);removeEventListener("pointerup",up);removeEventListener("pointercancel",up);if(mv2)gaLaySet({fy:f});};
      addEventListener("pointermove",mv);addEventListener("pointerup",up);addEventListener("pointercancel",up);return;}
    const h=e.target.closest(".gaPvDr");if(!h)return;e.preventDefault();   /* 按住上下拉：往下拉變高（直），往上拉變扁 */
    const y0=e.clientY,r0=gaLay().ratio,g=pv.querySelector(".gaPvC"),tiles=[...g.querySelectorAll(".gaPvT")],L=gaLay(),C=GA.C,cw=tiles[0]?tiles[0].offsetWidth:100,R=Math.ceil(tiles.length/C);let r=r0,moved=false;
    const mv=ev=>{const dy=ev.clientY-y0;if(Math.abs(dy)>4)moved=true;r=Math.max(0.3,Math.min(3,r0+dy/(cw*R*0.8)));const ch=cw*r,gp=L.gap*cw;tiles.forEach((t,i)=>{t.style.top=(Math.floor(i/C)*(ch+gp))+"px";t.style.height=ch+"px";});g.style.height=(R*ch+(R-1)*gp)+"px";const d=pv.querySelector(".gaPvDr");if(d)d.textContent=`⇕ 按住上下拉調高矮（${gaRt(r)}）`;};
    const up=()=>{removeEventListener("pointermove",mv);removeEventListener("pointerup",up);removeEventListener("pointercancel",up);if(moved){gaLaySet({ratio:+r.toFixed(3)});draw();}};
    addEventListener("pointermove",mv);addEventListener("pointerup",up);addEventListener("pointercancel",up);});
  pv.onclick=e=>{const t=e.target;if(t===pv||t.closest("[data-px]")){pv.remove();return;}
    const pr=t.closest("[data-prt]");if(pr){gaLaySet({ratio:+pr.dataset.prt});draw();return;}const pc=t.closest("[data-pc]");if(pc){GA.C=+pc.dataset.pc;draw();return;}
    const pz=t.closest("[data-pz]");if(pz){const L=gaLay();if(pz.dataset.pz==="zh")gaLaySet({zh:L.zh==="r"?"l":"r"});else gaLaySet({zv:L.zv==="d"?"u":"d"});draw();return;}
    const pf=t.closest("[data-pf]");if(pf){const L=gaLay(),v=+pf.dataset.pf;gaLaySet({fy:v===0?0:Math.round(Math.max(-50,Math.min(50,L.fy+v))*10)/10});draw();return;}
    if(t.closest("[data-pgo]")){pv.remove();const go=document.querySelector('#gaOv [data-ggo]');if(go)go.click();}};}
/* TK_V0.9.91 多截的一批：點一下選／取消，挑好按「用這幾張」，之後照樣可以排版、做動圖 */
function snFitLay(n,c0){const P=snLayPairs(n);if(P.length){const b=P.reduce((a,x)=>Math.abs(x[1]-c0)<Math.abs(a[1]-c0)||(Math.abs(x[1]-c0)===Math.abs(a[1]-c0)&&x[1]>a[1])?x:a);return [b[0],b[1]];}return [Math.max(1,Math.ceil(n/c0)),c0];}
function snSelOpen(sid,R){const L=R.pickL,need=R.need||Math.round(L.length/2),cols=R.cols||5,sel=new Set();const st=L.length/need;for(let i=0;i<need;i++)sel.add(Math.min(L.length-1,Math.floor(i*st+st/2)));
  const ov=document.createElement("div");ov.id="snSel";ov.className="snSelOv";document.body.appendChild(ov);const T=m=>(typeof toast==="function"?toast(m):alert(m));
  const P=typeof kPost==="function"?kPost:(typeof post==="function"?post:(typeof deepPost==="function"?deepPost:null));
  const tm=x=>SN.clk?SN.clk(x[0]):snHms(x[0]);
  const draw=()=>{const k=sel.size,rows=Math.max(1,Math.ceil(k/cols));
    ov.innerHTML=`<div class="snSelW"><div class="snSelH"><b>挑截圖：要 ${need} 張</b><span class="${k===need?"ok":"warn"}">已選 ${k} / ${need}</span><button data-ss="x">✕</button></div>
<div class="snSelN">已經先平均選好 ${need} 張（亮的）。點一下取消有擋住、拍糊的，再點旁邊的補上。${k!==need?`<br>選 ${k} 張也可以：版面會變成 ${snFitLay(k,cols).join(" 列 × ")} 欄${snFitLay(k,cols)[0]*snFitLay(k,cols)[1]>k?"（排不滿，最後一列會空）":"（剛好排滿）"}，之後還能換。`:""}</div>
<div class="snSelG">${L.map((x,i)=>`<div class="snSelC${sel.has(i)?" on":""}" data-si="${i}"><img loading="lazy" alt="" src="${imgB(snB())}/snap/${sid}/${x[1]}"><b>${tm(x)}</b>${sel.has(i)?"<i>✔</i>":""}</div>`).join("")}</div>
<div class="snSelB"><button data-ss="all">全選</button><button data-ss="none">全不選</button><button data-ss="even">平均選 ${need} 張</button><span style="flex:1"></span><button data-ss="cancel">不挑了</button><button class="snPkGo" data-ss="go"${k?"":" disabled"}>✔ 用這 ${k} 張</button></div></div>`;};
  draw();
  ov.onclick=async e=>{const c=e.target.closest("[data-si]");if(c){const i=+c.dataset.si;if(sel.has(i))sel.delete(i);else sel.add(i);   /* TK_V1.0.74 只改這一格（不整片重畫：手機上 200 多張不會閃、不會重新載圖） */
      const on=sel.has(i);c.classList.toggle("on",on);const ic=c.querySelector("i");if(on&&!ic)c.insertAdjacentHTML("beforeend","<i>✔</i>");if(!on&&ic)ic.remove();const k=sel.size;
      const hs=ov.querySelector(".snSelH span");if(hs){hs.className=k===need?"ok":"warn";hs.textContent=`已選 ${k} / ${need}`;}const gb=ov.querySelector('[data-ss="go"]');if(gb){gb.disabled=!k;gb.textContent=`✔ 用這 ${k} 張`;}
      const nn=ov.querySelector(".snSelN");if(nn){const fl=snFitLay(k,cols);nn.innerHTML=`已經先平均選好 ${need} 張（亮的）。點一下取消有擋住、拍糊的，再點旁邊的補上。${k!==need?`<br>選 ${k} 張也可以：版面會變成 ${fl.join(" 列 × ")} 欄${fl[0]*fl[1]>k?"（排不滿，最後一列會空）":"（剛好排滿）"}，之後還能換。`:""}`;}return;}
    const b=e.target.closest("[data-ss]");if(!b)return;const a=b.dataset.ss;const keepY=()=>{const g=ov.querySelector(".snSelG");return g?g.scrollTop:0;};
    if(a==="x"){ov.remove();return;}   /* 先關掉：下次打開這場會再問 */
    if(a==="all"){L.forEach((_,i)=>sel.add(i));const y=keepY();draw();ov.querySelector(".snSelG").scrollTop=y;return;}
    if(a==="none"){sel.clear();const y=keepY();draw();ov.querySelector(".snSelG").scrollTop=y;return;}
    if(a==="even"){sel.clear();for(let i=0;i<need;i++)sel.add(Math.min(L.length-1,Math.floor(i*st+st/2)));const y=keepY();draw();ov.querySelector(".snSelG").scrollTop=y;return;}
    if(a==="cancel"){if(!confirm("不挑了？這批截的會丟掉，現在的照片不動。"))return;const j=P&&await P("/api/pc/snap/pickx",{sid});T((j&&j.ok?"✔ ":"✖ ")+((j&&j.message)||""));ov.remove();return;}
    if(a==="go"){const names=[...sel].sort((p,q)=>p-q).map(i=>L[i][1].replace(/^pk_/,""));if(!confirm(`用這 ${names.length} 張？\n\n這場現在的 ${SN.L.length} 張照片會換掉，不能復原。`))return;b.disabled=true;b.textContent="換上去中…";
      const j=P&&await P("/api/pc/snap/pick",{sid,names,cols});T((j&&j.ok?"✔ ":"✖ ")+((j&&j.message)||"沒有成功"));if(j&&j.ok){ov.remove();if(SN.sid===sid){SN.lay=[j.rows,j.cols];SN.regenOn=true;snInfo(sid);}}else{b.disabled=false;b.textContent=`✔ 用這 ${names.length} 張`;}}};}
/* SN-END */

/* ================= 場次資料（直播中＝每秒增量；歷史＝一次載入） ================= */
const TK=["c","g","j","l","s","v"];
const dkey=t=>t?(t.k==="live"?"u:"+t.u:"s:"+t.sid):"";
async function loadSess(t,top){if(!t)return null;const key=dkey(t);let D=S.data[key];
  if(!D)D=S.data[key]={rows:{c:[],g:[],j:[],l:[],s:[],v:[]},cur:{},meta:null,ver:0,added:{}};
  if(D.busy)return D;D.busy=true;
  try{const qs=(t.k==="live"?"u="+encodeURIComponent(t.u):"id="+t.sid)+TK.map(k=>"&"+k+"="+(D.cur[k]||0)).join("")+(top?"&top=1":"");
    const j=await api("/api/pc/sess?"+qs);
    if(!j.sid){D.meta=null;return D;}
    if(D.meta&&D.meta.sid!==j.sid){S.data[key]=null;D.busy=false;return loadSess(t,top);}
    D.added={};for(const k of TK){const a=j[k]||[];D.added[k]=a;for(const r of a)D.rows[k].push(r);D.cur[k]=j.cur[k]!=null?j.cur[k]:D.cur[k];delete j[k];}
    D.meta=j;D.ver++;if(j.top)D.top=j.top;return D;}
  catch(e){return D;}finally{D.busy=false;}}
const nick=r=>r[4]||r[3]||"";
function joinCounts(rows){const c={},out=[];for(const r of rows){c[r[3]]=(c[r[3]]||0)+1;out.push(c[r[3]]);}return out;}
function likeSegments(rows,liveNow){const W=180,open={},closed=[];
  for(const r of rows){const u=r[3],ts=+r[1]||0,s=open[u];if(s&&ts-s.last<=W){s.sum+=+r[5]||0;s.last=ts;s.room=r[6];s.ls2=r[2];}else{if(s)closed.push(s);open[u]={u,nick:nick(r),first:ts,last:ts,ls:r[2],sum:+r[5]||0,room:r[6]};}}
  const now=liveNow?Date.now()/1000:0,act=[];for(const u in open){const s=open[u];if(liveNow&&now-s.last<=W)act.push(s);else closed.push(s);}
  act.sort((a,b)=>b.last-a.last);closed.sort((a,b)=>b.first-a.first);return {act,closed};}
const CARD_DEF=[["live","直播時間"],["viewers","目前在線"],["total_viewers","累積觀眾"],["peak","最高在線"],["unique_observed","觀測使用者"],["comments","留言"],["gifts","禮物"],["diamonds","鑽石"],["repeat","重複進入"],["likes","按讚"],["shares","分享"],["follows","追蹤"]];
const FLASH=new Set(["comments","gifts","diamonds","repeat","shares","follows"]);
/* ================= 直播總覽（和電腦版同樣的版面：鎖定版面＝依視窗等比例） ================= */
const LIVE_LAYOUT={hero:[0,0,1000,38],chart:[614,42,386,292],chat:[0,338,482,368],gift:[482,338,518,368],song:[0,706,382,294],like:[382,706,240,294],join:[622,706,378,294]};
const HIST_LAYOUT={hero:[0,0,680,40],video:[680,0,320,805],song:[680,805,320,195],chart:[352,40,328,216],chat:[0,256,460,444],like:[460,256,220,444],gift:[0,700,388,300],join:[388,700,292,300]};
const HIST_CARD_W=[[110,71,88,83],[82,76,74,120],[82,123,72,75]];
const songTxt=v=>{v=String(v||"");return v&&!/^[#＃]/.test(v)?"#"+v:v;};   /* V0.6.04 點歌一律保留 # */
function blk(key,g,inner){return `<div class="blk" data-b="${key}" style="left:${g[0]/10}%;top:${g[1]/10}%;width:${g[2]/10}%;height:${g[3]/10}%">${inner}</div>`;}
function tblPanel(key,title,extra=""){return `<div class="panel"><div class="bt">${esc(title)}${extra}</div><div class="tbh" id="tb_${key}" style="flex:1;display:flex;flex-direction:column;min-height:0"></div></div>`;}
PAGES[0]={render(pg){pg.innerHTML=`<div class="pg fill" id="dash"></div>`;this.build();},
  build(){const t=tabTarget(),el=$("#dash");if(!el)return;this.t=t;this.D=null;this._ls=null;this.hist=t&&t.k==="hist";this.lastLen={};
    if(!t){el.innerHTML=`<div class="hero"><div class="heroRow"><span class="hu">${S.st&&S.st.running?"連線中...":"目前沒有在監控"}</span></div></div><div class="panel grow" style="display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px"><div class="sub">目前沒有直播中的主播；有人開播會自動出現在上方 LIVE 分頁。</div><button onclick="go(10)">前往主播清單</button></div>`;return;}
    const L=this.hist?HIST_LAYOUT:LIVE_LAYOUT;let h="";
    h+=blk("hero",L.hero,`<div class="hero heroRow" style="height:100%"><span class="hu" id="hUser">…</span><span class="grow"></span><span id="hRoom" class="sub">Room ID：-</span><span id="hTs" class="sub">Time source：-</span></div>`);
    CARD_DEF.forEach(([k,lab],i)=>{let g;if(this.hist){const r=i/4|0,c=i%4,ws=HIST_CARD_W[r];g=[ws.slice(0,c).reduce((a,b)=>a+b,0),40+r*72,ws[c],72];}else{const r=i/4|0,c=i%4,ws=HIST_CARD_W[r],sx=612/352;g=[Math.round(ws.slice(0,c).reduce((a,b)=>a+b,0)*sx),42+r*97,Math.round(ws[c]*sx),r===2?98:97];}
      h+=blk("card_"+k,g,`<div class="card" id="cd_${k}" style="flex:1"><span class="ct">${lab}</span><span class="cvv">—</span></div>`);});
    h+=blk("chart",L.chart,`<div class="panel"><div class="bt">觀眾趨勢<span class="grow"></span><span class="sub">X軸</span><select id="chW">${[[0,"自動"],[30,"30 秒"],[60,"1 分鐘"],[180,"3 分鐘"],[300,"5 分鐘"],[600,"10 分鐘"],[900,"15 分鐘"],[1800,"30 分鐘"],[3600,"1 小時"],[5400,"1.5 小時"],[7200,"2 小時"],[10800,"3 小時"],[21600,"6 小時"]].map(([v,t])=>`<option value="${v}">${t}</option>`).join("")}</select><select id="chL"><option value="s">平滑曲線</option><option value="l">直線</option></select><button id="chS">統計 ▾</button></div><div class="chartw"><canvas id="chC"></canvas></div><div class="giftrow"><span>禮物範圍</span><input type="range" id="gLo" min="0" max="100" value="${CH.lo}"><span id="gLoT"></span><span>禮物數量</span><input type="range" id="gN" min="1" max="100" value="100"><span id="gNT"></span></div></div>`);
    h+=blk("chat",L.chat,tblPanel("dchat","留言"));h+=blk("gift",L.gift,tblPanel("dgift","即時送禮"));h+=blk("like",L.like,tblPanel("dlike",this.hist?"點讚":"即時點讚"));h+=blk("join",L.join,tblPanel("djoin","進入直播間"));
    h+=blk("song",L.song,tblPanel("dsong","歌曲 / 點歌"));
    if(this.hist)h+=blk("video",L.video,`<div class="panel"><div class="bt">歷史影片</div><div id="vidBox" style="flex:1;display:flex;min-height:0"><div class="ph2">讀取中…</div></div></div>`);
    el.innerHTML=(this.hist?HP.stripHtml():"")+`<div class="cv" id="dcv">${h}</div>`;
    const sync=this.hist;
    this.tChat=new VT($("#tb_dchat"),{key:"dchat",filter:false,stick:!sync,cols:[{t:"現在時間",w:90,k:1,f:fmtClk,al:"c"},{t:"暱稱",w:180,v:nick},{t:"留言",w:720,k:5}],onCtx:sync?HP.rowMenu:null,onScroll:sync?HP.userScroll:null});
    this.tGift=new VT($("#tb_dgift"),{key:"dgift",filter:false,stick:!sync,cols:[{t:"現在時間",w:90,k:1,f:fmtClk,al:"c"},{t:"暱稱",w:220,v:nick},{t:"禮物 × 數量",w:300,v:r=>r[5]+" × "+r[6]},{t:"Diamonds",w:110,k:8,f:v=>v?num(v):"—",al:"r"}],onCtx:sync?HP.rowMenu:null,onScroll:sync?HP.userScroll:null});
    this.tLike=new VT($("#tb_dlike"),{key:"dlike",filter:false,cols:[{t:"暱稱",w:150,k:0},{t:"讚數",w:70,k:1,f:num,al:"r"}]});
    this.tJoin=new VT($("#tb_djoin"),{key:"djoin",filter:false,stick:!sync,cols:[{t:"現在時間",w:90,k:1,f:fmtClk,al:"c"},{t:"暱稱",w:180,v:nick},{t:"IN",w:70,k:9,al:"c"}],onCtx:sync?HP.rowMenu:null,onScroll:sync?HP.userScroll:null});
    this.tSong=new VT($("#tb_dsong"),{key:this.hist?"dsongh":"dsong",filter:false,stick:!sync,cols:[{t:"現在時間",w:this.hist?70:90,k:1,f:fmtClk,al:"c"},{t:"暱稱",w:this.hist?110:180,v:nick},{t:"歌曲",w:250,k:5,f:songTxt}],onCtx:sync?HP.rowMenu:null,onScroll:sync?HP.userScroll:null});
    $("#chW").value=CH.win;$("#chL").value=CH.line;$("#chW").onchange=e=>{CH.win=+e.target.value;LS.set("ch",CH);this.chart();};$("#chL").onchange=e=>{CH.line=e.target.value;LS.set("ch",CH);this.chart();};
    $("#chS").onclick=e=>{e.stopPropagation();const r=e.target.getBoundingClientRect();menu(CH_SERIES.map(([k,t])=>({label:(CH.ser.includes(k)?"☑ ":"☐ ")+t,act:()=>{CH.ser=CH.ser.includes(k)?CH.ser.filter(x=>x!==k):CH.ser.concat([k]);LS.set("ch",CH);this.chart();}})),r.left,r.bottom);};
    $("#gLo").oninput=e=>{CH.lo=+e.target.value;LS.set("ch",CH);this.chart();};$("#gN").oninput=e=>{CH.n=+e.target.value;CH.nSet=true;this.chart();};
    new ResizeObserver(()=>{this.fitCards();this.chart();}).observe($("#dcv"));
    gfxLoad();GFX.hostFn=()=>this.hist?($("#dcv [data-b=video]")||$("#dcv")):$("#dcv");GFX.rp.rows=null;      // V0.6.46 送禮動畫：直播畫在總覽上，回放畫在影片上
    if(this.hist)HP.attach(t.sid,this);
    this.poll(true);},
  tab(){this.leave();this.build();},
  leave(){clearTimeout(this.pt);if(this.hist)HP.detach();},
  state(){},
  async poll(first){clearTimeout(this.pt);const t=this.t;if(!t)return;const D=await loadSess(t,false);if(this.t!==t||!$("#dash"))return;this.D=D;
    if(D&&D.meta)this.update(D,first);this.pt=setTimeout(()=>this.poll(false),this.hist?(HP.R&&!HP.R.ended||D&&D.meta&&D.meta.live?5000:60000):1000);},
  update(D,first){const m=D.meta;$("#hUser").textContent=`${m.name}  @${m.u}`;$("#hRoom").textContent="Room ID："+(m.room_id||"-");$("#hTs").textContent="Time source："+(m.time_source||"-");
    const c=Object.assign({},m.cards);c.live=fmtE(m.elapsed);if(c.repeat==null){const jc={};let n=0;for(const r of D.rows.j){jc[r[3]]=(jc[r[3]]||0)+1;if(jc[r[3]]===2)n++;}c.repeat=n;}
    for(const [k] of CARD_DEF){const el=$("#cd_"+k);if(!el)continue;const v=k==="live"?c.live:num(c[k]);const sp=el.querySelector(".cvv");if(sp.textContent!==v){if(!first&&FLASH.has(k)&&sp.textContent!=="—"){el.classList.add("flash");setTimeout(()=>el.classList.remove("flash"),650);}sp.textContent=v;}}
    this.fitCards();
    const R=D.rows;
    if(first||this.hist){this.tChat.setRows(R.c.slice());this.tGift.setRows(R.g.slice());const jc=joinCounts(R.j);this.tJoin.setRows(R.j.map((r,i)=>r.concat([0,0,0,0,0]).slice(0,9).concat([jc[i]])));if(this.tSong)this.tSong.setRows(R.s.slice());
      if(!this.hist){this.tChat.body.scrollTop=1e9;this.tGift.body.scrollTop=1e9;this.tJoin.body.scrollTop=1e9;}}
    else{this.tChat.push(D.added.c||[]);this.tGift.push(D.added.g||[]);if(this.tSong)this.tSong.push(D.added.s||[]);if(!this.hist&&(D.added.g||[]).length)try{gfxRows(D.added.g);}catch(e){}
      if((D.added.j||[]).length){const jc=joinCounts(R.j),b=R.j.length-D.added.j.length;this.tJoin.push(D.added.j.map((r,i)=>r.concat([0,0,0,0,0]).slice(0,9).concat([jc[b+i]])));}}
    this.likes(D);this.chart();if(this.hist)HP.dataReady(D);},
  likes(D){const rows=[];if(this.hist){const s={};for(const r of D.rows.l){const k=nick(r);s[k]=(s[k]||0)+(+r[5]||0);}Object.entries(s).sort((a,b)=>b[1]-a[1]).forEach(([n,v])=>rows.push([n,v]));}
    else{const now=Date.now()/1000,w={},tot={};for(const r of D.rows.l){const k=nick(r),c=+r[5]||0;tot[k]=(tot[k]||0)+c;if(now-(+r[1]||0)<=180)w[k]=(w[k]||0)+c;}
      Object.entries(w).sort((a,b)=>b[1]-a[1]).forEach(([n,v])=>rows.push([n,v]));rows.push({__sep:1,text:"──── 本場累計 ────"});Object.entries(tot).sort((a,b)=>b[1]-a[1]).forEach(([n,v])=>rows.push([n,v]));}
    const sig=rows.length+":"+(rows[0]?rows[0][1]:0)+":"+D.rows.l.length;if(this._ls!==sig){this._ls=sig;this.tLike.setRows(rows);}},
  fitCards(){const zf=S.zf||1;$$("#dcv .card").forEach(el=>{const sp=el.querySelector(".cvv"),w=el.clientWidth,h=el.clientHeight,n=Math.max(3,sp.textContent.length);   /* V0.6.50 縮小介面時數字／標題不會小到看不清楚 */
    sp.style.fontSize=Math.max(13/zf,Math.min(h*0.36,w*1.75/n,34/zf))+"px";el.querySelector(".ct").style.fontSize=Math.max(10/zf,Math.min(12/zf,h*0.13))+"px";});},
  pending(){const box=$("#pendBox");if(!box||!S.st)return;const list=S.st.rooms.filter(r=>!r.live);const nEl=$("#pendN");if(nEl)nEl.textContent=list.length+" 位";
    const h=list.map(r=>`<button class="${r.priority?"pri":""}" data-u="${esc(r.u)}" title="@${esc(r.u)}">${r.priority?"★":"○"} ${esc(r.name)}</button>`).join("");
    if(box._h!==h){box._h=h;box.innerHTML=h;$$("button",box).forEach(b=>b.onclick=async()=>{const u=b.dataset.u,r=S.st.rooms.find(x=>x.u===u);const j=await post("/api/pc/streamer/priority",{u,on:!(r&&r.priority)});if(j.ok){if(r)r.priority=j.priority;this.pending();}else toast("✖ "+(j.message||"沒有成功"));});}},
  chart(){const cv=$("#chC");if(!cv||!this.D||!this.D.meta)return;drawViewerChart(cv,this.D,this.hist?HP.t:null);const g=this.D.rows.g.filter(r=>+r[8]>0);$("#gLoT").textContent=`≥ ${CH_lo()}`;$("#gNT").textContent=`${CH.nSet?Math.max(1,Math.round(CH.n/100*g.length)):"全部"} / ${g.length}`;}};
/* ================= 觀眾趨勢圖（和 ViewerChart 一樣：平滑／直線、禮物紅點、留言／按讚／進場頻率） ================= */
const CH=Object.assign({win:0,line:"s",ser:["viewers","gifts"],lo:33,n:100},LS.get("ch",{}));CH.nSet=false;
const CH_SERIES=[["viewers","觀眾人數"],["gifts","禮物價值（紅點，≥10，頂點 5000）"],["comments","留言數"],["likes","按讚數"],["joins","進場數"]];
const CH_lo=()=>Math.round(Math.pow(10,CH.lo/100*Math.log10(5000)));
function niceStep(mx){const raw=mx/4,mag=Math.pow(10,Math.floor(Math.log10(raw||1)));for(const m of [1,2,5,10])if(raw<=m*mag)return m*mag;return 10*mag;}
function drawViewerChart(cv,D,tNow){const r=cv.getBoundingClientRect(),dpr=devicePixelRatio||1,W=r.width,H=r.height;if(!W||!H)return;cv.width=W*dpr;cv.height=H*dpr;const g=cv.getContext("2d");g.setTransform(dpr,0,0,dpr,0,0);
  const css=k=>getComputedStyle(document.documentElement).getPropertyValue("--"+k).trim();g.fillStyle=css("chart_bg");g.fillRect(0,0,W,H);
  const vs=D.rows.v;const L=44,R=10,T=20,Bm=20,pw=W-L-R,ph=H-T-Bm;g.font="11px sans-serif";
  if(vs.length<2){g.fillStyle=css("subtext");g.textAlign="center";g.fillText("等待 5 秒觀眾取樣資料…",W/2,H/2);return;}
  let t1=tNow!=null&&D.meta.live_start?D.meta.live_start+tNow:+vs[vs.length-1][1],t0=+vs[0][1];if(tNow==null)t1=Math.max(t1,+vs[vs.length-1][1]);
  if(CH.win>0)t0=Math.max(t0,t1-CH.win);if(tNow!=null&&CH.win===0)t1=+vs[vs.length-1][1];if(t1<=t0)t1=t0+1;
  const pts=vs.filter(x=>+x[1]>=t0-5&&+x[1]<=t1+5);const mxV=Math.max(1,...pts.map(x=>+x[2]||0))*1.12,st=niceStep(mxV),top=Math.ceil(mxV/st)*st;
  const X=t=>L+(t-t0)/(t1-t0)*pw,Y=v=>T+ph-v/top*ph;
  g.strokeStyle=css("chart_grid");g.fillStyle=css("chart_label");g.lineWidth=1;g.textAlign="right";
  for(let v=0;v<=top+1e-9;v+=st){const y=Y(v)+.5;g.beginPath();g.moveTo(L,y);g.lineTo(L+pw,y);g.stroke();g.fillText(num(v),L-4,y+4);}
  g.textAlign="center";for(let i=0;i<5;i++){const t=t0+(t1-t0)*i/4;g.fillText(fmtClk(t),Math.min(Math.max(L+20,X(t)),W-30),H-5);}
  g.textAlign="left";g.fillStyle=css("text");g.fillText("觀眾 · "+(CH.line==="s"?"平滑":"直線"),L,13);g.fillStyle=css("subtext");g.fillText("人數",4,13);
  const legend=[];
  const rate=(arr,col,lab)=>{const bk=Math.max(60,(t1-t0)/48);const n=Math.ceil((t1-t0)/bk)+1,b=new Array(n).fill(0);for(const [ts,c] of arr){if(ts<t0||ts>t1)continue;b[Math.floor((ts-t0)/bk)]+=c;}
    const mx=Math.max(1,...b);g.strokeStyle=col;g.globalAlpha=.82;g.lineWidth=1.4;g.beginPath();b.forEach((v,i)=>{const x=X(t0+i*bk+bk/2),y=T+ph-v/mx*ph*.9;i?g.lineTo(x,y):g.moveTo(x,y);});g.stroke();g.globalAlpha=1;
    legend.push([col,`${lab} 峰值 ${num(mx)}/${bk<=60?"":Math.round(bk/60)}分`]);};
  if(CH.ser.includes("comments"))rate(D.rows.c.map(r=>[+r[1],1]),css("series_comments"),"留言");
  if(CH.ser.includes("likes"))rate(D.rows.l.map(r=>[+r[1],+r[5]||0]),css("series_likes"),"按讚");
  if(CH.ser.includes("joins"))rate(D.rows.j.map(r=>[+r[1],1]),css("series_joins"),"進場");
  if(CH.ser.includes("viewers")){g.strokeStyle=css("viewer_line");g.lineWidth=2;g.beginPath();let px=null,py=null;
    pts.forEach((p,i)=>{const x=X(+p[1]),y=Y(+p[2]||0);if(!i)g.moveTo(x,y);else if(CH.line==="s")g.quadraticCurveTo(px,py,(px+x)/2,(py+y)/2);else g.lineTo(x,y);px=x;py=y;});if(CH.line==="s"&&px!=null)g.lineTo(px,py);g.stroke();legend.push([css("viewer_line"),"觀眾"]);}
  if(CH.ser.includes("gifts")){const lo=CH_lo(),cap=5000;let gs=D.rows.g.filter(r=>+r[1]>=t0&&+r[1]<=t1&&(+r[8]||0)>=lo);const allN=gs.length;
    let lim=CH.nSet?Math.max(1,Math.round(CH.n/100*D.rows.g.filter(r=>+r[8]>0).length)):((t1-t0)>=3600?10:1e9);
    if(gs.length>lim)gs=gs.slice().sort((a,b)=>b[8]-a[8]).slice(0,lim);const GY=v=>T+ph-Math.min(v,cap)/cap*ph*.92;
    g.setLineDash([4,3]);g.strokeStyle="rgba(255,59,92,.45)";g.beginPath();g.moveTo(L,GY(cap)+.5);g.lineTo(L+pw,GY(cap)+.5);g.stroke();g.setLineDash([]);g.fillStyle="rgba(255,59,92,.8)";g.textAlign="right";g.fillText("5000+",L+pw-2,GY(cap)-3);
    const used=[];g.textAlign="center";for(const r of gs){const x=X(+r[1]),y=GY(+r[8]);g.fillStyle="#ff3b5c";g.strokeStyle="#fff";g.lineWidth=1;g.beginPath();g.arc(x,y,3.5,0,7);g.fill();g.stroke();
      const lab=num(r[8]);if(!used.some(([ux,uy])=>Math.abs(ux-x)<34&&Math.abs(uy-y)<13)){g.fillStyle=css("gift_label");g.fillText(lab,x,y-6);used.push([x,y]);}}
    legend.push(["#ff3b5c",`禮物 ●${gs.length<allN?`（前${gs.length}高）`:"（全部）"}`]);}
  if(tNow!=null&&D.meta.live_start){const x=X(D.meta.live_start+tNow);if(x>=L&&x<=L+pw){g.strokeStyle=css("text_strong");g.globalAlpha=.55;g.beginPath();g.moveTo(x,T);g.lineTo(x,T+ph);g.stroke();g.globalAlpha=1;}}
  let lx=W-R;g.textAlign="right";for(const [c,t] of legend.reverse()){g.fillStyle=c;g.fillText(t,lx,13);lx-=g.measureText(t).width+14;if(lx<L+120)break;}}
/* ================= 歷史回放（紫色分頁）：時間軸、播放器、表格跟著時間走 ================= */
const HP={t:0,sid:0,R:null,page:null,
  stripHtml(){return `<div class="hero" style="flex:none"><div class="row"><b style="font-size:15px;color:var(--text_strong)" id="hpTitle">歷史回放</b><span id="hpPos" class="sub" style="min-width:260px">00:00:00 / 00:00:00  ·  --:--:--</span><div class="tl" id="hpTl"><canvas></canvas></div></div></div>
<div class="panel row wrap" style="flex:none;padding:4px 8px"><button id="hpPlay">▶ 播放</button><button id="hpPause">Ⅱ 暫停</button><button id="hpLive" style="display:none;color:#ff4d6d;font-weight:800" title="回到直播（約 15 秒延遲）">● LIVE</button><span class="sub">音量</span><input type="range" id="hpVol" min="0" max="150" value="${LS.get("vol",80)}" style="width:120px"><span id="hpVolT"></span>
<span class="sub">音檔對齊秒數</span><input type="number" id="hpOff" min="-120" max="120" step="0.5" value="0" style="width:70px"><button id="hpRst">↺ 重設</button><button id="hpJpg" class="mpjpg" hidden title="切換：看影片（MP4）／看 20 張圖（JPG）；預設先看圖">MP4/JPG</button><button onclick="edOpen(HP.sid,HP.t)" title="把這場剪成一節一節（也可以在任何場次上按右鍵）">✂ 剪輯</button><button id="hpYtB" hidden title="切換：用本機 MP4 播／直接播 YouTube（跟留言、時間軸同步）">▶ YouTube</button><button id="hpYtc" hidden title="直接從 YouTube 抓一段下來（不用整部下載）；抓好的在「剪好的」裡，也可以再細剪">✂ YouTube 抓這段</button><span id="hpState" class="sub grow"></span></div><div id="hpStrip"></div><div id="hpAct"></div><div id="hpClips"></div><div class="sub" id="hpInfo" style="flex:none"></div>`;},
  async attach(sid,page){this.page=page;this.sid=sid;this.t=0;this.follow=true;this.off=0;this.cur=null;
    const v=$("#hpVol");const vt=()=>{$("#hpVolT").textContent=v.value+"%";this.setVol();};v.oninput=()=>{LS.set("vol",+v.value);vt();};vt();
    $("#hpOff").onchange=e=>{this.off=+e.target.value||0;this.seek(this.t,!this.paused());};$("#hpRst").onclick=()=>{$("#hpOff").value=0;this.off=0;this.seek(this.t,!this.paused());};
    $("#hpPlay").onclick=()=>this.play();$("#hpPause").onclick=()=>this.pause();
    const tl=$("#hpTl");tl.onmousedown=e=>{const mv=ev=>this.tlSeek(ev,false);this.tlSeek(e,true);addEventListener("mousemove",mv);addEventListener("mouseup",()=>removeEventListener("mousemove",mv),{once:true});};
    new ResizeObserver(()=>this.drawTl()).observe(tl);
    try{this.R=await api("/api/replay?id="+sid);}catch(e){this.R=null;}if(this.sid!==sid)return;this.setupMedia();
    try{this.htl=htlMount($("#hpStrip"),{sid,key:"pc",total:()=>this.total||(this.R&&this.R.total)||1,t:()=>this.t||0,playing:()=>!this.paused(),seek:(t,p)=>this.seek(t,p)});}catch(e){}   /* V0.6.85 縮圖時間軸 */
    try{if(this.R&&this.R.u)this.act=haMount($("#hpAct"),{sid,u:this.R.u,name:this.R.name||this.R.u,pause:()=>this.pause(),after:()=>{}});}catch(e){}   /* V0.6.86 保存等級、只錄聲音、刪除 */
    try{const bx=$("#vidBox");let cp=$("#hpCp");if(bx&&!cp){cp=document.createElement("div");cp.id="hpCp";bx.insertAdjacentElement("afterend",cp);}cpMount(cp,bx,{sid,pause:()=>this.pause(),alive:()=>this.sid===sid,media:()=>this.el});}catch(e){}   /* V0.7.14 剪好的放在完整影片右邊，下面 « ●•••• » 切換 */
    if(this.lv){const lb=$("#hpLive");lb.style.display="";lb.onclick=()=>this.lvSeek(1e12,true);this.lvPoll();clearInterval(this.lvi);this.lvi=setInterval(()=>this.lvPoll(),2000);this.lvSeek(1e12,true);}   /* V0.6.53 LIVE 時移 */
   try{sxSubInit(sid,()=>$("#vidBox"),($("#hpState")||{}).parentNode);}catch(e){}this.drawTl();this.info();
    clearInterval(this.iv);this.iv=setInterval(()=>this.tick(),250);
    const A=S.histAt;if(A&&A.sid===sid&&this.R&&this.R.live_start){S.histAt=null;const t=Math.max(0,A.at-this.R.live_start+(A.how==="hl"?0:3));setTimeout(()=>{if(this.sid===sid){this.follow=true;this.seek(t,true);toast(A.how==="hl"?`✨ 從精彩片段開始播（${fmtE(t)}）`:`從禮物時間 +3 秒開始播（${fmtE(t)}）`);}},300);}},
  detach(){clearInterval(this.iv);if(this.ytP){try{this.ytP.destroy();}catch(e){}this.ytP=null;}this.ytm=false;this.ytCur=null;try{sxSubStop();}catch(e){}try{snStop();}catch(e){}this.iv=null;clearInterval(this.lvi);this.lvi=null;if(this.hls){try{this.hls.destroy();}catch(e){}this.hls=null;}this.lv=false;this.lvm=null;this.lvInfo=null;this.lvWant=false;if(this.el){try{this.el.pause();}catch(e){}}this.el=null;this.sid=0;},
  setupMedia(){const R=this.R,box=$("#vidBox");if(!box)return;const files=(R&&R.files)||[];this.lv=!!(R&&R.lv&&!R.ended);this.lvm=null;const hasV=files.some(f=>f.kind==="video")||this.lv,hasA=files.some(f=>f.kind==="audio");
    /* V0.8.24 ▶ YouTube 模式：本機沒有 MP4（或你選了 YouTube）就直接內嵌 YouTube 播，時間跟留言／送禮／時間軸同步 */
    this.ytL=((R&&R.yt)||[]).filter(y=>y&&y.url).slice().sort((a,b)=>a.L0-b.L0);this.ytm=false;if(this.ytP){try{this.ytP.destroy();}catch(e){}this.ytP=null;}
    {const yb=$("#hpYtB"),yc=$("#hpYtc"),has=!!this.ytL.length&&!this.lv;if(yb){yb.hidden=!has||!hasV;yb.textContent=LS.get("hp_yt",false)?"💾 本機播放":"▶ YouTube 播放";yb.onclick=()=>{LS.set("hp_yt",!LS.get("hp_yt",false));const t=this.t,pl=!this.paused();this.setupMedia();this.seek(t,pl);};}if(yc){yc.hidden=!has;yc.onclick=()=>ytcOpen(this.sid,this.t);}
      if(has&&(!hasV||LS.get("hp_yt",false))){this.ytm=true;box.classList.remove("jpg");box.innerHTML=`<div class="hv hpYtBox"><div id="hpYtP"></div></div>`;this.el=null;this.ytSetup();
        this.recStart=R&&R.segs&&R.segs.length?Math.min(...R.segs.map(s=>s.start)):0;this.total=R?R.total:0;$("#hpTitle").textContent=`歷史回放 · @${R?R.u:""} · ${R?R.name:""}`;
        $("#hpState").textContent=`▶ YouTube（不公開影片）· ${this.ytL.length} 段`+(hasV?"":" · 本機 MP4 已經沒有");return;}}
    const jb=$("#hpJpg");if(jb)jb.hidden=true;box.classList.remove("jpg");
    if(hasV){const sn=!this.lv,has=!!(R&&R.snaps&&R.snaps.length);box.innerHTML=`<video class="hv" id="hpVid" playsinline></video>`+(sn?`<div class="snHost" id="hpSnap"></div>`:"");this.el=$("#hpVid");   /* TK_V0.9.93 沒有截圖也有 MP4/JPG（JPG 那邊可以「從影片截圖」） */
      if(sn){try{snMount($("#hpSnap"),this.sid,R.snaps,t=>this.seek(t,!this.paused()),t=>fmtClk(R.live_start+t),R.snap_layout);}catch(e){}   /* V0.7.07 有影片也先看 20 張圖（MP4/JPG 切換） */
        if(has)box.classList.add("jpg");if(jb){jb.hidden=false;jb.classList.toggle("on",has);jb.onclick=()=>{const on=box.classList.toggle("jpg");jb.classList.toggle("on",on);};}}}
    else{const sn=!!(R&&R.snaps&&R.snaps.length);box.innerHTML=(sn?`<div class="snHost" id="hpSnap"></div>`:`<div class="ph2">${hasA||(R&&R.stream)?"無影片提供（只保留音訊）":"無影片提供"}</div>`)+`<audio id="hpAud"></audio>`;this.el=$("#hpAud");
      if(sn){try{snMount($("#hpSnap"),this.sid,R.snaps,t=>this.seek(t,!this.paused()),t=>fmtClk(R.live_start+t),R.snap_layout);}catch(e){}}}   /* V0.6.62 只錄聲音的快照放在影片的位置 */
    const el=this.el;el.onended=()=>{if(this.lv){if(this.lvm==="vod"&&this.vod)this.lvSeek(this.vod.end,true);else setTimeout(()=>{if(this.lv)this.lvSeek(1e12,true);},1500);return;}this.next();};el.ontimeupdate=()=>{};this.setVol();
    $("#hpTitle").textContent=`歷史回放 · @${R?R.u:""} · ${R?R.name:""}`;
    const st=this.lv?"📺 直播畫面（可往回看）準備中…":hasV?`影片可用 · ${files.filter(f=>f.kind==="video").length} 段`:hasA?"音檔可用":R&&R.stream?"FLV 尚未轉檔 · 先播聲音":"未提供音檔 · 文字時間軸仍可使用";$("#hpState").textContent=st+(!hasV&&R&&R.snaps&&R.snaps.length?` · 📷 ${R.snaps.length} 張快照（‹ › 翻看）`:"");
    this.recStart=R&&R.segs&&R.segs.length?Math.min(...R.segs.map(s=>s.start)):0;this.total=R?R.total:0;},
  /* ---- V0.8.24 YouTube 內嵌播放 ---- */
  ytId(u){const m=/(?:youtu\.be\/|v=|embed\/|shorts\/)([\w-]{11})/.exec(String(u||""));return m?m[1]:"";},
  ytAt(t){let p=null;for(const y of this.ytL||[])if(y.L0<=t+1)p=y;return p;},
  ytSetup(){const sid=this.sid;loadYtApi().then(ok=>{if(!ok||this.sid!==sid||!this.ytm){if(!ok)$("#hpState").textContent="YouTube 播放器載入失敗（網路？）";return;}
      const first=this.ytAt(this.t||this.recStart)||this.ytL[0];this.ytCur=first;
      this.ytP=new window.YT.Player("hpYtP",{width:"100%",height:"100%",videoId:this.ytId(first.url),playerVars:{playsinline:1,rel:0,modestbranding:1,origin:location.origin,start:Math.max(0,Math.floor((this.t||0)-first.L0))},
        events:{onReady:()=>{this.setVol();if(this.ytWant){const w=this.ytWant;this.ytWant=null;this.ytSeek(w.t,w.play);}},
          onStateChange:e=>{if(e.data===0){const i=this.ytL.indexOf(this.ytCur);if(i>=0&&i<this.ytL.length-1)this.ytSeek(this.ytL[i+1].L0,true);else $("#hpState").textContent="播放完成";}},
          onError:e=>{$("#hpState").textContent=`YouTube 播不了（${e.data===101||e.data===150?"影片不允許內嵌：要改成「不公開」，或還在處理":e.data===100?"影片不見了":"錯誤 "+e.data}）`;}}});});},
  ytSeek(t,play){t=Math.max(0,Math.min(this.total||t,t));this.t=t;this.follow=true;const y=this.ytAt(t);
    if(!this.ytP||!this.ytP.seekTo){this.ytWant={t,play};this.sync();return;}
    if(!y){try{this.ytP.pauseVideo();}catch(e){}$("#hpState").textContent="這個時間點 YouTube 上沒有（還沒開始錄）";this.sync();return;}
    const mt=Math.max(0,t-y.L0);
    if(y!==this.ytCur){this.ytCur=y;try{(play?this.ytP.loadVideoById:this.ytP.cueVideoById).call(this.ytP,{videoId:this.ytId(y.url),startSeconds:mt});}catch(e){}}
    else{try{this.ytP.seekTo(mt,true);if(play)this.ytP.playVideo();}catch(e){}}
    $("#hpState").textContent=`▶ YouTube 第 ${this.ytL.indexOf(y)+1}/${this.ytL.length} 段`;this.sync();},
  segAt(t){const R=this.R;if(!R||!R.segs)return null;let best=null;for(const s of R.segs){const e=s.end==null?1e12:s.end;if(t>=s.start&&t<e){best=s;break;}}return best;},
  seek(t,play){if(this.lv){this.lvSeek(t,play);return;}if(this.ytm){this.ytSeek(t,play);return;}t=Math.max(0,Math.min(this.total||t,t));this.t=t;this.follow=true;const R=this.R,el=this.el;if(!el||!R){this.sync();return;}
    const s=this.segAt(t);if(!s){try{el.pause();}catch(e){}$("#hpState").textContent="此時間點尚未開始錄音 · 前段沒有音檔";this.cur=null;this.sync();return;}
    const f=R.files[s.f];this.cur=s;
    if(f.kind==="flv"){const url=`${B}/aud/${this.sid}?t=${(t+this.off).toFixed(1)}`;el.src=url;this.base=t;this.flv=true;}
    else{this.flv=false;const url=B+f.url;if(el._u!==url){el.src=url;el._u=url;}const mt=t-s.start+s.off+this.off;const set=()=>{try{el.currentTime=Math.max(0,mt);}catch(e){}};if(el.readyState>=1)set();else el.onloadedmetadata=set;}
    if(play)el.play().catch(()=>{});this.sync();},
  next(){const R=this.R;if(!R||!this.cur)return;const segs=R.segs.slice().sort((a,b)=>a.start-b.start);const i=segs.indexOf(this.cur);if(i>=0&&i<segs.length-1)this.seek(segs[i+1].start,true);else $("#hpState").textContent="播放完成";},
  play(){if(this.ytm){if(this.ytP&&this.ytP.playVideo){if(!this.ytCur)this.ytSeek(this.t||this.recStart,true);else this.ytP.playVideo();}return;}if(!this.el)return;if(this.lv){if(!this.lvm)this.lvSeek(this.t||1e12,true);else this.el.play().catch(()=>{});return;}if(!this.cur)this.seek(this.t||this.recStart,true);else this.el.play().catch(()=>{});},
  pause(){if(this.ytm){try{this.ytP&&this.ytP.pauseVideo();}catch(e){}$("#hpState").textContent="已暫停（YouTube）";return;}if(this.el)this.el.pause();$("#hpState").textContent=this.R&&this.R.files&&this.R.files.length?"已暫停":$("#hpState").textContent;},
  paused(){if(this.ytm){try{return !this.ytP||!this.ytP.getPlayerState||this.ytP.getPlayerState()!==1;}catch(e){return true;}}return !this.el||this.el.paused;},
  setVol(){const v=+(($("#hpVol")||{}).value||80);if(this.ytm){try{this.ytP&&this.ytP.setVolume(Math.min(100,v));}catch(e){}return;}if(!this.el)return;if(v<=100){this.el.volume=v/100;if(this.gain)this.gain.gain.value=1;}
    else{this.el.volume=1;try{if(!this.actx){this.actx=new AudioContext();}if(!this.gain||this.gainEl!==this.el){const src=this.actx.createMediaElementSource(this.el);this.gain=this.actx.createGain();src.connect(this.gain).connect(this.actx.destination);this.gainEl=this.el;}this.gain.gain.value=v/100;}catch(e){}}},
  tick(){if(this.ytm){if(this.ytP&&this.ytCur&&!this.paused()){try{this.t=this.ytCur.L0+(this.ytP.getCurrentTime()||0);}catch(e){}this.sync();
      const p=this.page;if(p&&p.D)try{gfxReplay(p.D.rows.g,this.t,r=>+r[2]||0,r=>({k:gfxKey(r[9],r[5]),gid:r[9],name:r[5],nick:r[4]||r[3],count:+r[6]||1,dia:+r[8]||0}));}catch(e){}}return;}
    const el=this.el;if(this.lv&&this.R)this.total=Math.max(this.total||0,Date.now()/1000-this.R.live_start);
    if(el&&!el.paused&&(this.cur||this.lvm)){this.t=this.lvm?this.lvCur():this.flv?this.base+el.currentTime:this.cur.start+(el.currentTime-this.cur.off)-this.off;this.sync();
      const p=this.page;if(p&&p.D)try{gfxReplay(p.D.rows.g,this.t,r=>+r[2]||0,r=>({k:gfxKey(r[9],r[5]),gid:r[9],name:r[5],nick:r[4]||r[3],count:+r[6]||1,dia:+r[8]||0}));}catch(e){}}},     // V0.6.46
  sync(){const R=this.R,ls=R?R.live_start:0;$("#hpPos").textContent=`時間軸：${fmtE(this.t)} / ${fmtE(this.total)} · 實際 ${fmtClk(ls+this.t)}`;this.drawTl();try{sxSubPaint(this.t);}catch(e){}try{snPaint(this.t);}catch(e){}
    const p=this.page;if(!p||!p.D)return;if(this.follow)for(const tb of [p.tChat,p.tGift,p.tJoin]){const k=lowerBound(tb.rows,this.t);this._auto=true;tb.setDivider(k,`──── 目前時間 ${fmtClk(ls+this.t)} · ${fmtE(this.t)} ────`);tb.scrollToK(k,"2nd-last");setTimeout(()=>this._auto=false,50);}
    if(Math.abs((this._ct||0)-this.t)>2){this._ct=this.t;p.chart();}},
  userScroll(){if(!HP._auto)HP.follow=false;},
  /* ---- V0.6.53 LIVE 時移：還在直播、正在錄影的場次，用歷史回放的畫面看直播（約 15 秒延遲、可往回拖） ---- */
  async lvPoll(){if(!this.lv||!this.R)return;try{const j=await api("/api/lv?u="+encodeURIComponent(this.R.u));if(!this.lv)return;
      if(j.ok){this.lvBad=0;this.lvInfo=j;this.total=Math.max(this.total||0,j.now||0);if(this.lvWant&&j.ready){this.lvWant=false;this.lvSeek(this.lvWantT,true);}else if(!j.ready&&!this.lvm)$("#hpState").textContent="📺 準備直播畫面中…（第一次約 10 秒）";}
      else{this.lvBad=(this.lvBad||0)+1;if(this.lvBad>=3)this.lvGiveUp(j.message);else if(!this.lvm)$("#hpState").textContent=j.message||"直播畫面暫時不能用";}}catch(e){}},
  lvGiveUp(msg){if(!this.lv)return;this.lv=false;this.lvm=null;clearInterval(this.lvi);this.lvi=null;if(this.hls){try{this.hls.destroy();}catch(e){}this.hls=null;}
    try{this.el.pause();this.el.removeAttribute("src");this.el.load();}catch(e){}const lb=$("#hpLive");if(lb)lb.style.display="none";
    $("#hpState").textContent=(msg||"直播或錄影已經結束")+"：關掉這個分頁、從歷史紀錄重新打開就能看錄好的影片";},
  async lvSrc(url,t){const v=this.el;if(!v)return false;const full=B+"/"+url;
    if(v.canPlayType("application/vnd.apple.mpegurl")){if(this.hls){this.hls.destroy();this.hls=null;}v.src=full;}
    else{if(!(await loadHls())){$("#hpState").textContent="這個瀏覽器不能播直播畫面（需要 HLS）";return false;}if(this.hls)this.hls.destroy();
      this.hls=t==null?new Hls({liveSyncDuration:LV_DELAY,liveMaxLatencyDuration:LV_DELAY+15,maxLiveSyncPlaybackRate:1,maxBufferLength:30,backBufferLength:60}):new Hls({maxBufferLength:30});this.hls.loadSource(full);this.hls.attachMedia(v);}
    v.onloadedmetadata=()=>{if(t!=null){try{v.currentTime=t;}catch(e){}}else{try{if(v.seekable&&v.seekable.length)v.currentTime=Math.max(0,v.seekable.end(v.seekable.length-1)-LV_DELAY);}catch(e){}}};return true;},
  async lvSeek(t,play){if(!this.lv)return;const i=this.lvInfo;t=Math.max(0,Math.min(t,Math.max(this.total||0,i?i.now:0)));this.t=t;this.follow=true;
    if(!i||!i.ready){this.lvWant=true;this.lvWantT=t;$("#hpState").textContent="📺 準備直播畫面中…（第一次約 10 秒）";this.sync();return;}
    if(t>=i.buf[1]-8){this.lvm="live";this.lvT0=i.live_t0;if(!(await this.lvSrc(i.live,null)))return;$("#hpState").textContent="● LIVE（約 15 秒延遲）· 可以往回拖";}
    else{if(t<i.buf[0]){toast("更早的部分還在載入（藍色條往左長），先從最早的地方播");t=i.buf[0];}let j;try{j=await api(`/api/lv/vod?u=${encodeURIComponent(this.R.u)}&t=${t.toFixed(1)}`);}catch(e){return;}
      if(!j.ok){toast(j.message||"沒辦法跳到那裡");return;}this.vod=j;this.lvm="vod";if(!(await this.lvSrc(j.url,Math.max(0,t-j.start))))return;$("#hpState").textContent="⏪ 回看中 · 按 ● LIVE 回到現在";}
    const lb=$("#hpLive");if(lb)lb.textContent=this.lvm==="live"?"● LIVE":"回到 LIVE";
    if(play!==false&&this.el)this.el.play().catch(()=>{});this.t=t;this.sync();},
  lvCur(){const v=this.el;if(this.lvm==="vod"&&this.vod)return this.vod.start+(v.currentTime||0);if(this.lvm==="live"&&this.lvT0!=null)return this.lvT0+(v.currentTime||0);return this.t;},
  dataReady(D){this.sync();},
  rowMenu(r,e){const ls=HP.R?HP.R.live_start:0,t=+r[2]||0;menu([{label:`⏩ 跳到這個時間　${fmtClk(ls+t)}（直播 ${fmtE(t)}）`,act:()=>HP.seek(Math.max(0,t-0.5),true)},   /* V1.1.19 早 0.5 秒落地：送禮動畫完整出現 */{label:"⏪ 跳到前 10 秒並播放（看前因後果）",act:()=>HP.seek(t-10,true)},{label:"⏸ 跳過去但不播放",act:()=>{HP.pause();HP.seek(t,false);}}],e.clientX,e.clientY);},
  tlSeek(e,down){const r=$("#hpTl").getBoundingClientRect(),x=Math.max(0,Math.min(1,(e.clientX-r.left-8)/(r.width-16)));const rs=this.recStart,dur=this.total-rs;let t,play=true;
    if(rs>0){if(x<=0.05){t=rs*x/0.05;play=false;}else t=rs+dur*(x-0.05)/0.95;}else t=this.total*x;this.seek(t,play&&(!this.paused()||down));},
  drawTl(){const c=$("#hpTl canvas");if(!c)return;const r=c.getBoundingClientRect(),dpr=devicePixelRatio||1;c.width=r.width*dpr;c.height=r.height*dpr;const g=c.getContext("2d");g.setTransform(dpr,0,0,dpr,0,0);
    const W=r.width,x0=8,w=W-16,y=13,rs=this.recStart||0,tot=this.total||1,red=rs>0?0.05:0;g.fillStyle="#c83b46";if(red)g.fillRect(x0,y,w*red,5);g.fillStyle="#3ea9e8";g.fillRect(x0+w*red,y,w*(1-red),5);
    if(rs>0){g.fillStyle="#f3c75f";g.fillRect(x0+w*red-1,y-4,2,13);}const pos=rs>0?(this.t<=rs?this.t/rs*0.05:0.05+(this.t-rs)/(tot-rs||1)*0.95):this.t/tot;const px=x0+w*Math.max(0,Math.min(1,pos));
    const ts=getComputedStyle(document.documentElement).getPropertyValue("--text_strong");g.fillStyle=ts;g.fillRect(px-1,4,2,22);g.beginPath();g.arc(px,15.5,4,0,7);g.fill();},
  info(){const R=this.R;if(!R){$("#hpInfo").textContent="讀不到這一場的回放資料";return;}const ls=R.live_start,rs=this.recStart,tot=R.total;
    $("#hpInfo").textContent=`開播 ${fmtClk(ls)}　→　開始錄音 ${fmtClk(ls+rs)}　→　結束 ${fmtClk(ls+tot)}　｜　直播總長 ${fmtE(tot)}　｜　未錄製 ${fmtE(rs)}（紅色 5%）　｜　已錄製 ${fmtE(tot-rs)}（藍色 95%）`;}};
/* V0.8.24 YouTube IFrame API（只載一次） */
let _ytApiP=null;function loadYtApi(){if(window.YT&&window.YT.Player)return Promise.resolve(true);if(_ytApiP)return _ytApiP;
  _ytApiP=new Promise(res=>{const prev=window.onYouTubeIframeAPIReady;window.onYouTubeIframeAPIReady=()=>{try{prev&&prev();}catch(e){}res(true);};const s=document.createElement("script");s.src="https://www.youtube.com/iframe_api";s.onerror=()=>{_ytApiP=null;res(false);};document.head.appendChild(s);setTimeout(()=>res(!!(window.YT&&window.YT.Player)),15000);});return _ytApiP;}
/* V0.8.24 ✂ 從 YouTube 抓這段：只抓那一段（yt-dlp），抓好的放「剪好的」，也可以當初剪再細剪 */
function ytcFmt(s){s=Math.max(0,Math.round(s));return Math.floor(s/3600)+":"+String(Math.floor(s%3600/60)).padStart(2,"0")+":"+String(s%60).padStart(2,"0");}
function ytcParse(v){const p=String(v||"").trim().split(":").map(Number);if(p.some(isNaN))return NaN;return p.reduce((a,b)=>a*60+b,0);}
function ytcOpen(sid,t){let o=document.getElementById("ytcDlg");if(o)o.remove();o=document.createElement("div");o.id="ytcDlg";
  o.innerHTML=`<div class="ytcW"><div class="ytcH"><b>✂ 從 YouTube 抓這段</b><button data-x="1">✕</button></div>
<div class="ytcR"><label>從 <input id="ytcA" value="${ytcFmt(t-30)}"></label><label>到 <input id="ytcB" value="${ytcFmt(t+30)}"></label></div>
<div class="ytcR"><label style="flex:1">名稱（可不填） <input id="ytcN" maxlength="30" style="width:100%"></label></div>
<div class="ytcR ytcQ">${[["前後 30 秒",30,30],["前 1 分＋後 2 分",60,120],["後 5 分鐘",0,300]].map(([n,a,b])=>`<button class="pill" data-q="${a},${b}">${n}</button>`).join("")}</div>
<small>開播後的時間（時:分:秒）。只抓這一段，不整部下載；畫質約原檔 6～8 成。抓好的會在「剪好的」裡，可以再細剪；成品永久保留。</small>
<div class="ytcR" style="justify-content:flex-end"><span id="ytcMsg" class="sub grow"></span><button class="pill" data-x="1">取消</button><button class="pill on" data-go="1">✂ 開始抓</button></div></div>`;
  document.body.appendChild(o);
  o.onclick=async e=>{if(e.target===o||e.target.closest("[data-x]")){o.remove();return;}const q=e.target.closest("[data-q]");if(q){const [a,b]=q.dataset.q.split(",").map(Number);o.querySelector("#ytcA").value=ytcFmt(t-a);o.querySelector("#ytcB").value=ytcFmt(t+b);return;}
    if(e.target.closest("[data-go]")){const a=ytcParse(o.querySelector("#ytcA").value),b=ytcParse(o.querySelector("#ytcB").value),msg=o.querySelector("#ytcMsg");if(isNaN(a)||isNaN(b)){msg.textContent="時間格式：時:分:秒";return;}
      let j=await post("/api/pc/ytc/add",{sid,a,b,name:o.querySelector("#ytcN").value});
      if(j&&j.need_install){if(!confirm("第一次使用要先下載剪輯工具（yt-dlp＋Deno，約 60 MB，從官方 GitHub）。現在下載？"))return;await post("/api/pc/ytc/install",{});msg.textContent="下載剪輯工具中…";
        for(let k=0;k<300&&o.isConnected;k++){await new Promise(r=>setTimeout(r,2000));let I=null;try{I=await api("/api/pc/ytc/info");}catch(x){}if(!I)continue;msg.textContent=I.inst_msg||"";if(I.ready){j=await post("/api/pc/ytc/add",{sid,a,b,name:o.querySelector("#ytcN").value});break;}if(I.inst==="fail")return;}}
      if(!j||!j.ok){msg.textContent="✖ "+((j&&j.message)||"沒有成功");return;}o.remove();toast("✂ "+j.message);ytcWatch();}};}
async function ytcWatch(){if(ytcWatch.on)return;ytcWatch.on=true;try{for(let k=0;k<1800;k++){await new Promise(r=>setTimeout(r,2000));let I=null;try{I=await api("/api/pc/ytc/info");}catch(e){}if(!I)continue;
    const st=$("#hpState");if(I.cur&&st)st.textContent=`✂ 從 YouTube 抓片段：${I.cur.msg||""} ${I.cur.pct?Math.round(I.cur.pct)+"%":""}${I.q?` · 還有 ${I.q} 段排隊`:""}`;
    if(!I.cur&&!I.q){if(I.last)toast((I.last.ok?"✔ ":"✖ ")+I.last.message);break;}}}finally{ytcWatch.on=false;}}
function lowerBound(rows,t){let a=0,b=rows.length;while(a<b){const m=(a+b)>>1;if((+rows[m][2]||0)<t)a=m+1;else b=m;}return a;}
/* ================= 1 即時聊天室 · 2 禮物 · 4 進入紀錄 · 5 按讚 · 6 數據（目前選取的分頁的主播） ================= */
function streamPage(id,title,build){PAGES[id]={render(pg){pg.innerHTML=`<div class="pg fill"><div class="row"><h1 class="title">${title}</h1><span class="grow"></span><span class="sub" id="spWho"></span></div><div id="spT" style="flex:1;display:flex;flex-direction:column;min-height:0"></div></div>`;this.start();},
  start(){this.t=tabTarget();this.vt=build($("#spT"));this.n=-1;this.poll(true);},tab(){clearTimeout(this.pt);this.start();},leave(){clearTimeout(this.pt);},
  async poll(first){clearTimeout(this.pt);const t=this.t;if(!t){$("#spWho").textContent="沒有選取直播";return;}const D=await loadSess(t,id===6);if(this.t!==t||!$("#spT"))return;
    if(D&&D.meta){$("#spWho").textContent=(t.k==="hist"?"歷史 · ":"")+D.meta.name+"  @"+D.meta.u;this.vt.feed(D,first);}this.pt=setTimeout(()=>this.poll(false),t.k==="hist"?60000:1000);}};}
const TC=(k,t,w,o)=>Object.assign({t,w,k},o||{});
streamPage(1,"即時聊天室 Chat",host=>{const vt=new VT(host,{key:"chat",cols:[TC(1,"實際時間",100,{f:fmtClk,al:"c"}),TC(2,"直播時間",100,{f:fmtE,al:"c"}),TC(3,"@使用者",150),{t:"暱稱",w:160,v:nick},TC(5,"留言",650)]});
  vt.feed=(D,first)=>first?(vt.setRows(D.rows.c.slice()),vt.body.scrollTop=1e9):vt.push(D.added.c||[]);return vt;});
streamPage(2,"禮物 Gifts",host=>{const vt=new VT(host,{key:"gifts",cols:[TC(1,"實際時間",100,{f:fmtClk,al:"c"}),TC(2,"直播時間",100,{f:fmtE,al:"c"}),TC(3,"送禮者",150),{t:"暱稱",w:150,v:nick},TC(5,"禮物",160),TC(6,"數量",70,{al:"r"}),TC(7,"鑽石/件",90,{f:v=>v?num(v):"—",al:"r"}),TC(8,"鑽石合計",100,{f:v=>v?num(v):"—",al:"r"})]});
  vt.feed=(D,first)=>first?(vt.setRows(D.rows.g.slice()),vt.body.scrollTop=1e9):vt.push(D.added.g||[]);return vt;});
streamPage(4,"進入紀錄 Joins",host=>{const vt=new VT(host,{key:"joins",cols:[TC(1,"實際時間",100,{f:fmtClk,al:"c"}),TC(2,"直播時間",100,{f:fmtE,al:"c"}),TC(3,"@使用者",170),{t:"暱稱",w:200,v:nick},TC(5,"本場次數",100,{al:"c"})]});
  vt.feed=(D,first)=>{const jc=joinCounts(D.rows.j);if(first){vt.setRows(D.rows.j.map((r,i)=>r.slice(0,5).concat([jc[i]])));vt.body.scrollTop=1e9;}else{const b=D.rows.j.length-(D.added.j||[]).length;vt.push((D.added.j||[]).map((r,i)=>r.slice(0,5).concat([jc[b+i]])));}};return vt;});
streamPage(5,"按讚 Likes · 分段統計",host=>{const vt=new VT(host,{key:"likes",cols:[TC(0,"實際時間",100,{f:fmtClk,al:"c"}),TC(1,"直播時間",100,{f:fmtE,al:"c"}),TC(2,"@使用者",170),TC(3,"暱稱",200),TC(4,"本段按讚",100,{f:num,al:"r"}),TC(5,"房間累計讚",130,{f:v=>v==null?"—":num(v),al:"r"})]});
  vt.feed=(D)=>{const live=D.meta.live;const {act,closed}=likeSegments(D.rows.l,live);const m=s=>[s.first,s.ls,s.u,s.nick,s.sum,s.room];const rows=act.map(m);if(act.length||closed.length)rows.push({__sep:1,text:"──────── 已結算紀錄 ────────"});closed.forEach(s=>rows.push(m(s)));
    const sig=D.rows.l.length+":"+act.length;if(vt._sig!==sig||live){vt._sig=sig;const st=vt.body.scrollTop;vt.setRows(rows);vt.body.scrollTop=st;}};return vt;});
/* V0.6.53 6 數據頁已移除 */

/* ================= 7 歷史直播場次 ================= */
PAGES[7]={render(pg,arg){this.uf=typeof arg==="string"?arg:"";pg.innerHTML=`<div class="pg fill"><div class="row"><h1 class="title">歷史直播場次</h1><select id="seCat" style="display:none"></select><span class="grow"></span>
<button onclick="go(58)" title="同一場直播被程式重開、斷電切成好幾段 → 合成一場（影片照時間接著播，不重新輸出）">⧉ 合併重複場次</button><button disabled title="請在電腦本機操作">🩺 重整並統計場次</button><button id="seSA" title="找出時長不合理的場次（例如顯示 20 多小時），用最後一筆資料推算正確時長，勾選後修正（可復原）">⏱ 偵測場次異常</button><button disabled title="請在電腦本機操作">🗂 整理影片檔名</button><button disabled title="會刪除檔案，請在電腦本機操作">🧹 清理影片／錄音檔</button></div>
<div class="hero row" id="seF" style="display:none"><b id="seFT"></b><span class="grow"></span><button id="seFX">✕ 顯示全部主播</button></div><div id="seT" style="flex:1;display:flex;flex-direction:column;min-height:0"></div>
<div class="panel" id="seC" style="display:none;margin-top:6px;flex:none"><div class="bt"><span id="seCT">場次圖表</span><span class="grow"></span><span class="sub">灰色虛線＝已開播還沒監控（推算）· 線＝人流 · 點＝高價禮物　設定 → 歷史場次圖表 可調</span></div><canvas id="seCv" style="width:100%;height:80px;display:block"></canvas></div></div>`;
    this.vt=new VT($("#seT"),{key:"sessions",sort:this.uf?[3,true]:[3,true],cols:[TC(0,"ID",62,{al:"c"}),TC(1,"主播",125),TC(2,"暱稱",145),TC(3,"開播（TikTok）",145,{al:"c"}),TC(4,"結束",145,{al:"c"}),TC(5,"直播總時長",90,{al:"c"}),TC(6,"錄製時長",90,{al:"c"}),TC(7,"錄製區間",105,{al:"c"}),TC(8,"鑽石",85,{al:"r"}),TC(9,"按讚",75,{al:"r"}),TC(10,"累積觀眾",95,{al:"r"}),TC(11,"留言",75,{al:"r"}),TC(12,"狀態",85,{al:"c"}),TC(13,"MP4",85,{al:"r",css:r=>r[13]==="轉檔中"?"color:#fff;background:#c62845;font-weight:800;text-align:center":""}),TC(14,"剪輯",80,{al:"c",css:r=>r[14]?"color:#3fb6f2;font-weight:800":""}),TC(15,"字幕",60,{al:"c",css:r=>r[15]?"color:#f5a524;font-weight:800":""})],
      onDbl:r=>openHist(+r[0],r[2],r[5]),onCtx:(r,e)=>this.ctx(r,e)});
    $("#seSA").onclick=()=>saOpen();$("#seT").addEventListener("click",()=>setTimeout(()=>this.chart(),0));new ResizeObserver(()=>this.drawC()).observe($("#seC"));
    $("#seFX").onclick=()=>{this.uf="";this.load();};$("#seCat").onchange=e=>{this.cat=e.target.value;this.filter();this.load();};
    {const inp=$("#seT input");this.sq="";if(inp)inp.addEventListener("input",()=>{clearTimeout(this.sqt);this.sqt=setTimeout(()=>{const v=inp.value.trim();if(v!==this.sq){this.sq=v;this.load();}},450);});}   // V0.6.52 搜尋主播＝找資料庫裡那些主播的全部場次
    this.load();},
  async load(){$("#seF").style.display=this.uf?"flex":"none";if(this.uf)$("#seFT").textContent=`只顯示：${this.uf}　（最近一場在最上面）`;
    const sq=this.uf?"":(this.sq||""),cat=this.uf?"":(this.cat||""),j=await api("/api/pc/sessions?u="+encodeURIComponent(this.uf||"")+"&q="+encodeURIComponent(sq)+"&cat="+encodeURIComponent(cat));if(!$("#seT"))return;if(sq!==(this.uf?"":(this.sq||""))||cat!==(this.uf?"":(this.cat||"")))return;this.all=j.rows||[];this.of=j.of||{};{const ed=j.ed||{};const sr=new Set((j.srt||[]).map(Number));for(const r of this.all){const n=ed[String(+r[0])];r[14]=n?`✂ ${n} 段`:"";r[15]=sr.has(+r[0])?"SRT":"";}}
    sb(sq||cat?`${sq?`搜尋「${sq}」`:""}${cat?" 分類篩選":""}：找到 ${this.all.length} 場（全部場次，不受「最近 N 場」限制）`:"");      // V0.6.54
    const cb=$("#seCat"),cats=j.cats||[];cb.innerHTML=`<option value="">全部分類</option><option value="none">○ 未分類</option>`+cats.map(c=>`<option value="${c.id}">● ${esc(c.name)}</option>`).join("");cb.value=this.cat||"";cb.style.display=cats.length?"":"none";this.filter();
    clearTimeout(this.pt);this.pt=setTimeout(()=>this.load(),20000);},
  filter(){const f=$("#seCat").value;this.vt.setRows(this.all.filter(r=>!f||(f==="none"?!this.of[r[1]]:this.of[r[1]]===f)));},
  leave(){clearTimeout(this.pt);},
  async chart(){const r=this.vt.selected()[0];if(!r)return;const id=+r[0];this.cid=id;$("#seCT").textContent=`#${String(id).padStart(5,"0")}　${r[2]}　${r[3]}`;
    try{const j=await api("/api/hchart?ids="+id);if(this.cid!==id)return;this.cc=j.cfg||{};this.cd=(j.items||{})[id];
      const on=this.cc.enabled!==false&&this.cd;$("#seC").style.display=on?"":"none";if(on){$("#seCv").style.height=Math.max(60,(+this.cc.height||64)+24)+"px";this.drawC();}}catch(e){}},
  drawC(){const cv=$("#seCv");if(cv&&this.cd&&this.cc)hcDraw(cv,this.cd,this.cc,{sub:getComputedStyle(document.documentElement).getPropertyValue("--subtext")});},
  ctx(r,e){const sel=this.vt.selected();const ids=(sel.length>1&&sel.includes(r)?sel:[r]).map(x=>+x[0]);
    menu([ids.length===1?{label:"🔍 查看這一場",act:()=>openHist(+r[0],r[2],r[5])}:null,ids.length===1?{label:"✂ 剪輯這一場",act:()=>edOpen(+r[0])}:null,catSub(r[1]),{sep:1},{label:ids.length>1?`✖ 刪除 ${ids.length} 場`:"✖ 刪除這一場",act:async()=>{
      const lab=ids.slice(0,8).map(i=>"#"+String(i).padStart(5,"0")).join("、")+(ids.length>8?` 等 ${ids.length} 場`:"");
      if(!await confirmSteps([["刪除場次（1/2）",`確定要刪除 ${lab} 嗎？\n\n這些場次的留言、禮物、按讚、觀眾紀錄都會從歷史資料刪除（錄音檔與 LOG 資料夾不會刪）。刪除前會自動備份資料庫。`,["del","cancel"]],["刪除場次（2/2）",`最後確認：刪除 ${lab}？`,["cancel","del"]]]))return;
      const j=await post("/api/pc/sessions/delete",{ids});if(!j.ok)dialog("刪除場次",esc(j.message||"刪除失敗"));else{toast("✔ 已刪除");this.load();}}},
      ids.length===1?{label:`🎞 刪除這場直播的 MP4（紀錄、錄音保留）`,act:()=>delVidPC(String(r[1]).replace(/^@/,""),+r[0],()=>this.load())}:null,
      {label:`🎞 刪除 @${r[1]} 所有 MP4（紀錄、錄音保留）`,act:()=>delVidPC(String(r[1]).replace(/^@/,""),0,()=>this.load())},
      {label:`⛔ 刪除直播間所有訊息（@${r[1]} 全部紀錄＋檔案，移除監控）`,act:()=>purgePC(String(r[1]).replace(/^@/,""),()=>this.load())}],e.clientX,e.clientY);}};
/* V0.6.22 只刪影片：這一場或這位主播全部；聊天、禮物、觀眾紀錄、錄音保留 */
async function delVidPC(u,sid,after){const inf=await api(`/api/pc/streamer/media_info?u=${encodeURIComponent(u)}&sid=${sid||0}`);if(!inf||inf.error){dialog("刪除影片",esc((inf&&inf.error)||"讀取失敗"));return;}
  const x=sid?inf.one:inf.all,nm=inf.name||u;if(sid&&x.busy){dialog("刪除影片","這一場還在直播／錄影中，不能刪除影片。");return;}if(!x.n){dialog("刪除影片","找不到可以刪的影片檔。");return;}
  const what=(sid?`#${String(sid).padStart(5,"0")} 這一場`:`「${nm}」全部 ${x.sessions} 場`)+`的影片 ${x.n} 個（${((x.bytes||0)/1e9).toFixed(2)} GB）`;
  if(!await confirmSteps([["刪除影片（1/3）",`要刪除 ${what} 嗎？\n\n聊天、禮物、觀眾紀錄和錄音（M4A）都會保留。`,["del","cancel"]],["刪除影片（2/3）","再確認一次：影片刪除後沒辦法還原。",["cancel","del"]],["刪除影片（3/3）",`最後確認：刪除 ${what}？`,["cancel","keep","del"]]]))return;
  const j=await post("/api/pc/streamer/del_videos",{u,sid:sid||0});if(!j.ok){dialog("刪除影片",esc(j.message||"沒有成功"));return;}
  toast("🎞 正在背景刪除影片…");
  for(let i=0;i<3600;i++){await new Promise(r=>setTimeout(r,1500));let st;try{st=await api("/api/pc/streamer/purge_status");}catch(e){continue;}
    if(st.running){$("#sbMsg").textContent=`刪除影片：${st.stage||""}${st.total?` ${st.done}/${st.total}`:""}`;continue;}
    const r=st.result||{};toast(`✔ 已刪除 ${r.files||0} 個影片（${((r.bytes||0)/1e9).toFixed(2)} GB）`+(r.errors&&r.errors.length?`，${r.errors.length} 個沒刪掉`:""));$("#sbMsg").textContent="";if(after)after();break;}}
/* V0.6.21 刪除主播（全部）：三次確認（按鈕位置不同），背景刪除並顯示進度 */
async function purgePC(u,after){const inf=await api("/api/pc/streamer/purge_info?u="+encodeURIComponent(u));if(!inf||inf.error){dialog("刪除主播",esc((inf&&inf.error)||"讀取失敗"));return;}
  const nm=inf.name||u,what=`${inf.sessions} 場直播、${num(inf.comments)} 則留言、${num(inf.gifts)} 筆禮物（💎 ${num(inf.diamonds)}）、${num(inf.viewers)} 位觀眾在這位主播的紀錄（送禮者累計會扣掉）、${inf.files} 個影片／錄音檔（${((inf.bytes||0)/1e9).toFixed(2)} GB）`+(inf.in_roster?"，並從主播清單移除、停止監控":"");
  if(!await confirmSteps([["刪除主播（1/3）",`要刪除「${nm}　@${u}」嗎？\n\n會一起刪掉：${what}。`,["del","cancel"]],["刪除主播（2/3）",`再確認一次：刪除後沒辦法還原。`,["cancel","del"]],["刪除主播（3/3）",`最後確認：真的要把「${nm}　@${u}」全部刪掉？`,["cancel","keep","del"]]]))return;
  const j=await post("/api/pc/streamer/purge",{u});if(!j.ok){dialog("刪除主播",esc(j.message||"沒有成功"));return;}
  toast(`🗑 正在背景刪除「${nm}」的全部紀錄…`);
  for(let i=0;i<3600;i++){await new Promise(r=>setTimeout(r,1500));let st;try{st=await api("/api/pc/streamer/purge_status");}catch(e){continue;}
    if(st.running){$("#sbMsg").textContent=`刪除「${nm}」：${st.stage||""}${st.total?` ${st.done}/${st.total}`:""}`;continue;}
    const r=st.result||{};toast(`✔ 已刪除「${nm}」：${r.sessions||0} 場、${num(r.rows||0)} 筆紀錄、${r.files||0} 個檔案`+(r.errors&&r.errors.length?`（${r.errors.length} 個沒刪掉）`:""));$("#sbMsg").textContent="";if(after)after();break;}}
/* ================= 3 送禮者 ================= */
PAGES[3]={render(pg){pg.innerHTML=`<div class="pg fill" id="gfP"></div>`;this.list();},
  /* V0.6.17 送禮者分頁：先載入 500 位，捲到底再載入 500 位；點欄位標題（帳號／暱稱／場次／禮物／鑽石）由電腦端排序；搜尋找全部送禮者 */
  async list(){const el=$("#gfP"),self=this;el.innerHTML=`<h1 class="title">送禮者 Gifters · 永久個人檔案</h1><div class="row" style="margin-bottom:6px"><input id="gfQ" placeholder="搜尋全部送禮者：暱稱 / @帳號 / 主播…" style="width:320px" value="${esc(this.q||"")}"><span class="sub" id="gfN" style="margin-left:10px">讀取中…</span><span class="grow"></span><span class="sub">點欄位標題排序 · 捲到底自動載入更多</span></div><div id="gfT" style="flex:1;display:flex;flex-direction:column;min-height:0"></div>`;
    const SK={1:"user",2:"name",3:"sess",4:"gifts",5:"dia"};this.srt=this.srt||[5,true];
    const vt=new VT($("#gfT"),{key:"gifters2",filter:false,sort:this.srt,cols:[{t:"",w:30,v:r=>r[1],html:v=>`<img class="vav" loading="lazy" src="${B}/gav/${encodeURIComponent(v)}.jpg" onerror="this.style.visibility='hidden'">`},TC(1,"@使用者",155),TC(2,"暱稱",160),TC(3,"直播場次",85,{al:"r"}),TC(4,"累計禮物",95,{f:num,al:"r"}),TC(5,"累計 Diamonds",125,{f:num,al:"r"}),TC(6,"主要禮物",300),TC(7,"送禮直播主",360)],
      onSort:(ci,desc)=>{if(!SK[ci])return false;self.srt=[ci,desc];self.load(true);return true;},
      onScroll:v=>{if(v.body.scrollTop+v.body.clientHeight>=v.body.scrollHeight-v.o.rowH*40)self.load(false);},
      onDbl:r=>this.detail(r[1]),onCtx:(r,e)=>menu([{label:`🔍 查看送禮紀錄（@${r[1]}）`,act:()=>this.detail(r[1])},{label:"📛 暱稱變更紀錄",act:()=>this.names(r[1],r[2])}],e.clientX,e.clientY)});
    vt._srv=true;this.vt=vt;this.SK=SK;let qt=null;$("#gfQ").oninput=e=>{this.q=e.target.value;clearTimeout(qt);qt=setTimeout(()=>this.load(true),350);};
    this.load(true);},
  async load(reset){const vt=this.vt;if(!vt||!$("#gfT"))return;if(!reset&&(this.busy||vt.rows.length>=(this.tot||0)))return;
    const gen=this.gen=(this.gen||0)+(reset?1:0),off=reset?0:vt.rows.length,[ci,desc]=this.srt||[5,true];this.busy=true;
    if(!reset)$("#gfN").textContent=`載入中… 已載入 ${num(off)} / ${num(this.tot)} 位`;
    try{const j=await api(`/api/pc/gifters?off=${off}&n=500&sort=${this.SK[ci]||"dia"}&desc=${desc?1:0}&q=${encodeURIComponent((this.q||"").trim())}`);
      if(gen!==this.gen||this.vt!==vt)return;if(j.error)throw new Error(j.error);this.tot=+j.total||0;
      if(reset){vt.setRows(j.rows||[]);vt.body.scrollTop=0;}else{for(const r of j.rows||[])vt.rows.push(r);if(vt._srv){vt.view=vt.rows.map((_,i)=>i);vt.paint(true);}else vt.refresh();}
      $("#gfN").textContent=`${num(this.tot)} 位送禮者${(this.q||"").trim()?"（搜尋全部）":""} · 💎 ${num(j.sum||0)} · 已載入 ${num(vt.rows.length)} 位`;}
    catch(e){$("#gfN").textContent="讀取失敗："+(e.message||e);}
    finally{if(gen===this.gen)this.busy=false;}},
  async detail(u){const el=$("#gfP");el.innerHTML=`<div class="row"><h1 class="title" id="gdT">觀眾詳細：@${esc(u)}</h1><span class="grow"></span><button id="gdB">← 返回送禮者</button></div><div class="sub" id="gdS">讀取中…</div><div class="sub" id="gdN" style="margin:4px 0"></div><div id="gdUA"></div><div id="gdC" class="row wrap" style="gap:6px;margin:4px 0"></div><div id="gdTb" style="flex:1;display:flex;flex-direction:column;min-height:0"></div><div id="gdUL" class="uaL" style="flex:1;display:none"></div>`;
    $("#gdB").onclick=()=>this.list();
    uaMount($("#gdUA"),$("#gdUL"),u,k=>{const g=k==="gifts";$("#gdC").style.display=g?"":"none";$("#gdTb").style.display=g?"flex":"none";$("#gdUL").style.display=g?"none":"block";$("#gdS").style.display=g?"":"none";},(sid,ts,h)=>openHist(sid,h,null,ts));   // V0.6.52
    const vt=new VT($("#gdTb"),{key:"gifter",cols:[TC(0,"日期時間",180,{f:v=>{const d=new Date((+v||0)*1000);return d.toLocaleDateString()+" "+fmtClk(v);}}),TC(1,"場次",70,{f:v=>v?String(v).padStart(5,"0"):"—",al:"c"}),TC(2,"主播暱稱",240),TC(3,"禮物",300),TC(4,"數量",90,{al:"r"}),TC(5,"價值 Diamonds",140,{f:num,al:"r"})],
      onDbl:r=>r[1]&&openHist(r[1],r[2],null,r[0]),onCtx:(r,e)=>r[1]&&menu([{label:`▶ 從這個禮物 +3 秒開始播（場次 ${String(r[1]).padStart(5,"0")}）`,act:()=>openHist(r[1],r[2],null,r[0])},{label:`🔍 開啟歷史紀錄（場次 ${String(r[1]).padStart(5,"0")} 的分頁）`,act:()=>openHist(r[1],r[2])},{label:"✂ 剪輯這一場",act:()=>edOpen(+r[1])}],e.clientX,e.clientY)});
    const j=await api("/api/pc/gifter?u="+encodeURIComponent(u));const R=j.rows||[];this.gd={R,vt,off:new Set()};this.gdMode=this.gdMode||LS.get("gfmode","sess");this.gdDraw();$("#gdT").innerHTML=`<img class="vav big" src="${B}/gav/${encodeURIComponent(u)}.jpg" onerror="this.remove()"> 觀眾詳細：${esc(j.nick||u)}  @${esc(u)}`;$("#gdN").innerHTML=gNamesHtml(j.names);
    if(!R.length){$("#gdS").textContent="這位沒有送過禮；上面可以看他的留言、點讚、進場等全部紀錄。";return;}
    const n=R.reduce((a,r)=>a+(+r[4]||0),0),d=R.reduce((a,r)=>a+(+r[5]||0),0),st=new Set(R.map(r=>r[2]));const f=t=>{const x=new Date(t*1000);return x.toLocaleDateString()+" "+fmtClk(t);};
    $("#gdS").textContent=`共 ${num(R.length)} 筆送禮事件｜${num(n)} 件禮物｜${num(d)} Diamonds｜涉及 ${st.size} 位主播｜首次 ${f(R[0][0])}｜最後 ${f(R[R.length-1][0])}`;},
  /* V0.6.31 依場次（新→舊）／依金額（不分場次）／依直播間；勾選只看哪些直播間 */
  gdDraw(){const D=this.gd;if(!D||!$("#gdC"))return;const M=this.gdMode,vt=D.vt,self=this,hosts={};
    for(const r of D.R){const h=r[2]||"（不明）";(hosts[h]=hosts[h]||{n:0,d:0}).n++;hosts[h].d+=(+r[5]||0);}
    const HN=Object.entries(hosts).sort((a,b)=>b[1].d-a[1].d);
    $("#gdC").innerHTML=[["sess","依場次 新→舊"],["amt","依金額 大→小"],["host","依直播間"]].map(([k,x])=>`<button data-gm="${k}"${M===k?' class="start"':""}>${x}</button>`).join("")+`<span class="sub" style="margin-left:10px">直播間：</span>`+
      HN.map(([h,x])=>`<label style="display:inline-flex;align-items:center;gap:4px;margin-right:8px;font-size:12.5px"><input type="checkbox" data-h="${esc(h)}"${D.off.has(h)?"":" checked"}>${esc(h)} <span class="sub">💎 ${num(x.d)}</span></label>`).join("")+(HN.length>1?`<button data-ha="1">全選</button><button data-ha="0">全不選</button>`:"");
    $("#gdC").querySelectorAll("[data-gm]").forEach(b=>b.onclick=()=>{self.gdMode=b.dataset.gm;LS.set("gfmode",self.gdMode);self.gdDraw();});
    $("#gdC").querySelectorAll("[data-h]").forEach(c=>c.onchange=()=>{c.checked?D.off.delete(c.dataset.h):D.off.add(c.dataset.h);self.gdDraw();});
    $("#gdC").querySelectorAll("[data-ha]").forEach(b=>b.onclick=()=>{if(b.dataset.ha==="1")D.off.clear();else HN.forEach(([h])=>D.off.add(h));self.gdDraw();});
    const rows=D.R.filter(r=>!D.off.has(r[2]||"（不明）"));let out=[];
    if(M==="amt"){out=rows.slice().sort((a,b)=>(+b[5]||0)-(+a[5]||0)||b[0]-a[0]);vt.sort=[5,true];}
    else{const G=new Map(),key=r=>M==="host"?(r[2]||"（不明）"):String(r[1]||0);
      for(const r of rows){const k=key(r);if(!G.has(k))G.set(k,{rows:[],d:0,t:0,h:r[2],sid:r[1]});const g=G.get(k);g.rows.push(r);g.d+=(+r[5]||0);g.t=Math.max(g.t,+r[0]||0);}
      for(const g of [...G.values()].sort((a,b)=>M==="host"?b.d-a.d:b.t-a.t)){g.rows.sort((a,b)=>b[0]-a[0]);
        out.push({__sep:1,text:M==="host"?`${g.h||"（不明）"}　${g.rows.length} 筆　💎 ${num(g.d)}`:`#${String(g.sid||0).padStart(5,"0")}　${g.h||""}　${new Date(g.t*1000).toLocaleDateString()}　💎 ${num(g.d)}`});out.push(...g.rows);}
      vt.sort=null;}
    vt._srv=false;vt.header();vt.setRows(out);}};
/* ================= 8 使用者 ================= */
PAGES[8]={async render(pg){pg.innerHTML=`<div class="pg fill"><div class="row"><h1 class="title">使用者 Profiles</h1><span class="grow"></span><span class="sub">點兩下一位使用者：看他所有的留言、禮物、點歌、點讚、進場，還能匯出給 AI 分析</span></div><div id="prT" style="flex:1;display:flex;flex-direction:column;min-height:0"></div></div>`;
  const open=u=>{go(3);setTimeout(()=>PAGES[3].detail(u),60);};
  const vt=new VT($("#prT"),{key:"profiles",cols:[TC(0,"@使用者",170),TC(1,"暱稱",200),TC(2,"出現場次",100,{f:num,al:"r"}),TC(3,"留言",100,{f:num,al:"r"}),TC(4,"Join",100,{f:num,al:"r"}),TC(5,"禮物",100,{f:num,al:"r"}),TC(6,"Diamonds",130,{f:num,al:"r"})],
    onDbl:r=>open(r[0]),onCtx:(r,e)=>menu([{label:`🔍 看 @${r[0]} 的全部活動`,act:()=>open(r[0])},{label:"📥 匯出給 AI 分析（文字檔）",act:()=>{location.href=B+"/api/pc/uact/export?u="+encodeURIComponent(r[0]);}}],e.clientX,e.clientY)});
  const j=await api("/api/pc/profiles");vt.setRows(j.rows||[]);}};
/* ================= 12 錄音／錄影 ================= */
PAGES[12]={render(pg){pg.innerHTML=`<div class="pg fill"><div class="row"><h1 class="title">錄音／錄影</h1><span class="grow"></span><b id="exLive"></b></div>
<div class="sub">每個已連線的直播各自錄一路音訊（下播後轉成 M4A）；錄影開啟時同時錄影片（新版先存 SSD，下播後在 SSD 轉 MP4 再搬到影片資料夾）。開關與畫質在 設定 → 錄音。</div>
<div class="panel" style="flex:45;display:flex;flex-direction:column;min-height:0"><div class="row"><span class="sec">錄製中</span><span class="grow"></span><span class="sub" id="exVid"></span></div><div id="exA" style="flex:1;display:flex;flex-direction:column;min-height:0"></div></div>
<div class="panel" style="flex:35;display:flex;flex-direction:column;min-height:0"><div class="row"><span class="sec">最近完成</span></div><div id="exD" style="flex:1;display:flex;flex-direction:column;min-height:0"></div></div>
<div class="panel" style="flex:20;display:flex;flex-direction:column;min-height:0"><span class="sec">事件紀錄</span><div class="log" id="exL" style="flex:1;color:#bfeeff;background:#0a0e13"></div></div></div>`;
    this.a=new VT($("#exA"),{key:"exA",filter:false,cols:[TC(0,"主播",150),TC(1,"@帳號",150),TC(2,"場次",60,{al:"c"}),TC(3,"開始錄製",90,{al:"c"}),TC(4,"已錄時長",90,{al:"c"}),TC(5,"音訊大小",90,{al:"r"}),TC(6,"音訊狀態",130),TC(7,"影片",130),TC(8,"影片大小",95,{al:"r"}),TC(9,"下載速度",95,{al:"r"}),TC(10,"畫面大小",170)]});
    this.d=new VT($("#exD"),{key:"exD",filter:false,cols:[TC(0,"主播",150),TC(1,"@帳號",150),TC(2,"場次",60,{al:"c"}),TC(3,"完成時間",140,{al:"c"}),TC(4,"音訊大小",90,{al:"r"}),TC(5,"音訊",240),TC(6,"影片",260)],
      onDbl:r=>+r[2]&&openHist(+r[2],r[0]),onCtx:(r,e)=>+r[2]&&menu([{label:`🔍 查看歷史紀錄（開啟場次 ${r[2]} 的分頁）`,act:()=>openHist(+r[2],r[0])},{label:"✂ 剪輯這一場",act:()=>edOpen(+r[2])}],e.clientX,e.clientY)});
    this.poll();},leave(){clearTimeout(this.pt);},
  async poll(){const j=await api("/api/pc/rec");if(!$("#exA"))return;$("#exLive").textContent=j.live_state;$("#exVid").textContent=j.video_state;this.a.setRows(j.active);if(this.d.rows.length!==j.done.length||JSON.stringify(this.d.rows[0])!==JSON.stringify(j.done[0]))this.d.setRows(j.done);
    const L=$("#exL"),end=L.scrollTop+L.clientHeight>=L.scrollHeight-20;if(L.textContent!==j.log){L.textContent=j.log;if(end)L.scrollTop=1e9;}this.pt=setTimeout(()=>this.poll(),2000);}};
/* ================= 19 FLV 待處理 ================= */
PAGES[19]={render(pg){pg.innerHTML=`<div class="pg fill"><h1 class="title">FLV 待處理</h1><div class="sub" id="fvIntro">這裡列出所有還沒轉成 MP4 的 FLV（以前累積的、轉檔失敗的）。程式<b>不會自動</b>處理它們，勾選後按「處理勾選的」才會開始；其餘放著不動。處理方式：FLV 從 HDD 一次複製到 SSD → 在 SSD 轉 MP4（同時複製下一部）→ MP4 一次搬回 HDD，確認無誤才刪 HDD 上的 FLV。</div>
<div class="panel" style="flex:1;display:flex;flex-direction:column;min-height:0"><div class="row wrap"><button id="fvAll">全選</button><button id="fvNone">全不選</button><button id="fvR">↻ 重新整理</button><span class="grow"></span><span class="sub" id="fvSel"></span><button id="fvP">⏸ 暫停</button><button id="fvC" title="勾選的場次（沒勾就是正在做的那部）停止處理，FLV 留在原處、場次留在清單">✖ 取消工作</button><button class="start" id="fvGo">▶ 處理勾選的</button></div>
<div id="fvT" style="flex:1;display:flex;flex-direction:column;min-height:0;margin-top:6px"></div><div class="sub" id="fvLane" style="margin-top:6px;line-height:1.6"></div></div></div>`;
    this.chk=new Set();const self=this;
    this.vt=new VT($("#fvT"),{key:"flv",filter:false,cols:[{t:"",w:32,v:r=>r.dir,html:v=>`<input type="checkbox" data-d="${esc(v)}"${self.chk.has(v)?" checked":""}>`,al:"c"},{t:"主播",w:200,v:r=>r.name!==r.u?r.name+"  @"+r.u:"@"+r.u},{t:"場次",w:70,v:r=>r.sid?String(r.sid).padStart(5,"0"):"",al:"c"},{t:"開播時間",w:140,v:r=>r.live,al:"c"},{t:"FLV",w:50,v:r=>r.n||"",al:"c"},{t:"大小",w:100,v:r=>r.bytes,f:fmtB,al:"r"},{t:"位置",w:80,v:r=>r.ssd?"SSD（C）":"HDD",al:"c"},{t:"狀態",w:360,v:r=>((self.st&&self.st.jobs[r.dir])||{}).text||""}],
      onDbl:r=>{self.chk.has(r.dir)?self.chk.delete(r.dir):self.chk.add(r.dir);self.vt.paint(true);self.sel();}});
    $("#fvT").addEventListener("change",e=>{const d=e.target.dataset.d;if(d==null)return;e.target.checked?this.chk.add(d):this.chk.delete(d);this.sel();});
    $("#fvAll").onclick=()=>{this.vt.view.forEach(i=>this.chk.add(this.vt.rows[i].dir));this.vt.paint(true);this.sel();};$("#fvNone").onclick=()=>{this.chk.clear();this.vt.paint(true);this.sel();};$("#fvR").onclick=()=>this.load();
    $("#fvP").onclick=async()=>{const j=await post("/api/pc/flv/pause",{on:!(this.st&&this.st.paused)});if(j.ok){this.st.paused=j.paused;this.lane();}};
    $("#fvC").onclick=async()=>{const j=await post("/api/pc/flv/cancel",{dirs:[...this.chk]});toast(j.ok?`已取消 ${j.n||0} 場（FLV 留在原處）`:"✖ "+(j.message||"沒有成功"));this.status();};
    $("#fvGo").onclick=async()=>{if(!this.chk.size){toast("先勾選要處理的場次");return;}const j=await post("/api/pc/flv/go",{dirs:[...this.chk]});if(j.ok){toast(`開始處理 ${j.n} 場`);this.chk.clear();this.status();}else toast("✖ "+(j.message||"沒有成功"));};
    this.load();},leave(){clearTimeout(this.pt);},
  async load(){$("#fvSel").textContent="掃描中…";const j=await api("/api/pc/flv");if(!$("#fvT"))return;this.st=j;this.vt.setRows(j.rows||[]);this.sel();this.lane();clearTimeout(this.pt);this.pt=setTimeout(()=>this.status(),1500);},
  async status(){clearTimeout(this.pt);let j;try{j=await api("/api/pc/flv/status");}catch(e){}if(!$("#fvT"))return;if(j){const doneNow=Object.values(j.jobs).some(x=>(x.state==="done"||x.state==="failed")&&Date.now()/1000-x.t<2);this.st=Object.assign(this.st||{},j);this.vt.paint(true);this.lane();if(doneNow){this.load();return;}}this.pt=setTimeout(()=>this.status(),1500);},
  sel(){const R=(this.vt.rows||[]).filter(r=>this.chk.has(r.dir)),b=R.reduce((a,r)=>a+r.bytes,0),tot=(this.vt.rows||[]).reduce((a,r)=>a+r.bytes,0);const st=this.st||{};const hdd=st.hdd||110e6,conv=st.conv||250e6;
    $("#fvSel").textContent=`共 ${this.vt.rows.length} 場 · ${fmtB(tot)}　｜　勾選 ${R.length} 場 · ${fmtB(b)}`+(R.length?` · 預估約 ${fmtDur(Math.max(2*b/hdd,b/conv)+10*R.length)}`:"");},
  lane(){const s=this.st||{};$("#fvP").textContent=s.paused?"▶ 繼續":"⏸ 暫停";const pr=s.prog;let h="<b>硬碟工作：</b>";
    h+=s.cur?`${s.cur[0]==="publish"?"搬回 HDD":"複製到 SSD"} ${esc(String(s.cur[1]).split(/[\\/]/).pop())}`+(pr?`（${(pr.done/Math.max(1,pr.total)*100).toFixed(0)}%，${fmtB(pr.done)} / ${fmtB(pr.total)}）`:"")+(s.paused?"　<span style='color:#f0ad4e'>⏸ 暫停中</span>":""):(s.paused?"⏸ 暫停中":"閒置");
    h+=`<br>SSD → HDD 傳輸速度：${s.io_pct>=100?"不限速":(s.io_pct||30)+"%（約 "+fmtR(s.io_rate)+"，穩定傳輸）"}（設定 → 錄音），目前實際 ${fmtR(s.io_now||0)}，E 槽現在忙碌 ${Math.round(s.busy||0)}%<br>等著搬回 HDD ${s.pub||0} 個 · 等著複製到 SSD ${s.fetch||0} 個 · HDD 實測 ${fmtR(s.hdd)} · SSD 轉檔約 ${fmtR(s.conv)}<br>`+(s.ssd?`SSD 工作資料夾：${esc(s.ssd)}（剩 ${fmtB(s.ssd_free)}）`:`<span style="color:#f0ad4e">沒有使用 SSD 暫存（${esc(s.ssd_off||"")}），會直接在原硬碟轉檔。</span>`);$("#fvLane").innerHTML=h;}};

function gNamesHtml(N){if(!N||!N.length)return "";const f=t=>new Date(t*1000).toLocaleString("zh-TW",{year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit"});
  if(N.length===1)return `📛 暱稱沒有改過（從 ${f(N[0].first)} 開始）`;
  return `<b>📛 暱稱改過 ${N.length-1} 次</b>（新 → 舊）：`+N.map((x,i)=>`<span style="margin-right:14px">${i?"":"<b style='color:#45d483'>現在</b> "}<b>${esc(x.nick)}</b> ${f(x.first)}～${f(x.last)}${x.src!=="直播"?"（"+esc(x.src)+"）":""}</span>`).join("");}
PAGES[3].names=async function(u,n){let j;try{j=await api("/api/pc/gifter?names=1&u="+encodeURIComponent(u));}catch(e){return;}dialog(`📛 ${n||u} @${u} 的暱稱紀錄`,`<div style="line-height:1.9">${gNamesHtml(j.names).replace(/<span/g,"<div").replace(/<\/span>/g,"</div>")||"沒有暱稱紀錄"}</div>`);};
/* ================= 20 影片庫重整（只看：搬檔案請在電腦本機操作） ================= */
PAGES[20]={render(pg){pg.innerHTML=`<div class="pg fill"><div class="row"><h1 class="title">影片庫重整（BETA）</h1><span class="grow"></span><button id="ltR">↻ 重新掃描</button><button disabled title="會搬移／改名檔案，請在電腦本機操作">▶ 整理勾選的</button></div>
<div class="sub" id="ltI">讀取中…</div><div class="sub" id="ltTop" style="margin:6px 0"></div><div id="ltT" style="flex:1;display:flex;flex-direction:column;min-height:0"></div></div>`;
    this.vt=new VT($("#ltT"),{key:"libtidy",cols:[{t:"類型",w:110,k:"k"},{t:"主播",w:170,k:"n"},{t:"場次",w:60,k:"s",al:"c"},{t:"原本",w:330,k:"a"},{t:"整理後",w:330,k:"b"},{t:"說明",w:360,k:"note"}]});
    $("#ltR").onclick=()=>this.load(true);this.load(false);},
  async load(fresh){$("#ltI").textContent="掃描中…";let j;try{j=await api("/api/pc/libtidy"+(fresh?"?fresh=1":""));}catch(e){$("#ltI").textContent="讀取失敗";return;}if(!$("#ltT"))return;
    $("#ltI").innerHTML=`影片庫：<b>${esc(j.root||"")}</b>　新規則：${j.v2?'<b style="color:#45d483">已啟用</b>':'<b style="color:#f0ad4e">還沒啟用</b>（在電腦本機 實驗工作區 → 影片庫重整 勾選）'}　沒分類的主播放到：<b>${esc(j.default_cat||"最上層")}</b>　· 搬檔案請在電腦本機操作`;
    const col={ok:"#45d483",old:"#f0ad4e",temp:"#8a8fa0",file:"#f0ad4e"};$("#ltTop").innerHTML="最上層："+(j.top||[]).map(x=>`<span style="color:${col[x.st]||"inherit"}">${x.st==="file"?"📄":"📁"} ${esc(x.name)}</span>`).join("　");
    const root=(j.root||"").toLowerCase(),sh=x=>{x=String(x||"");return x.toLowerCase().startsWith(root)?x.slice(root.length+1):x;};
    this.vt.setRows((j.rows||[]).map(r=>({k:r.kname,n:r.name&&r.name!==r.user?`${r.name}  @${r.user}`:(r.user?"@"+r.user:""),s:r.sid?String(r.sid).padStart(5,"0"):"",a:sh(r.src),b:sh(r.dst),note:r.note})));}};

/* ================= 21 清理工具（只看：刪除要在電腦本機操作） ================= */
PAGES[21]={render(pg){pg.innerHTML=`<div class="pg"><div class="row"><h1 class="title">清理工具</h1><span class="grow"></span><button id="clR">↻ 重新掃描</button></div><div class="sub">歷史紀錄都在資料庫，這裡的東西清掉不影響歷史。刪除／瘦身請在電腦本機的「實驗工作區 → 清理工具」操作。</div><div id="clB" style="margin-top:8px">讀取中…</div></div>`;$("#clR").onclick=()=>this.load();this.load();},
  async load(){let j;try{j=await api("/api/pc/cleanup");}catch(e){$("#clB").textContent="讀取失敗";return;}if(!$("#clB"))return;
    const f=t=>t?new Date(t*1000).toLocaleString("zh-TW",{year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit"}):"（沒有紀錄）";
    $("#clB").innerHTML=`<div class="panel"><div class="sec">📄 每場直播的文字備份（TXT）</div>${j.txt_n} 場、${fmtB(j.txt_b)} · <span style="color:#45d483">已停止產生新的 TXT</span></div>
<div class="panel" style="margin-top:8px"><div class="sec">🗒 程式紀錄檔</div><table style="width:100%;font-size:13px">${(j.logs||[]).map(x=>`<tr><td>${esc(x.name)}</td><td style="text-align:right">${fmtB(x.bytes)}</td><td class="sub">${esc(x.note||"")}</td></tr>`).join("")}</table></div>
<div class="panel" style="margin-top:8px"><div class="sec">🍪 網頁登入（Cookie）</div><table style="width:100%;font-size:13px"><tr class="sub"><td>裝置</td><td>IP</td><td>登入</td><td>最後使用</td></tr>${(j.ws||[]).map(x=>`<tr><td>${esc(x.dev)}</td><td>${esc(x.ip||"—")}</td><td>${f(x.t0)}</td><td>${f(x.last)}</td></tr>`).join("")||"<tr><td>沒有記住的登入</td></tr>"}</table></div>
<div class="panel" style="margin-top:8px"><div class="sec">🖼 頭像快取</div>不在主播清單的頭像 ${j.av_n} 張、${fmtB(j.av_b)}</div>`;}};

/* ================= 15 LIVE 時移（BETA）：網頁用手機版同一套直播畫面（可往回拖） ================= */
function loadHls(){return new Promise(res=>{if(window.Hls)return res(true);const sc=document.createElement("script");sc.src="https://cdnjs.cloudflare.com/ajax/libs/hls.js/1.5.13/hls.min.js";sc.onload=()=>res(!!window.Hls);sc.onerror=()=>res(false);document.head.appendChild(sc);});}
const LV_DELAY=16;      // V0.6.14 like the phone: stay ~15–20 s behind the live edge so the picture never runs out
/* V0.6.53 LIVE 時移改成跟「歷史回放」同一個畫面：這頁只負責選主播，選了就用歷史回放的版面（12 格、可調大小）看直播 */
PAGES[15]={render(pg,arg){pg.innerHTML=`<div class="pg"><div class="row"><h1 class="title">LIVE 時移（BETA）</h1><span class="grow"></span><span class="sub">選一位正在直播＋錄影的主播：用歷史回放的畫面看直播（約 15 秒延遲，可往回拖到開始錄影的地方）</span></div><div id="lvPick" class="lvPick"></div></div>`;
    this.draw();clearInterval(this.iv);this.iv=setInterval(()=>this.draw(),3000);
    const u=typeof arg==="string"?arg:"";if(u){const r=liveRooms().find(x=>x.u===u);if(r&&r.rec&&r.sid)setTimeout(()=>openHist(r.sid,r.name),0);else toast("這位主播目前沒有在錄影，沒辦法看直播畫面");}},
  draw(){const el=$("#lvPick");if(!el){clearInterval(this.iv);return;}const L=liveRooms();
    const kk=n=>{n=+n||0;return n>=1e4?(n/1e3).toFixed(n>=1e5?0:1)+"K":n.toLocaleString();};          // V0.6.59 跟手機「直播中」一樣的格子：大頭照、人數、時間、鑽石、按讚
    el.innerHTML=L.length?L.map(r=>{const ok=r.rec&&r.sid,g=r.grace!=null,cls=g?" g":r.nv?" nv":ok?"":" off";
      const band=g?`訊號中斷 · 等待重連 剩 ${Math.floor(r.grace/60)}:${String(r.grace%60).padStart(2,"0")}`:`直播中 · ${(r.viewers||0).toLocaleString()} 人 · ${esc(r.elapsed||"")}${r.rec?" · ● 錄影中":r.nv?" · 🎧 只錄聲音（沒有畫面）":" · 沒有在錄影"}`;
      return `<button class="lvPk${cls}" data-sid="${r.sid||0}" data-n="${esc(r.name)}" data-ok="${ok?1:0}" title="${ok?"點一下看直播畫面（可往回看）":"這場沒有在錄影，沒有畫面可以看"}"><div class="lvT">${avHtml(r.u,r.avatar,r.av,46,"lvA")}<div class="lvI"><div class="lvN"><b>${esc(r.name)}</b><i class="lvD"></i></div>
<div class="lvU"><span>@${esc(r.u)}</span><em class="lvDi">💎 ${kk(r.diamonds)}</em><em class="lvLk">♥ ${kk(r.likes)}</em></div></div></div><div class="lvB">${band}</div></button>`;}).join(""):'<div class="sub" style="padding:20px">目前沒有直播中的主播</div>';
    el.onclick=e=>{const b=e.target.closest(".lvPk");if(!b)return;if(b.dataset.ok!=="1"){toast("這場沒有在錄影，沒有畫面可以看");return;}clearInterval(this.iv);openHist(+b.dataset.sid,b.dataset.n);};},
  leave(){clearInterval(this.iv);}};
/* ================= 16 電腦效能 ================= */
const PFC={cpu:"#4dc9ff",ram:"#b48cff",disk:"#45d483",net:"#f0ad4e",gpu:"#2ed3b7",pw:"#ffd166"};
function pcGpuLbl(g){const v=+g.vendor||0,n=String(g.name||"");return v===0x10DE||/nvidia/i.test(n)?"GPU（NVIDIA）":v===0x8086||/intel/i.test(n)?"GPU（Intel 內顯）":v===0x1002||/amd|radeon/i.test(n)?(/graphics$/i.test(n)?"GPU（AMD 內顯）":"GPU（AMD）"):"GPU";}
function pfSer(P,k){const H=P.hist||[];if(k.startsWith("gpu:")){const i=+k.slice(4);return {v:H.map(h=>h.gpus?h.gpus[i]:(i===0?h.gpu:null)),mx:100,c:i?"#c084fc":PFC.gpu};}   /* V0.7.18 每張顯示卡各自一條 */if(k==="cpu"||k==="ram"||k==="gpu")return {v:H.map(h=>h[k]),mx:100,c:PFC[k]};if(k.startsWith("disk:")){const L=k.slice(5);return {v:H.map(h=>(h.busy||{})[L]),mx:100,c:PFC.disk};}
  if(k==="net"){const v=H.map(h=>h.rx),v2=H.map(h=>h.tx);return {v,v2,mx:Math.max(1e5,...v.concat(v2).filter(x=>x!=null))*1.15,c:PFC.net};}if(k==="pw"){const v=H.map(h=>h.pw);return {v,mx:Math.max(100,...v.filter(x=>x!=null))*1.2,c:PFC.pw};}return {v:[],mx:100,c:"#888"};}
function pfDraw(cv,s,big){const r=cv.getBoundingClientRect(),dpr=devicePixelRatio||1,W=r.width,H=r.height;if(!W)return;cv.width=W*dpr;cv.height=H*dpr;const g=cv.getContext("2d");g.setTransform(dpr,0,0,dpr,0,0);
  const css=k=>getComputedStyle(document.documentElement).getPropertyValue("--"+k).trim();g.fillStyle=css("chart_bg");g.fillRect(0,0,W,H);
  if(big){g.strokeStyle=css("chart_grid");for(let i=1;i<10;i++){g.beginPath();g.moveTo(W*i/10,0);g.lineTo(W*i/10,H);g.stroke();}for(let i=1;i<5;i++){g.beginPath();g.moveTo(0,H*i/5);g.lineTo(W,H*i/5);g.stroke();}}
  const N=180,line=(v,dash,fill)=>{if(!v.length)return;const x0=W-(v.length-1)/(N-1)*W;g.beginPath();let st=false,f=0,l=0;v.forEach((y,i)=>{if(y==null)return;const X=x0+i/(N-1)*W,Y=H-Math.min(1,y/s.mx)*(H-2)-1;st?g.lineTo(X,Y):(g.moveTo(X,Y),st=true,f=X);l=X;});if(!st)return;
    g.strokeStyle=s.c;g.lineWidth=big?1.6:1.2;g.setLineDash(dash?[4,3]:[]);g.stroke();g.setLineDash([]);if(fill){g.lineTo(l,H);g.lineTo(f,H);g.closePath();g.globalAlpha=.18;g.fillStyle=s.c;g.fill();g.globalAlpha=1;}};
  line(s.v,false,true);if(s.v2)line(s.v2,true,false);g.strokeStyle=s.c;g.globalAlpha=.55;g.strokeRect(.5,.5,W-1,H-1);g.globalAlpha=1;}
PAGES[16]={render(pg){pg.innerHTML=`<div class="pg"><div class="row"><h1 class="title">電腦效能</h1><span class="sub" id="pfT">讀取中…</span></div><div class="panel" style="margin-top:8px"><div id="pfAn"></div></div>
<div class="row" style="align-items:stretch;gap:8px;margin-top:8px"><div class="panel" style="flex:3"><div class="row"><b id="pfBT" style="font-size:17px"></b><span class="grow"></span><b id="pfBV" style="font-size:17px"></b></div><div style="height:230px;position:relative;margin-top:4px"><canvas id="pfBig" style="position:absolute;inset:0;width:100%;height:100%"></canvas></div><div class="row sub"><span>6 分鐘前</span><span class="grow" style="text-align:center" id="pfAx"></span><span>現在</span></div><div class="kv" id="pfDet" style="margin-top:6px"></div></div><div class="tiles" id="pfTiles" style="flex:2;align-content:start"></div></div>
<div class="row" style="align-items:stretch;gap:8px;margin-top:8px"><div class="panel" style="flex:1"><div class="sec">⚡ 耗電估算（±20%）</div><div id="pfPow"></div></div><div class="panel" style="flex:1"><div class="sec">🌡 溫度</div><div id="pfTmp"></div></div></div>
<div class="panel" style="margin-top:8px"><div class="sec">🎞 FLV → MP4 轉檔排隊</div><div id="pfMq"></div></div><div class="panel" style="margin-top:8px"><div class="sec">💾 硬碟與資料夾容量</div><div id="pfSt"></div></div><div class="panel" style="margin-top:8px"><div class="sec">💡 同時很多主播直播時</div><div id="pfAdv"></div></div></div>`;this.sel=null;this.poll();},
  leave(){clearTimeout(this.pt);},
  async poll(){clearTimeout(this.pt);let P;try{P=await api("/api/perf");}catch(e){}if(!$("#pfT"))return;if(P&&!P.error){this.P=P;this.draw();}this.pt=setTimeout(()=>this.poll(),2000);},
  tiles(P){const T=[],tp=P.temps||{};T.push(["cpu","CPU",P.cpu!=null?Math.round(P.cpu)+"%":"—",tp.cpu?Math.round(tp.cpu)+"°C":""]);T.push(["ram","記憶體",P.ram!=null?Math.round(P.ram)+"%":"—",P.ram_total?fmtB(P.ram_used)+" / "+fmtB(P.ram_total):""]);
    (P.drives||[]).forEach(d=>T.push(["disk:"+d.d,`磁碟 ${d.d}${d.kind?" ("+d.kind+")":""}${d.data?" 📁":""}`,Math.round(d.busy||0)+"%",(d.temp!=null?`🌡 ${Math.round(d.temp)}°C · `:"")+`讀 ${fmtR(d.rd)} · 寫 ${fmtR(d.wr)}`]));
    T.push(["net","網路",fmtMb(P.net.rx),"↑ "+fmtMb(P.net.tx)]);(P.gpus||[]).forEach((g,i)=>{if(g.use!=null)T.push(["gpu:"+i,pcGpuLbl(g),Math.round(g.use)+"%",(g.temp!=null?Math.round(g.temp)+"°C · ":"")+(g.name||"")]);});
    const pw=P.power||{};if(pw.wall)T.push(["pw","耗電（估）","約 "+pw.wall+" W",Math.round(pw.wall*.8)+"–"+Math.round(pw.wall*1.2)+" W"]);return T;},
  draw(){const P=this.P,T=this.tiles(P);$("#pfT").textContent=P.time+" · 每 2 秒更新";if(!this.sel||!T.some(t=>t[0]===this.sel))this.sel=(T.find(t=>t[1].includes("📁"))||T[0])[0];
    const box=$("#pfTiles"),sig=T.map(t=>t[0]).join();if(box._s!==sig){box._s=sig;box.innerHTML=T.map(t=>`<div class="ptile" data-k="${t[0]}"><canvas></canvas><div><b></b><span class="v"></span><small></small></div></div>`).join("");$$(".ptile",box).forEach(d=>d.onclick=()=>{this.sel=d.dataset.k;this.draw();});}
    T.forEach(t=>{const d=box.querySelector(`[data-k="${CSS.escape(t[0])}"]`);d.classList.toggle("on",t[0]===this.sel);d.querySelector("b").textContent=t[1];d.querySelector(".v").textContent=t[2];d.querySelector("small").textContent=t[3];pfDraw(d.querySelector("canvas"),pfSer(P,t[0]),false);});
    const s=T.find(t=>t[0]===this.sel),ser=pfSer(P,this.sel);$("#pfBT").textContent=s[1];$("#pfBT").style.color=ser.c;$("#pfBV").textContent=s[2];pfDraw($("#pfBig"),ser,true);$("#pfAx").textContent=this.sel==="net"?"實線＝下載、虛線＝上傳":this.sel==="pw"?"瓦（估算）":"0–100%";
    const kv=rows=>rows.map(([a,b])=>`<span>${a}</span><b>${b}</b>`).join(""),tp=P.temps||{},k=this.sel;let det=[];
    if(k==="cpu")det=[["使用率",Math.round(P.cpu||0)+"%"],["溫度",tp.cpu?Math.round(tp.cpu)+"°C":"—"],["主機板",tp.board?Math.round(tp.board)+"°C":"—"],["型號",esc((P.power||{}).cpu_name||"—")]];
    else if(k==="ram"){det=[["使用中",fmtB(P.ram_used)],["總共",fmtB(P.ram_total)],["使用率",Math.round(P.ram||0)+"%"]];   /* TK_V0.9.22 記憶體誰在用 */
      const m=P.memx||{};if(!m.t)det.push(["誰在用","量測中…（約 1 分鐘內出來）"]);else{det.push(["TikLive 主程式",fmtB(m.me)],["FFmpeg 錄影／轉檔（"+(m.ffn||0)+" 個）",fmtB(m.ff)]);(m.top||[]).slice(0,5).forEach(([n,b,c])=>det.push([esc(n)+(c>1?"（"+c+" 個）":""),fmtB(b)]));const o=Math.max(0,(P.ram_used||0)-(m.sum||0));if(o)det.push(["Windows 系統、快取等",fmtB(o)]);}if(typeof MEMD_BTN==="string")det.push(["主程式",MEMD_BTN]);}
    else if(k==="net")det=[["下載",fmtMb(P.net.rx)+"（"+fmtR(P.net.rx)+"）"],["上傳",fmtMb(P.net.tx)],["其中錄影下載",fmtR(P.net.video)],["1000 Mbps 光纖用掉",((P.net.rx*8/1e6)/10).toFixed(1)+"%"]];
    else if(k==="gpu"||k.startsWith("gpu:")){const g=(P.gpus||[])[+(k.split(":")[1]||0)]||{};det=[["型號",esc(g.name||"—")],["使用率",g.use!=null?Math.round(g.use)+"%":"—"],["溫度",g.temp!=null?Math.round(g.temp)+"°C":"—"],["功耗",g.power!=null?Math.round(g.power)+" W":"—"]];}
    else if(k.startsWith("disk:")){const d=(P.drives||[]).find(x=>"disk:"+x.d===k)||{};det=[["使用中時間",Math.round(d.busy||0)+"%"],["讀取",fmtR(d.rd)],["寫入",fmtR(d.wr)],["溫度",d.temp!=null?Math.round(d.temp)+"°C":"讀不到*"],["已用",Math.round(d.used||0)+"%（剩 "+fmtB(d.free)+"）"],["型號",esc(d.name||"—")+(d.kind?" · "+d.kind:"")]];if(d.data)det.push(["用途","📁 資料／錄影硬碟"]);else if(d.use===false)det.push(["用途","沒用到（只是列出來看）"]);
      if(d.health)det.push(["健康狀態",{Healthy:"✔ 良好",Warning:"⚠ 警告",Unhealthy:"✖ 不良"}[d.health]||esc(d.health)]);if(d.tmax)det.push(["出廠最高溫",d.tmax+"°C"]);
      if(d.poh)det.push(["通電時數",num(d.poh)+" 小時（約 "+(d.poh/8760).toFixed(1)+" 年）"]);if(d.wear!=null&&d.kind==="SSD")det.push(["SSD 磨損",d.wear+"%"]);if(d.rerr||d.werr)det.push(["讀／寫錯誤",num(d.rerr)+" ／ "+num(d.werr)]);}
    $("#pfDet").innerHTML=kv(det);const pw=P.power||{};
    $("#pfPow").innerHTML=pw.wall?`<div style="font-size:24px;font-weight:800;margin:4px 0">約 ${pw.wall} W <span class="sub" style="font-size:12px">（${Math.round(pw.wall*.8)}–${Math.round(pw.wall*1.2)} W，插座端，最近 ${pw.avg_secs||12} 秒平均）</span></div><div>每天約 <b>${(pw.wall*24/1000).toFixed(1)} 度</b>、每月約 <b>${Math.round(pw.wall*24*30/1000)} 度</b></div><div class="kv" style="grid-template-columns:auto 1fr;margin-top:6px">${kv([["CPU",`${pw.cpu} W（${esc(pw.cpu_name||"?")}，滿載約 ${pw.tdp} W）`],["顯示卡",pw.gpu+" W"],["硬碟",pw.disks+" W"],["記憶體",pw.ram+" W"],["主機板／風扇等",pw.base+" W"],["電源損耗（效率 87%）",pw.psu_loss+" W"]])}</div>`:`<span class="sub">還算不出來</span>`;
    const acpi=(P.temp_srcs||{}).cpu==="ACPI";const TT=[[acpi?"CPU（主機板量）":"CPU",tp.cpu||null],["記憶體",null]];const TS=window.__tSeen=window.__tSeen||{};if(tp.board)TS.board=1;if(TS.board)TT.push(["主機板",tp.board||null]);(P.gpus||[]).forEach(g=>{const k="g:"+(g.name||"");if(g.temp!=null)TS[k]=1;if(TS[k])TT.push([pcGpuLbl(g),g.temp]);});   /* V0.7.39 讀到過的溫度格子一直留著，版面不跳 */(P.drives||[]).forEach(d=>TT.push(["磁碟 "+d.d,d.temp]));
    const dh=P.disk_helper||{};
    $("#pfTmp").innerHTML=`<div class="kv">${kv(TT.map(([a,t])=>[a,t==null?"—":`<span style="color:${t>=80?"#ff5c5c":t>=50?"#f0ad4e":"inherit"}">${Math.round(t)}°C</span>`]))}</div>`+
      `<div class="row" style="margin-top:8px"><span class="sub grow">${dh.on?`Windows 硬碟健康資料讀取中（${dh.n} 顆硬碟，${dh.temps} 顆有回報溫度；沒回報的是硬碟本身不提供）`:"硬碟溫度要管理員權限才讀得到：按右邊按鈕，電腦上會跳出 Windows 的詢問，在電腦前按「是」後每分鐘自動讀取（不用裝其他軟體）。"}</span>`+
      (dh.nt===false?"":`<button id="pfDh">${dh.on?"停用硬碟溫度讀取":"🌡 啟用硬碟溫度讀取"}</button>`)+`</div>`+
      `<div class="sub" style="margin-top:6px">${!tp.cpu?"CPU：這台電腦的 Windows 沒有提供 CPU 溫度（啟用上面的硬碟溫度讀取，或在電腦上開著免費的 LibreHardwareMonitor）。":acpi?"CPU：用 Windows 內建的 ACPI 溫度區，是主機板在 CPU 附近量的，可能跟核心溫度差幾度；要看核心溫度請開著 LibreHardwareMonitor。":"CPU：來自 "+esc((P.temp_srcs||{}).cpu||"LibreHardwareMonitor")+"。"}　記憶體：Windows 不提供記憶體溫度，大部分記憶體也沒有溫度感測器（只有部分 DDR5 有，要 LibreHardwareMonitor 才讀得到）。</div>`;
    const db=$("#pfDh");if(db)db.onclick=async()=>{if(dh.on&&!await confirmDlg("硬碟溫度","停用硬碟溫度讀取？（電腦上會再問一次管理員權限）","停用"))return;const j=await post("/api/pc/diskhelper",{on:!dh.on});toast(j.ok?(dh.on?"已送出停用":"✔ 電腦上已跳出管理員詢問，在電腦前按「是」後約 1 分鐘開始顯示"):"✖ "+(j.message||"沒有成功"),5000);};
    const M=P.merge||{},L=M.items||[];$("#pfMq").innerHTML=mqHtml(P);
    const st=P.store||{},bar=(p,c)=>`<div class="bar"><i style="width:${Math.max(1,Math.min(100,p))}%;background:${c}"></i></div>`;let sh=`<table style="width:100%;font-size:12.5px">`+(P.drives||[]).map(d=>`<tr><td style="width:150px"><b>${d.d}</b> ${d.kind||""}${d.data?" 📁":""}</td><td>${bar(d.used,d.used>=90?"#ff5c5c":d.used>=80?"#f0ad4e":"#45d483")}</td><td style="width:240px;text-align:right">已用 ${Math.round(d.used)}% · 剩 ${fmtB(d.free)} / ${fmtB(d.total)}</td></tr>`).join("")+"</table>";
    const MD=st.media;   // V0.6.03 只留重點：MP4、M4A、舊檔案 vs 分類資料夾；各主播按格子看
    if(!st.t||!MD)sh+=`<div class="sub" style="margin-top:6px">影片與錄音大小統計中…</div>`;else if(MD.error)sh+=`<div class="sub">統計失敗：${esc(MD.error)}</div>`;else{
      const all=(MD.mp4[0]+MD.m4a[0]+MD.flv[0])||1,T=(t,b,n,c,ck)=>`<div class="ptile"${ck?' data-who="1" title="點一下看各主播占比"':' style="cursor:default"'}><div style="width:100%"><b>${t}</b><span class="v">${fmtB(b)}</span><small>${num(n)} 個 · ${(b/all*100).toFixed(1)}%</small>${bar(b/all*100,c)}</div></div>`;
      sh+=`<div class="sec" style="margin-top:10px">🎞 影片與錄音 <span class="sub">共 ${fmtB(all)}</span></div><div class="tiles" style="grid-template-columns:repeat(auto-fill,minmax(210px,1fr));margin-top:6px">`+T("🎞 MP4 影片 ›",MD.mp4[0],MD.mp4[1],"#4dc9ff",1)+T("🎙 M4A 錄音 ›",MD.m4a[0],MD.m4a[1],"#b48cff",1)+(MD.flv[1]?T("⏳ FLV 還沒轉檔",MD.flv[0],MD.flv[1],"#f0ad4e"):"")+`</div>`;
      sh+=`<div class="sec" style="margin-top:10px">📁 放在哪裡 <span class="sub">舊檔案 vs 分類資料夾</span></div><div class="tiles" style="grid-template-columns:repeat(auto-fill,minmax(210px,1fr));margin-top:6px">`+T("🗃 舊的（還沒分資料夾） ›",MD.old[0],MD.old[1],"#8994a4").replace(' style="cursor:default"',' data-oldopen="1" title="點一下看是哪些檔案、為什麼還沒搬" style="cursor:pointer"').replace('</small>',(MD.old_age&&MD.old_age["3"]&&MD.old_age["3"][1]?` · ⚠ 3 天以上沒動 ${MD.old_age["3"][1]} 個`+(MD.old_age["14"][1]?`（14 天以上 ${MD.old_age["14"][1]}）`:""):"")+'</small>')+(MD.cats||[]).map(c=>T(`<span class="cdot" style="background:${c.color}"></span>${esc(c.name)}（📁 ${esc(c.folder)}）`,c.bytes,c.n,c.color)).join("")+`</div>`;
      sh+=`<div class="sub" style="margin-top:6px">點「MP4 影片」或「M4A 錄音」看每位主播占多少 · 每 10 分鐘重算一次（上次 ${fmtHM(st.t)}）</div>`;}
    $("#pfSt").innerHTML=sh;try{const tb_=$("#pfSt table");if(tb_&&typeof dhHtml==="function"){tb_.insertAdjacentHTML("afterend",`<div style="margin-top:8px">${dhHtml()}</div>`);dhMount($("#dhBox"));}}catch(e){}   /* V0.7.27 容量變化曲線 */$$("#pfSt [data-who]").forEach(x=>x.onclick=()=>pfWho(MD));
    const data=(P.drives||[]).find(d=>d.data)||{},H=P.hist||[],bb=H.slice(-150).map(h=>(h.busy||{})[data.d]).filter(x=>x!=null),b5=bb.length?bb.reduce((a,b)=>a+b,0)/bb.length:0,nv=(P.rec_video||[]).length;
    const tips=[`現在 ${P.live} 位直播中、錄影 ${nv} 路、錄音 ${P.rec_audio} 路；錄影一共 ${fmtR(P.net.video)}（每小時約 ${fmtB(P.net.video*3600)}）。`,`網路：下載用到 ${fmtMb(P.net.rx)}，1000 Mbps 光纖只用了 ${((P.net.rx*8/1e6)/10).toFixed(1)}%。`];
    if(data.d)tips.push(`${data.d} 硬碟最近 5 分鐘平均忙碌 ${Math.round(b5)}%${b5>=70?"：很忙":b5>=45?"：中等":"：還很輕鬆"}。`);if(L.length)tips.push(`轉檔排隊 ${L.length} 部，全部做完還要約 ${fmtDur(M.all_left)}。`);
    $("#pfAdv").innerHTML="<ul style='margin:4px 0;padding-left:18px;line-height:1.7'>"+tips.map(t=>`<li>${t}</li>`).join("")+"</ul>";
    {const h=`🩺 自我檢查、網路狀態、觀察到的異常 → 移到左邊「<a href="javascript:void(0)" onclick="go(22)">LOG 與問題</a>」${(P.anom||[]).length?`（最近 7 天 ${(P.anom||[]).length} 項）`:""}${P.health&&P.health.t&&!P.health.ok?` <b style="color:#ff4d6d">資料庫寫不進去 ${P.health.blocked_min} 分鐘</b>`:""}`;const el=$("#pfAn");if(el&&el._h!==h){el._h=h;el.innerHTML=h;}}}};
function anomHtml(L){if(!L||!L.length)return '<span style="color:#45d483">✔ 最近 7 天沒有觀察到異常（CPU、記憶體、硬碟忙碌、溫度、空間、資料庫與紀錄檔大小、主程式記憶體、畫面卡住都會自動盯著）</span>';
  const f=t=>{const d=new Date(t*1000);return (d.getMonth()+1)+"/"+d.getDate()+" "+String(d.getHours()).padStart(2,"0")+":"+String(d.getMinutes()).padStart(2,"0");};
  return L.slice(0,30).map(e=>`<div style="margin:4px 0"><b style="color:${e.level==="bad"?"#ff4d6d":"#f0ad4e"}">⚠ ${esc(e.title||"")}</b> <span style="opacity:.65;font-size:.9em">${f(e.t)}${(e.n||1)>1?` → ${f(e.last).slice(-5)}，${e.n} 次`:""}</span><br>${esc(e.detail||"")}${e.tip?`<br><span style="opacity:.65;font-size:.9em">${esc(e.tip)}</span>`:""}</div>`).join("");}

function pfWho(M){if(!M||!M.who)return;const all=M.who.reduce((a,w)=>a+w.mp4+w.m4a+w.flv,0)||1;
  dialog("各主播占用（大 → 小）",`<div style="max-height:68vh;overflow:auto"><table style="width:100%;font-size:12.5px;border-collapse:collapse"><tr class="sub" style="position:sticky;top:0;background:var(--panel)"><td>主播</td><td align="right">MP4</td><td align="right">影片數</td><td align="right">M4A</td><td align="right">錄音數</td><td align="right">合計</td><td align="right">占比</td><td>分類／舊檔</td></tr>`+
    M.who.map(w=>{const t=w.mp4+w.m4a+w.flv;return `<tr style="border-top:1px solid var(--border)"><td><b>${esc(w.name)}</b></td><td align="right">${fmtB(w.mp4)}</td><td align="right">${num(w.mp4n)}</td><td align="right">${fmtB(w.m4a)}</td><td align="right">${num(w.m4an)}</td><td align="right"><b>${fmtB(t)}</b></td><td align="right">${(t/all*100).toFixed(1)}%</td><td class="sub">${esc(w.cats.join("、"))}${w.old?(w.cats.length?"；":"")+"舊 "+fmtB(w.old):""}${w.flv?"；FLV "+fmtB(w.flv):""}</td></tr>`;}).join("")+"</table></div>");}
/* ================= 17 開播統計 ================= */
const STC={live:"#ff5c8a",rec:"#b48cff",meas:"#4dc9ff",est:"#f0ad4e"},STN={live:"同時開播",rec:"有錄影",meas:"下載（實測）",est:"下載（估算）"};
PAGES[17]={render(pg){const show=LS.get("stshow",{live:1,rec:1,meas:1,est:1});this.show=show;const t=new Date(),ymd=d=>d.getFullYear()+"-"+p2(d.getMonth()+1)+"-"+p2(d.getDate());
    pg.innerHTML=`<div class="pg"><h1 class="title">開播與流量統計</h1><div class="panel" style="margin-top:6px"><div class="row wrap">${[["48h","近 48 小時"],["today","今天"],["yday","昨天"],["7","近 7 天"],["30","近 30 天"]].map(([k,t])=>`<button data-q="${k}">${t}</button>`).join("")}<span style="width:16px"></span>
<input type="date" id="sf" value="${ymd(t)}"><select id="sh1">${Array.from({length:24},(_,h)=>`<option value="${h}">${p2(h)}:00</option>`).join("")}</select><span>到</span><input type="date" id="st2" value="${ymd(t)}"><select id="sh2">${Array.from({length:24},(_,h)=>`<option value="${h+1}"${h===23?" selected":""}>${p2(h+1)}:00</option>`).join("")}</select><button class="start" id="sgo">查詢</button></div>
<div class="row wrap" style="margin-top:6px">${Object.keys(STC).map(k=>`<label style="color:${STC[k]};font-weight:700"><input type="checkbox" data-k="${k}"${show[k]?" checked":""}> ${STN[k]}</label>`).join("")}<span class="grow"></span><span class="sub" id="sstat"></span></div></div>
<div class="row" style="gap:8px;margin-top:8px" id="stiles"></div><div class="panel" style="margin-top:8px"><div style="height:330px;position:relative"><canvas id="scv" style="position:absolute;inset:0;width:100%;height:100%"></canvas></div><div class="sub" id="snote"></div></div>
<div class="panel" style="margin-top:8px"><div class="sec">🗓 每天每小時最多同時開播</div><div class="hm" id="shm" style="margin-top:6px"></div></div></div>`;
    $$("[data-q]",pg).forEach(b=>b.onclick=()=>{this.q=b.dataset.q;this.load();});$("#sgo").onclick=()=>{this.q="";this.load();};
    $$("input[data-k]",pg).forEach(c=>c.onchange=()=>{this.show[c.dataset.k]=c.checked?1:0;LS.set("stshow",this.show);this.chart();});
    const cv=$("#scv");cv.onmousemove=e=>{const r=cv.getBoundingClientRect();this.fx=e.clientX-r.left;this.chart();};cv.onmouseleave=()=>{this.fx=null;this.chart();};
    this.q="48h";this.load();new ResizeObserver(()=>this.chart()).observe(cv);},
  params(){const now=Date.now()/1000,d0=new Date();d0.setHours(0,0,0,0);const today=d0.getTime()/1000,q=this.q;
    if(q==="48h")return `s=${now-172800}&e=${now}`;if(q==="today")return `s=${today}&e=${today+86400}`;if(q==="yday")return `s=${today-86400}&e=${today}`;if(q==="7"||q==="30")return `s=${now-q*86400}&e=${now}`;
    return `from=${$("#sf").value}&to=${$("#st2").value}&h1=${$("#sh1").value}&h2=${$("#sh2").value}`;},
  async load(){$$("[data-q]").forEach(b=>b.classList.toggle("start",b.dataset.q===this.q));$("#sstat").textContent="查詢中…";const d=await api("/api/stats/live?"+this.params());if(!$("#scv"))return;
    if(d.error){$("#sstat").textContent="✖ "+d.error;return;}$("#sstat").textContent="";this.d=d;
    const step=d.step>=3600?`每 ${d.step/3600} 小時一點`:`每 ${d.step/60} 分鐘一點`;
    $("#stiles").innerHTML=[["最多同時開播",d.peak.n+" 人",fmtHM(d.peak.t)],["實測最高下載",d.peak_dl?fmtMb(d.peak_dl):"—",d.peak_dl?fmtR(d.peak_dl):"還沒有紀錄"],["估算錄影下載高峰",fmtMb(d.peak_est),fmtR(d.peak_est)],["區間內場次",d.sessions+" 場",step]].map(([a,b,c])=>`<div class="panel" style="flex:1"><div class="sub">${a}</div><div style="font-size:21px;font-weight:800">${b}</div><div class="sub">${c}</div></div>`).join("");
    $("#snote").textContent=`左邊刻度＝人數、右邊＝下載 Mbps。實測下載從 ${d.log_from?fmtHM(d.log_from):"V0.5.68"} 才開始記錄；估算＝錄影檔大小÷直播長度加總。`;
    const rows=d.heat||[],mx=Math.max(1,...rows.map(r=>Math.max(...r[1])));$("#shm").innerHTML=`<span></span>`+Array.from({length:24},(_,h)=>`<span style="text-align:center">${h%3===0?h:""}</span>`).join("")+rows.map(([day,v])=>`<span>${day.slice(5).replace("-","/")}</span>`+v.map((x,h)=>`<i title="${day} ${h} 點：${x} 人" style="background:${x?`rgba(229,30,99,${.18+.82*x/mx})`:"transparent"}">${x||""}</i>`).join("")).join("");this.chart();},
  chart(){const d=this.d,cv=$("#scv");if(!d||!cv)return;const r=cv.getBoundingClientRect(),dpr=devicePixelRatio||1,W=r.width,H=r.height;cv.width=W*dpr;cv.height=H*dpr;const g=cv.getContext("2d");g.setTransform(dpr,0,0,dpr,0,0);
    const css=k=>getComputedStyle(document.documentElement).getPropertyValue("--"+k).trim();g.fillStyle=css("chart_bg");g.fillRect(0,0,W,H);const s=this.show,n=d.live.length,L=40,R=52,T=10,Bm=24,pw=W-L-R,ph=H-T-Bm,X=i=>L+(n<=1?0:i/(n-1))*pw;
    const nowI=Math.min(n-1,Math.floor((d.now-d.t0)/d.step)),maxN=Math.max(4,...(s.live?d.live:[0]),...(s.rec?d.rec:[0]));const mm=[...(s.meas?d.meas.filter(x=>x!=null):[]),...(s.est?d.est:[])],maxB=Math.max(125000,...mm)*1.1;
    const yN=v=>T+ph-v/maxN*ph,yB=v=>T+ph-v/maxB*ph;g.font="11px sans-serif";
    for(let i=0;i<=4;i++){const y=T+ph*i/4+.5;g.strokeStyle=css("chart_grid");g.beginPath();g.moveTo(L,y);g.lineTo(L+pw,y);g.stroke();g.fillStyle=css("chart_label");g.textAlign="right";g.fillText(Math.round(maxN*(1-i/4)),L-4,y+4);g.textAlign="left";g.fillText((maxB*(1-i/4)*8/1e6).toFixed(maxB*8/1e6>=20?0:1),L+pw+4,y+4);}
    const span=d.t1-d.t0,lab=ep=>{const x=new Date(ep*1000);return span>129600?(x.getMonth()+1)+"/"+x.getDate()+(span<345600?" "+p2(x.getHours())+"時":""):p2(x.getHours())+":"+p2(x.getMinutes());};g.textAlign="center";[0,.25,.5,.75,1].forEach(p=>g.fillText(lab(d.t0+p*span),Math.min(Math.max(L+24,L+p*pw),W-30),H-6));
    {const tsp=Math.max(1,(n-1)*d.step),md=new Date(d.t0*1000);md.setHours(24,0,0,0);g.save();g.setLineDash([4,4]);g.strokeStyle="rgba(137,148,164,.75)";g.fillStyle=css("chart_label");g.textAlign="left";   // V0.6.02 每天 00:00 一條線
      for(;md.getTime()/1000<d.t0+tsp;md.setDate(md.getDate()+1)){const mx=L+(md.getTime()/1000-d.t0)/tsp*pw;g.beginPath();g.moveTo(mx,T);g.lineTo(mx,T+ph);g.stroke();g.fillText((md.getMonth()+1)+"/"+md.getDate(),mx+3,T+11);}g.restore();}
    const line=(arr,y,col,fill,dash)=>{g.beginPath();let st=false,f=null,l=0;for(let i=0;i<=Math.min(n-1,nowI);i++){const v=arr[i];if(v==null){st=false;continue;}const px=X(i),py=y(v);if(!st){g.moveTo(px,py);st=true;if(f==null)f=px;}else g.lineTo(px,py);l=px;}
      g.strokeStyle=col;g.lineWidth=1.6;g.setLineDash(dash?[5,4]:[]);g.stroke();g.setLineDash([]);if(fill&&f!=null){g.lineTo(l,T+ph);g.lineTo(f,T+ph);g.closePath();g.globalAlpha=.14;g.fillStyle=col;g.fill();g.globalAlpha=1;}};
    if(s.live)line(d.live,yN,STC.live,true);if(s.rec)line(d.rec,yN,STC.rec);if(s.est)line(d.est,yB,STC.est,false,true);if(s.meas)line(d.meas,yB,STC.meas);
    if(this.fx!=null){const i=Math.max(0,Math.min(n-1,Math.round((this.fx-L)/pw*(n-1)))),px=X(i),t=d.t0+i*d.step;g.strokeStyle=css("text_strong");g.globalAlpha=.6;g.beginPath();g.moveTo(px,T);g.lineTo(px,T+ph);g.stroke();g.globalAlpha=1;
      const rows=[lab(t)+" "+fmtClk(t).slice(0,5)].concat(t>d.now?["（還沒到）"]:[`同時開播 ${d.live[i]} 人`,`有錄影 ${d.rec[i]} 人`,`實測 ${d.meas[i]!=null?fmtMb(d.meas[i]):"—"}`,`估算 ${fmtMb(d.est[i])}`]);
      const bw=Math.max(...rows.map(x=>g.measureText(x).width))+16,bx=px>W/2?px-bw-8:px+8;g.fillStyle=css("card");g.strokeStyle=css("border_strong");g.fillRect(bx,T+4,bw,rows.length*16+8);g.strokeRect(bx,T+4,bw,rows.length*16+8);g.textAlign="left";
      rows.forEach((x,j)=>{g.fillStyle=j===0?css("text"):[null,STC.live,STC.rec,STC.meas,STC.est][j]||css("text");g.fillText(x,bx+8,T+18+j*16);});}}};
/* ================= 18 主播分類 ================= */
const CATC=["#ff5c8a","#4dc9ff","#45d483","#f0ad4e","#b48cff","#ff7043","#2ed3b7","#ffd166","#8994a4"];
PAGES[18]={render(pg){this.vt=null;pg.innerHTML=`<div class="pg"><h1 class="title">主播分類</h1><div class="sub" id="caI"></div><div class="row" style="align-items:flex-start;gap:8px;margin-top:8px"><div class="panel" style="flex:2"><div class="sec">分類（標題、資料夾名、顏色都能改）</div><div id="caE"></div><div class="row" style="margin-top:8px"><button id="caAdd">＋ 新增分類</button><span class="grow"></span><button class="start" id="caSave">儲存分類</button></div><div id="caMsg" style="margin-top:6px"></div></div>
<div class="panel" style="flex:3"><div class="sec">主播（右邊選分類就能改）</div><input id="caQ" placeholder="🔍 搜尋主播名字 / @帳號" style="display:block;width:100%;max-width:420px;box-sizing:border-box;margin:6px 0 4px"><select id="caF" style="margin:0 0 6px"></select><div id="caT" style="height:520px;display:flex;flex-direction:column"></div><div class="sub" id="caS"></div></div></div></div>`;
    $("#caAdd").onclick=()=>{this.E.push({id:"",name:"",folder:"",color:CATC[this.E.length%CATC.length]});this.drawE();};$("#caSave").onclick=()=>this.save();$("#caF").onchange=()=>this.drawT();$("#caQ").oninput=()=>this.drawT();this.load();},
  async load(){const C=await api("/api/cats");if(!$("#caE"))return;this.C=C;this.E=C.cats.map(({id,name,folder,color})=>({id,name,folder,color}));
    $("#caI").textContent=`每個分類對應影片庫（${C.root}）裡的一個資料夾。主播設了分類，他的影片／錄音就搬進去，以後新錄的也直接放那裡；同一顆硬碟上是「改名」，一下就好。正在被看的檔案會等看完再搬。`;this.drawE();
    const f=$("#caF"),cur=f.value;f.innerHTML=`<option value="">全部 ${C.roster.length}</option><option value="none">○ 未分類 ${C.roster.filter(r=>!r.cat).length}</option>`+C.cats.map(c=>`<option value="${c.id}">● ${esc(c.name)} ${c.count}</option>`).join("");f.value=cur;this.drawT();
    const st=C.status||{};$("#caS").textContent=st.running?"⏳ 正在搬檔案…":st.last?`上次整理 ${fmtHM(st.last)}：搬了 ${st.moved_last||0} 個檔案`+(st.busy?`，${st.busy} 個正在被使用（看完後自動再試）`:"")+(st.conflict?`，${st.conflict} 個目的地已有同名檔案（沒動）`:""):"還沒整理過";this.statNote(C);},
  statNote(C){const P=C.stats_prog||{};let el=$("#caP");if(!el){el=document.createElement("div");el.id="caP";el.className="sub";$("#caS").after(el);}
    el.textContent=C.stats_ready===false?(P.err?"⚠ 統計失敗，2 分鐘後自動再試："+P.err:"⏳ 統計資料整理中 "+(P.total?P.done+"／"+P.total+" 場":"")+"（第一次比較久，之後只算新的場次），數字會邊算邊出現"):"";
    clearTimeout(this.pt);if(C.stats_ready===false)this.pt=setTimeout(async()=>{if(!$("#caT"))return;const N=await api("/api/cats");if(!$("#caT")||!N)return;this.C.roster=N.roster;this.C.stats_ready=N.stats_ready;this.C.stats_prog=N.stats_prog;this.drawT();this.statNote(this.C);},4000);},
  drawE(){const E=this.E;$("#caE").innerHTML=E.map((c,i)=>`<div class="hero row" style="margin-top:6px;padding:4px 6px" data-i="${i}"><button class="cc" style="width:26px;height:26px;border-radius:13px;background:${c.color};padding:0" title="換顏色"></button><input class="cn grow" value="${esc(c.name)}" placeholder="分類標題（例：舞蹈）"><span>📁</span><input class="cf grow" value="${esc(c.folder)}" placeholder="資料夾名（例：TKD-Dance）"><button class="cd" title="刪除">🗑</button></div>`).join("")||`<div class="sub" style="margin-top:6px">還沒有分類，按下面新增。</div>`;
    $$("#caE [data-i]").forEach(row=>{const i=+row.dataset.i;row.querySelector(".cn").oninput=e=>E[i].name=e.target.value;row.querySelector(".cf").oninput=e=>E[i].folder=e.target.value;
      row.querySelector(".cc").onclick=e=>{e.stopPropagation();const r=e.target.getBoundingClientRect();menu(CATC.map(x=>({html:`<span class="cdot" style="background:${x}"></span>${x}`,act:()=>{E[i].color=x;this.drawE();}})),r.left,r.bottom);};
      row.querySelector(".cd").onclick=async()=>{if(E[i].id&&!await confirmDlg("刪除分類",`刪除分類「${E[i].name||"（未命名）"}」？\n\n這個分類的主播會變回未分類，檔案搬回影片庫（不會刪任何影片）。按「儲存分類」後才會生效。`,"刪除","del"))return;E.splice(i,1);this.drawE();};});},
  drawT(){const C=this.C,f=$("#caF").value,q=(($("#caQ")||{}).value||"").trim().toLowerCase();const R=C.roster.filter(r=>(!f||(f==="none"?!r.cat:r.cat===f))&&(!q||String(r.name).toLowerCase().includes(q)||String(r.u).toLowerCase().includes(q)));      /* V0.6.61 文字搜尋 */if(!this.vt)this.vt=new VT($("#caT"),{key:"cats",filter:false,cols:[{t:"#",w:44,v:r=>p2(r.n),al:"c"},{t:"主播",w:200,v:r=>r.name},{t:"@帳號",w:150,v:r=>"@"+r.u},{t:"已直播",w:70,v:r=>r.sess||0,f:v=>v+" 場",al:"r"},{t:"MP4 合計",w:85,v:r=>r.mp4||0,f:v=>!v?"—":v>=1e9?(v/1e9).toFixed(1)+" GB":Math.max(1,Math.round(v/1e6))+" MB",al:"r"},{t:"鑽石",w:85,v:r=>r.dia||0,f:num,al:"r"},{t:"留言",w:75,v:r=>r.cmt||0,f:num,al:"r"},{t:"直播時長",w:80,v:r=>Math.round((r.dur||0)/3600),f:v=>v+" 小時",al:"r"},{t:"累積觀眾",w:85,v:r=>r.view||0,f:num,al:"r"},{t:"最高在線",w:80,v:r=>r.peak||0,f:num,al:"r"},{t:"錄到 %",w:65,v:r=>r.pct==null?"":r.pct,f:v=>v===""?"—":v+"%",al:"r"},{t:"最近開播",w:110,v:r=>r.last||0,f:v=>v?fmtHM(v):"—",al:"c"},{t:"分類",w:230,v:r=>r.cat,html:(v,r)=>`<select data-u="${esc(r.u)}" style="width:100%;padding:1px 4px"><option value="">○ 未分類</option>${C.cats.map(c=>`<option value="${c.id}"${c.id===v?" selected":""}>● ${esc(c.name)}（📁 ${esc(c.folder)}）</option>`).join("")}</select>`}]});
    this.vt.setRows(R);$("#caT").onchange=async e=>{const u=e.target.dataset.u;if(u==null)return;await catAssign(u,e.target.value);this.load();};},
  async save(){const cats=this.E.map(c=>({id:c.id,name:c.name.trim(),folder:(c.folder||c.name).trim(),color:c.color}));const j=await fetch(B+"/api/cats/save",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({cats})}).then(r=>r.json()).catch(()=>({ok:false,message:"連不到電腦"}));
    $("#caMsg").innerHTML=j.ok?`<span style="color:#45d483">✔ 分類已儲存，檔案在背景整理</span>`:`<span style="color:#ff5c5c">✖ ${esc(j.message||"沒有成功")}</span>`;if(j.ok){this.vt=null;this.load();}}};

/* ================= 10 主播清單 ================= */
/* V0.7.42.021 點「接下來可能開播」的名字：到主播清單、搜尋框填那位 */
/* V0.7.42.026 智慧功能狀態：點一行跳到那一頁 */
function smtGo(k){if(k==="pup"){if(typeof pupOpen==="function")pupOpen();return;}if(k==="nvexp"||k==="orphm"){window.LVS_KIND_NEXT=k==="nvexp"?"nv":"orph";go(42);return;}if(k==="ytauth")k="yt";   /* TK_V1.0.09 */
  const M={pfx:60,chv:13,today:51,dhealth:49,err:22,mem:16,smart:24,review:24,rescue:24,hl:33,reel:33,yt:34,disk:29,guard:30};if(M[k]==null)return;if(M[k]===24){const el=document.querySelector(k==="today"?".cgTd":k==="review"?".cgRv":k==="rescue"?".cgRq":".cgS");if(el){el.scrollIntoView({behavior:"smooth",block:"start"});return;}}go(M[k]);}
function soonPick(u){const f=()=>{const q=$("#stQ");if(!q)return false;q.value=u;PAGES[10].draw(true);return true;};if(!f()){go(10);setTimeout(f,350);}}
PAGES[10]={render(pg){pg.innerHTML=`<div class="pg"><div class="row"><h1 class="title">主播清單 Streamers</h1><span class="grow"></span><span class="sub" id="stC"></span><button id="stNv" title="批次設定：照常監控，只錄 M4A 聲音、不錄 MP4；可順便刪掉已存的 MP4">🎧 只錄聲音的主播</button><button id="stDeep" title="對久未開播和 0 場的主播，用 15 種不同方式測試連線">🔬 深度連線測試</button><button id="stEx">⇪ 匯出清單</button><button id="stIm">⇩ 匯入清單</button><input type="file" id="stImF" accept=".json" style="display:none"></div>
<div class="hero" style="margin-top:6px"><div class="row" style="align-items:stretch"><b style="align-self:center">新增／更新</b><textarea id="stAdd" class="grow" style="height:58px" placeholder="直接貼上：TikTok 主播網址（…/@帳號 或 …/@帳號/live）、[帳號](網址) 加下一行暱稱，或 @帳號。可一次貼多位；已存在的只更新暱稱。Ctrl+Enter 套用"></textarea><button class="start" id="stAddB">套用</button></div><div class="sub" id="stAddR" style="margin-top:4px"></div></div>
<div class="row" style="margin:8px 0 2px"><input id="stQ" placeholder="搜尋主播名稱 / @帳號…" style="width:260px"><span class="sub">拖曳格子調整排序 · 右鍵：編輯／重點／刪除 · 雙擊直播中的格子切換過去</span></div><div id="stSoon"></div><div id="stG"></div></div>`;
    $("#stQ").oninput=()=>this.draw(true);$("#stAddB").onclick=()=>this.add();$("#stAdd").onkeydown=e=>{if(e.key==="Enter"&&e.ctrlKey)this.add();};
    $("#stEx").onclick=()=>this.exportList();$("#stDeep").onclick=()=>deepDlg();$("#stNv").onclick=()=>nvOpen();$("#stIm").onclick=()=>$("#stImF").click();$("#stImF").onchange=e=>this.importList(e.target.files[0]);this.draw(true);},
  state(){this.draw(false);},
  async add(){const t=$("#stAdd").value.trim();if(!t)return;$("#stAddR").textContent="處理中…";const r=await fetch(B+"/add",{method:"POST",headers:{"Content-Type":"text/plain;charset=utf-8"},body:t});let j={};try{j=await r.json();}catch(e){}
    $("#stAddR").textContent=j.message||(r.ok?"完成":"沒有成功");if(r.ok)$("#stAdd").value="";pollState();stAskPrev(j,m=>{$("#stAddR").textContent=m;});},
  card(r){const cls=r.grace!=null?"grace":r.live?"live":r.priority?"pri":r.section==="stale"?"stale":"";const dot=r.grace!=null?"#f0ad4e":r.live?"#45d483":r.section==="stale"?"#9b6dff":"#7f8a99";
    const band=r.grace!=null?`訊號中斷 · 等待重連 剩 ${Math.floor(r.grace/60)}:${p2(r.grace%60)}`:r.live?`直播中 · ${num(r.viewers)} 人 · ${esc(r.elapsed)}${r.hlh?` · <span title="${esc(r.hlh.txt)}">✨${esc(r.hlh.ic)}</span>`:""}`:esc(r.text);   /* V0.7.42.029 */
    return `<div class="scard ${cls}" data-u="${esc(r.u)}" draggable="${r.section==="normal"?"true":"false"}" title="${p2(r.n)}　${esc(r.name)}　@${esc(r.u)}\n右鍵：編輯／重點／刪除　拖曳：調整排序">${avHtml(r.u,r.avatar,r.av,44,r.priority?"pri":r.live?"live":"")}
<div class="grow"><div class="row"><span class="no">${p2(r.n)}</span><span class="nm grow">${esc(r.name)}</span>${r.priority?'<span class="dot" style="background:#ff4d6d"></span>':""}<span class="dot" style="background:${dot}"></span></div>
<div class="row sub" style="font-size:11.5px"><span class="grow" style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap">@${esc(r.u)}</span>${r.live?`<span class="dia">💎 ${kf(r.diamonds)}</span> <span class="lik">♥ ${kf(r.likes)}</span>`:`<span>已記錄 ${r.sessions||0} 場</span>`}</div></div><div class="band">${band}</div></div>`;},
  draw(force){const s=S.st,g=$("#stG");if(!s||!g)return;const q=($("#stQ").value||"").toLowerCase();{const sb=$("#stSoon");if(sb){const h_=q?"":soonHtml();if(sb._h!==h_){sb._h=h_;sb.innerHTML=h_;}}soonLoad(()=>{if($("#stG"))this.draw(true);});}   /* V0.7.42.021 */const R=s.rooms.filter(r=>!q||(r.name+" "+r.u).toLowerCase().includes(q));
    $("#stC").textContent=`共 ${s.rooms.length} 位 · 直播中 ${s.rooms.filter(r=>r.live).length} 位 · ★重點 ${s.rooms.filter(r=>r.priority).length} 位`;
    const td=s.tier_days||[3,7];const sec=[["live","● 直播中","#45d483"],["normal",`未開播（${td[0]} 天內有開過）`,""],["d3",`超過 ${td[0]} 天未開播（不參與排序）`,"#9b6dff"],["d7",`超過 ${td[1]} 天未開播（不參與排序）`,"#7d5bd0"],["never","從沒開播過・0 場（不參與排序）","#8a8fa0"]];
    const h=sec.map(([k,t,c])=>{const L=R.filter(r=>k==="live"?r.live:(!r.live&&(r.tier||r.section)===k));if(!L.length)return"";return `<div class="shead" style="${c?"color:"+c:""}">${t}<span class="sub">${L.length} 位</span></div><div class="sgrid" style="--cols:${Math.max(3,Math.min(8,Math.floor(g.clientWidth/250)||5))}">${L.map(r=>this.card(r)).join("")}</div>`;}).join("");
    if(!force&&g._h===h)return;if(this.dragging)return;g._h=h;g.innerHTML=h;
    $$(".scard",g).forEach(c=>{const u=c.dataset.u;c.oncontextmenu=e=>{e.preventDefault();this.menu(u,e);};c.ondblclick=()=>{const r=s.rooms.find(x=>x.u===u);if(r&&r.live){S.tab={k:"live",u};go(0);}};
      c.ondragstart=e=>{this.dragging=u;c.classList.add("drag");e.dataTransfer.setData("text/plain",u);};c.ondragend=()=>{this.dragging=null;c.classList.remove("drag");};
      c.ondragover=e=>{if(this.dragging&&c.getAttribute("draggable")==="true"){e.preventDefault();c.classList.add("over");}};c.ondragleave=()=>c.classList.remove("over");
      c.ondrop=async e=>{e.preventDefault();c.classList.remove("over");const from=this.dragging;this.dragging=null;if(!from||from===u)return;const ids=s.rooms.map(r=>r.u);const i=ids.indexOf(from),j=ids.indexOf(u);ids.splice(i,1);ids.splice(j,0,from);
        const k=await post("/api/pc/streamer/order",{order:ids});if(k.ok){sb(`已將 ${from} 移到第 ${j+1} 位`);pollState();}else toast("✖ "+(k.message||"沒有成功"));};});},
  menu(u,e){const r=S.st.rooms.find(x=>x.u===u)||{u,name:u};menu([{label:`${r.name}　@${u}`,dis:true},{sep:1},{label:"✎ 編輯主播資訊",act:()=>editStreamer(u)},
    {label:r.priority?"☆ 取消重點標記":"★ 標記為重點（優先連線）",act:async()=>{const j=await post("/api/pc/streamer/priority",{u,on:!r.priority});if(j.ok)pollState();else toast("✖ "+(j.message||"沒有成功"));}},
    {label:"⟳ 重新查詢暱稱",act:async()=>{const j=await post("/api/pc/streamer/nick",{u});toast(j.ok?"已送出查詢":"✖ "+(j.message||"沒有成功"));}},
    r.live?{label:"▶ 切換到這個直播",act:()=>{S.tab={k:"live",u};go(0);}}:null,{label:"👤 主播總覽（開播時段、錄到幾成、等級）",act:()=>hostOpen(u)},{label:"🎞 GIF 製作（每格左右滑調時間）",act:()=>gfsOpen(u)},{label:"🕘 歷史紀錄（這位主播的所有場次）",act:()=>go(7,u)},{label:"🎞 檔案總管（只看這位：每場細節、剪輯）",act:()=>go(31,u)},{label:"🗂 審核（這位所有場次總覽、分級）",act:()=>go(38,u)},{label:"🖼 歷史縮圖（每場一格拼成一張大圖）",act:()=>go(41,u)},{label:"🌐 用瀏覽器開啟主頁",act:()=>window.open("https://www.tiktok.com/@"+encodeURIComponent(u),"_blank")},{label:"🔬 深度連線測試（15 種方式）",act:async()=>{const j=await post("/api/pc/deep/start",{users:[u]});if(j.ok)deepDlg(u);else toast("✖ "+(j.message||"沒有成功"));}},catSub(u),{sep:1},
    {label:"✖ 刪除主播",act:async()=>{if(!await confirmSteps([["刪除主播（1/3）",`確定要刪除「${r.name}　@${u}」嗎？\n\n歷史直播資料不會刪除。`,["del","cancel"]],["刪除主播（2/3）",`再確認一次：刪除後會停止監控「${r.name}」。`,["cancel","del"]],["刪除主播（3/3）",`最後確認：真的要刪除「${r.name}　@${u}」？`,["cancel","del","keep"]]]))return;
      const j=await post("/api/pc/streamer/delete",{u});if(j.ok){toast("✔ 已刪除");pollState();}else toast("✖ "+(j.message||"沒有成功"));}}],e.clientX,e.clientY);},
  exportList(){const R=S.st.rooms;const d=new Date(),stamp=d.getFullYear()+p2(d.getMonth()+1)+p2(d.getDate())+"_"+p2(d.getHours())+p2(d.getMinutes())+p2(d.getSeconds());
    const data={format:"TikLiveMonitor.streamers",version:1,app_version:S.st.ver,exported_at:d.toISOString(),streamers:R.map(r=>({uid:r.u,nickname:r.name}))};
    const a=document.createElement("a");a.href=URL.createObjectURL(new Blob([JSON.stringify(data,null,1)],{type:"application/json"}));a.download=`TikLive_主播清單_${stamp}.json`;a.click();toast(`已匯出 ${R.length} 位（照片要在電腦版匯出）`);},
  async importList(f){if(!f)return;let d;try{d=JSON.parse(await f.text());}catch(e){toast("✖ 看不懂這個檔案");return;}const L=(d.streamers||[]).map(x=>({u:String(x.uid||x.username||"").replace(/^@/,""),n:String(x.nickname||x.name||"")})).filter(x=>x.u);
    const have={};S.st.rooms.forEach(r=>have[r.u.toLowerCase()]=r);const rows=L.map(x=>{const h=have[x.u.toLowerCase()];return Object.assign(x,{st:!h?"new":(x.n&&x.n!==h.name?"diff":"same"),old:h?h.name:""});});
    dialog("匯入清單",`<div class="sub">檔案裡有 ${rows.length} 位：新主播 ${rows.filter(r=>r.st==="new").length} 位 · 暱稱不同 ${rows.filter(r=>r.st==="diff").length} 位 · 相同 ${rows.filter(r=>r.st==="same").length} 位</div><div style="max-height:50vh;overflow:auto;margin-top:8px"><table style="width:100%;font-size:12.5px">`+rows.map((r,i)=>`<tr><td><input type="checkbox" data-i="${i}"${r.st==="same"?" disabled":" checked"}></td><td>@${esc(r.u)}</td><td>${esc(r.n)}</td><td style="color:${r.st==="new"?"#45d483":r.st==="diff"?"#f0ad4e":"var(--subtext)"}">${r.st==="new"?"新主播（你目前沒有）":r.st==="diff"?`暱稱不同：${esc(r.old)} → ${esc(r.n)}`:"已存在（相同）"}</td></tr>`).join("")+"</table></div>",
      [["取消"],["套用匯入",()=>{const pick=$$(".dlg input[data-i]").filter(c=>c.checked).map(c=>rows[+c.dataset.i]);if(!pick.length)return;const text=pick.map(r=>`[${r.u}](https://www.tiktok.com/@${r.u})\n${r.n||r.u}`).join("\n");
        fetch(B+"/add",{method:"POST",headers:{"Content-Type":"text/plain;charset=utf-8"},body:text}).then(r=>r.json()).then(j=>{toast(j.message||"已匯入");pollState();stAskPrev(j,toast);}).catch(()=>toast("✖ 連不到電腦"));},"start"]]);}};
/* TK_V0.8.34.042 以前加過、後來刪掉的主播：列出來問要不要加回來 */
function stAskPz(j,say){if(!j||!j.pz||!j.pz.length)return Promise.resolve();const L=j.pz;   /* V1.1.62 封存中的主播又被新增：解封或取消 */
  return new Promise(res=>dialog("封存中的主播",`<div class="sub">這 ${L.length} 位目前封存中，要解封（移回來繼續監控）嗎？取消＝取消新增、維持封存。</div><div style="max-height:50vh;overflow:auto;margin-top:8px"><table style="width:100%;font-size:12.5px">`+L.map(p=>`<tr><td>${esc(p.name||p.u)}　@${esc(p.u)}${p.g?`　<b>${esc(p.g)}</b>`:""}</td></tr>`).join("")+`</table></div>`,
    [["取消",()=>{say("封存中的沒有新增（維持封存）");res();}],["解封",async()=>{try{const r=await fetch(B+"/add?ok=1&unp=1&src=pc",{method:"POST",headers:{"Content-Type":"text/plain;charset=utf-8"},body:L.map(p=>"@"+p.u).join("\n")});const k=await r.json();say(k.message||"已解封");pollState();}catch(e){say("✖ 連不到電腦");}res();},"start"]]));}
async function stAskPrev(j,say){await stAskPz(j,say);if(!j||!j.ask||!j.ask.length)return;const L=j.ask;
  dialog("以前加過的主播",`<div class="sub">這 ${L.length} 位以前加過、後來刪掉了，還要加回來嗎？（勾選要加的）</div><div style="max-height:50vh;overflow:auto;margin-top:8px"><table style="width:100%;font-size:12.5px">`+L.map((p,i)=>`<tr><td><input type="checkbox" data-pi="${i}"></td><td>${esc(p.text)}</td></tr>`).join("")+`</table></div>`,
    [["都不加",()=>say("以前加過的沒有加入")],["加入勾選的",async()=>{const pick=$$(".dlg input[data-pi]").filter(c=>c.checked).map(c=>L[+c.dataset.pi]);if(!pick.length){say("以前加過的沒有加入");return;}
      try{const r=await fetch(B+"/add?ok=1",{method:"POST",headers:{"Content-Type":"text/plain;charset=utf-8"},body:pick.map(p=>"@"+p.u).join("\n")});const k=await r.json();say(k.message||"已加入");pollState();}catch(e){say("✖ 連不到電腦");}},"start"]]);}
/* ================= 11 設定（和電腦版同一份設定：手機設定頁用的 /api/pcset） ================= */
PAGES[11]={render(pg,arg){pg.innerHTML=`<div class="pg fill"><div class="row"><h1 class="title">設定 Settings</h1><span class="grow"></span><input id="seQ" placeholder="搜尋設定…" style="width:240px"></div><div class="row" style="flex:1;min-height:0;align-items:stretch;gap:10px"><div class="setl panel" id="seL"></div><div class="grow" id="seR" style="overflow:auto;padding-right:4px"></div></div>
<div class="row"><span id="seDirty" style="color:#f0ad4e"></span><span class="grow"></span><button id="seDef">全部回復預設…</button><button id="seCan">取消</button><button class="start" id="seApply">套用</button></div></div>`;
    this.cat=typeof arg==="string"?arg:(this.cat||"monitor");this.ch={};$("#seQ").oninput=()=>this.drawR();$("#seCan").onclick=()=>{this.ch={};this.drawR();};$("#seApply").onclick=()=>this.apply();
    $("#seDef").onclick=async()=>{if(!await confirmDlg("全部回復預設","把所有設定改回預設值？（按「套用」後才會儲存）"))return;this.I.items.forEach(x=>{if(!x.lock&&JSON.stringify(x.value)!==JSON.stringify(x.default))this.ch[x.key]=x.default;});this.drawR();};this.load();},
  async load(){this.I=await api("/api/pcset");if(!$("#seL"))return;if(!this.I.cats.some(c=>c.key==="network"))this.I.cats.push({key:"network",name:"網路用量",desc:"下載速度與每日／每月／每季流量統計"});this.drawL();this.drawR();},
  drawL(){const COM=["monitor","record","stt","gfx","notify"],cs=this.I.cats,com=COM.map(k=>cs.find(c=>c.key===k)).filter(Boolean),adv=cs.filter(c=>!COM.includes(c.key));   /* V0.6.95 常用／進階分開，名字下面有說明 */
    const it=c=>`<div data-c="${c.key}" class="${c.key===this.cat?"on":""}" title="${esc(c.desc)}"><b style="font-weight:700">${esc(c.name)}</b><small style="display:block;font-size:10.5px;opacity:.65;font-weight:400;line-height:1.3;margin-top:1px">${esc(c.desc||"")}</small></div>`;
    $("#seL").innerHTML=`<p class="sub" style="margin:4px 6px 2px;font-size:11px;font-weight:800">常用</p>`+com.map(it).join("")+`<p class="sub" style="margin:10px 6px 2px;font-size:11px;font-weight:800">進階</p>`+adv.map(it).join("");
    $$("#seL div[data-c]").forEach(d=>d.onclick=()=>{this.cat=d.dataset.c;this.drawL();this.drawR();});},
  val(x){return this.ch[x.key]!==undefined?this.ch[x.key]:x.value;},
  ctl(x){const v=this.val(x),dis=x.lock?" disabled":"";if(x.kind==="bool")return `<label><input type="checkbox" data-k="${x.key}"${v?" checked":""}${dis}> 啟用</label>`;
    if(x.kind==="choice")return `<select data-k="${x.key}"${dis} style="min-width:200px">${(x.choices||[]).map(([l,cv])=>`<option value="${esc(JSON.stringify(cv))}"${JSON.stringify(cv)===JSON.stringify(v)?" selected":""}>${esc(l)}</option>`).join("")}</select>`;
    if(x.kind==="int"||x.kind==="float")return `<span class="num"><button data-d="-1" data-k="${x.key}"${dis}>－</button><input data-k="${x.key}" value="${v}"${dis}><button data-d="1" data-k="${x.key}"${dis}>＋</button><span class="sub">${esc(x.suffix||"")}</span></span>`;
    return `<input data-k="${x.key}" value="${esc(v)}"${dis} style="min-width:240px">`;},
  drawR(){const q=$("#seQ").value.trim().toLowerCase(),I=this.I;const items=I.items.filter(x=>q?(x.label+" "+(x.help||"")).toLowerCase().includes(q):x.cat===this.cat);const c=I.cats.find(c=>c.key===this.cat)||{};
    const dtxt=x=>x.kind==="bool"?(x.default?"啟用":"關閉"):x.kind==="choice"?((x.choices||[]).find(([l,cv])=>JSON.stringify(cv)===JSON.stringify(x.default))||[x.default])[0]:x.default+(x.suffix||"");
    let h=q?`<h2 style="margin:4px 0">搜尋「${esc(q)}」</h2>`:`<h2 style="margin:4px 0">${esc(c.name||"")}</h2><div class="sub" style="margin-bottom:8px">${esc(c.desc||"")}</div>`;
    h+=items.map(x=>`<div class="srow${this.ch[x.key]!==undefined?" dirty":""}"><div class="r0"><b>${esc(x.label)}${x.restart?'<span class="sub">　⟳ 需重開</span>':""}${x.lock?'<span class="sub">　🔒 只能在電腦上改</span>':""}</b>${this.ctl(x)}</div><div class="r1">${esc(x.help||"")}　預設：${esc(dtxt(x))}</div></div>`).join("")||`<div class="sub">沒有符合的設定</div>`;
    if(!q&&this.cat==="network")h+=`<div class="srow"><b>流量統計</b><div id="seNet" class="sub">讀取中…</div></div>`;
    if(!q&&this.cat==="tools")h+=`<div class="srow sub">資料存放位置、資料庫匯出／匯入、開啟資料夾等工具會操作電腦上的檔案，請在電腦本機的設定頁使用。</div>`;
    $("#seR").innerHTML=h;const n=Object.keys(this.ch).length;$("#seDirty").textContent=n?`● ${n} 項尚未套用（按「套用」才會儲存，「取消」還原）`:"";
    const get=k=>I.items.find(x=>x.key===k);
    $$("#seR [data-k]").forEach(el=>{const x=get(el.dataset.k);if(!x)return;
      if(el.tagName==="BUTTON")el.onclick=()=>{const step=x.step||1,cur=+this.val(x)||0;let v=+(cur+step*(+el.dataset.d)).toFixed(x.kind==="float"?1:0);if(x.min!=null)v=Math.max(x.min,v);if(x.max!=null)v=Math.min(x.max,v);this.set(x,v);};
      else el.onchange=()=>{let v;if(x.kind==="bool")v=el.checked;else if(x.kind==="choice")v=JSON.parse(el.value);else if(x.kind==="int")v=parseInt(el.value)||0;else if(x.kind==="float")v=parseFloat(el.value)||0;else v=el.value;this.set(x,v);};});
    if($("#seNet"))this.net();},
  set(x,v){if(JSON.stringify(v)===JSON.stringify(x.value))delete this.ch[x.key];else this.ch[x.key]=v;const st=$("#seR").scrollTop;this.drawR();$("#seR").scrollTop=st;},
  async apply(){if(!Object.keys(this.ch).length){toast("沒有要套用的變更");return;}const j=await post("/api/pcset",{changes:this.ch});if(!j.ok){dialog("套用失敗",esc(j.message||"沒有成功"));return;}
    this.ch={};this.I=j.info||this.I;this.drawR();toast(`✔ 已套用並儲存（${(j.changed||[]).length} 項）`+((j.restart||[]).length?`；${j.restart.join("、")} 下次開啟程式完全生效`:""),4000);},
  async net(){const d=await api("/api/pc/net");const el=$("#seNet");if(!el)return;const fs=b=>{b=+b||0;return b>=1099511627776?(b/1099511627776).toFixed(2)+" TB":b>=107374182400?(b/1073741824).toFixed(0)+" GB":b>=1073741824?(b/1073741824).toFixed(1)+" GB":(b/1048576).toFixed(0)+" MB";};
    el.innerHTML=`<table style="width:100%;margin-top:6px"><tr><td>期間</td><td align="right">下載</td><td align="right">上傳</td><td align="right">其中錄影下載</td></tr>`+d.periods.map(r=>`<tr style="color:var(--text)"><td>${esc(r[0])}</td><td align="right">${fs(r[1])}</td><td align="right">${fs(r[2])}</td><td align="right">${fs(r[3])}</td></tr>`).join("")+`</table><b style="display:block;margin-top:10px;color:var(--text)">最近 31 天</b><table style="width:100%"><tr><td>日期</td><td align="right">下載</td><td align="right">上傳</td><td align="right">錄影</td></tr>`+
      d.days.map(r=>{const any=r[1]||r[2]||r[3];return `<tr style="color:var(--text)"><td>${esc(r[0])}</td><td align="right">${any?fs(r[1]):"—"}</td><td align="right">${any?fs(r[2]):""}</td><td align="right">${any?fs(r[3]):""}</td></tr>`;}).join("")+"</table>";}};
/* ================= 9 連線診斷 ================= */
PAGES[9]={render(pg){pg.innerHTML=`<div class="pg fill"><h1 class="title">連線診斷 Diagnostics</h1><div class="panel" style="margin:6px 0"><span class="sec">🛠 網路處理（不影響 OlivePro 等其他軟體）</span> <button data-net="diag">🔍 診斷</button> <button data-net="flushdns">🧹 清 DNS 快取</button> <button data-net="rebuild">♻️ 重建這支程式的連線</button> <button data-restart="1" style="color:#ff6577">🔄 重新啟動主程式</button> <a href="javascript:void(0)" onclick="go(22)">看診斷結果與處理紀錄 →</a></div><div class="sub">手動勾選問題主播。每位最多自動診斷 3 次；單次失敗後等待 5 秒再重試，成功即停止。輸出會顯示卡在 ID、Sign、HTTP、WebSocket、ConnectEvent 或斷線哪一段。</div>
<div class="panel"><div class="sec">🩺 連線狀況（依每位主播最近的連線結果自動判斷）</div><div id="dgV" style="margin:6px 0;line-height:1.6">讀取中…</div><div class="row"><input id="dgU" class="grow" placeholder="輸入一位你「確定正在直播」的主播 @帳號（選填）"><button id="dgP">🔎 主動檢查</button><button id="dgR">↻</button></div><div id="dgT" style="height:240px;display:flex;flex-direction:column;margin-top:6px"></div></div>
<div class="panel row"><b>⚡ 快速檢查（TikTokLive 網頁查詢，不經簽章伺服器）</b><span class="grow"></span><button id="dgQ1">檢查勾選</button><button id="dgQ2">檢查全部主播</button></div>
<div class="row"><input id="dgS" class="grow" placeholder="搜尋主播 / @帳號…"><button id="dgA">全選</button><button id="dgC">清除</button><button class="start" id="dgGo">▶ 開始診斷</button><button id="dgStop">■ 停止</button></div>
<div class="row" style="flex:1;min-height:200px;align-items:stretch;gap:8px"><div class="panel" id="dgL" style="width:330px;overflow:auto"></div><div class="log grow" id="dgLog"></div></div></div>`;
    this.vt=new VT($("#dgT"),{key:"conn",filter:false,cols:[{t:"狀況",w:230,v:r=>r.icon+" "+r.label},{t:"主播",w:200,v:r=>r.name!==r.u?r.name+" @"+r.u:"@"+r.u},{t:"最近結果",w:240,v:r=>(r.t?fmtHM(r.t):"")+(r.etype?" · "+r.etype:"")+(r.http?" · HTTP "+r.http:"")},{t:"連續失敗",w:80,v:r=>r.fails||"",al:"c"},{t:"上次連上",w:100,v:r=>r.ok_t?fmtHM(r.ok_t):"",al:"c"},{t:"原始訊息",w:500,v:r=>r.msg||""}]});
    $("#dgR").onclick=()=>this.conn();$("#dgP").onclick=async()=>{const j=await post("/api/conn/probe",{u:$("#dgU").value.trim()});if(j.ok===false)toast(j.message||"沒有成功");setTimeout(()=>this.conn(),500);};
    const users=()=>$$("#dgL input:checked").map(c=>c.value);$("#dgA").onclick=()=>$$("#dgL input").forEach(c=>{if(c.parentNode.style.display!=="none")c.checked=true;});$("#dgC").onclick=()=>$$("#dgL input").forEach(c=>c.checked=false);
    $("#dgS").oninput=e=>{const q=e.target.value.toLowerCase();$$("#dgL label").forEach(l=>l.style.display=l.textContent.toLowerCase().includes(q)?"":"none");};
    $("#dgQ1").onclick=()=>this.quick(users());$("#dgQ2").onclick=()=>this.quick(S.st.rooms.map(r=>r.u));
    $("#dgGo").onclick=async()=>{const u=users();if(!u.length){dialog("沒有選擇","請先勾選至少一位主播。");return;}const j=await post("/api/pc/diag/start",{users:u});if(!j.ok){toast(j.message||"已經在診斷中");return;}this.logMode="diag";this.li=0;$("#dgLog").textContent="";this.pollLog();};
    $("#dgStop").onclick=()=>post("/api/pc/diag/stop",{});this.list();this.conn();},
  leave(){clearTimeout(this.ct);clearTimeout(this.lt);},
  list(){if(!S.st){setTimeout(()=>this.list(),500);return;}$("#dgL").innerHTML=S.st.rooms.map(r=>`<label style="display:block;padding:2px 0"><input type="checkbox" value="${esc(r.u)}"> @${esc(r.u)}  ${esc(r.name)}</label>`).join("");},
  async conn(){clearTimeout(this.ct);let d;try{d=await api("/api/conn");}catch(e){}if(!$("#dgV"))return;if(d&&!d.error){const v=d.verdict,col={bad:"#ff5c5c",warn:"#f0ad4e",ok:"#45d483"}[v.level]||"var(--text)";const C=d.cats,P=d.probe||{};
      $("#dgV").innerHTML=`<span style="font-size:16px;font-weight:800;color:${col}">${esc(v.title)}</span><br>${esc(v.detail)}`+v.advice.map(a=>`<br>　• ${esc(a)}`).join("")+`<br><span class="sub">監控 ${d.n_mon}/${d.n_roster} 位 · 直播中 ${d.n_live} 位${d.expected!=null?`；平常這個時段約 ${Math.round(d.expected)} 位在直播`:""}<br>${Object.entries(d.counts).sort((a,b)=>b[1]-a[1]).filter(([k])=>C[k]).map(([k,n])=>`${C[k][0]} ${esc(C[k][1])} <b>${n}</b>`).join("　")}</span>`+
        (P.users?`<br><b>主動檢查</b>（${fmtHM(P.t)}）${P.running?"：檢查中…":""}　${(P.results||[]).map(r=>`@${esc(r.user)} ${esc(r.label)}${r.known_live?"（你確定在播）":""}`).join("　")}`:"");this.vt.setRows(d.rows);}
    this.ct=setTimeout(()=>this.conn(),d&&d.probe&&d.probe.running?2500:10000);},
  async quick(users){if(!users.length){dialog("沒有選擇","請先勾選主播，或按「檢查全部主播」。");return;}const j=await post("/api/pc/quick/start",{users});if(!j.ok){toast("已經在檢查中");return;}this.logMode="quick";$("#dgLog").textContent="";this.pollLog();},
  async pollLog(){clearTimeout(this.lt);if(!$("#dgLog"))return;let j;if(this.logMode==="quick"){j=await api("/api/pc/quick");$("#dgLog").textContent=(j.lines||[]).join("\n");}else{j=await api("/api/pc/diag?from="+(this.li||0));if(j.lines&&j.lines.length){$("#dgLog").textContent+=(this.li?"\n":"")+j.lines.join("\n");this.li=j.n;}}
    const L=$("#dgLog");L.scrollTop=1e9;if(j.running)this.lt=setTimeout(()=>this.pollLog(),800);}};
/* ================= 14 線上更新 ================= */
PAGES[14]={render(pg){pg.innerHTML=`<div class="pg"><h1 class="title">線上更新 Update</h1><div class="sub">更新時監控與錄音不會中斷。選擇或拖曳更新包（TK_V版本_Update.zip）→ 開始更新；完成後電腦上的程式會自動重整為新版本，這個網頁也會重新載入。</div>
<div id="cuIn" style="margin-top:8px"></div><div class="hero" style="margin-top:8px"><div class="sec" id="upCur">目前版本：V${esc(S.st?S.st.ver:"")}</div><div class="drop" id="upDrop" style="margin-top:8px">把 TK_V版本_Update.zip 拖到這裡，或 <button id="upPick">選擇更新包…</button><input type="file" id="upF" accept=".zip" style="display:none"></div><div id="upDl" style="margin-top:8px"></div><div id="upInfo" style="margin-top:8px"></div><div class="row" style="margin-top:8px"><span class="grow"></span><button class="start" id="upGo" disabled>開始更新</button></div></div>
<div class="hero" style="margin-top:10px"><div class="sec">退回前一版</div><div class="sub">更新後如果出狀況，可以從這裡退回前兩個版本（每次更新前都會自動備份）。退回時監控與錄音一樣不會中斷。</div><div id="upRb" style="margin-top:6px"></div></div></div>`;
    const dz=$("#upDrop");$("#upPick").onclick=()=>$("#upF").click();$("#upF").onchange=e=>this.upload(e.target.files[0]);dz.ondragover=e=>{e.preventDefault();dz.classList.add("over");};dz.ondragleave=()=>dz.classList.remove("over");dz.ondrop=e=>{e.preventDefault();dz.classList.remove("over");this.upload(e.dataTransfer.files[0]);};
    $("#upGo").onclick=()=>this.apply();cuMount($("#cuIn"));this.rb();this.dl();if(S.updDlGo){S.updDlGo=0;setTimeout(()=>this.dlUse(),200);}},
  /* TK_V0.9.47 跟 VS 一樣：下載資料夾有比現在新的更新包 → 這裡直接列出來，按一下就檢查（還是要按「開始更新」） */
  async dl(){let d=null;try{d=await api("/api/update/dl");}catch(e){}const el=$("#upDl");if(!el)return;const f=d&&d.found;
    el.innerHTML=f?`<div class="row" style="padding:8px 10px;border:1px solid #ff2d55;border-radius:10px;background:rgba(255,45,85,.08)"><div class="grow">🆕 <b>下載資料夾有新的更新包</b>　${esc(f.name)}（V${esc(d.cur)} → <b>V${esc(f.ver)}</b>）<br><span class="sub">${esc(d.dir)}</span></div><button class="start" id="upDlGo">⚡ 用這個更新包</button></div>`:`<div class="sub">下載資料夾（${esc((d&&d.dir)||"")}）裡沒有比現在新的更新包；下載好會自動出現在這裡和右上角。</div>`;
    const b=$("#upDlGo");if(b)b.onclick=()=>this.dlUse();},
  async dlUse(){$("#upInfo").textContent="讀取下載資料夾的更新包、檢查中…";let r,j={};try{r=await fetch(B+"/api/update/dl/prep",{method:"POST",cache:"no-store"});j=await r.json();}catch(e){}
    this.show(j);},
  async upload(f){if(!f)return;$("#upInfo").textContent="上傳中…";let j={};try{const r=await fetch(B+"/api/update/upload?name="+encodeURIComponent(f.name),{method:"POST",body:f});j=await r.json();}catch(e){j={message:"連不到電腦或上傳中斷，請再試一次"};}
    this.show(j);},
  show(j){if(!j.ok){$("#upInfo").innerHTML=`<span style="color:#ff5c5c">✖ ${esc(j.message||"上傳失敗")}</span>`;return;}this.tok=j.tok;
    $("#upInfo").innerHTML=`<b>V${esc(j.from)} → V${esc(j.to)}</b>（${j.cmp>0?"升級":j.cmp===0?"相同版本":"⚠ 降版"}）<br>`+(j.notes||[]).map(n=>"• "+esc(n)).join("<br>")+`<br>${j.core?'<span style="color:#f0ad4e">本次含核心變更：正在進行的監控會沿用目前核心，下次重開程式才完全生效。</span>':'<span style="color:#45d483">只更新介面，可完全熱更新。</span>'}`;$("#upGo").disabled=false;},
  async apply(){if(!await confirmDlg("確認更新","開始更新？\n\n更新期間監控與錄音不會中斷，完成後電腦上的程式會自動重整為新版本。"))return;const j=await post("/api/update/apply",{tok:this.tok});if(!j.ok){dialog("更新失敗",esc(j.message||"沒有成功"));return;}$("#upGo").disabled=true;$("#upInfo").innerHTML+="<br><b style='color:#45d483'>✓ 檔案已更新，電腦正在重整為新版本…</b>";this.wait();},
  async wait(){for(let i=0;i<90;i++){await new Promise(r=>setTimeout(r,2000));try{const s=await api("/api/update/status");if(s.status&&s.status.state==="failed"){dialog("更新失敗",esc(s.status.message||""));return;}if(s.status&&s.status.state==="done"){toast("✔ 更新完成，重新載入網頁…");setTimeout(()=>location.reload(),1500);return;}}catch(e){}}},
  async rb(){const j=await api("/api/update/rollback");const el=$("#upRb");if(!el)return;el.innerHTML=(j.items||[]).map(x=>`<div class="row" style="padding:4px 0"><div class="grow"><b>V${esc(x.version)}</b>　<span class="sub">備份於 ${esc(x.time)}${x.older?"":"（比目前新）"}</span><br><span class="sub">${esc((x.notes||[]).slice(0,3).join("；"))}</span></div><button data-id="${esc(x.id)}" data-v="${esc(x.version)}">退回 V${esc(x.version)}</button></div>`).join("")||`<div class="sub">目前沒有可以退回的備份。</div>`;
    $$("#upRb button").forEach(b=>b.onclick=async()=>{if(!await confirmDlg("退回版本",`確定從 V${S.st.ver} 退回 V${b.dataset.v}？\n\n監控與錄音不會中斷，完成後畫面自動重整。`))return;const k=await post("/api/update/rollback",{id:b.dataset.id});if(!k.ok){dialog("退回失敗",esc(k.message||""));return;}toast("退回中…");this.wait();});}};
/* ================= 13 升級資訊 ================= */
PAGES[13]={render(pg){pg.innerHTML=`<div class="pg"><div id="chvP" class="panel" style="margin-top:8px"></div></div>`;chvMount($("#chvP"));}};   /* V0.7.42.042 🆕 版本與更新（搜尋、收合、新的標 🆕） */

/* ================= V0.6.04 深度連線測試（久未開播／0 場） ================= */
const DEEP_CODE={LIVE:"🟢 直播中",ROOM:"✔ 有直播間",OFFLINE:"✔ 沒開播",EXISTS:"✔ 帳號存在",NO_ROOM:"○ 沒直播間",NOT_FOUND:"✖ 找不到",LOGIN:"🔒 需登入",BLOCKED:"⛔ 被擋",WAF:"⛔ 防火牆",REGION:"🌐 地區",NET:"⚠ 網路",SIGN:"⚠ 簽章",ERR:"⚠ 錯誤",SKIP:"— 略過"};
const DEEP_COL={LIVE:"#45d483",READY:"#45d483",GONE:"#ff4d6d",BLOCKED:"#f0ad4e",LOGIN:"#f0ad4e"};
function deepDlg(sel){let P=null,cur=sel||null,timer=0;
  const bg=dialog("🔬 深度連線測試（久未開播／0 場主播）",`<div class="sub">對每位主播依序試 15 種方式（API 電腦／手機／台灣參數、oEmbed、個人頁、直播頁電腦／手機、瀏覽器暖身、secUid、TikTokLive 三種、check_alive、room/info、和監控相同的完整連線）。一次只測一位、每種方式間隔 2.5 秒，不影響正在進行的監控。</div>
<div class="row" style="margin:8px 0"><button class="start" id="dpAll">▶ 測試全部久未開播＋0 場</button><button id="dpStop">■ 停止</button><span class="sub grow" id="dpSt"></span></div>
<div style="display:flex;gap:10px;height:56vh"><div style="flex:1.2;overflow:auto" class="panel"><table class="dpt" style="width:100%;font-size:12.5px"><thead><tr><th>主播</th><th>分層</th><th>上次直播</th><th>結論</th><th>回應</th><th>測試時間</th></tr></thead><tbody id="dpB"></tbody></table></div>
<div style="flex:1;overflow:auto" class="panel" id="dpD"><div class="sub">點左邊一位看 15 種方式的結果</div></div></div>`,[["關閉"]]);
  const box=bg.querySelector(".dlg");if(box){box.style.width="min(1180px,96vw)";box.style.maxWidth="96vw";}
  const tierTxt=t=>({d3:`超過 ${P.tier_days[0]} 天`,d7:`超過 ${P.tier_days[1]} 天`,never:"0 場",normal:"近期有開",live:"直播中"}[t]||"");
  function det(){const d=$("#dpD");if(!d||!P||!cur)return;const r=P.results[cur];const live=P.cur===cur;const M=(live?P.steps:(r&&r.methods))||[];
    d.innerHTML=`<div style="margin-bottom:6px"><b>@${esc(cur)}</b>　${live?"⏳ 測試中…":r?`<b style="color:${DEEP_COL[r.verdict]||"inherit"}">${r.icon} ${esc(r.label)}</b>：${esc(r.why)}`:"還沒測試"}</div>`+
      `<table style="width:100%;font-size:12px"><tr><th>#</th><th>方式</th><th>結果</th><th>細節</th></tr>`+M.map((m,i)=>`<tr><td>${i+1}</td><td>${esc(m.name)}</td><td style="white-space:nowrap">${DEEP_CODE[m.code]||esc(m.code)}</td><td class="sub">${esc(m.detail)}</td></tr>`).join("")+`</table>`;}
  async function load(){if(!document.body.contains(bg)){clearInterval(timer);return;}try{P=await api("/api/pc/deep");}catch(e){return;}
    $("#dpSt").textContent=P.running?`測試中：@${P.cur||"…"}（第 ${P.steps.length}/15 種）· 已完成 ${P.done}/${P.total} 位 · 排隊 ${P.queue.length} 位`:`待測對象 ${P.targets.length} 位 · 已有結果 ${Object.keys(P.results).length} 位`;
    $("#dpStop").disabled=!P.running;const ord={never:0,d7:1,d3:2};const R=P.rows.slice().sort((a,b)=>(ord[a.tier]??9)-(ord[b.tier]??9)||a.u.localeCompare(b.u));
    $("#dpB").innerHTML=R.map(x=>{const r=x.r,c=x.u===P.cur,q=P.queue.includes(x.u);return `<tr data-u="${esc(x.u)}" style="cursor:pointer${x.u===cur?";background:var(--selection)":""}"><td>${esc(x.name)}<div class="sub">@${esc(x.u)}</div></td><td>${tierTxt(x.tier)}</td><td class="sub">${esc((x.text||"").split(" · 測：")[0])}</td><td style="color:${r&&!c?DEEP_COL[r.verdict]||"inherit":"inherit"}" title="${r?esc(r.why):""}">${c?"⏳ 測試中…":q?"… 排隊中":r?r.icon+" "+esc(r.label):"— 未測試"}</td><td>${r?r.useful+"/"+r.n:""}</td><td class="sub">${r?new Date(r.t*1000).toLocaleString("zh-TW",{month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit"}):""}</td></tr>`;}).join("");
    $$("#dpB tr").forEach(tr=>tr.onclick=()=>{cur=tr.dataset.u;load();});det();}
  $("#dpAll").onclick=async()=>{const j=await post("/api/pc/deep/start",{all:true});toast(j.ok?`已加入 ${j.n} 位`:"✖ "+(j.message||"沒有成功"));load();};
  $("#dpStop").onclick=async()=>{await post("/api/pc/deep/stop",{});load();};
  load();timer=setInterval(load,2000);}

/* ================= 22 匯出 LOG（V0.6.23） ================= */
PAGES[22]={render(pg){const pad=n=>String(n).padStart(2,"0"),loc=t=>{const d=new Date(t);return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;};
  pg.innerHTML=`<div class="pg"><h1 class="title">LOG 與問題</h1><div id="isu">${issuesHtml(S.isu)}</div><div class="sec" style="margin-top:12px">📤 匯出 LOG</div><div class="sub">把一段時間內所有紀錄（連線事件、每分鐘網路請求數、斷線／重試、錯誤、異常、設定）打包成一個 zip，下載後可以傳給別人分析。連線事件從 V0.6.23 開始記錄（保留 7 天）。</div>
<div class="panel" style="margin-top:8px"><div class="row wrap">${[[30,"最近 30 分鐘"],[60,"最近 1 小時"],[180,"最近 3 小時"],[720,"最近 12 小時"]].map(([m,t])=>`<button data-m="${m}">${t}</button>`).join("")}
<span style="margin-left:14px">自訂</span><input type="datetime-local" id="lxF" value="${loc(Date.now()-1800e3)}"><span>～</span><input type="datetime-local" id="lxT" value="${loc(Date.now())}"><button class="start" id="lxGo">匯出這段時間</button></div>
<div id="lxR" style="margin-top:8px"></div></div><div class="panel" style="margin-top:8px"><div class="sec">之前匯出的</div><div id="lxL" class="sub">讀取中…</div></div></div>`;
  const dl=n=>`${B}/api/pc/logx/dl?f=${encodeURIComponent(n)}`,kb=b=>(b/1024).toFixed(0)+" KB";
  const list=async()=>{const j=await api("/api/pc/logx/list");$("#lxL").innerHTML=(j.items||[]).length?`<table style="width:100%;font-size:12.5px">`+j.items.map(x=>`<tr><td>${esc(x.name)}</td><td align="right">${kb(x.bytes)}</td><td align="right">${fmtHM(x.t)}</td><td align="right"><a href="${dl(x.name)}" download="${esc(x.name)}">⬇ 下載</a></td></tr>`).join("")+"</table>":"還沒有匯出過";};
  const make=async qs=>{$("#lxR").innerHTML=`<div class="sub">⏳ 正在整理紀錄…</div>`;const j=await api("/api/pc/logx/make?"+qs);
    if(j.error){$("#lxR").innerHTML=`<div style="color:#ff6577">✖ ${esc(j.error)}</div>`;return;}
    $("#lxR").innerHTML=`<div>✔ ${esc(j.from)} ～ ${esc(j.to)}，${num(j.lines)} 行，${kb(j.bytes)}　<a href="${dl(j.name)}" download="${esc(j.name)}"><b>⬇ 下載 ${esc(j.name)}</b></a></div><pre style="white-space:pre-wrap;font-size:11.5px;max-height:55vh;overflow:auto;background:var(--panel2,rgba(127,127,127,.08));border-radius:8px;padding:8px;margin-top:6px">${esc(j.summary||"")}</pre>`;list();};
  pg.querySelectorAll("[data-m]").forEach(b=>b.onclick=()=>make("min="+b.dataset.m));
  $("#lxGo").onclick=()=>{const f=new Date($("#lxF").value).getTime()/1000,t=new Date($("#lxT").value).getTime()/1000;if(!f||!t||t<=f){toast("時間不對");return;}make(`from=${f}&to=${t}`);};list();
  issuesRefresh();clearInterval(this.iv);this.iv=setInterval(()=>{if(!$("#isu")){clearInterval(this.iv);return;}if(!document.hidden)issuesRefresh();},10000);}};
async function issuesRefresh(){try{const j=await api("/api/pc/issues");S.isu=j;const el=$("#isu");if(el){const h=issuesHtml(j);if(el._h!==h){el._h=h;el.innerHTML=h;}}}catch(e){}}
/* ================= V0.6.46 23 送禮動畫（共用的 gfxPageHtml / gfxBind；試播會在這一頁的示範框播） ================= */
PAGES[23]={async render(pg){pg.innerHTML=`<div class="pg"><div class="row"><h1 class="title">送禮動畫</h1><span class="grow"></span><span class="sub">直播總覽、歷史回放、手機網頁、主程式畫面都會播；門檻與停留時間在「設定 → 送禮動畫」</span></div><div id="gfxP" class="sub">讀取中…</div></div>`;
    await gfxLoad(true);this.draw();},
  draw(){const el=$("#gfxP");if(!el)return;el.className="";el.innerHTML=gfxPageHtml();gfxBind(el,()=>this.draw());},
  leave(){}};
/* ================= V0.6.47 24 連線管控／主播縮編（共用的 cgStatusHtml / cgRosterHtml / cgBind） ================= */
PAGES[37]={render(pg){pg.innerHTML=`<div class="pg"><div id="emgP" class="panel" style="margin-top:8px"></div></div>`;emgMount($("#emgP"));}};   /* V0.8.04 🚨 緊急處理 */
PAGES[38]={render(pg,arg){pg.innerHTML=`<div class="pg fill"><div id="rvRoot" style="flex:1;min-height:0"></div></div>`;rvMount($("#rvRoot"),arg||"");}};   /* V0.8.13 🗂 主播審核 */
PAGES[44]={render(pg,arg){const hu=typeof arg==="string"?arg.replace(/^@/,""):"";pg.innerHTML=`<div class="pg fill">${hu?`<div class="rvxH" style="display:flex;gap:8px;align-items:center;padding:6px 8px"><button onclick="go(44)">‹ 全部剪輯</button><b>📁 @${hu.replace(/[<>&"]/g,"")} 的剪輯影片</b></div>`:""}<div id="clpRoot" style="flex:1;min-height:0;overflow:auto"></div></div>`;clpMount($("#clpRoot"),hu?{u:hu}:null);}};   /* TK_V0.9.16 ✂ 初剪片段 */
PAGES[43]={render(pg){pg.innerHTML=`<div class="pg"><h2>⏯ 精選／審核 開關</h2><div id="featRoot" class="panel" style="padding:12px;max-width:640px"></div></div>`;featMount($("#featRoot"));}};   /* TK_V0.8.93 */
PAGES[42]={render(pg){pg.innerHTML=`<div class="pg fill"><div id="lvsRoot" style="flex:1;min-height:0;display:flex;flex-direction:column"></div></div>`;lvsMount($("#lvsRoot"),{pc:true});}};   /* TK_V0.8.97 網頁版照 VideoSift 版面；TK_V0.8.88 ⇣ 連續分級 */
PAGES[41]={render(pg,arg){pg.innerHTML=`<div class="pg" style="overflow:auto"><div id="htbRoot"></div></div>`;htbMount($("#htbRoot"),arg||"");}};   /* TK_V0.8.35 🖼 歷史縮圖 */
PAGES[40]={render(pg){pg.innerHTML=`<div class="pg"><div id="culP" class="panel" style="margin-top:8px"></div></div>`;culMount($("#culP"));}};   /* V0.8.25 🌐 Chrome 上傳自動限速 */
PAGES[39]={render(pg){pg.innerHTML=`<div class="pg"><div id="expP" class="panel" style="margin-top:8px"></div></div>`;expMount($("#expP"));}};   /* TK_V0.8.18.002 🧪 實驗工作區 */
PAGES[36]={render(pg){pg.innerHTML=`<div class="pg"><div id="wkrP" class="panel" style="margin-top:8px"></div></div>`;wkrMount($("#wkrP"));}};   /* V0.7.42.036 📰 每週報告 */
PAGES[24]={render(pg){pg.innerHTML=`<div class="pg"><div class="row"><h1 class="title">連線管控／主播縮編</h1><span class="grow"></span><span class="sub">設定 → 連線管控 可以改每分鐘上限、放慢倍數</span></div><div id="smtP" style="margin-top:8px"></div><div id="cgP" class="panel" style="margin-top:8px"></div></div>`;smtLoad($("#smtP"));   /* V0.7.42.026 智慧功能狀態 */
    const el=$("#cgP"),draw=()=>{if($("#cgP")===el)el.innerHTML=cgPageHtml();};cgBind(el,draw);cgLoad(el,draw);
    clearInterval(this.iv);this.iv=setInterval(async()=>{if(!$("#cgP")){clearInterval(this.iv);return;}try{CG.info=await cgGet("/api/pc/cg");const s=el.querySelector(".cgS");if(s){const t=document.createElement("div");t.innerHTML=cgStatusHtml(CG.info);s.replaceWith(t.firstElementChild);}}catch(e){}},5000);},
  leave(){clearInterval(this.iv);}};
/* ================= V0.6.52 25 語音轉字幕（共用的 sxMount） ================= */
PAGES[25]={render(pg){pg.innerHTML=`<div class="pg"><div class="row"><h1 class="title">語音轉字幕</h1><span class="grow"></span><span class="sub">本機 whisper.cpp · 免費 · 設定 → 語音轉字幕 可換模型／執行緒</span></div><div id="sxP" style="margin-top:8px"></div></div>`;
    const el=$("#sxP");sxMount(el,()=>S.page===25&&$("#sxP")===el);},
  leave(){clearInterval(SX.iv);SX.iv=null;}};
/* ================= V0.6.60 26 影片快速瀏覽（共用的 vbMount） ================= */
PAGES[27]={render(pg){pg.innerHTML=`<div class="pg fill"><div class="row"><h1 class="title">批量剪輯</h1><span class="grow"></span><span class="sub">選主播和禮物，一次剪出很多段；每支都能單獨下載</span></div><div id="spRoot" style="flex:1;display:flex;flex-direction:column;min-height:0;margin-top:8px;overflow:auto"></div></div>`;spMount($("#spRoot"));},
  leave(){clearTimeout(SP.iv);}};
PAGES[28]={render(pg){pg.innerHTML="";setTimeout(()=>go(29,"ed"),0);}};   /* V0.6.94 刪除已剪輯 → 合到「整理 MP4」 */
PAGES[35]={render(pg){pg.innerHTML=`<div class="pg"><div id="pf2Root"></div></div>`;pf2Mount(pg.querySelector("#pf2Root"));}};   /* V0.7.42.008 主播特性 */
/* TK_V1.0.30 自動處理紀錄、小檔備份（跟手機同一套） */
async function actMount(root){const A={cat:"",q:"",days:3};
  const L=async()=>{const j=await api(`/api/pc/actlog?cat=${A.cat}&days=${A.days}&q=${encodeURIComponent(A.q)}`);if(!j)return;const ic=Object.fromEntries((j.cats||[]).map(c=>[c.k,c.ic]));
    root.querySelector("#actC").innerHTML=`<button class="${A.cat?"":"on"}" data-ac="">全部</button>`+(j.cats||[]).map(c=>`<button class="${A.cat===c.k?"on":""}" data-ac="${c.k}">${c.ic} ${esc(c.nm)} <small>${c.n}</small></button>`).join("");
    root.querySelector("#actL").innerHTML=(j.rows||[]).map(r=>`<div class="actR"><small>${esc(r.t.slice(5,16))}</small><span>${r.m.startsWith(ic[r.k]||"\u0000")?"":(ic[r.k]||"")+" "}${esc(r.m)}</span></div>`).join("")||`<div class="sbkE">這幾天沒有這類紀錄</div>`;
    root.querySelector("#actN").textContent=`最近 ${j.days} 天 · ${j.n} 筆${j.n>400?"（只列最新 400 筆）":""}`;};
  root.innerHTML=`<div class="actT"><input id="actQ" placeholder="🔍 找字（例如 #04315、小宅宅）"><select id="actD"><option value="1">1 天</option><option value="3" selected>3 天</option><option value="7">7 天</option><option value="14">14 天</option></select></div><div class="actC" id="actC"></div><div class="actN" id="actN"></div><div class="actL" id="actL">讀取中…</div>`;
  root.querySelector("#actC").onclick=e=>{const b=e.target.closest("[data-ac]");if(!b)return;A.cat=b.dataset.ac;L();};
  root.querySelector("#actD").onchange=e=>{A.days=+e.target.value;L();};let tq=0;root.querySelector("#actQ").oninput=e=>{clearTimeout(tq);tq=setTimeout(()=>{A.q=e.target.value.trim();L();},400);};L();}
async function hevcMount(root){const GB=b=>(b/1e9).toFixed(b>=1e11?0:1)+" GB",MB=b=>(b/1e6).toFixed(1)+" MB";
  const L=async()=>{const j=await api("/api/pc/hevc");if(!j)return;const st=j.st||{},R=j.res;
    root.innerHTML=`<div class="sbkN">用顯示卡把一分鐘影片壓成 <b>HEVC（H.265）</b>，看同樣畫質能小多少。<b>只是試算，不會動到任何原本的影片</b>；背景最低優先權，電腦忙會先等。</div>
    <button class="pill sbkGo" id="hvGo"${st.running?" disabled":""}>${st.running?"試算中…":"🧪 拿最大的那支試一分鐘"}</button><div class="hvSt">${esc(st.msg||"")}</div>
    ${R?`<div class="hvR"><div><b>${MB(R.orig)}</b><small>原本 60 秒</small></div><div><b>${MB(R.hevc)}</b><small>HEVC 60 秒</small></div><div><b>${Math.round(R.ratio*100)}%</b><small>大小剩下</small></div><div><b>${R.x}×</b><small>壓縮速度</small></div></div>
    <div class="hvE">影片庫現在約 <b>${GB(R.lib)}</b>，照這個比例全部轉 HEVC 大約能空出 <b>${GB(R.save)}</b>（實際會依每支畫面不同）。試的是 ${esc(R.file)}，從第 ${Math.round(R.ss/60)} 分鐘開始。</div>
    <div class="hvI"><figure><img src="${B}/api/pc/hevc/img?f=orig&t=${R.t}"><figcaption>原本</figcaption></figure><figure><img src="${B}/api/pc/hevc/img?f=hevc&t=${R.t}"><figcaption>HEVC</figcaption></figure></div>`:""}`;
    const g=root.querySelector("#hvGo");if(g)g.onclick=async()=>{g.disabled=true;const r=await kPost("/api/pc/hevc",{});toast((r&&r.ok?"":"✖ ")+((r&&r.message)||""));setTimeout(L,1500);};
    clearTimeout(window._hvT);if(st.running)window._hvT=setTimeout(()=>{if(root.isConnected)L();},3000);};L();}
function csvMount(root){const A={days:30,u:window.CSV_U||""};   /* TK_V1.0.51 匯出場次表 */
  const P=()=>{root.innerHTML=`<div class="sbkN">把場次表匯出成 <b>CSV</b>（Excel、Google 試算表直接開）：場次、主播、開播時間、長度、錄到幾成、保存等級、鑽石、留言、最高觀眾、MP4 大小、手機錄屏段數、有沒有字幕。</div>
    <div class="actT"><select id="cvD">${[[7,"最近 7 天"],[30,"最近 30 天"],[90,"最近 90 天"],[365,"最近一年"]].map(([d,t])=>`<option value="${d}"${d===A.days?" selected":""}>${t}</option>`).join("")}</select><input id="cvU" placeholder="只匯出這位（帳號，空白＝全部）" value="${esc(A.u)}"></div>
    <a class="pill sbkGo" id="cvGo" href="#">⬇ 下載 CSV</a><div class="sbkE">檔案會在電腦的 _DB_SSD\\export 留最新 10 份。</div>`;
    root.querySelector("#cvD").onchange=e=>{A.days=+e.target.value;};root.querySelector("#cvU").oninput=e=>{A.u=e.target.value.trim().replace(/^@/,"");};
    root.querySelector("#cvGo").onclick=e=>{e.preventDefault();const a=document.createElement("a");a.href=`${B}/api/pc/export/sessions?days=${A.days}&u=${encodeURIComponent(A.u)}`;a.download="";document.body.appendChild(a);a.click();a.remove();toast("⬇ 匯出中，好了瀏覽器會自己下載");};};P();}
async function cuMount(root){   /* V1.1.13 ☁ 雲端更新（GitHub）：檢查／更新／略過這版；要換 EXE 會先列出正在錄的直播間 */
  if(!root)return;const esc=s=>String(s==null?"":s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const G=b=>!b?"":b>=1e6?(b/1048576).toFixed(1)+" MB":Math.round(b/1024)+" KB";
  const get=async()=>{try{return await (typeof api==="function"?api:J)("/api/pc/cloud");}catch(e){return null;}};
  const post=async(o)=>{const f=(typeof kPost==="function"?kPost:rvPost);const r=await f("/api/pc/cloud/set",o);return r||{};};
  const ask=async(t,m)=>typeof confirmDlg==="function"?await confirmDlg(t,m,"堅持現在更新","stop"):window.confirm(t+"\n\n"+m);
  const say=r=>{if(typeof toast==="function"&&r&&r.message)toast((r.ok!==false?"☁ ":"✖ ")+r.message,4500);};
  const draw=I=>{if(!root.isConnected)return false;if(!I){root.innerHTML='<div class="cuBox">☁ 雲端更新：讀不到狀態</div>';return true;}
    const c=I.chk||{},dl=I.dl;let h=`<div class="cuBox"><b>☁ 雲端更新（GitHub）</b> <span class="cuS">現在 V${esc(I.cur)} · EXE 第 ${I.launcher} 版${I.on?"":" · 自動檢查已關（設定裡可以開）"}</span><div class="cuT">`;
    if(I.busy||dl){const p=dl&&dl.size?Math.round(dl.got/dl.size*100):0;h+=`⏳ ${esc(I.msg||"下載中")}${dl?`<div class="cuBar"><i style="width:${p}%"></i></div>${esc(dl.label||"")} ${p}%（${G(dl.got)} / ${G(dl.size)}，${(dl.spd/1048576).toFixed(1)} MB/s）`:""}`;}
    else if(!I.chk)h+="還沒檢查（開程式 1 分鐘後會自動檢查，之後每 6 小時）";
    else if(!c.ok)h+=`✖ ${esc(c.message||"連不到 GitHub")}`;
    else if(c.newer){h+=`🆕 <b>有新版 V${esc(I.ver)}</b>${I.date?`（${esc(I.date)}）`:""}　${c.need_shell?'<b class="cuW">⚠ 這次要換 EXE：程式會關掉再自動打開（約 1 分鐘），開起來自動恢復監控</b>':'熱更新，監控錄影不中斷'}${c.skipped?" · 已略過這版":""}`;
      if(I.notes&&I.notes.length)h+=`<div class="cuN">${I.notes.slice(0,10).map(n=>"• "+esc(n)).join("<br>")}</div>`;
      if(c.need_shell&&I.rec&&I.rec.length)h+=`<div class="cuW">現在有 ${I.rec.length} 間正在錄影：${I.rec.map(x=>esc(x.name)).join("、")}（建議等錄完再更新）</div>`;}
    else h+=`✔ 已經是最新（雲端 V${esc(I.ver||I.cur)}，${c.t?new Date(c.t*1000).toLocaleString("zh-TW",{hour12:false}):""} 檢查）`;
    if(I.msg&&!I.busy)h+=`<div class="cuS">${esc(I.msg)}</div>`;
    h+=`</div><div class="cuR"><button class="btn pill" data-cu="check">☁ 檢查更新</button>${c.newer&&!I.busy?`${c.need_shell?"":`<button class="btn pill" data-cu="skip">${c.skipped?"已略過":"略過這版"}</button>`}<button class="btn pill start cuGo" data-cu="update">更新到 V${esc(I.ver)}</button>`:""}${I.busy&&dl?`<button class="btn pill" data-cu="cancel">取消下載</button>`:""}</div></div>`;
    root.innerHTML=h;
    root.querySelectorAll("[data-cu]").forEach(b=>b.onclick=async()=>{const op=b.dataset.cu;b.disabled=true;let r;
      if(op==="update"){r=await post({op:"update"});
        if(r.need_confirm){if(await ask("要換 EXE（會重開程式）",r.message))r=await post({op:"update",force:1});else{b.disabled=false;return;}}}
      else r=await post({op});
      say(r);setTimeout(tick,op==="check"?4000:600);});
    return true;};
  let tm=null;const tick=async()=>{clearTimeout(tm);const I=await get();if(!draw(I))return;tm=setTimeout(tick,I&&(I.busy||I.dl)?1500:8000);};
  tick();}
function migFabInit(){   /* V1.1.20 搬硬碟切換／收尾中：右下角浮動進度 */
  const G=b=>!b?"0":b>=1e12?(b/1e12).toFixed(2)+" TB":b>=1e9?(b/1e9).toFixed(1)+" GB":(b/1e6).toFixed(0)+" MB";
  let tm=0;const chk=async()=>{clearTimeout(tm);let j=null;if(!document.hidden){try{j=await (typeof api==="function"?api:J)("/api/pc/mig");}catch(e){}}
    let b=document.getElementById("migFab");const T=(j&&j.tail)||{},ph=j&&j.phase;
    const show=j&&(ph==="final"||((ph==="switched"||ph==="verify")&&T.fast));
    if(!show){if(b)b.remove();tm=setTimeout(chk,j&&(ph==="switched"||ph==="verify")?8000:30000);return;}
    if(!b){b=document.createElement("div");b.id="migFab";document.body.appendChild(b);b.onclick=()=>{try{if(location.pathname.replace(/\/$/,"").endsWith("/pc")&&typeof go==="function")go(57);else location.hash="tool/mig";}catch(e){}};}
    const spd=j.spd||0,eta=spd>1e5&&T.left_b?T.left_b/spd:null,H=s=>s>=3600?Math.floor(s/3600)+" 小時 "+Math.round(s%3600/60)+" 分":Math.max(1,Math.round(s/60))+" 分";
    b.className=T.ready?"ok":"";
    b.innerHTML=ph==="final"?`💽 <b>切換到 ${j.dst} 中</b><small>${String(j.final||"補最後差異").slice(0,30)}…（錄影照常）</small>`
      :T.ready?`✅ <b>收尾完成，可以關機了</b><small>停止監控並退出 → 關機 → 換硬碟</small>`
      :`🏁 <b>收尾中 · 剩 ${(T.left_n||0).toLocaleString()} 個 · ${G(T.left_b)}</b><small>${T.stage||""} · ${spd>1e5?(spd/1048576).toFixed(0)+" MB/s":"—"}${eta?" · 約 "+H(eta):""}${j.curf&&j.curf.rel?" · "+String(j.curf.rel).split(/[\\/]/).pop().slice(0,28):""}</small>`;
    tm=setTimeout(chk,3000);};
  setTimeout(chk,3000);document.addEventListener("visibilitychange",()=>{if(!document.hidden)chk();});}
setTimeout(()=>{try{migFabInit();}catch(e){}},2500);
async function mrgMount(root){   /* V1.1.25 ⧉ 合併重複場次 */
  if(!root)return;const E=s=>String(s==null?"":s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const get=async u=>{try{return await (typeof api==="function"?api:J)(u);}catch(e){return null;}};
  const post=async(u,o)=>{const f=(typeof kPost==="function"?kPost:rvPost);return (await f(u,o))||{};};
  const T=s=>{if(!s)return"—";const d=new Date(String(s).replace(" ","T"));return isNaN(d)?String(s).slice(5,16):d.toLocaleString("zh-TW",{hour12:false,month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit"});};
  const off=new Set();let I=null,tm=0;
  const draw=()=>{if(!root.isConnected)return;const sc=I&&I.scan,R=I&&I.run;let h=`<div class="mrgHead"><b>⧉ 合併重複場次</b><div class="snote">同一位主播、TikTok 開播時間一樣（相差 1 分鐘內）的場次＝同一場直播，只是程式重開、斷電、斷線被切成好幾段。合併後留言、禮物、送禮者、觀看人數都歸到同一場；<b>影片不重新輸出</b>，回放照時間軸一段接一段播，中間沒錄到的會自動跳過。合併前自動備份資料庫。直播中的場次不會動（等它下播）。</div></div>`;
    if(R&&R.state==="running")h+=`<div class="mrgBox">⏳ 合併中… ${R.done}/${R.n}（先備份資料庫）</div>`;
    else if(R&&(R.state==="done"||R.state==="error"))h+=`<div class="mrgBox ${R.state==="done"?"ok":"bad"}">${R.state==="done"?`✔ 合併了 ${R.done} 組${R.fails.length?`，${R.fails.length} 組沒合併（${E(R.fails[0][1])}）`:""}${R.backup?`<br><small>合併前的資料庫備份：${E(R.backup)}</small>`:""}`:"✖ "+E(R.message||"失敗")}</div>`;
    if(!I||I.scanning&&!sc)h+=`<div class="mrgBox">🔎 找可以合併的場次…</div>`;
    else if(sc&&sc.error)h+=`<div class="mrgBox bad">✖ 找的時候出錯：${E(sc.error)}</div>`;
    else if(sc){const G=sc.groups||[];const on=G.filter(g=>!off.has(g.ids.join(",")));
      h+=`<div class="mrgBar"><span>找到 <b>${G.length}</b> 組可以合併${sc.skipped?`（另有 ${sc.skipped} 組還在直播，先不動）`:""}</span><button class="btn pill" data-m="rescan">🔎 重新找</button>${G.length?`<button class="btn pill" data-m="all">${on.length===G.length?"全部取消":"全部勾選"}</button><button class="btn pill start" data-m="run" ${on.length?"":"disabled"}>⧉ 合併勾選的 ${on.length} 組</button>`:""}</div>`;
      if(!G.length)h+=`<div class="mrgBox ok">✔ 沒有需要合併的場次</div>`;
      h+=G.map(g=>{const k=g.ids.join(","),ck=!off.has(k),S=g.sessions||[],nc=S.reduce((a,x)=>a+x.comments,0),nd=S.reduce((a,x)=>a+x.diamonds,0),nv=S.reduce((a,x)=>a+x.videos,0);
        return `<label class="mrgG ${ck?"on":""}"><input type="checkbox" data-k="${k}" ${ck?"checked":""}><div><div class="mrgT"><b>${E(g.name)}</b> <small>@${E(g.user)}</small> · ${T(S[0]&&S[0].start)} 開播 · <b>${S.length} 段</b> → 1 場</div>
        <div class="mrgS">${S.map((x,i)=>`<span>#${x.id} ${T(x.start)}～${T(x.end).slice(-5)} · 💬${x.comments} · 🎁${x.gifts}${x.diamonds?` (💎${x.diamonds})`:""} · 🎬${x.videos}</span>`).join("")}</div>
        <div class="mrgS"><small>合併後：💬 ${nc} 則 · 💎 ${nd} · 🎬 ${nv} 段影片照時間接著播 · 留下編號 #${Math.max(...g.ids)}</small></div></div></label>`;}).join("");
      if(sc.more)h+=`<div class="snote">還有 ${sc.more} 組，這批合併完再按「重新找」</div>`;}
    root.innerHTML=h;
    root.querySelectorAll("input[data-k]").forEach(c=>c.onchange=()=>{c.checked?off.delete(c.dataset.k):off.add(c.dataset.k);draw();});
    root.querySelectorAll("[data-m]").forEach(b=>b.onclick=async e=>{e.preventDefault();const m=b.dataset.m,G=(sc&&sc.groups)||[];
      if(m==="all"){const allOn=G.every(g=>!off.has(g.ids.join(",")));G.forEach(g=>allOn?off.add(g.ids.join(",")):off.delete(g.ids.join(",")));draw();return;}
      if(m==="rescan"){await get("/api/pc/merge/scan?force=1");tick();return;}
      if(m==="run"){const on=G.filter(g=>!off.has(g.ids.join(",")));if(!confirm(`合併 ${on.length} 組場次？\n\n留言、禮物、影片都會歸到同一場（影片不重新輸出）。\n合併前會自動備份資料庫。`))return;
        b.disabled=true;const r=await post("/api/pc/merge/run",{groups:on.map(g=>g.ids)});if(typeof toast==="function")toast((r.ok?"⧉ ":"✖ ")+(r.message||""),3500);tick();}});};
  const tick=async()=>{clearTimeout(tm);if(!root.isConnected)return;I=await get("/api/pc/merge");if(I&&!I.scan&&!I.scanning&&!(I.run&&I.run.state==="running")){await get("/api/pc/merge/scan");I=await get("/api/pc/merge");}
    draw();tm=setTimeout(tick,I&&(I.scanning||(I.run&&I.run.state==="running"))?1500:15000);};
  tick();}
/* V1.1.32 📖 規則說明：程式實際怎麼做（照程式碼整理，改規則時這裡一起改） */
const RU_F=(a)=>'<div class="ruFlow">'+a.map((x,i)=>(i?'<i class="ruAr">→</i>':'')+'<span class="ruChip" style="'+(x[1]?'--c:'+x[1]:'')+'">'+x[0]+'</span>').join('')+'</div>';
const RU_G=(k,n,c)=>'<span class="ruG" style="--c:'+c+'">'+k+'</span><b>'+n+'</b>';
const RU_V=(k,u,d)=>'<span class="ruV" data-k="'+k+'" data-u="'+u+'"><b>'+d+'</b> '+u+'<i>✎</i></span>';   /* V1.1.35 規則裡的數字＝設定，可以直接改（要打勾確認） */
const RU_BAR=(segs)=>'<div class="ruBar">'+segs.map(s=>'<span style="flex:'+s[0]+';--c:'+s[2]+'">'+s[1]+'</span>').join('')+'</div>';
const RULES=[
 {k:"rec",i:"🎥",c:"#ff6b8a",t:"錄影與監控：怎麼錄、存在哪",s:[
  {t:"一場直播的檔案怎麼走",d:RU_F([["直播中","#ff4d6d"],["FLV 先寫 C 槽 SSD","#f0ad4e"],["下播：在 SSD 轉 MP4","#4dc9ff"],["搬進影片庫（R 槽）","#45d483"]])+
   "<ul><li>錄影時畫面直接複製串流、<b>不重新壓縮</b>，所以錄影本身幾乎不吃 CPU。</li><li>下播後在 SSD 上把 FLV 轉成 MP4：畫面大小沒變就直接複製（幾秒～幾分鐘）；直播中畫面大小變過（例如 PK）才重新壓縮成同一個大小，這時用<b>顯示卡</b>（主 FFmpeg 太新、1060 驅動不支援，用 ffmpeg_gpu 那份 FFmpeg 7.1.1）。</li><li><b>快的先轉</b>：排隊時先讀 FLV 標頭，看每部是「直接合併」還是「要重新壓縮」。直接合併的<b>兩條同時轉</b>（電腦忙時只用一條）；要重新壓縮的自己<b>一條、一次一部</b>（顯示卡壓縮、CPU 最多 2 核），不會擋住後面。轉到一半才發現要重新壓縮的，讓出來排到慢的那條<b>下一部</b>。設定 → 錄影「🚀 快的先轉」可以關。</li><li>轉好才一次搬到影片庫硬碟（HDD 只寫一次完整的 MP4，不會邊錄邊轉卡住）。轉成功就刪 FLV；<b>轉失敗一定保留 FLV</b>（放「FLV轉檔失敗」，之後可以重轉）。</li><li>聲音另外錄一份 M4A（48 kbps 單聲道，一小時約 22 MB），也是先放 SSD、轉好再搬。<b>就算 MP4 刪了，M4A、留言、禮物都還在</b>。</li></ul>"},
  {t:"空間不夠時",d:"<ul><li>SSD 剩不到 <b>"+RU_V('rec.ssd_min_free','GB',60)+"</b>：新的錄影改成直接錄在影片庫硬碟。</li><li>影片硬碟剩不到 <b>"+RU_V('rec.video_min_free','GB',30)+"</b>：不開始新的錄影（<b>聲音照錄</b>）。</li><li>🛡 C 槽守門員每分鐘看 C 剩多少、減少多快：第 1 級先停不急的背景工作；第 2 級全速把東西搬走；第 3 級（剩不到 15 GB 或 20 分鐘內會滿）才會一位一位停掉正在錄到 C 的影片（F → E → 未分級先停）。</li></ul>"},
  {t:"同一場直播的判定（斷線、重開）",d:"<ul><li>主播斷線後 <b>"+RU_V('conn.grace_minutes','分鐘',10)+"內</b>連回同一個直播間＝<b>續寫同一場</b>（錄影會分成第 2 段、第 3 段…）。</li><li>直播中卻 <b>"+RU_V('monitor.silent_min','分鐘',30)+"</b>沒有任何留言、禮物、進場、人數也沒變（而且沒在錄影）→ 重新連一次確認：還在播就續寫，結束了就把結束時間改回最後有資料的時間。</li><li>程式重開、斷電、超過 10 分鐘才連回來 → 會變成<b>另一場</b>。這種被切開的，用「⧉ 合併重複場次」合回一場（見「場次合併」）。</li></ul>"},
  {t:"開程式、熱更新時的監控",d:"<ul><li>開程式 3 秒後自動開始監控（設定可以關）。正在錄的場次在熱更新、重開時會<b>接著錄同一場</b>。</li><li>搬硬碟切換後，如果找不到影片硬碟（例如 R 槽代號跑掉），程式<b>先不開始監控</b>，不會錄到別的地方，會提示你去磁碟管理改代號。</li></ul>"},
  {t:"📲 手機錄特效",d:"<ul><li>一支安卓手機（紅米 10）用 USB 接電腦，裝好 scrcpy（工具頁可自動從官方 GitHub 下載）。</li><li>主播開播 → 手機自己亮起來、打開那個直播間 → 錄下手機畫面＋聲音（有禮物特效）。一支手機一次錄一場。</li><li>錄誰：<b>S 級</b>的主播，照「工具 → 📲 手機錄特效」裡拖好的順序；按「▶ 開始」後，排最前面、正在直播的那位先錄，他下播換下一位還在播的。要加人＝在審核改成 S。</li><li>改順序要按右下角「✔ 套用」才生效；套用後（或排更前面的開播了）正在錄的不是第一順位 → 倒數 10 秒停掉、換錄新的那位。</li><li>主播斷線／下播超過 90 秒才停；TikTok 被關掉或跳走會自己重新打開直播間；拔線再插回、scrcpy 中斷 → 接著錄下一段（_p2、_p3…）。</li><li>手機超過 46°C 先停錄，降到 41°C 再繼續。</li><li>先錄在 SSD（MKV，斷電也播得了），結束後不重新壓縮換成 MP4（idle），搬到影片資料夾 <b>TikLive_手機特效\\帳號\\</b>；不到 15 秒的段丟掉。</li><li>回放：同一場可以切換「原本／手機」版本（用聲音對齊；對不上用錄影時間，可能差幾秒）。剪輯器那場的來源最後多一個手機特效檔。</li><li>S 級：手機特效版也排進 YouTube（標題加「手機特效版」，跟原本的是不同一部）。容量預測也算進去。</li><li>🎁 禮物剪輯：「錄好的」那場按「禮物剪輯」→ 選一位大哥（不算 10 鑽以下），或不分是誰、單次 ≥ 2000 鑽的全部 → 每個禮物一格（一次顯示 10 格，往右滑再載入）；點一格只載那一小段，用 ±1／±5 調送禮前、送禮後幾秒，按 OK 換下一格；沒調的用預設 → 全部接成一支 MP4（連在一起的併成一段，用顯示卡壓縮）。</li><li>學習時間差：每次按 OK 都記下來（禮物、你調的秒數、當時幾個人在播…）。同一種禮物有 2 筆以上就用它們當預設：取中位數、差太多的先不算、其他平均；之後資料夠了可以分析延遲原因。</li><li>回放切到「手機」版本時，程式自己畫的送禮動畫不顯示（手機畫面本來就有真的特效）。</li><li>🧩 手機版合併：同一場有手機特效（自動錄）和上傳的手機／平板錄屏（用「手機錄屏」上傳，聲音自動對上這場）→ 回放的「📱 手機」預設用上傳的把重疊時間蓋掉；「錄好的」按「🧩 合併」可以改成只蓋幾分到幾分，也可以照結果輸出：每段各一支（各自原本的解析度，不混在一起、不補黑邊；被上傳的蓋掉的手機特效不輸出；整支用到直接複製，只用到一部分照原解析度剪），放在「暱稱_開播_#場次_手機合併」資料夾。</li><li>🎯 手動對齊：上傳的位置不對（聲音對不上、被放錯時間）→ 合併畫面每支上傳的按「🎯 手動對齊位置」：上面播上傳的、下面播這場（原本錄的或手機特效，可以點禮物清單跳過去），兩邊停在同一瞬間按「🎯 這兩個是同一刻」→ 程式再用聲音在前後 2 秒內找最準的一點（找不到就照你對的）；之後可以 ±0.1／±0.5 秒微調、「▶ 兩個一起播」檢查；存過的「蓋幾分到幾分」會跟著一起挪。</li><li>🎛 禮物陣列影片（工具／網頁版第 61 頁，或「錄好的」那場按「🎛 禮物陣列」，跟批量剪輯、GIF 陣列分開）：選一場 → 用「送禮的人／禮物／單次 ≥ 幾鑽」篩，每個禮物 5 張預覽圖（從開始秒數起每格長度內平均 5 張）看表情挑 → 排成陣列（畫面照「🧩 手機版合併」的結果：上傳的平板／手機錄屏蓋掉的時間用上傳的，被取代的手機特效不會出現），全部格子一起從頭循環播（每格是送禮前 10 秒～後 20 秒的小預覽影片，顯示卡壓縮、存 SSD）→ 點一格用 −0.1／+0.1（按住一直調）、−1／+1 調它從哪裡開始，其他格照播；「☑ 多選」「同一種禮物」可以一起調；◀ ▶ 換位置、✕ 拿掉 → 選每格秒數、排法（幾欄×幾列）、長邊、要不要聲音 → 輸出一支 MP4（存在 TikLive_手機特效\_禮物陣列\，背景一次一件、電腦忙先等）。「⏱ 前後」開始／結束各有 −1／−0.1／+0.1／+1（按住一直調），一起改全部格子，每格一樣長，時間條看黃線＝送禮、藍框＝要的那段；「🧩 疊法」跟截圖全覽一樣：間距（負＝疊在一起）、左右疊、上下疊、臉位置 ▲▼，另外可以勾「疊的地方柔化過渡」（輸出也一樣）；每格的小預覽影片前面多留 15 秒、後面多留 20 秒，調前後大多不用重做，超出才只重做那一格；做好的存在電腦 SSD（最多 2 萬支），換排版、換秒數、下次打開都直接用，離開頁面電腦也會在背景繼續做；上面有進度條和大概還要多久，輸出也有；某格讀不到 → 點那格看原因、按「🔄 重新讀取」。每次調整都記下來（_DB_SSD\pfx_gav_log.jsonl：哪種禮物、誰送、調前調後、當時幾個人在播），同一種禮物 2 格以上就自動當下次的預設開始秒數；工作區自動存，下次打開同一場接著做。</li><li>✂ 剪輯：那場有手機特效版會先問要剪「原本錄的」還是「手機特效版」；沒有就直接開。</li><li>看畫面：錄影中每 30 秒截一張手機畫面（頁面看得到），也讀畫面上的字、看現在是不是直播間。黑畫面（螢幕關了、直播間沒畫面）、TikTok 顯示「發生錯誤／請稍後再試」、跑到首頁不在直播間、一模一樣 2 分鐘（卡住）、錄影檔沒在長 → 看到就馬上動手，30 秒後還不對換下一招：①完全關掉 TikTok 重開直播間（每次開直播間都先這樣，避免叫回上一場已結束的）②先進另一位正在播的直播間 6 秒再回來 ③再關掉 TikTok 重開 ④檢查手機網路，不通就關掉 Wi-Fi 再打開 ⑤重開錄影 ⑥重開手機（6 小時最多一次）。小米「充電速度慢」這類跳出來的視窗按返回關掉。只是畫面沒動（主播可能停在同一畫面）救 3 招後改 3 分鐘再看。螢幕設成永遠不自己關。</li><li>自己處理：通知欄被拉下來、USB 用途選單、系統對話框 → 20 秒內自己收掉；離開 TikTok 會重新打開直播間；連不上 3 分鐘重新啟動 adb；處理不了的（找不到手機、電量低沒充電、在播卻沒在錄）會出現在狀態卡和這頁最上面。</li><li>聲音：開直播間前先把手機媒體音量調到 0（錄影還沒開始那幾秒不出聲），錄影接手聲音後（手機本來就不出聲）調回原本的音量，確保錄得到聲音。</li><li>螢幕：下播停錄 → 回桌面、把 TikTok 完全關掉（主帳號＋小米分身，不在背景一直播、耗電、出聲）；沒在錄、1 分鐘沒人操作 → 回桌面、亮度最低、關螢幕待機；開播時亮起來（亮度照設定，預設 50%）→ 回桌面 → 進直播間，開錄前先看一眼畫面，黑的就回桌面再開一次。頁面有手動按鈕：亮屏、熄屏、回桌面、開 TikTok、截一張、亮度拉桿（任何裝置都能按）。</li><li>SIM 卡：錄影手機不要插中國的 SIM 卡（TikTok 會把手機當成在中國，整頁「發生錯誤」、不能登入）；偵測到會在頁面最上面提醒。只用 Wi-Fi 就好。</li><li>帳號：有小米分身（雙開，系統使用者 999）登入另一個 TikTok 帳號時，每一場輪流用；一個帳號一直「發生錯誤」（可能被 TikTok 擋）就換另一個，被擋的休息 30 分鐘。兩個都不行就不再一直重開，改成等 5、10、20 分鐘再試，並提醒你（重開手機對這種沒用，只用在黑畫面）。</li><li>手機畫面每 30 秒截一張顯示在頁面（螢幕關著不截）；錄影中的截圖另外存成那支影片的「預覽」（檔名＝影片第幾秒），在「錄好的」按 🖼 預覽看，點一張從那裡播。要先開小米「USB 偵錯（安全設定）」程式才能按電源鍵。</li><li>每週二、週五凌晨 3～7 點（沒在錄、S 級都沒在播時）自動重開手機一次；</li><li>全部在背景執行緒：手機只把壓好的畫面傳過來，電腦不解碼、不開視窗。</li></ul>"},
  {t:"⏸ 暫停監控並封存",d:"<ul><li>主播分類（或審核、檔案總管）<b>長按主播</b> → 主播選單 →「⏸ 暫停監控並封存」。</li><li>從那一刻起<b>不再連線、不錄新的</b>（直播中的話那一場停在那裡、照常收尾）；主播清單、等級、分類、<b>以前的場次全部留著</b>，照常轉檔、整理、照等級排隊上傳 YouTube、照保留天數刪原檔。</li><li>在主播分類移到最下面「⏸ 暫停監控（封存）」那區；<b>審核頁</b>也收到最下面同一欄「⏸ 封存」（保留原本的等級、照等級排、灰階，點進去一樣看以前的紀錄）。同一個選單按「▶ 恢復監控」就接回來。</li><li>封存中的主播又被<b>新增</b>（貼 TikTok 連結、@帳號、匯入）：會先問「目前封存中，要解封嗎？」— 解封＝移回來繼續監控；取消＝取消新增、維持封存。</li><li>每一次封存／解封都會記下來（時間、從哪裡按的），長按主播的小視窗最上面「🗄 封存紀錄」看得到。</li><li>跟「🗑 刪除主播」不一樣：刪除＝整位全部刪掉（等於標 F 再處置）。</li></ul>"},
  {t:"只錄聲音的主播（照審核等級 G）",d:"<ul><li><b>在「主播審核」標 G＝只錄聲音</b>；改成別的等級就恢復錄影片。以前另外的「只錄聲音的主播」清單已經拿掉，程式每分鐘照等級對一次，以審核等級為準。</li><li>G 的主播直播中照樣錄畫面（FLV 先放 C 槽），下播後截 60 張圖＋字幕，自動傳 YouTube，傳好才移走原檔。</li><li>直播中每 <b>"+RU_V('rec.snap_min','分鐘',2)+"</b>另外拍一張快照，回放時在影片的位置左右翻看。</li></ul>"}]},
 {k:"play",i:"📺",c:"#4dc9ff",t:"回放與直播中觀看：延遲、預載入",s:[
  {t:"為什麼要「+3 秒」",d:RU_BAR([[3,"留言／禮物（資料）","#4dc9ff"],[1,"約 3 秒","#f0ad4e"],[3,"畫面上才看到","#45d483"]])+"<ul><li>TikTok 的畫面比留言、禮物的資料<b>晚大約 3 秒</b>。所以在回放點一則留言或禮物，會跳到「那個時間 <b>+3 秒</b>」，畫面才對得上（秒數在回放設定可以改）。</li><li>送禮動畫也跟著這個延遲一起延後，畫面上出現禮物那一刻才跳動畫。</li><li>點<b>禮物</b>時會再<b>早 0.5 秒</b>落地，播放 0.5 秒後動畫完整出現。</li></ul>"},
  {t:"看還在直播的場次（LIVE 時移）",d:RU_F([["錄影中的 FLV","#ff4d6d"],["切成 2 秒一片","#f0ad4e"],["手機／平板播放","#4dc9ff"]])+"<ul><li>還在直播、而且正在錄影的場次，回放會用「直播畫面（可回看）」：把錄影中的 FLV 切成 2 秒一片給手機播。</li><li>一打開先從<b>大約 30 秒前</b>開始，跟著最新畫面走；最新那一兩片寫到一半不給，所以最新畫面再晚約 4 秒，加上 TikTok 本身的延遲。</li><li>往回看：程式從尾巴往前<b>每次補 2 分鐘</b>（限速每秒約 3 MB，不搶錄影），補到哪裡才看得到哪裡，所以<b>剛打開時只能往回拉一點點</b>，等一下才能拉到開播。這就是「預載入速度會影響回放」。</li><li>同時最多 <b>3 位</b>主播用這種方式看；沒人看 <b>90 秒</b>就自動停掉、清掉暫存。</li></ul>"},
  {t:"已經下播的回放",d:"<ul><li>播的是影片庫裡的 MP4，可以直接跳到任何位置（程式一次只送一小段，不會整支讀完）。</li><li>一場有好幾段影片時，照時間軸<b>一段接一段</b>播；中間沒錄到的地方自動跳過。</li><li>影片在傳統硬碟上，硬碟很忙（轉檔、搬檔、搬硬碟）時，開始播放和跳轉會慢一點。設定「手機回放加速」打開後，有人在手機看回放時背景工作全部讓路。</li><li>MP4 已經刪掉的場次：用刪之前截的 60 張圖（或 20 張）在影片的位置左右翻看，留言、禮物、M4A 照舊。</li><li>剪輯成品手機放不出畫面時（HEVC、10-bit…），背景自動用顯示卡轉一份相容的，原檔留著。</li></ul>"},
  {t:"🚀 載入速度：快速通道與預載",d:"<ul><li>網頁的埠 <b>+1</b>（例如 8766）是<b>快速通道</b>：截圖、預覽大圖、縮圖、頭像、回放資料、影片都從這條拿，多執行緒、不排主程式畫面的隊。在外面（https）或連不到（Windows 防火牆）會<b>自動走原本的</b>；每天第一次會提示「🚀 已開」或「⚠ 連不到」。設定 →「🚀 圖片快速通道」可關。</li><li>回放：打開一場後，前後 6 場先在背景載好（資料＋第一頁截圖）；電腦端也先算好同一位主播前後各 2 場。歷史紀錄清單停在畫面上的場次、手指碰到的場次都先載。‹ › 中間的綠色小字＝這次換場花幾秒（⚡＝預載過）。</li><li>回放總覽用縮小版截圖（最近 14 天背景先做好），放大看、下載才用原圖。</li><li>檔案總管：往後 30 場、往回 2 場先載，最近 8 場整段大圖先載；電腦同時拼 4 張大圖（電腦忙時 1 張）。</li></ul>"},
  {t:"平板版回放（4 格）",d:'<div class="ruQuad"><span>左上<br>💬 留言</span><span>右上<br>🎁 禮物</span><span>左下<br>🎵 點歌</span><span>右下<br>👋 進入</span></div>'+"<ul><li>右上角「📱 手機／▭ 平板」切換（預設看螢幕大小）。平板<b>橫著</b>看回放時，右邊分成 4 格，每格選要看什麼。</li><li>中間一條直線貫穿上下，左右兩欄的橫線<b>各自</b>拖，可以上下不對稱；點兩下恢復。大小和選擇會記住。</li><li>App 以後的修正手機、平板一起改，除非你說「平板更正」。</li></ul>"}]},
 {k:"grade",i:"🏷",c:"#ffc94d",t:"主播等級（🗂 主播審核）",s:[
  {t:"每個等級的意思與自動規則",d:'<table class="ruT"><tr><th>等級</th><th>自動傳 YouTube</th><th>原檔（MP4）留多久</th><th>特別規則</th></tr>'+
   '<tr><td>'+RU_G("S","無條件保存","#ffc94d")+'</td><td>✔ 最優先</td><td>傳好後再留 '+RU_V('ret.yt_keep_days','天',7)+'</td><td>還沒傳好前不受時間限制</td></tr>'+
   '<tr><td>'+RU_G("A","保存","#45d483")+'</td><td>✔</td><td>傳好就刪</td><td></td></tr>'+
   '<tr><td>'+RU_G("AD","A-Dance","#56e39f")+'</td><td>✔</td><td>傳好後再留 '+RU_V('ret.yt_keep_days','天',7)+'</td><td></td></tr>'+
   '<tr><td>'+RU_G("AS","A-Sing","#f78fb3")+'</td><td>✔</td><td>傳好就刪</td><td></td></tr>'+
   '<tr><td>'+RU_G("B","普通","#2ec4b6")+'</td><td>—</td><td>下播後 '+RU_V('ret.be_days','天',14)+'</td><td></td></tr>'+
   '<tr><td>'+RU_G("E","觀察","#4dc9ff")+'</td><td>—</td><td>下播後 '+RU_V('ret.be_days','天',14)+'</td><td>C 槽快滿、要停錄影時：F 先停、再來 E、再來未分級</td></tr>'+
   '<tr><td>'+RU_G("G","只錄聲音","#b48cff")+'</td><td>✔</td><td>傳好就刪</td><td>截 60 張＋字幕做好後才傳</td></tr>'+
   '<tr><td>'+RU_G("F","刪除","#ff4d6d")+'</td><td>✖ 不傳</td><td>—</td><td>按「處置 F」會把這位整個刪掉</td></tr></table>'+
   "<ul><li><b>「傳好」＝每個 MP4 都在 YouTube 處理好；刪之前會再問 YouTube 一次確認還在</b>。還在 YouTube 排隊、上傳中、處理中的，<b>不受時間限制</b>（所以理論上原檔不會留超過 14 天，除非排隊一直排不上）。</li><li>上面是預設值。審核頁「🏷 等級設定」可以新增、改名、改色、排序，也可以改每一級要不要傳 YouTube、傳好原檔要不要留（S、F、G 的特別作用不能刪）。</li><li>「傳 YouTube」的等級：那一場的轉檔、截圖、字幕、預覽圖都做好之後才自動上傳。</li></ul>"},
  {t:"審核頁怎麼看",d:"<ul><li>每位主播所有場次、每 2 分鐘一張圖接成一長條（新的在上），用來決定等級。</li><li>圖只拿檔案總管已經做好的預覽圖，不另外跑 FFmpeg；還沒做好的先用 20 張截圖，都沒有就標「預覽圖排隊中」。</li></ul>"}]},
 {k:"lv",i:"🗂",c:"#45d483",t:"場次標記（−2／0／+1／+2）與刪除",s:[
  {t:"四種標記",d:'<div class="ruLv"><span style="--c:#ff4d6d">−2 可丟</span><span style="--c:#f0ad4e">0 未分類</span><span style="--c:#45d483">+1 待剪輯</span><span style="--c:#2ec4b6">+2 保存</span></div>'+"<ul><li>在檔案總管按等級＝存好、自動捲到下一場。</li><li><b>沒按就滑到下一場＝上一場自動標 −2</b>；有選片段的話，那些片段先合併輸出成 1 部剪輯成品。按「↩ 復原自動 −2」可以還原。</li></ul>"},
  {t:"−2 的場次要刪 MP4 時（重要）",d:'<div class="ruWarn">⚠ <b>只要這場有安排要傳 YouTube，就算你在檔案總管標了 −2、按了刪除，原檔也一定等 YouTube 傳完、處理好才會刪。</b></div>'+RU_F([["標 −2、按刪除","#ff4d6d"],["這場有安排傳 YouTube？","#f0ad4e"],["有 → 先不刪，等傳完","#4dc9ff"],["YouTube 處理好","#b48cff"],["隔離區 → 再確認 → 刪","#45d483"]])+
   "<ul><li><b>「有安排傳 YouTube」</b>包括：① 主播等級設定要傳（S、A、A-Dance、A-Sing、G…），還沒傳完；② 已經在 YouTube 排隊中；③ 正在上傳（傳到一半的也算）；④ 已經傳上去、YouTube 還在處理。四種都一樣：<b>先不刪</b>。</li><li>還沒排進 YouTube 的會自動排進去；傳完、YouTube 處理好之後，才移到「YouTube 已上傳-刪除隔離區」，再問 YouTube 一次確認影片還在，才刪原檔。</li><li>不管從哪裡刪都一樣：檔案總管 −2、整理 MP4、剪輯完刪、刪主播、回放頁、手機、網頁。</li><li>沒有安排傳 YouTube 的場次：直接照你按的刪。</li><li>查不到 YouTube 狀態時<b>寧可先不刪</b>。</li><li>還在直播／錄影中的場次<b>不能刪影片</b>；正在剪輯的那場剪完才刪。</li></ul>"},
  {t:"刪 MP4 之前一定先截圖",d:"<ul><li>不管從哪裡刪 MP4（歷史紀錄、檔案總管、整理 MP4、手機、網頁），刪之前先在影片 10%、20%…100% 各截圖，共 <b>60 張</b>（原檔不完整的 20 張），每張約 100 KB。</li><li>剪輯成品、留言、禮物、錄音全部留著；剪輯成品<b>永久保留</b>。</li><li>有 ⭐ 收藏片段的場次：刪 MP4／轉出時會跳過那些片段。</li></ul>"},
  {t:"🗓 原檔保留期限（自動）",d:RU_F([["B／E：下播 "+RU_V('ret.be_days','天',14)+"","#2ec4b6"],["刪 MP4（先截 60 張）","#ff4d6d"]])+RU_F([["S／AD：YouTube 傳好","#ffc94d"],["再留 "+RU_V('ret.yt_keep_days','天',7)+"","#f0ad4e"],["隔離區 → 確認 YouTube → 馬上刪","#ff4d6d"]])+RU_F([["A／AS／G：YouTube 傳好","#45d483"],["隔離區 → 確認 YouTube → 馬上刪","#ff4d6d"]])+"<ul><li>每 30 分鐘檢查一次（開程式 10 分鐘後開始）；B／E 一次最多刪 10 場，慢慢來。</li><li><b>不動</b>：還在 YouTube 排隊／上傳中／處理中的、直播／錄影中、有 ⭐ 收藏片段、標 <b>+1 待剪輯</b>或 <b>+2 保存</b>的場次。</li><li>刪的只有 MP4：截圖、預覽圖、字幕、留言、禮物、M4A 錄音、剪輯成品都留著。設定「🗓 原檔保留期限」可以整個關掉。</li><li><b>💾 容量預測</b>（設定 → 電腦效能 → 容量變化，<b>長按圖表</b>）：可以模擬每個等級留幾天、YouTube 每天上限，看幾天會滿、平衡在多少 TB；按左下角「套用變更」確認 3 次後，每個等級改成各自的天數（傳 YouTube 的＝傳好後幾天，0＝傳好就刪；不傳的＝下播後幾天或永久），上面的 B／E、留原檔天數就以那邊為準。</li></ul>"},
  {t:"程式自己會清的",d:"<ul><li><b>冗餘 14 天+</b>：放超過 14 天、沒有場次紀錄的 MP4（檔案總管「冗餘」那些）。</li><li><b>暫存</b>：只錄聲音的場次留著的 MP4，<b>5 天後</b>沒按「📌 留下」就自動刪。</li><li>每 30 秒一張的預覽圖：C 槽最多 "+RU_V('vg.cache_gb','GB',40)+"，超過從最久沒看的刪；要看時再做。精選用的每 2 秒圖保留 15 天、最多 "+RU_V('hl.keep2s_gb','GB',60)+"。</li></ul>"}]},
 {k:"yt",i:"▶",c:"#ff4d4d",t:"YouTube 上傳",s:[
  {t:"上傳規則",d:"<ul><li>照「主播等級」自動上傳（見主播等級），也可以在 YouTube 上傳頁手動加。隱私預設<b>不公開</b>（搜尋不到，只有拿到網址的人看得到；回放頁可以內嵌 YouTube 跟留言同步播）。</li><li>每 <b>24 小時最多 "+RU_V('yt.daily','個',100)+"</b>，照<b>上傳完成時間滾動</b>算；頁面會顯示第 101 個什麼時候可以開始。額度用完自動等 6 小時。</li><li>速度上限 "+RU_V('yt.mbps','Mbps',20)+"，不搶錄影的網路；可以設只在某個時段開始傳新的。<b>正在傳的那部一定照傳完</b>，不會中途斷。</li><li>「幾天後全部傳完」會<b>扣掉每天新增的</b>（最近 7 天平均）：每天真正消化＝每天上限 − 每天新增。新增的比上限多就會寫「追不上」，並告訴你上限至少要調到多少。</li></ul>"},
  {t:"先傳哪些",d:"<ul><li>現在是「<b>舊的場次先傳</b>」。S 級永遠最優先。</li><li><b>開播在最近 "+RU_V('yt.hold_new_days','天',3)+"內的場次先不傳</b>，留給合併同一場被切開的（YouTube 頁可以改天數，0＝不限）。已經開始傳的照傳完。</li></ul>"},
  {t:"傳好之後",d:"<ul><li>YouTube 處理好會把網址存進那一場。</li><li>「傳好原檔留著」沒勾的等級：原檔移到「YouTube 已上傳-刪除隔離區」，"+RU_V('yt.hold_auto_h','小時',24)+"後再跟 YouTube 確認一次就自動刪（設定可以關掉自動刪）。</li></ul>"}]},
 {k:"bg",i:"✨",c:"#b48cff",t:"背景工作：精選、字幕、預覽圖、轉檔順序",s:[
  {t:"誰先誰後",d:RU_F([["監控、錄影（永遠最先）","#ff4d6d"],["FLV → MP4 轉檔","#f0ad4e"],["語音轉字幕","#4dc9ff"],["預覽圖、截圖","#2ec4b6"],["✨ 精選（最後）","#b48cff"]])+"<ul><li>精選是非必要的工作，排最後：轉檔、字幕、搬檔、截圖在做，或 CPU 超過 "+RU_V('hl.max_cpu','%',55)+"、顯示卡超過 "+RU_V('hl.max_gpu','%',50)+"、硬碟忙超過 "+RU_V('hl.max_disk','%',50)+"時就先停（做到一半的之後重做那場）。</li><li>你正在檔案總管看的那場、排著要上傳 YouTube 的，精選和每 2 秒圖永遠先做。</li></ul>"},
  {t:"語音轉字幕",d:"<ul><li>下播、錄音整理好後（約 5 分鐘）自動排進來，只在顯示卡加速版可以用時自動轉（CPU 轉太吃效能）。</li><li>每場最慢 6 小時轉完，程式算出剛好轉完需要的最低用量，平常顯示卡幾乎閒著；排隊到 8 成以上會自動加快。</li></ul>"},
  {t:"以前留下的 FLV",d:"<ul><li>新的錄影一律自動轉。以前留在硬碟上的 FLV 預設不自動處理，到「FLV 待處理」勾選（V1.1.28 已經把積欠的一次全部排進去）。</li><li>一次轉一部；大部分只是換容器、直接複製畫面，速度看硬碟，顯示卡用不太到，這是正常的。</li></ul>"},
  {t:"每日精選影片",d:"<ul><li>每天早上把前一天的精彩片段（不含 PK）剪成一支，最長 "+RU_V('reel.max_min','分鐘',30)+"、只留 "+RU_V('reel.keep','天',7)+"；你自己剪的成品不受影響。</li></ul>"}]},
 {k:"th",i:"🌡",c:"#f0ad4e",t:"控溫、斷電、效能保護（不准讓主程式過載）",s:[
  {t:"CPU 預算",d:RU_BAR([[45,"整台 CPU 預算 45%（SortCut 有開）","#f0ad4e"],[55,"留給你和系統","#3a4250"]])+"<ul><li>背景的轉檔、合併、預覽、截圖、字幕全部算一組，用 Windows 內建的 CPU 硬上限壓住（只會變慢，不會停，最少留 "+RU_V('th.min','%',5)+"）。</li><li>上限＝整台預算 −（錄影和其他程式用的）。SortCut 有開時 "+RU_V('th.cpu','%',45)+"，沒開時 "+RU_V('th.cpu_solo','%',60)+"。<b>錄影、監控、畫面不受限制</b>。</li><li>顯示卡 <b>"+RU_V('th.gpu','°C',75)+"</b>以上，新的背景轉檔先等（跑到一半的照跑完，最多等 10 分鐘）。</li></ul>"},
  {t:"斷電偵測（通知 SortCut）",d:"<ul><li>程式沒按「停止監控並退出」就沒了、而且電腦重開過，再對照事件檢視器的 Kernel-Power 41 → 判定為<b>非人為斷電</b>。</li><li>重開後通知 SortCut："+RU_V('th.alert_h','小時',12)+"內降到最低（Lv 1、CPU 最低、同時 1 個）；24 小時內斷電 "+RU_V('th.alert_stop_n','次',2)+"以上 → 叫 SortCut 停止轉檔至少 24 小時。TikLive 自己的背景重活也少 15%。</li><li>顯示卡供需頁可以「解除警報」。</li></ul>"},
  {t:"💽 硬碟有壞掉的資料夾",d:"<ul><li>斷電可能讓硬碟的檔案系統壞掉一小塊，Windows 會跳「檔案或目錄已毀損…請執行 Chkdsk」。</li><li>程式不讓 Windows 跳這種視窗（以前按確定會一直重跳），改成記下那個路徑、之後跳過；快照要搬進去的資料夾壞了就改放 <b>_2</b>、_3 的新資料夾，回放照樣找得到。</li><li>狀態卡會出現「💽 硬碟檔案系統有錯」。處理：系統管理員命令提示字元 <b>chkdsk R: /scan</b>（只檢查，程式可以開著）→ 有錯再挑沒人在播的時候關掉 TikLive 跑 <b>chkdsk R: /spotfix</b>。</li></ul>"},
  {t:"效能自我保護",d:"<ul><li>CPU 95% 以上超過 2 分鐘、錄影用的硬碟忙超過 85% 超過 1 分鐘，或 70 位以上同時在播且 CPU 超過 85% → 精選、預告、預覽圖、搜尋、報告先暫停，閒下來自動繼續。</li><li>主程式畫面卡住超過 "+RU_V('ui.freeze_rest_s','秒',6)+" → 自動切到不用更新的「休息畫面」，監控、錄影照常。</li><li>資料庫寫不進去：3 分鐘先停背景資料庫工作，10 分鐘重開卡住的連線，"+RU_V('health.restart_min','分鐘',20)+"自動重開程式。</li></ul>"}]},
 {k:"conn",i:"🔌",c:"#2ec4b6",t:"連線與開播檢查（不被 TikTok 擋）",s:[
  {t:"多久查一次有沒有開播",d:'<table class="ruT"><tr><th>主播</th><th>檢查間隔</th></tr><tr><td>重點（紅色）</td><td>3 秒起，慢慢拉長到 '+RU_V('retry.priority','秒',10)+'</td></tr><tr><td>一般</td><td>'+RU_V('retry.normal','秒',60)+'（他平常開播的時段加快）</td></tr><tr><td>'+RU_V('conn.stale_days','天',7)+'以上沒開播</td><td>× '+RU_V('conn.stale_mult','倍',3)+'</td></tr><tr><td>帳號不存在（連續 3 次）</td><td>× 10</td></tr></table>'+"<ul><li>全部檢查排隊進行：續寫中的直播 → 重點 → 一般，<b>每分鐘最多 "+RU_V('conn.rate','次',80)+"</b>。TikTok 開始拒絕就自動放慢一級（45%）、最多兩級（22%），恢復正常 10 分鐘才加回來。</li><li>開播時間很固定的主播，快到平常時間前 3 分鐘就排到最前面。</li></ul>"},
  {t:"重開程式不是萬靈丹",d:"<ul><li>TikTok 正在拒絕、或簽章額度用完時，重開程式不會換網址，反而會斷掉直播中的場次（程式會先提醒你）。</li></ul>"}]},
 {k:"upd",i:"☁",c:"#3a7bd5",t:"更新、搬硬碟、場次合併",s:[
  {t:"雲端更新（GitHub）",d:RU_F([["開程式 1 分鐘後、每 6 小時檢查","#3a7bd5"],["有新版只提示","#f0ad4e"],["你按「更新」","#45d483"],["熱更新（不中斷錄影）","#2ec4b6"]])+"<ul><li><b>一定要你按才更新，不會自己重開</b>。下載限速、比對檔案完整才裝。</li><li>以後<b>只熱更新、絕對不換 EXE 外殼</b>（不會再要你關程式重裝）。</li><li>更新後有問題，可以在更新頁「退回前面的版本」（一樣不中斷錄影）。</li></ul>"},
  {t:"場次合併（⧉ 合併重複場次）",d:RU_F([["第 1 段","#4dc9ff"],["第 2 段","#4dc9ff"],["第 3 段","#4dc9ff"],["⧉ 合併 → 1 場","#45d483"]])+"<ul><li>同一位主播、<b>TikTok 開播時間一樣（相差 "+RU_V('history.merge_tol','秒',60)+"內）</b>＝同一場直播，只是程式重開、斷電、斷線被切開。</li><li>合併後留言、禮物、送禮者、觀看人數都歸到同一場；<b>影片不重新輸出</b>，回放照時間一段接一段播，中間沒錄到的自動跳過。留下編號最大的那一場。</li><li>合併前自動備份資料庫；直播中的場次不會動（等它下播）。</li></ul>"},
  {t:"搬硬碟（E → R，已完成）",d:"<ul><li>先複製、每個檔讀回來比對一樣才算數 → 第一輪搬完自動切換（錄影不停）→ 舊硬碟上的逐一確認後刪 → 「搬硬碟完成」。</li><li>舊硬碟上剩的十幾 GB 是 Windows 自己的（回收筒、系統還原、檔案系統本身），格式化就清掉。</li></ul>"}]},
 {k:"dev",i:"📱",c:"#9aa5b3",t:"手機、平板、網頁版",s:[
  {t:"差別",d:"<ul><li>手機版與平板版是同一個 App，右上角切換；除了回放（平板 4 格），其他畫面一樣。</li><li>網頁版（電腦瀏覽器）：右下角可以調滾輪倍數（×0.5～×8）、「滾輪 ∿」絲滑開關、介面大小。每個瀏覽器自己記。</li><li>會改東西的操作（更新、刪除、合併、設定）都要密碼；只看的不用。</li></ul>"}]}
];
async function rulesMount(root){if(!root)return;
  const st=(()=>{try{return JSON.parse(localStorage.getItem("tlm_rules_open")||"{}")||{};}catch(e){return {};}})();
  const draw=(q)=>{q=(q||"").trim().toLowerCase();let n=0;
    const h='<div class="ruHead"><b>📖 規則說明</b><div class="snote">程式實際怎麼做（照程式碼整理，V1.1.32）。看不懂、跟你遇到的不一樣，截圖跟我說，我改程式或改這裡。</div>'+
     '<input class="ruQ" placeholder="🔍 找規則（例如：−2、YouTube、延遲、斷電）" value="'+(q?q.replace(/"/g,"&quot;"):"")+'"><div class="ruToc">'+RULES.map(c=>'<button data-go="'+c.k+'" style="--c:'+c.c+'">'+c.i+' '+c.t.split("：")[0].split("（")[0]+'</button>').join("")+'</div></div>'+
     RULES.map(c=>{const S=c.s.filter(x=>!q||(c.t+x.t+x.d.replace(/<[^>]+>/g,"")).toLowerCase().includes(q));if(!S.length)return"";n+=S.length;const op=q||st[c.k]!==0;
      return '<section class="ruC'+(op?" on":"")+'" id="ru_'+c.k+'" style="--c:'+c.c+'"><h3 data-k="'+c.k+'"><span>'+c.i+'</span>'+c.t+'<em>'+S.length+' 項</em><i>'+(op?"▾":"▸")+'</i></h3><div class="ruB">'+S.map(x=>'<div class="ruI"><h4>'+x.t+'</h4>'+x.d+'</div>').join("")+'</div></section>';}).join("")+(q&&!n?'<div class="ruNone">找不到「'+q+'」</div>':"");
    root.innerHTML=h;rulesPaintVals(root);const qi=root.querySelector(".ruQ");qi.oninput=()=>{const v=qi.value,p=qi.selectionStart;draw(v);const q2=root.querySelector(".ruQ");q2.focus();try{q2.setSelectionRange(p,p);}catch(e){}};
    root.querySelectorAll("h3[data-k]").forEach(h3=>h3.onclick=()=>{const k=h3.dataset.k,sec=h3.parentElement,o=!sec.classList.contains("on");sec.classList.toggle("on",o);h3.querySelector("i").textContent=o?"▾":"▸";st[k]=o?1:0;try{localStorage.setItem("tlm_rules_open",JSON.stringify(st));}catch(e){}});
    root.querySelectorAll("[data-go]").forEach(b=>b.onclick=()=>{const s=root.querySelector("#ru_"+b.dataset.go);if(s){s.classList.add("on");s.scrollIntoView({behavior:"smooth",block:"start"});}});};
  draw("");rulesVals(root);}
/* V1.1.35 規則裡的數字：讀現在的設定值；點 ✎ → 改數字 → 旁邊打勾「確認修改」才存（雙重確認） */
async function rulesVals(root){const ks=[...new Set([...root.querySelectorAll(".ruV[data-k]")].map(x=>x.dataset.k))];if(!ks.length)return;
  let j=null;try{j=await (typeof api==="function"?api:J)("/api/pc/rules/vals?k="+ks.join(","));}catch(e){}if(!j||!j.vals)return;RU_VALS=j.vals;rulesPaintVals(root);}
let RU_VALS={};
function rulesPaintVals(root){root.querySelectorAll(".ruV[data-k]").forEach(sp=>{const k=sp.dataset.k,V=RU_VALS[k];if(!V||sp._ed)return;const u=sp.dataset.u;
  sp.innerHTML='<b>'+V.v+'</b> '+u+(V.v!==V.def?'<small title="預設 '+V.def+'">（預設 '+V.def+'）</small>':'')+'<i>✎</i>';sp.title=V.label+(V.help?'\n'+V.help:'')+'\n點一下可以改';
  sp.onclick=e=>{if(sp._ed)return;e.stopPropagation();rulesEdit(root,sp);};});}
function rulesEdit(root,sp){const k=sp.dataset.k,V=RU_VALS[k],u=sp.dataset.u;sp._ed=1;sp.classList.add("ed");
  sp.innerHTML='<input type="number" class="ruIn" value="'+V.v+'"'+(V.min!=null?' min="'+V.min+'"':'')+(V.max!=null?' max="'+V.max+'"':'')+(V.step!=null?' step="'+V.step+'"':'')+'> '+u+' <label class="ruCk"><input type="checkbox" disabled> 確認修改</label><button class="ruX" title="不改">✕</button>';
  const inp=sp.querySelector(".ruIn"),ck=sp.querySelector(".ruCk input"),lb=sp.querySelector(".ruCk");inp.focus();inp.select();
  const close=()=>{sp._ed=0;sp.classList.remove("ed");rulesPaintVals(root);};
  inp.oninput=()=>{const n=parseFloat(inp.value),bad=isNaN(n)||(V.min!=null&&n<V.min)||(V.max!=null&&n>V.max);ck.disabled=bad||n===V.v;lb.classList.toggle("go",!ck.disabled);lb.title=bad?("範圍 "+(V.min??"")+"～"+(V.max??"")):"";};
  inp.onkeydown=e=>{if(e.key==="Escape")close();};sp.querySelector(".ruX").onclick=e=>{e.stopPropagation();close();};
  sp.onclick=e=>e.stopPropagation();
  ck.onchange=async()=>{if(!ck.checked)return;const n=parseFloat(inp.value);ck.disabled=true;inp.disabled=true;
    const f=(typeof kPost==="function"?kPost:rvPost);let r=null;try{r=await f("/api/pc/rules/set",{k,v:n});}catch(e){}
    if(r&&r.ok){RU_VALS[k].v=r.value;if(typeof toast==="function")toast("✔ "+(r.message||"已改"),3000);close();root.querySelectorAll('.ruV[data-k="'+k+'"]').forEach(x=>{x.classList.add("done");setTimeout(()=>x.classList.remove("done"),2500);});}
    else{if(typeof toast==="function")toast("✖ "+((r&&r.message)||"沒有改成"),3500);ck.checked=false;ck.disabled=false;inp.disabled=false;}};}

async function migMount(root){   /* V1.1.07／1.1.08 💽 E → R 搬硬碟（照 SortCut「R 碟清空搬移」的樣子） */
  const esc=s=>String(s==null?"":s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const G=b=>b==null?"—":b>=1e12?(b/1e12).toFixed(2)+" TB":b>=1e9?(b/1e9).toFixed(1)+" GB":b>=1e6?(b/1e6).toFixed(1)+" MB":Math.round(b/1e3)+" KB";
  const MB=v=>v==null?"—":(v/1048576)>=10?(v/1048576).toFixed(1)+" MB/s":(v/1048576)>=0.1?(v/1048576).toFixed(2)+" MB/s":Math.round(v/1024)+" KB/s";
  const T=t=>t?new Date(t*1000).toLocaleTimeString("zh-TW",{hour12:false}):"—";
  const H=s=>{s=Math.max(0,s||0);const d=Math.floor(s/86400),h=Math.floor(s%86400/3600),m=Math.floor(s%3600/60);return d?`${d} 天 ${h} 小時`:h?`${h} 小時 ${m} 分`:`${m} 分`;};
  const post=async(o)=>{const f=(typeof kPost==="function"?kPost:rvPost);const r=await f("/api/pc/mig/set",o);if(typeof toast==="function"&&r&&r.message)toast((r.ok!==false?"✔ ":"✖ ")+r.message);return r;};
  const spark=(vals,max,col,dash,fill)=>{const n=vals.length;if(n<2)return"";const W=300,Hh=70,pts=vals.map((v,i)=>[(i/(n-1)*W).toFixed(1),(Hh-Math.min(1,(v||0)/(max||1))*(Hh-4)-2).toFixed(1)]);
    const p=pts.map(x=>x.join(",")).join(" ");return (fill?`<polygon points="0,${Hh} ${p} ${W},${Hh}" fill="${col}" opacity=".18"/>`:"")+`<polyline points="${p}" fill="none" stroke="${col}" stroke-width="1.6" ${dash?'stroke-dasharray="4 3"':""}/>`;};
  const grid=()=>{let g="";for(let i=1;i<10;i++)g+=`<line x1="${i*30}" y1="0" x2="${i*30}" y2="70" stroke="rgba(127,140,160,.18)"/>`;for(let i=1;i<4;i++)g+=`<line x1="0" y1="${i*17.5}" x2="300" y2="${i*17.5}" stroke="rgba(127,140,160,.18)"/>`;return g;};
  function dcard(lab,role,col,busyArr,rwArr,cur,curRw){const mx=Math.max(1048576,...rwArr.map(x=>Math.max(x?x[0]:0,x?x[1]:0)));
    return `<div class="mgD" style="--c:${col}"><div class="mgDh"><b>💽 ${esc(lab)}</b><span class="mgTag">${role}</span><em>${cur==null?"—":Math.round(cur)+"%"}</em></div>
      <div class="mgCl"><span>使用率</span><span>100%</span></div><svg viewBox="0 0 300 70" preserveAspectRatio="none" class="mgSv">${grid()}${spark(busyArr,100,col,false,true)}</svg>
      <div class="mgCl"><span>傳輸速率</span><span>${MB(mx)}</span></div><svg viewBox="0 0 300 70" preserveAspectRatio="none" class="mgSv sm">${grid()}${spark(rwArr.map(x=>x?x[0]:0),mx,col,true)}${spark(rwArr.map(x=>x?x[1]:0),mx,col,false)}</svg>
      <div class="mgCl b"><span>--- 讀 ${MB(curRw?curRw[0]:null)}</span><span>— 寫 ${MB(curRw?curRw[1]:null)}</span></div></div>`;}
  async function draw(){if(!root.isConnected)return;
    if(root.contains(document.activeElement)&&document.activeElement.tagName==="INPUT"){clearTimeout(root._t);root._t=setTimeout(draw,2500);return;}
    let j;try{j=await (typeof api==="function"?api:J)("/api/pc/mig");}catch(e){j=null;}
    if(!j||!j.ok){root.innerHTML='<div class="sbkE">讀不到</div>';clearTimeout(root._t);root._t=setTimeout(draw,5000);return;}
    const D=j.disk||{},s=D.src||{},d=D.dst||{},ph=j.phase,now=Date.now()/1000;
    const Hs=j.hist||[],last=Hs[Hs.length-1]||{},cp=j.pass||{};
    const mineArr=Hs.map(x=>x.mine||0),recent=mineArr.length?mineArr.reduce((a,b)=>a+b,0)/mineArr.length:0;
    const avg=j.avg||(j.tot_s>0?j.tot_b/j.tot_s:0),used=s.used||0,pct=used?Math.min(100,j.copied_b/used*100):0;
    const rate=(j.eta_rate>1e5?j.eta_rate:recent>1e5?recent:avg),left=Math.max(0,used-j.copied_b),eta=(ph==="copy"&&!j.paused&&rate>1e5)?left/rate:null;   /* V1.1.17 照最近 1 小時真的在搬的速度（斷電、關程式、暫停那段不算）；不到 10 分鐘先照最近 6 分鐘 */
    const rateTxt=j.eta_rate>1e5?`照最近 ${Math.round(Math.min(3600,j.eta_win||0)/60)} 分鐘 ${MB(rate)}`:recent>1e5?`照最近 6 分鐘 ${MB(rate)}，1 小時後改用 1 小時平均`:`照平均 ${MB(rate)}`;
    const leftN=Math.max(0,(j.src_files||0)-(j.copied_n||0));
    const pill={idle:["還沒開始","g"],copy:j.paused?["⏸ 暫停中","w"]:j.cur||j.curf?["▶ 搬移中","ok"]:j.why?["⏳ "+(j.why.length>14?"等待中":j.why),"w"]:["▶ 搬移中","ok"],final:["🔁 切換中","w"],handoff:["🔄 換新版接手中","w"],switched:["✔ 已切換","ok"],verify:["✔ 從 "+j.dst+" 執行中","ok"],cleaning:["🧹 清空中","w"],done:["✔ 搬完了","ok"]}[ph]||[ph,"g"];
    let h=`<div class="mgCard"><div class="mgRow1"><b>⚡ 傳輸速度</b><span class="mgBigV">${j.mbps} <small>MB/s</small></span><span class="mgChip">🧠 自動讓路</span></div>
      <input type="range" class="mgRange" min="5" max="300" step="5" value="${j.mbps}"><div class="mgTicks"><span>5</span><span>慢・省力</span><span>50</span><span>全速</span><span>300 MB/s</span></div>
      <div class="mgSmall">現在 ${MB(last.mine)} · ✋ 上限 ${j.mbps} MB/s · 💽 ${j.src} ${last.sb==null?"—":Math.round(last.sb)+"%"} ${j.dst} ${last.db==null?"—":Math.round(last.db)+"%"}</div>
      <div class="mgSmall">確認：<span class="mgChip on">🔎 完整讀回</span> 每個檔寫完都讀回來比對（CRC），一樣才改成正式檔</div>
      ${j.why&&ph==="copy"?`<div class="mgSmall w">⏳ ${esc(j.why)}</div>`:""}${j.slow&&ph==="copy"?`<div class="mgSmall w">💽 硬碟很忙（${j.slow.busy!=null?j.slow.busy+"%":"≥95%"}）：自動降到 ${j.slow.mbps} MB/s，不忙了會慢慢升回來</div>`:""}</div>`;
    h+=`<details class="mgHow"><summary>🚚 怎麼搬的（按一下看）</summary><ol>
      <li>${j.src} 整顆照原本的資料夾複製到 ${j.dst}（回收桶、系統資料夾不搬）；搬的期間程式照舊用 ${j.src}，新錄的也會跟著複製。</li>
      <li>每個檔：先寫成暫存檔 → 寫進硬碟 → 讀回來比對 → 一樣才改成正式檔；斷電只丟掉那一個暫存檔，開機後接著做。</li>
      <li>錄好的影片在搬進硬碟、硬碟或 CPU 很忙、太熱、剛斷電過 → 自己先停，讓監控先。</li>
      <li>${j.src} 上刪掉／改過的，${j.dst} 也跟著；一輪做完沒東西可搬就 30 分鐘再看一次。</li>
      <li>要關機裝硬碟時按「切換到 ${j.dst}」：補最後差異、改路徑；重開機從 ${j.dst} 執行沒問題，才按「清空 ${j.src}」。</li></ol></details>`;
    h+=`<div class="mgDisks">${dcard(j.src,"來源","#f5a524",Hs.map(x=>x.sb),Hs.map(x=>x.srw),last.sb,last.srw)}${dcard(j.dst,"目的","#45d483",Hs.map(x=>x.db),Hs.map(x=>x.drw),last.db,last.drw)}</div>`;
    h+=`<div class="mgCard mgMain"><div class="mgRow1"><span class="mgPct">${pct.toFixed(1)}<small>%</small></span><span class="mgPill ${pill[1]}">${esc(pill[0])}</span></div><div class="mgBar"><i style="width:${pct.toFixed(2)}%"></i></div>
      <div class="mgTiles">
       <div><small>已複製（比對過）</small><b>${G(j.copied_b)}</b><i>${(j.copied_n||0).toLocaleString()} 個</i></div>
       <div><small>還剩</small><b>${G(left)}</b><i>${j.src_files?leftN.toLocaleString()+" 個（上一輪算的）":"第一輪還在算"}</i></div>
       <div><small>最近 6 分鐘速度</small><b>${MB(recent)}</b><i>${j.src} 讀 ${MB(last.srw?last.srw[0]:null)}</i></div>
       <div><small>平均速度</small><b>${MB(avg)}</b><i>${j.t_start?"已經跑了 "+H(now-j.t_start):""}</i></div>
       <div class="${eta?"hi":""}"><small>預計完成</small><b>${eta?new Date((now+eta)*1000).toLocaleString("zh-TW",{hour12:false,month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit"}):"—"}</b><i>${eta?"還要 "+H(eta)+"（"+rateTxt+"）":j.passes?"第一輪完成了，持續同步":"—"}</i></div>
       <div><small>沒複製成</small><b class="${j.failed?"bad":""}">${j.failed||0}</b><i>原檔都還在 ${j.src}</i></div></div>
      <div class="mgSmall">${j.dst} 剩 ${G(d.free)}／${G(d.total)} · ${j.src} 用了 ${G(used)} · 已掃完 ${j.passes||0} 輪${cp.scanning?` · 🔎 掃描中（已看 ${(cp.files||0).toLocaleString()} 個）`:cp.todo?` · 這一輪要搬 ${cp.todo.toLocaleString()} 個，還剩 ${G(cp.todo_b)}（大檔先、小檔最後）`:""}</div></div>`;
    const cf=j.curf;
    h+=`<div class="mgSec">📄 正在處理</div>`;
    if(cf){const p=cf.size?Math.min(100,cf.done/cf.size*100):100;h+=`<div class="mgCur"><div class="mgCi">📥</div><div class="mgCm"><b>${esc(String(cf.rel).split(/[\\/]/).pop())}</b><small>${cf.stage==="比對"?"讀回來比對":"複製到 "+j.dst} · ${G(cf.size)} · ${Math.round(now-cf.t0)} 秒${cf.stage==="複製"?" · "+MB(cf.spd):""}</small></div><span class="mgCp">${p.toFixed(1)}%</span><div class="mgBar sm"><i style="width:${p}%"></i></div><small class="mgPath">${esc(j.dst)}\\${esc(cf.rel)}</small></div>`;}
    else if(j.cur)h+=`<div class="mgCur"><div class="mgCi">📥</div><div class="mgCm"><b>${esc(String(j.cur).split(/[\\/]/).pop())}</b><small>複製到 ${j.dst} · ${MB(last.mine)}</small></div><span class="mgCp"></span><small class="mgPath">${esc(j.dst)}\\${esc(j.cur)}</small></div>`;
    else h+=`<div class="mgCur idle"><div class="mgCi">⏸</div><div class="mgCm"><b>${ph==="copy"?(j.why?esc(j.why):"等下一個"):"沒有在搬"}</b></div></div>`;
    const vc=j.vcur;
    h+=`<div class="mgCur ${cf&&cf.stage==="比對"||vc?"":"idle"}"><div class="mgCi">🔎</div><div class="mgCm"><b>${vc?"二次比對："+esc(String(vc.rel).split(/[\\/]/).pop()):cf&&cf.stage==="比對"?"讀回來比對："+esc(String(cf.rel).split(/[\\/]/).pop()):"確認：沒有"}</b><small>每個檔複製完馬上讀回來比對一次；第一輪搬完後，趁閒再把 ${j.dst} 上的全部讀一次跟指紋比（二次比對）。已二次比對 ${(j.v2_n||0).toLocaleString()} 個（${G(j.v2_b)}）</small></div>${vc?`<span class="mgCp">${(vc.size?Math.min(100,vc.done/vc.size*100):0).toFixed(1)}%</span>`:""}</div>`;
    if(ph==="idle")h+=`<button class="btn mgWide" data-mg="start">▶ 開始複製 ${j.src} → ${j.dst}</button>`;
    if(ph==="copy")h+=`<div class="mgBtns"><button class="btn s mgWide" data-mg="pause" data-v="${j.paused?0:1}">${j.paused?"▶ 繼續":"⏸ 暫停（手上正在搬的做完再停）"}</button><button class="btn s" data-mg="kick">🔎 馬上再掃一輪</button></div>`;
    if(ph==="copy")h+=`<div class="migStep"><b>接下來會自動做：</b>第一輪搬完 → <b>自動切換到 ${j.dst}</b>（錄影、監控不停，之後新的錄影都直接進 ${j.dst}）→ ${j.src} 上搬好的逐一確認後刪掉。<br><b>回家要關機時：</b>按「🏁 收尾」→ 看右下角進度 → 顯示「可以關機了」→ 停止監控並退出、關機 → 換硬碟。<br><button class="btn" data-mg="tail_final" ${(j.passes||0)<1?"disabled":""}>🏁 收尾（準備關機）</button>${(j.passes||0)<1?`<small>第一輪複製完才能按（搬完會自動切換）</small>`:""}</div>`;
    if(ph==="final")h+=`<div class="migStep">🔁 ${esc(j.final||"切換中")}…（錄影、監控照常）</div>`;
    if(ph==="switched"){const T=j.tail||{},rd=T.ready,fs=T.fast;
      h+=`<div class="migStep ok">✔ 已切換：新的錄影都直接進 ${j.dst}，${j.src} 不會再有新檔進來。改了 ${j.rewrote||0} 處存起來的路徑。<br>
      ${j.src} 上搬好的：每 10 分鐘逐一確認（${j.dst} 上一樣大、複製時讀回來比對過）就刪掉；放超過 30 分鐘沒動的才刪。程式資料夾裡的設定、頭像這些小檔重開前還在用，只複製、不刪（${j.dst} 上都有）。<br>
      <b>收尾：</b>${T.stage==="補複製"?"補複製中…":T.stage==="確認後刪除"?"確認後刪除中…":"等下一輪"}${T.t_last?` · ${j.src} 上還有 <b>${(T.left_n||0).toLocaleString()} 個（${G(T.left_b||0)}）</b>要處理`:""} · 已刪 ${(T.deleted||0).toLocaleString()} 個（${G(T.deleted_b||0)}）${T.copied?` · 補複製 ${T.copied} 個`:""}${T.keep_n?` · 程式小檔 ${T.keep_n} 個（只複製）`:""}</div>`;
      h+=rd?`<div class="migStep ok" style="font-size:1.1em">✅ <b>收尾完成，可以關機了</b>${T.left_n?`（${j.src} 上還有 ${T.left_n} 個刪不掉的，${j.dst} 上都有）`:""}<br>① 按「停止監控並退出」 → ② 關機 → ③ 把 ${j.dst} 接 SATA 裝進主機、拔掉 ${j.src} → ④ 開機 → ⑤ 磁碟管理確認新硬碟是 <b>${j.dst}</b> 槽 → ⑥ 開程式（找不到 ${j.dst} 會先不監控）</div>`
        :`<button class="btn mgWide" data-mg="tail_final" ${fs?"disabled":""}>${fs?"🏁 收尾中…（全速）":"🏁 收尾（準備關機）"}</button>`;}
    if(ph==="verify"){const T=j.tail||{};h+=`<div class="migStep ok">✔ 現在從 ${j.dst} 執行（影片資料夾：${esc(j.video_root)}），${j.src} 是外接的舊硬碟。<br>
      ${j.src} 上的每 10 分鐘自動比對一輪：${j.dst} 上有一樣的 → 確認後刪；${j.dst} 上沒有的 → 放回 ${j.dst} 同一個位置再刪；不一樣的不蓋掉 ${j.dst} 在用的，放到 ${j.dst}\\從E槽多出來的。全部處理完會顯示「搬硬碟完成」，${j.src} 就是空的。<br>
      <b>現在：</b>${T.stage==="確認後刪除"?"比對、刪除中…"+(T.cur?" "+esc(String(T.cur).split(/[\\/]/).pop()):""):"等下一輪"} · 已刪 ${(T.deleted||0).toLocaleString()} 個（${G(T.deleted_b||0)}）${T.t_last?` · ${j.src} 上還有 <b>${(T.left_n||0).toLocaleString()} 個（${G(T.left_b||0)}）</b>`:""}${T.copied?` · 放回 ${T.copied} 個`:""}${T.extra?` · 不一樣的 ${T.extra} 個`:""}${T.err?` · 錯誤 ${T.err} 個（下一輪再試）`:""}</div>
      <button class="btn mgWide" data-mg="tail_final" ${T.fast?"disabled":""}>${T.fast?"⚡ 全速處理中…":"⚡ 全速處理（不用等）"}</button>`;}
    if(ph==="done"&&j.clean)h+=`<div class="migStep ok">✔ ${j.src} 清空了 ${j.clean.files} 個檔（${G(j.clean.bytes)}）${j.clean.extra?`，另外 ${j.clean.extra} 個切換後才有的放到 ${j.dst}\\從E槽多出來的`:""}${j.clean.junk?`（其中 ${j.clean.junk} 個是暫存檔／已轉好的 FLV，直接刪）`:""}${j.clean.err?`，錯誤 ${j.clean.err} 個`:""}。<br><b>搬硬碟完成，${j.src} 可以拔掉了。</b>${j.clean.sys_b?`${j.src} 上還用著的 ${G(j.clean.sys_b)} 是 Windows 自己的（資源回收筒、系統還原、檔案系統本身），不是 TikLive 的資料，格式化就清掉。`:""}</div>`;
    const JK=j.junk||{},JL=[["tmp","寫到一半的暫存檔（.copying／.part…）","不搬，清空 "+j.src+" 時一起刪"],["flv_done","已經轉好 MP4 的 FLV","旁邊有同名 MP4：不搬，清空 "+j.src+" 時一起刪"],["flv_todo","還沒轉檔的 FLV","是錄影原始檔：照常搬過去，之後在 "+j.dst+" 轉"]].filter(x=>JK[x[0]]&&JK[x[0]][0]);
    if(JL.length)h+=`<div class="mgSec">🗑 不搬的垃圾／要注意的檔${j.junk_t?`<small style="opacity:.6;font-weight:400">（上一次掃描 ${new Date(j.junk_t*1000).toLocaleString("zh-TW",{hour12:false,month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit"})}）</small>`:""}</div><div class="mgList">${JL.map(([k,t,d])=>`<details><summary><b>${t}</b> ${JK[k][0].toLocaleString()} 個 · ${G(JK[k][1])}<small> — ${d}</small></summary>${JK[k][2].map(p=>`<div class="mgJp">${esc(p)}</div>`).join("")}${JK[k][0]>JK[k][2].length?`<div class="mgJp">…還有 ${(JK[k][0]-JK[k][2].length).toLocaleString()} 個</div>`:""}</details>`).join("")}</div>`;   /* V1.1.12 */
    const rc=j.recent||[];
    h+=`<div class="mgSec">✅ 最近搬好的</div><div class="mgList">${rc.length?rc.map(x=>`<div><span class="ok">✔</span><div><b>${esc(String(x.rel).split(/[\\/]/).pop())}</b><small>${G(x.size)} → ${j.dst} · 複製 ${x.tc} 秒 · 比對 ${x.tv} 秒</small></div><i>${T(x.t)}</i></div>`).join(""):`<div class="mgE">還沒有（這次開程式之後搬好的會列在這裡）</div>`}</div>`;
    if((j.errors||[]).length)h+=`<details class="migErr"><summary>⚠ 最近的問題（${j.errors.length}）</summary>${j.errors.slice().reverse().map(e=>`<div><i>${new Date(e[0]*1000).toLocaleString("zh-TW",{hour12:false})}</i> ${esc(e[1])}</div>`).join("")}</details>`;
    const op_=[...root.querySelectorAll("details")].map((d,i)=>d.open?(d.className||"")+"|"+(d.querySelector("summary")||{}).textContent:"").filter(Boolean);   /* V1.1.22 點開的不會被重畫收起來 */
    root.innerHTML=h;if(op_.length)root.querySelectorAll("details").forEach(d=>{const k=(d.className||"")+"|"+(d.querySelector("summary")||{}).textContent;if(op_.some(x=>x.split("|")[0]===(d.className||"")&&x.split("|")[1].slice(0,6)===k.split("|")[1].slice(0,6)))d.open=true;});clearTimeout(root._t);root._t=setTimeout(draw,4000);}
  root.onclick=async e=>{const b=e.target.closest("[data-mg]");if(b){const op=b.dataset.mg;
      if(op==="tail_final"&&!confirm("收尾？\n\n全速把舊硬碟上剩的補到新硬碟、確認後刪掉。錄影、監控照常，不用停。\n完成會顯示「可以關機了」。"))return;
      if(op==="final"&&!confirm("切換到新硬碟？\n\n會先暫停搬進硬碟幾分鐘、補最後差異，再把程式改成用新硬碟。錄影、監控照常。\n切換好之後就可以關機裝硬碟。"))return;
      if(op==="clean"&&(!confirm("清空來源硬碟？\n\n只刪新硬碟上確定有一樣大小的檔；切換後才改過的會先複製一份過去再刪。")||prompt("確定的話請輸入：清空")!=="清空"))return;
      await post({op,v:b.dataset.v==="1"});draw();}};
  root.oninput=e=>{if(e.target.classList.contains("mgRange")){const v=root.querySelector(".mgBigV");if(v)v.innerHTML=e.target.value+" <small>MB/s</small>";}};
  root.onchange=async e=>{if(e.target.classList.contains("mgRange")){await post({op:"mbps",v:+e.target.value});e.target.blur();draw();}};
  draw();}
async function gsdMount(root,days){days=days||14;root.innerHTML='<div class="sbkE">計算中…</div>';   /* TK_V1.0.84 🎛 顯示卡供需 */
  const j=await (typeof api==="function"?api:J)("/api/pc/gpusd?days="+days);if(!j||!j.ok){root.innerHTML='<div class="sbkE">讀不到</div>';return;}
  const e_=s=>String(s==null?"":s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));const mn=Math.round(j.ratio*60*10)/10;
  const R=j.rows.slice().reverse();const mx=Math.max(1,...j.rows.map(r=>r.rec_h));
  const T=j.th||{};const thH=T.on?`<div class="hpTop ${T.hot?"bad":"ok"}"><b>🌡 控溫開著：背景轉檔／字幕整組 CPU ${T.cap!=null?"最多 "+T.cap+"%":"（還沒有背景重活在跑）"}${T.hot?` · 顯示卡 ${Math.round(T.gtemp)}°C 太熱，新的先等`:""}</b><small>整台預算 ${T.budget!=null?T.budget:T.cpu}%（${T.sc!=null?"SortCut 有開":"SortCut 沒開"}）− 錄影和其他 ${T.others??"—"}% · 現在用 ${T.job??0}%（${T.active||0} 個在跑）${T.gtemp?` · 顯示卡 ${Math.round(T.gtemp)}°C／上限 ${T.glim}°C`:""}${T.err?` · ⚠ ${e_(T.err)}`:""}。設定 → 自動處理 → 🌡 可以改。</small></div>`+(T.alert?`<div class="hpTop bad"><b>⚡ 電腦斷電重開過：已叫 SortCut ${T.alert.mode==="stop"?"停止轉檔":"降到最低"}（到 ${new Date(T.alert.until*1000).toLocaleString("zh-TW",{hour12:false})}）</b><small>24 小時內斷電 ${T.alert.n24} 次、7 天 ${T.alert.n7d} 次 · ${T.ack_ok?"✔ SortCut 已配合："+e_(T.ack.did||T.ack.mode||""):"SortCut 還沒回應（它更新支援後會回）"}${T.alert.evidence?" · "+e_(T.alert.evidence):""}</small></div><div class="hoB"><button class="pill" data-tha="clear">解除警報（SortCut 恢復正常）</button></div>`:"")+((T.power7||[]).length?`<div class="sbkN">最近 7 天沒正常關閉：${T.power7.map(r=>`${new Date(r.t*1000).toLocaleString("zh-TW",{hour12:false})} ${r.kind==="power"?"⚡ 斷電":r.kind==="crash"?"程式沒了":"有人重開"}`).join("、")}</div>`:""):`<div class="hpTop warn"><b>🌡 控溫關著</b><small>主機板會過熱斷電的話，到設定 → 自動處理 → 🌡 控溫打開。</small></div>`;   /* TK_V1.0.100 */
  root.innerHTML=thH+`<div class="hpTop ${j.lv}"><b>${j.lv==="ok"?"✔ ":j.lv==="warn"?"⚠ ":"❗ "}${e_(j.v)}</b><small>最近 ${j.days} 天 · ${e_(j.gpu||"沒有顯示卡")}${j.use_gpu?"":"（字幕現在用 CPU 轉）"}</small></div>
  <div class="hpX gsdX">
  <div><small>每天平均錄到（要轉字幕的量）</small><b>${j.avg_rec_h} 小時 · ${j.avg_rec_n} 場</b></div>
  <div><small>全速轉完一天的量要</small><b>${j.need_h} 小時 · 一天的 ${j.load}%</b></div>
  <div><small>字幕速度（${j.learned?`學了 ${j.learned} 場`:"預設值"}）</small><b>1 小時錄音 ≈ ${mn} 分鐘</b></div>
  <div><small>每天平均轉完</small><b>${j.avg_done_n} 場</b></div>
  <div><small>現在排隊</small><b>${j.q} 場${j.q_age!=null?` · 最舊的 ${j.q_age} 天前`:""}</b></div>
  <div><small>顯示卡 閒／輕／忙（每分鐘平均）</small><b>${j.idle_pct!=null?`${j.idle_pct}%／${j.light_pct}%／${j.busy_pct}%`:"這版開始記錄"}</b></div></div>
  <div class="sbkN">怎麼看：<b>全速要幾 %</b> 是「顯示卡全力轉，一天要花多少時間才轉得完當天錄到的」——低於 50% 就很充裕。實際上背景是用低功耗慢慢轉（每場最慢 ${j.plan&&j.plan.hours||6} 小時內轉完、最少用 ${j.plan&&j.plan.min||20}% 力氣），所以排隊有十幾場是正常的；要看的是<b>排隊最舊的那場是不是超過 2 天</b>、排隊數是不是每天越來越多。<br>閒＝顯示卡用不到 10%、輕＝10～35%、忙＝35% 以上；${j.hist_min?`已經記了 ${Math.round(j.hist_min/60)} 小時`:"更新後每分鐘記一筆，明天開始就看得到每天的比例"}。</div>
  <div class="hoT">📅 每天</div><div class="gsdT"><div class="gsdH"><span>日期</span><span>錄到</span><span>轉完字幕</span><span>顯示卡 閒／輕／忙</span></div>
  ${R.map(r=>{const m=r.m||0,pi=m?r.idle/m*100:0,pl=m?r.light/m*100:0,pb=m?r.busy/m*100:0;return `<div class="gsdR"><span>${r.d.slice(5)}</span><span><i class="gsdB" style="width:${Math.round(r.rec_h/mx*100)}%"></i><em>${r.rec_h}h · ${r.rec_n} 場</em></span><span><em>${r.done_n} 場${r.done_h?` · ${r.done_h}h`:""}</em></span><span>${m?`<i class="gsdG"><u style="width:${pi}%"></u><u style="width:${pl}%"></u><u style="width:${pb}%"></u></i><em>${Math.round(pi)}／${Math.round(pl)}／${Math.round(pb)}%${r.g!=null?` · 平均 ${r.g}%`:""}${r.q1!=null?` · 排隊 ${r.q0}→${r.q1}`:""}</em>`:"<em>—</em>"}</span></div>`;}).join("")}</div>
  <div class="hoB">${[7,14,30].map(d=>`<button class="pill${d===j.days?" on":""}" data-d="${d}">${d} 天</button>`).join("")}<button class="pill" data-d="${j.days}">↻ 重新計算</button></div>`;
  root.onclick=async e=>{const t=e.target.closest("[data-tha]");if(t){if(!confirm("解除斷電警報？SortCut 會恢復正常速度。"))return;const r=await (typeof kPost==="function"?kPost:rvPost)("/api/pc/th/alert",{op:"clear"});if(typeof toast==="function")toast((r&&r.ok?"✔ ":"✖ ")+((r&&r.message)||""));gsdMount(root,days);return;}const b=e.target.closest("[data-d]");if(b)gsdMount(root,+b.dataset.d);};}
async function hpMount(root){root.innerHTML='<div class="sbkE">檢查中…</div>';   /* TK_V1.0.69 🩺 一頁健檢 */
  const j=await (typeof api==="function"?api:J)("/api/pc/health");if(!j||!j.ok){root.innerHTML='<div class="sbkE">讀不到</div>';return;}const X=j.x||{},I=j.items||[];
  const nb=I.filter(x=>x.lv==="bad").length,nw=I.filter(x=>x.lv==="warn").length;const ago=t=>{if(!t)return "沒有";const h=(Date.now()/1000-t)/3600;return h<1?"不到 1 小時前":h<48?Math.round(h)+" 小時前":Math.round(h/24)+" 天前";};
  root.innerHTML=`<div class="hpTop ${nb?"bad":nw?"warn":"ok"}"><b>${nb?`❗ 有 ${nb} 件要馬上處理`:nw?`⚠ 有 ${nw} 件要留意`:"✔ 一切正常"}</b><small>${new Date(j.t*1000).toLocaleTimeString()} 檢查 · 共 ${I.length} 項</small></div>
  ${I.map(x=>`<button class="hpI ${x.lv||""}" data-k="${esc(x.k)}"><span>${x.ic||""}</span><div><b>${esc(x.t)}</b><small>${esc(x.v)}</small></div><i>›</i></button>`).join("")}
  <div class="hoT">🔧 平常不會跳出來的數字</div><div class="hpX">
  <div><small>版本</small><b>V${esc(X.ver||"")}</b></div><div><small>開著之後熱更新</small><b>${X.hot??"—"} 次</b></div><div><small>主程式記憶體</small><b>${X.mem_gb??"—"} GB</b></div>
  <div><small>字幕搜尋庫</small><b>${X.stt_idx??"—"}／${X.stt_tot??"—"} 場${X.stt_run?" · 整理中":""}</b></div><div><small>最近一次小檔備份</small><b>${ago(X.sbk_last)}</b></div><div><small>硬碟小工具資料</small><b>${X.disk_fresh?"✔ 有在更新":"⚠ 15 分鐘沒更新"}</b></div></div>
  <div class="hoB"><button class="pill" data-a="re">↻ 重新檢查</button></div>`;
  root.onclick=e=>{const b=e.target.closest("[data-k]");if(b){if(typeof smtGo==="function")smtGo(b.dataset.k);return;}if(e.target.closest('[data-a="re"]'))hpMount(root);};}
async function dtlMount(root){const A={day:""};   /* TK_V1.0.49 📅 一天的時間軸 */
  const fmtD=d=>`${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,"0")}-${String(d.getDate()).padStart(2,"0")}`;
  const L=async()=>{const j=await (typeof api==="function"?api:J)("/api/pc/daytl?day="+A.day);if(!j||!j.ok)return;A.day=j.day;const LC={"-2":"#ff4d6d","-1":"#ff8c42","0":"#f0c419","1":"#9ad94a","2":"#2ecc71"};
    root.innerHTML=`<div class="dtlT"><button class="pill" data-d="-1">‹ 前一天</button><b>${j.day}</b><button class="pill" data-d="1">後一天 ›</button><span>${j.rows.length} 位 · ${j.n} 場 · 共 ${j.hours} 小時${j.miss?` · <b style="color:#ff8c9f;font-size:12px">漏開頭 5 分以上 ${j.miss} 場</b>`:""}</span></div>
    <div class="dtlG"><div class="dtlH"><i></i><div>${[0,3,6,9,12,15,18,21].map(h=>`<u style="left:${h/24*100}%">${h}</u>`).join("")}</div></div>
    ${j.rows.map(r=>`<div class="dtlR"><i title="@${esc(r.u)}" data-u="${esc(r.u)}">${esc(r.n)}</i><div>${j.now!=null?`<em style="left:${j.now/24*100}%"></em>`:""}${r.b.map(b=>`<s data-sid="${b.sid}" title="${esc(b.lab)} ${esc(b.start||"")} · ${esc(b.dur||"")}${b.pct!=null?" · 錄到 "+b.pct+"%":""}" class="${b.live?"on":""}" style="left:${b.a/24*100}%;width:${Math.max(0.6,(b.z-b.a)/24*100)}%;--lc:${b.lv==null?"transparent":LC[String(b.lv)]}">${b.r!=null&&b.r>b.a?`<b style="width:${(b.r-b.a)/(b.z-b.a)*100}%"></b>`:""}</s>`).join("")}</div></div>`).join("")||'<div class="sbkE">這天沒有直播紀錄</div>'}</div>
    ${(j.pred||[]).map(r=>`<div class="dtlR dtlP"><i title="@${esc(r.u)}" data-u="${esc(r.u)}">${esc(r.n)}</i><div>${j.now!=null?`<em style="left:${j.now/24*100}%"></em>`:""}<s class="pd" title="過去 60 天的這個星期幾，有 ${r.c} 次在 ${r.h} 點開播" style="left:${r.h/24*100}%;width:${100/24}%"></s></div></div>`).join("")}
    <div class="dtlN">一條＝一場直播（開播→下播）；<b class="k3"></b>可能會開（照過去 60 天同一個星期幾）；<b class="k1"></b>錄到的部分　<b class="k2"></b>漏掉的開頭；下面的色條＝保存等級；紅線＝現在。點一條跳到那一場、點名字看主播總覽。</div>`;};
  root.onclick=e=>{const d=e.target.closest("[data-d]");if(d){const x=new Date(A.day+"T12:00:00");x.setDate(x.getDate()+(+d.dataset.d));A.day=fmtD(x);L();return;}
    const s=e.target.closest("[data-sid]");if(s){lvsFocus(+s.dataset.sid);return;}const u=e.target.closest("[data-u]");if(u&&typeof hostOpen==="function")hostOpen(u.dataset.u);};L();}
function hoColGet(){try{return JSON.parse(localStorage.getItem("ho_col")||"[]")||[];}catch(e){return [];}}   /* TK_V1.0.63 主播總覽：每一區可以收合（記住） */
function hoColApply(root){const C=hoColGet();let hide=false;for(const el of [...root.children]){if(el.classList.contains("hoT")){const k=el.textContent.replace(/[（(].*$/,"").trim();hide=C.includes(k);el.classList.toggle("hoTc",hide);continue;}if(el.classList.contains("hoB")){el.style.display="";hide=false;continue;}if(hide)el.style.display="none";else if(el.style.display==="none")el.style.display="";}}
async function hostMount(root,u){u=u||window.HOST_U||"";root.innerHTML='<div class="sbkE">讀取中…</div>';   /* TK_V1.0.42 主播總覽 */
  const j=await (typeof api==="function"?api:J)("/api/pc/host?u="+encodeURIComponent(u));if(!j||!j.ok){root.innerHTML=`<div class="sbkE">${esc((j&&j.message)||"讀不到")}</div>`;return;}
  if(j.pick){const P=j.pick.slice().sort((a,b)=>(b[2]-a[2])||(b[3]-a[3]));root.innerHTML=`<div class="sbkN">選一位主播看總覽（🔴 直播中、⭐ 重點主播排前面）</div><input class="hoPq" placeholder="🔎 打帳號或名字" autocomplete="off"><div class="hoPk">${P.map(r=>`<button data-pu="${esc(r[0])}" data-k="${esc((r[0]+" "+r[1]).toLowerCase())}"><img loading="lazy" src="${imgB(B)}/avatar/${encodeURIComponent(r[0])}" onerror="this.style.visibility='hidden'"><b>${r[2]?"🔴 ":""}${r[3]?"⭐ ":""}${esc(r[1])}</b><small>@${esc(r[0])}</small></button>`).join("")}</div>`;   /* TK_V1.0.66 */
    root.querySelector(".hoPq").oninput=e=>{const q=e.target.value.trim().toLowerCase();root.querySelectorAll("[data-pu]").forEach(b=>b.style.display=!q||b.dataset.k.includes(q)?"":"none");};
    root.onclick=e=>{const b=e.target.closest("[data-pu]");if(b)hostOpen(b.dataset.pu);};return;}
  const WD=["一","二","三","四","五","六","日"],mx=Math.max(1,...j.hm.flat());const LC={"-2":["−2","#ff4d6d"],"-1":["−1","#ff8c42"],"0":["0","#f0c419"],"1":["+1","#9ad94a"],"2":["+2","#2ecc71"],"none":["未分","#6b7280"]};
  const lvT=Object.values(j.lv).reduce((a,b)=>a+b,0)||1;const ytN=(j.yt.ready||0),ytW=(j.yt.wait||0)+(j.yt.up||0);
  root.innerHTML=`<div class="hoH"><img src="${imgB(B)}/avatar/${encodeURIComponent(j.u)}" onerror="this.style.visibility='hidden'"><div><b>${esc(j.name)}${j.pri?" ⭐":""}${j.live?' <span class="hoLive">🔴 直播中</span>':""}</b><small>@${esc(j.u)} · 共 ${j.n_all} 場 · 影片 ${j.gb} GB</small></div></div>
  <div class="hoK"><div><b>${j.n14}</b><small>14 天場數</small></div><div><b>${j.h14}</b><small>14 天小時</small></div><div><b>${j.pct14==null?"—":j.pct14+"%"}</b><small>平均錄到</small></div><div><b>${j.n60}</b><small>60 天場數</small></div></div>
  ${j.next?`<div class="hoNx">🔮 下次最可能：<b>${(()=>{const d=new Date(j.next.t*1000),dd=Math.round((d-new Date())/3600000);return `週${WD[(d.getDay()+6)%7]} ${d.getHours()}:00`+(dd<=24?`（約 ${dd} 小時後）`:"");})()}</b><small>最近 60 天這個時段開過 ${j.next.n} 次${j.top&&j.top.length?" · 常開："+j.top.map(([d,h,n])=>`週${WD[d]} ${h} 點（${n}）`).join("、"):""}</small></div>`:'<div class="hoNx"><small>🔮 開播時間還不固定（60 天內沒有同一個時段開過 2 次以上）</small></div>'}
  <div class="hoT">🕒 什麼時候在播（最近 60 天，越亮越常）</div><div class="hoHm"><i></i>${[0,3,6,9,12,15,18,21].map(h=>`<u style="grid-column:${h+2}/span 3">${h}</u>`).join("")}${j.hm.map((r,d)=>`<i>${WD[d]}</i>`+r.map((v,h)=>`<s title="週${WD[d]} ${h}:00 · ${v} 次" style="opacity:${v?0.18+0.82*v/mx:0.06}"></s>`).join("")).join("")}</div>
  <div class="hoT">📆 最近 5 週每天（越亮播越久）</div><div class="hoCal">${WD.map(w=>`<u>${w}</u>`).join("")}${(()=>{const t0=new Date();t0.setHours(0,0,0,0);const st=new Date(t0);st.setDate(st.getDate()-((t0.getDay()+6)%7)-28);let h="";for(let i=0;i<35;i++){const d=new Date(st);d.setDate(st.getDate()+i);const k=`${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,"0")}-${String(d.getDate()).padStart(2,"0")}`,v=(j.cal||{})[k]||0,fut=d>t0;h+=`<s class="${fut?"fu":""}${+d===+t0?" td":""}" title="${d.getMonth()+1}/${d.getDate()}${v?` · ${v} 小時`:" · 沒播"}" style="${v?`background:rgba(77,201,255,${Math.min(1,0.25+v/6)})`:""}">${d.getDate()}</s>`;}return h;})()}</div>   <!-- TK_V1.0.68 -->
  <div class="hoT">🗂 保存等級</div><div class="hoLv">${Object.keys(LC).filter(k=>j.lv[k]).map(k=>`<span style="flex:${j.lv[k]};background:${LC[k][1]}" title="${LC[k][0]}：${j.lv[k]} 場">${j.lv[k]/lvT>0.08?LC[k][0]+" "+j.lv[k]:""}</span>`).join("")}</div>
  <div class="hoChip">${j.phone?`<span>📱 手機錄屏 ${j.phone} 段</span>`:""}${ytN||ytW?`<span>▶ YouTube 已傳 ${ytN}${ytW?` · 排隊 ${ytW}`:""}</span>`:""}</div>
  <div class="hoT">🎁 禮物（最近 8 週，每週鑽石）</div><div id="hoGift" class="hoGift"><div class="sbkE">讀取中…</div></div>
  ${(j.notes||[]).length?`<div class="hoT">📝 我寫過的筆記（${j.notes.length}）</div>${j.notes.map(x=>`<button class="hoS hoNt" data-sid="${x.id}"><b>${esc(x.lab)}</b><span>${esc(x.tx)}</span><small>${esc((x.start||"").slice(5,16))}</small></button>`).join("")}`:""}   <!-- TK_V1.0.62 -->
  <div class="hoT">🎞 最近 8 場</div>${j.last.map(x=>`<button class="hoS" data-sid="${x.id}"><b>${esc(x.lab)}</b><span>${esc(x.start)} · ${esc(x.dur)}${x.live?" · 🔴":""}</span><small>${x.pct!=null?x.pct+"%":""}</small><em style="background:${(LC[x.lv==null?"none":String(x.lv)]||LC.none)[1]}">${(LC[x.lv==null?"none":String(x.lv)]||LC.none)[0]}</em></button>`).join("")}
  <div class="hoB"><button class="pill" data-a="fx">▦ 在檔案總管看全部場次</button><button class="pill" data-a="gifs">🎞 GIF 製作</button><button class="pill" data-a="sw">⇄ 換一位</button><a class="pill" href="https://www.tiktok.com/@${encodeURIComponent(j.u)}/live" target="_blank" rel="noopener">↗ 在 TikTok 打開</a><button class="pill" data-a="cp">📋 複製帳號</button>${j.mon?`<button class="pill" data-a="pri">${j.pri?"★ 取消重點主播":"☆ 設為重點主播"}</button>`:""} <a class="pill" href="${B}/api/pc/export/sessions?days=365&u=${encodeURIComponent(j.u)}" download>📤 匯出這位一年的場次（CSV）</a></div>`;
  hoColApply(root);
  (async()=>{const g=await (typeof api==="function"?api:J)("/api/pc/hostgift?u="+encodeURIComponent(j.u));const el=root.querySelector("#hoGift");if(!el)return;   /* TK_V1.0.61 */
    if(!g||!g.ok){el.innerHTML='<div class="sbkE">讀不到</div>';return;}if(!g.tot){el.innerHTML='<div class="sbkE">60 天內沒有收到禮物的紀錄</div>';return;}const mx=Math.max(1,...g.wk.map(x=>x.v));
    el.innerHTML=`<div class="hoWk">${g.wk.map(x=>`<div title="${x.d} 那週 ${x.v.toLocaleString()} 鑽"><s style="height:${Math.max(2,x.v/mx*56)}px"></s><small>${x.d}</small></div>`).join("")}</div>
    <div class="hoGs">60 天共 <b>${g.tot.toLocaleString()}</b> 鑽 · ${g.n} 位送禮者 · 前 10 位：</div>${g.top.map((r,i)=>`<button class="hoGf" data-gf="${esc(r[0])}"><i>${i+1}</i><b>${esc(r[1]||r[0])}</b><small>${r[3]} 場</small><em>${(+r[2]).toLocaleString()} 鑽</em></button>`).join("")}`;})();
  root.onclick=e=>{const ht=e.target.closest(".hoT");if(ht){const k=ht.textContent.replace(/[（(].*$/,"").trim();const C=hoColGet();if(C.includes(k))C.splice(C.indexOf(k),1);else C.push(k);try{localStorage.setItem("ho_col",JSON.stringify(C));}catch(x){}hoColApply(root);return;}const s=e.target.closest("[data-sid]");if(s){lvsFocus(+s.dataset.sid);return;}const gf=e.target.closest("[data-gf]");if(gf){const k=gf.dataset.gf;if(typeof PAGES!=="undefined"&&typeof go==="function"){go(3);setTimeout(()=>{try{PAGES[3].detail(k);}catch(x){}},400);}else location.hash="gifter/"+encodeURIComponent(k);return;}if(e.target.closest('[data-a="fx"]'))qsUser(j.u);if(e.target.closest('[data-a="gifs"]')){gfsOpen(j.u);return;}if(e.target.closest('[data-a="sw"]')){window.HOST_U="";hostMount(root,"");return;}if(e.target.closest('[data-a="cp"]')){const v="@"+j.u,fb=()=>{const ta=document.createElement("textarea");ta.value=v;ta.style.cssText="position:fixed;opacity:0;top:0";document.body.appendChild(ta);ta.select();let ok=false;try{ok=document.execCommand("copy");}catch(x){}ta.remove();toast(ok?"📋 已複製 "+v:"請長按選取："+v);};try{if(navigator.clipboard&&window.isSecureContext)navigator.clipboard.writeText(v).then(()=>toast("📋 已複製 "+v),fb);else fb();}catch(x){fb();}return;}   /* TK_V1.0.65 */
    const pb=e.target.closest('[data-a="pri"]');if(pb){pb.disabled=true;kPost("/api/pc/streamer/priority",{u:j.u,on:!j.pri}).then(r=>{if(r&&r.ok){toast(r.priority?"★ 設為重點主播（斷線會更快重連、開播會提醒）":"已取消重點主播");hostMount(root,j.u);}else{pb.disabled=false;toast("✖ "+((r&&r.message)||"沒有成功"));}});}};}   /* TK_V1.0.59 */
async function dhhMount(root){const A={days:30};   /* TK_V1.0.40 硬碟健康歷史 */
  const sp=(V,col,mx)=>{const P=V.map((v,i)=>v==null?null:[i,v]).filter(Boolean);if(!P.length)return '<span class="dhhNo">沒有資料</span>';const W=220,H=40,n=Math.max(1,V.length-1),lo=Math.min(...P.map(x=>x[1])),hi=Math.max(mx||0,...P.map(x=>x[1]));const y=v=>H-3-(hi===lo?0.5:(v-lo)/(hi-lo))*(H-6);
    return `<svg viewBox="0 0 ${W} ${H}" class="dhhSv"><polyline fill="none" stroke="${col}" stroke-width="2" points="${P.map(([i,v])=>`${(i/n*(W-4)+2).toFixed(1)},${y(v).toFixed(1)}`).join(" ")}"/></svg>`;};
  const L=async()=>{const j=await (typeof api==="function"?api:J)(`/api/pc/dhist?days=${A.days}`);if(!j)return;
    root.innerHTML=`<div class="sbkN">每小時記一次每顆硬碟的<b>溫度、讀寫錯誤、健康狀態</b>（資料來自每分鐘的硬碟小工具），看長期有沒有變差。錯誤數一直往上＝該準備換硬碟了。</div>
    <div class="actT"><select id="dhD">${[7,14,30,60].map(d=>`<option value="${d}"${d===A.days?" selected":""}>${d} 天</option>`).join("")}</select>${j.fresh?"":'<span class="dhhW">⚠ 硬碟小工具最近 15 分鐘沒有新資料（設定 → 效能 可以裝／重開）</span>'}</div>
    ${(j.alerts||[]).map(x=>`<div class="dhhA ${x.lv}">🩺 ${esc(x.name)}：${esc(x.why)}</div>`).join("")}
    ${(j.disks||[]).map(d=>{const T=d.days.map(x=>x[1]),Rr=d.days.map(x=>x[2]+x[3]),last=d.days[d.days.length-1]||[];const t0=T.filter(v=>v!=null);
      return `<div class="dhhD"><div class="dhhH"><b>💽 ${esc(d.name)}</b><span>${last[4]?esc(last[4]):""}</span></div>
      <div class="dhhR"><small>最高溫 ${t0.length?Math.max(...t0).toFixed(0)+"°C":"—"}（今天 ${last[1]!=null?(+last[1]).toFixed(0)+"°C":"—"}）</small>${sp(T,"#ffb547",55)}</div>
      <div class="dhhR"><small>讀＋寫錯誤累計 ${(last[2]||0)+(last[3]||0)}${Rr.length>1&&Rr[Rr.length-1]>Rr[0]?` <b class="bad">↑ 期間多了 ${Rr[Rr.length-1]-Rr[0]}</b>`:""}</small>${sp(Rr,"#ff4d6d")}</div></div>`;}).join("")||'<div class="sbkE">還沒有紀錄：程式開著、硬碟小工具有在跑，每小時會記一筆</div>'}`;
    root.querySelector("#dhD").onchange=e=>{A.days=+e.target.value;L();};};L();}
async function sbkMount(root){root.innerHTML='<div class="sbkE">讀取中…</div>';const L=async()=>{const j=await api("/api/pc/sbk");const T=t=>{const d=new Date(t*1000);return `${d.getMonth()+1}/${d.getDate()} ${String(d.getHours()).padStart(2,"0")}:${String(d.getMinutes()).padStart(2,"0")}`;};
  root.innerHTML=`<div class="sbkN">每天自動把分級、YouTube 排隊、手機錄屏紀錄、標記等設定小檔（_DB_SSD 裡的 JSON，不含影片和大資料庫）壓成一份備份，留最近 14 份。<br><small>${esc((j&&j.dir)||"")}</small></div><button class="pill sbkGo" id="sbkGo">🗂 現在備份一份</button>
  <div class="sbkL">${((j&&j.list)||[]).map(x=>`<div class="sbkR"><b>${T(x.t)}</b><span>${x.mb} MB</span><a class="pill" href="${B}/api/pc/sbk/file?f=${encodeURIComponent(x.f)}">⬇ 下載</a></div>`).join("")||'<div class="sbkE">還沒有備份（程式開著、電腦不忙時每天會自動做一份）</div>'}</div>`;
  $("#sbkGo").onclick=async()=>{$("#sbkGo").disabled=true;$("#sbkGo").textContent="備份中…";const r=await kPost("/api/pc/sbk",{});toast(r&&r.ok?`✔ 備份好了：${r.n} 個檔、${r.mb} MB`:"✖ "+((r&&r.message)||"沒有成功"));L();};};L();}
PAGES[46]={render(pg){pg.innerHTML=`<div class="pg" style="overflow:auto;padding:14px;max-width:900px"><div id="actRoot"></div></div>`;actMount(pg.querySelector("#actRoot"));}};
PAGES[52]={render(pg){pg.innerHTML=`<div class="pg" style="overflow:auto;padding:14px;max-width:760px"><div id="cvRoot"></div></div>`;csvMount(pg.querySelector("#cvRoot"));}};   /* TK_V1.0.51 */
PAGES[51]={render(pg){pg.innerHTML=`<div class="pg" style="overflow:auto;padding:14px"><div id="dtlRoot"></div></div>`;dtlMount(pg.querySelector("#dtlRoot"));}};   /* TK_V1.0.49 */
PAGES[50]={render(pg,arg){pg.innerHTML=`<div class="pg" style="overflow:auto;padding:14px;max-width:820px"><div id="hoRoot"></div></div>`;hostMount(pg.querySelector("#hoRoot"),arg||window.HOST_U);}};   /* TK_V1.0.42 */
PAGES[54]={render(pg,arg){pg.innerHTML=`<div class="pg" style="overflow:auto;padding:14px;max-width:900px"><div id="gfsRoot"></div></div>`;gfsMount(pg.querySelector("#gfsRoot"),arg||window.GIFS_U);}};   /* TK_V1.0.75 */
PAGES[56]={render(pg){pg.innerHTML=`<div class="pg" style="overflow:auto;padding:14px;max-width:960px"><div id="yhcRoot"></div></div>`;yhcMount(pg.querySelector("#yhcRoot"));}};   /* TK_V1.0.97 */
PAGES[59]={render(pg){pg.innerHTML=`<div class="pg" style="overflow:auto;padding:14px;max-width:1000px"><div id="ruRoot"></div></div>`;rulesMount(pg.querySelector("#ruRoot"));}};   /* V1.1.32 */
PAGES[61]={render(pg){pg.innerHTML=`<div class="pg" style="overflow:auto;padding:14px"><div id="gavRoot"></div></div>`;gavMount(pg.querySelector("#gavRoot"));}};   /* V1.1.77 禮物陣列影片 */
PAGES[60]={render(pg){pg.innerHTML=`<div class="pg" style="overflow:auto;padding:14px"><div id="pfxRoot"></div></div>`;pfxMount(pg.querySelector("#pfxRoot"));}};   /* V1.1.63 手機錄特效 */
PAGES[58]={render(pg){pg.innerHTML=`<div class="pg" style="overflow:auto;padding:14px;max-width:900px"><div id="mrgRoot"></div></div>`;mrgMount(pg.querySelector("#mrgRoot"));}};   /* V1.1.25 */
PAGES[57]={render(pg){pg.innerHTML=`<div class="pg" style="overflow:auto;padding:14px;max-width:900px"><div id="migRoot"></div></div>`;migMount(pg.querySelector("#migRoot"));}};   /* V1.1.07 */
PAGES[55]={render(pg){pg.innerHTML=`<div class="pg" style="overflow:auto;padding:14px;max-width:900px"><div id="gsdRoot"></div></div>`;gsdMount(pg.querySelector("#gsdRoot"));}};   /* TK_V1.0.84 */
PAGES[53]={render(pg){pg.innerHTML=`<div class="pg" style="overflow:auto;padding:14px;max-width:820px"><div id="hpRoot"></div></div>`;hpMount(pg.querySelector("#hpRoot"));}};   /* TK_V1.0.69 */
PAGES[49]={render(pg){pg.innerHTML=`<div class="pg" style="overflow:auto;padding:14px;max-width:820px"><div id="dhhRoot"></div></div>`;dhhMount(pg.querySelector("#dhhRoot"));}};   /* TK_V1.0.40 */
PAGES[48]={render(pg){pg.innerHTML=`<div class="pg" style="overflow:auto;padding:14px;max-width:900px"><div id="hvRoot"></div></div>`;hevcMount(pg.querySelector("#hvRoot"));}};   /* TK_V1.0.34 */
PAGES[47]={render(pg){pg.innerHTML=`<div class="pg" style="overflow:auto;padding:14px;max-width:760px"><div id="sbkRoot"></div></div>`;sbkMount(pg.querySelector("#sbkRoot"));}};
PAGES[45]={render(pg){pg.innerHTML=`<div class="pg" style="overflow:auto"><div id="phrRoot"></div></div>`;phrMount(pg.querySelector("#phrRoot"));}};   /* TK_V0.9.78 手機錄屏 */
PAGES[34]={render(pg){pg.innerHTML=`<div class="pg"><div id="ytRoot"></div></div>`;ytMount(pg.querySelector("#ytRoot"));}};   /* V0.7.42.005 YouTube 上傳 */
PAGES[33]={render(pg){pg.innerHTML=`<div class="pg"><div id="hlRoot"></div></div>`;hlMount(pg.querySelector("#hlRoot"));}};   /* V0.7.42.002 ✨ 精選 */
PAGES[31]={render(pg,arg){if(typeof lvsMount==="function"){if(arg){try{const f=lvsF();f.q=String(arg);lvsFSet(f);}catch(e){}}setTimeout(()=>go(42),0);return;}   /* TK_V0.9.17 檔案總管＝連續分級（舊的清單頁不用了；從主播選單來＝搜尋這位） */
  try{if(arg){VG.q=arg;VG.qFrom=arg;}else if(VG.qFrom&&VG.q===VG.qFrom){VG.q="";VG.qFrom="";}}catch(e){}   /* TK_V0.8.34.010 從主播選單來＝只看這位 */
pg.innerHTML=`<div class="pg fill"><div class="row"><h1 class="title">檔案總管</h1><span class="grow"></span><span class="sub">每幾秒一張圖排滿畫面，看一眼就知道這場值不值得留；點圖片選起來 → 初剪（免轉檔、永久保留）</span></div><div id="vgRoot" style="flex:1;min-height:0;margin-top:6px"></div></div>`;vgMount($("#vgRoot"));},
  leave(){VG.gen++;try{vgStopLoads();}catch(e){}try{VG.obs&&VG.obs.disconnect();}catch(e){}clearTimeout(VG.jt);clearTimeout(VG.preT);clearTimeout(VG.scT2);}};   /* V0.6.98 */
PAGES[32]={render(pg){pg.innerHTML=`<div class="pg fill"><div class="row"><h1 class="title">批量截 20 張</h1><span class="grow"></span><span class="sub">歷史場次先把 20 張圖截好（不用等刪 MP4）；新的場次下播後自動截</span></div><div id="shpRoot" style="flex:1;min-height:0;overflow:auto;max-width:900px;margin-top:6px"></div></div>`;shpMount($("#shpRoot"));},leave(){clearTimeout(SHP.iv);}};   /* V0.7.06 */
PAGES[30]={render(pg){pg.innerHTML=`<div class="pg fill"><div id="bgsRoot" style="flex:1;min-height:0;overflow:auto;max-width:980px"></div></div>`;bgsMount($("#bgsRoot"));}};   /* V0.6.92 後台狀態 */
PAGES[29]={render(pg,arg){pg.innerHTML=`<div class="pg fill"><div class="row"><h1 class="title">整理 MP4</h1><span class="grow"></span><span class="sub">只刪 MP4；刪之前先截 60 張圖，留言、禮物、錄音、剪輯成品全部留著</span></div><div id="lwRoot" style="flex:1;min-height:0;overflow:auto;max-width:980px;margin-top:6px"></div></div>`;lwOrgMount($("#lwRoot"),arg);}};   /* V0.6.94 等級整理＋刪除已剪輯 合成一頁 */
PAGES[26]={render(pg){pg.innerHTML=`<div class="pg fill"><div class="row"><h1 class="title">影片快速瀏覽</h1><span class="grow"></span><span class="sub">像 PotPlayer 一部接一部看，下一部先載好；刪除只刪 MP4（紀錄、M4A 保留）</span></div><div id="vbRoot" style="flex:1;display:flex;flex-direction:column;min-height:0;margin-top:8px"></div></div>`;vbMount($("#vbRoot"));},
  leave(){try{vbStopAll();}catch(e){}}};


boot();</script></body></html>'''


# V1.1.82 手機頁和網頁版一模一樣的程式（審核、剪輯器、檔案總管、禮物陣列、規則…）不再存兩份：網頁版這裡只留 @@SH數字@@，
# 送出時從手機頁（app.py 的 WEB_DASHBOARD_HTML）照「第一行～最後一行」整段拿過來 → 改一次兩邊都生效。找不到 → 那段換成 console.error（頁面照開，不讓主程式出錯）。
SH = [
[
"/* GFX-CSS-BEGIN */",
"/* GFX-CSS-END */"
],
[
"/* CG-CSS-BEGIN */",
"/* CG-CSS-END */"
],
[
"/* UA-CSS-BEGIN */",
"/* UA-CSS-END */"
],
[
"/* STT-CSS-BEGIN */",
"/* STT-CSS-END */"
],
[
"/* SA-CSS-BEGIN */",
"/* SA-CSS-END */"
],
[
"/* VB-CSS-BEGIN */",
"/* VB-CSS-END */"
],
[
"/* SN-CSS-BEGIN */",
"/* SN-CSS-END */"
],
[
"/* SP-CSS-BEGIN */",
"/* SP-CSS-END */"
],
[
"/* KIT-CSS-BEGIN */",
"/* KIT-CSS-END */"
],
[
"/* ED-CSS-BEGIN */",
"/* ED-CSS-END */"
],
[
"/* LW-CSS-BEGIN */",
"/* LW-CSS-END */"
],
[
"/* BG-CSS-BEGIN */",
"/* BG-CSS-END */"
],
[
"/* VG-CSS-BEGIN */",
"/* VG-CSS-END */"
],
[
"/* HL-CSS-BEGIN */",
"/* HL-CSS-END */"
],
[
"/* YT-CSS-BEGIN */",
"/* YT-CSS-END */"
],
[
"/* PF2-CSS-BEGIN */",
"/* PF2-CSS-END */"
],
[
"/* WKR-CSS-BEGIN */",
"/* WKR-CSS-END */"
],
[
"/* CHV-CSS-BEGIN */",
"/* CHV-CSS-END */"
],
[
"/* EMG-CSS-BEGIN */",
"/* EMG-CSS-END */"
],
[
"/* RV-CSS-BEGIN */",
"/* RV-CSS-END */"
],
[
"/* CUL-CSS-BEGIN */",
"/* CUL-CSS-END */"
],
[
"/* HTB-CSS-BEGIN */",
"/* HTB-CSS-END */"
],
[
".tkdSrc{display:flex;gap:6px;margin-bottom:8px}.tkdSrc button{flex:1;padding:9px;border-radius:10px;border:1px solid var(--border,#2b313c);background:var(--panel,#1b1f27);color:inherit;font-size:14.5px;font-weight:700}.tkdSrc button.on{background:#2a6b45;border-color:#45d483;color:#fff}",
"/* TKD-CSS-END */"
],
[
".gsdX{grid-template-columns:repeat(auto-fill,minmax(210px,1fr))}.gsdT{display:flex;flex-direction:column;gap:2px;font-size:12.5px}.gsdH,.gsdR{display:grid;grid-template-columns:46px 1.2fr .8fr 1.6fr;gap:8px;align-items:center;padding:5px 2px;border-bottom:1px solid var(--line,#2b313c)}.gsdH{opacity:.6;font-size:11.5px}",
"@media (max-width:560px){.gsdH,.gsdR{grid-template-columns:40px 1fr .7fr;}.gsdH span:nth-child(4){display:none}.gsdR span:nth-child(4){grid-column:1/-1}}"
],
[
".lvsTop{display:flex;align-items:center;gap:8px;flex-wrap:wrap;padding:4px 2px 6px}",
".lvsB,.lvsBox{overscroll-behavior:contain}"
],
[
"/* OLD-CSS-BEGIN */",
"/* OLD-CSS-END */"
],
[
"/* PHR-CSS-BEGIN */",
"/* PHR-CSS-END */"
],
[
"/* PUP-CSS-BEGIN */",
".rvT[data-s]{-webkit-touch-callout:none;-webkit-user-select:none;user-select:none}.rvT.rvPlay{outline:3px solid #4dc9ff;outline-offset:-3px}   /* TK_V1.0.87 */"
],
[
".rvGset{border:1px solid var(--border,#3a414d);background:transparent;color:inherit;border-radius:9px;padding:5px 10px;font-weight:700;margin-right:6px;white-space:nowrap}",
"/* PUP-CSS-END */"
],
[
"window.FASTP=(async function fastInit(){try{if(location.protocol!==\"http:\")return;const b=typeof B===\"string\"?B:\"\";const r=await fetch(b+\"/api/pc/fastimg\",{cache:\"no-store\"});if(!r.ok)return;const j=await r.json();if(!j||!j.ok||!j.on||!j.port||!j.key)return;",
"  if((e.key===\"k\"||e.key===\"K\")&&(e.ctrlKey||e.metaKey)){e.preventDefault();qsOpen();}else if(e.key===\"/\"&&!ed&&!e.ctrlKey&&!e.altKey){e.preventDefault();qsOpen();}});"
],
[
"/* V0.6.05 每場直播小圖表：灰色虛線＝已開播但還沒監控（推算），藍線＝監控到的人流，紅點＝前 N 名高價禮物 */",
"  if(d.m0>0){const mx=X(d.m0),t=hcClock(d.t0+d.m0)+\" 監控\",tw=x.measureText(t).width;if(mx-tw/2>x.measureText(\"00:00 開播\").width+pl+8&&mx+tw/2<W-40){x.textAlign=\"center\";x.fillStyle=lc;x.fillText(t,mx,yb);}}}"
],
[
"/* V0.6.17 FLV → MP4 轉檔排隊：手機版與電腦網頁版共用同一段顯示（資料都來自 /api/perf 的 merge） */",
"    finally{window.__mqBusy=0;}});})();"
],
[
"/* V0.6.28 LOG 與問題：自我檢查、網路狀態＋手動處理按鈕、自動處理紀錄、觀察到的異常（手機與電腦網頁版共用） */",
"  (typeof toast===\"function\"?toast:alert)(msg);if(typeof issuesRefresh===\"function\")issuesRefresh();});"
],
[
"/* V0.6.40 資料庫位置（手機與電腦網頁版共用） */",
"  (typeof toast===\"function\"?toast:alert)(j&&j.ok?\"💾 \"+(j.message||\"重新啟動中\"):\"✖ \"+((j&&j.message)||\"沒有成功\"));});"
],
[
"/* GFX-BEGIN */",
"/* GFX-END */"
],
[
"/* CG-BEGIN */",
"/* CG-END */"
],
[
"/* UA-BEGIN */",
"/* UA-END */"
],
[
"/* STT-BEGIN */",
"/* STT-END */"
],
[
"/* SA-BEGIN */",
"/* SA-END */"
],
[
"/* NV-BEGIN */",
"/* NV-END */"
],
[
"/* VB-BEGIN */",
"/* VB-END */"
],
[
"/* SP-BEGIN */",
"/* SP-END */"
],
[
"/* ED-BEGIN */",
"/* ED-END */"
],
[
"/* HT-BEGIN */",
"/* HT-END */"
],
[
"/* HA-BEGIN */",
"/* HA-END */"
],
[
"/* LW-BEGIN */",
"/* LW-END */"
],
[
"/* BG-BEGIN */",
"/* BG-END */"
],
[
"/* VG-BEGIN */",
"/* VG-END */"
],
[
"/* SH-BEGIN */",
"/* SH-END */"
],
[
"/* HL-BEGIN */",
"/* HL-END */"
],
[
"/* YT-BEGIN */",
"${(H.low||[]).length?`<div class=\"ytHoldD ytLow\">⚠ ${H.low.map(ytE).join(\"、\")}：確認沒問題就刪除暫放，空間才會回來</div>`:\"\"}<div class=\"ytHoldD\">YouTube 上都已經處理好、20 張圖也截好了。到 YouTube Studio 確認沒問題 → 按「刪除暫放資料夾」；想反悔 → 「全部放回原位」。</div>"
],
[
"/* TK_V0.9.41 退回分類先等 3 秒（可以反悔），時間到才真的從排隊拿掉 */",
"/* YT-END */"
],
[
"/* PF2-BEGIN */",
"/* PF2-END */"
],
[
"/* SOON-BEGIN */",
"/* SOON-END */"
],
[
"/* WKR-BEGIN */",
"/* WKR-END */"
],
[
"/* CHV-BEGIN */",
"/* CHV-END */"
],
[
"/* EMG-BEGIN */",
"/* EMG-END */"
],
[
"/* LEND-BEGIN */",
"/* LEND-END */"
],
[
"/* RV-BEGIN */",
"<div class=\"rvT2 rvGs\">${RVGK.map(k=>`<button type=\"button\" class=\"rvG${x.g===k?\" on\":\"\"}\" data-rg=\"${k}\" style=\"--gc:${RVG[k][2]}\"><b>${k}</b><small>${RVG[k][1]}</small></button>`).join(\"\")}<button type=\"button\" class=\"rvG${!x.g?\" on\":\"\"}\" data-rg=\"\" style=\"--gc:#9aa5b3\"><b>—</b><small>未分類</small></button>"
],
[
"async function rvOpen(u){const R=RV.root;if(!R)return;const b0=R.querySelector(\".rvBody\");if(b0&&!RV.u&&!R.querySelector(\".rvTl\"))RV.sy=b0.scrollTop;",
"  const r=await rvPost(\"/api/pc/rv/purge\",{});rvToast((r&&r.ok===false?\"✖ \":\"✔ \")+((r&&r.message)||\"\"));rvList();}"
],
[
"  const fx=t.closest(\"[data-fx]\");if(fx&&RV.u){e.stopPropagation();rvToFx(RV.u,+fx.dataset.fx);return;}",
"/* RV-END */"
],
[
"/* EXP-BEGIN */",
"/* EXP-END */"
],
[
"/* CUL-BEGIN */",
"/* CUL-END */"
],
[
"/* HTB-BEGIN */",
"/* HTB-END */"
],
[
"/* TKD-BEGIN */",
"/* TKD-END */"
],
[
"/* LVS-BEGIN */",
"function lvsF(){let f={};try{f=JSON.parse(localStorage.getItem(\"lvs_f\")||\"{}\")||{};}catch(e){}return {q:f.q||\"\",o:f.o||\"new\",cat:f.cat==null?\"*\":f.cat,g:Array.isArray(f.g)?f.g:[],pv:!!f.pv,lvf:f.lvf||\"\"};}"
],
[
"  if($r(\"#lvsDef\"))root.querySelector(\"#lvsDef\").onchange=e=>{try{localStorage.setItem(\"lvsDef\",e.target.checked?\"1\":\"0\");}catch(x){}lvsToast(e.target.checked?\"✔ 以後按「檔案總管」直接開連續分級\":\"以後按「檔案總管」開一般清單\");};",
"  const qs=/^#\\d+$/.test(q)?q.replace(/^#0*/,\"\"):\"\";   /* TK_V0.9.37 搜「#場次」＝只找那一場，不管其他篩選（標過等級的也找得到） */"
],
[
"    &&(F.cat===\"*\"||(r.cat||\"\")===F.cat)&&(!F.g.length||LVS.kind===\"nv\"||F.g.includes(r.g||\"-\"))&&(!F.pv||LVS.kind===\"nv\"||(r.prx!=null?r.prx>=80:r.pr!=null?r.pr>=80:(r.pv===1||r.s2===1))));   /* TK_V0.9.41 打開過的場次用實際拿到的預覽圖（prx）判斷 */   /* TK_V0.8.96 預覽圖實際有八成以上（照真的拿得到的圖算） */",
"  if(LVS.pc){const sc=LVS.strip,top=it.offsetTop-sc.offsetTop;if(top<sc.scrollTop||top+it.offsetHeight>sc.scrollTop+sc.clientHeight)sc.scrollTo({top:top-sc.clientHeight/2+it.offsetHeight/2,behavior:\"smooth\"});if(typeof lvpCur===\"function\")lvpCur(i);return;}"
],
[
"  LVS.strip.scrollTo({left:it.offsetLeft-(LVS.strip.clientWidth-it.offsetWidth)/2,behavior:\"smooth\"});lvsCurPaint(i);}",
"  if(nmiss>0&&nmiss>s._tiles.length*0.3)s.querySelector(\".lvsH\").insertAdjacentHTML(\"afterend\",`<div class=\"lvsWait\">⏳ 這場預覽圖還沒做完（${s._tiles.length-nmiss}/${s._tiles.length}），已排到背景最前面，做好會自動補上</div>`);"
],
[
"/* TK_V0.9.41 打開才發現預覽圖沒好的場次：從清單拿掉（停在原本那一場；如果正在看的就是它，換到下一場） */",
"  ov.onclick=e=>{const it=e.target.closest(\".lvsLI\");ov.remove();if(it)lvsJump(+it.dataset.i);};}"
],
[
"/* 改秒數／一列幾張：已經排好的場次重排（保留捲動位置在同一場） */",
"/* LVS-END */"
],
[
"/* CLP-BEGIN */",
"/* GFS-END */"
],
[
"/* OLD-BEGIN */",
"/* OLD-END */"
],
[
"/* PHR-BEGIN */",
"/* PHR-END */"
],
[
"/* PUP-BEGIN */",
"/* PUP-END */"
]
]
_SH_C = {}


def _sh_html(G):
    src = G.get('WEB_DASHBOARD_HTML', '') or ''
    k = (id(src), len(src))
    if k in _SH_C: return _SH_C[k]
    def one(m):
        i = int(m.group(1))
        try:
            f, l = SH[i]; a = src.find('\n' + f + '\n')
            if a < 0: raise ValueError('first')
            a += 1; b = src.find('\n' + l + '\n', a)
            if b < 0 and src.endswith('\n' + l): b = len(src) - len(l) - 1
            if b < 0: raise ValueError('last')
            return src[a:b + 1 + len(l)]
        except Exception as e:
            return f'/* SH{i} missing: {e} */'
    out = re.sub(r'@@SH(\d+)@@', one, HTML)
    _SH_C.clear(); _SH_C[k] = out
    return out


def sh_check(G):
    """打包前檢查：每一段都找得到（找不到回傳清單）."""
    return [i for i in range(len(SH)) if f'SH{i} missing' in _sh_html(G)]
