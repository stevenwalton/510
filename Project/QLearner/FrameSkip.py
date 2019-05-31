import retro
import gym

class Frameskip(gym.Wrapper):
    def __init__(self, env, skip=4):
        super().__init__(env)
        self.skip = skip

    def reset(self):
        return self.env.reset()

    def step(self, act):
        total_reward = 0.0
        done = None
        for i in range(self.skip):
            obs, reward, done, info = self.env.step(act)
            total_reward += reward
            if done:
                break

        return obs, total_reward, done, info
