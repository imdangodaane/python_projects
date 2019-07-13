import pyglet


display = pyglet.canvas.get_display()
screen = display.get_default_screen()

window = pyglet.window.Window()
label = pyglet.text.Label("Hello World",
                          font_name="Ubuntu Mono",
                          font_size=50,
                          x=window.width//2, y=window.height//2,
                          anchor_x="center", anchor_y="center")

@window.event
def on_draw():
    window.clear()
    label.draw()

pyglet.app.run()
