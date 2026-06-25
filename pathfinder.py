# pathfinder.py
import heapq

class AStarPathfinder:
    def __init__(self, width, height, grid_size, agent_radius):
        self.width = width
        self.height = height
        self.grid_size = grid_size
        self.agent_radius = agent_radius
        
        self.cols = width // grid_size
        self.rows = height // grid_size
        
        self.neighbors_mask = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        
        self.grid = []  # this is an occupancy grid which tracks teh obstacles in our environemtn

    def build_occupancy_grid(self, obstacles): # here we convert the grid to pixel coordinates and checking if the pixel is inside the obstacle or not. If it is inside the obstacle, then we mark that cell as blocked (1), otherwise we mark it as free (0).
        """
        0 = free, 1 = blocked.
        """
        self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        safety_padding = self.agent_radius - 2
        
        for row in range(self.rows):
            for col in range(self.cols):
                pixel_x = col * self.grid_size + self.grid_size // 2
                pixel_y = row * self.grid_size + self.grid_size // 2
                
                # obstacle hitting check
                for obs in obstacles:
                    if (pixel_x + safety_padding > obs.left and pixel_x - safety_padding < obs.right and
                        pixel_y + safety_padding > obs.top and pixel_y - safety_padding < obs.bottom):
                        self.grid[row][col] = 1 
                        break

    def _heuristic(self, a, b):
        """Manhattan distance heuristic for 4-directional grids."""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def _is_valid_node(self, col, row):
        """Validates node boundary and checks occupancy grid for obstacle collision."""
        if col < 0 or col >= self.cols or row < 0 or row >= self.rows:
            return False
        return self.grid[row][col] == 0

    def compute_path(self, start_pixel, target_pixel):
        """
        Computes the A* path. 
        Returns an empty list if no path exists.
        """
        # converting pixel coordinates to grid coordinates
        start_node = (int(start_pixel[0]) // self.grid_size, int(start_pixel[1]) // self.grid_size) 
        end_node = (int(target_pixel[0]) // self.grid_size, int(target_pixel[1]) // self.grid_size)
        

        if not self._is_valid_node(start_node[0], start_node[1]) or not self._is_valid_node(end_node[0], end_node[1]):
            return []

        open_set = []
        tie_breaker = 0
        heapq.heappush(open_set, (0, tie_breaker, start_node))
        
        came_from = {}
        g_score = {start_node: 0}
        f_score = {start_node: self._heuristic(start_node, end_node)}

        while open_set:
            current = heapq.heappop(open_set)[2]

            if current == end_node:
                path = []
                while current in came_from: # till we reach the start node we keep adding the nodes to the path list
                    # here path is getting reconstructed if goal is found
                    pixel_coord = (
                        current[0] * self.grid_size + self.grid_size // 2,
                        current[1] * self.grid_size + self.grid_size // 2
                    )
                    path.append(pixel_coord)
                    current = came_from[current]
                path.reverse()
                return path

            for dc, dr in self.neighbors_mask:
                neighbor = (current[0] + dc, current[1] + dr)
                
                if not self._is_valid_node(neighbor[0], neighbor[1]):
                    continue
                    
                tentative_g = g_score[current] + 1 

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self._heuristic(neighbor, end_node)
                    
                    tie_breaker += 1
                    heapq.heappush(open_set, (f_score[neighbor], tie_breaker, neighbor))
                    
        return []