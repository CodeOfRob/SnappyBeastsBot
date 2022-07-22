from __future__ import annotations

import json
from pathlib import Path


class Beerlist:
    def __init__(self, filename: str = "beerdrinkers.json") -> None:
        self.file = Path(filename)
        self.beer_drinkers = dict()
        self.__load_beer_drinkers()

    def __load_beer_drinkers(self) -> None:
        self.file.parent.mkdir(parents=True, exist_ok=True)
        self.file.touch(exist_ok=True)

        if self.file.stat().st_size > 0:
            with self.file.open(mode="r") as f:
                content = json.loads(f.read())

            for element in content:
                drinker = BeerDrinker(
                    element["username"],
                    element["user_id"], 
                    element["beers_drank"], 
                    element["beers_spilled"])
                self.beer_drinkers[element["user_id"]] = drinker

    def __save_beer_drinkers(self) -> None:
        with self.file.open("w") as f:
            f.write(json.dumps([drinker.__dict__ for drinker in self.beer_drinkers.values()]))
       
    def add_action(self, action, user_id, username, count):
        if action not in ["drink", "spill"]: return
        if not user_id in self.beer_drinkers.keys():
            self.beer_drinkers[user_id] = BeerDrinker(username, user_id)

        beer_drinker = self.beer_drinkers[user_id]
        beer_drinker.username = username
        beer_drinker.action(action, count)

        self.__save_beer_drinkers()

    def __str__(self) -> str:
        out = "<b>Beerlist:</b>\n"
        for drinker in self.beer_drinkers.values():
            out += f"- {str(drinker)}"
        return out

class BeerDrinker:
    def __init__(self, username: str, user_id: str, beers_drank: int = 0, beers_spilled: int = 0) -> BeerDrinker:
        self.username = username
        self.user_id = user_id
        self.beers_drank = beers_drank
        self.beers_spilled = beers_spilled
    
    def action(self, action, count = 1) -> BeerDrinker:
        if action == "drink":
            self.beers_drank += count
        elif action == "spill":
            self.beers_spilled += count
        else:
            print(f"action not supported: <{action}>")
        return self

    def __str__(self) -> str:
        return f"{self.username}: 🍻: {self.beers_drank}, 💦: {self.beers_spilled}\n" 
