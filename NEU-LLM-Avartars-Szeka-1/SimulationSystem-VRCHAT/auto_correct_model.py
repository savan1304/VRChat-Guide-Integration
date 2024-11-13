# Summary of the current changes as part of integration effort:
#  No changes needed for auto_correct_model.py
    # The entire auto_correct function as it helps improve input text quality

from spellchecker import SpellChecker


def auto_correct(sentence):
    spell = SpellChecker()
    
    # integration effort
    spell.word_frequency.load_words(['VRChat', 'avatar', 'world', 'instance', 'portal'])


    # Detect potentially misspelled words
    misspelled = spell.unknown(sentence.split())

    corrected_words = []
    for word in sentence.split():
        if word in misspelled:
            # Replace the word with its correction
            corrected_words.append(spell.correction(word))
        else:
            # Keep the original word
            corrected_words.append(word)

    # Join the words to form the corrected sentence
    corrected_sentence = ' '.join(corrected_words)

    return corrected_sentence

