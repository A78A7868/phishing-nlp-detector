"""
fill_cover_page.py
Overlay filled student & project information onto the official IICT Cover Page template,
preserving the outer box frame, fixing Student Name label clipping, and applying Jecrc University credentials.
"""

import os
import pypdf
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
TEMPLATE_PDF = os.path.join(
    os.path.expanduser("~"),
    ".gemini/antigravity/brain/4a89c5ba-8963-448f-9d0e-76fac7e8319a/.user_uploaded/media__1785175093508.pdf"
)
IEEE_REPORT_PDF = os.path.join(REPORTS_DIR, "IEEE_Report.pdf")
FILLED_COVER_PDF = os.path.join(REPORTS_DIR, "filled_cover_page.pdf")
FINAL_COMBINED_PDF = os.path.join(REPORTS_DIR, "IEEE_Report_With_Cover.pdf")
TEMP_PNG_PREFIX = os.path.join(REPORTS_DIR, "iict_template_300dpi")

FONT_REGULAR = "/System/Library/Fonts/Supplemental/Times New Roman.ttf"
FONT_BOLD = "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf"

W_PT, H_PT = A4  # 595.27 x 841.89 pt


def generate_clean_cover_pdf():
    png_path = f"{TEMP_PNG_PREFIX}-1.png"
    if not os.path.exists(png_path):
        cmd = f'pdftoppm -png -r 300 "{TEMPLATE_PDF}" "{TEMP_PNG_PREFIX}"'
        os.system(cmd)

    img = Image.open(png_path).convert('RGB')
    w_px, h_px = img.size

    draw = ImageDraw.Draw(img)

    # High-resolution fonts
    font_title = ImageFont.truetype(FONT_BOLD, 58)
    font_field = ImageFont.truetype(FONT_REGULAR, 48)

    # ---------------------------------------------------------------
    # 1) Title Area: White-out placeholder inside outer box frame
    # ---------------------------------------------------------------
    draw.rectangle([260, 560, 2246, 900], fill=(255, 255, 255))

    title1 = "AI-Driven Phishing Email Detection Using NLP"
    title2 = "(Natural Language Processing)"

    bbox1 = font_title.getbbox(title1)
    w1 = bbox1[2] - bbox1[0]
    draw.text(((w_px - w1) / 2, 600), title1, fill=(0, 0, 0), font=font_title)

    bbox2 = font_title.getbbox(title2)
    w2 = bbox2[2] - bbox2[0]
    draw.text(((w_px - w2) / 2, 690), title2, fill=(0, 0, 0), font=font_title)

    # ---------------------------------------------------------------
    # 2) Form Fields: Jecrc University credentials (Roll 23BCON1613)
    #    White-out starts well after label text to avoid clipping.
    # ---------------------------------------------------------------
    LINE_RIGHT = 2240  # Just inside right frame border at x=2252

    # --- Student Name (label ends at x=834; white-out starts at x=865) ---
    y1 = 2632
    draw.rectangle([865, y1 - 65, LINE_RIGHT + 5, y1 + 5], fill=(255, 255, 255))
    draw.text((885, y1 - 60), "Anand krishna G R Nair", fill=(0, 0, 0), font=font_field)
    draw.line([(865, y1), (LINE_RIGHT, y1)], fill=(0, 0, 0), width=3)

    # --- Institute Name: (label ends at x=889; white-out starts at x=915) ---
    y2 = 2737
    draw.rectangle([915, y2 - 65, LINE_RIGHT + 5, y2 + 5], fill=(255, 255, 255))
    draw.text((935, y2 - 60), "Jecrc University", fill=(0, 0, 0), font=font_field)
    draw.line([(915, y2), (LINE_RIGHT, y2)], fill=(0, 0, 0), width=3)

    # --- Institute Roll no.: (label ends at x=968; white-out starts at x=995) ---
    y3 = 2842
    draw.rectangle([995, y3 - 65, LINE_RIGHT + 5, y3 + 5], fill=(255, 255, 255))
    draw.text((1015, y3 - 60), "23BCON1613", fill=(0, 0, 0), font=font_field)
    draw.line([(995, y3), (LINE_RIGHT, y3)], fill=(0, 0, 0), width=3)

    # --- Enrollment no.: (label ends at x=899; white-out starts at x=925) ---
    y4 = 2948
    draw.rectangle([925, y4 - 65, LINE_RIGHT + 5, y4 + 5], fill=(255, 255, 255))
    draw.text((945, y4 - 60), "596563", fill=(0, 0, 0), font=font_field)
    draw.line([(925, y4), (LINE_RIGHT, y4)], fill=(0, 0, 0), width=3)

    # Save cleaned high-res image
    temp_edited_img = os.path.join(REPORTS_DIR, "clean_cover_edited.png")
    img.save(temp_edited_img, quality=98)

    # Convert image to single-page PDF in ReportLab
    c = canvas.Canvas(FILLED_COVER_PDF, pagesize=A4)
    c.drawImage(temp_edited_img, 0, 0, width=W_PT, height=H_PT)
    c.save()
    print(f"✓ Pristine Cover Page PDF saved to: {FILLED_COVER_PDF}")


def merge_cover_and_report():
    generate_clean_cover_pdf()

    writer = pypdf.PdfWriter()

    # 1. Add pristine Cover Page (Page 1)
    cover_reader = pypdf.PdfReader(FILLED_COVER_PDF)
    writer.add_page(cover_reader.pages[0])

    # 2. Add IEEE Thesis Body Pages (Pages 2+)
    if os.path.exists(IEEE_REPORT_PDF):
        body_reader = pypdf.PdfReader(IEEE_REPORT_PDF)
        for page in body_reader.pages:
            writer.add_page(page)

    # Save output combined PDF
    with open(FINAL_COMBINED_PDF, "wb") as f:
        writer.write(f)

    # Overwrite main IEEE_Report.pdf
    with open(IEEE_REPORT_PDF, "wb") as f:
        writer.write(f)

    print(f"✓ Final Report with Cover Page successfully saved to: {IEEE_REPORT_PDF}")


if __name__ == "__main__":
    merge_cover_and_report()
