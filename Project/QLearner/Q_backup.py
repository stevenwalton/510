import gym
import retro
import numpy as np
import random
import Node
import FrameSkip

class QAgent(gym.Wrapper):
    def __init__(self,
            game='Airstriker-Genesis',
            state=retro.State.DEFAULT,
            scenario=None,
            max_episode_steps=4500,
            timestep_limit=100_000_000,
            discount=0.8,
            gamma=0.8,
            save=False,
            savename="best.bk2",
            fs_skip=4,
            render=False,
            gamble_percent=0.8):

        self.save = save
        self.savename = savename
        self.render=render
        self.discount = discount
        self.gamma = gamma
        self.gamble_percent = gamble_percent
        if ".bk2" not in self.savename[-4:]:
            self.savename += ".bk2"

        self.best_reward = float('-inf')
        self.node_count = 1
        self.max_episode_steps=max_episode_steps
        self.timestep_limit = timestep_limit
        self.root = Node.Node()

        self.env = retro.make(game=game,
                              state=state,
                              scenario=scenario)
        #self.env = FrameSkip.Frameskip(self.env, skip=fs_skip)

    def select_actions(self):
        node = self.root
    
        acts = []
        steps = 0
        while steps < self.max_episode_steps:
            if node is None:
                # we've fallen off the explored area of the tree, just select random actions
                act = self.env.action_space.sample()
            else:
                if random.random() > self.gamble_percent:
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

                    #for act in range(self.env.action_space.n):
                    #    if node is not None and act in node.children:
                    #        value = node.children[act].value
                    #        all_children = node.children
                    #        for next_act in range(all_children):
                    #            if node is not None and next_act in all_children.children:
                    #                lookahead_val[next_act] = all_children.children[next_act].value
                    #            else:
                    #                lookahead_val[next_act] = -np.inf
                    #        best_lookahead_value = max(lookahead_val.values())
                    #        best_lookahead_acts = [
                    #                next_act for next_act, value in lookahead_val.items() if value == best_lookahead_value
                    #                ]
                    #    else:
                    #        lookahead_value = -np.inf
                    #        act_value[act] = -np.inf
                    #    best_value = max(act_value.values()) + self.discount*max(best_lookahead_value.values())
                    #    best_acts = [
                    #        act for act, value in act_value.items() if value == best_value
                    #    ]
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



    def run(self):
        acts = self.select_actions()
        steps, total_reward = self.rollout(acts)
        executed_acts = acts[:steps]
        self.node_count += self.update_tree(executed_acts, total_reward)
        return executed_acts, total_reward

    def start(self):
        while True:
            acts, reward = self.run()
            self.timesteps += len(acts)
            if reward > self.best_reward:
                print(f"New best reward {reward} from {self.best_reward}")
                self.best_reward = reward
                if (self.save):
                    self.env.unwrapped.record_movie(self.savename)
                    self.env.reset()
                    for act in acts:
                        self.env.step(act)
                    self.env.unwrapped.stop_record()
            if self.timesteps > self.timestep_limit:
                print("Timed out")
                break

