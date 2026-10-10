# FaceTimeOrPy

API xác thực khuôn mặt bằng Python, FastAPI và thư viện `face_recognition`. Dự án nhận hai ảnh đầu vào: ảnh hồ sơ và ảnh chụp từ camera, sau đó so sánh khuôn mặt và trả về kết quả khớp hoặc không khớp.

## 1. Tổng quan

Dự án này cung cấp một service HTTP với các chức năng chính:

- Kiểm tra sức khỏe service tại endpoint `/health`
- Xác thực khuôn mặt qua endpoint `/api/verify-face`
- Nhận dữ liệu dạng `multipart/form-data` với hai file hình ảnh
- So sánh encoding khuôn mặt bằng `face_recognition.compare_faces`
- Trả về JSON dạng `{ "match": true|false }`

Cấu trúc thư mục chính:

- `app/main.py`: định nghĩa FastAPI app và logic xác thực khuôn mặt
- `tests/test_main.py`: test cơ bản để kiểm tra endpoint `/health`
- `Dockerfile`: đóng gói ứng dụng thành image Docker
- `docker-compose.yml`: chạy service trong môi trường containerized
- `requirements.txt`: dependencies runtime
- `requirements-dev.txt`: dependencies để phát triển và kiểm thử

---

## 2. Yêu cầu môi trường

Trước khi chạy dự án, bạn cần:

- Python 3.11
- `pip` và `virtualenv`
- Docker + Docker Compose (nếu đóng gói bằng container)
- Trên Linux/macOS, bạn cần cài thêm các gói hệ thống hỗ trợ `dlib` và `face_recognition`

Các package cần thiết đã được định nghĩa trong file `requirements.txt`.

### Cài đặt trên Ubuntu/Debian

```bash
sudo apt-get update
sudo apt-get install -y \
  build-essential \
  cmake \
  libopenblas-dev \
  liblapack-dev \
  libx11-dev \
  libgtk-3-dev
```

---

## 3. Setup môi trường local

### Tạo môi trường ảo

```bash
cd /Users/tranduong/Documents/FaceTimeOrPy
python3 -m venv .venv
source .venv/bin/activate
```

### Cài đặt dependency

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

Nếu bạn đang ở môi trường Linux mà chưa có build-tools, hãy cài đặt các gói hệ thống phía trên trước khi cài `dlib`.

---

## 4. Chạy ứng dụng local

### Chạy bằng uvicorn

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Sau khi chạy, service sẽ sẵn sàng trên:

- `http://localhost:8000/health`
- `http://localhost:8000/docs` (Swagger UI)

### Kiểm tra sức khỏe

```bash
curl http://localhost:8000/health
```

Kết quả mong đợi:

```json
{
  "status": "ok"
}
```

---

## 5. Gọi API xác thực khuôn mặt

### Endpoint

```http
POST /api/verify-face
Content-Type: multipart/form-data
```

### Params

- `profile_image`: file ảnh đầu vào đại diện cho hồ sơ người dùng
- `camera_image`: file ảnh chụp từ camera để đối chiếu

### Ví dụ curl

```bash
curl -X POST "http://localhost:8000/api/verify-face" \
  -F "profile_image=@/path/to/profile.jpg" \
  -F "camera_image=@/path/to/camera.jpg"
```

### Ví dụ response

```json
{
  "match": true
}
```

Nếu không tìm thấy khuôn mặt trong ảnh, API sẽ trả về JSON báo lỗi kèm message mô tả rõ nguyên nhân.

---

## 6. Chạy test

Dự án hiện có test cơ bản để kiểm tra health endpoint:

```bash
pytest -q
```

Kết quả mong đợi là test pass và trả về status 200 cho `/health`.

---

## 7. Đóng gói bằng Docker

### Build image

```bash
docker build -t facetimeorpy:latest .
```

### Chạy container

```bash
docker run --rm -p 8000:8000 facetimeorpy:latest
```

Service sẽ chạy trên port `8000` và có thể truy cập tương tự như local:

```bash
curl http://localhost:8000/health
```

### Chạy bằng Docker Compose

```bash
docker compose up --build -d
```

Để dừng service:

```bash
docker compose down
```

---

## 8. Triển khai trên production

Đối với môi trường production, nên áp dụng các nguyên tắc sau:

- Chạy service dưới dạng container hoặc process manager
- Sử dụng reverse proxy như Nginx hoặc Traefik để xử lý HTTPS và domain
- Chạy nhiều worker nếu tải lớn để tăng hiệu suất
- Giới hạn kích thước file upload theo quy mô hệ thống
- Cấu hình logging và monitoring để theo dõi lỗi và thời gian xử lý
- Sử dụng secrets management cho các biến môi trường nếu bổ sung cấu hình nhạy cảm trong tương lai

### Ví dụ chạy production bằng uvicorn

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
```

### Ví dụ triển khai bằng Docker Compose production

```yaml
services:
  api:
    build: .
    container_name: face-attendance-api
    ports:
      - "80:8000"
    restart: unless-stopped
```

Trong môi trường production thực tế, bạn nên đặt phía trước một reverse proxy để bật TLS và quản lý domain, ví dụ:

- Nginx + Let's Encrypt
- Traefik
- Cloud Load Balancer

---

## 9. Lưu ý kỹ thuật

- Dự án phụ thuộc mạnh vào `dlib` và `face_recognition`, nên cần environment hỗ trợ compile native libraries.
- Ảnh upload nên là ảnh rõ mặt, có ánh sáng hợp lý và độ phân giải phù hợp để tăng độ chính xác.
- Nếu triển khai hàng loạt, nên cân nhắc tối ưu kích thước ảnh trước khi xử lý để giảm thời gian phản hồi.
- Mặc định API chỉ so sánh 1 khuôn mặt đầu tiên được phát hiện trong mỗi ảnh, nên với ảnh có nhiều khuôn mặt cần bổ sung logic chọn khuôn mặt phù hợp.

---

## 10. Mục tiêu dự án

Dự án này hướng đến bài toán kiểm tra danh tính bằng khuôn mặt trong các ứng dụng như:

- Attendance / chấm công bằng khuôn mặt
- Xác thực tài khoản bằng hình ảnh
- Hệ thống kiểm soát truy cập
- API backend cho ứng dụng mobile/web

---

## 11. Tài liệu tham khảo nhanh

- FastAPI: https://fastapi.tiangolo.com/
- Uvicorn: https://www.uvicorn.org/
- face_recognition: https://github.com/ageitgey/face_recognition
- Docker: https://docs.docker.com/

---

## 12. Các lệnh thao tác nhanh

```bash
# Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run local
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Test
pytest -q

# Docker build
docker build -t facetimeorpy:latest .

# Docker run
docker run --rm -p 8000:8000 facetimeorpy:latest

# Docker compose
docker compose up --build -d
```

---

Nếu bạn muốn, tôi có thể tiếp tục viết thêm một phiên bản README chuyên nghiệp hơn theo kiểu doanh nghiệp, hoặc tạo luôn file `.env.example`, `Makefile`, và cấu hình deploy cho production.
