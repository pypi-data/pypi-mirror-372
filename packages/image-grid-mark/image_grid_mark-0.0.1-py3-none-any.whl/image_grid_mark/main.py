# coding: utf-8

from image_grid_mark.resource_manager import ResourceManager
from image_grid_mark.tk_inf import App


def main():
    rm = ResourceManager()
    app = App(rm=rm)
    app.mainloop()


if __name__ == "__main__":
    main()
