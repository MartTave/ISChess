def getMoves(board,pos,ennemies):
    case = board[pos[0]][pos[1]]
    piecette = case[0]
    couleur = case[1]
    newBoard = []
    outBoards = []

    match piecette:
        case 'p':
            print("ESTRE PION")
            if board[pos[0]-1][pos[1]][1] == '': #si la case au dessus est vide
                newBoard = board.clone()
                newBoard[pos[0]-1][pos[1]] = board[pos[0]-1][pos[1]][1]
                newBoard[pos[0]][pos[1]] = ""
                outBoards.append(newBoard)

            if board[pos[0]-1][pos[1]-1][1] == '': #si la case au dessus est vide   


        case 'r':
            print("ESTRE TOURRE")

        case 'n':
            print("ESTRE CHEVALIN")

        case 'b':
            print("ESTRE FOSU")

        case 'k':
            print("ESTRE ROA")

        case 'q':
            print("ESTRE RAINE")