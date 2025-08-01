import pytesseract
import re
import cv2
from docx import Document

#Image Capture Part
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Erro ao abrir a câmera")
    exit()
else:
    window_name='Captura da nota fiscal'
    cv2.namedWindow(window_name)
    
    while True:
        ret, frame = cap.read()

        if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
            print("Janela fechada pelo usuário")
            break
        if not ret:
            print("Erro ao ler o frame da câmera")
            break

        #Frame
        height, width, _ = frame.shape
        frame_width = int(width * 0.99)
        frame_height = int(height * 0.1)
        start_x = int((width - frame_width) / 2)
        start_y = int((height - frame_height) / 2)
        end_x = start_x + frame_width
        end_y = start_y + frame_height
        color = (200, 0, 255)  
        thickness = 2       
        
        cv2.rectangle(frame, (start_x, start_y), (end_x, end_y), color, thickness)

        cv2.imshow(window_name, frame)

        if cv2.waitKey(1) & 0xFF == ord('s'): 
            roi = frame[start_y:end_y, start_x:end_x]   
            cv2.imwrite('captura.jpg', roi)
            print("Imagem capturada!")
            break

    
cap.release()
cv2.destroyAllWindows()

#Data process
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

try:
    img_capturada = cv2.imread('captura.jpg')
    if img_capturada is None:
        raise FileNotFoundError("Arquivo de imagem não encontrado.")
except FileNotFoundError as e:
    print(e)
    exit()

#filters
gray = cv2.cvtColor(img_capturada, cv2.COLOR_BGR2GRAY)
thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
dilated = cv2.dilate(thresh, kernel, iterations=1)

cv2.imshow('Imagem Processada',dilated )
cv2.waitKey(0)
cv2.destroyAllWindows()

config_tesseract = '--psm 6'
texto_completo = pytesseract.image_to_string(thresh, lang='por',config=config_tesseract)

print("\n--- Texto Extraído ---")
print(texto_completo)
print("----------------------\n")

def extrair_dados_fatura(texto):
    faturas = []
    
    numero_padrao = r'(\d{9}/\d{2})'
    data_padrao = r'(\d{2}/\d{2}/\d{4})'
    valor_padrao = r'(\d{1,3}\.\d{3},\d{2})'
    
    numeros = re.findall(numero_padrao, texto)
    datas = re.findall(data_padrao, texto)
    valores = re.findall(valor_padrao, texto)

    for i in range(len(numeros)):
        try:
            faturas.append({
                'numero': numeros[i],
                'vencimento': datas[i],
                'valor': valores[i]
            })
        except IndexError:
            continue           
    return faturas

dados_faturas = extrair_dados_fatura(texto_completo)
#test
print("\nDados da fatura extraídos:")
print(dados_faturas)

