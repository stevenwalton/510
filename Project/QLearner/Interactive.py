import abc 
import sys
import time
import ctypes
import numpy as np
import pyglet
from pyglet import gl
from pyglet.window import key as keycodes
import retro

class Interactive(abc.ABC):
    '''
    Base class for interactive gym environments
    '''
    def __init__(self, env, sync=True, tps=60, aspect_ratio=None):
        obs = env.reset()
        self.image = self.get_image(obs, env)
        assert len(self.image.shape) == 3 and self.image.shape[2] == 3, 'Must be an RGB image!'
        image_height, image_width = self.image.shape[:2]

        if aspect_ratio is None:
            aspect_ratio = image_width / image_height

        '''
        Let's guess a screen size that doesn't distort too much
        '''
        platform = pyglet.window.get_platform()
        display = platform.get_default_display()
        screen = display.get_default_screen()
        max_width = screen.width * 0.9
        max_height = screen.height * 0.9
        win_width = image_width
        win_height = int(win_width / aspect_ratio)

        while win_width > max_width or win_height > max_height:
            win_width //= 2
            win_height //= 2
        while win_width < max_width / 2 and win_height < max_height / 2:
            win_width *= 2
            win_height *= 2

        win = pyglet.window.Window(width=win_width, height=win_height)

        self.key_handler = pyglet.window.key.KeyStateHandler()
        win.push_handlers(self.key_handler)
        win.on_close = self.on_close

        gl.glEnable(gl.GL_TEXTURE_2D)
        self.texture_id = gl.GLuint(0)
        gl.glGenTextures(1, ctypes.byref(self.texture_id))
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture_id)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA8, image_width, image_height, 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, None)

        self.env = env
        self.win = win

        self.key_previous_states = {}
        self.steps = 0
        self.episode_steps = 0
        self.episode_returns = 0
        self.prev_episode_returns = 0

        self.tps = tps
        self.sync = sync
        self.current_time = 0
        self.sim_time = 0
        self.max_sim_frames_per_update = 4

    def update(self, dt):
        '''
        caps the number of frames being rendered 
        '''
        max_dt = self.max_sim_frames_per_update / self.tps
        if dt > max_dt:
            dt = max_dt

        ''' Make sum catch up '''
        self.current_time += dt
        while self.sim_time < self.current_time:
            self.sim_time += 1 / self.tps

            keys_clicked = set()
            keys_pressed =set()
            for key_code, pressed in self.key_handler.items():
                if pressed:
                    keys_pressed.add(key_code)
                if not self.key_previous_states.get(key_code, False) and pressed:
                    keys_clicked.add(key_code)
                self.key_previous_states[key_code] = pressed

            if keycodes.ESCAPE in keys_pressed:
                self.on_close()

            ''' repeat keys for as long as they are held '''
            inputs = keys_pressed
            if self.sync:
                inputs = keys_clicked

            keys = []
            for keycode in inputs:
                for name in dir(keycodes):
                    if getattr(keycodes, name) == keycode:
                        keys.append(name)

            act = self.keys_to_act(keys)

            if not self.sync or act is not None:
                obs, rew, done, info = self.env.step(act)
                self.image = self.get_image(obs, self.env)
                self.episode_returns += rew
                self.steps += 1
                self.episode_steps += 1
                np.set_printoptions(precision=2)
                if self.sync:
                    done_int = int(done)
                    print(f'steps={self.steps} episode_steps={self.episode_steps} rew={rew} episode_returns={self.episode_returns} done={done_int}')
                elif self.steps % self.tps == 0 or done:
                    episode_returns_delta = self.episode_returns - self.prev_episode_returns
                    self.prev_episode_returns = self.episode_returns
                    print(f'steps={self.steps} episode_steps={self.episode_steps} episode_returns_delta={episode_returns_delta} episode_returns={self.episode_returns}')
                if done:
                    self.env.reset()
                    self.episode_steps = 0
                    self.episode_returns = 0
                    self.prev_episode_returns = 0

    def draw(self):
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture_id)
        video_buffer = ctypes.cast(self.image.tobytes(), ctypes.POINTER(ctypes.c_short))
        gl.glTexSubImage2D(gl.GL_TEXTURE_2D, 0, 0, 0, self.image.shape[1], self.image.shape[0], gl.GL_RGB, gl.GL_UNSIGNED_BYTE, video_buffer)

        x = 0
        y = 0
        w = self.win.height
        h = self.win.height

        pyglet.graphics.draw(
            4,
            pyglet.gl.GL_QUADS,
            ('v2f', [x, y, x + w, y, x + w, y + h, x, y + h]),
            ('t2f', [0, 1, 1, 1, 1, 0, 0, 0]),
        )

    def on_close(self):
        self.env.close()
        print("Closing game")
        sys.exit(0)

    @abc.abstractmethod
    def get_image(self, obs, venv):
        '''
        given an observation and the environment, return rgb array to display
        '''
        pass

    @abc.abstractmethod
    def keys_to_act(self, keys):
        '''
        given list of keys from user input, produce gym action to pass to envirnment
        Sync environments: keys is a list of keys that have been pressed since
        last step.

        Async environments: keys is a list of keys currently held down
        '''
        pass

    def run(self):
        '''
        run interactive window until user quits by pressing Esc
        '''
        prev_frame_time = time.time()
        while True:
            self.win.switch_to()
            self.win.dispatch_events()
            now = time.time()
            self.update(now - prev_frame_time)
            prev_frame_time = now
            self.draw()
            self.win.flip()
