import pygame
import random
import time
import highscore

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 706

class Title:
    def __init__(self, screen):

        #loads background music when game starts, with try except
        try:
            pygame.mixer.music.load("./resource/music.wav")
            pygame.mixer.music.set_volume(.5)
            pygame.mixer.music.play(-1)
        except pygame.error as err:
            print(err)

	    #creates titleimage
        pygame.display.set_caption("BU Invasion")
        self.title_screen = pygame.image.load("./resource/title.png")
        screen.blit(self.title_screen, (0, 0))
        pygame.display.flip()

class Background(pygame.sprite.Sprite):

    def __init__(self):

        #generates sprite of background image
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(pygame.image.load("./resource/background.png"), [SCREEN_WIDTH, SCREEN_HEIGHT])
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0

class Enemy(pygame.sprite.Sprite):

    def __init__(self, multiplier):

        #generates sprite for UFO image
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(pygame.image.load("./resource/enemy.png"), [100, 42])
        self.rect = self.image.get_rect()
        self.reset_pos()
        #used to increase the speed of the enemies as time progresses
        self.speed = multiplier // 2

    #generates the enemies into 6 columns, randomly generated
    def reset_pos(self):
        self.rect.x = random.choice([0, 100, 200, 300, 400, 500])
        self.rect.y = random.randrange(-SCREEN_HEIGHT, 0)

    #allows enemies to move by updating position
    def update(self):
        self.rect.y += self.speed
        if self.rect.y > SCREEN_HEIGHT + self.rect.height:
            self.reset_pos()

class Rocket(pygame.sprite.Sprite):

    def __init__(self):

        #generates sprite of player
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(pygame.image.load("./resource/rocket.png"), [60, 77])
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH // 2
        self.rect.y = SCREEN_HEIGHT * 10 // 14

    #moves the rocket according to the cursor position
    def update(self):
        pos = pygame.mouse.get_pos()
        self.rect.x = pos[0]
        self.rect.y = pos[1]

class Bullet(pygame.sprite.Sprite):

    def __init__(self, x, y):

        #generates sprite bullet image
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(pygame.image.load("./resource/bullet.png"), (10, 10))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 10

    #shoots the bullet forward when it is created
    def update(self):
        self.rect.y -= self.speed

