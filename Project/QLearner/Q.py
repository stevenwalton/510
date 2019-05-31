"""
Most of this is taken from the brute force learner, which is a greedy learner.
We have implemented a value learning reward with one-step lookahead.
"""

import random

import numpy as np
import retro
import gym

import Node


class Q:
    """
    Implementation Value Learner with one step lookahead

    Creates and manages the tree storing game actions and rewards
    """

    def __init__(self, 
                 env, 
                 max_episode_steps, 
                 render,
                 gambler_percent,
                 discount,
                 gamma,
                 exploration_constant,
                 max_depth):
        self.node_count = 1
        self.root = Node.Node()
        self.env = env
        self.max_episode_steps = max_episode_steps
        self.render=render
        self.gambler_percent = np.float(gambler_percent)
        self.discount = np.float(discount)
        self.gamma = gamma
        self.max_depth = max_depth
        self.k = exploration_constant

    def run(self):
        acts = self.select_actions()
        steps, total_reward = self.rollout(acts)
        executed_acts = acts[:steps]
        self.node_count += self.update_tree(executed_acts, total_reward)
        return executed_acts, total_reward

    def exploration_function(self,u,n):
        """
        u = value estimate
        n = visit
        """
        return u + self.k/n

    def update_values(self, node, value,step):
        """
        Updates the values with a max depth using Bellman Equation
        """
        step += 1
        if step > self.max_depth and node is not None and act in node.children:
            max_val = max(node.children[act].values())
            best_acts = [
                    act for act, value in act_value.items() if value == max_val
                    ]
            best_pick = None
            best_val = -np.inf
            for act in node.children:
                value = exploration_function(node.children[act].value,node.children[act].visits)
                if value > best_val:
                    best_val = val
                    best_pick = act
                
            return self.gamma*(update_values(node.children[best_pick].children, best_val, step) + self.discount*max_value) + value
        else:
            return value


    def select_actions(self):
        """
        Select actions from the tree

        We will use the Bellman equation to update our values and pick the best acts
        """
        node = self.root
    
        acts = []
        steps = 0
        while steps < self.max_episode_steps:
            if node is None:
                # we've fallen off the explored area of the tree, just select random actions
                act = self.env.action_space.sample()
            else:
                # Gambler
                if random.random() > self.gambler_percent:
                    act = self.env.action_space.sample()
                # Book keeper
                else:
                    act_value = {}
                    for act in range(self.env.action_space.n):
                        if node is not None and act in node.children:
                            act_value[act] = self.update_values(node,0,0)
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


