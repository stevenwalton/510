import gym
import retro
import math
import random 
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from collections import namedtuple
from itertools import count
from PIL import Image
#
#import torch
#import torch.nn as nn
#import torch.optim as optim
#import torchvision.transforms as T
import argparse

# Our functions
import RetroInteractive as RI
import BruteForce as B
import Random as R
import QAgent as Q

def arglist():
    '''
    Function to take care of the arguments. Here to make things cleaner
    '''
    parser = argparse.ArgumentParser(prog="OpenAI Retro Learner", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # Learners
    lt = parser.add_argument_group("(Required) Learner Type")
    learnerType = lt.add_mutually_exclusive_group(required=True)
    learnerType.add_argument('-i','--interactive', default=False, action='store_true', 
            help="Run the game interactively")
    learnerType.add_argument('-b','--brute', default=False, action='store_true', 
            help="Run the game with retro's brute forcer")
    learnerType.add_argument('-r','--random', default=False, action='store_true', 
            help="Run the game with random 'learner'")
    learnerType.add_argument('-q','--qlearn', default=False, action='store_true', 
            help="Run the game with Q-Learner")
    # Retro options
    retro_opts = parser.add_argument_group("Retro Arguments")
    retro_opts.add_argument('--game', default='Airstriker-Genesis', 
            help="Specify the game to run.")
    retro_opts.add_argument('--state', default=retro.State.DEFAULT, 
            help="Specify the starting state.")
    retro_opts.add_argument('--scenario', default=None, 
            help="Specify the scenario")
    #retro_opts.add_argument('-s','--save', default=False, action='store_true',
    retro_opts.add_argument('-s', '--save', default=None,
            help="Save best results to a bk2 file")
    retro_opts.add_argument('--timestep-limit', default=100_000_000,
            help="Set timestep limit")
    #retro_opts.add_argument('--savename', default='best.bk2', type=str,
    #        help="Name of bk2 output file")
    retro_opts.add_argument('--render', default=False, action='store_true',
            help="Render game (unstable)")
    retro_opts.add_argument('-fs','--frame-skip', default=4, type=int,
            metavar='', help="Specify the number of frame skips (advanced)")
    #retro_opts.add_argument('--load', default=None,
    #         help="Load a bk2 file and learn from last state")
    # Learning options
    learning_opts = parser.add_argument_group("Learning Options")
    learning_opts.add_argument('--discount', default=0.8, type=np.float,
            help="Specify the discount for the learner")
    learning_opts.add_argument('--gamma', default=0.8, type=np.float,
            help="Specify the learning rate of the learner")
    learning_opts.add_argument('--depth', default=1, type=int,
            help="Q Learning option: max depth we lookahead")
    learning_opts.add_argument('--explore', default=0, type=int,
            help="Q Learning option: how we weight our exploration function. f(u,v) = u + k/v")
    learning_opts.add_argument('--gambler', default=0.8, type=np.float,
            help="Q Learning option: changes how often we explore random actions. The higher the number the less exploration we do. Values >=1 do not explore.")
                    
    return parser.parse_args()

# Not currently working
#def load_state(load_file):
#    #assert(".bk2" in load_file[:-4]),"Load file must be of type .bk2"
#    load = retro.Movie(load_file)
#    load.step()
#    env = retro.make(game=load.get_game(),
#                     state=None,
#                     use_restricted_actions=retro.Actions.ALL,
#                     players=load.players)
#    env.initial_state = load.get_state()
#    env.reset()
#    while load.step():
#        keys = []
#        for i in range(len(env.buttons)):
#            keys.append(load.get_key(i,0))
#        obs, reward, done, info = env.step(keys)
#        saved_state = env.em.get_state()
#    return saved_state


def run_interactive(game,
                    state,
                    scenario,
                    record):
    '''
    Run the game interactively
    '''
    ia = RI.RetroInteractive(game=game, state=state, scenario=scenario)
    ia.run()

def run_brute(game,
              state,
              scenario,
              save,
              savename,
              fs_skip,
              render):
    '''
    Brute force algorithm to learn
    '''
    b = B.BruteForce(game=game, state=state, scenario=scenario, save=save, savename=savename,fs_skip=fs_skip, render=render)
    b.start()

def run_random(game,
               state,
               scenario):
    r = R.RandomAgent(game=game, state=state,scenario=scenario)
    r.run()

def run_q_agent(game,
                state,
                scenario,
                discount,
                gamma,
                save,
                fs_skip,
                render,
                exploration_constant,
                max_depth,
                gambler_percent,
                timestep_limit,
                ):
    '''
    Runs our Q Learning algorithm
    '''
    q = Q.QAgent(game=game, state=state, scenario=scenario, discount=discount, gamma=gamma, save=save, fs_skip=fs_skip, render=render, exploration_constant=exploration_constant, max_depth=max_depth,gambler_percent=gambler_percent, timestep_limit=timestep_limit)
    q.start()

def main():
    args = arglist()
    #if (args.load is not None):
    #    args.state = load_state(args.load)
    if(args.interactive): # Interactive game
        run_interactive(game=args.game, state=args.state, scenario=args.scenario)
    elif(args.brute): # Brute forcer (greedy solver)
        run_brute(game=args.game, state=args.state, scenario=args.scenario, save=args.save, fs_skip=int(args.frame-skip), render=args.render)
    elif(args.random): # Random player
        run_random(game=args.game, state=args.state, scenario=args.scenario)
    elif(args.qlearn): # Simple Q learner
        run_q_agent(game=args.game, state=args.state, scenario=args.scenario, discount=args.discount, gamma=args.gamma, save=args.save, fs_skip=args.frame_skip,render=args.render,exploration_constant=args.explore, max_depth=args.depth,gambler_percent=args.gambler,timestep_limit=args.timestep_limit)
    else:
        print("==================================================")
        print("You must supply a method to interact with the game")
        print("==================================================")
        parser.print_help()
        exit(1)


if __name__ == '__main__':
    main()
