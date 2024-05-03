from bs4 import BeautifulSoup
from collections import Counter
import requests
import re
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet

# loads common words to filter later
def read_common_words(file_path):
    with open(file_path, "r") as file:
        common_words = [word.strip() for word in file.readlines()]
    return common_words

common_words = read_common_words("common_words.txt")

wnl = WordNetLemmatizer()
# download some packages for nltk
# nltk.download('punkt')
# nltk.download('wordnet')
# nltk.download('averaged_perceptron_tagger')

# grabs wiki content currently search_term
# search_term has to be exact title since not using api
def get_wiki(search_term):
    url = "https://en.wikipedia.org/wiki/" + search_term
    wiki = requests.get(url)
    soup = BeautifulSoup(wiki.text, "html.parser")
    wiki_text = soup.stripped_strings
    return wiki_text

# takes the stripped_string from beautiful soup 
# for each in array: 'sents' and tokenize
def tokenize_sents(sents):
    tokenized_sents = []
    for sent in sents:
        # Tokenize the sentence for nltk
        tokens = word_tokenize(sent)  
         # Append the list of tokens to token_sents
        tokenized_sents.append(tokens) 
    return tokenized_sents

# helper function for lemmantize_list()
# converts pos_tag from the default to wordnet 
def pos_tagger(nltk_tag):
    if nltk_tag.startswith("J"):
        return wordnet.ADJ
    elif nltk_tag.startswith("V"):
        return wordnet.VERB
    elif nltk_tag.startswith("N"):
        return wordnet.NOUN
    elif nltk_tag.startswith("R"):
        return wordnet.ADV
    else:
        return None

# tag the sentences
def tag_list(stringList):
    return nltk.pos_tag_sents(stringList)

# after all the tagging you end up with list(list(tuple))
# function just extracts it for counter
def extract_tuples(data):
    extracted_tuples = []
    for sublist in data:
        for word, pos_tag in sublist:
            extracted_tuples.append((word, pos_tag))
    return extracted_tuples


# lemmatize_list so somewhat similar words are treated
# helps with removing common word and counting for later
# common words taken out and punctuation
def lemmatize_list(stringList):
    lemmatized_list = []
    # Unpack word and POS tag
    for word, pos_tag in stringList:  
        pos = pos_tagger(pos_tag)  
        if (pos) and (not (re.match(r"[^\w\s]", word))): 
            if len(word) > 3:
                if pos == 'N':
                    lemmatized_list.append((word, pos))
                else:
                    lmt_word = wnl.lemmatize(word.lower(), pos)  
                    if lmt_word not in common_words:
                        lemmatized_list.append((lmt_word, pos))
    return lemmatized_list

# organize words by their tags before madlibs
def organize_words(occur_list):
    org_list = {}  # Dictionary to store organized words
    for occur in occur_list:
        word_set = occur[0]
        word = word_set[0]
        tag = word_set[1]
        if tag in org_list:
            org_list[tag].append(word)
        else:
            org_list[tag] = [word]
    return org_list

# retrieving all the words for the madlibs and sentence
def grab_words(tags_dict, sentence):
    # counters to keep track of words chosen from tags_dict
    a_counter = 0
    v_counter = 0
    n_counter = 0
    r_counter = 0

    sentence_list = sentence.split()
    replaced_sentence = []

    # iterate through each word in the sentence
    for word in sentence_list:
        # check if the word is a placeholder for a tag
        if word == "[a]":
            if "a" in tags_dict:
                # wraps around just in runs out
                replaced_sentence.append(
                    tags_dict["a"][a_counter % len(tags_dict["a"])]
                )
                a_counter += 1
        elif word == "[v]":
            if "v" in tags_dict:
                replaced_sentence.append(
                    tags_dict["v"][v_counter % len(tags_dict["v"])]
                )
                v_counter += 1
        elif word == "[n]":
            if "n" in tags_dict:
                replaced_sentence.append(
                    tags_dict["n"][n_counter % len(tags_dict["n"])]
                )
                n_counter += 1
        elif word == "[r]":
            if "r" in tags_dict:
                replaced_sentence.append(
                    tags_dict["r"][r_counter % len(tags_dict["r"])]
                )
                r_counter += 1
        else:
            replaced_sentence.append(word)

    # join the replaced words to form the new sentence
    new_sentence = " ".join(replaced_sentence)
    print(new_sentence)


def main():
    # replace Pokemon_Go with title you want
    wiki_content = get_wiki("Linear_Programming")
    word_tokens = tokenize_sents(wiki_content)
    tagged_words = tag_list(word_tokens)
    extract_tag = extract_tuples(tagged_words)
    lmt_words = lemmatize_list(extract_tag)
    counter = Counter(lmt_words)
    # 20 is the cutoff the most common occuring words
    most_occur = counter.most_common(20)
    tags_dict = organize_words(most_occur)
    print(most_occur)
    # replace the string with the sentence you want
    # [n] for noun [v] for verb etc... 
    grab_words(tags_dict, "My favorite [a] [n] is the one that can [v] [n] the best ")
    
main()
