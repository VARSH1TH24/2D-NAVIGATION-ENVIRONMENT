import pygame
import math
import random

pygame.init()


WIDTH = 800
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Navigation Environment")

clock = pygame.time.Clock()


WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GRAY = (100, 100, 100)
BLACK = (0, 0, 0)


agent_radius = 15
agent_x = 100
agent_y = 100
speed = 7


font = pygame.font.Font(None, 36)
score = 0


def generate_obstacles():

    obstacles = []

    NUM_OBSTACLES = 5
    GAP = 50

    while len(obstacles) < NUM_OBSTACLES:

        width = random.randint(60, 120)
        height = random.randint(60, 120)

        x = random.randint(40, WIDTH - width - 40)
        y = random.randint(40, HEIGHT - height - 40)

        new_rect = pygame.Rect(x, y, width, height)

        valid = True

        # Don't spawn near the agent
        agent_safe_zone = pygame.Rect(
            agent_x - 80,
            agent_y - 80,
            160,
            160
        )

        if new_rect.colliderect(agent_safe_zone):
            valid = False

        # Keep a gap between obstacles
        if valid:
            expanded_rect = pygame.Rect(
                new_rect.x - GAP,
                new_rect.y - GAP,
                new_rect.width + GAP * 2,
                new_rect.height + GAP * 2
            )

            for obstacle in obstacles:
                if expanded_rect.colliderect(obstacle):
                    valid = False
                    break

        if valid:
            obstacles.append(new_rect)

    return obstacles


obstacles = generate_obstacles()


target_radius = 15


def generate_target():

    while True:

        x = random.randint(
            target_radius,
            WIDTH - target_radius
        )

        y = random.randint(
            target_radius,
            HEIGHT - target_radius
        )

        target_rect = pygame.Rect(
            x - target_radius,
            y - target_radius,
            target_radius * 2,
            target_radius * 2
        )

        valid = True

        # Not inside obstacle
        for obstacle in obstacles:
            if target_rect.colliderect(obstacle):
                valid = False
                break

        if not valid:
            continue

        # Not too close to agent
        distance_to_agent = math.sqrt(
            (x - agent_x) ** 2 +
            (y - agent_y) ** 2
        )

        if distance_to_agent < 150:
            continue

        return x, y


target_x, target_y = generate_target()


running = True

while running:

  
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

   
    old_x = agent_x
    old_y = agent_y

  
    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]:
        agent_y -= speed

    if keys[pygame.K_s]:
        agent_y += speed

    if keys[pygame.K_a]:
        agent_x -= speed

    if keys[pygame.K_d]:
        agent_x += speed


    agent_x = max(
        agent_radius,
        min(WIDTH - agent_radius, agent_x)
    )

    agent_y = max(
        agent_radius,
        min(HEIGHT - agent_radius, agent_y)
    )


    agent_rect = pygame.Rect(
        agent_x - agent_radius,
        agent_y - agent_radius,
        agent_radius * 2,
        agent_radius * 2
    )

 
    collision = False

    for obstacle in obstacles:

        if agent_rect.colliderect(obstacle):
            collision = True
            break

    if collision:
        agent_x = old_x
        agent_y = old_y

  
    distance = math.sqrt(
        (agent_x - target_x) ** 2 +
        (agent_y - target_y) ** 2
    )

    if distance <= agent_radius + target_radius:

        score += 1

        print(f"Target Reached! Score: {score}")

        target_x, target_y = generate_target()


    screen.fill(WHITE)

    # Obstacles
    for obstacle in obstacles:
        pygame.draw.rect(
            screen,
            GRAY,
            obstacle
        )

    # Target
    pygame.draw.circle(
        screen,
        RED,
        (target_x, target_y),
        target_radius
    )

    # Agent
    pygame.draw.circle(
        screen,
        BLUE,
        (agent_x, agent_y),
        agent_radius
    )

    # Score
    score_text = font.render(
        f"Score: {score}",
        True,
        BLACK
    )

    screen.blit(score_text, (10, 10))

    pygame.display.update()
    clock.tick(60)

pygame.quit()