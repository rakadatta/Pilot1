import json
import os
import random
from typing import List, final

import otree
import yaml
from otree.api import *

doc = """
TODO: add description here
this is a survey
"""

os.environ["OTREE_PRODUCTION"] = "1"

def parse_yaml(filename: str):
    """
    parse the data yaml file, YAML is choosen because easy to operate for small data samples
    """
    assert os.path.exists(filename)
    with open(filename, "r") as file:
        data = yaml.safe_load(file)
    return data["Experiments"]


class C(BaseConstants):
    NAME_IN_URL = "Experimental_workshop_pilot"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    loss = models.IntegerField(initial=15)
    loss_probability = models.IntegerField(initial=10)
    initial_earning = models.IntegerField(initial=20)
    pass


class Player(BasePlayer):
    age = models.IntegerField(label="Please enter your age?", min=13, max=125)
    gpa = models.FloatField(label="Please enter your current GPA?", min=0, max=4)
    family_income = models.CurrencyField(
        label="Please enter your gross family income (monthly/annual)"
    )
    birth_order = models.IntegerField(
        label=f"What is your birth order? \t (If your parents have 6 children and you have two elder siblings and three younger siblings, you were the 'third' kid your parents had and your birth order is 3)",
        min=1,
        max=15,
    )

    etnicity = models.StringField(
        label="Which ethnicity best describes you?",
        widget=widgets.RadioSelect,
        choices=[
            "American",
            "African American",
            "African",
            "Asian",
            "Hispanic",
            "Latin American",
            "Others",
        ],
    )

    prev_reward = models.CurrencyField(initial=0, doc="value accumulated so far")
    num_messages = models.IntegerField(initial=0)
    game_finished = models.BooleanField()
    premium = models.CurrencyField(initial="0")


class SurveyModel(ExtraModel):
    player = models.Link(Player)
    experiment_name = models.StringField()
    reward = models.FloatField()
    option_choosen = models.StringField()


class SurveyModel2(ExtraModel):
    player = models.Link(Player)
    experiment_name = models.StringField()
    reward = models.FloatField()
    option_choosen = models.StringField()


# PAGES
class Introduction(Page):
    pass


class Introduction2(Page):
    pass


def pick_with_a_probabilty(probabilities: List, rewards: List):
    """
    given a list of probabilities pick the rewards
    @Return: selected reward
    """
    # Ensure probabilities sum up to 1
    assert sum(probabilities) == 1.0, "Probabilities should sum up to 1"
    chosen_value = random.choices(rewards, weights=probabilities, k=1)[0]
    return chosen_value


# TODO: maybe move to initial one
dat_filename = os.path.dirname(__file__) + "/data/survey1.yaml"
dat2_filename = os.path.dirname(__file__) + "/data/survey2.yaml"
experiments_data = parse_yaml(dat_filename)
experiments_data2 = parse_yaml(dat2_filename)
max_num_messages = len(experiments_data)
max_num_messages2 = len(experiments_data)
all_experimanent_names = [exp for exp in experiments_data]
all_experimanent_names2 = [exp for exp in experiments_data2]
# to eandomize the Experiments
random.shuffle(all_experimanent_names)
random.shuffle(all_experimanent_names2)


def reward_gained(experiment_id, key):
    exp_data = experiments_data[experiment_id]
    if key == "left":
        probs = "left_probs"
        rewards = "left_rewards"
        return pick_with_a_probabilty(exp_data[probs], exp_data[rewards])
    if key == "right":
        probs = "right_probs"
        rewards = "right_rewards"
        return pick_with_a_probabilty(exp_data[probs], exp_data[rewards])


def reward_gained2(experiment_id, key):
    exp_data = experiments_data2[experiment_id]
    if key == "yes":
        return exp_data["final_earning"]
    else:
        return pick_with_a_probabilty([0.9, 0.1], [exp_data["initial_earning"], 5])


def get_next_experiment(signle_exp_data):
    data_left = []
    data_right = []
    for i in zip(signle_exp_data["left_rewards"], signle_exp_data["left_probs"]):
        data_left.append({"name": "$" + str(i[0]), "y": i[1]})

    for i in zip(signle_exp_data["right_rewards"], signle_exp_data["right_probs"]):
        data_right.append({"name": "$" + str(i[0]), "y": i[1]})


    return dict(
        pieleft=json.dumps(data_left),
        pieright=json.dumps(data_right),
    )


