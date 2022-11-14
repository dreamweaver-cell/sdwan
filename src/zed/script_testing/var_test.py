import click
import yaml
from nested_lookup import nested_lookup


@click.command()
@click.option("--snapvar", "-v", default=False, help="varefile to test")
@click.option("--listvar", "-v", default=False, help="varefile to test")
def main(snapvar, listvar):
    with open(f"{snapvar}") as file:
        variable_list = yaml.safe_load(file, Loader=yaml.FullLoader)

        # print(variable_list)

    with open(f"{listvar}") as f:
        lines = [line.rstrip() for line in f]

    for variable in lines:
        if not nested_lookup(variable, variable_list):
            print(variable)


if __name__ == "__main__":
    """test variables start"""
    main()
