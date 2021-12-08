import os
from algorithm import load_phonetic_dictionary, is_phonetic_similar, is_phonetic_included

def main(a: str, b: str):
    similarity = is_phonetic_similar(a, b)
    print(f"similarity: {similarity}")
    phonetic_included = is_phonetic_included(a, b)
    print(f"phonetic_included: {phonetic_included}")
    

if __name__ == "__main__":
    phonetic_data = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        'ypzdiao.pkl'
    ))
    load_phonetic_dictionary(phonetic_data)

    main("村", "邨")