#-*- cording: utf-8 -*-

import pygame.mixer

class AudioPlayerPygame(object):
    def __init__(self, music_name=None):
        pygame.mixer.init()

        self.__init_flag = False

        if music_name is not None:
            self.set_music(music_name)
        
    def set_music(self, music_name):
        self.__init_flag = False
        try:
            self.__sound = pygame.mixer.Sound(music_name)

        except pygame.error:
            print('no file', music_name)

        else:
            print('sound length = ', self.__sound.get_length())
            print('sound volume = ', self.__sound.get_volume())
            self.__init_flag = True

    def play(self, loop=False):
        if self.__init_flag == False:
            print('sound not inited yet')
            return

        if loop:
            loops = -1
        else:
            loops = 0

        self.__sound.play(loops=loops)

    def stop(self):
        if self.__init_flag == False:
            print('sound not inited yet')
            return

        self.__sound.stop()

if __name__ == '__main__':
    audio = AudioPlayerPygame('../sound/lamp-oshizu.wav')
    audio.play(loop=True)
    input()
    audio.stop()
    audio.set_music('../sound/tanuki.wav')
    audio.play(loop=False)
    print('audio_stoped!')
    input()
    print('test end')
    
    

#    pygame.mixer.init()
#    pygame.mixer.music.load('test.mp3')
#    pygame.mixer.music.play(1)
