import random
#import nltk
#from nltk.corpus import wordnet as wn
import openai
import os
#from nltk.probability import FreqDist

# removed nltk due to latency
#nltk.download('webtext')
#nltk.download('averaged_perceptron_tagger')
#nltk.download('punkt')
from collections import Counter
import json
import unicodedata

#setup logger
from modules import logger
from modules.logger import setup_logger

#start logger
logger = setup_logger("poem_gen")
logger.debug("Logger is set up and running.")

openai.api_key = os.environ["OPENAI_API_KEY"]

# create the first input to create the base poem
def gen_creative_prompt_api(entropy):
            completion = openai.ChatCompletion.create(
                model="gpt-4-1106-preview",
                messages=[
                    {"role": "system", "content": "You generate random words. Only output the words themselves, nothing extraneous. First, I want you to pick 50 randomly, and then randomly pick 5 of those random 50. Only output the final 5 words."},
                    {"role": "user", "content": "Generate up to 5 random words from the English language. These should be randomly selected between nouns, verbs, adjectives, adverbs, pronouns, etc."},
                ],
                max_tokens=500,
                temperature=(entropy * 2),
                # temp is set to go between 0.8 and 2, this linear function maps randomness_factor to temp 
                #temperature=0.8 + (randomness_factor * (2 - 0.8))
                #temperature=1.0
            )
            
            if completion['choices'][0]['message']['role'] == "assistant":
                creative_prompt = completion['choices'][0]['message']['content'].strip()
            else:
                creative_prompt_syscontent = completion['system'].strip()  # put into a var for later use 

            #logger.info(f"gen_creative_prompt Prompt tokens: {completion['usage']['prompt_tokens']}")
            #logger.info(f"gen_creative_prompt Completion tokens: {completion['usage']['completion_tokens']}")
            #logger.info(f"gen_creative_prompt Total tokens: {completion['usage']['total_tokens']}")

            logger.info(f"gen_creative_prompt_api words are:\n{creative_prompt}")
            return creative_prompt

def get_abstract_concept():
    abstract_concepts = {
        "adventure": "positive",
        "affection": "positive",
        "ambition": "positive",
        "amusement": "positive",
        "anguish": "negative",
        "anxiety": "negative",
        "apathy": "negative",
        "awe": "positive",
        "balance": "positive",
        "beauty": "positive",
        "belonging": "positive",
        "bitterness": "negative",
        "bliss": "positive",
        "bravery": "positive",
        "camaraderie": "positive",
        "chaos": "negative",
        "charm": "positive",
        "cheerfulness": "positive",
        "compassion": "positive",
        "contentment": "positive",
        "courage": "positive",
        "curiosity": "positive",
        "delight": "positive",
        "desolation": "negative",
        "despair": "negative",
        "destiny": "neutral",
        "determination": "positive",
        "dignity": "positive",
        "discipline": "positive",
        "discontent": "negative",
        "dishonesty": "negative",
        "divinity": "positive",
        "doubt": "negative",
        "dreams": "positive",
        "ecstasy": "positive",
        "elegance": "positive",
        "embarrassment": "negative",
        "empathy": "positive",
        "empowerment": "positive",
        "endurance": "positive",
        "enlightenment": "positive",
        "envy": "negative",
        "equality": "positive",
        "eternity": "neutral",
        "euphoria": "positive",
        "faith": "positive",
        "fear": "negative",
        "forgiveness": "positive",
        "freedom": "positive",
        "frolic": "positive",
        "frustration": "negative",
        "gaiety": "positive",
        "giddiness": "positive",
        "glee": "positive",
        "gleefulness": "positive",
        "grace": "positive",
        "gratitude": "positive",
        "grief": "negative",
        "guilt": "negative",
        "harmony": "positive",
        "hate": "negative",
        "hope": "positive",
        "honor": "positive",
        "humiliation": "negative",
        "humor": "positive",
        "ignorance": "negative",
        "imagination": "positive",
        "ingenuity": "positive",
        "innocence": "positive",
        "integrity": "positive",
        "injustice": "negative",
        "jealousy": "negative",
        "jollity": "positive",
        "joviality": "positive",
        "joy": "positive",
        "justice": "positive",
        "knowledge": "positive",
        "liberty": "positive",
        "lightheartedness": "positive",
        "loneliness": "negative",
        "liveliness": "positive",
        "love": "positive",
        "loyalty": "positive",
        "malice": "negative",
        "memory": "neutral",
        "merriment": "positive",
        "mirth": "positive",
        "mischief": "neutral",
        "misery": "negative",
        "morality": "positive",
        "mortality": "negative",
        "mundanity": "neutral",
        "mystery": "neutral",
        "nobility": "positive",
        "optimism": "positive",
        "pain": "negative",
        "passion": "positive",
        "patience": "positive",
        "pep": "positive",
        "perseverance": "positive",
        "playfulness": "positive",
        "pleasure": "positive",
        "prejudice": "negative",
        "pride": "positive",
        "prosperity": "positive",
        "quaintness": "positive",
        "radiance": "positive",
        "redemption": "positive",
        "regret": "negative",
        "resentment": "negative",
        "respect": "positive",
        "reverence": "positive",
        "romance": "positive",
        "sadness": "negative",
        "satisfaction": "positive",
        "sensuality": "positive",
        "serenity": "positive",
        "shame": "negative",
        "silliness": "neutral",
        "solitude": "neutral",
        "sorrow": "negative",
        "sparkle": "positive",
        "spirituality": "positive",
        "sympathy": "positive",
        "tenacity": "positive",
        "time": "neutral",
        "torment": "negative",
        "tranquility": "positive",
        "transcendence": "positive",
        "transience": "neutral",
        "truth": "positive",
        "unity": "positive",
        "valor": "positive",
        "vigor": "positive",
        "vivacity": "positive",
        "whimsy": "positive",
        "wisdom": "positive",
        "wonder": "positive",
        "worthlessness": "negative",
        "wit": "positive",
        "yearning": "neutral",
        "zest": "positive"
    }
    # Pick a random abstract_concept
    selected_abstract_concept = random.choice(list(abstract_concepts.keys()))
    # Choose randomly from the list of original word + synonyms
    return selected_abstract_concept

