import string


class BaseGA:
    alphabet = list(string.ascii_uppercase)

    population_size = 100
    generation_count = 1000

    mutation_probability = 0.65

    crossover_k_count = 20
    crossover_probability = 0.65

    tournament_win_prob = 0.75
    tournament_size = 10

    unchanged_threshold = 50
