from dnd_character import *
import json

def playerCharCreate(name,age,level,gender,description,background,playerclass):
    newChar = Character(
        name=name,
        age=age,
        level=level,
        gender=gender,
        description=description,
        background=background,
        classs=CLASSES[playerclass.lower()])
    return newChar

print(playerCharCreate(name="Thor Odinson",
    age="34",
    level=1,
    gender="Male",
    description="Looks like a pirate angel",
    background="Born on Asgard, God of Thunder",
    playerclass="Fighter"))

