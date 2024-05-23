import sys
import numpy as np
from scipy.io import wavfile


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
    assert len(sys.argv) == 4

    cmd = sys.argv[1].lower()

    if cmd == "-e" or cmd == "encode":
        sample_rate, data = wavfile.read(sys.argv[2])
        encoded_data = encode(data)
        wavfile.write(sys.argv[3], sample_rate, encoded_data)

    elif cmd == "-d" or cmd == "decode":
        sample_rate, data = wavfile.read(sys.argv[2])
        decoded_data = decode(data)
        wavfile.write(sys.argv[3], sample_rate, decoded_data)

    else:
        print("Invalid command passed to function")
