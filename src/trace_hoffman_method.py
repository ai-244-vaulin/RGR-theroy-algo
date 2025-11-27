import heapq
import struct
import os
from collections import defaultdict
from VARS import *


# ---------- Вузол дерева ----------
class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

    def __repr__(self):
        return f"Node({repr(self.char)}, {self.freq})"


# ---------- Побудова таблиці частот ----------
def build_frequency_table(data: str):
    print("\n=== КРОК 1: Таблиця частот ===")
    freq = defaultdict(int)

    for ch in data:
        freq[ch] += 1

    for ch, fr in freq.items():
        symbol = ch if ch != "\n" else "\\n"
        print(f"'{symbol}' -> {fr}")

    return freq


# ---------- Побудова дерева Хаффмана ----------
def build_huffman_tree(freq_table):
    print("\n=== КРОК 2: Побудова мін-купи ===")

    heap = []
    for ch, fr in freq_table.items():
        node = Node(ch, fr)
        heapq.heappush(heap, node)
        print(f"Вставка вузла: {node}")

    print("Початковий heap:", heap)

    if len(heap) == 1:
        print("Єдиний символ у файлі → створюємо фіктивний вузол.")
        only = heapq.heappop(heap)
        fake = Node(None, 0)
        new = Node(None, only.freq)
        new.left = only
        new.right = fake
        return new

    print("\n=== КРОК 3: Побудова дерева ===")
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)

        print(f"Беремо два мінімальні вузли: {left}, {right}")

        merged = Node(None, left.freq + right.freq)
        merged.left = left
        merged.right = right

        heapq.heappush(heap, merged)
        print(f"Створено новий вузол: {merged}")
        print("Оновлений heap:", heap)

    print("\nДерево Хаффмана побудовано.")
    return heap[0]


# ---------- Генерація кодів ----------
def generate_codes(node, prefix="", codes=None):
    if codes is None:
        codes = {}

    if node.char is not None:
        symbol = node.char if node.char != "\n" else "\\n"
        print(f"Код символу '{symbol}' = {prefix}")
        codes[node.char] = prefix
    else:
        generate_codes(node.left, prefix + "0", codes)
        generate_codes(node.right, prefix + "1", codes)

    return codes


# ---------- Бітовий рядок → bytes ----------
def bits_to_bytes(bitstring):
    padding = 8 - (len(bitstring) % 8)
    if padding != 8:
        bitstring += "0" * padding
    else:
        padding = 0

    print(f"\nДодаємо {padding} біт(ів) доповнення для вирівнювання.")

    out = bytes(int(bitstring[i:i+8], 2) for i in range(0, len(bitstring), 8))
    return padding.to_bytes(1, "big") + out


# ---------- bytes → бітовий рядок ----------
def bytes_to_bits(padded_data):
    padding = padded_data[0]
    bitstring = "".join(f"{byte:08b}" for byte in padded_data[1:])
    print(f"Видаляємо {padding} біт(ів) доповнення.")
    return bitstring[:-padding] if padding else bitstring


# ============================================================
#                         С Т И С Н Е Н Н Я
# ============================================================

def huffman_compress(input_path, output_path):
    print("\n================ С Т И С Н Е Н Н Я ================")
    print(f"Читання файлу: {input_path}")

    Sorig = os.path.getsize(input_path)
    print(f"Розмір до стиснення: {Sorig} байт")

    with open(input_path, "r", encoding="utf-8") as f:
        data = f.read()

    freq_table = build_frequency_table(data)
    tree = build_huffman_tree(freq_table)

    print("\n=== КРОК 4: Генерація кодів ===")
    codes = generate_codes(tree)

    print("\n=== КРОК 5: Кодування тексту ===")
    encoded_bits = "".join(codes[ch] for ch in data)
    print("Бітовий потік:", encoded_bits)

    encoded_bytes = bits_to_bytes(encoded_bits)

    print("\n=== КРОК 6: Запис у файл ===")
    with open(output_path, "wb") as f:
        f.write(struct.pack(">H", len(freq_table)))

        for ch, fr in freq_table.items():
            char_enc = ch.encode("utf-8")
            f.write(struct.pack(">B", len(char_enc)))
            f.write(char_enc)
            f.write(struct.pack(">I", fr))

        f.write(encoded_bytes)

    Scomp = os.path.getsize(output_path)

    # ---- Метрики стиснення ----
    compression_ratio = 1 - (Scomp / Sorig)
    compression_factor = Sorig / Scomp

    print("\n=== Показники стиснення ===")
    print(f"S_orig: {Sorig} байт")
    print(f"S_comp: {Scomp} байт")
    print(f"Compression Ratio:  {compression_ratio:.4f} ({compression_ratio*100:.2f}%)")
    print(f"Compression Factor: {compression_factor:.4f} разів")
    print(f"\nФайл стиснено -> {output_path}")


# ============================================================
#                         Р О З П А К У В А Н Н Я
# ============================================================

def huffman_decompress(input_path, output_path):
    print("\n================ Р О З П А К У В А Н Н Я ================")
    print(f"Читання файлу: {input_path}")

    with open(input_path, "rb") as f:
        raw = f.read()

    pos = 0

    symbols_count = struct.unpack(">H", raw[pos:pos+2])[0]
    pos += 2
    print(f"Кількість символів у таблиці: {symbols_count}")

    freq_table = {}

    for _ in range(symbols_count):
        strlen = struct.unpack(">B", raw[pos:pos+1])[0]
        pos += 1

        ch = raw[pos:pos+strlen].decode("utf-8")
        pos += strlen

        fr = struct.unpack(">I", raw[pos:pos+4])[0]
        pos += 4

        freq_table[ch] = fr
        print(f"'{ch}' → {fr}")

    print("\nПобудова дерева для декодування...")
    tree = build_huffman_tree(freq_table)

    print("\nДекодування...")
    bit_data = bytes_to_bits(raw[pos:])

    result = []
    node = tree

    for bit in bit_data:
        node = node.left if bit == "0" else node.right
        if node.char is not None:
            result.append(node.char)
            node = tree

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("".join(result))

    print(f"Файл розпаковано → {output_path}")


# ============== Приклад запуску ==============
if __name__ == "__main__":
    # huffman_decompress(f"{PATH_TO_OUTPUT_FILES}sample1_short.huff", f"{PATH_TO_DECODED_FILES}sample1_short.decoded")
    # huffman_decompress(f"{PATH_TO_OUTPUT_FILES}sample2_medium.huff", f"{PATH_TO_DECODED_FILES}sample2_medium.decoded")
    # huffman_decompress(f"{PATH_TO_OUTPUT_FILES}sample3_large.huff", f"{PATH_TO_DECODED_FILES}sample3_large.decoded")
    # huffman_decompress(f"{PATH_TO_OUTPUT_FILES}sample4_random.huff", f"{PATH_TO_DECODED_FILES}sample4_random.decoded")
    # huffman_decompress(f"{PATH_TO_OUTPUT_FILES}sample5_numbers.huff", f"{PATH_TO_DECODED_FILES}sample5_numbers.decoded")
    huffman_decompress(f"{PATH_TO_OUTPUT_FILES}sample6_ukr.huff", f"{PATH_TO_DECODED_FILES}sample6_ukr.decoded")
