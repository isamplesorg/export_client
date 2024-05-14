import click
import requests
import json

@click.command()
@click.option(
    "-u",
    "--url",
    help="The url to the JSON schema.",
    default="https://raw.githubusercontent.com/isamplesorg/metadata/main/src/schemas/iSamplesSchemaCore1.0.json"
)
def main(url: str):
    response = requests.get(url)
    jsonschema_content = response.json()
    properties = jsonschema_content.get("properties")
    table_column_list = []
    table_columns = {"table:columns": table_column_list}
    # turn each item into something like this:
    #                 {
    #                     "name": "sample_identifier",
    #                     "description": "URI that identifies the physical sample described by this record",
    #                     "type": "string"
    #                 },
    # and it comes in looking like this:
    #        "sample_identifier": {
    #        "description": "URI that identifies the physical sample described by this record",
    #        "type": "string"
    #    },
    #
    #
    #
    for key, value in properties.items():
        next_column = {
            "name": key,
            "description": value.get("description"),
            "type": value.get("type") or "string"
        }
        table_column_list.append(next_column)
    result = json.dumps(table_columns, indent=2)
    print(result)


if __name__ == "__main__":
    main()
