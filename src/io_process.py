#!/usr/bin/env python3

from src import senders
from src.battlelog_parsing import battlelog_parsing
from src.login import log_in
from src.battle import Battle

import random
from time import sleep
battles = []
nb_fights_max = 10 #Maximum fights that can be done in 1 session. Exits when reached
nb_fights_simu_max = 1 #Maximum simultaneous fights, I think showdown already caps this at 2 (searches)
sleeptime = 0.5
#Too many fights - may hit the message throttle limit. 5 is dangerous w/ chat. 6 msg/600ms? Maybe add a throttle here too.
nb_fights = 0
search = False  # tracking this because PS does not let you search twice for the same format
# because of this sometimes u can make searches that dont go through and play less games
# 2019/01/13: Turns out this has to be global not local for this to work, but it works. Wack

#2019/01/19: Future note, there is a high load limit of 12 battles per 3 minutes. Someone can break bot by challenging
#2020/05/30: We back baby
formats = [ #Formats you can play. First in list is used in searches
    #"gen7randombattle",
    #"gen7monotyperandombattle",
    #"gen7hackmonscup",
    #"gen7challengecup1v1",
    #"gen6battlefactory",
    #"gen7bssfactory",
    #"gen7randomdoublesbattle",
    # "gen7metronomebattle"
    "gen8metronomebattle"
]

teams = [
    # "vacation|shaymin|weaknesspolicy|flowerveil|metronome|Relaxed|252,252,252,252,252,252|||||128]i am NOT on|shayminsky|weaknesspolicy|simple|metronome|Sassy|252,252,252,252,252,252|||||128",
    # "Gameshark|lucariomega|kingsrock|serenegrace|metronome|Hardy|252,252,252,252,252,252|M||||128]Action replay|lucariomega|kingsrock|serenegrace|metronome|Quirky|252,252,252,252,252,252|F||||128",
    # "PEKACHU|pikachustarter|lightball|intrepidsword|metronome|Brave|252,252,252,252,252,252|||||]pekachu2|pikachustarter|lightball|download|metronome|Serious|252,252,252,252,252,252|||||",
    # "Brave|sirfetchd|leek|superluck|metronome|Brave|252,252,252,252,252,252|M||||]Quiet|sirfetchd|leek|superluck|metronome|Quiet|252,252,252,252,252,252|F||S||",
    "PEKACHU|pikachustarter|lightball|teravolt|metronome|Hardy|252,252,252,252,252,252|||||]KILLER|pikachustarter|lightball|teravolt|metronome|Hardy|252,252,252,252,252,252|||||",
    ]

def check_battle(battle_list, battletag) -> Battle or None:
    """
    Get Battle corresponding to room_id.
    :param battle_list: Array of Battles.
    :param battletag: String, Tag of Battle.
    :return: Battle.
    """
    for battle in battle_list:
        if battle.battletag == battletag:
            return battle
    return None

