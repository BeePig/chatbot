

def gen_line():
    books = open('raw_data/tensach.txt', encoding='utf-8', errors='ignore').read().split('\n')
    f = open('raw_data/gen.txt',"w")

    Lindex = 269
    Uindex = 129
    for book in books:
        metadata = gen_metadata(Lindex,Uindex)
        q = "ai là tác giả cuốn " + book + "\n"
        line_q = metadata + q
        f.write(line_q)
        a = "tác giả của cuốn sách là \n"
        Lindex = Lindex + 1
        metadata = gen_metadata(Lindex ,Uindex)
        line_a = metadata + a
        f.write(line_a)
        Lindex = Lindex + 1
        Uindex = Uindex +1
    f.close()


def gen_metadata(Lindex, Uindex):
    spl = "+++$+++"
    return "L" + str(Lindex) + " "+spl+ " "+"u" +str(Uindex) + " " + spl + " " +"m0" + " "+spl + " " + "BIANCA" + " "+spl + " "

if __name__ == "__main__":
    gen_line()