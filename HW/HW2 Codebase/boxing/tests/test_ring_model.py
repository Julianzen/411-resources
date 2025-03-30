#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 28 22:05:29 2025

@author: viroop
"""

from dataclasses import asdict

import pytest

from boxing.models.ring_model import RingModel
from boxing.models.boxer_model import Boxer

@pytest.fixture()
def ring_model():
    """Fixture to provide a new instance of RingModel for each test."""
    return RingModel()

"""Fixtures providing sample boxers for the tests."""
@pytest.fixture
def sample_boxer1():
    return Boxer(1, 'Boxer 1', 165, 177, 20, "MIDDLEWEIGHT")

@pytest.fixture
def sample_boxer2():
    return Boxer(2, 'Boxer 2', 140, 150, 25, "LIGHTWEIGHT")

@pytest.fixture
def sample_ringlist(sample_boxer1, sample_boxer2):
    return [sample_boxer1, sample_boxer2]

def test_add_boxer_to_ring(ring_model, sample_boxer1):
    """Test adding a boxer to the ring.

    """
    ring_model.enter_ring(sample_boxer1)
    assert len(ring_model.ring) == 1
    assert ring_model.ring[0].title == 'Boxer 1'


def test_add_three_boxers_to_ring(ring_model, sample_boxer1, sample_boxer2, sample_boxer3):
    """Test error when adding three boxers to the ring.

    """
    ring_model.enter_ring(sample_boxer1)
    ring_model.enter_ring(sample_boxer2)
    
    with pytest.raises(ValueError, match="Ring is full, cannot add more boxers."):
        ring_model.enter_ring(sample_boxer3)


def test_add_bad_song_to_playlist(playlist_model, sample_song1):
    """Test error when adding a duplicate song to the playlist by ID.

    """
    with pytest.raises(TypeError, match="Song is not a valid Song instance"):
        playlist_model.add_song_to_playlist(asdict(sample_song1))


def test_remove_song_from_playlist_by_song_id(playlist_model, sample_playlist):
    """Test removing a song from the playlist by song_id.

    """
    playlist_model.playlist.extend(sample_playlist)
    assert len(playlist_model.playlist) == 2

    playlist_model.remove_song_by_song_id(1)
    assert len(playlist_model.playlist) == 1, f"Expected 1 song, but got {len(playlist_model.playlist)}"
    assert playlist_model.playlist[0].id == 2, "Expected song with id 2 to remain"


def test_remove_song_by_track_number(playlist_model, sample_playlist):
    """Test removing a song from the playlist by track number.

    """
    playlist_model.playlist.extend(sample_playlist)
    assert len(playlist_model.playlist) == 2

    playlist_model.remove_song_by_track_number(1)
    assert len(playlist_model.playlist) == 1, f"Expected 1 song, but got {len(playlist_model.playlist)}"
    assert playlist_model.playlist[0].id == 2, "Expected song with id 2 to remain"


def test_clear_playlist(playlist_model, sample_song1):
    """Test clearing the entire playlist.

    """
    playlist_model.playlist.append(sample_song1)

    playlist_model.clear_playlist()
    assert len(playlist_model.playlist) == 0, "Playlist should be empty after clearing"