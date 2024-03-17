import easyocr

#easyorc to extract the text from an roi
def extract_text_from_image(image_path):
    try:
        reader = easyocr.Reader(['en'])    
        result = reader.readtext(image_path)    
        extracted_text = ' '.join([text[1] for text in result])
        return extracted_text.strip()
    except Exception as e:
        print(f"An error occurred: {e}")
        return 'No text extracted'  
