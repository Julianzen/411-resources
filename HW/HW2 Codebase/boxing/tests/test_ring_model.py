#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 28 22:05:29 2025

@author: viroop
"""

from dataclasses import asdict

import pytest

from boxing.models.ring_model import RingModel
from boxing.models.boxers_model import Boxer

@pytest.fixture()
def ring_model():
    """Fixture to provide a new instance of RingModel for each test."""
    return RingModel()

"""Fixtures providing sample boxers for the tests."""
@pytest.fixture
def sample_boxer1():
    return Boxer(1, 'Boxer 1', 165, 177, 72.0, 28, "MIDDLEWEIGHT")  

@pytest.fixture
def sample_boxer2():
    return Boxer(2, 'Boxer 2', 140, 150, 69.5, 25, "LIGHTWEIGHT")

@pytest.fixture
def sample_boxer3():
    return Boxer(3, 'Boxer 3', 170, 175, 74.5, 27, "MIDDLEWEIGHT")

@pytest.fixture
def sample_ringlist(sample_boxer1, sample_boxer2):
    return [sample_boxer1, sample_boxer2]

def test_add_boxer_to_ring(ring_model, sample_boxer1):
    """Test adding a boxer to the ring.

    """
    ring_model.enter_ring(sample_boxer1)
    assert len(ring_model.ring) == 1
    assert ring_model.ring[0].name == 'Boxer 1'

def test_add_two_boxers_to_ring(ring_model, sample_boxer1, sample_boxer2):
    """Test error when adding three boxers to the ring.

    """
    ring_model.enter_ring(sample_boxer1)
    ring_model.enter_ring(sample_boxer2)
    
    assert len(ring_model.ring) == 2
    assert ring_model.ring[0].name == 'Boxer 1'
    assert ring_model.ring[1].name == 'Boxer 2'

def test_add_three_boxers_to_ring(ring_model, sample_boxer1, sample_boxer2, sample_boxer3):
    """Test error when adding three boxers to the ring.

    """
    ring_model.enter_ring(sample_boxer1)
    ring_model.enter_ring(sample_boxer2)
    
    with pytest.raises(ValueError, match="Ring is full, cannot add more boxers."):
        ring_model.enter_ring(sample_boxer3)

def test_clear_ring(ring_model, sample_boxer1, sample_boxer2):
    """Test clearing the ring.
    
    """
    
    ring_model.enter_ring(sample_boxer1)
    ring_model.enter_ring(sample_boxer2)

    ring_model.clear_ring()
    assert len(ring_model.ring) == 0
    
def test_add_bad_boxer_to_ring(ring_model, sample_boxer1):
    """Test error when adding a non-Boxer instance (e.g. a dict) to the ring.
    
    """
    
    with pytest.raises(TypeError, match="Invalid type: Expected 'Boxer'"):
        ring_model.enter_ring(asdict(sample_boxer1))

def test_fight_with_two_boxers_boxer_one_wins(ring_model, sample_boxer1, sample_boxer2, mocker):
    """
    Tests fight between two boxers with predetermined random_number value in fight method. Boxer 1 should win due to get_random being too low based on sample boxers.

    """
    mocker.patch("boxing.models.ring_model.get_random", return_value=0.1)

    ring_model.enter_ring(sample_boxer1)
    ring_model.enter_ring(sample_boxer2)

    assert ring_model.fight() == 'Boxer 1'

def test_fight_with_two_boxers_boxer_two_wins(ring_model, sample_boxer1, sample_boxer2, mocker):
    """
    Tests fight between two boxers with predetermined random_number value in fight method. Boxer 2 should win due to get_random being too low based on sample boxers.

    """
    mocker.patch("boxing.models.ring_model.get_random", return_value=0.9)

    ring_model.enter_ring(sample_boxer1)
    ring_model.enter_ring(sample_boxer2)

    assert ring_model.fight() == 'Boxer 2'
    

def test_get_one_boxer_from_ring(ring_model, sample_boxer1):
    """
    Tests that the ring has one boxers once one boxer is added.

    """
    ring_model.enter_ring(sample_boxer1)
    
    assert ring_model.get_boxers() == [sample_boxer1]
    
def test_get_two_boxers_from_ring(ring_model, sample_boxer1, sample_boxer2):
    """
    Tests that the ring has two boxers once two boxers are added.

    """
    ring_model.enter_ring(sample_boxer1)
    ring_model.enter_ring(sample_boxer2)
    
    assert ring_model.get_boxers() == [sample_boxer1, sample_boxer2]
    
def test_get_fighting_skill_calculation(ring_model):
    """
    Tests that fighting skill calculation given by get_fighting_skill function is correct by comparing own manual calculation to function calculation.
    
    """
    boxer = Boxer(10, 'Test Boxer', 210, 177, 40.2, 30, 'HEAVYWEIGHT')
    skill = ring_model.get_fighting_skill(boxer)

    expected = 210 * 10 + (40.2 / 10) + 0  
    assert skill == expected

