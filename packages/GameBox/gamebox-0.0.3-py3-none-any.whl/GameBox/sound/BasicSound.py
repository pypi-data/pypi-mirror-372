import pygame

class Sound:
    def __init__(self):
        # Initialize pygame mixer
        pygame.mixer.init()
        self.sounds = {}
        self.music_playing = False

    def load_sound(self, name: str, filepath: str):
        """
        Load a sound effect into memory.
        name -> reference key for later
        filepath -> path to .wav/.ogg/.mp3
        """
        self.sounds[name] = pygame.mixer.Sound(filepath)

    def play_sound(self, name: str, loops=0):
        """
        Play a loaded sound effect.
        loops = 0 plays once, -1 loops forever
        """
        if name in self.sounds:
            self.sounds[name].play(loops=loops)
        else:
            print(f"[Sound] '{name}' not found!")

    def stop_sound(self, name: str):
        """
        Stop a specific sound effect if it is playing.
        """
        if name in self.sounds:
            self.sounds[name].stop()

    def load_music(self, filepath: str):
        """
        Load a background music track (only one at a time).
        """
        pygame.mixer.music.load(filepath)

    def play_music(self, loops=-1):
        """
        Play loaded background music.
        loops=-1 means infinite loop.
        """
        pygame.mixer.music.play(loops)
        self.music_playing = True

    def stop_music(self):
        """
        Stop background music.
        """
        pygame.mixer.music.stop()
        self.music_playing = False

    def pause_music(self):
        """
        Pause background music.
        """
        pygame.mixer.music.pause()

    def resume_music(self):
        """
        Resume paused background music.
        """
        pygame.mixer.music.unpause()
