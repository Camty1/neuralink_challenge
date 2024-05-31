import sys
import numpy as np
from scipy.io import wavfile


class Node:
    def __init__(self, name=None, count=None):
        self.left = None
        self.right = None
        self.name = name
        self.count = count

    def __str__(self):
        return f"({self.name} : {self.count}, [{self.left}], [{self.right}])"


def huffman_tree(count_dict):

    queue = [Node(key, value) for key, value in count_dict.items()]

    while len(queue) > 1:
        queue = sorted(queue, key=lambda x: x.count, reverse=True)
        a = queue.pop()
        b = queue.pop()

        ab = Node(a.name + b.name, a.count + b.count)
        ab.left = a
        ab.right = b

        queue.append(ab)
    return queue[0]


def populate_tree_codes(node, codes, prefix):
    if node.left == None and node.right == None:
        codes[node.name] = prefix
    else:
        populate_tree_codes(node.left, codes, prefix + "0")
        populate_tree_codes(node.right, codes, prefix + "1")


def encode(data: np.ndarray) -> np.ndarray:
    num_repetitions = 240
    data_str = "".join([format(x, "16b") for x in data])
    initial_len = len(data_str)
    starting_ascii = 58
    encode_dict = {}
    decode_dict = {}
    for r in range(num_repetitions):
        repetition_dict = {}
        for i in range(len(data_str) - 1):
            if data_str[i : i + 2] in repetition_dict:
                repetition_dict[data_str[i : i + 2]] += 1
            else:
                repetition_dict[data_str[i : i + 2]] = 1

        max_rep = max(repetition_dict.items(), key=lambda x: x[1])
        value = max_rep[0]

        key = chr(starting_ascii + r)
        encode_dict[value] = key
        decode_dict[key] = value

        new_str = ""
        flag = False
        for i in range(len(data_str)):
            if flag:
                if data_str[i] == value[1]:
                    new_str += key
                else:
                    new_str += data_str[i - 1 : i + 1]
                flag = False
            else:
                if data_str[i] == value[0]:
                    flag = True
                else:
                    new_str += data_str[i]

        data_str = new_str
        print(r + 1, len(data_str))

    final_len = len(data_str)
    print(f"Compression Ratio: {initial_len/final_len:.2f}")

    return data


def decode(data: np.ndarray) -> np.ndarray:
    return data


if __name__ == "__main__":

    assert len(sys.argv) >= 2

    cmd = sys.argv[1].lower()

    if cmd == "-e" or cmd == "encode":
        assert len(sys.argv) == 4
        sample_rate, data = wavfile.read(sys.argv[2])
        encoded_data = encode(data)
        wavfile.write(sys.argv[3], sample_rate, encoded_data)

    elif cmd == "-d" or cmd == "decode":
        assert len(sys.argv) == 4
        sample_rate, data = wavfile.read(sys.argv[2])
        decoded_data = decode(data)
        wavfile.write(sys.argv[3], sample_rate, decoded_data)

    elif cmd == "-t" or cmd == "test":
        sample_rate, data = wavfile.read("ff970660-0ffd-461f-93de-379e95cd784a.wav")

        unique_vals = np.unique(data)
        bits_needed = np.ceil(np.log(len(unique_vals)) / np.log(2))
        print(bits_needed)
        unique_dict = {}
        inv_unique_dict = {}
        for i, val in enumerate(unique_vals):
            unique_dict[val] = i
            inv_unique_dict[i] = val

        unique_data = np.array([unique_dict[val] for val in data], dtype="int16")
        print(unique_data.dtype)
        data = unique_data.tobytes()
        count = {}
        for datum in data:
            if datum in count:
                count[datum] += 1
            else:
                count[datum] = 1
        # data = "".join(
        #     [
        #         str(x)
        #         for x in np.concatenate(
        #             [
        #                 np.zeros(15, dtype=int),
        #                 np.ones(7, dtype=int),
        #                 2 * np.ones(6, dtype=int),
        #                 3 * np.ones(6, dtype=int),
        #                 4 * np.ones(5, dtype=int),
        #             ]
        #         )
        #     ]
        # )

        # count = {}
        # for datum in data:
        #     if datum in count:
        #         count[datum] += 1
        #     else:
        #         count[datum] = 1

        tree = huffman_tree(count)
        tree_codes = {}
        populate_tree_codes(tree, tree_codes, "")

        output = "".join([tree_codes[datum] for datum in data])
        print((len(data) * 8) / len(output))

    else:
        print("Invalid command passed to function")
