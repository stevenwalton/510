# CIS 510: Multi-Agent Systems Project
--------------------------------------
This project runs a basic Q Learner through OpenAI's retro environment. A few ROMs
are provided with retro. By default the program will run Airstriker Genesis, which
is one of the included ROMs. 

For the most basic run, use the command
```
python main.py -q
```
This will run the basic Q Learner. For a full list of options use the help flag.
All learning variables are modifiable. Default values are also shown in help. 

## Requirements
This code has been tested on Python 3.7.1
We use the following modules
- gym
- gym-retro
- numpy

These should be able to be loaded with the requirements file. Versions are also
specified in there. Make sure you install `gym-retro` and not `retro`. 

## Help

```bash
$ python main.py -h
usage: OpenAI Retro Learner [-h] (-i | -b | -r | -q) [--game GAME]
                            [--state STATE] [--scenario SCENARIO] [-s SAVE]
                            [--render] [-fs] [--discount DISCOUNT]
                            [--gamma GAMMA] [--depth DEPTH]
                            [--explore EXPLORE] [--gambler GAMBLER]

optional arguments:
  -h, --help            show this help message and exit

(Required) Learner Type:
  -i, --interactive     Run the game interactively (default: False)
  -b, --brute           Run the game with retro's brute forcer (default:
                        False)
  -r, --random          Run the game with random 'learner' (default: False)
  -q, --qlearn          Run the game with Q-Learner (default: False)

Retro Arguments:
  --game GAME           Specify the game to run. (default: Airstriker-Genesis)
  --state STATE         Specify the starting state. (default: State.DEFAULT)
  --scenario SCENARIO   Specify the scenario (default: None)
  -s SAVE, --save SAVE  Save best results to a bk2 file (default: None)
  --render              Render game (unstable) (default: False)
  -fs , --frame-skip    Specify the number of frame skips (advanced) (default:
                        4)

Learning Options:
  --discount DISCOUNT   Specify the discount for the learner (default: 0.8)
  --gamma GAMMA         Specify the learning rate of the learner (default:
                        0.8)
  --depth DEPTH         Q Learning option: max depth we lookahead (default: 1)
  --explore EXPLORE     Q Learning option: how we weight our exploration
                        function. f(u,v) = u + k/v (default: 0)
  --gambler GAMBLER     Q Learning option: changes how often we explore random
                        actions. The higher the number the less exploration we
                        do. Values >=1 do not explore. (default: 0.8)
```
Interactive, Brute, Random, and QLearn are options in how to play the game.
One must be supplied.

Interactive isn't actually a learner, but lets you play the game. Just in case
you want to ensure that you are still superior than the robot overloards.

Brute uses a brute focing tactic, focusing on greedy strategies. 

Random also isn't a learner. It just does random actions. If an agent isn't better
than this, then something is very wrong.

QLearn is a basic Q-Learner. There are variables to modify the exploration function,
how many steps we lookahead, discount, and learning rate. We follow the
Bellman Equations for this learner. 

### Included ROMs
According to the [retro documentation](https://retro.readthedocs.io/en/latest/)
there are other included ROMs, but I could not find any other than 
Airstriker-Genesis. If you wish to play other games you must find the ROM 
yourself. You can then import them with 

```bash
$ python -m retro.import /path/to/ROM_directory
```
You should see if a ROM correctly imports. I have found this to not always work,
even if the file type/extension is correct. You may have to try a few ROMs.

### Tips
Frame Skip allows the game to skip a few frames before taking an action. This
can help in minimizing the lookahead. For a fast paced game it is advised to keep
this value low or 0. For a slow moving game it may be better to increase this.

Games where there are a lot more options, it may be advised to do further lookaheads.
While this will slow down the game and increase memory usage it can really help
it learn faster. 


### Integration Notes:
Some integration information is difficult to find. This is to help keep things
condense and be used as a later reference.

If you are trying to integrate a game that is not already integrated into the 
environment note that you must add the system's memory address number to any
hex numbers you have obtained. For example, if you are integrating a SNES
game you must lookup 
[this file](https://github.com/openai/retro/blob/master/cores/snes.json)
where you'll notice a `rambase` number (8257536). 

So if you have grabbed the hex value `0x000E00` (coins in SMK) then you need to
not only convert it to a decimal number (3584) but add the rambase number to it
(8261120). 

Certain RAM values also will not increment by one or may do weird things. For
example, the SMK value for a lap you have to subtract 128 from the RAM address
to get the correct lap number. Or to get your current rank you have to divide
the address's value by 2 and then add 1. 

You can also use Lua scripts to help with these complicated issues. There are 
examples in retro's source. Search in `retro/data/stable` for `*.lua` files.
