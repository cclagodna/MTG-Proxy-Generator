# -*- coding: utf-8 -*-
"""
Created on Thu Dec 30 16:13:10 2021

@author: Carl
"""

import os
from PIL import Image, ImageFont, ImageDraw
import math
#Class helping with functions converting text to image
import CardTextToImage as ctti
#Class for downloading MtG cards
import MtGCardDownloader as mtgcd
import time
import os.path as path

#--------------------------------------------------------------------

#Removes empty strings from array (from splitting text)
#Each text file may end with \n\n,
#   giving rise to this empty string when splitting later on
def removeEmptyStrings(self):
    # For each empty character
    loops = self.count("")
    
    while loops > 0:
        self.remove("")
        loops -= 1

def changeSettings():
    #TODO: Allow users to change settings and save these changes
    print("Current directory: {}".format(os.getcwd()))
    print("Image file folder: {}".format(imageFolderPath))
    print("Text file folder: {}".format(textFolderPath))
    print("Proxy file folder: {}".format(proxyFolderPath))
    print("File with list of cards: {}".format(textFileLocation))

# #--------------------------------------------------------------------
# #Initialize variables

#Used for measuring program execution time
startMain = time.time()
# start = time.time()

#Name of txt file storing card list
textFileLocation = "cardlist.txt"
#Folder path storing images of cards
imageFolderPath = "Images\\"
#Folder path storing texts of cards
textFolderPath = "Texts\\"
#Folder name for images of proxies
proxyFolderPath = "Proxies\\"
#File path to proxy image
layout = Image.open("Resources\\proxyLayout.png")
#Retrive list of all card texts
listOfTexts = os.listdir(textFolderPath)

#List of keys for dictionary
keys = ["name", "mana", "type", "oracle", "flavor", "stats"]

while True:
    
    print("\n----------------------------------------\n")
    print("\nHello, welcome to the totally legal Magic the Gathering proxy downloader.")
    print("1) Download images")
    print("2) Download texts")
    print("3) Download images and texts")
    print("4) Draw texts onto a proxy image")
    print("5) Draw texts and images onto a proxy image")
    print("6) Change settings")
    print("Type anything else to quit.")
    
    inp = input("-->\t")
    
    #Download card images
    if inp == "1":
        start = time.time()
        #Open text file
        textFile = open(textFileLocation, 'r')
        #Separate text into array, split by lines (\n)
        cards = textFile.read().splitlines()
        #Close file
        textFile.close()
        #Format entries in list, removing extraneous characters
        mtgcd.formatCardList(cards)
        #Download each card specified in list
        for c in cards:
            mtgcd.downloadCardImage(c)
        end = time.time()
        print("\nTotal Image Download Time:\t{0:.4f}s".format(end - start))
      
    #Download card texts
    elif inp == "2":
        start = time.time()
        #Open text file
        textFile = open(textFileLocation, 'r')
        #Separate text into array, split by lines (\n)
        cards = textFile.read().splitlines()
        #Close file
        textFile.close()
        #Format entries in list, removing extraneous characters
        mtgcd.formatCardList(cards)
        #Download each card specified in list
        for c in cards:
            mtgcd.downloadCardText(c)

        end = time.time()
        print("\nTotal Image Download Time:\t{0:.4f}s".format(end - start))
    
    elif inp == "3":
        start = time.time()
        #Open text file
        textFile = open(textFileLocation, 'r')
        #Separate text into array, split by lines (\n)
        cards = textFile.read().splitlines()
        #Close file
        textFile.close()
        #Format entries in list, removing extraneous characters
        mtgcd.formatCardList(cards)
        #Download each card specified in list
        for c in cards:
            mtgcd.downloadCardImageAndText(c)
        end = time.time()
        print("\nTotal Image and Text Download Time:\t{0:.4f}s".format(end - start))
    
    #Draw texts on proxy image (no image)
    elif inp == "4":
        start = time.time()
        #Create proxy for each card with downloaded text
        listOfTexts = os.listdir(textFolderPath)
        for text in listOfTexts:
            #Open folder containing text files
            file = open(textFolderPath + text, 'r', encoding="utf-8")
            #Split text into relevant sections
            #\n\n to denotes new section on card
            splitText = file.read().split("\n\n")
            file.close()
            #May have empty strings, removes these from split text
            removeEmptyStrings(splitText)
            ctti.drawTextOnProxy(splitText, text)
        end = time.time()
        print("\nTotal Proxy Drawing Time:\t{0:.4f}s".format(end - start))
      
    #Draw texts and card image on proxy image 
    elif inp == "5":
        start = time.time()
        listOfImages = os.listdir(imageFolderPath)
        listOfTexts = os.listdir(textFolderPath)
        for text in listOfTexts:
            file = open(textFolderPath + text, 'r', encoding="utf-8")
            #Split text into relevant sections
            #\n\n to denotes new section on card
            splitText = file.read().split("\n\n")
            file.close()
            #May have empty strings, removes these from split text
            removeEmptyStrings(splitText)
            ctti.drawTextAndImageOnProxy(splitText, text)
        end = time.time()
        print("\nTotal Enhanced Proxy Drawing Time:\t{0:.4f}s".format(end - start))
    
    #View and change settings (file paths, etc)
    elif inp == "6":
        changeSettings()
    
    else:
        #Terminate program
        break



#Print time to execute entire program
end = time.time()
print("\n\n----------------------------------------\n")
print("Total Program Time:\t{0:.4f}s".format(end - startMain))
#Leave console window open until user presses enter
wait = input("\nPress ENTER when done... ")