async def battle_tag(websocket, message, usage):
    """
    Main in fuction. Filter every message sent by server and launch corresponding function.
    :param websocket: Websocket stream.
    :param message: Message received from server. Format : room|message1|message2.
    :param usage: 0: Only recieving. 1 Challenging Synedh. 2 searching random battles.
    """
    global battles
    global sleeptime
    battleturn = -1   
    currentturn = 1
    good = ["not even close baby", "yes", "ez", "this is epic", "gg", "nice", "outplayed", "predicted", "woah", "tactical",
            "laugh out loud", "gottem"
            # "IndentationError: unexpected indent", "SyntaxError: invalid syntax"
            ] #good lines in general (se move, crit)
    bad = ["ur using gameshark", "powersaves", "calling nintendo on you rn", "hax", "no", "damn",
           "this is rigged", "rng abused",
           "action replay", "sheesh", "unfortunate", "sad", "unfort", "geez", "F", "crit mattered",
           "cant even learn metronome in the real games", "that mon is photoshopped"
           # "Traceback (most recent call last): File \"metronome_damage_calc\", line 1, in <module>"
           ]
    neutral = ["IndentationError: unexpected indent"]
    death = ["rip", "big rip", "SyntaxError: invalid syntax"]
    responses = ["faint", "-crit", "-supereffective", "-start"]
    toxicity = ["Taunt", "Imprison", "Attract", "Disable", "Torment"] #mom
    lines = message.splitlines()
    battle = check_battle(battles, lines[0].split("|")[0].split(">")[1])

    for line in lines[1:]:
        try:
            current = line.split('|')
            if current[1] == "init":
                # Creation de la bataille
                battle = Battle(lines[0].split("|")[0].split(">")[1])
                battles.append(battle)
                sleep(sleeptime)
                await senders.sendmessage(websocket, battle.battletag, "I am a bot. Good luck have fun") #a nice greeting
                sleep(sleeptime)
                await senders.sendmessage(websocket, battle.battletag, "/timer on")
                # sleep(sleeptime)
                # await senders.sendmessage(websocket, battle.battletag,
                #                           "Calculated estimation probability (approximate): "+
                #                           str(random.random()*100)+"%")
                #14 decimals


            elif current[1] == "player" and len(current) > 3 and current[3].lower() == "flame20xx": #identify our ID
                # Récupérer l'id joueur du bot
                battle.player_id = current[2]
                battle.turn += int(current[2].split('p')[1]) - 1
            # elif current[1] == "player" and len(current) > 3 and current[3].lower != "flame20xx": #if not us

                # battle.enemy_id = current[2]
                # # battle.enemy_name = current[3] #this is the enemy
                # enemyname = current[3]

                # await senders.sendmessage(websocket, battle.battletag, "test "+battle.enemy_name)
            elif current[1] == "request":
                if current[2] == '':
                    continue;
                # Maj team bot
                if len(current[2]) == 1:
                    try:
                        await battle.req_loader(current[3].split('\n')[1], websocket)
                    except KeyError as e:
                        print(e)
                        print(current[3])
                else:
                    await battle.req_loader(current[2], websocket)
            elif current[1] == "teampreview":
                # Selection d'ordre des pokemons
                await battle.make_team_order(websocket)
            elif current[1] == "turn":
                # Phase de reflexion
                sleep(sleeptime)
                await battle.make_action(websocket)
            elif current[1] == "callback" and current[2] == "trapped":
                await battle.make_move(websocket)
            elif current[1] == "win":
                sleep(sleeptime)
                await senders.sendmessage(websocket, battle.battletag, "Good game!") #friendly
                #await senders.savereplay(websocket, battle.battletag)
                sleep(sleeptime)
                await senders.leaving(websocket, battle.battletag)
                sleep(sleeptime)
                battles.remove(battle)
                if usage == 2:
                    with open("log.txt", "r+") as file:
                        line = file.read().split('/')
                        file.seek(0)
                        if "flame20xx" in current[2].lower(): #I am the win
                            file.write(str(int(line[0]) + 1) + "/" + line[1] + "/" + str(int(line[2]) + 1))
                        else:# I lost.
                            file.write(line[0] + "/" + str(int(line[1]) + 1) + "/" + str(int(line[2]) + 1))

            elif current[1] == "c":
                # This is a message
                pass
            

                
            
            else:
                # Send to battlelog parser.

                battlelog_parsing(battle, current[1:])
                split_line = current[1:]

                if split_line[0] in responses:
                    #' Optimistically i would like some weighting system, like set flags midturn
                    # and go through next turn so priority (imprison > faint > crit > se)

                    if battleturn != battle.turn: #has to be here since some message at end of fights isnt handled by first checks
                        #and battle ends so no battle.turn = crash
                        sleep(sleeptime)  # wait 1 second
                        if split_line[0] == "faint":
                            await senders.sendmessage(websocket, battle.battletag, "rip")
                            # battleturn = battle.turn #1 massage per turn - Flame
                        elif split_line[0] == "-start" and split_line[2].split()[-1] in toxicity: #fair move statuses
                            #there are move: toxic and then there is just toxic alone (disable) - wack...
                            await senders.sendmessage(websocket, battle.battletag, split_line[2].split()[-1]+" is a fair move")
                        elif split_line[0] == "-crit":
                            await senders.sendmessage(websocket, battle.battletag, "crit mattered")
                        # elif split_line[0] == "-supereffective" or split_line[0] == "-crit":
                        #     if battle.player_id in split_line[1]:
                        #         await senders.sendmessage(websocket, battle.battletag, random.choice(bad))
                        #     else:
                        #         await senders.sendmessage(websocket, battle.battletag, random.choice(good))
                            # battleturn = battle.turn #1 massage per turn - Flame

                        battleturn = battle.turn #1 massage per turn - Flame

                # commented out because typing too quickly interrupts the bot

                
                    

                
              
        except IndexError:
            pass

