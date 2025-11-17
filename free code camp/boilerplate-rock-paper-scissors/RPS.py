MOVES = ("R", "P", "S")
COUNTER_MOVE = {"R": "P", "P": "S", "S": "R"}
RESULT_SCORES = {
    ("R", "S"): 1,
    ("S", "P"): 1,
    ("P", "R"): 1,
    ("S", "R"): -1,
    ("P", "S"): -1,
    ("R", "P"): -1,
}
BOT_NAMES = ("quincy", "kris", "mrugesh", "abbey")


def _outcome_score(ours, theirs):
    if ours == theirs:
        return 0
    return RESULT_SCORES.get((ours, theirs), -RESULT_SCORES.get((theirs, ours), 0))


def _simulate_quincy(state_slice):
    choices = ("R", "R", "P", "P", "S")
    state_slice["counter"] = state_slice.get("counter", 0) + 1
    return choices[state_slice["counter"] % len(choices)]


def _simulate_kris(prev_play):
    if prev_play == "":
        prev_play = "R"
    return COUNTER_MOVE[prev_play]


def _simulate_mrugesh(state_slice, prev_play):
    opponent_history = state_slice.setdefault("opponent_history", [])
    opponent_history.append(prev_play)
    last_ten = opponent_history[-10:]

    if last_ten:
        most_frequent = max(set(last_ten), key=last_ten.count)
    else:
        most_frequent = ""

    if most_frequent == "":
        most_frequent = "S"

    return COUNTER_MOVE[most_frequent]


def _simulate_abbey(state_slice, prev_play):
    opponent_history = state_slice.setdefault("opponent_history", [])
    play_order = state_slice.setdefault(
        "play_order",
        {
            "RR": 0,
            "RP": 0,
            "RS": 0,
            "PR": 0,
            "PP": 0,
            "PS": 0,
            "SR": 0,
            "SP": 0,
            "SS": 0,
        },
    )

    if not prev_play:
        prev_play = "R"
    opponent_history.append(prev_play)

    last_two = "".join(opponent_history[-2:])
    if len(last_two) == 2:
        play_order[last_two] += 1

    potential_plays = [
        prev_play + "R",
        prev_play + "P",
        prev_play + "S",
    ]

    sub_order = {k: play_order[k] for k in potential_plays}
    prediction = max(sub_order, key=sub_order.get)[-1]

    return COUNTER_MOVE[prediction]


def _init_state_if_needed(state):
    if state.get("detection") is None:
        state["detection"] = {bot: {"matches": 0, "total": 0} for bot in BOT_NAMES}
        state["last_predictions"] = {}
        state["identified"] = None
        state["sim"] = {
            "quincy": {"counter": 0},
            "kris": {},
            "mrugesh": {"opponent_history": []},
            "abbey": {
                "opponent_history": [],
                "play_order": {
                    "RR": 0,
                    "RP": 0,
                    "RS": 0,
                    "PR": 0,
                    "PP": 0,
                    "PS": 0,
                    "SR": 0,
                    "SP": 0,
                    "SS": 0,
                },
            },
        }


def player(prev_play, opponent_history=[], player_history=[], state={"detection": None}):
    if prev_play == "" and (opponent_history or player_history):
        opponent_history.clear()
        player_history.clear()
        state.clear()

    _init_state_if_needed(state)

    detection = state["detection"]
    last_predictions = state.get("last_predictions", {})

    if prev_play:
        opponent_history.append(prev_play)
        for bot_name, predicted in last_predictions.items():
            stats = detection[bot_name]
            stats["total"] += 1
            if prev_play == predicted:
                stats["matches"] += 1

        accuracy_table = []
        best_bot = None
        best_accuracy = 0.0
        for bot_name, stats in detection.items():
            total = stats["total"]
            if total == 0:
                continue
            accuracy = stats["matches"] / total
            accuracy_table.append((accuracy, total, bot_name))
            if accuracy > best_accuracy:
                best_accuracy = accuracy
                best_bot = bot_name

        accuracy_table.sort(reverse=True)
        second_accuracy = accuracy_table[1][0] if len(accuracy_table) > 1 else 0.0

        if best_bot:
            best_total = detection[best_bot]["total"]
            if best_total >= 3 and best_accuracy >= 0.6:
                if best_bot == state.get("identified") or best_accuracy - second_accuracy >= 0.15 or best_total >= 6:
                    state["identified"] = best_bot

        current_id = state.get("identified")
        if current_id:
            id_stats = detection[current_id]
            id_accuracy = id_stats["matches"] / id_stats["total"] if id_stats["total"] else 0
            if id_stats["total"] >= 4 and id_accuracy < 0.52:
                state["identified"] = None

        elif best_accuracy < 0.5:
            state["identified"] = None

    prev_input = player_history[-1] if player_history else ""
    sim_state = state["sim"]

    predictions = {
        "quincy": _simulate_quincy(sim_state["quincy"]),
        "kris": _simulate_kris(prev_input),
        "mrugesh": _simulate_mrugesh(sim_state["mrugesh"], prev_input),
        "abbey": _simulate_abbey(sim_state["abbey"], prev_input),
    }

    state["last_predictions"] = dict(predictions)

    identified = state.get("identified")

    if identified:
        predicted_move = predictions.get(identified, "R")
        guess = COUNTER_MOVE.get(predicted_move, "P")
    else:
        best_guess = None
        best_score = float("-inf")

        accuracy_weights = {}
        for bot_name, stats in detection.items():
            total = stats["total"]
            if total == 0:
                accuracy_weights[bot_name] = 0.2
            else:
                accuracy = stats["matches"] / total
                accuracy_weights[bot_name] = accuracy ** 2 * max(1, total / 2)

        # If one bot is clearly ahead, lean on that prediction even before locking in.
        sorted_candidates = sorted(
            (
                (accuracy_weights.get(bot_name, 0), bot_name)
                for bot_name in BOT_NAMES
            ),
            reverse=True,
        )

        top_weight, top_bot = sorted_candidates[0]
        second_weight = sorted_candidates[1][0] if len(sorted_candidates) > 1 else 0.0

        if top_weight > 0 and (top_weight - second_weight) >= 0.5:
            predicted_move = predictions.get(top_bot, "R")
            guess = COUNTER_MOVE.get(predicted_move, "P")
        else:
            for candidate in MOVES:
                score = 0.0
                for bot_name, predicted in predictions.items():
                    weight = accuracy_weights.get(bot_name, 0.2)
                    score += weight * _outcome_score(candidate, predicted)
                if score > best_score:
                    best_score = score
                    best_guess = candidate
            guess = best_guess or "P"

    player_history.append(guess)
    return guess
