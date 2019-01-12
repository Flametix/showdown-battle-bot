# showdown-battle-bot

Socket (Metronome) battle bot for the pokemon simulator [Pokemon Showdown](http://pokemonshowdown.com). Developped in Python 3.5.X

### Requirements
- python 3.5.X
- requests
- asyncio
- websockets

### Supported formats
- gen7metronomebattle

(gen8metronomebattle upcoming)

### Installation
```
pip3 install -r requirement.txt
./main 
```
future me: run the main file

### How does that works
The bot works in three parts : I/O process, game engine and """AI""".
  
I/O process is about sending and receiving datas from Showdown's servers.  
Showdown use websockets to send datas, therefor I use them too. 
Then all I had to do is to follow the [Pokemon Showdown Protocol](https://github.com/Zarel/Pokemon-Showdown/blob/master/PROTOCOL.md). 
Tricky part is about connection, the protocol is not very precise about it.
To be simple, once connected to the websockets' server, you receive a message formated this way : `|challstr|<CHALLSTR>`. 
Then you send a post request to `https://play.pokemonshowdown.com/action.php` with the `<CHALLSTR>` but web-formated (beware of special characters) and the ids of the bot.
In the answer, you have to extract the `assertion` part.
Finally, you have to send a websrequest this format : `/trn <USERNAME>,0,<ASSERTION>` where `<USERNAME>` is the one you gave previously and `<ASSERTION>` the one you extract just before.
For more informations about it, check the [login.py](src/login.py) file.

(IO process is pretty important, I agree)

Game engine is about simulate battles, teams and pokemons. 
For each battle, an object is created and filled with informations sent by Showdown's servers. 
For the unkowns informations (enemy's team), moves are filled thanks to a file take from source code where moves and pokemons are listed.
See [data](data/) forlder for more informations.

(The engine is cool and very involved with the AI but for metronome purposes we don't use it.)

Bot's brain, the AI:

(I forked this bot and destroyed its ai. Whenever it makes a move it says "/choose default". This lets it play doubles when it couldn't before.)
