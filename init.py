#first screen, lets user pick easy or hard mode

from tkinter import *
import sys

#animation starter code from http://www.cs.cmu.edu/~112/notes/notes-animations-part1.html

def init(data):
    #learned to load image from:
    #http://www.cs.cmu.edu/~112/notes/notes-animations-demos.html#imagesDemo
    
    #image from supermariorun.com, converted to gif at https://www.zamzar.com/con´vert/png-to-gif/
    data.filename = 'images/mario.gif'
    data.image = PhotoImage(file = data.filename)

def mousePressed(event, data):
    # use event.x and event.y
    pass

def keyPressed(event, data):
    # use event.char and event.keysym
    if event.keysym == 'e':
        data.root.destroy()
        import gameStr
    elif event.keysym == 'h':
        data.root.destroy()
        import gameCir

def redrawAll(canvas, data):
    # draw in canvas
    canvas.create_rectangle(0,0,data.width, data.height, fill = 'black')
    canvas.create_text(data.width/2, data.height/8, text = 'Welcome to Mario Kart!', 
                        fill = 'red', font = 'Helvetica 40 bold')
    canvas.create_text(data.width/2, data.height/3, text = 'press E for easy mode!', 
                        fill = 'yellow', font = 'Helvetica 25 bold')
    canvas.create_text(data.width/2, data.height/2.3, text = 'press H for hard mode!', 
                        fill = 'yellow', font = 'Helvetica 25 bold')
    canvas.create_image(data.width/2, data.height*(2/3), image = data.image)

#run function from http://www.cs.cmu.edu/~112/notes/notes-animations-part1.html, slightly modified
def run(width=300, height=300):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height,
                                fill='white', width=0)
        redrawAll(canvas, data)
        canvas.update()

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.root = Tk()
    data.root.resizable(width=False, height=False) # prevents resizing window
    init(data)
    # create the root and the canvas
    canvas = Canvas(data.root, width=data.width, height=data.height)
    canvas.configure(bd=0, highlightthickness=0)
    canvas.pack()
    # set up events
    data.root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    data.root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    redrawAllWrapper(canvas, data)
    # and launch the app
    data.root.mainloop()  # blocks until window is closed
    print("bye!")

run(500, 500)
