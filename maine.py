import getNewBoard
from textwrap import wrap

if __name__ == '__main__':
    startBoard =   [["rw","nw","bw","qw","kw","bw","nw","rw"],
                    ["pw","pw","pw","pw","pw","pw","pw","pw"],
                    ["--","--","--","--","--","--","--","--"],
                    ["--","--","--","--","--","--","--","--"],
                    ["--","--","--","--","--","--","--","--"],
                    ["--","--","--","--","--","--","--","--"],
                    ["pb","pb","pb","pb","pb","pb","pb","pb"],
                    ["rb","nb","bb","kb","qb","bb","nb","rb"]]
    
    nouveauxMoves = getNewBoard.getMoves(startBoard,wrap("0w21b0", 3))