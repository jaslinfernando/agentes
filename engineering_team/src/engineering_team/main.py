#!/usr/bin/env python
import sys
import warnings
import os
from datetime import datetime

from engineering_team.crew import EngineeringTeam

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# Create output directory if it doesn't exist
os.makedirs('output', exist_ok=True)

requirements = """
The system must allow users to create accounts and link those accounts to bets. Users will be able to place bets and modify their sports bets.

The system must allow users to register a bet on a sporting event, specifying the amount.

The system must calculate the total value of the user's portfolio and the profit or loss on the initial deposit available for betting.

The system must be able to report the user's investments at any time.

The system must be able to report the user's profits or losses at any time.

The system must be able to list the user's transactions over time.

The system must prevent the user from withdrawing funds that would leave them with a negative balance, betting more money than they can afford, or betting on matches that have already been played.

The system has access to the `get_bet(sport)` function, which returns the current bet for a sport and includes a test implementation that returns fixed amounts for soccer, basketball, and baseball.
"""
module_name = "bets.py"
class_name = "Bet"


def run():
    """
    Run the research crew.
    """
    inputs = {
        'requirements': requirements,
        'module_name': module_name,
        'class_name': class_name
    }

    # Create and run the crew
    result = EngineeringTeam().crew().kickoff(inputs=inputs)


if __name__ == "__main__":
    run()