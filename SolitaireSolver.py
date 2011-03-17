import pymouse, time

class SolitaireSolver():

    def __init__(self):
        self.bottomRowStacks = [[],[],[],[],[],[],[]]
        self.moveCount = 0
        self.lastMove = ((-1,-1),(-1,-1)) # dummy values
        self.m = pymouse.PyMouse()
        self.insideDist = 20
        # Solitaire Locations
        #topRow = [(875, 150), (1133, 150), (1391, 150), (1649, 150)]
        self.wastePile = (101,151)
        #wasteCard = (359, 150)
        self.bottomRowY = 495 #the top of the bottom row
        self.bottomRowX = [101, 359, 617, 875, 1133, 1391, 1649]
        self.cardsToNotMove = []
        self.tmpCardsToNotMove = []
        self.lastWasteCard = None
        self.bottomRowInfo = None
        self.usedKings = []


    def makeMove(self, cardDictionary):
        """
        Given the current configuration of the game, decides on the next move to make

        cardDictionary is a dictionary of the format:
        (x,y) : (num, suit)

        (x, y) are the coordinates of the top left of the card

        Make the next move in the game
        Returns true if it has succeeded in making a move
        Returns false if a move is not possible
        """

        # Be careful: these are all lists, even wasteCardInfo
        topRowInfo, wasteCardInfo, self.bottomRowInfo = self.produceOrderedListsOfCardRows(cardDictionary)

        # Check for end of game
        r = map(lambda t: t == 'empty', self.bottomRowInfo)
        if sum(r) == len(r): # if all elements are true...
            print "Game over - good job!"
            return -1

        # update the stacks
        for i in range(7):
            if len(self.bottomRowStacks[i]) == 0 or self.bottomRowStacks[i] == ['empty']:
                self.bottomRowStacks[i] = [self.bottomRowInfo[i]]
                    
        # First see if any card can go to the top row
        allEligible = wasteCardInfo + self.bottomRowInfo

        # Start with aces
        p = self.numberInList('ace', allEligible)
        if p:
            c = self.getCoordsFromList(p, cardDictionary)
            print "double click on", p
            self.doubleClick(c)
            self.updateStacks(p)
            return True

        # Then see if any other card can go
        for c in topRowInfo:
            cNum = c[0]
            cSuit = c[1]

            oneUp = (self.nextNumberUp(cNum), cSuit)
            if oneUp in allEligible:
                mf = self.getCoordsFromList(oneUp, cardDictionary)
                print "double click on", oneUp
                self.doubleClick(mf)
                self.updateStacks(oneUp)
                return True

        moveList = []
            
        # Next see if any cards can be moved around on the bottom row
        # First see if any of the bottoms of the stacks can be moved.
        print
        print "Stacks:", self.bottomRowStacks
        print "BottomRowInfo", self.bottomRowInfo
        print "Lastmove", self.lastMove
        for st in self.bottomRowStacks:
            st = st[0] # because the stacks are stored as one-element lists
            for c2 in self.bottomRowInfo:
                if self.isDiffColor(st, c2) and self.nextNumberDown(c2[0]) == st[0]:
                    mf = self.getStackCoords(st, cardDictionary)
                    mt = self.getCoordsFromList(c2, cardDictionary)
                    move = [mf, mt, st]
                    moveList.append(move)

                ## # Kings can move to empty spots
                ## if st[0] == 'king' and c2 == 'empty': # and king is not already at the bottom of the stack - kings should not move once they are grounded
                ##     mf = self.getStackCoords(st, cardDictionary)
                ##     mt = (self.bottomRowX[bottomRowInfo.index('empty')], self.bottomRowY)
                ##     #self.tmpCardsToNotMove.append(c1)
                ##     move = [mf, mt, st]
                ##     moveList.append(move)


        # Then check for moves elsewhere
        for c1 in self.bottomRowInfo:
            for c2 in self.bottomRowInfo:
                # if c1 is a different color, and one less number, then move it
                if self.isDiffColor(c1, c2) and self.nextNumberDown(c2[0]) == c1[0]:
                    mf = self.getCoordsFromList(c1, cardDictionary)
                    mt = self.getCoordsFromList(c2, cardDictionary)
                    move = [mf, mt, c1]
                    moveList.append(move)
                    
        # Next see if the waste card can go to the bottom row
        if len(wasteCardInfo) > 0:
            for c in self.bottomRowInfo:
                
                if self.isDiffColor(c, wasteCardInfo[0]) and self.nextNumberDown(c[0]) == wasteCardInfo[0][0]:
                    mf = self.getCoordsFromList(wasteCardInfo[0], cardDictionary)
                    mt = self.getCoordsFromList(c, cardDictionary)
                    move = [mf, mt, wasteCardInfo[0]]
                    moveList.append(move)


        # Check if the current move is a reverse of the last move (TODO: find a way to look several moves back)
        # also a mechanism to only allow kings to move once
        while len(moveList) > 0 and (self.moveIsReverseOfLastMove(moveList[0]) or moveList[0][2] in self.usedKings):
            del moveList[0]
            
        if len(moveList) > 0:
            move = moveList[0]
            mf = move[0]
            mt = move[1]
            currLocCard = move[2]
            
            if currLocCard[0] == 'king':
                self.usedKings.append(currLocCard)
                
            return self.moveCard(mf, mt, currLocCard)
        else: #(len(movelist) == 0, nothing can be done), then press the waste pile
            self.nextCardInPile()
            return True

    def getStackCoords(self, stackCard, cardDictionary):
        """
        Given a card which is the bottom of a stack, find the coords
        """
        i = self.bottomRowStacks.index([stackCard])
        x = self.bottomRowX[i]
        lowCoordList = filter(lambda k: x-20 < k[0] < x+20 and  self.bottomRowY < k[1]+20, cardDictionary)
        if len(lowCoordList) == 0:
            print "problem"
        lowCoords = lowCoordList[0] # assume this result has only one
        lowCard = cardDictionary[lowCoords]

        # find the number of cards between the lowcard and the stackCard and use that to guess the distance
        between = self.numCardsBetween(stackCard, lowCard)
        # assume that the average amount of a stack card showing is 50 pixels
        stackShowing = 50

        return (lowCoords[0], lowCoords[1] - stackShowing*between)

    
    def numCardsBetween(self, highC, lowC):
        """
        highC, lowC are of the form (num, suit)
        When using this function, we assume that highC is higher than lowC
        """
        count = 0
        currNum = highC[0]
        while(currNum != lowC[0]):
            count += 1
            if currNum == 'ace':
                print "There are no cards further down from an ace."
                return 0
            currNum = self.nextNumberDown(currNum)

        return count
        

    def produceOrderedListsOfCardRows(self, cardDictionary):
        """
        This takes an unordered dictionary of the form:
             (x, y) : (num, suit)
        and assigns each card a position on the board based on
        coordinates. This is specific to the layout, screen resolution,
        and game. It would be better if it was more general.
        """
        
        # Separate Cards based on position
        bottomRowCoords = filter(lambda k : k[1] > 450,cardDictionary)
        wasteCardCoords = filter(lambda k: 340 < k[0] < 400 and  k[1] < 450, cardDictionary)
        topRowCoords = filter(lambda k: 800 < k[0] and  k[1] < 450, cardDictionary)

        # Get info about all cards. Info is: (num, suit)
        topRowInfo =  map(lambda k : cardDictionary[k], topRowCoords)
        wasteCardInfo =  map(lambda k : cardDictionary[k], wasteCardCoords)

        # Make sure the spaces are all there
        sortBotRowCrds = sorted(bottomRowCoords)
        bottomRowInfo = ["empty", "empty", "empty", "empty", "empty", "empty", "empty"]
        j = 0
        for i in range(7):
            if len(sortBotRowCrds) > j:
                if self.bottomRowX[i] - 20 < sortBotRowCrds[j][0] < self.bottomRowX[i] + 20:
                    bottomRowInfo[i] = cardDictionary[sortBotRowCrds[j]]
                    j += 1

        #print "Info with spaces:", bottomRowInfo
        #print "Sortbotrow",len(sortBotRowCrds)
        #print "Card Dict",len(cardDictionary)
        return topRowInfo, wasteCardInfo, bottomRowInfo
        

    def isDiffColor(self, info1, info2):
        """
        Given 2 info tuples (num, suit), we want to know
        if they are different colors
        """
        black = ["spade", "club"]
        red = ["heart", "diamond"]

        if info1 == 'empty' or info2 == 'empty':
            return True

        return info1[1] in black and info2[1] in red or \
               info1[1] in red and info2[1] in black


    def numberInList(self, num, cList):
        """
        Note: num should be a string
        It is used in the sense of the number of a card, and can
        be ace, or jack, or queen, or 10, or 2

        List is a list of cardInfo:
        [('ace', 'heart'), ('jack', 'spade')]

        if the number is in the list, it returns the tuple
        else, it returns false
        """
        for p in cList:
            if p[0] == num:
                return p

        return False


    def suitInList(self, suit, cList):
        """
        Note: suit should be a string

        List is a list of cardInfo:
        [('ace', 'heart'), ('jack', 'spade')]

        if the number is in the list, it returns the tuple
        else, it returns false
        """
        for p in cList:
            if p[1] == suit:
                return p

        return False


    def nextNumberDown(self, cardNum):
        """
        Given a number, (as a string)
        then return the next number down.
        Note: this does not wrap, so 'ace' -> None

        For example:
        'ace' -> None
        'king' -> 'queen'
        '10' -> '9'

        The suit makes no difference
        """
        num = cardNum

        if num == 'ace':
            return None
        elif num == 'empty':
            return 'king'
        elif num == 'e':
            return 'king'
        elif num == 'king':
            return 'queen'
        elif num == 'queen':
            return 'jack'
        elif num == 'jack':
            return '10'
        elif num == '2':
            return 'ace'
        else:
            return str(int(num) - 1)


    def nextNumberUp(self, cardNum):
        """
        Given cardInfo (num, info), both strings
        then return the next number up.
        Note: this wraps, so 'king' -> 'ace'

        For example:
        'ace' -> '2'
        'king' -> 'ace'
        '10' -> 'jack'

        The suit makes no difference
        """
        num = cardNum

        if num == 'ace':
            return '2'
        elif num == 'king':
            return 'ace'
        elif num == 'queen':
            return 'king'
        elif num == 'jack':
            return 'queen'
        elif num == '10':
            return 'jack'
        else:
            return str(int(num) + 1)


    def getCoordsFromList(self, cardInfo, dictionary):
        """
        This is a kind of backwards dictionary lookup
        cardInfo is: (number, suit)
        dictionary is: {coords:cardinfo, coords:cardinfo,...}
        Given cardinfo, we want coords
        """
        if cardInfo == 'empty':
            return (self.bottomRowX[self.bottomRowInfo.index('empty')], self.bottomRowY)
        
        for k in dictionary.keys():
            if dictionary[k] == cardInfo:
                return k


    def doubleClick(self, loc):
        """ Perform a double-click on the specified location"""
        self.m.click(loc[0], loc[1], 1)
        self.m.click(loc[0], loc[1], 1)

    def moveCard(self, currLoc, newLoc, currLocCard):
        """
        This function does the actual moving, and all the housekeeping associated
        with each move.

        currLoc and newLoc are tuples (x, y), and currLocCard is a card: (num, suit)

        """

        print "Moving card: ", currLocCard, "from", currLoc, "to", newLoc

        insideCurr = (currLoc[0] + self.insideDist, currLoc[1] + self.insideDist)
        insideNew = (newLoc[0] + self.insideDist, newLoc[1] + self.insideDist)

        self.m.click(insideCurr[0], insideCurr[1], 1)
        #time.sleep(1)
        self.m.click(insideNew[0], insideNew[1], 1)

        self.lastMove = (currLoc, newLoc)

        # update bottom row stacks
        # if a card moves off a stack, set it to empty and it will get updated.
        # currLoc may not be in the cardDictionary if it points to a stack value
        # find the card that has the same x as currloc (or close)
        
        #card = cardDictionary[currLoc]
       
        #print card, self.bottomRowStacks
        self.updateStacks(currLocCard)
        
        # if a card moves on a stack, nothing changes. 
        
        return True


    def updateStacks(self, currLocCard):
        """
        This takes care of keeping the bottom card of the stack correct.
        """
        
        if [currLocCard] in self.bottomRowStacks:
            i = self.bottomRowStacks.index([currLocCard])
            print "Setting column", i, "to empty"
            self.bottomRowStacks[i] = []


    def moveIsReverseOfLastMove(self, currMove):
        """
        lMove is both of the form:
             ((f.x, f.y), (t.x, t.y))
        that is, a tuple of tuples
        
        currMove is of the form:
            [(f.x, f.y), (t.x, t.y), (num, suit)]
        but the third element (a card) is not used in this function
        """
        currLoc = currMove[0]
        newLoc = currMove[1]

        lastCurrLoc = self.lastMove[0]
        lastNewLoc = self.lastMove[1]

        return self.similarPoints(currLoc, lastNewLoc) and self.similarPoints(newLoc, lastCurrLoc)


    def similarPoints(self, p1, p2):
        """
        Decides if two points (tuples), are near each other based on an offset
        """
        offset = 70
        return p1[0]-offset < p2[0] < p1[0]+offset and p1[1]-offset < p2[1] < p1[1]+offset


    def nextCardInPile(self):
        """
        Click on the waste pile
        """
        self.m.click(self.wastePile[0] + self.insideDist, self.wastePile[1] + self.insideDist, 1)


if __name__ == '__main__':
    ah = ('5', 'heart')
    kh = ('king', 'heart')
    ts = ('2', 'spade')
    #print isDiffColor(ts, kh)

    #p = (100, 20)
    #p2 = (105, 23)
    s = SolitaireSolver()
    print s.numCardsBetween(ah, ts)
    
