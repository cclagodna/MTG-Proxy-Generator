# -*- coding: utf-8 -*-
"""
Created on Wed Dec 22 14:36:58 2021

@author: Carl
"""

#--------------------------------------------------------------------

#This class contains methods that assist in downloading iamges and
#   text of cards.
#When passed a URL to scryfall.com, it will retrive the HTML data
#   and extract the specific iamge or card information

# TODO: Ensure this program works for niche card layouts, such as:
#   flip cards, meld cards, split cards, etc

# TODO: combine image and text retrival so it only needs one HTML
#   request. Currently, program requests each individually

# TODO: Merge the functional parts into the main class
#

#--------------------------------------------------------------------


from bs4 import BeautifulSoup
#from bs4 import SoupStrainer
import os.path as path
import requests
import time


#Format card name to work with scryfall's URL
def formatStringForURL(s):
    s = replaceBadCharacters(s)
    s = checkForQuotationMarks(s)
    return s
   
#Replaces "bad" characters so string is compatible for scryfall.com search function  
def replaceBadCharacters(s):
    #Dict of bad characters with their replacements
    filterChars = {'.' : '', ',' : '', ' ' : '+', '//' : ''}
    for oldChar in filterChars:
        s = s.replace(oldChar, filterChars[oldChar])
    return s

#Add quotation mark to begining or end of string if needed
def checkForQuotationMarks(s):
    if s.startswith('\"') is False:
        s = '\"{}'.format(s)
    if s.endswith('"') is False:
        s = '{}\"'.format(s)
    return s

#Format entries in card list to only contain name of card
def formatCardList(self):

    #Iterate over list
    for i, v in enumerate(self):
        #i = current list index
        #v = current index value
        #
        #Shifting of the start and end depend on how Arckidekt exports card names
        #Thus, these are hard-coded in and may not work for different lists
        #Unedited example:
        #   1x Aetherize (znc) ^Have,#37d67a^
        
        #Copy the text after the first space
        start = v.index(" ") + 1
        #Copy the text before parenthesis, if there are any
        if v.count("(") > 0:
            end = v.index ("(") - 1
        else:
            end = len(v)
        #Some cards have \\ in name, replace this to prevent file errors
        v = v.replace("//", "--")
        self[i] = v[start:end]

#Extract web page for desired card name from scryfall.com
def getWebPage(cardName):
    #Format card name so it can be used in URL
    formattedCardName = formatStringForURL(cardName)
    #Generate URL to search for card
    URL = "https://scryfall.com//search?q=%21{}".format(formattedCardName)
    #Get response (webpage of card) from scryfall and save it
    page = requests.get(URL)
    #Use BeautifulSoup module to parse HTML file
    soup = BeautifulSoup(page.content, "html.parser")
    return soup

#Some cards may have a back side. This will only be called for images
def checkIfHasBackSide(self):
    #Input:  BeautifulSoup object
    #Output: True/False
    #
    #Some cards have iamges on the back
    #Checks if true, so back image can be downloaded
    
    #If "image-back" tag exists, must have a back image
    try:
        self.find(class_="print-langs-item current")["data-card-image-back"]
    except:
        return False
    
    return True

#Some cards are 'split' and have two parts. This will only be called for text
def checkIfSplitCard(self):
    #Input:  BeautifulSoup object
    #Output: True/False
    #
    #Some cards are "split" and are two cards in one
    #Check if true, so text of both parts will be downloaded as separate pieces
    
    
    #If a card has two names, must be a "split" card
    if len(self.find_all(class_="card-text-card-name")) > 1:
        return True
    
    return False

