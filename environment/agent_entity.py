class Agent:
    def __init__(self, name, position, goal):
        self.name = name
        self.position = position
        self.goal = goal

    def move_with_action(self, direction, world):
        dx, dy = 0, 0
        if direction == "up":
            dx = -1
        elif direction == "down":
            dx = 1
        elif direction == "left":
            dy = -1
        elif direction == "right":
            dy = 1

        new_x = self.position[0] + dx
        new_y = self.position[1] + dy
        if 0 <= new_x < world.height and 0 <= new_y < world.width:
            self.position = [new_x, new_y]
        world.update_positions()
