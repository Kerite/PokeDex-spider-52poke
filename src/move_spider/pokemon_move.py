"""
技能列表
"""
from pathlib import Path

from bs4 import BeautifulSoup

from src import utils, value_map_dict
from src.utils import OutputType

skill_category_dict = {
    '变化': 'STATUS',
    '物理': 'PHYSICAL',
    '特殊': 'SPECIAL',
    '极巨': 'MAX',
    '超极巨': 'GIGANTAMAX'
}


class PokemonMoveSpider(utils.SpiderBase):
    """
    爬取宝可梦的技能列表
    """

    def __init__(self, output_type=OutputType.SQLITE, output_path: Path = Path("./pokemon.db")):
        super(PokemonMoveSpider, self).__init__(output_type, output_path)

    def _init_database(self):
        self._cursor.execute('DROP TABLE IF EXISTS pokemon_move')
        self._cursor.execute(
            'CREATE TABLE pokemon_move('
            '  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,'
            '  move_id INTEGER,'
            '  name TEXT NOT NULL ,'
            '  jp_name TEXT NOT NULL,'
            '  en_name TEXT NOT NULL,'
            '  type TEXT NOT NULL,'
            '  category TEXT NOT NULL,'
            '  power TEXT NOT NULL,'
            '  accuracy TEXT NOT NULL,'
            '  pp INTEGER NOT NULL,'
            '  description TEXT NOT NULL,'
            '  generation INTEGER NOT NULL'
            ')'
        )
        self._cursor.execute(
            'CREATE INDEX index_move_type on pokemon_move(type)'
        )
        self._cursor.execute(
            'CREATE INDEX index_move_category on pokemon_move(category)'
        )
        self._connection.commit()

    def fetch(self):
        list_url = "https://wiki.52poke.com/zh-hans/%E6%8B%9B%E5%BC%8F%E5%88%97%E8%A1%A8"
        req = utils.request_get(list_url)
        soup = BeautifulSoup(req.text, features="html.parser")
        tables = soup.find_all("table", "hvlist")
        result = []
        for (skill_gen, skill_table) in enumerate(tables):
            # skill_gen = skill_table.find_previous_sibling().span.attrs['id']
            skill_rows = skill_table.find_all("tr")
            for skill_row in skill_rows:
                tds = skill_row.find_all("td")
                if len(tds) > 0:
                    if tds[0].string is not None:
                        skill_id = tds[0].string.replace("\n", "")  # 技能编号
                        skill_name = tds[1].a.string  # 技能名字
                        skill_url = tds[1].a.attrs['href']
                        if skill_name is None:
                            skill_url = tds[1].contents[1].attrs['href']
                            skill_name = tds[1].contents[1].string
                        skill_jp_name = tds[2].string.replace("\n", "")
                        skill_en_name = tds[3].string
                        if skill_en_name is None:
                            skill_en_name = tds[3].span.string
                        skill_en_name = skill_en_name.replace("\n", "")
                        skill_type = tds[4].string.replace("\n", "")
                        skill_damage = tds[5].a.string.replace("\n", "")
                        skill_power = tds[6].string.replace("\n", "")
                        skill_accuracy = tds[7].string.replace("\n", "")
                        skill_pp = tds[8].string.replace("\n", "")
                        skill_description = tds[9].string.replace("\n", "")
                        values = [
                            skill_id.replace('—', ''),
                            skill_name.strip('\u200e'), skill_jp_name, skill_en_name,
                            value_map_dict.pokemon_types[skill_type], skill_category_dict[skill_damage], skill_power,
                            skill_accuracy, skill_pp, skill_description, skill_gen + 1, skill_url
                        ]
                        self._save_data(values)
                        result.append(values)
        return result

    def _save_sqlite(self, data: list):
        self._cursor.execute(
            'INSERT INTO pokemon_move'
            '(move_id, name, jp_name, en_name, type, category, power, accuracy, pp, description, generation)'
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', data)
        self._connection.commit()


if __name__ == "__main__":
    # PokemonMoveSpider(output_path=utils.default_sqlite_path).fetch()
    for item in PokemonMoveSpider(output_type=OutputType.NO_OUT_PUT).fetch():
        print(item)
