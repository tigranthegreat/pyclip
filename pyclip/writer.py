import cv2
import pygame
import numpy as np

import time
import sys
import logging

from movie import MovieBase
from renderer import Renderer, Converter
import progress_bar
import logger


class MovieWriter(MovieBase):

    __instance = None

    def __init__(self):

        if MovieWriter.__instance != None:
            raise Exception(__class__.__name__ + " is a singleton class.")

        MovieBase.__init__(self, None, None, None, None)

        self._display = None

        self._renderer = None

        self._clock = pygame.time.Clock()
        self._video_writer = None

        MovieWriter.__instance = self

    def init_display(self, movie):
        self._width = movie.width
        self._height = movie.height
        self._fps = movie.fps

        self._display = pygame.display.set_mode((movie.width, movie.height), flags=pygame.HIDDEN)
        pygame.display.set_caption("Writer window.")

        self._renderer = Renderer(self._display)

    @staticmethod
    def get_instance():
        return MovieWriter.__instance

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height


MovieWriter()


@logger.movie_writer_log
def export(movie):

    movie_writer = MovieWriter.get_instance()

    movie_writer.init_display(movie)

    movie_writer._video_writer = cv2.VideoWriter("{}.mp4".format(movie.name), cv2.VideoWriter_fourcc(*"mp4v"), 30, (movie.width, movie.height))

    for frame_index in range(1, movie.frame_count + 1):

        # current_clips = [clip for i, clip in movie.get_clip_by_frame_index(frame_index)]

        movie_writer._renderer.clear(movie.background_color)

        # current_frames = []
        # for clip in current_clips:
        #     current_frames.append(next(clip.get_next_frame(), np.empty(0)))
        #
        # for clip, frame in zip(current_clips, current_frames):
        #     movie_writer._renderer.render_frame(movie.width, movie.height, frame, clip.info.trans)
        #

        for i, clip in movie.process_running_clips(frame_index):
            frame = next(clip.get_next_frame())
            movie_writer._renderer.render_frame(movie.width, movie.height, frame, clip.info.trans)

        display_frame = Converter.surface_to_frame(pygame.display.get_surface())

        movie_writer._video_writer.write(display_frame)

        progress_bar.print_progress(frame_index, movie.frame_count, 30)

    # print(time.time() - time1)

    pygame.display.quit()

    return True