class Game(object):

    def __init__(self, screen):

        self.score = 0
        self.game_over = False

        # sprite lists
        self.background = pygame.sprite.Group()
        self.rocket = pygame.sprite.Group()
        self.enemy_list = pygame.sprite.Group()
        self.bullet_list = pygame.sprite.Group()

        #screen for score counter and flag for counter
        self.wn = screen
        self.scorer = True

        #calls the database with the top 5 scores
        self.high_score_database = highscore.HighScore(5)

        #used to blit the score counter later on
        self.scorefont = pygame.font.Font(None, 50)
        self.hiscore = self.scorefont.render("Score: " + str(self.score), True, (255, 255, 255))
        self.score_x = (SCREEN_WIDTH) - (108 + self.hiscore.get_width())
        self.score_y = (SCREEN_HEIGHT) - (20 + self.hiscore.get_height())

        # background
        self.background.add(Background())

        # rocket
        self.player = Rocket()
        self.rocket.add(self.player)

        # timer for enemy spawn (generates new enemies every 1000 milliseconds)
        self.enemy_spawn = 1000
        self.last_spawn = 0

        # uses the multiplier in order to increase enemies' speed as game progresses
        self.enemy_multiplier = 2
        self.INCREMENT = True

        # timer for bullet firing rate (you can only shoot every 300 milliseconds)
        self.interval = 300
        self.lasttime = 0

    def enemy_respawn(self):

            #controls how often new enemies respawn
            now = pygame.time.get_ticks()
            if self.score % 10 == 1:
                self.INCREMENT = True

            #every 10 points, the multiplier increases to make enemies accelerate
            if (self.score % 10 == 0) and self.INCREMENT and (self.score != 0):
                self.enemy_multiplier += 1
                self.INCREMENT = False

            #makes it so that enemies only respawn every 1000 milliseconds
            if (now - self.last_spawn) > self.enemy_spawn:
                self.enemy_list.add(Enemy(self.enemy_multiplier))
                self.last_spawn = now

    def handle_event(self):

        #controls the fire rate for the rocket
        now = pygame.time.get_ticks()

        for event in pygame.event.get():

            if (now - self.lasttime) > self.interval :

                #click X in window, game closes
                if event.type == pygame.QUIT:
                    return True

                elif event.type == pygame.MOUSEBUTTONDOWN:

                    #click mouse on game over screen, game resets
                    if self.game_over:
                        self.high_score_database.closeConnection()
                        self.__init__(self.wn)

                    else:
                        #plays sound effect when rocket shoots
                        try:
                            sound = pygame.mixer.Sound("./resource/shoot.wav")
                            sound.play()
                            sound.set_volume(.3)
                        except pygame.error as err:
                            print(err)

                        #click mouse, bullet shoots
                        self.bullet_list.add(Bullet(self.player.rect.x + self.player.image.get_width()//2, self.player.rect.y))
                        self.lasttime = pygame.time.get_ticks()

                #press ESC key, game closes
                elif event.type == pygame.KEYDOWN:
                    if event.key == 27:
                        return True

                    #press SPACEBAR, bullet shoots
                    elif event.key == 32:
                        self.bullet_list.add(Bullet(self.player.rect.x + self.player.image.get_width()//2, self.player.rect.y))
                        self.lasttime = pygame.time.get_ticks()

        return False

    def scoreCount(self):
        #prints new score every time you destroy an enemy
        if self.scorer:
            self.hiscore = self.scorefont.render("Score: " + str(self.score), True, (255, 255, 255))
            self.scorer = False
        self.wn.blit(self.hiscore, [self.score_x, self.score_y])

    def run_logic(self):

        if not self.game_over:
            # update sprites
            self.rocket.update()
            self.enemy_list.update()
            self.bullet_list.update()

            # check collision player and enemy
            hit_list = pygame.sprite.spritecollide(self.player, self.enemy_list, True)
            # if play hits enemy, game over
            if len(hit_list) != 0:
                self.game_over = True
                self.high_score_database.addScore("Player", self.score)

            # check collision bullet and enemy
            for bullet in self.bullet_list:
                if bullet.rect.y <= 0:
                    self.bullet_list.remove(bullet)

                #when bullet collides with enemy, both disappear & flag initiates score counter
                enemy_hit_list = pygame.sprite.spritecollide(bullet, self.enemy_list, True)
                for enemy in enemy_hit_list:
                    self.score += 1
                    self.bullet_list.remove(bullet)
                    self.scorer = True

                    #plays sound effect once an enemy is destroyed
                    try:
                        sound = pygame.mixer.Sound("./resource/boom.wav")
                        sound.play()
                        sound.set_volume(.3)
                    except pygame.error as err:
                        print(err)

                    break

            #if enemy touches university, game over
            for enemy in self.enemy_list:
                if enemy.rect.y > SCREEN_HEIGHT - 160:
                    self.game_over = True
                    self.high_score_database.addScore("Player", self.score)

    def display_frame(self, screen):

        if self.game_over:

            #checks to see if your score is better than the lowest high score, returns True or False
            high_score_flag = self.high_score_database.checkHighScore(self.score)

            #if you get high score, prints Congratulations message
            if high_score_flag:
                font = pygame.font.SysFont(None, 40)
                congrats = font.render("Congratulations, you're in the top five!", True, (255, 255, 255))
                screen.blit(congrats, [(SCREEN_WIDTH // 2) - (congrats.get_width() // 2), 40])

            #returns all scores in database
            db = self.high_score_database.highScorers()

            #prints each high score from database on screen with Player and Score
            accum = 1
            for s in db:
                font = pygame.font.SysFont(None, 40)
                name1 = str(s[0])
                score1 = str(s[1])
                hiscore_display = font.render((name1 + "       " + score1), True, (255, 255, 255))
                screen.blit(hiscore_display, [(SCREEN_WIDTH // 2) - (hiscore_display.get_width() // 2), (50 + (accum * 40))])
                accum += 1

                #prints Game Over screen
                font = pygame.font.SysFont(None, 50)
                text = font.render("Game Over, click to restart", True, (255,255,255))
                center_x = (SCREEN_WIDTH // 2) - (text.get_width() // 2)
                center_y = (SCREEN_HEIGHT // 2) - (text.get_height() // 2)
                screen.blit(text, [center_x, center_y])

        #updates screen as game plays
        if not self.game_over:
            self.background.draw(screen)
            self.rocket.draw(screen)
            self.enemy_list.draw(screen)
            self.bullet_list.draw(screen)
            self.scoreCount()

        pygame.display.flip()


def main():
    pygame.init()

    #screen dimensions
    size = [SCREEN_WIDTH, SCREEN_HEIGHT]
    screen = pygame.display.set_mode(size)

    #hides mouse cursor
    pygame.mouse.set_visible(False)

    #game does not initiate during title screen
    game_started = False

    #create our objects and set the data
    done = False
    clock = pygame.time.Clock()

    #create an instance of the Game class with screen as parameter for score counter
    game = Game(screen)

    #generates title menu
    title = Title(screen)

    #main game loop
    while not done:

        if not game_started:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                        game_started = True

        else:
	        #process events (keystrokes, mouse clicks, etc)
            done = game.handle_event()

	        #update object positions, check for collisions
            game.run_logic()

	        #draw the current frame
            game.display_frame(screen)

            #generates new enemy spawn points
            game.enemy_respawn()

	        #updates screen
            clock.tick()

    #close window and exit
    pygame.quit()

if __name__ == "__main__":
    main()
