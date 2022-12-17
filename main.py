import typer
from src.core import settings  # export ENVIROMENT
from src.scripts.autohic import mul_gen_png


def run():
    typer.run(mul_gen_png)

# TODO: add logger to file

if __name__ == '__main__':
    run()
