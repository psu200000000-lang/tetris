import pygame
import random
import sys
import numpy as np

# Pygame 초기화
pygame.init()

# 게임 상수
GRID_WIDTH = 10
GRID_HEIGHT = 20
BLOCK_SIZE = 20
WINDOW_WIDTH = GRID_WIDTH * BLOCK_SIZE + 120
WINDOW_HEIGHT = GRID_HEIGHT * BLOCK_SIZE

# 색상 정의 (옛날 테트리스 색상)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_GRAY = (20, 20, 20)
LIGHT_GRAY = (100, 100, 100)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
MAGENTA = (255, 0, 255)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# 테트리스 피스 정의
PIECES = [
    {'shape': [[1, 1, 1, 1]], 'color': CYAN},           # I
    {'shape': [[1, 1], [1, 1]], 'color': YELLOW},       # O
    {'shape': [[0, 1, 0], [1, 1, 1]], 'color': MAGENTA},# T
    {'shape': [[1, 0, 0], [1, 1, 1]], 'color': BLUE},   # L
    {'shape': [[0, 0, 1], [1, 1, 1]], 'color': ORANGE}, # J
    {'shape': [[0, 1, 1], [1, 1, 0]], 'color': GREEN},  # S
    {'shape': [[1, 1, 0], [0, 1, 1]], 'color': RED}     # Z
]

def create_block_sound():
    """벽돌 소리 생성"""
    sample_rate = 22050
    duration = 0.1
    frequency = 400
    frames = int(sample_rate * duration)
    arr = np.sin(2.0 * np.pi * frequency * np.linspace(0, duration, frames))
    arr = (arr * 32767).astype(np.int16)
    arr = np.repeat(arr.reshape(frames, 1), 2, axis=1)
    sound = pygame.mixer.Sound(arr)
    return sound

