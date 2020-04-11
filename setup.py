from distutils.core import setup
setup(
  name = 'venvipy',
  packages = ['venvipy'],
  version = '1.0',
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'A GUI for managing Python virtual environments. Built with PyQt5.',
  author = 'Youssef Serestou',
  author_email = 'youssef.serestou.83@gmail.com',
  url = 'https://github.com/sinusphi/venvipy',
  download_url = 'https://github.com/sinusphi/venvipy/archive/v_1.tar.gz',
  keywords = ["python", "python3", "venv", "virtualenvironment", "pyqt", "pyqt5", "pyqt5-desktop-application", "gui"],
  install_requires=[            # I get to this in a second
          'PyQt5',
          'PyQt5-sip',
      ],
  classifiers=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
  ],
)
