import requests
import re
import json
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# ================= HTTP =================
session = requests.Session()
session.headers.update(HEADERS)

def fetch_json(url):
    try:
        r = session.get(url, timeout=15)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    return {}

# ================= STREAM CHECK =================
def is_working_m3u8(url):
    if ".m3u8" not in url: 
        return False
    try:
        r = session.head(url, timeout=3)  # HEAD nhanh hơn GET
        return r.status_code == 200
    except:
        return False

def is_valid_tv(url):
    if ".m3u8" not in url: 
        return False
    if any(x in url for x in ["udp://", "rtp://"]): 
        return False
    return True

# ================= PICK STREAM =================
def pick_stream(streams):
    m3u8_hd = None
    m3u8 = None
    for s in streams:
        name = s.get("name", "").upper()
        url = s.get("sourceUrl")
        if not url: continue
        
        if ".m3u8" in url:
            if "FHD" in name or "HD" in name:
                m3u8_hd = url
            else:
                m3u8 = url
    return m3u8_hd or m3u8

# ================= API STANDARD =================
def process_standard(url, group):
    out = []
    data = fetch_json(url)
    for item in data.get("data", []):
        dt = datetime.now()
        if item.get("startTime"):
            try:
                dt = datetime.strptime(item["startTime"][:19], "%Y-%m-%dT%H:%M:%S") + timedelta(hours=7)
            except:
                pass
                
        for c in item.get("fixtureCommentators", []):
            comm = c.get("commentator", {})
            stream = pick_stream(comm.get("streams", []))
            if not stream: 
                continue
                
            out.append({
                "time": dt,
                "group": group,
                "title": f'{dt.strftime("%H:%M")} | {item.get("title")}',
                "logo": item.get("homeTeam", {}).get("logoUrl", ""),
                "url": stream
            })
            break
    return out

# ================= VONG CAM =================
def process_vongcam():
    out = []
    data = fetch_json("https://sv.bugiotv.xyz/internal/api/matches")
    for item in data.get("data", []):
        url = item.get("commentator", {}).get("streamSourceFhd")
        if not url or ".m3u8" not in url: 
            continue
            
        out.append({
            "time": datetime.now(),
            "group": "VÒNG CẤM TV",
            "title": item.get("title"),
            "logo": item.get("homeClub", {}).get("logoUrl", ""),
            "url": url
        })
    return out

# ================= CA LA TV =================
def process_cala_tv():
    out = []
    data = fetch_json("https://api.cltvlv.com/api/matches")
    for key, item in data.get("data", {}).items():
        dt = datetime.fromtimestamp(item.get("matchTime", datetime.now().timestamp()))
        home = item.get("home_team", {})
        away = item.get("away_team", {})
        streams = item.get("anchorAppointmentVoList", [])
        stream_url = None
        
        for s in streams:
            if s.get("playStreamAddress2") and ".m3u8" in s["playStreamAddress2"]:
                stream_url = s["playStreamAddress2"]
                break
                
        if not stream_url: 
            continue
            
        out.append({
            "time": dt,
            "group": "CA LA TV",
            "title": f'{dt.strftime("%H:%M")} | {home.get("name")} vs {away.get("name")}',
            "logo": home.get("logo", ""),
            "url": stream_url
        })
    return out

# ================= LOAD EXTERNAL KEEP GROUP =================
def load_external_keep_group(url):
    out = []
    try:
        r = session.get(url, timeout=15)
        lines = r.text.splitlines()
        title = ""
        logo = ""
        group = "OTHER"
        for line in lines:
            if line.startswith("#EXTINF"):
                title = line.split(",")[-1].strip()
                m_logo = re.search(r'tvg-logo="([^"]+)"', line)
                logo = m_logo.group(1) if m_logo else ""
                m_group = re.search(r'group-title="([^"]+)"', line)
                group = m_group.group(1) if m_group else "OTHER"
            elif line.startswith("http"):
                out.append({
                    "time": datetime.now(),
                    "group": group,
                    "title": title,
                    "logo": logo,
                    "url": line.strip()
                })
    except Exception as e:
        print(f"Error loading external M3U: {e}")
    return out

# ================= LOAD FPT SPORT =================
def load_fpt_sport(url):
    out = []
    try:
        r = session.get(url, timeout=15)
        lines = r.text.splitlines()
        title = ""
        for line in lines:
            if line.startswith("#EXTINF"):
                title = line.split(",")[-1].strip()
            elif line.startswith("http"):
                out.append({
                    "time": datetime.now(),
                    "group": "FPT SPORT",
                    "title": title if title else "FPT SPORT",
                    "logo": "",
                    "url": line.strip()
                })
    except Exception as e:
        print(f"Error loading FPT Sport: {e}")
    return out

# ================= WRITE FILE (JSON + HTML) =================
def check_stream(url):
    if is_valid_tv(url):
        return url if is_working_m3u8(url) else None
    return None

