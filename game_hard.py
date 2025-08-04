import pygame
import random
import sys
import math

pygame.init()

WIDTH, HEIGHT = 480, 640
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("도트 피하기")

WHITE = (255, 255, 255)
BLUE = (50, 100, 255)
RED = (255, 50, 50)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

player_radius = 15
player_x = WIDTH // 2
player_y = HEIGHT - 50
player_speed = 5

enemy_radius = 10
enemy_speed = 3

score = 0
font = pygame.font.SysFont(None, 36)
clock = pygame.time.Clock()

CHASER_LIFETIME = 10000  # chase 패턴이 터지기 전 생존 시간 (ms)
FRAGMENT_LIFETIME = 1500  # 파편 수명 (ms)

def create_enemy(sc):
    available_patterns = ['straight']

    if sc > 5:
        available_patterns.append('zigzag')
    if sc > 10:
        available_patterns.append('chase')
    if sc > 15:
        available_patterns.append('circle')
    if sc > 20:
        available_patterns.append('splitter')
    if sc > 30:
        available_patterns.append('bomb')

    pattern = random.choice(available_patterns)
    x = random.randint(enemy_radius, WIDTH - enemy_radius)
    y = -enemy_radius

    e = {
        'x': x,
        'y': y,
        'pattern': pattern,
        'born_time': pygame.time.get_ticks(),
        'fragments': [],
        'exploded': False,
    }

    if pattern == 'chase':
        e['phase'] = 1
    if pattern == 'zigzag':
        e['x_dir'] = random.choice([-1, 1])
        e['y_dir'] = 1
        e['x_speed'] = random.uniform(2.0, 3.5)
        e['y_speed'] = random.uniform(2.0, 3.5)
        e['cool']=600
    if pattern == 'bomb':
        e['phase']=1
        e['cool']=0
    

    return e


def create_fragments(x, y, count=8):
    fragments = []
    angle_gap = 2 * math.pi / count
    speed = 4
    for i in range(count):
        angle = i * angle_gap
        fx = x
        fy = y
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        fragments.append({'x': fx, 'y': fy, 'vx': vx, 'vy': vy, 'born_time': pygame.time.get_ticks()})
    return fragments

enemies = []

spawn_timer = 0
spawn_interval = 1500

running = True
game_started=False
game_over = False

while not game_started and running:
    dt = clock.tick(60)
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if not game_started and event.key == pygame.K_SPACE:
                game_started = True

    if not game_started:
        screen.fill(WHITE)
        title = font.render("Press SPACE to Start", True, (0, 0, 0))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 20))
        pygame.display.flip()
        continue

