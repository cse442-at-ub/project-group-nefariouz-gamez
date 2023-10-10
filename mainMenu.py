import pygame

pygame.init()

def display_main_menu(screen):

    background_img = pygame.image.load("images/main_background.png")
    background_img = pygame.transform.scale(background_img, (screen.get_size()[0], screen.get_size()[1]))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        screen.blit(background_img, (0,0))

        pygame.display.flip()

    pygame.quit()
    
if __name__ == "__main__":
    screen = pygame.display.set_mode((1248, 702), pygame.RESIZABLE)
    pygame.display.set_caption("Shrubbery Quest")
    display_main_menu(screen)