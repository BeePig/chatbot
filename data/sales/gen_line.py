

def gen_line():
    books = open('raw_data/theloaixs.txt', encoding='utf-8', errors='ignore').read().split('\n')
    f = open('raw_data/gen.txt',"w")

    Lindex = 307
    Uindex = 149
    for book in books:
        metadata = gen_metadata(Lindex,Uindex)
        q = "mình muốn tìm tác phẩm thuộc thể loại " + book + "\n"
        line_q = metadata + q
        f.write(line_q)
        a = "thể loại này có các tác phẩm như \n"
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