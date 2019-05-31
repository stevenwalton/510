"""
Implementation of the Brute from "Revisiting the Arcade Learning Environment:
Evaluation Protocols and Open Problems for General Agents" by Machado et al.
https://arxiv.org/abs/1709.06009

This is an agent that uses the determinism of the environment in order to do
pretty well at a number of retro games.  It does not save emulator state but
does rely on the same sequence of actions producing the same result when played
back.
"""

import random

import numpy as np
import retro
import gym

import Node


EXPLORATION_PARAM = 0.005

class Brute:
    """
    Implementation of the Brute

    Creates and manages the tree storing game actions and rewards
    """

    def __init__(self, env, max_episode_steps, render=False):
        self.node_count = 1
        self.root = Node.Node()
        self.env = env
        self.max_episode_steps = max_episode_steps
        self.render=render

    def run(self):
        acts = self.select_actions()
        steps, total_reward = self.rollout(acts)
        executed_acts = acts[:steps]
        self.node_count += self.update_tree(executed_acts, total_reward)
        return executed_acts, total_reward


    def select_actions(self):
        """
        Select actions from the tree
    
        Normally we select the greedy action that has the highest reward
        associated with that subtree.  We have a small chance to select a
        random action based on the exploration param and visit count of the
        current node at each step.
    
        We select actions for the longest possible episode, but normally these
        will not all be used.  They will instead be truncated to the length
        of the actual episode and then used to update the tree.
        """
        node = self.root
    
        acts = []
        steps = 0
        while steps < self.max_episode_steps:
            if node is None:
                # we've fallen off the explored area of the tree, just select random actions
                act = self.env.action_space.sample()
            else:
                epsilon = EXPLORATION_PARAM / np.log(node.visits + 2)
                if random.random() < epsilon:
                    # random action
                    act = self.env.action_space.sample()
                else:
                    # greedy action
                    act_value = {}
                    for act in range(self.env.action_space.n):
                        if node is not None and act in node.children:
                            act_value[act] = node.children[act].value
                        else:
                            act_value[act] = -np.inf
                    best_value = max(act_value.values())
                    best_acts = [
                        act for act, value in act_value.items() if value == best_value
                    ]
                    act = random.choice(best_acts)
    
                if act in node.children:
                    node = node.children[act]
                else:
                    node = None
    
            acts.append(act)
            steps += 1
    
        return acts
    
    
    def rollout(self, acts):
        """
        Perform a rollout using a preset collection of actions
        """
        total_reward = 0
        self.env.reset()
        steps = 0
        for act in acts:
            if (self.render):
                self.env.render()
            obs, reward, done, info = self.env.step(act)
            steps += 1
            total_reward += reward
            if done:
                break
    
        return steps, total_reward
    
    
    def update_tree(self, executed_acts, total_reward):
        """
        Given the tree, a list of actions that were executed before the game ended, and a reward, update the tree
        so that the path formed by the executed actions are all updated to the new reward.
        """
        self.root.value = max(total_reward, self.root.value)
        self.root.visits += 1
        new_nodes = 0
    
        node = self.root
        for step, act in enumerate(executed_acts):
            if act not in node.children:
                node.children[act] = Node.Node()
                new_nodes += 1
            node = node.children[act]
            node.value = max(total_reward, node.value)
            node.visits += 1
    
        return new_nodes


