#%%
import pygame
import random
import os
import sys
import time

# ----- 게임창 위치설정 -----

win_posx = 700
win_posy = 300
# 윈도우창 위치 설정
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (win_posx, win_posy)

# ----- 전역변수 -----

SCREEN_WIDTH = 480
SCREEN_HEIGHT = 640
FPS = 60

score = 0
playtime = 1

# ----- 색상 -----

BLACK = 0, 0, 0
WHITE = 255,255,255
RED = 255, 0, 0
GREEN1 = 25, 102, 25
GREEN2 = 51, 204, 51
GREEN3 = 233, 249, 185
BLUE = 17, 17, 212
BLUE2 = 0, 0, 255
YELLOW = 255, 255, 0
LIGHT_PINK1 = 255, 230, 255
LIGHT_PINK2 = 255, 204, 255


#%%
# ----- 게임창 설정 -----
def initialize_game(width, height):
    pygame.init()
    surface = pygame.display.set_mode((width, height)) # 화면 표면반환
    pygame.display.set_caption("Chunsik")  # 캡션 이름 'Chunsik'
    return surface

# ----- 게임 로직 -----
def game_loop(surface):
    background = pygame.image.load('background.png')    # 게임진행 배경화면
    background2=pygame.image.load('enter_to_start.png') # 게임실행 배경화면
    bg_rect = background.get_rect()
    clock = pygame.time.Clock()
    sprite_group = pygame.sprite.Group()
    mobs = pygame.sprite.Group()                        # 장애물
    bullets = pygame.sprite.Group()                     # 미사일
    player = PlayerShip()                               # 캐릭터
    coins = pygame.sprite.Group()                       # 코인

    global play_time, total_time                        # 전역함수, 플레이 시간
    play_time=60                                        # 제한시간 60초
    total_time=60

    global player_health                                # 전역함수, 캐릭터 생명력
    player_health= 100                                  # 제한 100
    
    global score                                        # 전역함수 점수
    score = 0
    sprite_group.add(player)
    for i in range(7):                                  # 한번에 생성되는 눈, 코인 수 
        enemy = Mob()
        item = Coin()
        sprite_group.add(item)
        sprite_group.add(enemy)
        mobs.add(enemy)
        coins.add(item)

    running = False
    while 1:
        # 시작 화면 삽입, enter키 눌렀을 때 게임 시작
        if not running:
            surface.blit(background2, (0, 0))                                         
            pygame.display.flip()                                                  
            for event in pygame.event.get():                     
                if event.type == pygame.QUIT:                    
                    pygame.quit()                                
                    exit(0)                                      
                if event.type == pygame.KEYDOWN:                 
                    if event.key==pygame.K_RETURN:                                                
                        running = True
                        start_ticks = pygame.time.get_ticks()

        else:
            # 마우스클릭 하거나 스페이스 버튼 클릭시 슈팅 
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        running = False
                    if event.key == pygame.K_SPACE:
                        player.shoot(sprite_group, bullets)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    player.shoot(sprite_group, bullets)


            sprite_group.update()
            
            # 춘식이와 눈 충돌시 HP 20씩 감소, 0이 되면 gameover 화면 5초 유지 후 게임중지, 리스타트
            hits = pygame.sprite.spritecollide(player, mobs, True)
            if hits:
                print('a mob hits player!')
                player_health -= 20
                if player_health < 0:
                    gameover(surface)
                    close_game()
                    restart()
            
            # 춘식이와 코인 획득시 score 10씩 증가
            gets = pygame.sprite.spritecollide(player, coins, True)
            if gets:
                print('player gets a coin!')
                score += 10

            # 경과 시간 계산
            elapsed_time = (pygame.time.get_ticks() - start_ticks) / 1000 # ms -> s
            textfont=pygame.font.Font('PixelGameFont.ttf', 60)
            play_time=int(total_time - elapsed_time)
            
            # 제한시간 60초 초과했다면 Time over 출력 및 게임 중지
            if total_time - elapsed_time < 0:
                game_result = "Time Over"
                textfont=pygame.font.Font('PixelGameFont.ttf', 60)
                text=textfont.render("Time Over",True,BLACK)
                textpos=text.get_rect()
                textpos.center=(SCREEN_WIDTH/2,SCREEN_HEIGHT/2)
                screen.blit(text,textpos)
                time.sleep(5)
                running = False

            surface.fill(LIGHT_PINK1)
            surface.blit(background, bg_rect)
            sprite_group.draw(surface)
            score_update(surface)
            pygame.display.flip()
            clock.tick(FPS)

    pygame.quit()
    print('game played: ',playtime)

