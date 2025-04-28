import pandas as pd
import random
from collections import defaultdict

def generate_initial_schedule(players, dates, original_schedule_df):
    """
    Generates a random initial schedule, ensuring each player plays a similar
    number of matches, AND takes into account existing 'S' and 'X' values
    from the original schedule.

    Args:
        players (list): List of player names.
        dates (list): List of date columns.
        original_schedule_df (pd.DataFrame): DataFrame containing the original schedule.

    Returns:
        pd.DataFrame: DataFrame with the initial schedule.
    """
    schedule = original_schedule_df.copy()

    # Create a list of (player, date) combinations, excluding those already filled
    player_dates = []
    for player in players:
        for date in dates:
            if schedule.loc[player, date] == 'NaN':  # Only consider empty slots
                player_dates.append((player, date))
    random.shuffle(player_dates)  # Shuffle for randomness

    for player, date in player_dates:
      if 'S' in schedule[date].values:
        if schedule[date].value_counts()['S'] < 4:
          if schedule.loc[player, date] == 'NaN' and schedule.loc[player].value_counts()['S'] <= 9:
            schedule.loc[player, date] = 'S'
          elif schedule.loc[player, date] == 'NaN' and schedule.loc[player].value_counts()['S'] > 9:
            schedule.loc[player, date] = 'X'
        else:
          for player in players:
            if schedule.loc[player, date] == 'NaN':
              schedule.loc[player, date] = 'X'
      else:
        schedule.loc[player, date] = 'S'
      

    return schedule



def calculate_round_robbin_score(schedule, players):
    """
    Calculates a score based on how close the schedule is to a round-robin format.
    A higher score indicates that players have played with each other more.

    Args:
        schedule (pd.DataFrame): The schedule data.
        players (list): List of player names

    Returns:
        int: The round-robin score.
    """
    played_with_counts = {player: defaultdict(int) for player in players}
    total_pairs = 0
    possible_pairs = len(players) * (len(players) -1) / 2

    for date in schedule.columns:
        # Get the players scheduled on this date
        scheduled_players = [player for player in players if schedule.loc[player, date] == 'S']
        # Iterate through all unique pairs of players
        for i in range(len(scheduled_players)):
            for j in range(i + 1, len(scheduled_players)):
                player1 = scheduled_players[i]
                player2 = scheduled_players[j]
                # Increment the count for each player having played with the other
                played_with_counts[player1][player2] += 1
                played_with_counts[player2][player1] += 1
                total_pairs += 1

    # Calculate a score based on the distribution of "played with" counts
    round_robin_score = 0
    for player in players:
        for other_player in players:
            if player != other_player:
                round_robin_score += played_with_counts[player][other_player]
    return round_robin_score / possible_pairs # Normalize


def calculate_balance_score(schedule, players):
    """
    Calculates a score based on how balanced the schedule is in terms of
    the number of matches played by each player.

    Args:
        schedule (pd.DataFrame): The schedule data.
        players (list): List of player names.

    Returns:
        int: The balance score.
    """
    player_match_counts = {player: 0 for player in players}
    for player in players:
        for date in schedule.columns:
            if schedule.loc[player, date] == 'S':
                player_match_counts[player] += 1

    # Calculate the standard deviation of match counts
    match_counts = list(player_match_counts.values())
    if len(match_counts) > 0:
      std_dev = pd.Series(match_counts).std()
    else:
      std_dev = 0
    # A lower standard deviation means a more balanced schedule, so subtract
    # it from a maximum value (number of dates) to get a positive score
    balance_score = len(schedule.columns) - std_dev
    return balance_score

def calculate_aidan_score(schedule, players, dates):
    """
    Calculates a score based on how many of Aidan's matches are scheduled
    in May, June, and July.

    Args:
        schedule (pd.DataFrame): The schedule data.
        players (list): List of player names.
        dates (list): List of date columns.

    Returns:
        int: The Aidan score.
    """
    aidan_score = 0
    dt_dates = pd.to_datetime(dates, format='%d-%b')
    for date, dt_date in list(zip(dates, dt_dates)):
        if dt_date.month in [4, 5, 6, 7] and schedule.loc['Aidan', date] == 'S':
            aidan_score += 1
    return aidan_score

def calculate_total_score(schedule, players, dates):
    """
    Calculates a weighted total score for the schedule, considering
    balance, round-robin, and Aidan's preferences.

    Args:
        schedule (pd.DataFrame): The schedule data.
        players (list): List of player names.
        dates (list): List of date columns.

    Returns:
        float: The total score.
    """
    round_robin_score = calculate_round_robbin_score(schedule, players)
    balance_score = calculate_balance_score(schedule, players)
    aidan_score = calculate_aidan_score(schedule, players, dates)

    # You can adjust these weights to change the importance of each factor
    total_score = (0.4 * balance_score + 0.3 * round_robin_score + 0.3 * aidan_score)
    return total_score

def optimize_schedule(players, dates, original_schedule_df, iterations=1000):
    """
    Optimizes the golf schedule by generating random variations and
    selecting the one with the highest total score.

    Args:
        players (list): List of player names.
        dates (list): List of date columns.
        original_schedule_df (pd.DataFrame): The original schedule
        iterations (int, optional): Number of optimization iterations.
            Defaults to 1000.

    Returns:
        pd.DataFrame: The optimized schedule.
    """
    best_schedule = None
    best_score = -1
    print("Starting optimization...")

    for i in range(iterations):
        if (i + 1) % 100 == 0:
            print(f"Iteration: {i + 1}/{iterations}")
        # Generate a new random schedule on each iteration
        current_schedule = generate_initial_schedule(players, dates, original_schedule_df) # Pass the original schedule
        current_score = calculate_total_score(current_schedule, players, dates)

        if current_score > best_score:
            best_score = current_score
            best_schedule = current_schedule.copy()

    print("Optimization complete. Best score:", best_score)
    return best_schedule


