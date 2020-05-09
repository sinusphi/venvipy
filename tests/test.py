# -*- coding: utf-8 -*-
from time import sleep

from venvipy import venvi


main_ui = venvi.MainWindow()

venvi.main()
sleep(5)

if venvi.main():
    main_ui.on_close()
