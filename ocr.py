import sys
import json

try:
    from pdf2image import convert_from_path
    import pytesseract
except ImportError:
    print("", end="")
    sys.exit(0)

path = sys.argv[1]
images = convert_from_path(path)
text = ""
for img in images:
    text += pytesseract.image_to_string(img)

print(text)

