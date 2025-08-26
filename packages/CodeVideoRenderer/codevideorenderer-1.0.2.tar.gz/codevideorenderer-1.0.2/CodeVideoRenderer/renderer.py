from manim import *
from contextlib import contextmanager
from pydantic import validate_call, Field
from typing import Annotated
import random, logging, sys, os, time, string

@validate_call
def CodeVideo(
    # -------------------------------------------------- video name --------------------------------------------------
    video_name: str = "CodeVideo", 

    # ----------------------------------------------------- code -----------------------------------------------------
    code_string: str = None,
    code_file: str = None,
    font: str = 'Consolas',
    language: str = None, 

    # --------------------------------------------------- interval ---------------------------------------------------
    interval_range: tuple[Annotated[float, Field(ge=0.2)], Annotated[float, Field(ge=0.2)]] = (0.2, 0.4), 

    # ---------------------------------------------------- camera ----------------------------------------------------
    camera_floating_maximum_value: Annotated[float, Field(ge=0)] = 0.1,
    camera_move_interval: Annotated[float, Field(ge=0)] = 0.1,
    camera_move_duration: Annotated[float, Field(ge=0)] = 0.5,

    # ---------------------------------------------------- screen ----------------------------------------------------
    screen_scale: float = 0.3
    ):

    if interval_range[0] > interval_range[1]:
        raise ValueError("interval_range[0] must be less than interval_range[1]")

    start_time = time.time()
    logging.basicConfig(level=logging.INFO)
    config.output_file = video_name

    # Camera that smoothly moves to a cursor's position
    class LoopMovingCamera(VGroup):

        def __init__(
            self,
            mob,
            scene,
            move_interval,
            move_duration,
            **kwargs,
        ):
            super().__init__(**kwargs)
            self.mob = mob
            self.scene = scene
            self.move_interval = move_interval
            self.move_duration = move_duration
            self.elapsed_time = 0
            self.is_moving = False  # Indicate whether it is moving
            self.move_progress = 0  # Move progress (0 to 1)
            self.start_pos = None   # Moving start position
            self.target_pos = None  # Moving target position

            self.add_updater(lambda m, dt: self.update_camera_position(dt))

        def update_camera_position(self, dt):
            # If it is moving, handle smooth transition
            if self.is_moving:
                self.move_progress += dt / self.move_duration
                # Calculate current position (interpolation from start to target)
                current_pos = interpolate(
                    self.start_pos,
                    self.target_pos,
                    smooth(self.move_progress)  # Apply smooth transition function
                )
                self.scene.camera.frame.move_to(current_pos)
                
                # Reset status after movement is complete
                if self.move_progress >= 1:
                    self.is_moving = False
                    self.move_progress = 0
                return

            # If not moving, accumulate time to determine whether to start moving
            self.elapsed_time += dt
            if self.elapsed_time >= self.move_interval:
                self.start_pos = self.scene.camera.frame.get_center()  # Record current position
                self.target_pos = self.mob.get_center() + (            # Get target position
                    UP*random.uniform(-camera_floating_maximum_value,camera_floating_maximum_value)+
                    LEFT*random.uniform(-camera_floating_maximum_value,camera_floating_maximum_value)
                )
                self.is_moving = True                                  # Start moving
                self.elapsed_time -= self.move_interval                # Reset timer

    class code_video(MovingCameraScene):
        
        def replace_empty_chars(self, s):
            translator = str.maketrans('', '', string.whitespace)
            return s.translate(translator)
        
        # no manim output
        @contextmanager
        def _no_manim_output(self):
            manim_logger = logging.getLogger("manim")
            original_manim_level = manim_logger.getEffectiveLevel()
            original_stderr = sys.stderr
            try:
                manim_logger.setLevel(logging.WARNING)
                sys.stderr = open(os.devnull, 'w')
                yield
            finally:
                manim_logger.setLevel(original_manim_level)
                sys.stderr = original_stderr

        def construct(self):
            global code_mobject, line_number, code_str

            if code_string and code_file:
                raise ValueError("Only one of code_string and code_file can be passed in")

            # get code string and check if it contains chinese characters or punctuation
            if code_string is not None:
                code_str = code_string.replace("\t", 4*' ')
                if not code_str.isascii():
                    raise ValueError("There are non-English characters in the code, please remove them")
            elif code_file is not None:
                with open(os.path.abspath(code_file), "r") as f:
                    try:
                        code_str = f.read().replace("\t", 4*' ')
                    except UnicodeDecodeError:
                        raise ValueError("There are non-English characters in the code, please remove them") from None
            
            if self.replace_empty_chars(code_str) == '':
                raise ValueError("code is empty")

            # split each line of code, so that can be accessed using xxx[line][column]
            code_str_per_line = code_str.split("\n")

            # initialize cursor
            cursor_width = 0.0005
            cursor = RoundedRectangle(height=0.35, width=cursor_width, corner_radius=cursor_width/2, 
                                      fill_opacity=1, fill_color=WHITE, color=WHITE).set_z_index(2)
            
            # initialize code block
            code_block = Code(code_string=code_str, 
                              language=language, 
                              formatter_style='material', 
                              paragraph_config={'font': font})
            line_numbers = code_block.submobjects[1].set_color(GREY) # line numbers
            code_mobject = code_block.submobjects[2].set_z_index(2) # code

            line_number = len(line_numbers)
            max_char_num_per_line = max([len(code_mobject[i]) for i in range(line_number)])
            output_char_num_per_line = max(20, max_char_num_per_line)

            # occupy block
            # use '#' to occupy, prevent no volume space
            occupy = Code(
                code_string=line_number*(max_char_num_per_line*'#' + '\n'),
                paragraph_config={'font':font},
                language=language
            ).submobjects[2]
            code_line_rectangle = SurroundingRectangle(occupy[0], color="#333333", fill_opacity=1, stroke_width=0).set_z_index(1)
            
            self.camera.frame.scale(screen_scale).move_to(occupy[0][0].get_center())
            self.add(line_numbers[0].set_color(WHITE), code_line_rectangle)
            self.wait()

            cursor.next_to(occupy[0][0], LEFT, buff=-cursor_width) # cursor move to the left of occupy block
            self.add(cursor)

            # create loop moving camera
            moving_cam = LoopMovingCamera(
                mob=cursor,
                scene=self,
                move_interval=camera_move_interval,
                move_duration=camera_move_duration
            )
            self.add(moving_cam)
            hyphens = (output_char_num_per_line+len(str(line_number))+4)*'─'
            print(f"\033[32mTotal:\033[0m\n"
                  f" - line: \033[33m{line_number}\033[0m\n"
                  f" - character: \033[33m{len(code_str)}\033[0m\n"
                  f"\033[32mSettings:\033[0m\n"
                  f" - language: \033[33m{language}\033[0m\n"
                  f" - font: \033[33m{font}\033[0m\n"
                  f"╭{hyphens}╮")

            # traverse code lines
            for line in range(line_number):
                # set line number color
                line_numbers.set_color(GREY)
                line_numbers[line].set_color(WHITE)

                # code line character number
                char_num = len(code_mobject[line])
                
                # progress bar
                line_number_spaces = (len(str(line_number))-len(str(line+1)))*' '
                this_line_number = f"\033[30m{line_number_spaces}{line+1}\033[0m"
                spaces = output_char_num_per_line*' '
                print(f"│ {this_line_number}  {spaces} │ Rendering...  \033[33m0%\033[0m", end='')

                # if the line is empty, move the cursor to the left of the occupy block and wait
                if code_str_per_line[line] == '':
                    cursor.next_to(occupy[line], LEFT, buff=-cursor_width) # cursor move to the left of occupy block
                    self.wait(random.uniform(*interval_range))
                
                code_line_rectangle.set_y(occupy[line].get_y())
                
                self.add(line_numbers[line]) # add line number
                line_y = line_numbers[line].get_y() # line number y coordinate
                
                # traverse code line characters
                is_leading_space = True
                output_highlighted_code = []
                for column in range(char_num):

                    char_mobject = code_mobject[line][column] # code line character
                    charR, charG, charB = [int(rgb*255) for rgb in char_mobject.get_color().to_rgb()]
                    # use RGB to set output text color
                    output_highlighted_code.append(f"\033[38;2;{charR};{charG};{charB}m{code_str_per_line[line][column]}\033[0m")

                    # if it is a leading space, skip
                    if code_str_per_line[line][column] == ' ' and is_leading_space:
                        pass
                    else:
                        is_leading_space = False
                        occupy_char = occupy[line][column] # occupy block character
                        self.add(char_mobject) # add code line character
                        cursor.next_to(occupy_char, RIGHT, buff=0.05) # cursor move to the right of occupy block
                        cursor.set_y(line_y-0.05) # cursor y coordinate in the same line
                        self.wait(random.uniform(*interval_range))

                    # output progress
                    code_spaces = (output_char_num_per_line - column - 1)*' '
                    percent = int((column+1)/char_num*100)
                    percent_spaces = (3-len(str(percent)))*' '
                    print(f"\r│ {this_line_number}  {''.join(output_highlighted_code)}{code_spaces} │ "
                          f"Rendering...\033[33m{percent_spaces}{percent}%\033[0m", end='')
                
                # overwrite the previous progress bar
                code_spaces = (output_char_num_per_line-len(code_str_per_line[line]))*' '
                print(f"\r│ {this_line_number}  {''.join(output_highlighted_code)}{code_spaces} │ \033[32m√\033[0m               ")

            print(f"╰{hyphens}╯\n"
                  "Combining to Movie file.")
            self.wait()

        def render(self, **kwargs):
            with self._no_manim_output():
                super().render(**kwargs)
            end_time = time.time()
            total_render_time = end_time - start_time
            print(f"File ready at \033[32m'{self.renderer.file_writer.movie_file_path}'\033[0m\n"
                  f"Rendered {video_name}.mp4\n"
                  f"\033[30m[Finished in {total_render_time:.2f}s]\033[0m")

    return code_video()
