import qrcode
import json
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# Step 1: Prepare your data (as a dict)
data_dict = {
    "name": "product 1",
    "point": "5"
}

# Convert dict to JSON string
data_json = json.dumps(data_dict)

# Step 2: Generate QR code from JSON string
qr = qrcode.make(data_json)
qr_image_path = "qrcode1.png"
qr.save(qr_image_path)

# Step 3: Create PDF and add QR image
pdf_path = "qrcode1.pdf"
c = canvas.Canvas(pdf_path, pagesize=A4)
width, height = A4
image_size = 200

# Position in center
x = (width - image_size) / 2
y = (height - image_size) / 2

c.drawImage(qr_image_path, x, y, width=image_size, height=image_size)
c.showPage()
c.save()

print(f"QR with product data saved to PDF: {pdf_path}")