def get_next_experiment2(signle_exp_data):
    return dict(
        premium=signle_exp_data["premium"],
        final_earning=signle_exp_data["final_earning"],
    )


class Survey(Page):
    @staticmethod
    def live_method(player, data):
        # we send empty at the beginning
        if data == "load":
            curr_experiment_data = get_next_experiment(experiments_data[all_experimanent_names[0]])
            # we send empty at the beginning
            return {
                player.id_in_group: {
                    "is_done": "not_game_finished",
                    "exp_data": curr_experiment_data,
                    "prev_reward": 0,
                    "option_selected": data,
                }
            }

        # the data recieved is either left button or right button
        player.num_messages += 1

        #  result_probabilty = models.FloatField()
        #  option_choosen = models.StringField()
        try:
            player.prev_reward = reward_gained(
                all_experimanent_names[player.num_messages - 1], key=data
            )
            # data logging
            SurveyModel.create(
                player=player,
                experiment_name=all_experimanent_names[player.num_messages - 1],
                reward=player.prev_reward,
                option_choosen=data,
            )

        except:
            pass

        if player.num_messages >= max_num_messages:
            return {
                player.id_in_group: {
                    "is_done": "game_finished",
                    "prev_reward": player.prev_reward,
                    "option_selected": data,
                }
            }
        else:
            player.game_finished = False
            curr_experiment_data = get_next_experiment(
                experiments_data[all_experimanent_names[player.num_messages]]
            )
            return {
                player.id_in_group: {
                    "is_done": "not_game_finished",
                    "exp_data": curr_experiment_data,
                    "prev_reward": player.prev_reward,
                    "option_selected": data,
                }
            }


class Survey2(Page):
    @staticmethod
    def live_method(player, data):
        if data == "load":
            player.num_messages = 0
            curr_experiment_data = get_next_experiment2(
                experiments_data2[all_experimanent_names2[0]]
            )
            # we send empty at the beginning
            return {
                0: {
                    "is_done": "not_game_finished",
                    "exp_data": curr_experiment_data,
                    "reward": 0,
                    "option_selected": data,
                }
            }

        # the data recieved is either left button or right button
        player.num_messages += 1

        #  result_probabilty = models.FloatField()
        #  option_choosen = models.StringField()
        reward_gained = 0
        try:
            reward_gained = reward_gained2(
                all_experimanent_names2[player.num_messages - 1], key=data
            )
            # data logging
            SurveyModel2.create(
                player=player,
                experiment_name=all_experimanent_names2[player.num_messages - 1],
                reward=reward_gained,
                option_choosen=data,
            )

        except:
            pass

        if player.num_messages >= max_num_messages:
            return {
                0: {
                    "is_done": "game_finished",
                    "reward": reward_gained,
                    "option_selected": data,
                }
            }
        else:
            player.game_finished = False
            curr_experiment_data = get_next_experiment2(
                experiments_data2[all_experimanent_names2[player.num_messages]]
            )
            return {
                0: {
                    "is_done": "not_game_finished",
                    "exp_data": curr_experiment_data,
                    "reward": reward_gained,
                    "option_selected": data,
                }
            }


def custom_export(players):
    yield ["session.code", "participant_code", "id_in_session"]
    survye1 = SurveyModel.filter()
    survye2 = SurveyModel2.filter()

    for survey in survye1:
        player = survey.player
        participant = player.participant
        yield [
            participant.code,
            participant.id_in_session,
            survey.experiment_name,
            survey.option_choosen,
            survey.reward,
        ]

    for survey in survye2:
        player = survey.player
        participant = player.participant
        yield [
            participant.code,
            participant.id_in_session,
            survey.experiment_name,
            survey.option_choosen,
            survey.reward,
        ]


class Questions(Page):
    form_model = "player"
    form_fields = ["age", "gpa", "family_income", "etnicity", "birth_order"]
    pass


class thanks(Page):
    pass


page_sequence = [Introduction, Survey, Introduction2, Survey2, Questions, thanks]
# page_sequence = [ Survey2, Questions, thanks]
