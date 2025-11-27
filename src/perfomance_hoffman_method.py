import heapq
import struct
import os
from collections import defaultdict


# ---------- Вузол дерева ----------
class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq


# ---------- Побудова таблиці частот ----------
def build_frequency_table(data: str):
    freq = defaultdict(int)
    for ch in data:
        freq[ch] += 1
    return freq


# ---------- Побудова дерева Хаффмана ----------
def build_huffman_tree(freq_table):
    heap = []
    for ch, fr in freq_table.items():
        heapq.heappush(heap, Node(ch, fr))

    # Якщо символ один → додаємо фейковий
    if len(heap) == 1:
        only = heapq.heappop(heap)
        fake = Node(None, 0)
        new = Node(None, only.freq)
        new.left = only
        new.right = fake
        return new

    # Основний цикл побудови дерева
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)

        merged = Node(None, left.freq + right.freq)
        merged.left = left
        merged.right = right

        heapq.heappush(heap, merged)

    return heap[0]


# ---------- Генерація кодів ----------
def generate_codes(node, prefix="", codes=None):
    if codes is None:
        codes = {}

    if node.char is not None:
        codes[node.char] = prefix
    else:
        generate_codes(node.left, prefix + "0", codes)
        generate_codes(node.right, prefix + "1", codes)

    return codes


# ---------- Перетворення бітового рядка у bytes ----------
def bits_to_bytes(bitstring):
    padding = 8 - (len(bitstring) % 8)
    if padding != 8:
        bitstring += "0" * padding
    else:
        padding = 0

    out = bytes(int(bitstring[i:i+8], 2) for i in range(0, len(bitstring), 8))
    return padding.to_bytes(1, "big") + out


# ---------- Перетворення bytes у бітовий рядок ----------
def bytes_to_bits(padded_data):
    padding = padded_data[0]
    bitstring = "".join(f"{byte:08b}" for byte in padded_data[1:])
    return bitstring[:-padding] if padding else bitstring


# ============================================================
#                         С Т И С Н Е Н Н Я
# ============================================================

def huffman_compress(input_path, output_path):

    # Розмір до стиснення
    Sorig = os.path.getsize(input_path)

    # Зчитування тексту
    with open(input_path, "r", encoding="utf-8") as f:
        data = f.read()

    freq_table = build_frequency_table(data)
    tree = build_huffman_tree(freq_table)
    codes = generate_codes(tree)

    # Кодування тексту
    encoded_bits = "".join(codes[ch] for ch in data)
    encoded_bytes = bits_to_bytes(encoded_bits)

    # Запис стисненого файлу
    with open(output_path, "wb") as f:
        f.write(struct.pack(">H", len(freq_table)))

        for ch, fr in freq_table.items():
            char_encoded = ch.encode("utf-8")
            f.write(struct.pack(">B", len(char_encoded)))
            f.write(char_encoded)
            f.write(struct.pack(">I", fr))

        f.write(encoded_bytes)

    # Розмір після стиснення
    Scomp = os.path.getsize(output_path)

    # Показники ефективності
    compression_ratio = 1 - (Scomp / Sorig)
    compression_factor = Sorig / Scomp

    print("\n=== Показники стиснення ===")
    print(f"Sorig (до):      {Sorig} байт")
    print(f"Scomp (після):   {Scomp} байт")
    print(f"Compression Ratio:  {compression_ratio:.4f}  ({compression_ratio*100:.2f}%)")
    print(f"Compression Factor: {compression_factor:.4f} разів")

    print(f"\nФайл стиснено → {output_path}")


# ============================================================
#                         Р О З П А К У В А Н Н Я
# ============================================================

def huffman_decompress(input_path, output_path):

    with open(input_path, "rb") as f:
        raw = f.read()

    pos = 0

    # Кількість символів
    symbols_count = struct.unpack(">H", raw[pos:pos+2])[0]
    pos += 2

    # Читання частот
    freq_table = {}
    for _ in range(symbols_count):
        strlen = struct.unpack(">B", raw[pos:pos+1])[0]
        pos += 1

        ch = raw[pos:pos+strlen].decode("utf-8")
        pos += strlen

        freq = struct.unpack(">I", raw[pos:pos+4])[0]
        pos += 4

        freq_table[ch] = freq

    # Залишок → бітовий потік
    bit_data = bytes_to_bits(raw[pos:])

    # Побудова дерева та декодування
    tree = build_huffman_tree(freq_table)

    result = []
    node = tree

    for bit in bit_data:
        node = node.left if bit == "0" else node.right

        if node.char is not None:
            result.append(node.char)
            node = tree

    # Запис результату
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("".join(result))

    print(f"Файл розпаковано → {output_path}")


# ============== Приклад запуску ==============
if __name__ == "__main__":
    huffman_compress("sample1_short.txt", "sample1_short.huff")
    huffman_decompress("sample1_short.huff", "decoded_sample1.txt")
