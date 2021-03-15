import csv
from dataclasses import dataclass, field
from pprint import pprint
from pathlib import Path
from typing import List, Optional

from mkdocs.plugins import BasePlugin


class Plugin(BasePlugin):
    pass


@dataclass
class Item:
    name: str
    sku: str
    qty: int
    length: Optional[float]


@dataclass
class Product:
    name: str
    sku: str
    items: List[Item] = field(default_factory=list)


def define_env(env):
    def generate_hardware_bom_tables(products):
        for index, product in enumerate(products):
            yield f""
            yield f"#### {product.name} (`{product.sku}`)"
            yield f"| SKU | Product name | QTY | Length (mm) |"
            yield f"| --- | ------------ | --- | ------ |"
            for item in product.items:
                length = item.length if item.length else ""
                yield f"| `{item.sku}` | {item.name} | {item.qty} | {length} |"

    @env.macro
    def hardware_bom(file_path: str):
        with open(Path(env.conf["docs_dir"]) / file_path, newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=",", quotechar='"')
            is_next_product = False
            is_next_item = False
            products = []
            for row in reader:
                if not row[1] or row[1].upper() == "B.O.M.":
                    continue
                elif row[4].upper() == "ITEM NAME":
                    is_next_item = True
                elif row[4].upper() == "PRODUCT NAME":
                    is_next_product = True
                    is_next_item = False
                    continue
                elif is_next_item:
                    item = Item(name=row[4], sku=row[1], qty=row[0], length=None)
                    if row[2]:
                        item.length = row[2]
                    products[-1].items.append(item)
                elif is_next_product:
                    products.append(Product(name=row[4], sku=row[1]))
                    is_next_product = False

        return "\n".join(generate_hardware_bom_tables(products))

    @env.macro
    def printed_parts_bom(file_path: str, repo_base_url: Optional[str] = None):
        if repo_base_url is None:
            repo_base_url = env.variables['config']['repo_url']
        table = []
        table.append(f"| Category | Name | QTY | Link |")
        table.append(f"| -------- | ---- | --- | ---- |")
        with open(Path(env.conf["docs_dir"]) / file_path, newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=",", quotechar='"')
            for row in reader:
                table.append(
                    f"| {row[0]} | {row[1]} | {row[2]} | [:material-download: Download]({repo_base_url}/tree/main{row[3]}){{: target=_blank }} |"
                )

        return "\n".join(table)
