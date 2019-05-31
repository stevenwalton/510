import retro

import FrameSkip
import TimeLimit
import Brute

class BruteForce():
    def __init__(self,
                 game='Airstriker-Genesis',
                 max_episode_steps=4500,
                 timestep_limit=100_000_000,
                 state=retro.State.DEFAULT,
                 scenario=None,
                 save=False,
                 savename="best.bk2",
                 fs_skip=4,
                 render=False):

        self.game = game
        self.max_episode_steps = max_episode_steps
        self.timestep_limit = timestep_limit
        self.state = state
        self.scenario = scenario
        self.save=save
        self.savename = savename
        self.fs_skip=fs_skip
        self.render=render
        if ".bk2" not in self.savename[-4:]:
            self.savename += ".bk2"

        self.timesteps = 0
        self.best_reward = float('-inf')

        self.env = retro.make(game=game, 
                              state=state, 
                              use_restricted_actions=retro.Actions.DISCRETE,
                              scenario=scenario)
        self.env = FrameSkip.Frameskip(self.env, skip=self.fs_skip)
        self.env = TimeLimit.TimeLimit(self.env, max_episode_steps=self.max_episode_steps)

    def start(self):
        brute = Brute.Brute(self.env, max_episode_steps=self.max_episode_steps,render=self.render)
        while True:
            acts, reward = brute.run()
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
