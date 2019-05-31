import retro

import FrameSkip
import TimeLimit
import Q

class QAgent():
    def __init__(self,
                 game,
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
                 max_episode_steps=4500,
                 ):
        self.game = game
        self.max_episode_steps = max_episode_steps
        self.timestep_limit = int(timestep_limit)
        self.state = state
        self.discount = discount
        self.gamma = gamma
        self.gambler_percent = gambler_percent
        self.scenario = scenario
        self.save=save
        self.exploration_constant = exploration_constant
        self.max_depth = max_depth
        self.render=render
        if save is not None and ".bk2" not in self.save[-4:]:
            self.save+= ".bk2"

        self.timesteps = 0
        self.best_reward = float('-inf')

        self.env = retro.make(game=game, 
                              state=state, 
                              use_restricted_actions=retro.Actions.DISCRETE,
                              scenario=scenario)
        if fs_skip > 0:
            self.env = FrameSkip.Frameskip(self.env, skip=fs_skip)
        self.env = TimeLimit.TimeLimit(self.env, max_episode_steps=self.max_episode_steps)

    def start(self):
        q = Q.Q(self.env, 
                max_episode_steps=self.max_episode_steps,
                render=self.render, 
                gambler_percent=self.gambler_percent, 
                discount=self.discount,
                gamma=self.gamma,
                exploration_constant=self.exploration_constant, 
                max_depth=self.max_depth)
        while True:
            acts, reward = q.run()
            self.timesteps += len(acts)
            if reward > self.best_reward:
                print(f"New best reward {reward} from {self.best_reward}")
                self.best_reward = reward
                if (self.save is not None):
                    print("Saving",self.save)
                    self.env.unwrapped.record_movie(self.save)
                    self.env.reset()
                    for act in acts:
                        self.env.step(act)
                    self.env.unwrapped.stop_record()
            if self.timesteps > self.timestep_limit:
                print("Timed out")
                break
