import logging
import math
from typing import List

from boxing.models.boxers_model import Boxer, update_boxer_stats
from boxing.utils.logger import configure_logger
from boxing.utils.api_utils import get_random


logger = logging.getLogger(__name__)
configure_logger(logger)


class RingModel:
    """
    A class to manage the Boxers in the Ring.
    
    Attributes:
        ring: The list of boxers in the ring.
    """
    def __init__(self):
        """
        Initializes RingModel Object with an empty list of Boxers.

        """
        self.ring: List[Boxer] = []

    def fight(self) -> str:
        """
        Simulates a fight between two boxers and decides the winner and loser.
        
        Arguments:
            self: The RingModel object 
            
        Exceptions Raised:
            ValueError if the ring does not have 2 boxers so a fight can not occur.
            
        Returns:
            The name of the Boxer that won.
        """
        if len(self.ring) < 2:
            logger.error("Need two boxers for a fight to happen.")
            raise ValueError("There must be two boxers to start a fight.")

        boxer_1, boxer_2 = self.get_boxers()

        skill_1 = self.get_fighting_skill(boxer_1)
        skill_2 = self.get_fighting_skill(boxer_2)

        # Compute the absolute skill difference
        # And normalize using a logistic function for better probability scaling
        delta = abs(skill_1 - skill_2)
        normalized_delta = 1 / (1 + math.e ** (-delta))

        random_number = get_random()

        if random_number < normalized_delta:
            winner = boxer_1
            loser = boxer_2
        else:
            winner = boxer_2
            loser = boxer_1

        update_boxer_stats(winner.id, 'win')
        update_boxer_stats(loser.id, 'loss')

        self.clear_ring()

        logger.info("Winner of the fight will be shown now.")
        return winner.name

    def clear_ring(self):
        """
         Clears the ring of any boxers.
         
         Argument:
             self: The RingModel object.
        
        Returns:
            Nothing
        """ 
        
        logger.info("Received request to clear the ring of any Boxers.")
        
        if not self.ring:
            return
        self.ring.clear()

    def enter_ring(self, boxer: Boxer):
        """
         Makes a Boxer enter the ring.
         
         Arguments:
             self: The RingModel object
             boxer: Instance of a Boxer Object representing a boxer. 
             
        Returns:
            Nothing
        """ 
        
        if not isinstance(boxer, Boxer):
            logger.error("boxer is not an instance of Boxer")
            raise TypeError(f"Invalid type: Expected 'Boxer', got '{type(boxer).__name__}'")

        if len(self.ring) >= 2:
            logger.error("Ring is already at maximum capacity.")
            raise ValueError("Ring is full, cannot add more boxers.")

        self.ring.append(boxer)

    def get_boxers(self) -> List[Boxer]:
        """
          Retrieve a list of boxers currently in the ring.

        Returns:
            List[Boxer]: A list of Boxer objects representing the boxers in the ring.

        Note:
            If there are no boxers in the ring, the function will simply return an empty list.
        """ 
        if not self.ring:
            pass
        else:
            pass

        logger.info(f"Retrieving list of boxers from ring: {self.ring}")
        return self.ring

    def get_fighting_skill(self, boxer: Boxer) -> float:
        """
             Calculate and return the fighting skill of a given boxer.

            The fighting skill is determined using an arbitrary formula based on the boxer's weight,
            name length, reach, and age. Age modifiers are applied as follows:
            - Age < 25: -1 modifier
            - Age > 35: -2 modifier
            - Age 25-35: No modifier

            Arguments:
                boxer (Boxer): The boxer whose skill is to be calculated.

            Returns:
                float: The calculated fighting skill of the boxer.
        """ 
        # Arbitrary calculations
        age_modifier = -1 if boxer.age < 25 else (-2 if boxer.age > 35 else 0)
        skill = (boxer.weight * len(boxer.name)) + (boxer.reach / 10) + age_modifier

        logger.info(f"Retrieving boxer {boxer.name} and their skill: {skill}")
        return skill
