from plotter.pixelfigure import PixelFigure

class Main2:
    def __init__(self):
        self.splineInterval = [0, 0.99999]
        
    def run(self):
        figure = PixelFigure()
        
        figure.draw()
    
def run():
    main = Main2()
    main.run()

if __name__ == "__main__":
    run()
