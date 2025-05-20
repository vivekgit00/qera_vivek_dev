import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
import os
import uuid

print(uuid.uuid4())

# List of data/URLs for QR codes
qr_data_list = [
    {"pont": "2", "product_name":"shower", "uuid":"asdasd-asdasd-asdfasd-asd"},
    {"pont": "2", "product_name":"shower", "uuid":"asdasd-asdasd-asdfasd-asd1"},
    {"pont": "2", "product_name":"shower", "uuid":"asdasd-asdasd-asdfasd-asd2"},
    {"pont": "2", "product_name":"shower", "uuid":"asdasd-asdasd-asdfasd-asd3"},
    {"pont": "2", "product_name":"shower", "uuid":"asdasd-asdasd-asdfasd-asd4"},
]

# Generate QR code images
qr_images = []
for i, data in enumerate(qr_data_list):
    qr = qrcode.make(data)
    filename = f"qr_temp_{i}.png"
    qr.save(filename)
    qr_images.append(filename)

# Create a PDF
pdf_filename = "multiple_qr_codes.pdf"
c = canvas.Canvas(pdf_filename, pagesize=letter)

# Page size and layout config
page_width, page_height = letter
qr_size = 1 * inch  # Size of each QR code image
margin = 1 * inch
spacing = 0.3 * inch

# Layout: 3 QR codes per row
qr_per_row = 3
x = margin
y = page_height - margin - qr_size

for i, img_path in enumerate(qr_images):
    c.drawImage(img_path, x, y, width=qr_size, height=qr_size)
    x += qr_size + spacing

    if (i + 1) % qr_per_row == 0:
        x = margin
        y -= qr_size + spacing

    # Add new page if needed
    if y < margin:
        c.showPage()
        x = margin
        y = page_height - margin - qr_size

# Save PDF
c.save()

# Clean up temp QR images
for img in qr_images:
    os.remove(img)

print(f"PDF '{pdf_filename}' created with {len(qr_data_list)} QR codes.")
