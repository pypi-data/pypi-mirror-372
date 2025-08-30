import re

def chopify(text: str, prefix: str = "ch") -> str:
    """
    Converts a word or sentence to its "chopped" version by replacing the
    initial consonant(s) of each word with a given prefix.

    Examples:
    - poop -> choop
    - unc -> chunc
    - hamster -> chamster
    - hello world -> chello chorld

    Parameters:
        text (str): The text to chopify (word or sentence).
        prefix (str): The prefix to use for chopping. Defaults to "ch".

    Returns:
        str: The chopified text.
    """
    if not text:
        return text

    words = re.split(r'(\s+)', text)
    chopped_words = [_chopify_word(word, prefix) for word in words]
    return "".join(chopped_words)

def _chopify_word(word: str, prefix: str) -> str:
    """Chopifies a single word."""
    if not word.strip():
        return word

    original_word = word
    is_capitalized = original_word and original_word[0].isupper() and not all(c.isupper() for c in original_word)
    is_all_caps = original_word and all(c.isupper() for c in original_word)

    word_lower = original_word.lower()
    vowels = "aeiouy"

    if not word_lower:
        return ""

    chopped_word = ""
    if word_lower[0] in vowels:
        chopped_word = prefix.lower() + word_lower
    else:
        for i, char in enumerate(word_lower):
            if char in vowels:
                chopped_word = prefix.lower() + word_lower[i:]
                break
        else: # no vowels
            chopped_word = prefix.lower() + word_lower

    if is_all_caps:
        return chopped_word.upper()
    if is_capitalized:
        return chopped_word.capitalize()
    else:
        return chopped_word

def is_chopified(word: str, prefix: str = "ch") -> bool:
    """
    Checks if a word is in its "chopified" form.

    Examples:
    - is_chopified("choop") -> True
    - is_chopified("poop") -> False

    Parameters:
        word (str): The word to check.
        prefix (str): The prefix to check for. Defaults to "ch".

    Returns:
        bool: True if the word is chopified, False otherwise.
    """
    return word.lower().startswith(prefix.lower())
