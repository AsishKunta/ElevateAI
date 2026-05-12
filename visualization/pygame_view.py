"""
Pygame visualization for the ElevateAI simulator.

Provides real-time graphical representation of the elevator system
including building layout, elevator positions, request indicators,
and dashboard metrics.
"""

import pygame
from typing import Dict, List, Tuple
from core.building import Building
from core.elevator import Elevator


class PygameView:
    """
    Pygame-based visualization for the elevator simulation.

    Attributes:
        building (Building): The building being visualized.
        screen (pygame.Surface): Main rendering surface.
        width (int): Screen width.
        height (int): Screen height.
        fps (int): Frames per second.
    """

    BACKGROUND = (18, 24, 38)
    SHAFT_COLOR = (40, 55, 80)
    FLOOR_LINE_COLOR = (90, 110, 140)
    TEXT_COLOR = (230, 230, 240)
    ELEVATOR_COLORS = [(88, 217, 255), (255, 146, 118), (163, 255, 146), (255, 226, 89)]
    REQUEST_UP_COLOR = (98, 255, 165)
    REQUEST_DOWN_COLOR = (255, 112, 112)
    DASHBOARD_PANEL = (35, 46, 72)

    def __init__(self, building: Building, width: int = 1100, height: int = 720, fps: int = 30):
        pygame.init()
        pygame.font.init()

        self.building = building
        self.width = width
        self.height = height
        self.fps = fps
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("ElevateAI - Elevator Simulator")
        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont("Arial", 18)
        self.title_font = pygame.font.SysFont("Arial", 24, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 16)

        self.dashboard_width = 280
        self.building_width = self.width - self.dashboard_width - 40
        self.building_left = 20
        self.building_top = 20
        self.building_bottom = self.height - 20
        self.floor_count = max(self.building.floors, 10)
        self.floor_height = (self.building_bottom - self.building_top) / self.floor_count
        self.elevator_gap = self.building_width / max(len(self.building.elevators), 1)
        self.elevator_width = min(80, int(self.elevator_gap * 0.7))
        self.step_progress = 0.0
        self.paused = False
        self.current_algorithm = "FCFS"

    def handle_events(self) -> Dict[str, bool]:
        """
        Process Pygame events and translate them into simulation controls.

        Returns:
            Dict[str, bool]: Keys for quit, pause, and request generation.
        """
        controls = {
            "quit": False,
            "toggle_pause": False,
            "toggle_algorithm": False,
            "new_up_request": False,
            "new_down_request": False,
        }

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                controls["quit"] = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    controls["quit"] = True
                elif event.key == pygame.K_SPACE:
                    controls["toggle_pause"] = True
                elif event.key == pygame.K_a:
                    controls["toggle_algorithm"] = True
                elif event.key == pygame.K_u:
                    controls["new_up_request"] = True
                elif event.key == pygame.K_d:
                    controls["new_down_request"] = True

        return controls

    def set_step_progress(self, progress: float) -> None:
        """
        Update the visualization interpolation progress between simulation steps.
        """
        self.step_progress = min(max(progress, 0.0), 1.0)

    def render(self, simulation_time: int) -> None:
        """
        Render the current simulator state to the screen.

        Args:
            simulation_time (int): Current simulated time.
        """
        self.screen.fill(self.BACKGROUND)
        self._draw_building_shell()
        self._draw_floor_lines()
        self._draw_request_indicators()
        self._draw_elevators()
        self._draw_dashboard(simulation_time)
        pygame.display.flip()

    def _draw_building_shell(self) -> None:
        """Draw the building shaft and boundary."""
        shaft_rect = pygame.Rect(
            self.building_left,
            self.building_top,
            self.building_width,
            self.building_bottom - self.building_top,
        )
        pygame.draw.rect(self.screen, self.SHAFT_COLOR, shaft_rect, border_radius=10)

    def _draw_floor_lines(self) -> None:
        """
        Draw horizontal floor lines and floor labels.

        Floor coordinates are mapped from building floor index to screen Y position.
        """
        for floor in range(self.floor_count):
            y = self._floor_y(floor)
            pygame.draw.line(
                self.screen,
                self.FLOOR_LINE_COLOR,
                (self.building_left, y),
                (self.building_left + self.building_width, y),
                2,
            )

            label = self.font.render(f"Floor {floor}", True, self.TEXT_COLOR)
            self.screen.blit(label, (self.building_left - 90, y - 10))

    def _draw_elevators(self) -> None:
        """
        Draw moving elevators as animated rectangles.

        Elevator positions are interpolated between last_floor and current_floor
        to create smooth motion without changing simulation timestep.
        """
        for index, elevator in enumerate(self.building.elevators):
            color = self.ELEVATOR_COLORS[index % len(self.ELEVATOR_COLORS)]
            x = self.building_left + self.elevator_gap * index + (self.elevator_gap - self.elevator_width) / 2
            interpolated_floor = elevator.last_floor + (elevator.current_floor - elevator.last_floor) * self.step_progress
            y = self._floor_y(interpolated_floor)
            elevator_rect = pygame.Rect(x, y - self.floor_height + 6, self.elevator_width, self.floor_height - 12)
            pygame.draw.rect(self.screen, color, elevator_rect, border_radius=8)
            pygame.draw.rect(self.screen, self.BACKGROUND, elevator_rect, 2, border_radius=8)

            label = self.small_font.render(f"E{elevator.elevator_id}", True, self.BACKGROUND)
            self.screen.blit(label, (x + 8, y - self.floor_height + 12))

            state_text = self.small_font.render(self._elevator_state_label(elevator), True, self.TEXT_COLOR)
            self.screen.blit(state_text, (x, y + 6))

    def _draw_request_indicators(self) -> None:
        """
        Show active floor requests as ↑/↓ text indicators.

        Requests are displayed beside their source floors.
        Multiple requests on the same floor are stacked vertically.
        Indicators are removed after pickup.
        """
        floor_requests: Dict[int, List[int]] = {}
        for request in self.building.get_all_requests():
            if not request.picked_up and not request.completed:
                floor_requests.setdefault(request.source_floor, []).append(request.direction)

        for floor, directions in floor_requests.items():
            y = self._floor_y(floor)
            x = self.building_left + self.building_width + 15

            # Count up and down requests
            up_count = directions.count(1)
            down_count = directions.count(-1)

            # Render indicators with proper spacing
            indicator_y_offset = -16
            if up_count > 0:
                up_text = self.font.render("↑", True, self.REQUEST_UP_COLOR)
                self.screen.blit(up_text, (x, y + indicator_y_offset))
                indicator_y_offset += 18

            if down_count > 0:
                down_text = self.font.render("↓", True, self.REQUEST_DOWN_COLOR)
                self.screen.blit(down_text, (x, y + indicator_y_offset))

    def _draw_arrow(self, position: Tuple[int, int], upward: bool) -> None:
        """
        Draw an up or down arrow icon for a floor request.
        
        This method is kept for compatibility but uses text rendering
        which is cleaner and more readable than polygon shapes.
        """
        x, y = position
        text = "↑" if upward else "↓"
        color = self.REQUEST_UP_COLOR if upward else self.REQUEST_DOWN_COLOR
        arrow_text = self.font.render(text, True, color)
        self.screen.blit(arrow_text, (x, y))

    def _draw_dashboard(self, simulation_time: int) -> None:
        """
        Render the side dashboard with simulation metrics.

        Dashboard layout (top to bottom):
        - Title
        - Simulation Info (time, algorithm, state)
        - Blank line
        - Metrics section (performance data)
        - Blank line
        - Elevator States
        - Blank line
        - Controls (help text)
        """
        panel_x = self.width - self.dashboard_width - 10
        panel_y = self.building_top
        panel_rect = pygame.Rect(panel_x, panel_y, self.dashboard_width, self.building_bottom - self.building_top)
        pygame.draw.rect(self.screen, self.DASHBOARD_PANEL, panel_rect, border_radius=16)

        y_offset = panel_y + 16
        line_height = 22

        # ========== TITLE ==========
        title = self.title_font.render("Dashboard", True, self.TEXT_COLOR)
        self.screen.blit(title, (panel_x + 16, y_offset))
        y_offset += 36

        # ========== SIMULATION INFO SECTION ==========
        info_header = self.small_font.render("SIMULATION INFO", True, (200, 200, 220))
        self.screen.blit(info_header, (panel_x + 16, y_offset))
        y_offset += 20

        now_text = self.font.render(f"Time: {simulation_time}s", True, self.TEXT_COLOR)
        self.screen.blit(now_text, (panel_x + 16, y_offset))
        y_offset += line_height

        algorithm_text = self.font.render(f"Algorithm: {self.current_algorithm}", True, self.TEXT_COLOR)
        self.screen.blit(algorithm_text, (panel_x + 16, y_offset))
        y_offset += line_height

        pause_status = "PAUSED" if self.paused else "RUNNING"
        pause_text = self.font.render(f"State: {pause_status}", True, self.TEXT_COLOR)
        self.screen.blit(pause_text, (panel_x + 16, y_offset))
        y_offset += line_height + 8

        # ========== METRICS SECTION ==========
        metrics_header = self.small_font.render("METRICS", True, (200, 200, 220))
        self.screen.blit(metrics_header, (panel_x + 16, y_offset))
        y_offset += 20

        completed = len([req for req in self.building.get_all_requests() if req.completed])
        total = len(self.building.get_all_requests())
        completed_text = self.font.render(f"Completed: {completed}/{total}", True, self.TEXT_COLOR)
        self.screen.blit(completed_text, (panel_x + 16, y_offset))
        y_offset += line_height

        wait_times = [
            req.pickup_time - req.timestamp
            for req in self.building.get_all_requests()
            if req.pickup_time is not None
        ]
        average_wait = sum(wait_times) / len(wait_times) if wait_times else 0.0
        wait_text = self.font.render(f"Avg. Wait: {average_wait:.1f}s", True, self.TEXT_COLOR)
        self.screen.blit(wait_text, (panel_x + 16, y_offset))
        y_offset += line_height

        total_distance = sum(e.total_distance for e in self.building.elevators)
        distance_text = self.font.render(f"Distance: {total_distance}f", True, self.TEXT_COLOR)
        self.screen.blit(distance_text, (panel_x + 16, y_offset))
        y_offset += line_height

        idle_time = sum(e.idle_time for e in self.building.elevators)
        idle_text = self.font.render(f"Idle Time: {idle_time}s", True, self.TEXT_COLOR)
        self.screen.blit(idle_text, (panel_x + 16, y_offset))
        y_offset += line_height

        efficiency = (completed / total_distance * 100) if total_distance > 0 else 0.0
        efficiency_text = self.font.render(f"Efficiency: {efficiency:.1f}%", True, self.TEXT_COLOR)
        self.screen.blit(efficiency_text, (panel_x + 16, y_offset))
        y_offset += line_height

        active_requests = len([req for req in self.building.get_all_requests() if not req.completed])
        active_text = self.font.render(f"Active: {active_requests}", True, self.TEXT_COLOR)
        self.screen.blit(active_text, (panel_x + 16, y_offset))
        y_offset += line_height + 8

        # ========== ELEVATOR STATES SECTION ==========
        elevator_header = self.small_font.render("ELEVATOR STATES", True, (200, 200, 220))
        self.screen.blit(elevator_header, (panel_x + 16, y_offset))
        y_offset += 20

        for elevator in self.building.elevators:
            state_line = f"E{elevator.elevator_id}: {self._elevator_state_label(elevator)}"
            line_text = self.small_font.render(state_line, True, self.TEXT_COLOR)
            self.screen.blit(line_text, (panel_x + 16, y_offset))
            y_offset += line_height
        
        y_offset += 8

        # ========== CONTROLS SECTION ==========
        controls_header = self.small_font.render("CONTROLS", True, (200, 200, 220))
        self.screen.blit(controls_header, (panel_x + 16, y_offset))
        y_offset += 20

        controls = [
            "ESC: Quit",
            "SPACE: Pause",
            "A: Scheduler",
            "U: UP req",
            "D: DOWN req",
        ]
        for line in controls:
            control_text = self.small_font.render(line, True, self.TEXT_COLOR)
            self.screen.blit(control_text, (panel_x + 16, y_offset))
            y_offset += 18

    def _elevator_state_label(self, elevator: Elevator) -> str:
        """
        Return a readable state label for an elevator.

        Uses the elevator's explicit state property for accurate representation.
        """
        if elevator.state == "IDLE":
            return "IDLE"
        elif elevator.state == "MOVING_UP":
            return f"UP → F{elevator.target_floor}"
        elif elevator.state == "MOVING_DOWN":
            return f"DOWN → F{elevator.target_floor}"
        elif elevator.state == "PICKING_UP":
            return f"PICKUP @ F{elevator.current_floor}"
        elif elevator.state == "DROPPING_OFF":
            return f"DROP @ F{elevator.current_floor}"
        else:
            return "UNKNOWN"

    def _floor_y(self, floor: float) -> float:
        """Map a floor value to the screen Y coordinate."""
        return self.building_bottom - floor * self.floor_height

    def close(self) -> None:
        """Shut down Pygame cleanly."""
        pygame.quit()
