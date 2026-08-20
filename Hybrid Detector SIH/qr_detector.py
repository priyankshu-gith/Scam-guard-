import cv2
import os

def extract_link_from_qr(image_path):
    print(f"[*] ScamGuard QR Engine: Scanning image from {image_path}...")
    
    if not os.path.exists(image_path):
        print(f"[-] Error: Image file '{image_path}' not found!")
        return None
        
    try:
        # 1. Read the image using OpenCV
        img = cv2.imread(image_path)
        
        # 2. Initialize the OpenCV QR Code Detector
        detector = cv2.QRCodeDetector()
        
        # 3. Detect and decode the hidden message/link
        secret_link, bbox, straight_qrcode = detector.detectAndDecode(img)
        
        if secret_link:
            print(f"[+] Successfully extracted hidden link: {secret_link}")
            return secret_link
        else:
            print("[-] Scan Failed: No QR code detected or it is unreadable.")
            return None
            
    except Exception as e:
        print(f"[-] An unexpected error occurred: {e}")
        return None

# --- Quick Test Loop ---
# Replace this with any actual QR code image name in your folder to test live!
test_image = "test_qr.png" 
extract_link_from_qr(test_image)

