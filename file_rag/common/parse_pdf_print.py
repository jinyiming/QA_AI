import fitz
from PIL import Image
import pytesseract
import io

def extract_text_from_pdf_with_images(pdf_path):
    text = ""
    
    # 打开 PDF 文件
    pdf_document = fitz.open(pdf_path)
    
    # 遍历每一页
    for page_number in range(len(pdf_document)):
        page = pdf_document.load_page(page_number)
        
        # 提取图片并进行 OCR
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            image = Image.open(io.BytesIO(image_bytes))
            
            # 使用 Tesseract OCR 进行文本提取
            text += pytesseract.image_to_string(image,lang='chi_sim')
            print(text)
    # 关闭 PDF 文件
    pdf_document.close()
    
    return text

# 示例用法
pdf_path = "./data/1930ff7e248a2000/main_doc/省数据局关于开展数据资源开发利用试点申报的通知.pdf"  # 替换为您的 PDF 文件路径
extracted_text = extract_text_from_pdf_with_images(pdf_path)
print(extracted_text)
