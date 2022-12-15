def get_about(fname=None, about=None):
    text_list = []
    if not fname:
        for item in about:
            text = item.text
            text = text.replace(u'\xa0', u' ')
            text_list.append(text)
        fname = 'About.txt'
        with open(fname, 'w') as f:
            for text in text_list:
                f.write(f"{text}\n")
    else:
        with open(fname, 'r') as f:
            for line in f:
                text_list.append(line.strip())
    return text_list