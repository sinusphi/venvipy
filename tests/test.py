# -*- coding: utf-8 -*-
import sys
from time import sleep

from venvipy import venvi


venvi.main()
sleep(5)
venvi.MainWindow.close()

sys.exit(0)
