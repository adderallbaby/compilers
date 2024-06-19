import regex

ident_pattern = r'(?<!`)\b(?!where\b)\p{L}[\p{L}0-9]*(?<!`)'

# keyword_pattern = "where|->|=>"
# op_pattern = "(?!--)[[ !#$%&*+.\/<=>?@\\^|~ -]+"
# op_pattern = "(?!--?>|=>)[ !#$%&*+.\/<?@\\^|~ -]+"
op_pattern = r'(?!--)([[!#$%&*+.\/<=>?@\\^|~-] ?)+'
# op_pattern = "(?!--)[[!#$%&*+.\/<=>?@\\^|~ -]+"
# op_pattern = "(?!.*(?:->|=\\?))[ !#$%&*+.\/<=>?@\\^|~ -]+
one_line_comment = r'(?<![!#$%&*+.\/<=>?@\\^|~]\s)--.*'
another_op = r'`\\p{L}[\\p{L}0-9]*`'
kwarrow = r'(?<![!#$%&*+.\/<=>?@\\^|~]\s)\b *-> *\b(?![!#$%&*+.\/<=>?@\\^|~]\s)'
kwfollows = r'(?<![!#$%&*+.\/<=>?@\\^|~]\s)\b *=> *\b(?![!#$%&*+.\/<=>?@\\^|~]\s)'
kw = f'{kwarrow}|{kwfollows}|where'
number_pattern = r'(?<=\s|^)\d+'
kwc = regex.compile(kw)
# keyword_pattern = f'{kwwhere}|{kwarrow}|{kwfollows}'
# print(regex.findall(one_line_comment, test2))


f = open('input.txt', 'r')
multi_line_comment_start = '{-'
multi_line_comment_end = '-}'
inside_comment = False
numline = 0
for line in f:

    numline += 1
    end_of_comment = regex.search('}-', line[::-1])
    if end_of_comment and inside_comment:
        inside_comment = False
        # print('found it;')
        line = line[end_of_comment.span()[0]+1:]
    elif end_of_comment and not inside_comment:
        print('syntax error',
              f'({numline}, {(end_of_comment.span()[0])})')
        line = line[end_of_comment.span()[0]+1:]

    if not inside_comment:

        # print(line, end= '\n')
        olc_match = regex.search(one_line_comment, line)
        end = 1000000
        if olc_match:
            print('ONE LINE COMMENT', f'{numline}:', olc_match.group())

            end = olc_match.span()[0]
            line = line[0:end]
        mlc_match = regex.search(multi_line_comment_start, line)
        if mlc_match and mlc_match.span()[0] < end:
            print('MULTI LINE COMMENT', f'{numline}:', mlc_match.group())

            inside_comment = True
            end = mlc_match.span()[0]
            line = line[0:end]

        # idents = regex.findall(ident_pattern, line)
        # print(line, end = '_________\n')
        keyword_match = regex.finditer(kwc, line)
        # line += line[:-1] + ' b']

        # print(line)
        # if line.endswith('')
        splitted = line.split()
        for word in splitted:
            # print(word, 'word')
            if (not list(regex.finditer(kwc, word))) \
                and (not list(regex.finditer(op_pattern, word))) \
                and (not list(regex.finditer(another_op, word))) \
                and (not list(regex.finditer(ident_pattern, word))
                     and (not list(regex.finditer(number_pattern, line)))):
                print('syntax error', f'({numline}, {line.index(word)})')

        if keyword_match:
            for kw in list(keyword_match):
                print('KEYWORD', f'{numline, kw.span()[0]}:', kw.group())
        # line = line[:-2]
        ops_match = regex.finditer(op_pattern, line)
        if ops_match:
            for ow in list(ops_match):
                if not regex.fullmatch(r' *-> *', ow.group()) \
                        and not regex.fullmatch(r' *=> *', ow.group()):
                    print('OPERATOR', f'{numline, ow.span()[0]}:', ow.group())
        ops_match2 = regex.finditer(another_op, line)
        if ops_match2:
            for ow in list(ops_match2):
                print('OPERATOR', f'{numline, ow.span()[0]}:', ow.group())
        idents_match = regex.finditer(ident_pattern, line)
        if idents_match:
            for iw in list(idents_match):
                print('IDENT', f'{numline, iw.span()[0]}:', iw.group())
        nums_match = regex.finditer(number_pattern, line)
        if nums_match:
            for iw in list(nums_match):
                print('NUMBER', f'{numline, iw.span()[0]}:', iw.group())
