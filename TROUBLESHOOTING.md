# Database Холболтын Алдаа - Шийдэх Заавар

## Алдаа: Connection timed out

Хэрэв та дараах алдааг харж байвал:

```
connection to server at "13.214.153.0", port 5432 failed: Connection timed out
```

## Шалгах зүйлс:

### 1. Database сервер ажиллаж байгаа эсэх

- Database сервер ажиллаж байгаа эсэхийг шалгана уу
- Network холболт байгаа эсэхийг шалгана уу

### 2. Firewall шалгах

- Windows Firewall эсвэл бусад firewall database port (5432)-ийг блоклож байгаа эсэх
- Firewall дээр PostgreSQL port-ийг зөвшөөрөх

### 3. Network холболт шалгах

```bash
# Ping шалгах
ping 13.214.153.0

# Port шалгах (Windows)
telnet 13.214.153.0 5432
```

### 4. Database credentials шалгах

- `config.py` эсвэл `.env` файлд зөв credentials байгаа эсэх
- Database нэр зөв эсэх

### 5. Test connection ажиллуулах

```bash
python test_connection.py
```

## Түр шийдэл

Хэрэв database холбогдохгүй байвал:

1. Систем database холболтгүйгээр эхэлнэ (lazy loading)
2. Query хийхэд алдаа гарна
3. Database холбогдсоны дараа дахин оролдоно

## Байнгын шийдэл

1. Database сервер ажиллаж байгаа эсэхийг баталгаажуулах
2. Network/Firewall тохиргоог шалгах
3. Database credentials зөв эсэхийг баталгаажуулах
