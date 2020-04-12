def gen_convasations():
    lines = open('raw_data/sale_lines.txt', encoding='utf-8', errors='ignore').read().split('\n')
    f = open('raw_data/gen.txt', "w")
    metadata = "u0 +++$+++ u2 +++$+++ m0 +++$+++ "
    idx_conv = ""
    s_bracket = "["
    e_bracket = "]"
    cur = ""
    for line in lines:
        if line.startswith("****"):
            continue
        if len(line.strip()) == 0:
            continue
        _line = line.split(' +++$+++ ')

        if idx_conv == _line[1]:
            cur = cur + "," + "'" + _line[0] + "'"
        elif len(idx_conv) == 0:
            cur = cur + s_bracket + "'" + _line[0] + "'"
            idx_conv = _line[1]
            pass
        else:
            data = metadata + cur + e_bracket + "\n"
            f.write(data)
            cur = s_bracket + "'" + _line[0] + "'"
            idx_conv = _line[1]

    f.close()

if __name__ == "__main__":
    gen_convasations()
