from setuptools import setup

setup(
    name='dragonboard',
    version='0.0.5',
    description='A reader library for the cta dragonboard data',
    url='http://github.com/cta-observatory/dragonboard_testbench',
    author='Kai Brügge, Mario Hörbe, Dominik Neise, Maximilian Nöthe',
    author_email='kai.bruegge@tu-dortmund.de',
    license='MIT',
    install_requires=[
        'numpy',
        'matplotlib',
        'scipy',
        'pandas',
        'tqdm',
        'joblib',
    ],
    packages=['dragonboard', 'dragonboard.tools'],
    entry_points={
        'gui_scripts': [
            'dragonviewer = dragonboard.__main__:main',
            'dragonboard_fakedata = dragonboard.tools.create_fake_data:main',
            'dragonboard_calc_calib_constants = dragonboard.tools.calc_calib_constants:main',
            'dragonboard_dataextraction = dragonboard.tools.dataextraction:main',
            'calc_timelapse_constants = dragonboard.tools.calc_timelapse_constants:main',
        ]
    }
)