#Downloads card image from scryfall.com at specified URL
def downloadCardImage(cardName, soup = None):
    #Input:  Name of card that's being downloaded
    #Output: Card is downloaded and placed in respective folder
    
    start = time.time()

    #Check if file already exists
    fileNameA = "{}{} (A).png".format(imageFolderPath, cardName)
    fileNameB = "{}{} (B).png".format(imageFolderPath, cardName)
    fileName = "{}{}.png".format(imageFolderPath, cardName)
    #If card has two parts, both aprts must be present
    alreadyExists = path.exists(fileName) or (path.exists(fileNameA) and path.exists(fileNameB))
        
    #If it does, print failure message and skip download
    if alreadyExists:
        end = time.time()
        printOutput("{}".format(cardName))
        printOutput("\tImage not downloaded:\t{0:.4f}s".format(end - start))
        return
    
    #Get web page from scryfall containing card image
    if soup == None:
        soup = getWebPage(cardName)  
    #Check is card has a back image
    hasBackSide = checkIfHasBackSide(soup)
    
    #Extract URL to the card image from web page
    imgURLFront = soup.find(class_="print-langs-item current")["data-card-image-front"]
    
    #Some cards may have extra image, thus special case is needed
    if hasBackSide:
         imgURLBack = soup.find(class_="print-langs-item current")["data-card-image-back"]
    else:
        imgURLBack = None
        
    #If there is a back image for the card
    if hasBackSide:
        img = requests.get(imgURLFront)
        #Save image as a png with a file name
        #Directory will be the same as wherever this script is
        f = open("{}{} (A).png".format(imageFolderPath, cardName), 'wb')
        f.write(img.content)
        f.close()
        
        img = requests.get(imgURLBack)
        #Save image as a png with a file name
        #Directory will be the same as wherever this script is
        f = open("{}{} (B).png".format(imageFolderPath, cardName), 'wb')
        f.write(img.content)
        f.close()
    
    #Card has no back image (as is the case 99% of the time)
    else:
        #Download image and specify its file name
        #Get stream of image from requested URL
        img = requests.get(imgURLFront)
        #Save image as a png with a file name
        #Directory will be the same as wherever this script is
        f = open("{}{}.png".format(imageFolderPath, cardName), 'wb')
        f.write(img.content)
        f.close()
    
    end = time.time()
    
    #Output success message to console
    printOutput("{}".format(cardName))
    printOutput("\tDownloaded image:\t{0:.4f}s".format(end - start))

#Store card text into a dict (alternative to downloading image)
def downloadCardText(cardName, soup = None):
    #Input: Name of card with desired text
    #Output: Text stored as text file in folder
    #
    #Stores card information as text
    #Some cards may not have a certain category of information,
    #   code will skip over these categories
    #Locations of card information depends on how scryfall organizes their site.
    #   If it changes, this code will likely break

    start = time.time()

    #Check if file already exists
    fileNameA = "{}{} (A).txt".format(textFolderPath, cardName)
    fileNameB = "{}{} (B).txt".format(textFolderPath, cardName)
    fileName = "{}{}.txt".format(textFolderPath, cardName)
    alreadyExists = path.exists(fileName) or (path.exists(fileNameA) and path.exists(fileNameB))  
    #If it does, print failure message and skip download
    if alreadyExists:
        end = time.time()
        printOutput("{}".format(cardName))
        printOutput("\tTexts not downloaded:\t{0:.4f}s".format(end - start))
        return

    #Web page of desired card, found by inputting card name
    #May also input specific URL, and will search by that instead
    if soup == None:
        soup = getWebPage(cardName)
    
    #Dictionary holding information of card
    card1 = {
        "name" : "<null>",
        "mana" : "<null>",
        "type" : "<null>",
        "oracle" : "<null>",
        "flavor" : "<null>",
        "stats" : "<null>"
        }
    #Used if card is a "split" card
    card2 = {
        "name" : "<null>",
        "mana" : "<null>",
        "type" : "<null>",
        "oracle" : "<null>",
        "flavor" : "<null>",
        "stats" : "<null>"
        }
    #Set breakPoint to 0, reevaluate if card is "split"
    #Determines where first and second part of card are
    breakPoint = 0
    #Checks if card is "split", has two cards in one
    isSplitCard = checkIfSplitCard(soup)
    
    #If card has two parts, find breakPoint where part 1 ends and part 2 begins
    if isSplitCard:
        for n in soup.find_all(class_="card-text-card-name"):
            breakPoint = max(breakPoint, n.sourceline)
    
    #Get text fields from scryfall and save them
    #---------------------------------------------------------------
    #Get name(s) of cards
    names = soup.find_all(class_="card-text-card-name")
    for name in names:
        #If card is not split, or if card part is before the breakpoint
        if breakPoint == 0 or name.sourceline < breakPoint:
            card1["name"] = name.text.strip()
        #Otherwise, must be second part of card (if it exists)
        else:
            card2["name"] = name.text.strip()
    
    manas = soup.find_all(class_="card-text-mana-cost")
    for mana in manas:
        if breakPoint == 0 or mana.sourceline < breakPoint:
            card1["mana"] = mana.text.strip()
        else:
            card2["mana"] = mana.text.strip()
    
    types = soup.find_all(class_="card-text-type-line")
    for type_ in types:
        if breakPoint == 0 or type_.sourceline < breakPoint:
            card1["type"] = type_.text.strip()
        else:
            card2["type"] = type_.text.strip()
            
    oracles = soup.find_all(class_="card-text-oracle")
    for oracle in oracles:
        if breakPoint == 0 or oracle.sourceline < breakPoint:
            card1["oracle"] = oracle.text.strip()
        else:
            card2["oracle"] = oracle.text.strip()
    
    flavors = soup.find_all(class_="card-text-flavor")
    for flavor in flavors:
        if breakPoint == 0 or flavor.sourceline < breakPoint:
            card1["flavor"] = flavor.text.strip()
        else:
            card2["flavor"] = flavor.text.strip()
    
    stats = soup.find_all(class_="card-text-stats")
    for stat in stats:
        if breakPoint == 0 or stat.sourceline < breakPoint:
            card1["stats"] = stat.text.strip()
        else:
            card2["stats"] = stat.text.strip()
    #---------------------------------------------------------------     
    
    #Export card text to text file
    if isSplitCard:
        #If card is a "split" card...
        #Export first part of card
        cardText1 = open("{}{} (A).txt".format(textFolderPath, cardName), 'w+', encoding="utf-8")
        for val in card1.values():
            #Write each section of text on new line
            cardText1.write("{}\n\n".format(val))
        cardText1.close()
        
        #Export second part of card
        cardText2 = open("{}{} (B).txt".format(textFolderPath, cardName), 'w+', encoding="utf-8")
        for val in card2.values():
            #Write each section of text on new line
            cardText2.write("{}\n\n".format(val))
        cardText2.close()
    
    #If card is not split (99% of the time)
    else:
        cardText = open("{}{}.txt".format(textFolderPath, cardName), 'w+', encoding="utf-8")
        for val in card1.values():
            #Write each section of text on new line
            cardText.write("{}\n\n".format(val))
        
        cardText.close()


    end = time.time()
    #Print success message to console
    printOutput("{}".format(cardName))
    printOutput("\tDownloaded texts:  {0:.4f}s".format(end - start))

