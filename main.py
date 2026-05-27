from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from random import randint
import os

# ================= SETTINGS =================
BEST_SCORE_FILE = "best_score.txt"

GRID_WIDTH = 20
GRID_HEIGHT = 25

CONTROL_HEIGHT = 180


# ================= GAME =================
class SnakeGame(Widget):

    def __init__(self, speed=0.15, hard_mode=False,
                 menu_callback=None, **kwargs):

        super().__init__(**kwargs)

        self.menu_callback = menu_callback
        self.hard_mode = hard_mode

        # Dynamic sizes
        self.game_width = Window.width
        self.game_height = Window.height - CONTROL_HEIGHT

        self.cell_size = min(
            self.game_width / GRID_WIDTH,
            self.game_height / GRID_HEIGHT
        )

        # Snake
        self.snake = [(5, 5)]
        self.direction = (1, 0)

        # Food
        self.food = (10, 10)

        # Bonus food
        self.bonus_food = None
        self.bonus_visible = False
        self.bonus_timer = 0

        # Scores
        self.score = 0
        self.best_score = self.load_best_score()

        # ================= SCORE LABELS =================
        self.score_label = Label(
            text="Score: 0",
            font_size='20sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(None, None),
            size=(150, 50),
            pos=(20, Window.height - 50)
        )

        self.best_label = Label(
            text=f"Best: {self.best_score}",
            font_size='20sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(None, None),
            size=(150, 50),
            pos=(Window.width - 170, Window.height - 50)
        )

        self.add_widget(self.score_label)
        self.add_widget(self.best_label)

        # Game loop
        self.event = Clock.schedule_interval(self.update, speed)

        self.redraw()

    # ================= CONTROLS =================
    def move_up(self, instance):
        if self.direction != (0, -1):
            self.direction = (0, 1)

    def move_down(self, instance):
        if self.direction != (0, 1):
            self.direction = (0, -1)

    def move_left(self, instance):
        if self.direction != (1, 0):
            self.direction = (-1, 0)

    def move_right(self, instance):
        if self.direction != (-1, 0):
            self.direction = (1, 0)

    # ================= DRAW =================
    def redraw(self):

        self.canvas.before.clear()

        with self.canvas.before:

            # Background
            Color(0, 0, 0)

            Rectangle(
                pos=(0, CONTROL_HEIGHT),
                size=(Window.width, self.game_height)
            )

            # ================= SNAKE =================
            for i, (x, y) in enumerate(self.snake):

                draw_x = x * self.cell_size
                draw_y = y * self.cell_size + CONTROL_HEIGHT

                # HEAD
                if i == 0:

                    Color(0, 0.8, 0)

                    Rectangle(
                        pos=(draw_x, draw_y),
                        size=(self.cell_size, self.cell_size)
                    )

                    # Eyes
                    Color(1, 1, 1)

                    Rectangle(
                        pos=(draw_x + self.cell_size * 0.2,
                             draw_y + self.cell_size * 0.7),
                        size=(3, 3)
                    )

                    Rectangle(
                        pos=(draw_x + self.cell_size * 0.7,
                             draw_y + self.cell_size * 0.7),
                        size=(3, 3)
                    )

                # BODY
                else:

                    if i % 2 == 0:
                        Color(0, 0.7, 0)
                    else:
                        Color(0, 0.5, 0)

                    Rectangle(
                        pos=(draw_x + 1, draw_y + 1),
                        size=(self.cell_size - 2,
                              self.cell_size - 2)
                    )

            # ================= NORMAL FOOD =================
            Color(1, 0, 0)

            Rectangle(
                pos=(
                    self.food[0] * self.cell_size,
                    self.food[1] * self.cell_size + CONTROL_HEIGHT
                ),
                size=(self.cell_size, self.cell_size)
            )

            # ================= BONUS FOOD =================
            if self.bonus_visible:

                Color(1, 1, 0)

                Rectangle(
                    pos=(
                        self.bonus_food[0] * self.cell_size,
                        self.bonus_food[1] * self.cell_size + CONTROL_HEIGHT
                    ),
                    size=(self.cell_size, self.cell_size)
                )

    # ================= GAME LOOP =================
    def update(self, dt):

        head_x, head_y = self.snake[0]
        dx, dy = self.direction

        new_head = (head_x + dx, head_y + dy)

        # ================= HARD MODE =================
        if self.hard_mode:

            if (
                new_head[0] < 0
                or new_head[0] >= GRID_WIDTH
                or new_head[1] < 0
                or new_head[1] >= GRID_HEIGHT
            ):
                self.game_over()
                return

        # ================= EASY/MEDIUM WRAP =================
        else:

            if new_head[0] < 0:
                new_head = (GRID_WIDTH - 1, new_head[1])

            elif new_head[0] >= GRID_WIDTH:
                new_head = (0, new_head[1])

            if new_head[1] < 0:
                new_head = (new_head[0], GRID_HEIGHT - 1)

            elif new_head[1] >= GRID_HEIGHT:
                new_head = (new_head[0], 0)

        # ================= SELF COLLISION =================
        if new_head in self.snake:
            self.game_over()
            return

        self.snake.insert(0, new_head)

        # ================= NORMAL FOOD =================
        if new_head == self.food:

            self.score += 1
            self.score_label.text = f"Score: {self.score}"

            # Best score
            if self.score > self.best_score:

                self.best_score = self.score
                self.best_label.text = f"Best: {self.best_score}"

                self.save_best_score()

            # New food
            self.food = (
                randint(0, GRID_WIDTH - 1),
                randint(0, GRID_HEIGHT - 1)
            )

            # ================= BONUS EVERY 5 =================
            if (
                self.score % 5 == 0
                and self.score != 0
                and not self.bonus_visible
            ):

                self.bonus_food = (
                    randint(0, GRID_WIDTH - 1),
                    randint(0, GRID_HEIGHT - 1)
                )

                self.bonus_visible = True
                self.bonus_timer = randint(5, 10)

        # ================= BONUS FOOD =================
        elif self.bonus_visible and new_head == self.bonus_food:

            self.score += 5
            self.score_label.text = f"Score: {self.score}"

            if self.score > self.best_score:

                self.best_score = self.score
                self.best_label.text = f"Best: {self.best_score}"

                self.save_best_score()

            self.bonus_visible = False
            self.bonus_food = None

        else:
            self.snake.pop()

        # ================= BONUS TIMER =================
        if self.bonus_visible:

            self.bonus_timer -= dt

            if self.bonus_timer <= 0:

                self.bonus_visible = False
                self.bonus_food = None

        self.redraw()

    # ================= BEST SCORE =================
    def load_best_score(self):

        if os.path.exists(BEST_SCORE_FILE):

            with open(BEST_SCORE_FILE, "r") as f:
                return int(f.read())

        return 0

    def save_best_score(self):

        with open(BEST_SCORE_FILE, "w") as f:
            f.write(str(self.best_score))

    # ================= GAME OVER =================
    def game_over(self):

        self.event.cancel()

        self.add_widget(Label(
            text="GAME OVER",
            font_size='40sp',
            center=(Window.width / 2,
                    Window.height / 2)
        ))

        btn = Button(
            text="Back To Menu",
            size_hint=(None, None),
            size=(220, 60),
            pos=(Window.width / 2 - 110,
                 Window.height / 2 - 80)
        )

        btn.bind(on_press=lambda x: self.menu_callback())

        self.add_widget(btn)


