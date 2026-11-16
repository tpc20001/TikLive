# TikLive Monitor

TikTok 直播監控／錄影程式。這個 repo 只放程式碼和雲端打包設定。

- 推上 `main`：GitHub Actions 在 Windows 上打包（PyInstaller），版本號讀 `app/app.py` 的 `APP_VERSION`。
- 該版本的 tag（`v版本`）還沒有時，自動發佈到 Releases：
  - `TK_V版本_Update.zip`：程式更新包（熱更新，不中斷錄影）
  - `TK_Shell_L啟動器版本.zip`：EXE 外殼（`TikLiveMonitor.exe` + `_internal`）
  - `TikLive_Full_V版本.zip`：完整安裝包
  - `update.json`：程式內「☁ 雲端更新」讀這個檔
- 程式內只「提示」有新版，一定要使用者按「更新」才會更新。
