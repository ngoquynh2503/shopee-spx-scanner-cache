import streamlit as st
import requests
import time
from datetime import datetime
from typing import Optional, Dict, List
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import threading

# ==================== CẤU HÌNH HỆ THỐNG ====================
API_ALL_LIST  = "https://spx.shopee.vn/api/in-station/cache_order_task/all_list"
API_DETAIL    = "https://spx.shopee.vn/api/in-station/cache_order_task/detail"
API_ORDER_ADD = "https://spx.shopee.vn/api/in-station/cache_order_task/order/add"

COOKIE_SPREADSHEET_ID = "1O1rDK916nKZnWrJJNbruUsGZ8msxqafxYkhxR0871TM"
LOG_SPREADSHEET_ID    = "1G8V-lbw4mfe_bGdMnKpvOYlRXX_E9OlSH9brWypwf94"

status_mapping = {1: "Packing", 2: "Packed", 3: "Đã hủy (Cancelled)"}

GOOGLE_CREDS_DICT = {
    "type": "service_account",
    "project_id": "shopeeapiver2",
    "private_key_id": "2d1b681ee0bd44363ac6a48053ffd1f4b22b0abb",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDNkU2Tj3T1IGJT\ng69OEwrv1jQ/WlzrL6Zc2e4T+F+sW+dzzZhtt3/FOLctZQJP4GEGRhBvDOcCMsI8\nQdoIM6TK9y+BbXyxn6kvDGEB7PQtJ3tBSgoA7eqtW/osg0a2I43EKtL68f8YVzwY\n2aFLL0IkIa0iR2oGmaU16Acdeq54iSAjkXgyqPPHRSnhAZnvSHX3GKDxsWdkksK3\neRLnPwAIse6GN/cwPICFhJlon9UOdq+EJJd/rOALL95AVVivdj4eTlze0RfQaVPO\nni+fIWLiFDTriPSfngUK08ff2wsP4Pvx2btnQdTxzbF1Uga36V6K8ILmXTJQ8DgN\nhATpVbT/AgMBAAECggEAA33z+B+YKplC8lY9C2igQssFKQyiD7wjVzFOP+YGXXcK\nxsb3vTH3Oq26ZJUpHHccTtOwcBA1nhvMoSv8oXh3HcCtfKCmgcHwJISaULB8xM8G\ndWlTkVHnCjoAwvI+OtYi6/G8kulNMMNgUK/AmBsUsh+TLzO+gTHpi40GMw+SBk5p\noDkBmii1GCxwjW2K1npR2DECbdPlKEEK1f0Pr8EmpO8LoK5JYCFtNTSKhg+VA5lh\ncDQclMxdQ9ilk5UFRKQE77hO4/JwNMyqNNqrbPIBqHSKsW1QDWTxTrl4NVu1dB74\nX4ZapkSe5hDskMxf7S5L3Q91gC6xYfGVVdl8RATf6QKBgQD6iP3216SdcGk6BKGA\ngBBRapffJ26Qi2uXRrZSVgIkDWKtlWFgwKUlRP3xn7mLHeDCq4J4mvT/Wj7jgl3o\nINmbJPebiVzYkLqWMgYrt4wRXOLgS8jkUlbT9xA028/3So716RS3WQEExwKk1M3W\nLl6AmZHsodsZuQvVmUh4Fo31PQKBgQDSDTVuKn30kn2OZHvlIfPnqKf39tzPhXAs\nroJw4fzPBPC2tIucas7LjWMTVCBZsu8as66WY7qW9dCwcszE5SvUFDg6hkJg3YYJ\nxSBYFtIdzoicmwS9yMuUffyEzGoW/xJgyJPl2ti0vmVlx6/xgHUcLWDB6L8ZmMEK\nHpF1jFFO6wKBgQCd7IKh+ZaTg4tg/hBLru4aVCW9jd6dELVWW0WMKxkYXrOoFbSX\nR3gSQSYODA/qSIAoVfJdUdhDqkBgKwpEy4g/ypKmIXU8MibbjFblccLCIxoEJuFQ\nQzLmVCOMHk8+Y2owSqc7V8hTmZrqChZh/0Kkr6kTT4eL9GAoWYIb6KO9RQKBgQCt\nIQf1+n4AlLF6KOZZcIe5XDC917IeNazElz2aTxnxg+/nl54u2XYDHlEYAFH9vNcJ\nGip/eEm13XwZwzV14DIkxlmmGz0g29V7vgevs3eR68Z71eWti5AIn2MADgAvXiPG\ns+v7G0tchkXLAzDIjAl6pQhIK08/iMErVxCrY3Es6wKBgQDqK/Z2V26/55Ou/c9p\nVZvFQ9mmRVoRffeBgNMKyGShZMa+zDuZt1orqMr6p9uACX7laSPa6tNzUJ6NH0Hm\n3dgcVS2eRzK0A17knAXb8u9jm7IpKejA2CoxTVMNJ++QIBdWUUtBkE5PcoZK/LYU\nWEq8jpIfdkbAllrfOy5dSK5IWg==\n-----END PRIVATE KEY-----\n",
    "client_email": "huypham@shopeeapiver2.iam.gserviceaccount.com",
    "client_id": "114566912904828944092",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/huypham%40shopeeapiver2.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

if "http_session" not in st.session_state:
    st.session_state.http_session = requests.Session()

if "history" not in st.session_state:
    st.session_state.history = []
if "scan_error" not in st.session_state:
    st.session_state.scan_error = None
if "cached_cookie" not in st.session_state:
    st.session_state.cached_cookie = None
if "active_task_id" not in st.session_state:
    st.session_state.active_task_id = None

# ==================== GOOGLE SHEETS FUNCTIONS ====================
def fetch_cookie_from_sheet() -> Optional[str]:
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
        creds = Credentials.from_service_account_info(GOOGLE_CREDS_DICT, scopes=scopes)
        service = build("sheets", "v4", credentials=creds)
        result = service.spreadsheets().values().get(
            spreadsheetId=COOKIE_SPREADSHEET_ID,
            range="'Cookie'!C2:C2"
        ).execute()
        rows = result.get("values", [])
        if rows and rows[0]:
            return rows[0][0].strip()
        return None
    except Exception as e:
        st.error(f"Lỗi Cookie Sheet: {e}")
        return None

def get_or_refresh_cookie() -> Optional[str]:
    if not st.session_state.cached_cookie:
        with st.spinner("Đang tải Cookie..."):
            cookie = fetch_cookie_from_sheet()
            if cookie:
                st.session_state.cached_cookie = cookie
    return st.session_state.cached_cookie

def _async_append_sheet(row_data: List):
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_info(GOOGLE_CREDS_DICT, scopes=scopes)
        service = build("sheets", "v4", credentials=creds)
        body = {"values": [row_data]}
        service.spreadsheets().values().append(
            spreadsheetId=LOG_SPREADSHEET_ID,
            range="LOG_CO!A:G",
            valueInputOption="USER_ENTERED",
            body=body
        ).execute()
    except Exception:
        pass

def append_to_google_sheet_async(row_data: List):
    threading.Thread(target=_async_append_sheet, args=(row_data,), daemon=True).start()

# ==================== SCAN & PARSER UTILS ====================
def extract_latest_scan_code(raw: str) -> str:
    raw = raw.strip()
    if not raw: return ""
    
    for prefix in ["SPXVN", "CO", "SPX"]:
        if prefix in raw:
            positions = []
            start = 0
            while True:
                idx = raw.find(prefix, start)
                if idx == -1: break
                positions.append(idx)
                start = idx + 1
            if positions:
                return raw[positions[-1]:]
                
    half = len(raw) // 2
    if len(raw) % 2 == 0 and raw[:half] == raw[half:]:
        return raw[half:]
        
    return raw

def build_headers(cookie: str) -> dict:
    return {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Cookie": cookie,
    }

# ==================== SHOPEE API CALLS ====================
def lookup_task(task_id: str, cookie: str) -> Dict:
    hdrs = build_headers(cookie)
    payload = {"cache_order_task": task_id.strip(), "pageno": 1, "count": 24}
    
    try:
        resp = st.session_state.http_session.post(API_ALL_LIST, json=payload, headers=hdrs, timeout=5)
        if resp.status_code == 401: 
            st.session_state.cached_cookie = None
            return {"_error": "Cookie hết hạn (401)"}
            
        if resp.status_code != 200: return {"_error": f"Lỗi HTTP {resp.status_code}"}
        
        res = resp.json()
        if res.get("retcode") != 0: return {"_error": res.get("message", "Lỗi Shopee API")}
        
        items = res.get("data", {}).get("list", [])
        raw_data = {}
        for item in items:
            if str(item.get("cache_order_task", "")).strip() == task_id.strip():
                raw_data = item
                break
        if not raw_data and items: raw_data = items[0]
        if not raw_data: return {"_error": f"Không tìm thấy Task [{task_id}]"}

        raw_status = raw_data.get("status", "")
        try: status_code = int(raw_status)
        except: status_code = None
        status_str = status_mapping.get(status_code, str(raw_status) if raw_status != "" else "—")

        params = {"cache_order_task": task_id.strip(), "pageno": 1, "count": 250}
        resp_detail = st.session_state.http_session.get(API_DETAIL, params=params, headers=hdrs, timeout=5)
        sub_orders = []
        if resp_detail.status_code == 200 and resp_detail.json().get("retcode") == 0:
            orders = resp_detail.json().get("data", {}).get("list", [])
            sub_orders = [o for o in orders if str(o.get("order_remark", "")).strip() == ""]

        return {
            "cache_order_task": str(raw_data.get("cache_order_task", task_id)),
            "status": status_str,
            "packed_order_quantity": str(raw_data.get("packed_order_quantity", "0")),
            "fulfilled_order_quantity": str(raw_data.get("fulfilled_order_quantity", "0")),
            "rts_order_quantity": str(raw_data.get("rts_order_quantity", "0")),
            "create_time_str": str(raw_data.get("create_time_str", "—")),
            "sub_orders": sub_orders 
        }
    except Exception as e:
        return {"_error": f"Lỗi kết nối: {e}"}

def add_order_to_task(task_id: str, fleet_order_id: str, cookie: str) -> dict:
    hdrs = build_headers(cookie)
    payload = {
        "cache_order_task": task_id.strip(),
        "fleet_order_id": fleet_order_id.strip(),
        "force_abnormal_from_other_container": True,
        "auto_print_enabled": False
    }
    try:
        resp = st.session_state.http_session.post(API_ORDER_ADD, json=payload, headers=hdrs, timeout=5)
        if resp.status_code == 401:
            st.session_state.cached_cookie = None
        return resp.json()
    except Exception as e:
        return {"retcode": -1, "message": f"Lỗi: {e}"}

# ==================== GIAO DIỆN WEB MOBILE TỐI ƯU ====================
st.set_page_config(page_title="SPX Mobile Scanner", layout="centered")

# Ẩn các thành phần thừa, tối ưu CSS hiển thị trên Mobile
st.markdown(
    """
    <style>
    /* 1. Ẩn menu 3 chấm, nút Deploy mặc định và Header */
    #MainMenu {visibility: hidden !important; display: none !important;}
    footer {visibility: hidden !important; display: none !important;}
    .stDeployButton {display: none !important;}
    header {display: none !important; visibility: hidden !important;}
    
    /* 2. Ẩn nút tròn quản lý trạng thái/kết nối Cloud ở góc phải */
    div[data-testid="stStatusWidget"] {display: none !important; visibility: hidden !important;}
    button[title="View app source"] {display: none !important;}
    
    /* 3. BẮT CHÍNH XÁC VÀ TRIỆT TIÊU PROFILE CONTAINER & VIEWER BADGE TRÊN CHROME */
    [class*="_profileContainer_"],
    [class*="_container_gzau3_"],
    [class*="_viewerBadge_"],
    [class*="viewerBadge"],
    div[class^="_profileContainer_"],
    div[class^="_viewerBadge_"] {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        height: 0 !important;
        width: 0 !important;
        position: absolute !important;
        left: -9999px !important; /* Đẩy hẳn ra khỏi màn hình hiển thị */
    }
    
    /* 4. Xóa bỏ hoàn toàn thanh toolbar bọc ngoài ở cạnh dưới cùng */
    .stAppToolbar {display: none !important; visibility: hidden !important; height: 0 !important;}
    iframe[title="Manage app"] {display: none !important; visibility: hidden !important;}
    
    /* Tối ưu khoảng cách phía trên */
    .block-container {
        padding-top: 2rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🛵 SPX Mobile Scanner")

cookie_value = get_or_refresh_cookie()
if not cookie_value:
    st.error("❌ Lỗi lấy Cookie từ Google Sheet.")
    st.stop()

# ĐỊNH NGHĨA POPUP CHI TIẾT ĐƠN HÀNG (FULL MÀN HÌNH MOBILE)
@st.dialog("📦 CHI TIẾT TASK & ĐƠN CON", width="large")
def show_task_detail_popup(task_id: str):
    # Tìm thông tin task hiện tại từ history
    task = next((h for h in st.session_state.history if h['cache_order_task'] == task_id), None)
    if not task:
        st.error("Không tìm thấy dữ liệu Task.")
        return

    # Khối thông số dạng cột dọc siêu gọn trên mobile
    st.markdown(f"**Mã Task:** `{task['cache_order_task']}`")
    st.markdown(f"**Trạng thái:** `{task['status']}`")
    
    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("Packed", task['packed_order_quantity'])
    m_col2.metric("Fulfilled", task['fulfilled_order_quantity'])
    m_col3.metric("RTS", task['rts_order_quantity'])
    
    st.caption(f"Thời gian: {task['create_time_str']}")
    st.markdown("---")
    
    # Form thêm nhanh đơn hàng con ngay trong popup
    st.markdown("### ➕ Thêm đơn con")
    with st.form(key=f"popup_add_order_{task['cache_order_task']}", clear_on_submit=True):
        fleet_id_input = st.text_input("Nhập/Quét Fleet Order ID:", placeholder="Quét mã đơn...")
        submit_btn = st.form_submit_button("Thêm Đơn", use_container_width=True)
        
        if submit_btn and fleet_id_input:
            fleet_id = extract_latest_scan_code(fleet_id_input.strip())
            with st.spinner("Đang thêm đơn..."):
                res_api = add_order_to_task(task['cache_order_task'], fleet_id, cookie_value)
            if res_api.get("retcode") == 0:
                st.success(f"✅ Đã thêm: {fleet_id}")
                # Cập nhật lại dữ liệu danh sách con ngay tại chỗ
                updated_result = lookup_task(task['cache_order_task'], cookie_value)
                if "_error" not in updated_result:
                    for idx, h in enumerate(st.session_state.history):
                        if h['cache_order_task'] == task['cache_order_task']:
                            st.session_state.history[idx] = updated_result
                            break
                    time.sleep(0.5)
                    st.rerun()
            else:
                st.error(f"❌ Lỗi: {res_api.get('message')}")
                
    st.markdown(f"### 📄 Đơn con ({len(task['sub_orders'])})")
    if task['sub_orders']:
        table_data = []
        for o_idx, o in enumerate(task['sub_orders'], 1):
            stime = o.get("scan_time", 0)
            stime_str = datetime.fromtimestamp(stime).strftime('%H:%M:%S') if stime else "—"
            table_data.append({
                "STT": o_idx,
                "Mã Đơn Hàng": o.get("fleet_order_id", "—"),
                "Giờ": stime_str
            })
        st.dataframe(table_data, use_container_width=True, hide_index=True)
    else:
        st.info("Chưa có đơn hàng con nào.")

# CALLBACK XỬ LÝ QUÉT MÃ MỚI VÀ KÍCH HOẠT POPUP LẬP TỨC
def handle_scan():
    raw_input = st.session_state.scan_input_field.strip()
    st.session_state.scan_input_field = ""  
    st.session_state.scan_error = None      
    
    if raw_input:
        sid = extract_latest_scan_code(raw_input)
        if sid:
            result = lookup_task(sid, cookie_value)
            if "_error" in result:
                st.session_state.scan_error = f"❌ LỖI TASK [{sid}]: {result['_error']}"
                st.session_state.active_task_id = None
            else:
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                row_log = [
                    now_str,
                    result["cache_order_task"],
                    result["status"],
                    result["packed_order_quantity"],
                    result["fulfilled_order_quantity"],
                    result["rts_order_quantity"]
                ]
                append_to_google_sheet_async(row_log)
                
                # Cập nhật history
                st.session_state.history = [h for h in st.session_state.history if h['cache_order_task'] != result['cache_order_task']]
                st.session_state.history.insert(0, result)
                
                # Lưu Task ID vừa quét thành công để kích hoạt popup tự động
                st.session_state.active_task_id = result["cache_order_task"]

# --- KHU VỰC 1: SCAN MÃ TASK (Cố định ở vị trí trên cùng dễ thao tác) ---
st.text_input(
    "📷 Đặt con trỏ vào đây để quét mã:", 
    key="scan_input_field", 
    on_change=handle_scan,
    placeholder="Nhấn vào để quét tự động..."
)

if st.session_state.scan_error:
    st.error(st.session_state.scan_error)

# KÍCH HOẠT POPUP BẬT LÊN NGAY LẬP TỨC KHI ĐỔI TRẠNG THÁI ACTIVE_TASK_ID
if st.session_state.active_task_id:
    task_to_open = st.session_state.active_task_id
    st.session_state.active_task_id = None  # Xóa trạng thái chờ để tránh loop vô hạn
    show_task_detail_popup(task_to_open)

# --- KHU VỰC 2: DANH SÁCH RÚT GỌN LỊCH SỬ QUÉT (DÀNH CHO MOBILE) ---
st.subheader("📋 Lịch sử quét trong phiên")
if not st.session_state.history:
    st.info("Hệ thống sẵn sàng. Hãy quét mã vạch.")
else:
    # Hiển thị list dạng thẻ (Card) rút gọn tối giản trên mobile
    for h_task in st.session_state.history:
        with st.container(border=True):
            st.markdown(f"**Mã Task:** `{h_task['cache_order_task']}`")
            st.markdown(f"Trạng thái: **{h_task['status']}** | Đơn con: `{len(h_task['sub_orders'])}`")
            
            # Nút bấm mở lại Popup bất cứ lúc nào
            if st.button(f"🔎 Xem chi tiết & Thêm đơn", key=f"btn_open_{h_task['cache_order_task']}", use_container_width=True):
                show_task_detail_popup(h_task['cache_order_task'])
