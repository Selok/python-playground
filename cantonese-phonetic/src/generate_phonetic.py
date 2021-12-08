import os
import logging.config
import codecs


from algorithm._phonetic import generate_dictionary

log = logging.getLogger(__name__)
root_dir = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..'))

if __name__ == "__main__":
    entity_path = os.path.abspath(
        os.path.join(root_dir, 'data', 'phonetic', 'ypzdiao.txt')
    )
    variant_path = os.path.abspath(
        os.path.join(root_dir, 'data', 'phonetic', 'variant.txt')
    )
    save_path = os.path.abspath(
        os.path.join(root_dir, 'model', 'phonetic', 'ypzdiao.pkl')
    )

    dictionary = {}
    with codecs.open(entity_path, encoding="utf-8-sig") as f:
        for line in f:
            sources = line.strip().split(',')
            if len(sources) != 3:
                print(line)
                continue
            c = sources[1].strip()
            phonetic = list(
                map(str.strip, sources[2].strip('" ').split('/')))
            if c in dictionary:
                phonetic = list(set().union(dictionary[c], phonetic))
            dictionary[c] = phonetic

    with codecs.open(variant_path, encoding="utf-8-sig") as f:
        for line in f:
            sources = line.strip().split(',')
            if len(sources) != 3:
                print(line)
                continue
            c = sources[1].strip()
            phonetic = list(
                map(str.strip, sources[2].strip('" ').split('/')))
            if c in dictionary:
                phonetic = list(set().union(dictionary[c], phonetic))
            dictionary[c] = phonetic

    generate_dictionary(dictionary, save_path)
    print("done")