async def stringing(websocket, message, usage=2): #Mod this for usage mode
    """
    First filtering function on received messages.
    Handle challenge and research actions.
    :param websocket: Websocket stream.
    :param message: Message received from server. Format : room|message1|message2.
    :param usage: 0: Only recieving. 1 Challenging user. 2 searching random battles.
    """
    global nb_fights_max
    global nb_fights
    global nb_fights_simu_max
    global battles
    global formats
    global search
    global sleeptime
    


    string_tab = message.split('|')
    if string_tab[1] == "challstr":
        # If we got the challstr, we now can log in.
        await log_in(websocket, string_tab[2], string_tab[3])
    elif string_tab[1] == "updateuser" and "Flame20XX" in string_tab[2]: #replace with your bot name I guess
        #space in front because of IDENTITIES
        # Once we are connected.
        if usage == 1:
            sleep(sleeptime)
            await senders.sender(websocket, "", "/utm " + random.choice(teams))
            await senders.challenge(websocket, "Flametix", formats[0])
        if usage == 2:
            if search == False:
                sleep(sleeptime)
                await senders.sender(websocket, "", "/utm " + random.choice(teams))
                search = True
                await senders.searching(websocket, formats[0])
                nb_fights += 1
    elif string_tab[1] == "deinit" and usage == 2:
        # If previous fight is over and we're in 2nd usage
        if nb_fights < nb_fights_max and len(battles) < nb_fights_simu_max:  # If it remains fights
            if search == False:
                sleep(sleeptime)
                await senders.sender(websocket, "", "/utm " + random.choice(teams))                        
                sleep(sleeptime)
                await senders.searching(websocket, formats[0])
                search = True
                nb_fights += 1


        elif nb_fights >= nb_fights_max and len(battles) == 0:  # If it don't remains fights (Fights reached max limit)
            #I think the = makes it so you may end up with a searching leftover when done, nothing serious.
            exit(0)
    elif "|inactive|Battle timer is ON:" in message and usage == 2 and "savereplay" not in message and "|c|" not in message:
        # If previous fight has started and we can do more simultaneous fights and we're in 2nd usage.
        # And the inactive part isn't from the replay save log
        # And it's not a human saying it
        if len(battles) < nb_fights_simu_max and nb_fights < nb_fights_max:
            if search == False:
                search = True
                sleep(sleeptime)
                await senders.sender(websocket, "", "/utm " + random.choice(teams))                        
                await senders.searching(websocket, formats[0])
                nb_fights += 1
                sleep(sleeptime)
    elif "updatechallenges" in string_tab[1]:
        # If somebody challenges the bot
        try:
            if string_tab[2].split('\"')[3] != "challengeTo":
                if string_tab[2].split('\"')[5] in formats and usage != 2: #challenges may break it? temporary
                    if string_tab[2].split('\"')[5] == "gen8metronomebattle":
                        sleep(sleeptime)
                        await senders.sender(websocket, "", "/utm " + random.choice(teams))
                        sleep(sleeptime)
                    await senders.sender(websocket, "", "/accept " + string_tab[2].split('\"')[3])

                else:
                    sleep(sleeptime)
                    await senders.sender(websocket, "", "/reject " + string_tab[2].split('\"')[3])
                    sleep(sleeptime)
                    # await senders.sender(websocket, "", "/pm " + string_tab[2].split('\"')[3]
                    #                      + ", Sorry, I accept only Metronome Battle.")

        except KeyError:
            pass
    elif string_tab[1] == "pm" and "Flame20XX" not in string_tab[2]:
        if string_tab[4] == "Me and you can rule this city spiderman, or we can just fight to the death. You choose!":
            sleep(sleeptime)
            await senders.sender(websocket, "", "/pm " + string_tab[2] + ", Command List: https://pastebin.com/qsa3j7Ey")
            # await senders.sender(websocket, "", "/pm " + string_tab[2] + ", Showdown Battle Bot. Active for "
            #                                                            + ", ".join(formats[:-1]) + " and "
            #                                                            + formats[-1] + ".")
            # sleep(sleeptime)
            # await senders.sender(websocket, "", "/pm " + string_tab[2] + ", Please challenge me to test your skills.")
            sleep(sleeptime)
        else:
            sleep(sleeptime)
            await senders.sender(websocket, "", "/pm " + string_tab[2] +
                                 ", Unknown command, type \"Me and you can rule this city spiderman, or we can just fight to the death. You choose!\" for help.")
            sleep(sleeptime) #YOU NEED THAT COMMA
            
    elif string_tab[1] == "init":
        search = False #Battle started   - debug this part...
        #avoid "deinit" match
    # elif "popup|Couldn't search" in message and usage == 2 and "|c|" not in message:
    #     nb_fights -= 1 #undo that
    #before search wasnt working - not a high priority issue now

    # if "throttle-notice" in message and "|c|" not in message:

    if "battle" in string_tab[0]:
        # Battle concern message.
        await battle_tag(websocket, message, usage)
