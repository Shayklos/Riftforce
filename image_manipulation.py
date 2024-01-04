from PIL import Image as Img
from os.path import getsize
from colorama import Fore
from random import sample
import sys
sys.path.insert(0, './riftforce')
from Game import *
from Player import Player
from Card import Card, FACTIONS_ENG
import logging
from random import choice
from math import ceil

logging.basicConfig(level=logging.DEBUG)
directory = "files/imgs/Original/"
dmg1 = Img.open(directory + 'dmg1.png')
dmg3 = Img.open(directory + 'dmg3.png')

reducer = 1.5
dmg1 = dmg1.resize((round(dmg1.width/reducer), round(dmg1.width/reducer)))
dmg3 = dmg3.resize((round(dmg3.width/reducer), round(dmg3.width/reducer)))

background_color = (49, 51, 56) #This is Discord's default dark mode background color

def damage_tokens(card_img: Img, amount) -> Img:
    match amount:
        case 0: return
        case 1:
            card_img.paste(dmg1, (card_img.width//2 - dmg1.width//2, 10), dmg1)
        case 2:
            card_img.paste(dmg1, (card_img.width//2 - dmg1.width, 10), dmg1)
            card_img.paste(dmg1, (card_img.width//2, 10), dmg1)
        case 3:
            card_img.paste(dmg3, (card_img.width//2 - dmg3.width//2, 10), dmg3)
        case 4:
            card_img.paste(dmg1, (card_img.width//2 - dmg1.width, 10), dmg1)
            card_img.paste(dmg3, (card_img.width//2, 10), dmg3)
        case 5:
            card_img.paste(dmg1, (card_img.width//2 - round(1.25*dmg1.width), 10), dmg1)
            card_img.paste(dmg3, (card_img.width//2 - dmg3.width//2, 10), dmg3)
            card_img.paste(dmg1, (card_img.width//2 + dmg1.width//4, 10), dmg1)

        case 6:
            card_img.paste(dmg3, (card_img.width//2 - dmg3.width, 10), dmg3)
            card_img.paste(dmg3, (card_img.width//2, 10), dmg3)
        case other:
            logging.critical("More than 6 damage not allowed")

def createImgHand(cards: list[Card], handIMG_width = 2000, extension = ".png", save_dir = 'test.jpg') -> Img:
    if len(cards) == 0:
        print("TODO, mano vacía")
        return

    imgs = []
    for card in cards:
        card_directory = directory + f"{FACTIONS_ENG.get(card.faction)}{card.health}" + extension
        imgs.append(Img.open(card_directory))

    height = max([img.height for img in imgs])

    if len(imgs) == 1:
        imgs[0].save(save_dir, transparency = 0)
        logging.debug(Fore.MAGENTA + f"Saved hand of size {len(imgs)}: {round(getsize(save_dir)/1024)} KB" + Fore.WHITE)
        return

    if len(imgs) == 2:
        handIMG_width = imgs[0].width + imgs[1].width
        
    logging.debug(Fore.MAGENTA + f"{imgs[0].mode},{imgs[0].filename}" + Fore.WHITE)
    
    handImg = Img.new('RGB', (handIMG_width, height), background_color)
    step = (handIMG_width - imgs[0].width)// (len(imgs)-1)
    width_moved = 0
    for img in imgs:
        handImg.paste(img, (width_moved, 0), img)
        width_moved += step
    return handImg.convert('RGB')
    logging.debug(Fore.MAGENTA + f"Saved hand of size {len(imgs)}: {round(getsize(save_dir)/1024)} KB" + Fore.WHITE)

def columnImg(column: list[Card], extension = '.png') -> Img:
    if len(column) == 0:
        return Img.new('RGBA', (750, 1),background_color)
        
    imgs = []
    for card in column:
        card_directory = directory + f"{FACTIONS_ENG.get(card.faction)}{card.health}" + extension
        imgs.append(Img.open(card_directory).convert('RGBA'))

    if len(imgs) == 1:
        damage_tokens(imgs[0], column[0].health-column[0].health_left)
        return imgs[0]

    # logging.debug(Fore.MAGENTA + f"{imgs[0].mode},{imgs[0].filename}" + Fore.WHITE)
    
    width = max([img.width for img in imgs])

    step = imgs[0].height // 6

    handImg = Img.new('RGBA', (width, step * (len(column) -1) + imgs[0].height), background_color)
    height_moved = 0
    for img, card in zip(imgs, column):
        damage_tokens(img, card.health-card.health_left)
        handImg.paste(img, (0, height_moved), img)
        height_moved += step
    return handImg

def columnsImg(columns, flip = False) -> Img:
    columnsIMG_list = []
    for column in columns:
        columnsIMG_list.append(columnImg(column))
    
    height = max([img.height for img in columnsIMG_list if img is not None])
    width = sum([img.width for img in columnsIMG_list if img is not None])

    columns_IMG = Img.new('RGBA', (width, height), background_color)
    width_moved = 0

    iterator = reversed(columnsIMG_list) if flip else columnsIMG_list

    for img in iterator:
        if img is None:
            width_moved += 750
        columns_IMG.paste(img, (width_moved, 0), img)
        width_moved += img.width

    return columns_IMG

def boardImg(board: Board, separation = 100) -> Img:
    columns1 = columnsImg(board.columns1)
    columns2 = columnsImg(board.columns2, flip = True)
    board_img = Img.new('RGBA', (columns1.width, columns1.height + columns2.height + separation), background_color)
    board_img.paste(columns2, (0, columns1.height + separation), columns2)
    board_img = board_img.rotate(180)
    board_img.paste(columns1, (0, columns2.height + separation),columns1)
    return board_img.convert('RGB')

def draftImg(draft: Draft, extension = '.png', separation = 100) -> Img:
    available_factions_imgs = []
    for faction in draft.factions:
        card_directory = directory + f"{FACTIONS_ENG.get(faction)}" + extension
        available_factions_imgs.append(Img.open(card_directory))
    
    if len(available_factions_imgs) > 4:
        width = max(len(draft.player1_factions), ceil(len(draft.factions) / 2)) * available_factions_imgs[0].width #Note len(draft.player1_factions) >= len(draft.player2_factions)
        height = 4 * available_factions_imgs[0].height
    else:
        width = max(len(draft.player1_factions), len(draft.factions)) * available_factions_imgs[0].width #Note len(draft.player1_factions) >= len(draft.player2_factions)
        height = 3 * available_factions_imgs[0].height

    draft_img = Img.new('RGBA', (width, height + 2*separation))

    width_moved, height_moved = 0, 0
    for faction in draft.player2_factions:
        card_directory = directory + f"{FACTIONS_ENG.get(faction)}" + extension
        card = Img.open(card_directory)
        draft_img.paste(card, (width_moved, 0), card)
        width_moved += card.width

    width_moved = 0
    height_moved += available_factions_imgs[0].height + separation
    if len(available_factions_imgs) > 4:
        i = 0 
        for img in available_factions_imgs:
            draft_img.paste(img, (width_moved, height_moved), img)
            width_moved += available_factions_imgs[0].width
            i += 1
            if i == ceil(len(draft.factions) / 2): 
                width_moved = 0
                height_moved += available_factions_imgs[0].height
    else:
        for img in available_factions_imgs:
            draft_img.paste(img, (width_moved, height_moved), img)
            width_moved += available_factions_imgs[0].width
        

    width_moved = 0
    height_moved += available_factions_imgs[0].height + separation
    for faction in draft.player1_factions:
        card_directory = directory + f"{FACTIONS_ENG.get(faction)}" + extension
        card = Img.open(card_directory)
        draft_img.paste(card, (width_moved, height_moved), card)
        width_moved += card.width

    return draft_img.convert('RGB')

def draftImg_separate(draft: Draft, extension = '.png') -> Img:
    def img_gen(factions):
        imgs = []
        for faction in factions:
            card_directory = directory + f"{FACTIONS_ENG.get(faction)}" + extension
            card = Img.open(card_directory)
            imgs.append(card)

        if len(factions) > 4:
            width = ceil(len(factions) / 2) * imgs[0].width #Note len(draft.player1_factions) >= len(draft.player2_factions)
            height = 2 * imgs[0].height
        else:
            width = len(factions) * imgs[0].width #Note len(draft.player1_factions) >= len(draft.player2_factions)
            height = imgs[0].height

        IMG = Img.new('RGBA', (width, height), background_color)

        if len(factions) > 4:
            i = 0 
            width_moved = height_moved = 0
            for img in imgs:
                IMG.paste(img, (width_moved, height_moved), img)
                width_moved += imgs[0].width
                i += 1
                if i == ceil(len(draft.factions) / 2): 
                    width_moved = 0
                    height_moved += imgs[0].height
        else:
            width_moved = 0
            for img in imgs:
                IMG.paste(img, (width_moved, 0), img)
                width_moved += img.width
        return IMG.convert('RGB')

    return img_gen(draft.player2_factions), img_gen(draft.factions), img_gen(draft.player1_factions) 