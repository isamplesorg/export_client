import click


@click.command()
@click.option(
    "-v",
    "--verbosity",
    default="DEBUG",
    help="Specify logging level",
    show_default=True,
)
def main(verbosity: str):
    """
    This is a sample python main script, driven by Click
    """
    print(f"Hello World, verbosity is {verbosity}")


"""
Stub main python script, ready to go
"""
if __name__ == "__main__":
    main()