# 상단 점수바 폰트, 위치 설정
def score_update(surface):
    font = pygame.font.Font('PixelGameFont.ttf', 30)
    image = font.render(f'  Score : {score}  HP: {player_health}  Time: {play_time}', True, BLUE2)
    pos = image.get_rect()
    pos.move_ip(10,10)
    pygame.draw.rect(image, BLACK,(pos.x-10, pos.y-10, pos.width, pos.height), 2)
    surface.blit(image, pos)

# gameover 화면 띄우기
def gameover(surface):
    gameover_bg=pygame.image.load('GAME_OVER_FULL.png')
    surface.blit(gameover_bg, (0, 0)) 
    pygame.display.update()
    time.sleep(5)

# 게임창 닫기
def close_game():
    pygame.quit()
    print('Game closed')

# 게임창 리스타트
def restart():
    screen = initialize_game(SCREEN_WIDTH,SCREEN_HEIGHT)
    game_loop(screen)
    close_game()

# 캐릭터 동작 
class PlayerShip(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('chunsik.png')     # 캐릭터 이미지 삽입
        self.rect = self.image.get_rect()
        self.rect.centerx = int(SCREEN_WIDTH / 2)         # 캐릭터 시작 위치 정의 (화면 가운데)
        self.rect.centery = SCREEN_HEIGHT - 20
        self.speedx = 0
        self.speedy = 0
    
    # 춘식이 움직임, 속도, 화면에서 벗어나지 않도록 경계값 설정
    def update(self):
        self.speedx = 0
        self.speedy = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx = -5
        if keystate[pygame.K_RIGHT]:
            self.speedx = 5
        if keystate[pygame.K_UP]:
            self.speedy = -5
        if keystate[pygame.K_DOWN]:
            self.speedy = 5
        self.rect.x += self.speedx
        self.rect.y += self.speedy

        # 캐릭터 화면에서 벗어나지 않게 함수 정의
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
        if self.rect.top < 0:
            self.rect.top = 0
    
    #미사일 발사
    def shoot(self, all_sprites,bullets):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)

class Coin(pygame.sprite.Sprite):
    def __init__(self): # 클래스 초기화
        pygame.sprite.Sprite.__init__(self) # 스프라이트 초기화
        self.image = pygame.image.load('coin.png')
        self.image = pygame.transform.scale(self.image, (30,30))
        self.rect = self.image.get_rect() # 스프라이트로 그려준다
        # 코인의 생성 위치와 속도 랜덤하게 설정
        self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 8)
        self.speedx = random.randrange(-3, 3)
        self.direction_change = False

    # 코인 움직임
    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy

        if self.rect.top > SCREEN_HEIGHT + 10 or self.rect.left < -25 or self.rect.right > SCREEN_WIDTH + 20:
            self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(3, 8) 


class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        # 눈 크기 랜덤하게 선택하여 생성
        snowImage=['snow_S.png','snow_M.png','snow_L.png']
        self.image = pygame.image.load(random.choice(snowImage))
        self.rect = self.image.get_rect()
        # 코인의 생성 위치와 속도 랜덤하게 설정
        self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 8)
        self.speedx = random.randrange(-3, 3)
        self.direction_change = False
    
    # 눈 움직임
    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy

        if self.rect.top > SCREEN_HEIGHT + 10 or self.rect.left < -25 or self.rect.right > SCREEN_WIDTH + 20:
            self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(3, 8)

   

class Bullet(pygame.sprite.Sprite):
    def __init__(self, player_x, player_y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((10,20))
        self.image.fill(GREEN1)
        self.rect = self.image.get_rect()
        self.rect.bottom = player_y
        self.rect.centerx = player_x
        self.speedy = - 10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

if __name__ == '__main__':
    screen = initialize_game(SCREEN_WIDTH,SCREEN_HEIGHT)
    game_loop(screen)
    sys.exit()
# %%
