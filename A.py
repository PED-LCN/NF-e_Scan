#Image Capture Part
import cv2

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Erro ao abrir a câmera")
    exit()
else:
    window_name='Captura da nota fiscal'
    cv2.namedWindow(window_name)
    
    while True:
        ret, frame = cap.read()

        if cv2.getWindowProperty('Captura da nota fiscal', cv2.WND_PROP_VISIBLE) < 1:
            print("Janela fechada pelo usuário")
            break
        if not ret:
            print("Erro ao ler o frame da câmera")
            break

        #Frame
        height, width, _ = frame.shape
        frame_width = int(width * 0.8)
        frame_height = int(height * 0.2)
        start_x = int((width - frame_width) / 2)
        start_y = int((height - frame_height) / 2)
        end_x = start_x + frame_width
        end_y = start_y + frame_height
        color = (0, 0, 245)  
        thickness = 2       
        
        cv2.rectangle(frame, (start_x, start_y), (end_x, end_y), color, thickness)

        cv2.imshow(window_name, frame)

        if cv2.waitKey(1) & 0xFF == ord('s'):    
            cv2.imwrite('captura.jpg', frame)
            print("Imagem capturada!")
            break

    
cap.release()
cv2.destroyAllWindows()

