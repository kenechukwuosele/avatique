import qrcode

# The URL where your waitlist is hosted.
# Since you are running locally right now, this defaults to localhost.
# You can change this to your real domain (e.g. https://avatique.com) later.
TARGET_URL = "http://127.0.0.1:5000" 

def generate_qr(url, filename="waitlist_qr.png"):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)
    print(f"QR Code generated and saved to {filename}")
    print(f"URL encoded: {url}")

if __name__ == "__main__":
    print(" Generating QR Code for your waitlist...")
    # You can uncomment the line below to ask for input every time
    # url = input("Enter the website URL: ")
    generate_qr(TARGET_URL)
