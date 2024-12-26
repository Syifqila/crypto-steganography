from PIL import Image  # Library untuk manipulasi gambar

# Fungsi untuk membuat kamus substitusi dengan pergeseran berdasarkan kunci
def create_shifted_substitution(key):
    """Membuat kamus substitusi yang digeser berdasarkan key."""
    # Kamus substitusi dasar
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
    
    shifted_dict = {}  # Kamus baru untuk substitusi hasil geser
    for k in original_substitution:
        if k.isupper():  # Untuk huruf besar
            new_pos = chr((ord(k) - ord('A') + key) % 26 + ord('A'))
            shifted_dict[k] = original_substitution[new_pos]
        else:  # Untuk huruf kecil
            new_pos = chr((ord(k) - ord('a') + key) % 26 + ord('a'))
            shifted_dict[k] = original_substitution[new_pos]
    
    return shifted_dict

# Fungsi untuk mengenkripsi pesan menggunakan substitusi
def encrypt_message(message, key):
    """Mengenkripsi pesan menggunakan Caesar cipher dengan substitusi kustom."""
    substitution_dict = create_shifted_substitution(key)
    encrypted = []
    
    for char in message:
        if char in substitution_dict:  # Jika karakter ada dalam kamus substitusi
            encrypted.append(substitution_dict[char])
        else:  # Jika tidak ada, tambahkan karakter asli
            encrypted.append(char)
    
    return ' '.join(encrypted)  # Gabungkan hasil enkripsi dengan spasi

# Fungsi untuk mendekripsi pesan
def decrypt_message(encrypted_message, key):
    """Mendekripsi pesan yang dienkripsi."""
    substitution_dict = create_shifted_substitution(key)
    reverse_dict = {v: k for k, v in substitution_dict.items()}  # Buat kamus terbalik
    
    words = encrypted_message.split()  # Pisahkan pesan terenkripsi ke dalam kata
    decrypted = ''
    
    for word in words:
        if word in reverse_dict:  # Jika kata ditemukan di kamus terbalik
            decrypted += reverse_dict[word]
        else:  # Jika tidak, tambahkan kata asli
            decrypted += word
    
    return decrypted

# Fungsi untuk menyembunyikan pesan dalam gambar menggunakan LSB
def encode_image(image_name, message, output_image_name):
    # Tambahkan penanda akhir pesan
    message = message + "$$"
    
    # Buka gambar dan konversi ke mode RGB
    image = Image.open(image_name).convert('RGB')
    
    # Pastikan file output disimpan sebagai PNG
    output_ext = output_image_name.split('.')[-1].lower()
    if output_ext != 'png':
        output_image_name = output_image_name.rsplit('.', 1)[0] + '.png'
        print("Warning: Output file akan disimpan sebagai PNG untuk menghindari kehilangan data")
    
    encoded_image = image.copy()
    pixels = encoded_image.load()
    width, height = image.size
    
    # Konversi pesan ke biner
    binary_message = ''.join(format(ord(char), '08b') for char in message)
    binary_length = len(binary_message)
    
    # Cek apakah pesan terlalu panjang untuk gambar
    if binary_length > width * height * 3:
        raise ValueError("Pesan terlalu panjang untuk gambar ini")
    
    idx = 0
    for y in range(height):
        for x in range(width):
            if idx < binary_length:
                r, g, b = pixels[x, y]
                if idx < binary_length:  # Modifikasi bit LSB pada kanal merah
                    r = (r & ~1) | int(binary_message[idx])
                    idx += 1
                if idx < binary_length:  # Modifikasi bit LSB pada kanal hijau
                    g = (g & ~1) | int(binary_message[idx])
                    idx += 1
                if idx < binary_length:  # Modifikasi bit LSB pada kanal biru
                    b = (b & ~1) | int(binary_message[idx])
                    idx += 1
                pixels[x, y] = (r, g, b)
            else:
                break
    
    # Simpan gambar hasil dengan format PNG
    encoded_image.save(output_image_name, 'PNG')
    return f"Pesan berhasil disembunyikan dalam file {output_image_name}"

# Fungsi untuk membaca pesan tersembunyi dari gambar
def decode_image(image_name):
    # Buka gambar dan konversi ke mode RGB
    image = Image.open(image_name).convert('RGB')
    pixels = image.load()
    width, height = image.size
    
    binary_data = ""
    # Ekstraksi bit LSB dari setiap piksel
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            binary_data += str(r & 1)
            binary_data += str(g & 1)
            binary_data += str(b & 1)
    
    # Konversi data biner ke karakter ASCII
    decoded_data = ""
    for i in range(0, len(binary_data), 8):
        byte = binary_data[i:i+8]
        if len(byte) == 8:
            char = chr(int(byte, 2))
            decoded_data += char
            if decoded_data[-2:] == "$$":  # Cek penanda akhir pesan
                return decoded_data[:-2]  # Hapus penanda
    
    return "Tidak ada pesan tersembunyi atau format tidak sesuai"

# Fungsi utama untuk menjalankan program
def main():
    while True:
        print("\nImage Steganography")
        print("1. Encode")
        print("2. Decode")
        choice = input("Masukkan pilihan Anda: ")
        
        if choice == '1':  # Pilihan untuk encode
            image_name = input("Masukkan nama file gambar (dengan ekstensi): ")
            message = input("Masukkan pesan yang akan dienkripsi: ")
            key = int(input("Masukkan kunci pergeseran (angka): "))
            
            # Enkripsi pesan sebelum disembunyikan
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
        
        elif choice == '2':  # Pilihan untuk decode
            image_name = input("Masukkan nama file gambar (dengan ekstensi): ")
            cipher_text = input("Masukkan cipher text: ")
            key = int(input("Masukkan kunci pergeseran (angka): "))
            try:
                # Dekripsi pesan
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
    main()  # Jalankan fungsi utama
