def reverse(string):
    return string[::-1]

def is_palindrome(string):
    reverse = string[::-1]
    if reverse == string:
        return True
    else:
        return False

def to_binary(string):
    return " ".join(format(ord(c), "08b") for c in string)

def count_characters(string)
    return len(string)