import pygame
import constants as cnt


def draw_grid(screen, game, n):
    if not screen: return
    screen.fill(cnt.WHITE)
    font = pygame.font.SysFont(None, 30)
    text = font.render(game.current_step, True, cnt.BLACK)
    screen.blit(text, (20, 10))

    for i in range(n):
        for j in range(n):
            x = j * (cnt.CELL_SIZE + cnt.MARGIN)
            y = i * (cnt.CELL_SIZE + cnt.MARGIN) + cnt.HEADER_HEIGHT
            node = (i, j)

            # Start with white for open cells, black for closed
            if game.Ship.nodes[node]['weight'] == cnt.CELL_OPENED:
                color = cnt.WHITE
            else:
                color = cnt.BLACK

            if game.step < 4:
                if node in game.one_neighbour_set:
                    color = cnt.YELLOW
                if node in game.dead_ends:
                    color = cnt.RED
                if node in game.currently_open and (node not in game.dead_ends):
                    color = cnt.GREEN
            else:

                if game.currLocalizer and node in game.currLocalizer.possible_locations:
                    color = cnt.GREEN

            pygame.draw.rect(screen, color, (x, y, cnt.CELL_SIZE, cnt.CELL_SIZE))
            pygame.draw.rect(screen, cnt.GRAY, (x, y, cnt.CELL_SIZE, cnt.CELL_SIZE), 1)

    # Rest of your code remains the same...
    pygame.draw.rect(screen, cnt.BLUE, (cnt.SCREEN_SIZE[0] // 2 - 50, cnt.SCREEN_SIZE[1] - 40, 100, 30))
    message = "Proceed" if game.canProceed else "Loading ..."
    if game.game_over: message = "Restart"
    text = font.render(message, True, cnt.WHITE)
    screen.blit(text, (cnt.SCREEN_SIZE[0] // 2 - 30, cnt.SCREEN_SIZE[1] - 35))

    pygame.display.flip()


def draw_grid_internal(graph):
    draw_grid(graph.screen, graph, graph.n)


def getColor(prob):
    # Special case: exactly 0 probability
    if prob == 0.0:
        return cnt.GRAY  # Or (128, 128, 128) if cnt.GRAY isn't defined

    # Clamp probability between 0 and 1 (excluding 0 now)
    prob = max(0.0001, min(1.0, prob))  # Using 0.0001 to avoid log(0) if needed

    # Smooth gradient from green (low) to red (high)
    if prob < 0.5:
        # Green (0,255,0) to yellow (255,255,0)
        red = int(510 * prob)  # 510 = 255*2
        green = 255
    else:
        # Yellow (255,255,0) to red (255,0,0)
        red = 255
        green = int(510 * (1 - prob))  # 510 = 255*2

    # Clamp values (shouldn't be needed but safe)
    red = max(0, min(255, red))
    green = max(0, min(255, green))

    return red, green, 0