class Button:
    """게임 버튼 클래스"""
    def __init__(self, x, y, width, height, text, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.is_hovered = False
    
    def draw(self, screen):
        # 버튼 테두리
        color = LIGHT_GRAY if self.is_hovered else WHITE
        pygame.draw.rect(screen, color, self.rect, 2)
        
        # 버튼 텍스트
        text_surface = self.font.render(self.text, True, color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
    
    def is_clicked(self, mouse_pos, mouse_pressed):
        return self.rect.collidepoint(mouse_pos) and mouse_pressed

class TetrisGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("TETRIS")
        self.clock = pygame.time.Clock()
        # 픽셀 폰트 스타일 (작은 크기로 옛날 느낌)
        self.small_font = pygame.font.Font(None, 16)
        self.medium_font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 40)
        
        # 사운드 초기화
        pygame.mixer.init()
        self.block_sound = create_block_sound()
        
        # 재시작 버튼 (가운데)
        button_x = WINDOW_WIDTH // 2 - 50
        button_y = WINDOW_HEIGHT // 2 + 50
        self.restart_button = Button(button_x, button_y, 100, 30, 'Restart', self.small_font)
        
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.score = 0
        self.lines = 0
        self.level = 1
        self.game_over = False
        self.paused = False
        
        self.current_piece = self.create_new_piece()
        self.next_piece = self.create_new_piece()
        self.current_x = GRID_WIDTH // 2 - 1
        self.current_y = 0
        
        self.drop_speed = 1000 - (self.level - 1) * 100
        self.last_drop_time = pygame.time.get_ticks()
        
    def create_new_piece(self):
        piece = random.choice(PIECES)
        return {
            'shape': [row[:] for row in piece['shape']],
            'color': piece['color']
        }
    
    def move_piece(self, dx, dy):
        self.current_x += dx
        self.current_y += dy
        
        if self.is_colliding():
            self.current_x -= dx
            self.current_y -= dy
            return False
        return True
    
    def is_colliding(self):
        piece = self.current_piece['shape']
        
        for y in range(len(piece)):
            for x in range(len(piece[y])):
                if piece[y][x] == 0:
                    continue
                
                new_x = self.current_x + x
                new_y = self.current_y + y
                
                if new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT:
                    return True
                
                if new_y >= 0 and self.grid[new_y][new_x] != 0:
                    return True
        
        return False
    
    def rotate_piece(self):
        piece = self.current_piece['shape']
        rotated = [[piece[y][x] for y in range(len(piece)-1, -1, -1)] 
                   for x in range(len(piece[0]))]
        
        original_shape = self.current_piece['shape']
        self.current_piece['shape'] = rotated
        
        if self.is_colliding():
            self.current_piece['shape'] = original_shape
    
    def is_grid_full(self):
        # 화면이 모두 찼는지 확인
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x] == 0:
                    return False
        return True
    
    def lock_piece(self):
        piece = self.current_piece['shape']
        
        for y in range(len(piece)):
            for x in range(len(piece[y])):
                if piece[y][x] != 0:
                    grid_y = self.current_y + y
                    grid_x = self.current_x + x
                    
                    if grid_y >= 0:
                        if grid_y < GRID_HEIGHT and 0 <= grid_x < GRID_WIDTH:
                            self.grid[grid_y][grid_x] = self.current_piece['color']
                    else:
                        self.game_over = True
                        return
        
        self.clear_lines()
        
        self.current_piece = self.next_piece
        self.next_piece = self.create_new_piece()
        self.current_x = GRID_WIDTH // 2 - 1
        self.current_y = 0
        
        # 새로운 피스가 맨 위에서 블록과 충돌하면 게임 오버
        if self.is_colliding():
            self.game_over = True
    
    def clear_lines(self):
        lines_cleared = 0
        y = GRID_HEIGHT - 1
        
        while y >= 0:
            if all(self.grid[y][x] != 0 for x in range(GRID_WIDTH)):
                del self.grid[y]
                self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])
                lines_cleared += 1
            else:
                y -= 1
        
        if lines_cleared > 0:
            self.lines += lines_cleared
            self.score += lines_cleared * lines_cleared * 100
            
            # 라인 제거될 때마다 벽돌 소리 재생
            self.block_sound.play()
            
            if self.lines % 5 == 0:
                self.level += 1
                self.drop_speed = max(100, 1000 - (self.level - 1) * 100)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_r:
                        self.__init__()
                    continue
                
                if event.key == pygame.K_LEFT:
                    self.move_piece(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    self.move_piece(1, 0)
                elif event.key == pygame.K_UP:
                    self.rotate_piece()
                elif event.key == pygame.K_DOWN:
                    self.move_piece(0, 1)
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
            
            # 마우스 클릭 이벤트
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if self.game_over and self.restart_button.is_clicked(mouse_pos, True):
                    self.__init__()
        
        return True
    
    def update(self):
        if self.game_over or self.paused:
            return
        
        current_time = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()
        
        # 아래 화살표가 눌려있으면 빠른 낙하
        current_drop_speed = self.drop_speed
        if keys[pygame.K_DOWN]:
            current_drop_speed = 50  # 매우 빠르게 내려감
        
        if current_time - self.last_drop_time > current_drop_speed:
            if not self.move_piece(0, 1):
                self.lock_piece()
            self.last_drop_time = current_time
    
    def draw_grid(self):
        # 게임판 테두리
        pygame.draw.rect(self.screen, WHITE, (0, 0, GRID_WIDTH * BLOCK_SIZE, GRID_HEIGHT * BLOCK_SIZE), 2)
        
        # 게임판 배경 (검은색)
        pygame.draw.rect(self.screen, BLACK, (1, 1, GRID_WIDTH * BLOCK_SIZE - 2, GRID_HEIGHT * BLOCK_SIZE - 2))
        
        # 격자의 블록들
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x] != 0:
                    # 블록 채우기
                    block_x = x * BLOCK_SIZE
                    block_y = y * BLOCK_SIZE
                    pygame.draw.rect(self.screen, self.grid[y][x], 
                                   (block_x, block_y, BLOCK_SIZE, BLOCK_SIZE))
                    
                    # 3D 입체감 효과 (밝은 선)
                    pygame.draw.line(self.screen, WHITE, 
                                   (block_x, block_y), (block_x + BLOCK_SIZE, block_y), 1)
                    pygame.draw.line(self.screen, WHITE, 
                                   (block_x, block_y), (block_x, block_y + BLOCK_SIZE), 1)
                    
                    # 3D 입체감 효과 (어두운 선)
                    pygame.draw.line(self.screen, BLACK, 
                                   (block_x + BLOCK_SIZE, block_y), (block_x + BLOCK_SIZE, block_y + BLOCK_SIZE), 1)
                    pygame.draw.line(self.screen, BLACK, 
                                   (block_x, block_y + BLOCK_SIZE), (block_x + BLOCK_SIZE, block_y + BLOCK_SIZE), 1)
    
    def draw_current_piece(self):
        if self.paused:
            return
        
        piece = self.current_piece['shape']
        
        for y in range(len(piece)):
            for x in range(len(piece[y])):
                if piece[y][x] != 0:
                    draw_x = self.current_x + x
                    draw_y = self.current_y + y
                    
                    if draw_y >= 0:
                        # 블록 채우기
                        block_x = draw_x * BLOCK_SIZE
                        block_y = draw_y * BLOCK_SIZE
                        pygame.draw.rect(self.screen, self.current_piece['color'],
                                       (block_x, block_y, BLOCK_SIZE, BLOCK_SIZE))
                        
                        # 3D 입체감 효과 (밝은 선)
                        pygame.draw.line(self.screen, WHITE, 
                                       (block_x, block_y), (block_x + BLOCK_SIZE, block_y), 1)
                        pygame.draw.line(self.screen, WHITE, 
                                       (block_x, block_y), (block_x, block_y + BLOCK_SIZE), 1)
                        
                        # 3D 입체감 효과 (어두운 선)
                        pygame.draw.line(self.screen, BLACK, 
                                       (block_x + BLOCK_SIZE, block_y), (block_x + BLOCK_SIZE, block_y + BLOCK_SIZE), 1)
                        pygame.draw.line(self.screen, BLACK, 
                                       (block_x, block_y + BLOCK_SIZE), (block_x + BLOCK_SIZE, block_y + BLOCK_SIZE), 1)
    
    def draw_info(self):
        # 우측 정보 패널
        info_x = GRID_WIDTH * BLOCK_SIZE + 10
        
        # 제목
        title = self.medium_font.render('TETRIS', True, WHITE)
        self.screen.blit(title, (info_x, 10))
        
        # 구분선
        pygame.draw.line(self.screen, WHITE, (info_x, 35), (WINDOW_WIDTH - 5, 35), 1)
        
        # 점수
        score_label = self.small_font.render('SCORE', True, WHITE)
        score_value = self.small_font.render(str(self.score).zfill(6), True, WHITE)
        self.screen.blit(score_label, (info_x, 45))
        self.screen.blit(score_value, (info_x, 60))
        
        # 레벨
        level_label = self.small_font.render('LEVEL', True, WHITE)
        level_value = self.small_font.render(str(self.level), True, WHITE)
        self.screen.blit(level_label, (info_x, 85))
        self.screen.blit(level_value, (info_x, 100))
        
        # 라인
        lines_label = self.small_font.render('LINES', True, WHITE)
        lines_value = self.small_font.render(str(self.lines), True, WHITE)
        self.screen.blit(lines_label, (info_x, 125))
        self.screen.blit(lines_value, (info_x, 140))
        
        # 구분선
        pygame.draw.line(self.screen, WHITE, (info_x, 165), (WINDOW_WIDTH - 5, 165), 1)
        
        # 다음 피스
        next_label = self.small_font.render('NEXT', True, WHITE)
        self.screen.blit(next_label, (info_x, 175))
        
        piece = self.next_piece['shape']
        for y in range(len(piece)):
            for x in range(len(piece[y])):
                if piece[y][x] != 0:
                    pygame.draw.rect(self.screen, self.next_piece['color'],
                                   (info_x + x * 12, 200 + y * 12, 12, 12))
                    pygame.draw.rect(self.screen, WHITE,
                                   (info_x + x * 12, 200 + y * 12, 12, 12), 1)
        
        # 일시정지 상태
        if self.paused:
            pause_text = self.small_font.render('PAUSED', True, WHITE)
            self.screen.blit(pause_text, (info_x, WINDOW_HEIGHT - 40))
    
    def draw_game_over(self):
        if not self.game_over:
            return
        
        # 반투명 오버레이
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # 게임 오버 텍스트 (흔들리지 않음)
        game_over_text = self.large_font.render('end', True, WHITE)
        score_text = self.medium_font.render(f'Score: {self.score}', True, WHITE)
        
        self.screen.blit(game_over_text, (WINDOW_WIDTH // 2 - game_over_text.get_width() // 2, 60))
        self.screen.blit(score_text, (WINDOW_WIDTH // 2 - score_text.get_width() // 2, 130))
        
        # 버튼이 커졌다 작아졌다 하는 효과
        import math
        current_time = pygame.time.get_ticks()
        
        # 크기 변화 (0.7 ~ 1.3 배)
        scale = 0.7 + abs(math.sin(current_time * 0.008)) * 0.6
        
        # 원래 버튼 크기
        original_width = self.restart_button.rect.width
        original_height = self.restart_button.rect.height
        
        # 스케일된 크기
        scaled_width = int(original_width * scale)
        scaled_height = int(original_height * scale)
        
        # 버튼을 중앙에 유지하기 위해 오프셋 계산
        offset_x = (original_width - scaled_width) // 2
        offset_y = (original_height - scaled_height) // 2
        
        # 재시작 버튼 (크기 변화)
        button_rect = pygame.Rect(
            self.restart_button.rect.x + offset_x,
            self.restart_button.rect.y + offset_y,
            scaled_width,
            scaled_height
        )
        
        # 버튼 테두리
        color = LIGHT_GRAY if self.restart_button.is_hovered else WHITE
        pygame.draw.rect(self.screen, color, button_rect, 2)
        
        # 버튼 텍스트 (스케일된 크기)
        text_surface = self.restart_button.font.render(self.restart_button.text, True, color)
        scaled_text_surface = pygame.transform.scale(text_surface, 
                                                     (int(text_surface.get_width() * scale),
                                                      int(text_surface.get_height() * scale)))
        text_rect = scaled_text_surface.get_rect(center=button_rect.center)
        self.screen.blit(scaled_text_surface, text_rect)
    
    def draw(self):
        self.screen.fill(DARK_GRAY)
        self.draw_grid()
        self.draw_current_piece()
        self.draw_info()
        self.draw_game_over()
        
        # 마우스 위치 업데이트
        mouse_pos = pygame.mouse.get_pos()
        if self.game_over:
            self.restart_button.update(mouse_pos)
        
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game = TetrisGame()
    game.run()