while running:
    dt = clock.tick(70)
    spawn_timer += dt

    while game_over and running:
        clock.tick(60)
        screen.fill(WHITE)
        if game_over:
            text = font.render("Game Over! Press SPACE to Restart", True, (255, 0, 0))
        else:
            text = font.render("Press SPACE to Start", True, (0, 0, 0))
        score_text = font.render(f"Score: {int(score)}", True, (0, 0, 0))
        screen.blit(score_text, (10, 10))
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 20))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game_over=False
                    enemies = []
                    score = 0
                    spawn_interval=1500
                    enemy_speed = 3
                    player_x = WIDTH // 2
                    player_y = HEIGHT - 50



    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_x - player_speed - player_radius > 0:
        player_x -= player_speed
    if keys[pygame.K_RIGHT] and player_x + player_speed + player_radius < WIDTH:
        player_x += player_speed
    if keys[pygame.K_UP] and player_y - player_speed - player_radius > 0:
        player_y -= player_speed
    if keys[pygame.K_DOWN] and player_y + player_speed + player_radius < HEIGHT:
        player_y += player_speed

    if spawn_timer > spawn_interval:
        enemies.append(create_enemy(score))
        enemies.append(create_enemy(score))
        spawn_timer = 0
        enemy_speed = min(10, enemy_speed+0.03)
        if spawn_interval > 500:
            spawn_interval -= 10 if score < 30 else 20

    current_time = pygame.time.get_ticks()

    for enemy in enemies:
        if enemy['pattern'] == 'straight':
            enemy['y'] += enemy_speed * 2.5


        elif enemy['pattern'] == 'zigzag':
            enemy['y'] += enemy['y_dir'] * enemy['y_speed'] * enemy_speed * 2 / 5
            enemy['x'] += enemy['x_dir'] * enemy['x_speed'] * enemy_speed * 2 / 5
            # 벽에 닿으면 방향 반전
            if (enemy['x'] <= enemy_radius and enemy['x_dir'] == -1) or (enemy['x'] >= WIDTH - enemy_radius and enemy['x_dir'] == 1):
                enemy['x_dir'] *= -1
            if (enemy['y'] <= enemy_radius and enemy['y_dir'] == -1) or (enemy['y'] >= HEIGHT - enemy_radius and enemy['y_dir'] == 1):
                enemy['y_dir'] *= -1
            enemy['cool']-=1



        elif enemy['pattern'] == 'chase':
            if not enemy['exploded']:
                if enemy['phase'] == 1:
                    dx = player_x - enemy['x']
                    dy = player_y - enemy['y']
                    dist = math.hypot(dx, dy)
                    if dist != 0:
                        enemy['x'] += (dx / dist) * (enemy_speed * 0.7)
                        enemy['y'] += (dy / dist) * (enemy_speed * 0.7)
                else:
                    enemy['x'] += enemy['x_dir'] * enemy_speed * 0.5
                    enemy['y'] += enemy['y_speed']
                    enemy['y_speed'] += 0.6

                # 터질 시간 도달하면 explode
                if enemy['phase']==2 and enemy['y'] > HEIGHT * 2 // 5:
                    enemy['exploded'] = True
                    enemy['fragments'] = create_fragments(enemy['x'], enemy['y'], 6)
                elif enemy['phase']==1 and current_time - enemy['born_time'] > CHASER_LIFETIME or enemy['y'] > HEIGHT * 2 // 5:
                    enemies.append({
                        'x': enemy['x'],
                        'y': HEIGHT * 2 // 5,
                        'pattern': 'chase',
                        'born_time': pygame.time.get_ticks(),
                        'fragments': [],
                        'exploded': False,
                        'phase' : 2,
                        'x_dir' : 1,
                        'y_speed' : -10
                    })
                    enemies.append({
                        'x': enemy['x'],
                        'y': HEIGHT * 2 // 5,
                        'pattern': 'chase',
                        'born_time': pygame.time.get_ticks(),
                        'fragments': [],
                        'exploded': False,
                        'phase' : 2,
                        'x_dir' : -1,
                        'y_speed' : -10
                    })
                    enemy['phase'] = 0
            else:
                # 파편 이동
                new_fragments = []
                for frag in enemy['fragments']:
                    frag['x'] += frag['vx'] * enemy_speed / 3
                    frag['y'] += frag['vy'] * enemy_speed / 3
                    # 중력 효과 (옵션)
                    frag['vy'] += 0.15
                    # 수명 체크
                    if current_time - frag['born_time'] < FRAGMENT_LIFETIME:
                        new_fragments.append(frag)
                enemy['fragments'] = new_fragments

        elif enemy['pattern'] == 'circle':
            if 'angle' not in enemy:
                enemy['center_x'] = enemy['x']
                enemy['angle'] = 0
                enemy['radius'] = 160
            enemy['angle'] += 0.05
            enemy['x'] = enemy['center_x'] + math.cos(enemy['angle']) * enemy['radius']
            enemy['y'] += enemy_speed * 0.2

        elif enemy['pattern'] == 'splitter':
            # 터지지 않았으면 아래로 이동
            if not enemy.get('exploded', False):
                enemy['y'] += enemy_speed
                if enemy['y'] > HEIGHT - 15:
                    enemy['exploded'] = True
                    enemy['fragments'] = create_fragments(enemy['x'],enemy['y'],14)
            else:
                # 파편 이동
                new_fragments = []
                for frag in enemy['fragments']:
                    frag['x'] += frag['vx'] * enemy_speed / 7
                    frag['y'] += frag['vy'] * enemy_speed / 7
                    if current_time - frag['born_time'] < FRAGMENT_LIFETIME:
                        new_fragments.append(frag)
                enemy['fragments'] = new_fragments

        elif enemy['pattern'] == 'bomb':
            if not enemy['exploded']:
                if enemy['phase']==1:
                    enemy['y'] += enemy_speed
                    if (HEIGHT//2 < enemy['y'] and random.random()<0.05) or  enemy['y'] >= HEIGHT + 40:
                        enemy['phase'] = 2
                        enemy['cool'] = 400
                elif enemy['phase'] == 2:
                    enemy['cool']-=1
                    if enemy['cool'] <= 0:
                        enemy['exploded'] = True
                        enemy['fragments'] = create_fragments(enemy['x'], enemy['y'],10)
            else:
                # 파편 이동
                new_fragments = []
                for frag in enemy['fragments']:
                    frag['x'] += frag['vx'] * enemy_speed / 3
                    frag['y'] += frag['vy'] * enemy_speed / 3
                    # 수명 체크
                    if current_time - frag['born_time'] < FRAGMENT_LIFETIME:
                        new_fragments.append(frag)
                enemy['fragments'] = new_fragments
                    



    # 적 제거 (터진 chase는 fragments가 없으면 제거)
    enemies = [e for e in enemies if (e['pattern'] not in  ['chase','splitter','bomb'] or not e['exploded']) or len(e['fragments']) > 0]
    # 화면 밖에 있으면 제거 (터지기 전 적들)
    enemies = [e for e in enemies if -enemy_radius < e['y'] < HEIGHT + enemy_radius or (e['pattern'] in ['chase','splitter','bomb'] and e['exploded'])]

    enemies = [e for e in enemies if e['pattern'] != 'zigzag' or e['cool'] > 0]

    enemies = [e for e in enemies if e['pattern'] != 'chase' or e['phase'] > 0]

    score += dt / 1000

    # 기존 충돌 검사
    for enemy in enemies:
        if enemy['pattern'] not in ['chase','splitter','bomb'] or not enemy['exploded']:
            dist = math.hypot(player_x - enemy['x'], player_y - enemy['y'])
            if dist < player_radius + enemy_radius:
                game_over = True
                break

    # 파편 충돌 검사
    for enemy in enemies:
        if enemy['pattern'] in ['chase','splitter','bomb'] and enemy['exploded']:
            for frag in enemy['fragments']:
                dist = math.hypot(player_x - frag['x'], player_y - frag['y'])
                if dist < player_radius + 4:
                    game_over = True
                    break

    screen.fill(WHITE)
    pygame.draw.circle(screen, BLUE, (player_x, player_y), player_radius)

    for enemy in enemies:
        # if enemy['pattern'] == 'straight':
        #     color = RED
        #     pygame.draw.circle(screen, color, (int(enemy['x']), int(enemy['y'])), enemy_radius)
        #
        # elif enemy['pattern'] == 'zigzag':
        #     color = ORANGE
        #     pygame.draw.circle(screen, color, (int(enemy['x']), int(enemy['y'])), enemy_radius)
        #
        # elif enemy['pattern'] == 'chase':
        #     color = PURPLE

        color=RED

        if enemy['pattern'] == 'straight':
            color = RED
        elif enemy['pattern'] == 'zigzag':
            color = ORANGE
        elif enemy['pattern'] == 'chase':
            color = (220, 220, 0)
        elif enemy['pattern'] == 'circle':
            color = (0, 200, 100)  # 연녹색
        elif enemy['pattern'] == 'splitter':
            color = (0, 150, 255)  # 하늘색
        elif enemy['pattern'] == 'bomb':
            color = PURPLE

        if not enemy['exploded']:
            pygame.draw.circle(screen, color, (int(enemy['x']), int(enemy['y'])), enemy_radius)
        else:
            # 파편 그리기 (작은 원)
            for frag in enemy['fragments']:
                pygame.draw.circle(screen, color, (int(frag['x']), int(frag['y'])), 4)

    score_text = font.render(f"Score: {int(score)}", True, (0, 0, 0))
    screen.blit(score_text, (10, 10))

    pygame.display.flip()


pygame.quit()
sys.exit()
