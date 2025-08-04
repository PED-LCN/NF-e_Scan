import os
import io
from google.cloud import vision
import re
import cv2
from Document_maneger import create_document  

#Image Capture Part
cap = cv2.VideoCapture(0)
foto_salva = False
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
            foto_salva = True
            print("Imagem capturada!")
            break

cap.release()
cv2.destroyAllWindows()

if not foto_salva:
    print("Processamento cancelado, nenhuma foto foi salva.")
    exit()

#Data process
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'C:\Users\PEDRO\Documents\google_creds\extratordenotasfiscais-c7b0947eedc2.json'

def detectar_texto_em_imagem_estruturado(caminho_para_foto):
   
    client = vision.ImageAnnotatorClient()
    
    with io.open(caminho_para_foto, 'rb') as image_file:
        content = image_file.read()
    
    image = vision.Image(content=content)
    
    response = client.document_text_detection(image=image)
    
    return response

def extrair_dados_fatura_api(api_response):
    
    faturas = []
    TOLERANCIA_Y = 2
    
    palavras_com_coordenadas = []
    for page in api_response.full_text_annotation.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    word_text = ''.join([symbol.text for symbol in word.symbols])
                    y_coord = word.bounding_box.vertices[0].y
                    x_coord = word.bounding_box.vertices[0].x
                    palavras_com_coordenadas.append({'texto': word_text, 'y': y_coord, 'x': x_coord})
    
    palavras_com_coordenadas.sort(key=lambda item: item['y'])
    
    linhas_de_texto = []
    if palavras_com_coordenadas:
        linha_atual = [palavras_com_coordenadas[0]]
        for i in range(1, len(palavras_com_coordenadas)):
            if abs(palavras_com_coordenadas[i]['y'] - linha_atual[-1]['y']) < TOLERANCIA_Y:
                linha_atual.append(palavras_com_coordenadas[i])
            else:
                linhas_de_texto.append(linha_atual)
                linha_atual = [palavras_com_coordenadas[i]]
        linhas_de_texto.append(linha_atual)
    
    numero_padrao = r'(\d{9}/\d{2})'
    data_padrao = r'(\d{2}/\d{2}/\d{4})'
    valor_padrao = r'(\d{1,3}\.\d{3},\d{2})'
    
    for linha in linhas_de_texto:
        numeros = [item for item in linha if re.match(numero_padrao, item['texto'])]
        datas = [item for item in linha if re.match(data_padrao, item['texto'])]
        valores = [item for item in linha if re.match(valor_padrao, item['texto'])]

        if numeros:
            numeros.sort(key=lambda item: item['x'])
            datas.sort(key=lambda item: item['x'])
            valores.sort(key=lambda item: item['x'])

            for i in range(len(numeros)):
                try:
                    faturas.append({
                        'numero': numeros[i]['texto'],
                        'vencimento': datas[i]['texto'],
                        'valor': valores[i]['texto']
                    })
                except IndexError:
                    continue

    return faturas

caminho_imagem = 'captura.jpg'

print("\n--- Enviando imagem para Google Vision AI ---")
try:
    response_api = detectar_texto_em_imagem_estruturado(caminho_imagem)
    print("Texto extraído com sucesso pela API!")
    
except Exception as e:
    print(f"Ocorreu um erro ao chamar a API: {e}")
    print("Verifique se sua chave de autenticação está configurada corretamente.")
    exit()

dados_faturas = extrair_dados_fatura_api(response_api)

print("\n--- Dados Processados ---")
if dados_faturas:
    for fatura in dados_faturas:
        print(f"Número: {fatura['numero']}, Vencimento: {fatura['vencimento']}, Valor: {fatura['valor']}")
else:
    print("Nenhum item de fatura encontrado.")

#doc step
if dados_faturas:
    print("\n--- Gerando documento Word com paginacao ---")
    create_document(dados_faturas, 'documento_notas_fiscais.docx')

print("VERIFIQUE SE O DOCUMENTO ESTÁ CORRETO")

