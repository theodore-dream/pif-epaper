import nltk
nltk.download('wordnet')
from nltk.corpus import wordnet as wn

def print_synsets(word_type, num_lines=10):
    """Prints a specified number of synsets of a given type."""
    all_synsets = list(wn.all_synsets(word_type))
    for synset in all_synsets[:num_lines]:
        print(synset)

if __name__ == "__main__":
    print("Nouns:")
    print_synsets('n')
    print("\nVerbs:")
    print_synsets('v')
    print("\nAdjectives:")
    print_synsets('a')
    print("\nAdverbs:")
    print_synsets('r')
