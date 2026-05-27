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
CELL_SIZE = 20
BEST_SCORE_FILE = "best_score.txt"

# Mobile responsive offsets
GAME_Y_OFFSET = 180


# ================= GAME =================
class SnakeGame(Widget):

    def __init__(self, speed=0.15, hard_mode=False,
                 menu_callback=None, **kwargs):

        super().__init__(**kwargs)

        self.menu_callback = menu_callback
        self.hard_mode = hard_mode

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

        # Responsive grid
        self.cols = 20
        self.rows = 25

        # ================= SCORE LABELS =================
        self.score_label = Label(
            text="Score: 0",
            font_size='20sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(None, None),
            size=(150, 50),
            pos=(20, Window.height - 80)
        )

        self.best_label = Label(
            text=f"Best: {self.best_score}",
            font_size='20sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(None, None),
            size=(150, 50),
            pos=(Window.width - 170, Window.height - 80)
        )

        self.add_widget(self.score_label)
        self.add_widget(self.best_label)

        # Start game
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
                pos=(0, 0),
                size=(Window.width, Window.height)
            )

            # ================= SNAKE =================
            for i, (x, y) in enumerate(self.snake):

                draw_x = x * CELL_SIZE
                draw_y = y * CELL_SIZE + GAME_Y_OFFSET

                # ===== HEAD =====
                if i == 0:

                    Color(0, 0.8, 0)

                    Rectangle(
                        pos=(draw_x, draw_y),
                        size=(CELL_SIZE, CELL_SIZE)
                    )

                    # Eyes
                    Color(1, 1, 1)

                    Rectangle(
                        pos=(draw_x + 4, draw_y + 12),
                        size=(3, 3)
                    )

                    Rectangle(
                        pos=(draw_x + 13, draw_y + 12),
                        size=(3, 3)
                    )

                # ===== BODY =====
                else:

                    if i % 2 == 0:
                        Color(0, 0.7, 0)
                    else:
                        Color(0, 0.5, 0)

                    Rectangle(
                        pos=(draw_x + 1, draw_y + 1),
                        size=(CELL_SIZE - 2, CELL_SIZE - 2)
                    )

            # ================= FOOD =================
            Color(1, 0, 0)

            Rectangle(
                pos=(
                    self.food[0] * CELL_SIZE,
                    self.food[1] * CELL_SIZE + GAME_Y_OFFSET
                ),
                size=(CELL_SIZE, CELL_SIZE)
            )

            # ================= BONUS FOOD =================
            if self.bonus_visible:

                Color(1, 1, 0)

                Rectangle(
                    pos=(
                        self.bonus_food[0] * CELL_SIZE,
                        self.bonus_food[1] * CELL_SIZE + GAME_Y_OFFSET
                    ),
                    size=(CELL_SIZE, CELL_SIZE)
                )

    # ================= GAME LOOP =================
    def update(self, dt):

        head_x, head_y = self.snake[0]
        dx, dy = self.direction

        new_head = (head_x + dx, head_y + dy)

        # ================= HARD MODE =================
        if self.hard_mode:

            if (
                new_head[0] < 0 or
                new_head[0] > self.cols - 1 or
                new_head[1] < 0 or
                new_head[1] > self.rows - 1
            ):
                self.game_over()
                return

        # ================= EASY/MEDIUM =================
        else:

            if new_head[0] < 0:
                new_head = (self.cols - 1, new_head[1])

            elif new_head[0] > self.cols - 1:
                new_head = (0, new_head[1])

            if new_head[1] < 0:
                new_head = (new_head[0], self.rows - 1)

            elif new_head[1] > self.rows - 1:
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
                randint(0, self.cols - 1),
                randint(0, self.rows - 1)
            )

            # ================= BONUS EVERY 5 =================
            if (
                self.score % 5 == 0 and
                self.score != 0 and
                not self.bonus_visible
            ):

                self.bonus_food = (
                    randint(0, self.cols - 1),
                    randint(0, self.rows - 1)
                )

                self.bonus_visible = True

                # 5-10 sec
                self.bonus_timer = randint(5, 10)

        # ================= BONUS EATEN =================
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
            font_size='30sp',
            center=(Window.width / 2, Window.height / 2)
        ))

        btn = Button(
            text="Back To Menu",
            size_hint=(None, None),
            size=(220, 60),
            pos=(Window.width / 2 - 110, Window.height / 2 - 80)
        )

        btn.bind(on_press=lambda x: self.menu_callback())

        self.add_widget(btn)


# ================= MENU =================
class MenuScreen(BoxLayout):

    def __init__(self, start_game_callback, **kwargs):

        super().__init__(**kwargs)

        self.orientation = "vertical"
        self.spacing = 25
        self.padding = [40, 150, 40, 150]

        self.add_widget(Label(
            text="SNAKE GAME",
            font_size='32sp',
            bold=True,
            size_hint=(1, 0.3)
        ))

        easy = Button(
            text="Easy",
            font_size='24sp'
        )

        medium = Button(
            text="Medium",
            font_size='24sp'
        )

        hard = Button(
            text="Hard",
            font_size='24sp'
        )

        easy.bind(on_press=lambda x: start_game_callback(0.20, False))
        medium.bind(on_press=lambda x: start_game_callback(0.12, False))
        hard.bind(on_press=lambda x: start_game_callback(0.07, True))

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

        game = SnakeGame(
            speed=speed,
            hard_mode=hard_mode,
            menu_callback=self.show_menu
        )

        # ================= CONTROL PAD =================
        controls = BoxLayout(
            size_hint=(1, None),
            height=220,
            orientation="vertical",
            padding=15,
            spacing=10
        )

        row1 = BoxLayout(spacing=10)
        row2 = BoxLayout(spacing=10)
        row3 = BoxLayout(spacing=10)

        up = Button(
            text="⬆",
            font_size='28sp',
            size_hint=(0.3, 1)
        )

        down = Button(
            text="⬇",
            font_size='28sp',
            size_hint=(0.3, 1)
        )

        left = Button(
            text="⬅",
            font_size='28sp',
            size_hint=(0.3, 1)
        )

        right = Button(
            text="➡",
            font_size='28sp',
            size_hint=(0.3, 1)
        )

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

        # ================= MAIN CONTAINER =================
        container = BoxLayout(
            orientation="vertical"
        )

        container.add_widget(game)
        container.add_widget(controls)

        self.root_layout.add_widget(container)


# ================= RUN =================
SnakeApp().run()
