# MTG-Proxy-Generator

This program generates proxies for the card game Magic: the Gathering. These proxies can then be printed off and used.
These copies are meant to test deck ideas before buying the real cards themselves.
Card images and texts will be scraped from [Scryfall](https://scryfall.com).
Proxies are **lightened, then printed in black and white** to save on ink.

I **DO NOT** endorse the use of this program to sell proxies or pass them off as real.
This is meant as a fun programming challenge for me, and to have a decent deck to play against my (much better) friends.

## To Use
- The file `cardlist.txt` must be in the same folder as `main.py` and contain a new-line separated list of desired cards. Card lists downloaded from [Archidekt](https://archidekt.com) should work innately.
- Create folders `EnhancedProxies/`, `Images/`, `Proxies/`, and `Texts/` in the same directory as `main.py`
- Run `main.py` to choose what kind of proxies you want to generate!
- Go to `EnhancedProxies/` or `Proxies/`, select all, then print off through file explorer.
- (For Windows) In the printing window, uncheck "fit picture to frame" and select "wallet" size. This will print each proxy with the standard MtG dimensions
- Painstakingly cut out the cards, sleeve them with bulk cards, then you're good to go!

## TODO:
- A GUI
- Support for uncommon card types (planeswalkers, split cards, etc)
- Allow printing of cards through the program
- Allow downloading of token cards
- Allow downloading of specific card art, instead of the first result
- Create simple mana symbols to replace text in brackets, such as: {R}{3}
