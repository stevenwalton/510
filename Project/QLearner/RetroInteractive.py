import retro
import gym
import Interactive as I
import pyglet
from pyglet import gl
from pyglet.window import key as keycodes


class RetroInteractive(I.Interactive):
    '''
    interactive setup for retro games
    '''
    def __init__(self, game, state, scenario):
        env = retro.make(game=game, state=state, scenario=scenario)
        self.buttons = env.buttons
        super().__init__(env=env, sync=False, tps=60, aspect_ratio=4/3)

    def get_image(self, obs, env):
        return env.render(mode='rgb_array')

    def keys_to_act(self, keys):
        inputs = {
            None: False,

            'BUTTON': 'Z' in keys,
            'A': 'Z' in keys,
            'B': 'X' in keys,

            'C': 'C' in keys,
            'X': 'A' in keys,
            'Y': 'S' in keys,
            'Z': 'D' in keys,

            'L': 'Q' in keys,
            'R': 'W' in keys,

            'UP': 'UP' in keys,
            'DOWN': 'DOWN' in keys,
            'LEFT': 'LEFT' in keys,
            'RIGHT': 'RIGHT' in keys,

            'MODE': 'TAB' in keys,
            'SELECT': 'TAB' in keys,
            'RESET': 'ENTER' in keys,
            'START': 'ENTER' in keys,
        }
        return [inputs[b] for b in self.buttons]
