from PIL import Image

def create_shifted_substitution(key):
    """Membuat kamus substitusi yang digeser berdasarkan key."""
    original_substitution = {
        'A': 'Batu', 'B': 'Lebah', 'C': 'Kaca', 'D': 'Lada', 'E': 'Lelah', 'F': 'Info',
        'G': 'Laga', 'H': 'Bahu', 'I': 'Diri', 'J': 'Baja', 'K': 'Luka', 'L': 'Pulau',
        'M': 'Lama', 'N': 'Dunia', 'O': 'Solo', 'P': 'Tepi', 'Q': 'Taqwa', 'R': 'Bara',
        'S': 'Masa', 'T': 'Kota', 'U': 'Kutu', 'V': 'Lava', 'W': 'Mawar', 'X': 'Pixel',
        'Y': 'Daya', 'Z': 'Azan',
        'a': 'batu', 'b': 'lebah', 'c': 'kaca', 'd': 'lada', 'e': 'lelah', 'f': 'info',
        'g': 'laga', 'h': 'bahu', 'i': 'diri', 'j': 'baja', 'k': 'luka', 'l': 'pulau',
        'm': 'lama', 'n': 'dunia', 'o': 'solo', 'p': 'tepi', 'q': 'taqwa', 'r': 'bara',
        's': 'masa', 't': 'kota', 'u': 'kutu', 'v': 'lava', 'w': 'mawar', 'x': 'pixel',
        'y': 'daya', 'z': 'azan'
    }
    
    shifted_dict = {}
    for k in original_substitution:
        if k.isupper():
            # Untuk huruf besar
            new_pos = chr((ord(k) - ord('A') + key) % 26 + ord('A'))
            shifted_dict[k] = original_substitution[new_pos]
        else:
            # Untuk huruf kecil
            new_pos = chr((ord(k) - ord('a') + key) % 26 + ord('a'))
            shifted_dict[k] = original_substitution[new_pos]
    
    return shifted_dict

def encrypt_message(message, key):
    """Mengenkripsi pesan menggunakan Caesar cipher dengan substitusi kustom."""
    substitution_dict = create_shifted_substitution(key)
    encrypted = []
    
    for char in message:
        if char in substitution_dict:
            encrypted.append(substitution_dict[char])
        else:
            encrypted.append(char)
    
    return ' '.join(encrypted)

def decrypt_message(encrypted_message, key):
    """Mendekripsi pesan yang dienkripsi."""
    substitution_dict = create_shifted_substitution(key)
    # Buat dictionary terbalik untuk dekripsi
    reverse_dict = {v: k for k, v in substitution_dict.items()}
    
    words = encrypted_message.split()
    decrypted = ''
    
    for word in words:
        if word in reverse_dict:
            decrypted += reverse_dict[word]
        else:
            decrypted += word
    
    return decrypted

def encode_image(image_name, message, output_image_name):
    # Tambahkan marker di akhir pesan
    message = message + "$$"
    
    # Buka gambar dan pastikan dalam mode RGB
    image = Image.open(image_name).convert('RGB')
    
    # Cek ekstensi output file
    output_ext = output_image_name.split('.')[-1].lower()
    if output_ext != 'png':
        # Jika bukan PNG, ubah ke PNG
        output_image_name = output_image_name.rsplit('.', 1)[0] + '.png'
        print("Warning: Output file akan disimpan sebagai PNG untuk menghindari kehilangan data")
    
    encoded_image = image.copy()
    pixels = encoded_image.load()
    width, height = image.size
    
    # Convert message ke binary
    binary_message = ''.join(format(ord(char), '08b') for char in message)
    binary_length = len(binary_message)
    
    if binary_length > width * height * 3:
        raise ValueError("Pesan terlalu panjang untuk gambar ini")
    
    idx = 0
    for y in range(height):
        for x in range(width):
            if idx < binary_length:
                r, g, b = pixels[x, y]
                if idx < binary_length:
                    r = (r & ~1) | int(binary_message[idx])
                    idx += 1
                if idx < binary_length:
                    g = (g & ~1) | int(binary_message[idx])
                    idx += 1
                if idx < binary_length:
                    b = (b & ~1) | int(binary_message[idx])
                    idx += 1
                pixels[x, y] = (r, g, b)
            else:
                break
    
    # Selalu simpan sebagai PNG untuk menghindari kompresi
    encoded_image.save(output_image_name, 'PNG')
    return f"Pesan berhasil disembunyikan dalam file {output_image_name}"

def decode_image(image_name):
    # Buka gambar dan konversi ke RGB
    image = Image.open(image_name).convert('RGB')
    pixels = image.load()
    width, height = image.size
    
    binary_data = ""
    # Baca bit LSB dari setiap channel RGB
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            binary_data += str(r & 1)
            binary_data += str(g & 1)
            binary_data += str(b & 1)
    
    # Konversi binary ke ASCII
    decoded_data = ""
    for i in range(0, len(binary_data), 8):
        byte = binary_data[i:i+8]
        if len(byte) == 8:  # Pastikan byte lengkap
            try:
                char = chr(int(byte, 2))
                decoded_data += char
                # Cek apakah kita menemukan marker akhir pesan
                if decoded_data[-2:] == "$$":
                    return decoded_data[:-2]  # Hapus marker $$
            except:
                break
    
    return "Tidak ada pesan tersembunyi atau format tidak sesuai"

def main():
    while True:
        print("\nImage Steganography")
        print("1. Encode")
        print("2. Decode")
        choice = input("Masukkan pilihan Anda: ")
        
        if choice == '1':
            image_name = input("Masukkan nama file gambar (dengan ekstensi): ")
            message = input("Masukkan pesan yang akan dienkripsi: ")
            key = int(input("Masukkan kunci pergeseran (angka): "))
            
            # Enkripsi pesan
            encrypted_message = encrypt_message(message, key)
            print("\n=== Hasil Enkripsi ===")
            print(f"Plain text: {message}")
            print(f"Cipher text: {encrypted_message}")
            print("==================")
            
            output_name = input("\nMasukkan nama untuk gambar hasil (dengan ekstensi): ")
            try:
                result = encode_image(image_name, encrypted_message, output_name)
                print(result)
                print("\nSimpan cipher text di atas untuk proses decode!")
            except Exception as e:
                print(f"Error: {str(e)}")
        
        elif choice == '2':
            image_name = input("Masukkan nama file gambar (dengan ekstensi): ")
            cipher_text = input("Masukkan cipher text: ")
            key = int(input("Masukkan kunci pergeseran (angka): "))
            try:
                # Langsung dekripsi dari cipher text yang dimasukkan
                decrypted_message = decrypt_message(cipher_text, key)
                print("\n=== Hasil Dekripsi ===")
                print(f"Cipher text: {cipher_text}")
                print(f"Plain text: {decrypted_message}")
                print("==================")
            except Exception as e:
                print(f"Error: {str(e)}")
        
        else:
            print("Pilihan tidak valid")
            
        if input("\nTekan 1 untuk lanjut, 0 untuk keluar: ") != '1':
            break

if __name__ == "__main__":
    main()
