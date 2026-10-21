# usb6501_control

ควบคุม NI USB-6501 (Digital I/O 24 ช่อง: P0/P1/P2 พอร์ตละ 8 line, 5V TTL) ด้วย Python + NI-DAQmx

## ติดตั้ง (Windows)
1. ติดตั้ง driver **NI-DAQmx** จาก ni.com (Pi/ARM Linux ไม่รองรับ)
2. เสียบ USB-6501 แล้วดูชื่ออุปกรณ์ใน NI MAX (เช่น `Dev1`)
3. `pip install -r requirements.txt`

## ใช้งาน
```
python -m usb6501 list
python -m usb6501 read 0            # อ่านทั้ง port0
python -m usb6501 read 0 3          # อ่าน P0.3
python -m usb6501 write 0 3 1       # P0.3 = 1
python -m usb6501 write 1 0xFF      # port1 = 255
python -m usb6501 pulse 0 0 500     # pulse P0.0 500 ms
python -m usb6501 monitor 1         # ดูการเปลี่ยนแปลงของ port1
python -m usb6501 gui
python -m usb6501 --simulate gui    # ทดสอบโดยไม่มีฮาร์ดแวร์
```
เลือกอุปกรณ์อื่นด้วย `--dev Dev2`

```python
from usb6501 import Usb6501
with Usb6501("Dev1", hold=True) as d:
    d.write_line(0, 0, True)
    print(d.read_port(1))
```

## ข้อควรระวัง
- เมื่อไม่ใช้ `hold=True` ขา output จะกลับเป็น input (tri-state) ทันทีที่คำสั่งเสร็จ ถ้าต้องการให้ค้างระดับ ให้ใช้ `hold=True` (และห้าม close ก่อนจบงาน)
- ระดับไฟ 5V TTL, กระแสต่อ line จำกัด (ดู datasheet) — ใช้ relay driver/optocoupler เมื่อขับโหลด
- โค้ดนี้ทดสอบบน Pi ด้วย `--simulate` เท่านั้น ยังไม่ได้ทดสอบกับอุปกรณ์จริง: ลอง loopback P0.0 → P1.0 ก่อน

## ทดสอบ
`python -m pytest tests/`
