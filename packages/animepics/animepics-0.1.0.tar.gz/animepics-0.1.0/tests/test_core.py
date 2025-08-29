from animepics import get_random_anime_pic

def test_get_random_anime_pic():
    url = get_random_anime_pic()
    assert url.startswith("http"), "Returned URL is not valid"
