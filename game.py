import pygame
import random
import os
import sys

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Plane Destroyer Pro")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)


def load_image(name, scale=1):
    try:
        image = pygame.image.load(f"assets/{name}.png").convert_alpha()
        width = int(image.get_width() * scale)
        height = int(image.get_height() * scale)
        return pygame.transform.scale(image, (width, height))
    except:
        if name == "player":
            surf = pygame.Surface((50, 30), pygame.SRCALPHA)
            pygame.draw.polygon(surf, GREEN, [(0, 15), (45, 0), (45, 30)])
            pygame.draw.circle(surf, GREEN, (10, 15), 5)
            return surf
        elif name == "enemy":
            surf = pygame.Surface((50, 30), pygame.SRCALPHA)
            pygame.draw.polygon(surf, RED, [(50, 15), (5, 0), (5, 30)])
            pygame.draw.circle(surf, RED, (40, 15), 5)
            return surf
        elif name == "bullet":
            surf = pygame.Surface((15, 5), pygame.SRCALPHA)
            pygame.draw.rect(surf, YELLOW, (0, 0, 15, 5))
            return surf
        elif name == "background":
            surf = pygame.Surface((WIDTH, HEIGHT))
            surf.fill(BLACK)
            for _ in range(100):
                x, y = random.randint(0, WIDTH), random.randint(0, HEIGHT)
                pygame.draw.circle(surf, WHITE, (x, y), 1)
            return surf


def load_sound(name):
    try:
        return pygame.mixer.Sound(f"assets/{name}.wav")
    except:
        return None


if not os.path.exists("assets"):
    os.makedirs("assets")


pi = load_image("player", 0.8)
ei = load_image("enemy", 0.8)
bi = load_image("bullet")
bgi = load_image("background")
ss = load_sound("shoot")
es = load_sound("explosion")

