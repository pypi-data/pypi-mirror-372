def gae_advantages(
    values: list[float],
    rewards: list[float],
    gae_lambda: float,
    gae_gamma: float,
) -> list[float]:
    response_length = len(values)

    lastgaelam = 0.0
    advantages_reversed: list[float] = []
    for t in reversed(range(response_length)):
        nextvalues = values[t + 1] if t < response_length - 1 else 0.0
        delta = rewards[t] + gae_gamma * nextvalues - values[t]
        lastgaelam = delta + gae_gamma * gae_lambda * lastgaelam
        advantages_reversed.append(lastgaelam)

    return advantages_reversed[::-1]


def discounted_cumulative_rewards(
    rewards: list[float],
    gamma: float,
) -> list[float]:
    n = len(rewards)
    returns = [0.0] * n
    returns[-1] = rewards[-1]
    for t in reversed(range(n - 1)):
        returns[t] = rewards[t] + gamma * returns[t + 1]

    return returns


def gae_td_returns(
    advantages: list[float],
    values: list[float],
) -> list[float]:
    returns = [a + b for a, b in zip(advantages, values)]
    return returns
