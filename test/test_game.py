# coding: utf-8
import datetime
from unittest import mock

import requests
import pytest
import sys
import time

from _common import *
from boardgamegeek import BGGError, BGGItemNotFoundError, BGGValueError
from boardgamegeek.objects.games import BoardGameVideo, BoardGameVersion, BoardGameRank
from boardgamegeek.objects.games import PlayerSuggestion


@mock.patch("requests.sessions.Session.get")
def test_get_unknown_game_info(mock_get, bgg):
    mock_get.side_effect = simulate_bgg

    with pytest.raises(BGGItemNotFoundError):
        game = bgg.game(TEST_INVALID_GAME_NAME)


@mock.patch("requests.sessions.Session.get")
def test_get_game_with_invalid_parameters(mock_get, bgg):
    mock_get.side_effect = simulate_bgg

    with pytest.raises(BGGError):
        bgg.game(name=None, game_id=None)

    for invalid in [None, ""]:
        with pytest.raises(BGGError):
            bgg.game(invalid)

    for invalid in [None, "", "asd"]:
        with pytest.raises(BGGError):
            bgg.game(None, game_id=invalid)


def check_game(game):
    assert game is not None
    assert game.name == TEST_GAME_NAME
    assert game.id == TEST_GAME_ID
    assert game.year == 2007
    assert game.mechanics == ['Area Enclosure', 'Card Drafting',
                              'Hand Management', 'Variable Player Powers',
                              'Worker Placement']
    assert game.min_players == 1
    assert game.max_players == 5
    assert game.thumbnail == "https://cf.geekdo-images.com/images/pic259085_t.jpg"
    assert game.image == "https://cf.geekdo-images.com/images/pic259085.jpg"
    assert game.playing_time > 100
    assert game.min_age == 12

    assert "Economic" in game.categories
    assert "Farming" in game.categories

    assert game.families == ['Agricola', 'Animals: Cattle', 'Animals: Horses',
                             'Animals: Pigs', 'Animals: Sheep', 'Harvest Series',
                             'Solitaire Games', 'Tableau Building']
    assert game.designers == ["Uwe Rosenberg"]
    assert game.artists == ["Klemens Franz"]

    assert "Lookout Games" in game.publishers
    assert u"Compaya.hu - Gamer Café Kft." in game.publishers

    assert u"Агрикола" in game.alternative_names
    assert u"아그리콜라" in game.alternative_names

    assert len(game.description) == 1985

    assert game.users_rated == 51439
    assert game.rating_average == 8.0345
    assert game.rating_bayes_average == 7.93694
    assert game.rating_stddev == 1.56465
    assert game.rating_median == 0.0
    assert game.rating_num_weights == 5540
    assert game.rating_average_weight == 3.6319
    assert game.boardgame_rank == 15

    assert game.users_owned == 62141
    assert game.users_trading == 1121
    assert game.users_wanting == 1120
    assert game.users_wishing == 8407
    assert game.users_commented == 11034

    assert len(game.expansions) == 23
    assert 43018 in [g.id for g in game.expansions]

    # check for videos
    assert type(game.videos) == list
    assert len(game.videos) > 0
    for vid in game.videos:
        assert type(vid) == BoardGameVideo
        assert type(vid.id) == int
        assert type(vid.name) in STR_TYPES_OR_NONE
        assert type(vid.category) in STR_TYPES_OR_NONE
        assert type(vid.language) in STR_TYPES_OR_NONE
        assert type(vid.uploader) in STR_TYPES_OR_NONE
        assert vid.link.startswith("http")
        assert type(vid.uploader_id) == int
        assert type(vid.post_date) == datetime.datetime

    # check for versions
    assert type(game.versions) == list
    assert len(game.versions) > 0
    for ver in game.versions:
        assert type(ver) == BoardGameVersion
        assert type(ver.id) == int
        assert type(ver.name) in STR_TYPES_OR_NONE
        assert type(ver.language) in STR_TYPES_OR_NONE
        assert type(ver.publisher) in STR_TYPES_OR_NONE
        assert type(ver.artist) in STR_TYPES_OR_NONE
        assert type(ver.product_code) in STR_TYPES_OR_NONE
        assert type(ver.year) == int
        assert type(ver.width) == float
        assert type(ver.length) == float
        assert type(ver.depth) == float
        assert type(ver.weight) == float

    # check the ranks of the result, to make sure everything is returned properly
    assert type(game.ranks) == list
    for rank in game.ranks:
        assert type(rank) == BoardGameRank
        assert type(rank.type) in STR_TYPES_OR_NONE

    # check player suggestions were retrieved
    assert type(game.player_suggestions) == list
    suggestions_not_found = set(range(game.min_players, game.max_players + 1))

    for sg in game.player_suggestions:
        assert type(sg) == PlayerSuggestion
        assert type(sg.player_count) == str
        assert type(sg.numeric_player_count) == int
        assert type(sg.best) == int
        assert type(sg.not_recommended) == int
        assert type(sg.recommended) == int
        try:
            # the test game has a number of players between 1 and 5, but also a suggestion for 5+ players (huh?)
            # That's why the try...except here.
            suggestions_not_found.remove(sg.numeric_player_count)
        except:
            pass

    # should have found suggestions for all number of players
    assert not len(suggestions_not_found)

    # make sure no exception gets thrown
    repr(game)


