import tkinter as tk
from itertools import combinations
from textwrap import wrap
from tkinter import filedialog
import numpy as np
from tkinter import messagebox
from statistics import mode

def encode(message, r, m):
    G = generate_G(r, m)
    return np.dot(message, G) % 2

def get_combinations(iterable, r):
    return combinations(iterable, r)

def get_column(index, m):
    n = 2 ** m
    column = np.zeros(n)
    for i in range(n):
        if (i >> index) & 1:
            column[i] = 1
    return column

def generate_G(r, m):
    G = []
    n = 2 ** m
    for i in range(r + 1):
        for subset in get_combinations(range(m), i):
            column = np.ones(n)
            for j in subset:
                column *= get_column(j, m)
            G.append(column)
    return np.array(G)

def encode_blocks(blocks, r, m):
    max_length = max(len(block) for block in blocks)
    padded_blocks = [block + '0' * (max_length - len(block)) for block in blocks]
    binary_blocks = np.array([list(map(int, block)) for block in padded_blocks])
    encoded_blocks = encode(binary_blocks, r, m)
    return encoded_blocks

def browse_file():
    filepath = filedialog.askopenfilename(filetypes=[("Text file", "*.txt")])
    if filepath:
        file_path_label_1.config(text=f"Выбранный файл: {filepath}")
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
            binary_content = text_to_binary(content)
            blocks = wrap(binary_content, k)
            encoded_message = encode_blocks(blocks, r, m)
            encoded_message = encoded_message.astype(int)
            encoded_message = encoded_message.tolist()
            save_file_encode(encoded_message)

def text_to_binary(text):
    binary_content = "".join(format(x, "08b") for x in bytearray(text, "utf-8"))
    return binary_content

def save_file_encode(encoded_message):
    filepath = filedialog.asksaveasfilename(defaultextension=".rmencode")
    if filepath:
        with open(filepath, 'w') as file:
            for i in encoded_message:
                for j in i:
                    file.write(str(j))
    messagebox.showinfo("Кодирование", f"Ваш файл сохранен в директории {filepath}")

def save_file_decode(decoded_message):
    filepath = filedialog.asksaveasfilename(defaultextension=".txt")
    if filepath:
        with open(filepath, 'w') as file:
            file.write(decoded_message)
    messagebox.showinfo("Декодирование", f"Ваш файл сохранен в директории {filepath}")

def majority_decode(block, G, k):
    equations = {
        11: [[0, 4, 8, 12], [1, 5, 9, 13], [2, 6, 10, 14], [3, 7, 11, 15]],
        10: [[0, 2, 8, 10], [1, 3, 9, 11], [4, 6, 12, 14], [5, 7, 13, 15]],
        9: [[0, 2, 4, 6], [1, 3, 5, 7], [8, 10, 12, 14], [9, 11, 13, 15]],
        8: [[0, 1, 8, 9], [2, 3, 10, 11], [4, 5, 12, 13], [6, 7, 14, 15]],
        7: [[0, 1, 4, 5], [2, 3, 6, 7], [8, 9, 12, 13], [10, 11, 14, 15]],
        6: [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11], [12, 13, 14, 15]],
        5: [[0, 8], [1, 9], [2, 10], [3, 11], [4, 12], [5, 13], [6, 14], [7, 15]],
        4: [[0, 4], [1, 5], [2, 6], [3, 7], [8, 12], [9, 13], [10, 14], [11, 15]],
        3: [[0, 2], [1, 3], [4, 6], [5, 7], [8, 10], [9, 11], [12, 14], [13, 15]],
        2: [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9], [10, 11], [12, 13], [14, 15]]
    }
    encoded_block = []
    encoded_block_n = []
    majority = []
    block_b = block.copy()
    for i in range(k, 0, -1):
        for j in equations.keys():
            if i == j and j > 5:
                t = equations[j]
                for y in t:
                    b = 0
                    for u in y:
                        b += abs(block_b[u])
                    majority.append(b % 2)
                    b = 0
                encoded_block.insert(0, mode(majority))
                encoded_block_n.insert(0, mode(majority))
                majority = []
    block_b = block_b - (np.dot(encoded_block, G[5:12]))
    block_b = block_b % 2
    encoded_block = []
    for i in range(k, 0, -1):
        for j in equations.keys():
            if i == j and 1 < j < 6:
                t = equations[j]
                for y in t:
                    b = 0
                    for u in y:
                        b += abs(block_b[u])
                    majority.append(b % 2)
                    b = 0
                encoded_block.insert(0, int(mode(majority)))
                encoded_block_n.insert(0, int(mode(majority)))
                majority = []
    block_b = block_b - (np.dot(encoded_block, G[1:5]))
    block_b = block_b % 2
    encoded_block_n.insert(0, int(mode(block_b)))
    return encoded_block_n

def decode_blocks(encoded_blocks, r, m):
    decoded_blocks = []
    for block in encoded_blocks:
        decoded_block = majority_decode(block,generate_G(r, m), k)
        decoded_blocks.append(decoded_block)
    return decoded_blocks

def decode_file():
    filepath = filedialog.askopenfilename(filetypes=[("RM Encode Files", "*.rmencode")])
    if filepath:
        file_path_label_2.config(text=f"Выбранный файл: {filepath}")
        with open(filepath, 'r') as file:
            content = file.read()
            encoded_blocks = wrap(content, 2**m)
            binary_blocks = np.array([list(map(int, block)) for block in encoded_blocks])
            decoded_blocks = decode_blocks(binary_blocks, r, m)
            decoded_binary = "".join(["".join(map(str, block)) for block in decoded_blocks])
            decoded_message = binary_to_text(decoded_binary)
            save_file_decode(decoded_message)

def binary_to_text(binary_str):
    d_str = int(binary_str, 2).to_bytes((len(binary_str) + 7) // 8, byteorder='big').decode('utf-8')
    return d_str


r, m, k = 2, 4, 11

root = tk.Tk()
root.title("Кодек Рида-Маллера")
root.geometry("400x400")

label_encode = tk.Label(root, text="Выберите файл для кодирования")
label_encode.pack()

browse_button = tk.Button(root, text="Выбрать", command=browse_file)
browse_button.pack()

file_path_label_1 = tk.Label(root, text="")
file_path_label_1.pack()

label_decode = tk.Label(root, text="Выберите файл для декодирования")
label_decode.pack()

browse_decode_button = tk.Button(root, text="Выбрать", command=decode_file)
browse_decode_button.pack()

file_path_label_2 = tk.Label(root, text="")
file_path_label_2.pack()

root.mainloop()
