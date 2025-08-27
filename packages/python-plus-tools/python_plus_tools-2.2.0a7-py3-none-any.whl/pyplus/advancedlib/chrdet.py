import chrdet

def get_encoding(file):
    with open(file, 'rb') as f:
        result = chrdet.detect(f.read())
    return result['encoding']