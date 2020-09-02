def quoted(x, n=200):
    '''Add quotation marks around `x`, and take only the first `n` letters.'''
    return f'"{str(x)[:n]}"'
