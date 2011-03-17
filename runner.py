import SolitaireSolver
import processCards
import time

def main():
    print "Beginning the Solitaire Solver..."
    # Give some time to open the window...
    time.sleep(5)

    s = SolitaireSolver.SolitaireSolver()
    #cards = processCards.extractCards()
    #topRowInfo, wasteCardInfo, bottomRowInfo = SolitaireSolver.produceOrderedListsOfCardRows(cards)

    while True:
        cards = processCards.extractCards()
        if len(cards) == 0:
            break
        meaning = processCards.getMeaningFromCards(cards)
        retValue = s.makeMove(meaning)
        if retValue == False:
            print "makeMove Returned false"
            break
        if retValue == -1:
            break
        
        #time.sleep(1)

    
    



if __name__ == "__main__":
    main()
