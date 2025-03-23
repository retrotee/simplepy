from SimplePy import SimplePy
import math
import time

game = SimplePy(title="Test", width=500, height=500, fps=60)

enemy = game.create_sprite(x=400, y=300, width=50, height=50, color="red")
player = game.create_sprite(x=game.width / 2, y=game.height / 2, width=50, height=50, color="blue")
gun = game.create_sprite(x=100, y=100, width=50, height=10, color="green")

enemy.set_anchor("center")
player.set_anchor("center")
gun.set_anchor("left")

gun.set_layer(3)

score = 0
PLAYER_SAFE_DISTANCE = 150
MAX_BULLETS = 50

bullet_pool = []
bullets = []
def start():
    global bullet_pool
    for _ in range(MAX_BULLETS):
        bullet = game.create_sprite(x=-100, y=-100, width=2, height=2, color="red")
        bullet.set_anchor("center")
        bullet.active = False
        bullet_pool.append(bullet)


def create_bullet():
    global bullet_pool
    for bullet in bullet_pool:
        if not bullet.active:
            bullet.set_layer(2)
            bullet.x = gun.x
            bullet.y = gun.y
            bullet.direction = gun.direction
            bullet.speed = 10 / 2
            bullet.active = True
            bullets.append(bullet)
            return

def update():
    enemy.point_towards(gun.x, gun.y, True)
    enemy.move_forward(5 / 2)

    gun.move_to(player.x + 25, player.y + 20)
    enemy_center_x = enemy.x + enemy.width / 2
    enemy_center_y = enemy.y + enemy.height / 2
    gun.turn_towards(enemy_center_x, enemy_center_y, 100, True)
    player.turn_towards(enemy_center_x, enemy_center_y, 100, True)

    player.move_forward(10 / 2)

    if game.check_collision(player, enemy):
        if game.distance(player.x, player.y, enemy.x, enemy.y) < player.width * 0.8:
            game.draw_text("GAME OVER!", game.width / 2, game.height / 2, "red", 40, "Arial")
            game.freeze(math.inf)

    if len(bullets) < MAX_BULLETS:
        create_bullet()

    for bullet in list(bullets):
        bullet.move_forward(bullet.speed)

        if game.check_collision(bullet, enemy):
            global score
            score += 1
            bullet.active = False
            bullets.remove(bullet)
            while True:
                enemy.x = game.random_number(0, game.width)
                enemy.y = game.random_number(0, game.height)
                if game.distance(enemy.x, enemy.y, player.x, player.y) > PLAYER_SAFE_DISTANCE:
                    break

        if bullet.is_touching_edge():
            bullet.active = False
            if bullet in bullets:
                bullets.remove(bullet)



def draw():
    global score
    game.draw_text(score, 20, 20, "black", 20, anchor="left")
    game.draw_text(f"FPS: {game.current_fps}", 400, 20, anchor="topleft")


game.on_start = start
game.on_update = update
game.on_draw = draw

game.run()