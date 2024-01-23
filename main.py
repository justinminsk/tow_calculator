import panel as pn
import pandas as pd
import hvplot.pandas

models_widget = pn.widgets.IntInput(name="Models", value=1, start=1, end=100)
attacks_widget = pn.widgets.IntInput(name="Attacks", value=1, start=1, end=20)
weapon_skill_widget = pn.widgets.IntInput(name="Weapon Skill", value=1, start=1, end=10)
strength_widget = pn.widgets.IntInput(name="Strength", value=1, start=1, end=10)
target_toughness_widget = pn.widgets.IntInput(
    name="Target Toughness", value=1, start=1, end=10
)
target_weapon_skill_widget = pn.widgets.IntInput(
    name="Target Weapon Skill", value=1, start=1, end=10
)
target_selector_widget = pn.widgets.Select(
    name="Target",
    options=["Target Toughness", "Target Weapon Skill"],
    value="Target Toughness",
)


def calc_to_hit(weapon_skill: int):
    result_dict = {}
    for opp_weapon_skill in range(1, 11):
        to_hit = 5
        weapon_skill_comp = weapon_skill / opp_weapon_skill
        if weapon_skill_comp > 2:
            to_hit = 2
        if weapon_skill_comp >= 0.5 and weapon_skill_comp <= 2:
            to_hit = 3
        if weapon_skill_comp < 0.5:
            to_hit = 4
        result_dict[opp_weapon_skill] = to_hit
    return result_dict


def calc_to_wound(strength: int):
    wound_look_up_dict = {
        1: {1: 4, 2: 5, 3: 6, 4: 6, 5: 6, 6: 6, 7: 0, 8: 0, 9: 0, 10: 0},
        2: {1: 3, 2: 4, 3: 5, 4: 6, 5: 6, 6: 6, 7: 6, 8: 0, 9: 0, 10: 0},
        3: {1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 6, 7: 6, 8: 6, 9: 0, 10: 0},
        4: {1: 2, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 6, 8: 6, 9: 6, 10: 0},
        5: {1: 2, 2: 2, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6, 8: 6, 9: 6, 10: 6},
        6: {1: 2, 2: 2, 3: 2, 4: 2, 5: 3, 6: 4, 7: 5, 8: 6, 9: 6, 10: 6},
        7: {1: 2, 2: 2, 3: 2, 4: 2, 5: 2, 6: 3, 7: 4, 8: 5, 9: 6, 10: 6},
        8: {1: 2, 2: 2, 3: 2, 4: 2, 5: 2, 6: 2, 7: 3, 8: 4, 9: 5, 10: 6},
        9: {1: 2, 2: 2, 3: 2, 4: 2, 5: 2, 6: 2, 7: 2, 8: 3, 9: 4, 10: 5},
        10: {1: 2, 2: 2, 3: 2, 4: 2, 5: 2, 6: 2, 7: 2, 8: 2, 9: 3, 10: 4},
    }
    result_dict = wound_look_up_dict[strength]
    return result_dict

# TODO: add reroll 1/failed hit and wounds
# TODO: add multi wound
def calc_damage(models: int, attacks: int, to_hit: int, to_wound: int, poison = False):
    if to_wound == 0:
        return 0
    # TODO: add options based on ToW skills ie reroll to wound
    number_of_attacks = models * attacks
    number_hit = 0
    number_wound = 0
    if poison == True:
        sixes = number_of_attacks / 6
        number_hit = (number_of_attacks - sixes) * ((6 - to_hit + 1) / 6)
        number_wound = number_hit * ((6 - to_wound + 1) / 6) + sixes
    else:
        number_hit = number_of_attacks * ((6 - to_hit + 1) / 6)
        number_wound = number_hit * ((6 - to_wound + 1) / 6)
    return number_wound

# TODO: add saves later
def result_table_creation(weapon_skill: int, strength: int, models: int, attacks: int):
    if weapon_skill and strength and models and attacks:
        hit_dict = calc_to_hit(weapon_skill)
        wound_dict = calc_to_wound(strength)

        result_dict_list = []
        for op_ws in hit_dict:
            for t in wound_dict:
                damage = calc_damage(models, attacks, hit_dict[op_ws], wound_dict[t])
                result_dict_list.append(
                    {"toughness": t, "opponents weapon skill": op_ws, "damage": damage}
                )
        return pd.DataFrame.from_records(result_dict_list).sort_values(
            by=["toughness", "opponents weapon skill"]
        )
    else:
        return pd.Dataframe()


@pn.depends(
    weapon_skill_widget,
    strength_widget,
    models_widget,
    attacks_widget,
    target_toughness_widget,
    target_weapon_skill_widget,
    target_selector_widget,
)
def make_table(
    weapon_skill: int,
    strength: int,
    models: int,
    attacks: int,
    target_toughness: int,
    target_weapon_skill: int,
    target_select: str,
):
    selector_dict = {
        "Target Toughness": "toughness",
        "Target Weapon Skill": "opponents weapon skill",
    }

    result_table = result_table_creation(weapon_skill, strength, models, attacks)
    if target_select == "Target Toughness":
        result_table = result_table[
            result_table[selector_dict[target_select]] == target_toughness
        ]
    if target_select == "Target Weapon Skill":
        result_table = result_table[
            result_table[selector_dict[target_select]] == target_weapon_skill
        ]
    return pn.widgets.DataFrame(result_table)


@pn.depends(
    weapon_skill_widget,
    strength_widget,
    models_widget,
    attacks_widget,
    target_toughness_widget,
    target_weapon_skill_widget,
    target_selector_widget,
)
def plot_results_line(
    weapon_skill: int,
    strength: int,
    models: int,
    attacks: int,
    target_toughness: int,
    target_weapon_skill: int,
    target_select: str,
):
    selector_dict = {
        "Target Toughness": "toughness",
        "Target Weapon Skill": "opponents weapon skill",
    }

    result_table = result_table_creation(weapon_skill, strength, models, attacks)
    if target_select == "Target Toughness":
        result_table = result_table[
            result_table[selector_dict[target_select]] == target_toughness
        ]
        graph_x = "opponents weapon skill"
    if target_select == "Target Weapon Skill":
        result_table = result_table[
            result_table[selector_dict[target_select]] == target_weapon_skill
        ]
        graph_x = "toughness"

    return result_table.hvplot.line(x=graph_x, y="damage")


template = pn.template.MaterialTemplate(
    title="ToW Calculator",
)
template.main.append(
    pn.Column(
        pn.Row(
            pn.Column(models_widget, attacks_widget),
            pn.Column(weapon_skill_widget, strength_widget),
            pn.Column(target_toughness_widget, target_weapon_skill_widget),
            target_selector_widget,
        ),
        pn.Row(make_table, plot_results_line),
    )
)

template.servable(target="panel")
