import numpy as np

class Player:
    def __init__(self, playerTab):
        self.team = playerTab[0]
        self.color = playerTab[1]
        self.orientation = playerTab[2]

    def playerToString(self):
        return "{},{},{}".format(self.team,self.color,self.orientation)


def getMoves(board,players):
    outBoards = [] #tableau de sortie avec tous les boards
    me = Player(players[0]) #ca c'est moi
    allies = [me] #tableau de players qui contient les alliés
    ennemies = [] #tableau de players qui contient les ennemis
    authorizedChars = ['-'] #tableau avec les chars ou on peut bouger, ce serait chiant d'aller chercher dans ennemies pis faut ajouter les cases vides
    for i in range(1,len(players)):
        #rempli les tableaux d'alliés/ennemis
        if players[i][0] == me.team:
            allies.append(Player(players[i]))
        else:
            newEnnemy = Player(players[i])
            ennemies.append(newEnnemy)
            authorizedChars.append(newEnnemy.color)
    
    #ca va etre du code un peu degeu mais je vois pas comment faire autrement ;-;

    for i in range(0,len(board)): #axe y je crois
        for j in range(0,len(board[0])): #axe x je crois
            #boucle sur chaque case du Board d'entrée
            if board[i][j][1] == me.color:
                #si c'est une piece que je peux bouger
                match board[i][j][0]:
                    case 'p': #piong
                        match me.orientation:
                            case 0:
                                #vers le haut
                                try: #utilisation d'un try pour les problemes d'index?
                                    if board[i-1][j][1] == '-':
                                        bidouilleBoard = np.copy(board)
                                        bidouilleBoard[i][j] = "--"
                                        if(i-1 == 0):
                                            bidouilleBoard[i-1][j] = "{}q".format(me.color)
                                        else:
                                            bidouilleBoard[i-1][j] = "{}p".format(me.color)
                                        outBoards.append(bidouilleBoard)
                                except:
                                    print("Code P1: Y a eu un soucax, mais c'est surement un move qui sort du tableau alors ca va :D")

                                try: #utilisation d'un try pour les problemes d'index?
                                    leCharEnQuestion = board[i-1][j-1][1]
                                    if leCharEnQuestion in authorizedChars and leCharEnQuestion != '-':
                                        bidouilleBoard = np.copy(board)
                                        bidouilleBoard[i][j] = "--"
                                        if(i-1 == 0):
                                            bidouilleBoard[i-1][j-1] = "{}q".format(me.color)
                                        else:
                                            bidouilleBoard[i-1][j-1] = "{}p".format(me.color)
                                        outBoards.append(bidouilleBoard)
                                except:
                                    print("Code P2: Y a eu un soucax, mais c'est surement un move qui sort du tableau alors ca va :D")

                                try: #utilisation d'un try pour les problemes d'index?
                                    leCharEnQuestion = board[i-1][j+1][1]
                                    if leCharEnQuestion in authorizedChars and leCharEnQuestion != '-':
                                        bidouilleBoard = np.copy(board)
                                        bidouilleBoard[i][j] = "--"
                                        if(i-1 == 0):
                                            bidouilleBoard[i-1][j+1] = "{}q".format(me.color)
                                        else:
                                            bidouilleBoard[i-1][j+1] = "{}p".format(me.color)
                                        outBoards.append(bidouilleBoard)
                                except:
                                    print("Code P3: Y a eu un soucax, mais c'est surement un move qui sort du tableau alors ca va :D")


                            case 1:
                                #vers la gauche
                                try: #utilisation d'un try pour les problemes d'index?
                                    if board[i][j-1][1] == '-':
                                        bidouilleBoard = np.copy(board)
                                        bidouilleBoard[i][j] = "--"
                                        if(j-1 == 0):
                                            bidouilleBoard[i][j-1] = "{}q".format(me.color)
                                        else:
                                            bidouilleBoard[i][j-1] = "{}p".format(me.color)
                                        outBoards.append(bidouilleBoard)
                                except:
                                    print("Code P4: Y a eu un soucax, mais c'est surement un move qui sort du tableau alors ca va :D")

                                try: #utilisation d'un try pour les problemes d'index?
                                    leCharEnQuestion = board[i-1][j-1][1]
                                    if leCharEnQuestion in authorizedChars and leCharEnQuestion != '-':
                                        bidouilleBoard = np.copy(board)
                                        bidouilleBoard[i][j] = "--"
                                        if(j-1 == 0):
                                            bidouilleBoard[i-1][j-1] = "{}q".format(me.color)
                                        else:
                                            bidouilleBoard[i-1][j-1] = "{}p".format(me.color)
                                        outBoards.append(bidouilleBoard)
                                except:
                                    print("Code P5: Y a eu un soucax, mais c'est surement un move qui sort du tableau alors ca va :D")

                                try: #utilisation d'un try pour les problemes d'index?
                                    leCharEnQuestion = board[i+1][j-1][1]
                                    if leCharEnQuestion in authorizedChars and leCharEnQuestion != '-':
                                        bidouilleBoard = np.copy(board)
                                        bidouilleBoard[i][j] = "--"
                                        if(j-1 == 0):
                                            bidouilleBoard[i+1][j-1] = "{}q".format(me.color)
                                        else:
                                            bidouilleBoard[i+1][j-1] = "{}p".format(me.color)
                                        outBoards.append(bidouilleBoard)
                                except:
                                    print("Code P6: Y a eu un soucax, mais c'est surement un move qui sort du tableau alors ca va :D")


                            case 2:
                                #vers le bas
                                try: #utilisation d'un try pour les problemes d'index?
                                    if board[i+1][j][1] == '-':
                                        bidouilleBoard = np.copy(board)
                                        bidouilleBoard[i][j] = "--"
                                        if(i+1 == 0):
                                            bidouilleBoard[i+1][j] = "{}q".format(me.color)
                                        else:
                                            bidouilleBoard[i+1][j] = "{}p".format(me.color)
                                        outBoards.append(bidouilleBoard)
                                except:
                                    print("Code P7: Y a eu un soucax, mais c'est surement un move qui sort du tableau alors ca va :D")

                                try: #utilisation d'un try pour les problemes d'index?
                                    leCharEnQuestion = board[i+1][j-1][1]
                                    if leCharEnQuestion in authorizedChars and leCharEnQuestion != '-':
                                        bidouilleBoard = np.copy(board)
                                        bidouilleBoard[i][j] = "--"
                                        if(i+1 == 0):
                                            bidouilleBoard[i+1][j-1] = "{}q".format(me.color)
                                        else:
                                            bidouilleBoard[i+1][j-1] = "{}p".format(me.color)
                                        outBoards.append(bidouilleBoard)
                                except:
                                    print("Code P8: Y a eu un soucax, mais c'est surement un move qui sort du tableau alors ca va :D")

                                try: #utilisation d'un try pour les problemes d'index?
                                    leCharEnQuestion = board[i+1][j+1][1]
                                    if leCharEnQuestion in authorizedChars and leCharEnQuestion != '-':
                                        bidouilleBoard = np.copy(board)
                                        bidouilleBoard[i][j] = "--"
                                        if(i+1 == 0):
                                            bidouilleBoard[i+1][j+1] = "{}q".format(me.color)
                                        else:
                                            bidouilleBoard[i+1][j+1] = "{}p".format(me.color)
                                        outBoards.append(bidouilleBoard)
                                except:
                                    print("Code P9: Y a eu un soucax, mais c'est surement un move qui sort du tableau alors ca va :D")

                            case 3:
                                #vers la droite
                                try: #utilisation d'un try pour les problemes d'index?
                                    if board[i][j+1][1] == '-':
                                        bidouilleBoard = np.copy(board)
                                        bidouilleBoard[i][j] = "--"
                                        if(j+1 == 0):
                                            bidouilleBoard[i][j+1] = "{}q".format(me.color)
                                        else:
                                            bidouilleBoard[i][j+1] = "{}p".format(me.color)
                                        outBoards.append(bidouilleBoard)
                                except:
                                    print("Code P10: Y a eu un soucax, mais c'est surement un move qui sort du tableau alors ca va :D")

                                try: #utilisation d'un try pour les problemes d'index?
                                    leCharEnQuestion = board[i-1][j+1][1]
                                    if leCharEnQuestion in authorizedChars and leCharEnQuestion != '-':
                                        bidouilleBoard = np.copy(board)
                                        bidouilleBoard[i][j] = "--"
                                        if(j+1 == 0):
                                            bidouilleBoard[i-1][j+1] = "{}q".format(me.color)
                                        else:
                                            bidouilleBoard[i-1][j+1] = "{}p".format(me.color)
                                        outBoards.append(bidouilleBoard)
                                except:
                                    print("Code P11: Y a eu un soucax, mais c'est surement un move qui sort du tableau alors ca va :D")

                                try: #utilisation d'un try pour les problemes d'index?
                                    leCharEnQuestion = board[i+1][j+1][1]
                                    if leCharEnQuestion in authorizedChars and leCharEnQuestion != '-':
                                        bidouilleBoard = np.copy(board)
                                        bidouilleBoard[i][j] = "--"
                                        if(j+1 == 0):
                                            bidouilleBoard[i+1][j+1] = "{}q".format(me.color)
                                        else:
                                            bidouilleBoard[i+1][j+1] = "{}p".format(me.color)
                                        outBoards.append(bidouilleBoard)
                                except:
                                    print("Code P12: Y a eu un soucax, mais c'est surement un move qui sort du tableau alors ca va :D")

                    case 'n': #cheval
                        try: #utilisation d'un try pour les problemes d'index?
                            if board[i-1][j+2][1] in authorizedChars:
                                bidouilleBoard = np.copy(board)
                                bidouilleBoard[i][j] = "--"
                                bidouilleBoard[i-1][j+2] = "{}n".format(me.color)
                                outBoards.append(bidouilleBoard)
                        except:
                            print("Code N1: Y a eu un soucax, mais c'est surement un move qui sort du tableau alors ca va :D")

                        try: #utilisation d'un try pour les problemes d'index?
                            if board[i+1][j+2][1] in authorizedChars:
                                bidouilleBoard = np.copy(board)
                                bidouilleBoard[i][j] = "--"
                                bidouilleBoard[i+1][j+2] = "{}n".format(me.color)    
                                outBoards.append(bidouilleBoard)    
                        except:
                            print("Code N2: Y a eu un soucax, mais c'est surement un move qui sort du tableau alors ca va :D")

                        try: #utilisation d'un try pour les problemes d'index?
                            if board[i+2][j+1][1] in authorizedChars:
                                bidouilleBoard = np.copy(board)
                                bidouilleBoard[i][j] = "--"
                                bidouilleBoard[i+2][j+1] = "{}n".format(me.color)
                                outBoards.append(bidouilleBoard)
                        except:
                            print("Code N3: Y a eu un soucax, mais c'est surement un move qui sort du tableau alors ca va :D")

                        try: #utilisation d'un try pour les problemes d'index?
                            if board[i+2][j-1][1] in authorizedChars:
                                bidouilleBoard = np.copy(board)
                                bidouilleBoard[i][j] = "--"
                                bidouilleBoard[i+2][j-1] = "{}n".format(me.color)  
                                outBoards.append(bidouilleBoard)      
                        except:
                            print("Code N4: Y a eu un soucax, mais c'est surement un move qui sort du tableau alors ca va :D")

                        try: #utilisation d'un try pour les problemes d'index?
                            if board[i+1][j-2][1] in authorizedChars:
                                bidouilleBoard = np.copy(board)
                                bidouilleBoard[i][j] = "--"
                                bidouilleBoard[i+1][j-2] = "{}n".format(me.color)
                                outBoards.append(bidouilleBoard)
                        except:
                            print("Code N5: Y a eu un soucax, mais c'est surement un move qui sort du tableau alors ca va :D")

                        try: #utilisation d'un try pour les problemes d'index?
                            if board[i-1][j-2][1] in authorizedChars:
                                bidouilleBoard = np.copy(board)
                                bidouilleBoard[i][j] = "--"
                                bidouilleBoard[i-1][j-2] = "{}n".format(me.color)       
                                outBoards.append(bidouilleBoard) 
                        except:
                            print("Code N6: Y a eu un soucax, mais c'est surement un move qui sort du tableau alors ca va :D")

                        try: #utilisation d'un try pour les problemes d'index?
                            if board[i-2][j-1][1] in authorizedChars:
                                bidouilleBoard = np.copy(board)
                                bidouilleBoard[i][j] = "--"
                                bidouilleBoard[i-2][j-1] = "{}n".format(me.color)
                                outBoards.append(bidouilleBoard)
                        except:
                            print("Code N7: Y a eu un soucax, mais c'est surement un move qui sort du tableau alors ca va :D")

                        try: #utilisation d'un try pour les problemes d'index?
                            if board[i-2][j+1][1] in authorizedChars:
                                bidouilleBoard = np.copy(board)
                                bidouilleBoard[i][j] = "--"
                                bidouilleBoard[i-2][j+1] = "{}n".format(me.color)  
                                outBoards.append(bidouilleBoard)      
                        except:
                            print("Code N8: Y a eu un soucax, mais c'est surement un move qui sort du tableau alors ca va :D")
                    
                    case 'k': #roa
                        try: #utilisation d'un try pour les problemes d'index?
                            if board[i-1][j][1] in authorizedChars:
                                bidouilleBoard = np.copy(board)
                                bidouilleBoard[i][j] = "--"
                                bidouilleBoard[i-1][j] = "{}k".format(me.color)
                                outBoards.append(bidouilleBoard)
                        except:
                            print("Code K1: Y a eu un soucax, mais c'est surement un move qui sort du tableau alors ca va :D")

                        try: #utilisation d'un try pour les problemes d'index?
                            if board[i+1][j][1] in authorizedChars:
                                bidouilleBoard = np.copy(board)
                                bidouilleBoard[i][j] = "--"
                                bidouilleBoard[i+1][j] = "{}k".format(me.color) 
                                outBoards.append(bidouilleBoard)       
                        except:
                            print("Code K2: Y a eu un soucax, mais c'est surement un move qui sort du tableau alors ca va :D")

                        try: #utilisation d'un try pour les problemes d'index?
                            if board[i][j-1][1] in authorizedChars:
                                bidouilleBoard = np.copy(board)
                                bidouilleBoard[i][j] = "--"
                                bidouilleBoard[i][j-1] = "{}k".format(me.color)
                                outBoards.append(bidouilleBoard)
                        except:
                            print("Code K3: Y a eu un soucax, mais c'est surement un move qui sort du tableau alors ca va :D")

                        try: #utilisation d'un try pour les problemes d'index?
                            if board[i][j+1][1] in authorizedChars:
                                bidouilleBoard = np.copy(board)
                                bidouilleBoard[i][j] = "--"
                                bidouilleBoard[i][j+1] = "{}k".format(me.color) 
                                outBoards.append(bidouilleBoard)       
                        except:
                            print("Code K4: Y a eu un soucax, mais c'est surement un move qui sort du tableau alors ca va :D")

                        try: #utilisation d'un try pour les problemes d'index?
                            if board[i-1][j-1][1] in authorizedChars:
                                bidouilleBoard = np.copy(board)
                                bidouilleBoard[i][j] = "--"
                                bidouilleBoard[i-1][j-1] = "{}k".format(me.color)
                                outBoards.append(bidouilleBoard)
                        except:
                            print("Code K5: Y a eu un soucax, mais c'est surement un move qui sort du tableau alors ca va :D")

                        try: #utilisation d'un try pour les problemes d'index?
                            if board[i+1][j-1][1] in authorizedChars:
                                bidouilleBoard = np.copy(board)
                                bidouilleBoard[i][j] = "--"
                                bidouilleBoard[i+1][j-1] = "{}k".format(me.color)     
                                outBoards.append(bidouilleBoard)   
                        except:
                            print("Code K6: Y a eu un soucax, mais c'est surement un move qui sort du tableau alors ca va :D")

                        try: #utilisation d'un try pour les problemes d'index?
                            if board[i-1][j+1][1] in authorizedChars:
                                bidouilleBoard = np.copy(board)
                                bidouilleBoard[i][j] = "--"
                                bidouilleBoard[i-1][j+1] = "{}k".format(me.color)
                                outBoards.append(bidouilleBoard)
                        except:
                            print("Code K7: Y a eu un soucax, mais c'est surement un move qui sort du tableau alors ca va :D")

                        try: #utilisation d'un try pour les problemes d'index?
                            if board[i+1][j+1][1] in authorizedChars:
                                bidouilleBoard = np.copy(board)
                                bidouilleBoard[i][j] = "--"
                                bidouilleBoard[i+1][j+1] = "{}k".format(me.color)   
                                outBoards.append(bidouilleBoard)     
                        except:
                            print("Code K8: Y a eu un soucax, mais c'est surement un move qui sort du tableau alors ca va :D")

                    case 'b': #fosu
                        #TODO: ajouter les moves de fou a outBoards
                        print("j'en ai marre des lignes rouges quand y a rien derriere un bloc")

                    case 'q': #rein
                        #TODO: ajouter les moves de reine a outBoards
                        print("j'en ai marre des lignes rouges quand y a rien derriere un bloc")

                    case 'r': #tour
                        #TODO: ajouter les moves de tour a outBoards
                        print("j'en ai marre des lignes rouges quand y a rien derriere un bloc")

    return outBoards