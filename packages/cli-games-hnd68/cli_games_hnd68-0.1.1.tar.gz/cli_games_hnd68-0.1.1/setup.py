from setuptools import setup, find_packages

setup(
    name="cli-games-hnd68",  # pip install name
    version="0.1.1",
    description="Fun CLI games: Number Guessing Duel, Math Quiz Duel, Typing Speed Race",
    author="Wai Phyo Aung",
    author_email="info@waiphyoaung.dev",
    url="https://github.com/Orgpg/CLI-Game",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    entry_points={
        'console_scripts': [
            'guessing=cli_games.guess_the_number:play_game',
            'mathquiz=cli_games.math_quiz_duel:play_game',
            'typerace=cli_games.typing_speed_race:play_game',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
