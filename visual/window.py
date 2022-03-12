import pygame
from random import shuffle

import visual.colors as vc
import importlib
import keyboard
import math


class Window:
    WIDTH = 0
    HEIGHT = 0
    FPS = 1

    def __init__(self, array: list[int], algorithm: str):

        Window.FPS *= round(math.log2(len(array))) ** 2
        self.default_fps = Window.FPS

        self.clock = pygame.time.Clock()
        self.running = False

        self.array = array
        self.algorithm = algorithm
        self.sorted = False

        pygame.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        Window.WIDTH, Window.HEIGHT = self.screen.get_size()

        self.screen.fill(vc.Color.BLACK)
        pygame.display.set_caption("Sorting Visualizer : " + algorithm)

    def _refresh_background(self) -> None:
        self.screen.fill(vc.Color.BLACK)

    def _refresh_all(self) -> None:
        pygame.event.pump()  # I still don't know why, but removing this line of code makes the program crash at the middle of the animation (lol)
        pygame.display.update()
        pygame.display.flip()
        self._refresh_background()
        self.show_speed()
        self.clock.tick(Window.FPS)

    def _draw_rods(self, important_rods: list[int] = []) -> None:
        rod_width = (Window.WIDTH - 100 - len(self.array)) / len(self.array)
        rod_height = (Window.HEIGHT - 100) / max(self.array) - 1

        x_coord = Window.WIDTH / 2 - (len(self.array) * (rod_width + 1)) / 2
        for k in self.array:
            if k in important_rods:
                pygame.draw.rect(
                    self.screen,
                    vc.Color.RED,
                    (
                        x_coord,
                        Window.HEIGHT - k * rod_height,
                        rod_width,
                        k * rod_height,
                    ),
                )
            else:
                pygame.draw.rect(
                    self.screen,
                    vc.Color.WHITE,
                    (
                        x_coord,
                        Window.HEIGHT - k * rod_height,
                        rod_width,
                        k * rod_height,
                    ),
                )
            x_coord += rod_width + 1

    def _draw_some_rods(
        self, array: list[int], important_rods: list[int] = [], do_others: bool = False
    ) -> None:
        rod_width = (Window.WIDTH - 100 - len(self.array)) / len(self.array)
        rod_height = (Window.HEIGHT - 100) / max(self.array) - 1

        x_coord = Window.WIDTH / 2 - (len(self.array) * (rod_width + 1)) / 2
        for k in self.array:
            if k in array:
                pygame.draw.rect(
                    self.screen,
                    vc.Color.GREEN,
                    (
                        x_coord,
                        Window.HEIGHT - k * rod_height,
                        rod_width,
                        k * rod_height,
                    ),
                )
            else:
                pygame.draw.rect(
                    self.screen,
                    vc.Color.WHITE,
                    (
                        x_coord,
                        Window.HEIGHT - k * rod_height,
                        rod_width,
                        k * rod_height,
                    ),
                )
            x_coord += rod_width + 1

    def sorted_animation(self) -> None:
        """Little animation that plays at the end of a sorting animation"""
        tmp = []
        for k in self.array:
            tmp.append(k)
            self._draw_some_rods(tmp, do_others=True)
            self._refresh_all()
            self.handle_quit_keyboard()
            self.handle_speed_keys()

    def show_total_time(self, total_time: int) -> None:
        print(
            vc.CMDColors.BLUE
            + "Total time: "
            + str(total_time)
            + "ms"
            + vc.CMDColors.RESET
        )
        
    def show_speed(self) -> None:
        """Show the speed of the animation (Window.FPS) but adapted to 1x at the top left corner"""
        font = pygame.font.SysFont("Arial", 30)
        text = font.render("Speed: x" + str(round(Window.FPS / self.default_fps, 3)), True, vc.Color.WHITE)
        text_rect = text.get_rect()
        text_rect.left = 10
        text_rect.top = 10
        self.screen.blit(text, text_rect)

    def handle_speed_keys(self) -> None:
        """Must be in a loop"""
        dec = 0
        try:
            if keyboard.is_pressed("right"):
                if dec == 0:
                    Window.FPS += 1
                    dec += 1
                else:
                    dec += 1
            if keyboard.is_pressed("left"):
                if dec == 0:
                    Window.FPS -= 1
                    dec += 1
                else:
                    dec += 1
        except:
            pass

    def handle_quit_keyboard(self) -> None:
        """Must be put in a loop !!!!"""
        try:
            if keyboard.is_pressed("esc"):
                self.running = False
                pygame.quit()
                quit()
        except:
            pass

    def start(self):
        if self.running:
            raise RuntimeError("Window is already running")
        else:
            self.running = True
            while self.running:

                # Tick
                self.clock.tick(Window.FPS)

                # Handling events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False

                try:
                    if keyboard.is_pressed("space"):
                        if not self.sorted:
                            print("\nSorting...")

                            # Sort the array
                            total_time = 0
                            for step, important_rods, time in ArrayTool.sort(
                                self.algorithm, self.array
                            ):
                                if (
                                    step is not None
                                    and len(step) > 0
                                    and not (len(step) == 1 and step[0] != -1)
                                ):
                                    self.array = [s for s in step if s != -1]
                                else:
                                    continue

                                total_time = time

                                # In a case where the yielded array is not the same length as the original array (e.g Merge Sort)

                                # Refreshing EVERYTHING
                                self._draw_rods(important_rods)
                                self._refresh_all()
                                self.handle_quit_keyboard()
                                self.handle_speed_keys()

                            self.sorted_animation()
                            print(vc.CMDColors.GREEN + "Sorted!" + vc.CMDColors.RESET)
                            self.sorted = True
                            self.show_total_time(total_time)

                        # Resetting the array
                        elif self.sorted:
                            shuffle(self.array)
                            self.sorted = False
                except:
                    pass

                # Refreshing EVERYTHING
                self._draw_rods()
                self._refresh_all()
                self.handle_quit_keyboard()
                self.handle_speed_keys()


class ArrayTool:
    @staticmethod
    def sort(algorithm: str, array: list[int]):
        steps = None

        alg = algorithm.replace(" ", "_").lower()
        module = importlib.import_module(f"algorithms.{alg}")
        steps = module.sort(array)

        return steps
