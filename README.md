Dưới đây là mẫu README.md hoàn chỉnh, trình bày đẹp mắt và chuyên nghiệp, mô tả đầy đủ chức năng và cách cài đặt dự án của bạn. Bạn chỉ cần copy nội dung này dán vào file README.md trên repo của mình.
```markdown
# 📺 Auto IPTV & Football Streams JSON Fetcher

Dự án tự động thu thập (crawl), kiểm tra (check live) và chuyển đổi các liên kết truyền hình, bóng đá từ các nguồn M3U/API thành định dạng JSON. Hệ thống được tự động hóa hoàn toàn nhờ **GitHub Actions**, liên tục cập nhật mỗi 10 phút và có giao diện hiển thị trạng thái bằng HTML.

---

## ✨ Tính Năng Nổi Bật

- 🔄 **Tự động hóa 100%**: Chạy ngầm tự động mỗi 10 phút thông qua GitHub Actions (Cron Job).
- ⚡ **Kiểm tra luồng (Live Check) siêu tốc**: Sử dụng `ThreadPoolExecutor` để check đa luồng (multi-threading) các link M3U8, loại bỏ các kênh chết (dead link) nhanh chóng.
- 📦 **Xuất chuẩn JSON**: Dữ liệu đầu ra là mảng JSON, rất dễ dàng để tích hợp vào các ứng dụng Web/App, Smart TV hoặc Extension.
- 🎨 **Giao diện Dashboard**: Tự động sinh ra file `index.html` có giao diện đẹp mắt để theo dõi thống kê số lượng kênh cập nhật mới nhất.
- 🌐 **Hỗ trợ đa nguồn**: Tích hợp nhiều nguồn (Hội Quán, Thiên Đình, Vòng Cấm, Ca La TV, FPT Sport...).

---

## 📂 Cấu Trúc Dữ Liệu

Sau khi chạy, script sẽ tự động tạo ra 3 file:

1. `tv.json`: Chứa danh sách các kênh **đang sống (Live/Working)**.
2. `full.json`: Chứa danh sách **tất cả** các kênh quét được (Bao gồm cả link die).
3. `index.html`: Trang web hiển thị thống kê trạng thái lấy dữ liệu thành công.

**Định dạng JSON output:**
```json
[
    {
        "group": "Tên Nhóm",
        "title": "Thời gian | Tên Trận Đấu / Kênh",
        "logo": "URL_Logo",
        "url": "[http://domain.com/stream.m3u8](http://domain.com/stream.m3u8)",
        "time": "YYYY-MM-DD HH:MM:SS"
    }
]

```
## 🚀 Hướng Dẫn Thiết Lập (Cho GitHub)
Nếu bạn muốn tạo một hệ thống tự động chạy trên GitHub của riêng mình, hãy làm theo các bước sau:
### 1. Tạo Repository
 * **Fork** repository này hoặc tạo một repository mới.
 * Đảm bảo repo của bạn có đủ 2 file: main.py và .github/workflows/update.yml.
### 2. Cấp Quyền Cho GitHub Actions
Để bot tự động commit file mới lên repo, bạn cần cấp quyền Ghi (Write):
 * Truy cập vào **Settings** của Repo.
 * Chọn **Actions** > **General** ở thanh menu bên trái.
 * Kéo xuống phần **Workflow permissions**, chọn **Read and write permissions**.
 * Bấm **Save**.
### 3. Bật Trang Web (GitHub Pages)
Để xem file index.html trực tiếp như một trang web báo cáo:
 * Vào **Settings** > **Pages**.
 * Ở mục **Source**, chọn nhánh main (hoặc master), thư mục /root.
 * Bấm **Save**. Đợi 1-2 phút, bạn sẽ có link truy cập trang web (VD: https://<username>.github.io/<repo-name>/).
## 💻 Chạy Trực Tiếp (Local)
Nếu bạn muốn chạy test ngay trên máy tính của mình:
 1. Yêu cầu hệ thống đã cài đặt **Python 3.x**.
 2. Cài đặt thư viện requests:
   ```bash
   pip install requests
   
   ```
 3. Chạy file mã nguồn:
   ```bash
   python main.py
   
   
   ```
```
4. Các file dữ liệu sẽ được tạo ngay trong thư mục chứa file chạy.

---

## ⚠️ Khuyến Cáo (Disclaimer)

- Dự án này được tạo ra nhằm mục đích học tập kỹ năng Web Scraping, xử lý JSON và tự động hóa CI/CD. 
- Mọi dữ liệu về các luồng phát sóng (streams) đều được thu thập từ các nguồn công khai trên Internet. 
- Chủ sở hữu kho lưu trữ không lưu trữ hoặc sở hữu bất kỳ tệp tin đa phương tiện nào và không chịu trách nhiệm pháp lý về việc sử dụng các liên kết do công cụ này thu thập.

```
```

```