# ================= MENU =================
class MenuScreen(BoxLayout):

    def __init__(self, start_game_callback, **kwargs):

        super().__init__(**kwargs)

        self.orientation = "vertical"
        self.spacing = 20
        self.padding = 40

        self.add_widget(Label(
            text="SNAKE GAME",
            font_size='40sp'
        ))

        easy = Button(text="Easy", font_size='28sp')
        medium = Button(text="Medium", font_size='28sp')
        hard = Button(text="Hard", font_size='28sp')

        easy.bind(on_press=lambda x:
                  start_game_callback(0.20, False))

        medium.bind(on_press=lambda x:
                    start_game_callback(0.12, False))

        hard.bind(on_press=lambda x:
                  start_game_callback(0.07, True))

        self.add_widget(easy)
        self.add_widget(medium)
        self.add_widget(hard)


# ================= APP =================
class SnakeApp(App):

    def build(self):

        self.root_layout = BoxLayout(
            orientation="vertical"
        )

        self.show_menu()

        return self.root_layout

    # ================= MENU =================
    def show_menu(self):

        self.root_layout.clear_widgets()

        self.root_layout.add_widget(
            MenuScreen(self.start_game)
        )

    # ================= START GAME =================
    def start_game(self, speed, hard_mode):

        self.root_layout.clear_widgets()

        container = BoxLayout(
            orientation="vertical"
        )

        game = SnakeGame(
            speed=speed,
            hard_mode=hard_mode,
            menu_callback=self.show_menu
        )

        # ================= CONTROL PAD =================
        controls = BoxLayout(
            size_hint=(1, None),
            height=CONTROL_HEIGHT,
            orientation="vertical",
            padding=10,
            spacing=5
        )

        row1 = BoxLayout()
        row2 = BoxLayout()
        row3 = BoxLayout()

        up = Button(text="⬆", font_size='30sp')
        down = Button(text="⬇", font_size='30sp')
        left = Button(text="⬅", font_size='30sp')
        right = Button(text="➡", font_size='30sp')

        up.bind(on_press=game.move_up)
        down.bind(on_press=game.move_down)
        left.bind(on_press=game.move_left)
        right.bind(on_press=game.move_right)

        row1.add_widget(Label())
        row1.add_widget(up)
        row1.add_widget(Label())

        row2.add_widget(left)
        row2.add_widget(Label())
        row2.add_widget(right)

        row3.add_widget(Label())
        row3.add_widget(down)
        row3.add_widget(Label())

        controls.add_widget(row1)
        controls.add_widget(row2)
        controls.add_widget(row3)

        container.add_widget(game)
        container.add_widget(controls)

        self.root_layout.add_widget(container)


# ================= RUN =================
SnakeApp().run()
