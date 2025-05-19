import os

def clear_and_display(world):
    os.system("cls" if os.name == "nt" else "clear")
    world.display()