#Method to print
# TODO: Alter this to print messages to a UI element
def printOutput(s, e = "\n"):
    print(s, end = e)
    
#Used when image and text must be downloaded
def downloadCardImageAndText(cardName):
    start = time.time()
    
    #Check if image is already downloaded
    fileNameA = "{}{} (A).txt".format(textFolderPath, cardName)
    fileNameB = "{}{} (B).txt".format(textFolderPath, cardName)
    fileName = "{}{}.txt".format(textFolderPath, cardName)
    imageExists = path.exists(fileName) or (path.exists(fileNameA) and path.exists(fileNameB))  
    
    #Check if text is already downloaded
    fileNameA = "{}{} (A).png".format(imageFolderPath, cardName)
    fileNameB = "{}{} (B).png".format(imageFolderPath, cardName)
    fileName = "{}{}.png".format(imageFolderPath, cardName)
    textExists = path.exists(fileName) or (path.exists(fileNameA) and path.exists(fileNameB))
        
    #If both do, print failure message and skip download
    if imageExists and textExists:
        end = time.time()
        printOutput("{}".format(cardName))
        printOutput("\tCard not downloaded:\t{0:.4f}s".format(end - start))
        return
    
    #Retrieve web page of card
    soup = getWebPage(cardName)
    
    #Extract image from web page
    if not imageExists:
        downloadCardImage(cardName, soup)
    #Extract text from web page
    if not textExists:
        downloadCardText(cardName, soup)
    
    print("\tTime to download card:\t{0:.4f}s".format(time.time() - start))
    
#--------------------------------------------------------------------





#--------------------------------------------------------------------

#Name of txt file storing card list
textFileLocation = "cardlist.txt"

imageFolderPath = "Images\\"
textFolderPath = "Texts\\"

# #Open text file at location
# textFile = open(textFileLocation, 'r')
# #Separate text into array, split by lines (\n)
# cards = textFile.read().splitlines()
# #Close file
# textFile.close()
# #Format entries in list, removing extraneous characters
# formatCardList(cards)