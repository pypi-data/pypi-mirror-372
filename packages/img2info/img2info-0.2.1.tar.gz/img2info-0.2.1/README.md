# OCR.Space Python SDK (Upgraded)

## Mô tả

SDK nâng cấp cho Im2 info:

- Client sạch với xác thực, xử lý lỗi
- Hỗ trợ input: file, url, bytes, base64
- Có ví dụ và CLI đơn giản
- Cài đặt dễ dàng: `pip install -e .`

## Hướng dẫn sử dụng

### 1. Cài đặt package

Nếu đã upload lên PyPI:

```powershell
pip install img2info
```

Hoặc cài từ source:

```powershell
pip install -e .
```

### 2. Cài đặt dependencies

```powershell
pip install requests
```

### 3. Thiết lập API key

Windows CMD:

```powershell
set OCRSPACE_API_KEY=your_key
```

PowerShell:

```powershell
$env:OCRSPACE_API_KEY="your_key"
```

Linux/macOS:

```sh
export OCRSPACE_API_KEY=your_key
```

### 4. Sử dụng trong code Python

```python
from ocrspace import OCRSpaceClient
client = OCRSpaceClient(api_key="your_key")
result = client.from_file("invoice.png")
print(result.text)
```
