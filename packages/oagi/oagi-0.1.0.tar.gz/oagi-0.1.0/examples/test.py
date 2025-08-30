from examples.execute_task_manual import execute_task_manual
from oagi import PyautoguiActionHandler, ScreenshotMaker, ShortTask


def main():
    is_completed, screenshot = execute_task_manual(
        desc := "Search weather with Google", max_steps=5
    )
    with open("screenshot.png", "wb") as f:
        f.write(screenshot.read())


if __name__ == "__main__":
    short_task = ShortTask()
    is_completed = short_task.auto_mode(
        "Search weather with Google",
        max_steps=5,
        executor=PyautoguiActionHandler(),  # or executor = lambda actions: print(actions) for debugging
        image_provider=(sm := ScreenshotMaker()),
    )
