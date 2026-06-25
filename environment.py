import pygame
import math
import random
from pathfinder import AStarPathfinder

pygame.init()

WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Interactive A* Path Planning Simulator")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GRAY = (100, 100, 100)
BLACK = (0, 0, 0)
GREEN = (0, 205, 0)
DARK_BG = (30, 30, 30)

agent_radius = 15
target_radius = 15
speed = 5

font = pygame.font.Font(None, 28)
large_font = pygame.font.Font(None, 45)

GRID_SIZE = 20
pathfinder_engine = AStarPathfinder(WIDTH, HEIGHT, GRID_SIZE, agent_radius)


def generate_agent(existing_obstacles, existing_target_x, existing_target_y):
    """Spawns the agent in a valid spot away from obstacles and target."""
    while True:
        x = random.randint(agent_radius * 2, WIDTH - agent_radius * 2)
        y = random.randint(agent_radius * 2, HEIGHT - agent_radius * 2)
        agent_rect = pygame.Rect(x - agent_radius, y - agent_radius, agent_radius*2, agent_radius*2)
        
        valid = True
        for obs in existing_obstacles:
            if agent_rect.colliderect(obs):
                valid = False
                break
        
        if existing_target_x and existing_target_y:
            dist = math.sqrt((x - existing_target_x)**2 + (y - existing_target_y)**2)
            if dist < 100: valid = False
            
        if valid: return x, y

def generate_target(existing_obstacles, existing_agent_x, existing_agent_y):
    """Spawns the target in a valid spot away from obstacles and agent."""
    while True:
        x = random.randint(target_radius * 2, WIDTH - target_radius * 2)
        y = random.randint(target_radius * 2, HEIGHT - target_radius * 2)
        target_rect = pygame.Rect(x - target_radius, y - target_radius, target_radius*2, target_radius*2)
        
        valid = True
        for obs in existing_obstacles:
            if target_rect.colliderect(obs):
                valid = False
                break
                
        if existing_agent_x and existing_agent_y:
            dist = math.sqrt((x - existing_agent_x)**2 + (y - existing_agent_y)**2)
            if dist < 100: valid = False
            
        if valid: return x, y

def generate_obstacles(existing_agent_x, existing_agent_y, existing_target_x, existing_target_y):
    """Spawns 5 random obstacles, ensuring they never sit on the agent or target."""
    new_obstacles = []
    NUM_OBSTACLES = 5
    GAP = 40

    while len(new_obstacles) < NUM_OBSTACLES:
        width = random.randint(60, 140)
        height = random.randint(60, 140)
        x = random.randint(40, WIDTH - width - 40)
        y = random.randint(60, HEIGHT - height - 40) # Keep top clear for UI
        
        new_rect = pygame.Rect(x, y, width, height)
        valid = True

        # Ensure it doesn't drop on the Agent
        if existing_agent_x and existing_agent_y:
            safe_agent = pygame.Rect(existing_agent_x - 40, existing_agent_y - 40, 80, 80)
            if new_rect.colliderect(safe_agent): valid = False

        # Ensure it doesn't drop on the Target
        if existing_target_x and existing_target_y:
            safe_target = pygame.Rect(existing_target_x - 40, existing_target_y - 40, 80, 80)
            if new_rect.colliderect(safe_target): valid = False

        # Keep obstacles from overlapping each other too much
        if valid:
            expanded_rect = pygame.Rect(new_rect.x - GAP, new_rect.y - GAP, new_rect.width + GAP*2, new_rect.height + GAP*2)
            for obs in new_obstacles:
                if expanded_rect.colliderect(obs):
                    valid = False
                    break

        if valid: new_obstacles.append(new_rect)
        
    #rebuild its internal grid Every time obstacles change
    pathfinder_engine.build_occupancy_grid(new_obstacles)
    return new_obstacles


obstacles = []
agent_x, agent_y = 100, 100
target_x, target_y = 700, 500

# Generate initial board ensuring everything is valid
obstacles = generate_obstacles(agent_x, agent_y, target_x, target_y)
agent_x, agent_y = generate_agent(obstacles, target_x, target_y)
target_x, target_y = generate_target(obstacles, agent_x, agent_y)

# State Variables
state = 'SETUP'
planned_path = []
waypoint_index = 0

