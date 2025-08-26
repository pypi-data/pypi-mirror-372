from matplotlib import pyplot as plt


def plot(img):
    """ Plota uma imagem usando matplotlib."""
    plt.imshow(img, cmap='gray')
    
    plt.axis('off')             
    plt.show()

    
    

imagem = plt.imread(r"C:\Users\User\OneDrive\Imagens\eu\danielsansrj.png")
plot(imagem)
    