def write_files(data):
    seen = set()
    full_items = []
    
    # Chuẩn bị dữ liệu mảng dictionary cho FULL
    for item in data:
        url = item["url"]
        if url in seen:
            continue
        seen.add(url)
        
        # Chuyển đổi datetime object về string để dump ra JSON
        time_str = item["time"].strftime("%Y-%m-%d %H:%M:%S") if isinstance(item["time"], datetime) else str(item["time"])
        
        full_items.append({
            "group": item["group"],
            "title": item["title"],
            "logo": item["logo"],
            "url": url,
            "time": time_str
        })

    tv_items = []

    # TV FILTER: kiểm tra stream song song bằng ThreadPoolExecutor
    print("Đang kiểm tra kết nối các luồng (Live check)...")
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(check_stream, item["url"]): item for item in full_items}
        for future in as_completed(futures):
            result = future.result()
            if result:
                tv_items.append(futures[future])

    # 1. Ghi ra file JSON
    with open("tv.json", "w", encoding="utf-8") as f:
        json.dump(tv_items, f, ensure_ascii=False, indent=4)
        
    with open("full.json", "w", encoding="utf-8") as f:
        json.dump(full_items, f, ensure_ascii=False, indent=4)

    # 2. Tạo code HTML thông báo thành công
    now = datetime.now() + timedelta(hours=7) # Giờ VN (GMT+7)
    time_updated = now.strftime("%d/%m/%Y - %H:%M:%S")
    tv_count = len(tv_items)
    full_count = len(full_items)

    html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trạng Thái Cập Nhật Dữ Liệu</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0f172a; color: #f8fafc; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
        .card {{ background: #1e293b; padding: 40px; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); text-align: center; max-width: 400px; width: 90%; border: 1px solid #334155; }}
        .icon {{ font-size: 60px; margin-bottom: 15px; display: inline-block; animation: pop 0.5s ease-out; }}
        h1 {{ color: #10b981; font-size: 24px; margin: 0 0 20px 0; }}
        .stats {{ text-align: left; background: #0f172a; padding: 15px 20px; border-radius: 8px; margin-bottom: 20px; }}
        .stats p {{ margin: 10px 0; font-size: 16px; display: flex; justify-content: space-between; }}
        .stats span {{ font-weight: bold; color: #38bdf8; }}
        .time {{ font-size: 13px; color: #94a3b8; margin-top: 10px; font-style: italic; }}
        .links a {{ display: inline-block; margin: 5px; padding: 8px 15px; text-decoration: none; background: #3b82f6; color: white; border-radius: 6px; font-size: 14px; transition: 0.2s; }}
        .links a:hover {{ background: #2563eb; }}
        @keyframes pop {{ 0% {{ transform: scale(0); }} 80% {{ transform: scale(1.1); }} 100% {{ transform: scale(1); }} }}
    </style>
</head>
<body>
    <div class="card">
        <div class="icon">✅</div>
        <h1>Get Dữ Liệu Thành Công!</h1>
        <div class="stats">
            <p>📺 Kênh Live (TV): <span>{tv_count}</span></p>
            <p>📦 Tổng dữ liệu (FULL): <span>{full_count}</span></p>
        </div>
        <div class="links">
            <a href="tv.json" target="_blank">Xem tv.json</a>
            <a href="full.json" target="_blank">Xem full.json</a>
        </div>
        <div class="time">Cập nhật lần cuối: {time_updated} (GMT+7)</div>
    </div>
</body>
</html>"""

    # 3. Ghi ra file index.html
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print("=======================")
    print("✅ DONE PRO MAX++")
    print(f"📺 TV Channels (Live): {tv_count}")
    print(f"📦 FULL Channels: {full_count}")
    print("🌐 Generated: index.html")
    print("=======================")


# ================= MAIN =================
if __name__ == "__main__":
    data = []
    
    print("Đang cào dữ liệu từ các nguồn...")
    # HỘI QUÁN
    data += process_standard("https://sv.hoiquantv.xyz/api/v1/external/fixtures/unfinished", "HỘI QUÁN")
    # THIÊN ĐÌNH
    data += process_standard("https://sv.thiendinhtv.xyz/api/v1/external/fixtures/unfinished", "THIÊN ĐÌNH")
    # VÒNG CẤM
    data += process_vongcam()
    # CA LA TV
    data += process_cala_tv()
    # TV.m3u giữ nguyên group
    data += load_external_keep_group("https://raw.githubusercontent.com/hieu-TQS/TV/refs/heads/main/TV.m3u")
    # FPT SPORT
    data += load_fpt_sport("https://raw.githubusercontent.com/t23-02/bongda/refs/heads/main/bongda.m3u")
    
    # WRITE JSON & HTML FILES
    write_files(data)
