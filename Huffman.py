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
        # Set the father node of the left and right nodes to n
        return n

    def encode(n):
        if n.father is None:
            return b''
            # If the node is the root node, the code is empty
        if n.father.left == n:
            return HuffmanNode.encode(n.father) + b'0'
            # If the node is the left child of the father node, the code is 0
        else:
            return HuffmanNode.encode(n.father) + b'1'
            # If the node is the right child of the father node, the code is 1

# Huffman tree construction
def build_tree(nodes_list):
    if len(nodes_list) == 1:
        return nodes_list
    sorts = sorted(nodes_list, key=lambda x: x.value, reverse=False)
    # Sort the nodes in ascending order according to the weight of the nodes
    n = HuffmanNode.build_father(sorts[0], sorts[1])
    # Take the first two nodes as the left and right children of the father node, and the weight of the father node is the sum of the weights of the two nodes
    sorts.pop(0)
    sorts.pop(0)
    sorts.append(n)
    return build_tree(sorts)
    # Recursively construct the Huffman tree until there is only one node left in the list

def encode(echo):
    for x in huffman_nodes.keys():
        encoded_symbols[x] = HuffmanNode.encode(huffman_nodes[x])
        # Encode each node
        if echo:
            print(x)
            print(encoded_symbols[x])

def encodefile(file_path):
    print("Starting encode...")
    f = open(file_path, "rb")
    byte_width = 1
    i = 0
    f.seek(0, 2)
    # Get the size of the file
    count = f.tell() / byte_width
    print("size: "+str(count)+" bytes")
    nodes = []
    buff = [''] * int(count)
    f.seek(0)
    while i < count:
        buff[i] = f.read(byte_width)
        if symbol_counts1.get(buff[i], -1) == -1:
            symbol_counts1[buff[i]] = 0
        symbol_counts1[buff[i]] += 1
        i += 1
    # Read the file and count the number of frequency of each byte
    print("The frequency of each character:")
    print(symbol_counts1)
    for x in symbol_counts1.keys():
        huffman_nodes[x] = HuffmanNode(symbol_counts1[x])
        nodes.append(huffman_nodes[x])
    # Create a node for each byte and add it to the node list
    f.close()
    tree = build_tree(nodes)
    encode(False)
    head = sorted(symbol_counts1.items(), key=lambda x: x[1], reverse=True)
    frequency_width = 1
    if head[0][1] > 255:
        frequency_width = 2
        if head[0][1] > 65535:
            frequency_width = 3
            if head[0][1] > 16777215:
                frequency_width = 4
    # Get the number of bytes required to store the frequency of the most frequent byte
    i = 0
    raw = 0b1
    last = 0
    name = file_path.split('.')
    o = open(name[0] + ".ys", 'wb')
    # Write the file header
    o.write(int.to_bytes(len(encoded_symbols), 2, byteorder='big'))
    o.write(int.to_bytes(frequency_width, 1, byteorder='big'))
    # Write the number of bytes and the number of bytes required to store the frequency
    for x in encoded_symbols.keys():
        o.write(x)
        o.write(int.to_bytes(symbol_counts1[x], frequency_width, byteorder='big'))
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
    # Write the percentage of the encoding process
    if raw.bit_length() > 1:
        raw = raw << (8 - (raw.bit_length() - 1))
        raw &= ~(1 << raw.bit_length() - 1)
        o.write(int.to_bytes(raw, 1, byteorder='big'))
    o.close()
    # Write the remaining bits
    print("File encode successful.")

def decodefile(input_file_path, output_file_path):
    print("Starting decode...")
    count = 0
    raw = 0
    last = 0
    i = 0
    byte_width = 1
    f = open(input_file_path, 'rb')
    o = open(output_file_path, 'wb')
    f.seek(0, 2)
    eof = f.tell()
    f.seek(0)
    count = int.from_bytes(f.read(2), byteorder='big')
    print("size: "+str(count)+" bytes")
    frequency_width = int.from_bytes(f.read(1), byteorder='big')
    i = 0
    de_dict = {}
    while i < count:
        key = f.read(1)
        value = int.from_bytes(f.read(frequency_width), byteorder='big')
        de_dict[key] = value
        i += 1
    # Read the file header and get the dictionary of each byte
    print("Frequency:")
    print(de_dict)
    for x in de_dict.keys():
        huffman_nodes[x] = HuffmanNode(de_dict[x])
        nodes.append(huffman_nodes[x])
    # Create a node for each byte and add it to the node list
    tree = build_tree(nodes)
    encode(False)
    # Create a node for each byte and add it to the node list
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
    # Write the percentage of the decoding process
    f.close()
    o.close()
    print("File decode successful.")

if __name__ == '__main__':
    huffman_nodes = {}
    symbol_counts1 = {}
    symbol_counts2 = {}
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
        output_file_path = input("Enter the output file name after decompression:")
        input_file_path = os.path.join(script_dir, file_to_decompress)
        output_file_path = os.path.join(script_dir, output_file_path)
        decodefile(input_file_path, output_file_path)
    else:
        print("Invalid operation")