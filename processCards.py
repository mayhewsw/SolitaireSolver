import gtk.gdk
import cv
import numpy
import time
import os
import string
import pytesser
import Image

def takeScreenCapture(screenShotNum = ""):
    time.sleep(1)
    
    w = gtk.gdk.get_default_root_window()
    sz = w.get_size()
    #print "The size of the window is %d x %d" % sz
    pb = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB,False,8,sz[0],sz[1])
    pb = pb.get_from_drawable(w,w.get_colormap(),0,0,0,0,sz[0],sz[1])

    # Convert gtk.PixelBuf to a NumPy array
    array = pb.get_pixels_array()

    # Convert NumPy array to CvMat
    mat = cv.fromarray(array)

    # Convert RGB to BGR
    cv.CvtColor(mat, mat, cv.CV_RGB2BGR)

    #cv.ShowImage("win",mat)
    #cv.WaitKey(0)

    return mat

def getMeaningFromCards(cards):
    """
    This takes a dictionary of the form:
         (x, y) : Card image
    and returns a dictionary of the form:
         (x, y) : (number, suit)

    (x, y) are the coordinates of the top left of the card
    """

    imgdir = "LibraryImages"
    templatesNums = os.listdir(os.path.join(imgdir,"Numbers"))
    templatesSuits = os.listdir(os.path.join(imgdir,"Suits"))
                               
    #templates = filter(lambda s: s[-4:] == ".png", templates)
    templatesNums = map(lambda s: os.path.join(imgdir,"Numbers", s), templatesNums)
    templatesSuits = map(lambda s: os.path.join(imgdir, "Suits",  s), templatesSuits)    


    for k in cards.keys():
        card = cards[k]

        cardImg = cv.CreateImageHeader((card.width, card.height), 8, 3)
        cv.SetData(cardImg, card.tostring())

        numAndSuit3 = cv.GetSubRect(cardImg, (0,0,30,80))

        numAndSuit1 = cv.CreateImage((numAndSuit3.width, numAndSuit3.height), 8, 1)
        cv.CvtColor(numAndSuit3, numAndSuit1, cv.CV_RGB2GRAY)
        # Convert the 1 channel grayscale to 3 channel grayscale
        # (GRAY2RGB doesn't actually introduce color)
        cv.CvtColor(numAndSuit1, numAndSuit3, cv.CV_GRAY2RGB)
        

        num = findBestTemplateMatch(templatesNums, numAndSuit3)
        suit = findBestTemplateMatch(templatesSuits, numAndSuit3)
        #print num, suit

        # If this image was recognized as a card, but didn't match
        # any template, it shouldn't be in the list in the first place
        if num == None or suit == None:
            del cards[k]
            continue


        num = string.split(os.path.basename(num), '.')[0]
        suit = string.split(os.path.basename(suit), '.')[0]

        # The alternate file names have underscores
        # after their names
        if num[-1] == '_':
            num = num[:-1]

        if suit[-1] == '_':
            suit = suit[:-1]

        cards[k] = (num, suit)

        #cv.ShowImage("NumandSuit", numAndSuit)
        #cv.WaitKey(0)

    return cards


def findBestTemplateMatch(tplList, img):
    """
    Compares img against a list of templates.
    tplList is a list of string filenames of template images
    Returns a tuple (num, suit) if a template is suitably matched
    or None if not
    """
    
    minTpl = 200 # arbitrarily large number
    tString = None
    
    for t in tplList:
        tpl = cv.LoadImage(t)
        
        w = img.width - tpl.width + 1
        h = img.height - tpl.height + 1
        result = cv.CreateImage((w,h), 32, 1)
        cv.MatchTemplate(img, tpl, result, cv.CV_TM_SQDIFF_NORMED)
        
        (minVal, maxVal, minLoc, maxLoc) = cv.MinMaxLoc(result)

        #print t
        #print (minVal, maxVal, minLoc, maxLoc)

        # 0.2 found by experiment (the non-card images end up being around
        # 0.25 - 0.28, and all the card images were much around 0.08 and less
        if minVal < minTpl and minVal < 0.2:
            minTpl = minVal
            tString = t


    #print minTpl, tString
    #cv.ShowImage("win", img)
    #cv.ShowImage("win2", result)
    #cv.WaitKey(0)

    return tString
        

def extractCards(fileName = None):
    """
    Given an image, this will extract the cards from it.
    """
    if fileName == None:
        mat = takeScreenCapture()
    else:
        mat = cv.LoadImage(fileName)

    # First crop the image: but only crop out the bottom.
    # It is useful to have all dimensions accurate to the screen
    # because otherwise they will throw off the mouse moving and clicking.
    # Cropping out the bottom does not change anything in terms of the mouse.
    unnec_top_distance = 130
    unnec_bottom_distance = 40
    margin = 50
    submat = cv.GetSubRect(mat, (0,0,mat.width, mat.height - unnec_bottom_distance))
    subImg = cv.CreateImageHeader((submat.width, submat.height), 8, 3)
    cv.SetData(subImg, submat.tostring())


    gray = cv.CreateImage((submat.width, submat.height), 8, 1)
    cv.CvtColor(submat, gray, cv.CV_RGB2GRAY)

    thresh = 250
    max_value = 255
    cv.Threshold(gray, gray, thresh, max_value, cv.CV_THRESH_BINARY)

    cv.Not(gray,gray)
    #cv.ShowImage("sub", submat)
    #cv.WaitKey(0)

    storage = cv.CreateMemStorage (0)

    cpy = cv.CloneImage(gray)
    contours = cv.FindContours( cpy, storage, cv.CV_RETR_LIST, cv.CV_CHAIN_APPROX_SIMPLE, (0,0) );
    #contours = cv.ApproxPoly(contours, cv.CreateMemStorage(), cv.CV_POLY_APPROX_DP, 3, 1)

    bboxes = []

    if contours:
        while(contours):
            area = cv.ContourArea(contours)
            # It turns out that all the cards are about 44000 in area...
            # It would definitely be nice to have a better way to do this:
            # ie, find the size of the card programmatically and use it then
            if(area > 44000 and area < submat.width*submat.height*2/3):
                bb = cv.BoundingRect(contours)
                bboxes.append(bb)
            contours = contours.h_next()

    #drawBoundingBoxes(bboxes, submat)

    # cards is a dictionary of the form:
    #    (x, y) : card
    cards = {}
    
    for box in bboxes:
        card = cv.GetSubRect(subImg, box)
        #cv.ShowImage("card", card)
        #cv.WaitKey(0)
        cards[(box[0], box[1])] = card

    return cards
    

def drawBoundingBoxes(bb, img):
    for b in bb:
        x = b[0]
        y = b[1]
        width = b[2]
        height = b[3]
        cv.Rectangle(img, (x,y), (x+width, y+height), (0,255,0,0))

    cv.ShowImage("bb", img)
    cv.WaitKey(0)


def drawSquares(listWithPoints,img):
    for l in listWithPoints:
        for p in range(len(l)-1):
            cv.Line(img, l[p], l[p+1], (0,0,255,0),2)
        cv.Line(img, l[-1], l[0], (0,0,255,0),2)

    #cv.ShowImage("sub", img)
    #cv.WaitKey(0)    

def contourToPointList(contour):
    plist = []
    for (x,y) in contour:
        plist.append((x,y))
        
    return plist


if __name__ == '__main__':
    cards = extractCards('CardImages/4_heart.jpg')
    print cards
    #c = cards[cards.keys()[0]]
    #print c

    

    
