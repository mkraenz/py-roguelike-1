from dataclasses import dataclass
from py_roguelike_tutorial.procgen.procgen_config import (
    ProcgenConfig as data,
)
import random
from py_roguelike_tutorial.entity import Item
from py_roguelike_tutorial.procgen.gen_helpers import (
    get_max_row_for_floor,
    get_prefabs_at_random,
)


@dataclass(frozen=True)
class ShopGenerationParams:
    max_floors_ahead: int


def generate_shop_inventory(
    params: ShopGenerationParams,
    current_floor: int,
) -> list[Item]:
    up_to_floor = random.randint(current_floor, current_floor + params.max_floors_ahead)
    number_of_items = random.randint(
        get_max_row_for_floor(data.MAX_SHOP_ITEMS_BY_FLOOR, current_floor).max_value,
        get_max_row_for_floor(data.MAX_SHOP_ITEMS_BY_FLOOR, up_to_floor).max_value,
    )
    items = get_prefabs_at_random(data.item_chances, number_of_items, up_to_floor)
    return items