def draw_ui_panel(text, color):
    """Helper to draw instructions cleanly at the top of the screen."""
    pygame.draw.rect(screen, DARK_BG, (0, 0, WIDTH, 40))
    ui_text = font.render(text, True, color)
    screen.blit(ui_text, (20, 10))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN:
            if state in ['SETUP', 'UNREACHABLE']:
                if event.key == pygame.K_o: # Randomize Obstacles
                    obstacles = generate_obstacles(agent_x, agent_y, target_x, target_y)
                    state = 'SETUP'
                    planned_path = []
                elif event.key == pygame.K_a: # Randomize Agent
                    agent_x, agent_y = generate_agent(obstacles, target_x, target_y)
                    state = 'SETUP'
                    planned_path = []
                elif event.key == pygame.K_t: # Randomize Target
                    target_x, target_y = generate_target(obstacles, agent_x, agent_y)
                    state = 'SETUP'
                    planned_path = []
                elif event.key == pygame.K_SPACE: # Attempt to Generate Path
                    planned_path = pathfinder_engine.compute_path((agent_x, agent_y), (target_x, target_y))
                    if planned_path:
                        state = 'READY_TO_RUN'
                    else:
                        state = 'UNREACHABLE'
            
            elif state == 'READY_TO_RUN':
                if event.key == pygame.K_RETURN: 
                    waypoint_index = 0
                    state = 'MOVING'
                elif event.key == pygame.K_SPACE:
                    planned_path = []
                    state = 'SETUP'

            elif state == 'REACHED':
                if event.key == pygame.K_SPACE:
                    obstacles = generate_obstacles(None, None, None, None)
                    agent_x, agent_y = generate_agent(obstacles, None, None)
                    target_x, target_y = generate_target(obstacles, agent_x, agent_y)
                    planned_path = []
                    state = 'SETUP'


    # MOVEMENT LOGIC
    if state == 'MOVING':
        if waypoint_index < len(planned_path):
            wp_x, wp_y = planned_path[waypoint_index]
            
            if agent_x < wp_x: agent_x += min(speed, wp_x - agent_x)
            elif agent_x > wp_x: agent_x -= min(speed, agent_x - wp_x)
            elif agent_y < wp_y: agent_y += min(speed, wp_y - agent_y)
            elif agent_y > wp_y: agent_y -= min(speed, agent_y - wp_y)
            
            if agent_x == wp_x and agent_y == wp_y:
                waypoint_index += 1
        else:
            state = 'REACHED'


    screen.fill(WHITE)

    # Render Obstacles
    for obs in obstacles:
        pygame.draw.rect(screen, GRAY, obs)

    # Render Planned Path
    if state in ['READY_TO_RUN', 'MOVING'] and len(planned_path) > 1:
        if state == 'MOVING':
            points_to_draw = [(agent_x, agent_y)] + planned_path[waypoint_index:]
        else:
            points_to_draw = [(agent_x, agent_y)] + planned_path
            
        if len(points_to_draw) > 1:
            pygame.draw.lines(screen, GREEN, False, points_to_draw, 4)

    pygame.draw.circle(screen, RED, (target_x, target_y), target_radius)
    pygame.draw.circle(screen, BLUE, (agent_x, agent_y), agent_radius)

    if state == 'SETUP':
        draw_ui_panel("SETUP: [O] Rand Obs | [A] Rand Start | [T] Rand Target | [SPACE] Gen Path", WHITE)
    elif state == 'READY_TO_RUN':
        draw_ui_panel("PATH FOUND - Press [ENTER] to Run or [SPACE] to Cancel", GREEN)
    elif state == 'MOVING':
        draw_ui_panel("NAVIGATING... Please Wait.", WHITE)
    elif state == 'UNREACHABLE':
        draw_ui_panel("NO PATH FOUND - Target blocked. Press [O], [A], or [T] to shuffle board.", RED)
        error_text = large_font.render("NO VALID PATH", True, RED)
        screen.blit(error_text, (WIDTH//2 - error_text.get_width()//2, HEIGHT//2))
    elif state == 'REACHED':
        draw_ui_panel("TARGET REACHED! Press [SPACE] for next round.", BLUE)
        success_text = large_font.render("SUCCESS!", True, BLUE)
        screen.blit(success_text, (WIDTH//2 - success_text.get_width()//2, HEIGHT//2))

    pygame.display.update()
    clock.tick(60)

pygame.quit()