def get_lang_device():
    language_devices = {
        "metaphor": "a figure of speech in which a word or phrase is applied to an object or action to which it is not literally applicable.",
        "simile": "a figure of speech involving the comparison of one thing with another thing of a different kind, used to make a description more emphatic or vivid.",
        "personification": "the attribution of a personal nature or human characteristics to something non-human, or the representation of an abstract quality in human form.",
        "allegory": "a story, poem, or picture that can be interpreted to reveal a hidden meaning, typically a moral or political one.",
        "idiom": "a group of words established by usage as having a meaning not deducible from those of the individual words (e.g., rain cats and dogs, see the light).",
        "anachronism": "a thing belonging or appropriate to a period other than that in which it exists, especially a thing that is conspicuously old-fashioned.",
        "hyperbole": "exaggerated statements or claims not meant to be taken literally.",
        "irony": "the expression of one's meaning by using language that normally signifies the opposite, typically for humorous or emphatic effect.",
        "oxymoron": "a figure of speech in which apparently contradictory terms appear in conjunction (e.g., bittersweet, living death).",
        "synecdoche": "a figure of speech in which a part is made to represent the whole or vice versa.",
        "alliteration": "the occurrence of the same letter or sound at the beginning of adjacent or closely connected words.",
        "assonance": "the repetition of the sound of a vowel or diphthong in non-rhyming stressed syllables.",
        "consonance": "the recurrence of similar sounds, especially consonants, in close proximity.",
        "enjambment": "the continuation of a sentence without a pause beyond the end of a line, couplet, or stanza.",
        "caesura": "a break between words within a metrical foot, a pause near the middle of a line."
}

    # Pick a random language device
    selected_lang_device = random.choice(list(language_devices.keys()))
    return selected_lang_device

# temporarily disabling use of this function due to latency
def gen_random_words(randomness_factor=1):

    # Get the list of file IDs in the web text corpus.
    fileids = nltk.corpus.webtext.fileids()

    # Randomly select a file ID.
    random_fileid = random.choice(fileids)

    # get up to 1500 characters of raw text from the file
    raw_text = nltk.corpus.webtext.raw(random_fileid)[:1500]

    # log the number of words
    logger.info("Number of words: {}".format(len(raw_text.split())))

    # Tokenize the raw text.
    tokens = nltk.word_tokenize(raw_text)

    # Tag the tokens with their parts of speech.
    tagged = nltk.pos_tag(tokens)

    # Filter to get only the nouns (NN), adjectives (JJ), adverbs (RB), 
    # personal pronouns (PRP), possessive pronouns (PRP$), and coordinating conjunctions (CC).
    nouns = [word for word, pos in tagged if pos in ['NN', 'NNS'] and word.isalpha()]
    adjectives = [word for word, pos in tagged if pos in ['JJ', 'JJR', 'JJS'] and word.isalpha()]
    adverbs = [word for word, pos in tagged if pos in ['RB', 'RBR', 'RBS'] and word.isalpha()]
    pronouns = [word for word, pos in tagged if pos in ['PRP', 'PRP$'] and word.isalpha()]
    conjunctions = [word for word, pos in tagged if pos == 'CC' and word.isalpha()]

    # Select a random word from each category.
    random_noun = random.choice(nouns)
    random_adj = random.choice(adjectives)
    random_adv = random.choice(adverbs)
    random_pronoun = random.choice(pronouns)
    random_conjunction = random.choice(conjunctions)

  # Combine all categories into a single list.
    all_words = [random_noun, random_adj, random_adv, random_pronoun, random_conjunction]

    # Control the total number of words selected based on the randomness_factor
    #num_words = int(1 + 4 * randomness_factor)  # This will give a value between 1 and 5

    # Select random words from the entire list, the number of words specificed by randomness_factor
    #random_webtext_words = random.choices(all_words, k=num_words)

    # Combine the words into a single string.
    #webtext_words = ' '.join(random_webtext_words)
    webtext_words = ' '.join(all_words)
    logger.info(f"webtext words are: {webtext_words}")

    return webtext_words