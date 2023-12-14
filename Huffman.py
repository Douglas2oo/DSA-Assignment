import sys
import os

sys.setrecursionlimit(1000000)  # Modify the limit for real-time compression of large files

# Define the node class for the Huffman tree
class HuffmanNode(object):

    def __init__(self, value=None, left=None, right=None, father=None):
        self.value = value
        self.left = left
        self.right = right
        self.father = father

    def build_father(left, right):
        n = HuffmanNode(value=left.value + right.value, left=left, right=right)
        left.father = right.father = n
        return n

    def encode(n):
        if n.father is None:
            return b''
        if n.father.left == n:
            return HuffmanNode.encode(n.father) + b'0'
        else:
            return HuffmanNode.encode(n.father) + b'1'

# Huffman tree construction
def build_tree(nodes_list):
    if len(nodes_list) == 1:
        return nodes_list
    sorts = sorted(nodes_list, key=lambda x: x.value, reverse=False)
    n = HuffmanNode.build_father(sorts[0], sorts[1])
    sorts.pop(0)
    sorts.pop(0)
    sorts.append(n)
    return build_tree(sorts)

def encode(echo):
    for x in huffman_nodes.keys():
        encoded_symbols[x] = HuffmanNode.encode(huffman_nodes[x])
        if echo:
            print(x)
            print(encoded_symbols[x])

def encodefile(file_path):
    print("Starting encode...")
    f = open(file_path, "rb")
    byte_width = 1
    i = 0
    f.seek(0, 2)
    count = f.tell() / byte_width
    print(count)
    nodes = []
    buff = [b''] * int(count)
    f.seek(0)
    while i < count:
        buff[i] = f.read(byte_width)
        if symbol_counts.get(buff[i], -1) == -1:
            symbol_counts[buff[i]] = 0
        symbol_counts[buff[i]] += 1
        i += 1
    print("Read OK")
    print(symbol_counts)
    for x in symbol_counts.keys():
        huffman_nodes[x] = HuffmanNode(symbol_counts[x])
        nodes.append(huffman_nodes[x])
    f.close()
    tree = build_tree(nodes)
    encode(False)
    print("Encode OK")

    head = sorted(symbol_counts.items(), key=lambda x: x[1], reverse=True)
    frequency_width = 1
    print("head:", head[0][1])
    if head[0][1] > 255:
        frequency_width = 2
        if head[0][1] > 65535:
            frequency_width = 3
            if head[0][1] > 16777215:
                frequency_width = 4
    print("frequency_width:", frequency_width)
    i = 0
    raw = 0b1
    last = 0
    name = file_path.split('.')
    o = open(name[0] + ".ys", 'wb')
    o.write(int.to_bytes(len(encoded_symbols), 2, byteorder='big'))
    o.write(int.to_bytes(frequency_width, 1, byteorder='big'))
    for x in encoded_symbols.keys():
        o.write(x)
        o.write(int.to_bytes(symbol_counts[x], frequency_width, byteorder='big'))

    print('head OK')
    while i < count:
        for x in encoded_symbols[buff[i]]:
            raw = raw << 1
            if x == 49:
                raw |= 1
            if raw.bit_length() == 9:
                raw &= ~(1 << 8)
                o.write(int.to_bytes(raw, 1, byteorder='big'))
                o.flush()
                raw = 0b1
                process = int(i / len(buff) * 100)
                if process > last:
                    print("encode:", process, '%')
                    last = process
        i += 1

    if raw.bit_length() > 1:
        raw = raw << (8 - (raw.bit_length() - 1))
        raw &= ~(1 << raw.bit_length() - 1)
        o.write(int.to_bytes(raw, 1, byteorder='big'))
    o.close()
    print("File encode successful.")

def decodefile(input_file_path, output_file_path):
    print("Starting decode...")
    count = 0
    raw = 0
    last = 0
    f = open(input_file_path, 'rb')
    o = open(output_file_path, 'wb')
    f.seek(0, 2)
    eof = f.tell()
    f.seek(0)
    count = int.from_bytes(f.read(2), byteorder='big')
    frequency_width = int.from_bytes(f.read(1), byteorder='big')
    i = 0
    de_dict = {}
    while i < count:
        key = f.read(1)
        value = int.from_bytes(f.read(frequency_width), byteorder='big')
        de_dict[key] = value
        i += 1
    for x in de_dict.keys():
        huffman_nodes[x] = HuffmanNode(de_dict[x])
        nodes.append(huffman_nodes[x])
    tree = build_tree(nodes)
    encode(False)
    for x in encoded_symbols.keys():
        decoded_symbols[encoded_symbols[x]] = x
    i = f.tell()
    data = b''
    while i < eof:
        raw = int.from_bytes(f.read(1), byteorder='big')
        i += 1
        j = 8
        while j > 0:
            if (raw >> (j - 1)) & 1 == 1:
                data += b'1'
                raw &= ~(1 << (j - 1))
            else:
                data += b'0'
                raw &= ~(1 << (j - 1))
            if decoded_symbols.get(data, 0) != 0:
                o.write(decoded_symbols[data])
                o.flush()
                data = b''
            j -= 1
        process = int(i / eof * 100)
        if process > last:
            print("decode:", process, '%')
            last = process
        raw = 0

    f.close()
    o.close()
    print("File decode successful.")

if __name__ == '__main__':
    huffman_nodes = {}
    symbol_counts = {}
    encoded_symbols = {}
    nodes = []
    decoded_symbols = {}

    print("Please place the file to be operated on in the same directory as the application before performing the operation.")

    operation = input("1: Compress File\t2: Decompress File\nEnter the operation you want to perform:")

    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

    if operation == '1':
        file_to_compress = input("Enter the file name to compress:")
        file_path = os.path.join(script_dir, file_to_compress)
        encodefile(file_path)
    elif operation == '2':
        file_to_decompress = input("Enter the file name to decompress:")
        output_file_path = input("Enter the output file path after decompression:")
        input_file_path = os.path.join(script_dir, file_to_decompress)
        output_file_path = os.path.join(script_dir, output_file_path)
        decodefile(input_file_path, output_file_path)
    else:
        print("Invalid operation")