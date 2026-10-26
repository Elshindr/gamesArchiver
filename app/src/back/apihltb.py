from howlongtobeatpy import HowLongToBeat

def get_howlongtobeat_id(id):
    result = HowLongToBeat().search_from_id(id)
    return result.main_story, f"https://howlongtobeat.com/games/{result.json_content.get("game_image")}"


def get_howlongtobeat_name(name):
    results = HowLongToBeat().search(name)
    if results is not None and len(results) > 0:
        best = max(results, key=lambda element: element.similarity)
        return best.main_story, f"https://howlongtobeat.com/games/{best.json_content.get("game_image")}"

    else:
        return None, None

def get_howlongtobeat(id, name):
    print(name, id)
    if id :
        return get_howlongtobeat_id(id)
    else:
        return get_howlongtobeat_name(name)

              