pr = pi.get_rect(center=(100, HEIGHT // 2))
ps = 5
ph = 100
mxh = 100
invincible = False
invincible_timer = 0

b = []
bs = 10
bc = 0
bcm = 15

enemies = []
enemy_spawn_timer = 0
enemy_spawn_delay = 45
enemy_speed_min = 2
enemy_speed_max = 5

explosions = []
explosion_imgs = []
for i in range(1, 6):
    try:
        img = pygame.image.load(f"assets/explosion_{i}.png").convert_alpha()
        explosion_imgs.append(img)
    except:
        pass

if not explosion_imgs:
    for size in range(5, 30, 5):
        surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (255, 165, 0, 200), (size, size), size)
        explosion_imgs.append(surf)

powerups = []
powerup_types = ["health", "double", "speed"]
pst = 0
spd = 300

score = 0
high_score = 0
level = 1
game_over = False
fs = pygame.font.SysFont(None, 24)
fm = pygame.font.SysFont(None, 36)
fl = pygame.font.SysFont(None, 72)

clock = pygame.time.Clock()
running = True


def spawn_explosion(x, y, scale=1.0):
    explosions.append({
        'x': x,
        'y': y,
        'frame': 0,
        'scale': scale,
        'active': True
    })
    if es:
        es.play()


def spawn_powerup(x, y):
    pt = random.choice(powerup_types)
    powerups.append({
        'rect': pygame.Rect(x, y, 30, 30),
        'type': pt,
        'speed': 3
    })


def show_game_over():
    screen.blit(bgi, (0, 0))
    G_O_T = fl.render("GAME OVER", True, RED)
    st = fm.render(f"Final Score: {score}", True, WHITE)
    hst = fm.render(f"High Score: {high_score}", True, WHITE)
    rt = fs.render("Press R to restart or Q to quit", True, WHITE)

    screen.blit(G_O_T, (WIDTH // 2 - G_O_T.get_width() // 2, HEIGHT // 2 - 100))
    screen.blit(st, (WIDTH // 2 - st.get_width() // 2, HEIGHT // 2))
    screen.blit(hst, (WIDTH // 2 -hst.get_width() // 2, HEIGHT // 2 + 50))
    screen.blit(rt, (WIDTH // 2 - rt.get_width() // 2, HEIGHT // 2 + 120))
    pygame.display.flip()


def reset_game():
    global p_r, ph, b, e, ex, p
    global score, level, g_o, E_S_D, E_S_Mi, E_S_Mx

    p_r = pi.get_rect(center=(100, HEIGHT // 2))
    ph = mxh
    b = []
    e = []
    ex = []
    powerups = []
    score = 0
    level = 1
    g_o = False
    E_S_D = 45
    E_S_Mi = 2
    E_S_Mx = 5


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                if bc == 0:
                    b.append({
                        'rect': bi.get_rect(midleft=pr.midright),
                        'active': True
                    })
                    if ss:
                        ss.play()
                    bullet_cooldown = bcm
            if game_over and event.key == pygame.K_r:
                reset_game()
            if game_over and event.key == pygame.K_q:
                running = False

    if not game_over:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            pr.y -= ps
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            pr.y += ps
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            pr.x -= ps
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            pr.x += ps



        pr.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

        if invincible:
            invincible_timer -= 1
            if invincible_timer <= 0:
                invincible = False

        if bc > 0:
            bc -= 1

        enemy_spawn_timer += 1
        if enemy_spawn_timer >= enemy_spawn_delay:
            enemies.append({
                'rect': ei.get_rect(center=(WIDTH + 50, random.randint(50, HEIGHT - 50))),
                'speed': random.randint(enemy_speed_min, enemy_speed_max),
                'health': 30
            })

            enemy_spawn_timer = 0



        pst += 1
        if pst >= spd and random.random() < 0.3:
            spawn_powerup(random.randint(100, WIDTH - 100), random.randint(50, HEIGHT - 50))
            pst = 0

        for bullet in b[:]:
            bullet['rect'].x += bs
            if bullet['rect'].left > WIDTH:
                b.remove(bullet)
                continue


            for enemy in enemies[:]:
                if bullet['rect'].colliderect(enemy['rect']):
                    enemy['health'] -= 10
                    if bullet in b:
                        b.remove(bullet)
                    if enemy['health'] <= 0:
                        spawn_explosion(enemy['rect'].centerx, enemy['rect'].centery)
                        enemies.remove(enemy)
                        score += 10
                        if random.random() < 0.2:
                            spawn_powerup(enemy['rect'].centerx, enemy['rect'].centery)
                    break

        for enemy in enemies[:]:
            enemy['rect'].x -= enemy['speed']
            if enemy['rect'].right < 0:
                enemies.remove(enemy)


            if enemy['rect'].colliderect(pr) and not invincible:
                ph -= 10
                spawn_explosion(enemy['rect'].centerx, enemy['rect'].centery, 0.7)
                enemies.remove(enemy)
                invincible = True
                invincible_timer = 60
                if ph <= 0:
                    game_over = True
                    if score > high_score:
                        high_score = score

        for explosion in explosions[:]:
            explosion['frame'] += 0.5
            if explosion['frame'] >= len(explosion_imgs):
                explosions.remove(explosion)

        for powerup in powerups[:]:
            powerup['rect'].x -= powerup['speed']
            if powerup['rect'].right < 0:
                powerups.remove(powerup)
                continue

            if powerup['rect'].colliderect(pr):
                if powerup['type'] == "health":
                    player_health = min(mxh, ph + 20)
                elif powerup['type'] == "double":
                    bcm = max(5, bcm // 2)
                elif powerup['type'] == "speed":
                    ps += 1
                powerups.remove(powerup)



        if score >= level * 100:
            level += 1
            enemy_spawn_delay = max(15, enemy_spawn_delay - 5)
            enemy_speed_min += 0.5
            enemy_speed_max += 0.5

    screen.blit(bgi, (0, 0))

    if not game_over:
        if not invincible or pygame.time.get_ticks() % 200 < 100:
            screen.blit(pi, pr)

        for bullet in b:
            screen.blit(bi, bullet['rect'])

        for enemy in enemies:
            screen.blit(ei, enemy['rect'])

        for i in explosions:
            frame_idx = min(int(i['frame']), len(explosion_imgs) - 1)
            img = explosion_imgs[frame_idx]
            s_i = pygame.transform.scale(img,(int(img.get_width() * i['scale']),int(img.get_height() * i['scale'])))
            screen.blit(s_i,(i['x'] - s_i.get_width() // 2,i['y'] - s_i.get_height() // 2))

        for y in powerups:
            if y['type'] == "health":
                color = GREEN
            elif y['type'] == "double":
                color = YELLOW
            else:
                color = BLUE



            pygame.draw.rect(screen, color, y['rect'])
            pygame.draw.rect(screen, WHITE, y['rect'], 2)

        pygame.draw.rect(screen, RED, (10, 10, 200, 20))
        pygame.draw.rect(screen, GREEN, (10, 10, 200 * (ph / mxh), 20))
        pygame.draw.rect(screen, WHITE, (10, 10, 200, 20), 2)
        ht = fs.render(f"{ph}/{mxh}", True, WHITE)
        screen.blit(ht, (100 - ht.get_width() // 2, 12))


        st = fm.render(f"Score: {score}", True, WHITE)
        lt = fm.render(f"Level: {level}", True, WHITE)
        screen.blit(st, (WIDTH - st.get_width() - 10, 10))
        screen.blit(lt, (WIDTH - lt.get_width() - 10, 50))




        if bcm < 10:
            rt = (10 - bcm) * 2
            dt = fs.render(f"Double Fire: {rt}s", True, YELLOW)
            screen.blit(dt, (10, 40))

        if ps > 5:
            spt = fs.render(f"Speed Boost: {ps - 5}", True, BLUE)
            screen.blit(spt, (10, 70))
    else:
        show_game_over()

    pygame.display.flip()

    clock.tick(60)




pygame.quit()
sys.exit()