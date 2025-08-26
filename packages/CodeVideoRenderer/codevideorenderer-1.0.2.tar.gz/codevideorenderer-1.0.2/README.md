This repository is used to render and generate videos of input code, with the video perspective following the cursor movement.

**Tip: Use `manim` for animation rendering. Please ensure that `manim` can run properly before use.**

This repository provides `CodeVideo`, which you can use to create a video object. The parameters are as follows:

```python
CodeVideo(
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
    )
```

This library uses `validate_call` from `pydantic`, which automatically checks the parameter types when you pass them in to ensure correctness.

**<u>Please feel free to use it!</u>**

--- 

You can use the `render` method on the `CodeVideo` object to generate the video, and you can check the save location of the video in the terminal.

Example:

```python
from CodeVideoRenderer import *
video = CodeVideo(code_string="print('Hello World!')", language='python')
video.render()
```

**Tip: Although `language` will be automatically recognized, it may sometimes be incorrect, so it is recommended to specify it.**
