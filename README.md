## 網頁攻擊與防禦1 說明

### 階段一：啟動網頁伺服器
注意此階段僅僅是在本地用各位的電腦架起網頁伺服器，其他在網際網路(或稱外網、WAN)上的人是存取不到的
在終端機輸入以下指令進入 app/ 目錄並啟動伺服器：
   ```bash
   cd app/
   python3 -m http.server 8080
   ```
### 階段二：攻擊方 Path traversal

原理：當我們執行 python3 -m http.server 時，底層是啟動一個基礎伺服器。其邏輯是「直接將 HTTP 請求的 URL 路徑，映射到本地實體檔案系統路徑」。

當瀏覽器發送 GET /admin_panel/flag.txt HTTP/1.1 的請求給伺服器時。伺服器會直接向 Linux 系統發出要求，請求開啟相對應路徑的檔案（例如呼叫 open("./admin_panel/secret_flag.txt")）。

### 階段三：防禦方 權限控管

當我們修改權限後， Linux 系統的核心(kernel)在接收到開啟檔案的要求後，會檢查該檔案的權限資訊，如果發現讀取權限被拔除，就不會允許該要求通過。

## 網頁攻擊與防禦2 說明

### 階段一：啟動服務以及測試
1. `cd`到`advanced_app/`再執行`python3 server.py` 啟動伺服器。
2. 在輸入框輸入本地端 IP `127.0.0.1` 並送出。
3. 網頁下方會回傳 Linux 系統中執行 `ping -c 3 127.0.0.1` 的正常結果。

原理：送出表單時，Python 網頁伺服器接收了 HTTP 請求，把 `ip` 參數萃取出來。伺服器內部的程式碼使用字串拼接：`command = "ping -c 3 " + ip_address`，然後呼叫作業系統的 Shell (直譯器，用來翻譯文字指令給電腦底層看的工具)去執行這串字串。最後，伺服器將 Shell 執行結果的文字結果包裝成 HTML 顯示在網頁上。

### 階段二：駭客
1. 嘗試在網頁輸入框中輸入：`127.0.0.1; ls -la`
2. 送出後，網頁除了顯示 ping 的結果，還印出了伺服器當前目錄的所有檔案清單
3. 已知機密檔案藏在上層目錄。在輸入框輸入：`127.0.0.1; cat ../secret/root_flag.txt`

原理：為什麼能注入指令？這個攻擊能成立，是因為在 Linux Shell 中，分號 `;` 是一個特殊的控制字元，代表「執行完前面的指令，接著執行後面的指令」。又因為 Python 程式碼中使用了 `shell=True` 這個危險設定，且沒有過濾特殊符號。當輸入 `127.0.0.1; ls -la` 時，伺服器拼接出的完整字串變成了 `ping -c 3 127.0.0.1; ls -la`。

### 階段三：防護與修補

#### 防禦實作一：
* **操作步驟**：
  1. 在終端機關閉伺服器 (`Ctrl + C`)。
  2. 更改機密檔案的讀取權限，只允許擁有者（root/admin）讀取：
     `chmod 700 ../secret/root_flag.txt`
  3. 重開伺服器後再次利用網頁攻擊。網頁會顯示 `Permission denied`。
* **原理（最小權限原則）**：
  網頁伺服器在作業系統中只是一個具有一般使用者權限的程式。當伺服器被駭客控制，試圖去讀取機密檔案時，Linux Kernel 會檢查檔案的權限設定。因為我們拔除了其他人的讀取權限，Linux 核心會直接在底層攔截並拒絕這個讀取行為。

#### 防禦實作二：程式碼修補
* **操作步驟**：
  打開 `server.py`，將原本危險的寫法改為安全的「陣列（List）」寫法，並移除 `shell=True`：
  ```python
  subprocess.check_output(["ping", "-c", "3", ip_address], text=True)


## Bash 自動化腳本實作範本
```bash
#!/bin/bash

# 變數設定
# 任務 1: 設定硬碟警告的 % 數上限為 80
DISK_LIMIT=____
TARGET_IP="8.8.8.8"

# 系統基本資訊
function check_system() {
    echo "=== 系統基本資訊 ==="
    uptime
    free -h
}

# 硬碟空間檢查與警報
function check_disk() {
    echo "=== 硬碟空間檢查 ==="
    # 自動抓出根目錄的使用率數字 (同學先不用背這行)
    USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
    echo "目前根目錄使用率: ${USAGE}%"

    # 任務 2: 判斷 USAGE 是否大於 DISK_LIMIT
    if [ $USAGE ____ $DISK_LIMIT ]; then
        echo "警告：硬碟空間即將不足！請盡速清理！"
    else
        echo "硬碟空間安全。"
    fi
}

# 絕招三：網路連線測試
function check_network() {
    echo "=== 網路連線測試 ==="
    echo "正在測試與外部網路 ($TARGET_IP) 的連線..."
    # 任務 3: 用 ping 發送 3 個測試封包給目標 IP
    ping ____ 3 $TARGET_IP
}

# 主程式：無限輪迴的互動選單
while true; do
    echo ""
    echo "--------------------------"
    echo " 歡迎來到系統管理員控制台 "
    echo " 1. 查看系統基本資訊"
    echo " 2. 檢查硬碟空間與警報"
    echo " 3. 測試網路連線"
    echo " 4. 離開系統"
    echo "--------------------------"
    
    # 任務 4: 讀取使用者的輸入，並將輸入的數字存入變數 choice
    ____ -p "請輸入選項 (1-4): " choice

    # 任務 5: 根據使用者輸入的 choice 變數，執行對應的絕招
    case ____ in
        1) check_system ;;
        2) check_disk ;;
        3) check_network ;;
        4) echo "登出系統，系統管理員辛苦了！"; exit 0 ;;
        *) echo "無效的選項，請重新輸入。" ;;
    esac
    sleep 1 # 暫停一秒，讓畫面看起來更順暢
done

```

### 腳本解答(有編碼過，能把它還原嗎？)
ODAgLWd0IC1jIHJlYWQgJGNob2ljZQ==