@mock.patch("requests.sessions.Session.get")
def test_get_known_game_info(mock_get, bgg, null_logger):
    mock_get.side_effect = simulate_bgg

    # use an older game that's not so likely to change
    game = bgg.game(TEST_GAME_NAME, videos=True, versions=True)

    check_game(game)

    # for coverage's sake
    game._format(null_logger)

    assert type(game.data()) == dict


@mock.patch("requests.sessions.Session.get")
def test_get_known_game_info_by_id(mock_get, bgg):
    mock_get.side_effect = simulate_bgg

    game = bgg.game(None, game_id=TEST_GAME_ID, videos=True, versions=True)
    check_game(game)


@mock.patch("requests.sessions.Session.get")
def test_get_known_game_info_by_id_list(mock_get, bgg):
    mock_get.side_effect = simulate_bgg

    game_list = bgg.game_list(game_id_list=[TEST_GAME_ID, TEST_GAME_ID_2],
                              videos=True, versions=True)
    check_game(game_list[0])


def test_game_id_with_invalid_params(bgg):
    with pytest.raises(BGGValueError):
        bgg.get_game_id(TEST_GAME_NAME, choose="voodoo")


@mock.patch("requests.sessions.Session.get")
def test_get_game_id_by_name(mock_get, bgg):
    mock_get.side_effect = simulate_bgg

    game_id = bgg.get_game_id(TEST_GAME_NAME)
    assert game_id == TEST_GAME_ID

    # Use the game "Eclipse" to test the game choosing methods
    all_eclipse_games = bgg.games("eclipse")

    game_id = bgg.get_game_id("eclipse", choose="first")
    assert game_id == all_eclipse_games[0].id

    game_id = bgg.get_game_id("eclipse", choose="recent")
    recent_year = -100000
    recent_id = None
    for g in all_eclipse_games:
        if g.year > recent_year:
            recent_id = g.id
            recent_year = g.year
    assert game_id == recent_id

    game_id = bgg.get_game_id("eclipse", choose="best-rank")
    best_rank = 1000000000
    best_id = None
    for g in all_eclipse_games:
        if g.boardgame_rank is not None and g.boardgame_rank < best_rank:
            best_id = g.id
            best_rank = g.boardgame_rank
    assert game_id == best_id


@mock.patch("requests.sessions.Session.get")
def test_get_games_by_name(mock_get, bgg, null_logger):
    mock_get.side_effect = simulate_bgg

    games = bgg.games("coup")

    for g in games:
        assert g is not None
        assert type(g.id) == int
        assert g.name == "Coup"
        g._format(null_logger)

    assert len(games) > 1

@mock.patch("requests.sessions.Session.get")
def test_implementations(mock_get, bgg):
    mock_get.side_effect = simulate_bgg

    game = bgg.game(game_id=TEST_GAME_WITH_IMPLEMENTATIONS_ID)

    assert game.id == TEST_GAME_WITH_IMPLEMENTATIONS_ID
    assert len(game.implementations) == 2
    assert "Age of Industry" in game.implementations
    assert "Brass: Birmingham" in game.implementations


@mock.patch("requests.sessions.Session.get")
def test_get_expansion(mock_get, bgg):
    mock_get.side_effect = simulate_bgg

    game = bgg.game(game_id=TEST_GAME_EXPANSION_ID)

    assert game.id == TEST_GAME_EXPANSION_ID
    assert game.expansion

    assert len(game.expands) == 2
    expanded_game_ids = [g.id for g in game.expands]
    assert 169786 in expanded_game_ids
    assert 199727 in expanded_game_ids


@mock.patch("requests.sessions.Session.get")
def test_get_accessory(mock_get, bgg):
    mock_get.side_effect = simulate_bgg

    game = bgg.game(game_id=TEST_GAME_ACCESSORY_ID)

    assert game.id == TEST_GAME_ACCESSORY_ID
    assert game.accessory
