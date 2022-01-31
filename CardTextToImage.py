# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 16:49:25 2021

@author: Carl
"""

#--------------------------------------------------------------------

#This class contains methods that assist in converting card text
#   (stored as a text file) into an image.
#It does this by reading text, and drawing that text on a basic
#   MtG card image.

#--------------------------------------------------------------------



from PIL import Image, ImageFont, ImageDraw, ImageEnhance
import math
import time
import os
from os import path



#Returns midpoint between two points, rounded up
def midpoint(a, b):
    return (a + b) / 2

#If given a box with attributes (X, Y, width, height), returns its X midpoint
def xMidpoint(box):
    return midpoint(box[0], box[0] + box[2] - 1)

#If given a box with attributes (X, Y, width, height), returns its Y midpoint
def yMidpoint(box):
    return midpoint(box[1], box[1] + box[3] - 1)

#Returns font with maximum size that allows text to fit in box
def getFontSizeToFitInBounds(font, text, box, multiline = False):
    
    if text == "":
        #print("No text to check font with!")
        return font
    
    #Amount to add/ subtract to font size 
    jumpSize = 50
    global fontType
    global fontSize
    fontSize = font.size
    
    #Binary division until text can fit in box
    while jumpSize >= 1:
        
        #Checks if single/multi line text will fit in box
        if willTextFit(font, text, box, multiline):
            fontSize += jumpSize
            
        #If length or width is larger than the box...
        else:
            fontSize -= jumpSize
            #Divide by 2 and round down
            jumpSize = jumpSize // 2
            
        #Set new font, so new text size can be rechecked
        font = ImageFont.truetype(fontType, fontSize)

    return font

#Returns true or false on whether text (with specified font) will fit in box
def willTextFit(font, text, box, multiline = False, axis = 'xy'):
    #Can only check specific axis, or both
    #If multiline is True, that means text may have \n characters
    
    w = box[2]
    h = box[3]
    
    #May get passed a font with a negative value
    if font.size <= 0:
        return True
    
    #Single line text
    if not multiline:
        dim = font.getsize(text)
    #Multiline text
    else:
        dim = font.getsize_multiline(text)
    
    #Check if text fits in box
    if axis == 'x':
        if dim[0] <= w:
            return True
    elif axis == 'y':
        if dim[1] <= h:
            return True
    else:
        if dim[0] <= w and dim[1] <= h:
            return True
        
    #If text dimensions are larger than the box...
    return False


#Find the largest font size that allows text to still fit in box
def findMaxFontSize(font, text, box, multiline = False):
    
    start = time.time()
    
    global fontType
    testFontSize = 1
    mintestFontSize = testFontSize
    #Dummy font to test if new testFontSize works
    testFont = ImageFont.truetype(fontType, testFontSize)
    
    #Check if new font size will still fit in box
    # TODO: remove this 'x' if "fit's shucked"
    #while willTextFit(testFont, text, box, multiline, "x"):
    while willTextFit(testFont, text, box, multiline):
        #Copy dummy font to real font
        font = testFont
        #Save smallest possible font size currently known
        mintestFontSize = testFontSize
        #Iterate font size and dummy font
        testFontSize *= 2
        testFont = ImageFont.truetype(fontType, testFontSize)
        
    #Initialize 'shift' to font size of 'real' font
    shift = font.size / 2
    testFontSize = font.size
    #Loop until shift value is between 1 and -1
    while shift >= 1 or shift <= -1:
        #Shift font size up or down
        testFontSize += math.floor(shift)
        #Dummy font to test if new testFontSize works
        testFont = ImageFont.truetype(fontType, testFontSize)
        #Boolean if new font size will fit in box
        textFits = willTextFit(testFont, text, box, multiline)
        
        #If 'testFont' does work
        #Smaller text sides obviouslly will fit if larger one does,
        #   thus will only change size if larger than known minimum
        if textFits and testFont.size > mintestFontSize:
            #Set 'real' font
            font = testFont
            #Since font fits, start growing it
            shift = abs(shift)
        elif not textFits:
            #Since font is too big, start shrinking it
            shift = -1 * abs(shift)
            
        #Iterate shift logramithacally
        shift /= 2 
            
   
    end = time.time()
    #print("findMaxtestFontSize Time: {0:.4f}s".format(end - start))
    return font

#Add newline characters to text so it fits in box
def fitToBox(font, text, box, multiline = False):
    #Pass font and text, seeing if it fits in box horizontally
    
    start = time.time()
    
    #Split text by each word
    splitText = text.split(" ")
    #String that will be returned will added new lines
    newText = ""
    
    #--------------------
    #Code works perfectly, problem is it takes long to process
    #Roughly ~6.20s for 1000 characters
    #   Seemingly linear growth, ~15.87s for 2500 chars
    #Thankfully, this doesn't seem to be an issue in a practically
    
    #For each word in text...
    for t in splitText:
        #If putting next word into string still fits in box...
        if willTextFit(font, newText + " " + t, box, multiline, 'x'):
            newText += " " + t
        #If it won't fit, add a new line
        else:
            newText += "\n" + t
    
    #--------------------
    #Find width to height ratio of box, and try shape text to that ratio
    #Then scale up text as much as possible
    #--------------------
    #Possible solution: calculate char length of one line,
    #   then chunk future lines together
    #Much faster, but is much buggier than above
    #{Deleted code}
    #--------------------
    
    #Remove trailing whitespace or newline
    if newText[0] in (" ", "\n"):
        newText = newText[1:]
    #Remove ending whitespace or newline
    if newText[-1] in (" ", "\n"):
        newText = newText[:-1]
    
    end = time.time()
    #print("fitToBox Time: {0:.4f}s".format(end - start))
    return newText

#Combination of findMaxFontSize and fitToBox
def fitOracleText(font, text, box, multiline = True):
    # FIXME: Font is being exported with size 32 in most cases,
    #   even when it could be larger to fill more of the text box
    #Setting font to maxSize before loop seems to fix this, but then
    #   lengthy cards are printed much smaller
    
    
    start = time.time()
    
    global fontType
    global minFontSize
    global prefFontSize
    
    #Must preserve original text and font
    oldText = text
    oldFont = font
    
    #Gives up after maxTries and just sets text to preffered size
    tries = 0
    maxTries = 5
    while not willTextFit(font, text, box, multiline):
        if tries >= maxTries:
            font = ImageFont.truetype(fontType, prefFontSize)
            text = fitToBox(font, text, box, multiline)
            break
        text = fitToBox(font, oldText, box, multiline)
        font = findMaxFontSize(oldFont, text, box, multiline)
        tries += 1
    
    if font.size > maxFontSize:
        font = ImageFont.truetype(fontType, maxFontSize)
    
    end = time.time()
    #print("fitOracleText Time: {0:.4f}s".format(end - start))
    return font, text


def drawTextOnProxy(c, fileName):   
    #Declare as global or else changes won't save
    global card
    global nameFont
    global manaFont
    global typeFont
    global oracleFont
    global statsFont
    
    #Record start time for this loop iteration
    start = time.time()
    
    saveFileAs = "{}{}.png".format(proxyFolderPath, fileName[:-4])
    
    #If text has already been drawn and saved, skip it
    #text[:-4] truncates the .txt from the file name
    if path.exists(saveFileAs):
        end = time.time()
        print("{}".format(c[0]))
        print("\tText already drawn:\t{0:.4f}s".format(end - start))
        return
    
    #Create dictionary with loaded card text associated with keys
    #<null> is just a marker for empty card sections
    #Replace "<null>" with empty string so it won't be written on card
    card = {}
    for i in range(len(c)):
        if c[i] == "<null>":
            card[keys[i]] = ""
        else:
            card[keys[i]] = c[i]
    
    #If card has no name, skip it
    #This should not happen
    if card["name"] in ("<null>", "", " "):
        print("ERROR: NO NAME GIVEN")
        return
    
    #Generate fonts for each section so text fills up as much space
    #   as possible, without crossing border
    nameFont = getFontSizeToFitInBounds(f, card["name"], nameBox)
    manaFont = getFontSizeToFitInBounds(f, card["mana"], manaBox)
    typeFont = getFontSizeToFitInBounds(f, card["type"], typeBox)
    #Oracle text may have more than one line of text
    #Both the font and the text itself must be edited
    oracleFont, card["oracle"] = fitOracleText(f, card["oracle"], oracleBox, True)
    statsFont = getFontSizeToFitInBounds(f, card["stats"], statsBox)
    
    #File path to proxy image
    layout = Image.open("Resources\\proxyLayout.png")
    #Draw text
    drawText(layout)
    #Save image, with card text drawn on proxy
    #text[:-4] truncates the .txt from the file name
    layout.save(saveFileAs)
    #Show new image (for debugging purposes)
    #layout.show()
    #Close image
    layout.close()
    
    #Print time taken to process one image
    end = time.time()
    print("{}".format(card["name"]))
    print("\tSaved Proxy Image: {0:.4f}s".format(end - start))


def drawTextAndImageOnProxy(c, fileName, color = False):
    start = time.time()
    
    #Generate new file name for proxy png
    newFileName = enhancedProxyFolderPath + fileName[:-4] + ".png"
    
    #Don't draw proxy if file with its name already exists
    if path.exists(newFileName):
        end = time.time()
        print("{}".format(c[0]))
        print("\tEnhanced Proxy Already Drawn:\t{0:.4f}s".format(end - start))
        return
        
    #Draw a basic proxy with just card text
    drawTextOnProxy(c, fileName)
    #Retrieve this proxy
    proxyOfCard = proxyFolderPath + fileName[:-4] + ".png"
    proxy = Image.open(proxyOfCard, 'r')
    proxy = proxy.convert('RGBA')
    
    #First two numbers are top-left pixel, last two are bottom-right
    manaBox = proxy.crop((421, 95, 627, 154))
    
    #Retrive card image
    imageOfCard = imageFolderPath + fileName[:-4] + ".png"
    #Crop out just the image box on the card
    img = Image.open(imageOfCard, 'r')
    img = img.crop((49, 102, 623, 521))
    img = img.convert('RGBA')
    
    #Paste card image onto proxy layout
    proxy.paste(img, (49, 102))
    #Paste mana box over image
    proxy.paste(manaBox, (421, 95))
    
    #If want to print image in black and white
    if not color:
        #Brighten proxy image
        brightnessFactor = 2.5
        e = ImageEnhance.Brightness(proxy)
        proxy = e.enhance(brightnessFactor)
        
        #Remove color from image
        colorFactor = 0
        e = ImageEnhance.Color(proxy)
        proxy = e.enhance(colorFactor)
    
    proxy.save(newFileName)
    
    end = time.time()
    print("\tSaved Enhanced Proxy Image:\t{0:.4f}s".format(end - start))
    
#Removes empty strings from array (from splitting text)
#Each text file may end with \n\n,
#   giving rise to this empty string when splitting later on
def removeEmptyStrings(self):
    # For each empty character
    loops = self.count("")
    
    while loops > 0:
        self.remove("")
        loops -= 1

#Read text and draw it on proxy card image
def drawText(self):
    #INPUT: Uses global variables, thus input/ output not needed
    #OUPUT: ^
    
    start = time.time()
    
    #Load image to place text onto
    image_editable = ImageDraw.Draw(self)
    
    #Add name text to card image
    image_editable.text(nameBoxPos, card["name"], textColor, font=nameFont, align = nameAlign, anchor = nameAnchor)
    
    #Add mana text to card image
    image_editable.text((manaBoxMidX, manaBoxMidY), card["mana"], textColor, font=manaFont, align = manaAlign, anchor = manaAnchor)
    
    #Add type text to card image
    image_editable.text((typeBox[0], typeBoxMidY), card["type"], textColor, font=typeFont, align = typeAlign, anchor = typeAnchor)
    
    #Add oracle text to card image
    image_editable.multiline_text((oracleBox[0], oracleBox[1]), card["oracle"], textColor, font=oracleFont, align = oracleAlign, anchor = oracleAnchor)
    
    #Add stats text to card image
    image_editable.text((statsBoxMidX, statsBoxMidY), card["stats"], textColor, font=statsFont, align = statsAlign, anchor = statsAnchor)
    
    #Replace image w/o text with new one that has text
    self = image_editable
    
    

#--------------------------------------------------------------------
#Initialize variables

#Used for measuring program execution time
startMain = time.time()
start = time.time()

#Name of txt file storing card list
textFileLocation = "cardlist.txt"
#Folder path storing images of cards
imageFolderPath = "Images\\"
#Folder path storing texts of cards
textFolderPath = "Texts\\"
#Folder name for images of proxies
proxyFolderPath = "Proxies\\"
#Folder name for enhanced proxies
enhancedProxyFolderPath = "EnhancedProxies\\"
#File path to proxy image
layout = Image.open("Resources\\proxyLayout.png")
#Retrive list of all card texts
listOfTexts = os.listdir(textFolderPath)

#Default font and text options
textColor = (0, 0, 0)
fontType = 'LiberationSansNarrow-Regular.ttf'
#Min, preferred, and max text font
#These limits are used ONLY for oracle text
minFontSize = 16
prefFontSize = 32
maxFontSize = 48
#Initialize font object
fontSize = prefFontSize
f = ImageFont.truetype(fontType, fontSize)
#Padding around every inner edge for every box, in pixels
#Padding over 11 seems to cause errors
boxPadding = 6

#List of keys for dictionary
keys = ["name", "mana", "type", "oracle", "flavor", "stats"]

#Read from proxy dimension text file and save as a dictionary
#These dimensions were measured by hand
boxDimensions = {}
file = open("Resources\\proxyDimensions.txt", 'r', encoding="utf-8")
dimText = file.read().split("\n")
for dim in dimText:
    pair = dim.split("\t")
    boxDimensions.update({pair[0] : pair[1]})
file.close()

#Convert dimensions from string -> int, and save in dictionary
for key, val in boxDimensions.items():
    val = val.replace("(", "")
    val = val.replace(")", "")
    newVal = val.split(", ")
    
    #Alter box dimensions by boxPadding
    #index 0 & 1 are X & Y coordinates, must be added by padding
    #2 & 3 are width & height, must be subtracted by 2 * padding
    newVal[0] = int(newVal[0]) + boxPadding
    newVal[1] = int(newVal[1]) + boxPadding
    newVal[2] = int(newVal[2]) - 2 * boxPadding
    newVal[3] = int(newVal[3]) - 2 * boxPadding
    boxDimensions[key] = newVal

end = time.time()
print("\tFinished Initializations:\t{0:.4f}s".format(end - start))

#--------------------------------------------------------------------
#Process and write card text to image
# FIXME: Y midpoints seem to be 3-6 pixels higher than they should be
#   For now, just adding the 3-6 pixels to the midpoint result

#Properties for "name" box
nameBox = boxDimensions["name"]
#Find Y-center so name can be vertically centered
nameBoxMidY = yMidpoint(nameBox) + 3
#Position for top-left pixel of text to be placed
nameBoxPos = (nameBox[0], nameBoxMidY)
nameFont = f
nameAlign = 'center'
nameAnchor = 'lm'

#---------------------------------------
#Properties for "mana" box

manaBox = boxDimensions["mana"]
#Mana symbols are centered on X and Y axis
manaBoxMidX = xMidpoint(manaBox)
manaBoxMidY = yMidpoint(manaBox)
manaFont = f
manaAlign = "center"
manaAnchor = "mm"

#---------------------------------------
#Properties for card "type" box

typeBox = boxDimensions["type"]
#Must be shifted down by three pixels to fit in box
# TODO: Fix this
typeBoxMidY = yMidpoint(typeBox) + 3
typeFont = f
typeAlign = 'center'
typeAnchor = 'lm'

#---------------------------------------
#Properties for "oracle" box

oracleBox = boxDimensions["oracle"]
oracleBoxMidX = xMidpoint(oracleBox)
oracleBoxMidY = yMidpoint(oracleBox)
oracleFont = f
oracleAlign = 'left'
oracleAnchor = 'la'

#---------------------------------------
#Properties for "flavor" text box
#Flavor text is not important, thus can be skipped
#---------------------------------------
#Properties for "stats" box

statsBox = boxDimensions["stats"]
statsBoxMidX = xMidpoint(statsBox)
#Must be shifted down by six pixels to fit in box
# TODO: Fix this
statsBoxMidY = yMidpoint(statsBox) + 6
statsFont = f
statsAlign = 'center'
statsAnchor = 'mm'

#---------------------------------------

end = time.time()
print("Loaded Proxy Layout:\t{0:.4f}s".format(end - start))

#--------------------------------------------------------------------