import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

SEPARATOR = b"\x00"
PATH_SEPARATOR = "\x01"


def traverse(obj: dict[str, Any]) -> Iterable[tuple[str, str]]:
    for key, value in sorted(obj.items()):
        if isinstance(value, dict):
            for sub_path, sub_value in traverse(value):
                yield f"{key}\x01{sub_path}", sub_value
        else:
            yield key, value


def obj_hash(obj: dict[str, Any]) -> str:
    md5 = hashlib.md5()

    for key, value in traverse(obj):
        md5.update(key.encode("utf-8"))
        md5.update(SEPARATOR)
        md5.update(value.encode("utf-8"))
        md5.update(SEPARATOR)

    return md5.hexdigest()


def file_hash(path: Path) -> str:
    return obj_hash(json.loads(path.read_text(encoding="utf-8")))


class Manifest:
    CONTENT_TYPES = ("m_ability_details","m_ability_effect_types","m_abnormal_condition_types","m_accessories","m_allies","m_armors","m_attribute_tags","m_battle_result_reactions","m_buff_types","m_building_skill_effect_descriptions","m_building_skill_levels","m_building_skill_params","m_building_skill_restricts","m_buildings","m_campaigns","m_chapter_areas","m_chapter_quests","m_chapter_repeat_quests","m_chapters","m_character_abilities","m_character_action_skills","m_character_profiles","m_character_skins","m_characters","m_content_type_details","m_defend_stages","m_defensive_unit_effect_tags","m_defensive_units","m_degrees","m_description_text_colors","m_dictionary_enemies","m_dictionary_enemy_groups","m_dictionary_non_player_character_groups","m_dictionary_non_player_characters","m_dictionary_world_groups","m_dictionary_worlds","m_disaster_boss_messages","m_disaster_boss_restricts","m_disaster_bosses","m_disaster_level_restricts","m_disaster_quests","m_dungeons","m_enchantment_details","m_encounter_campaigns","m_encounter_quests","m_enemies","m_enemy_skills","m_event_currencies","m_event_miner_quest_restricts","m_event_miner_quests","m_event_story_stages","m_event_top_characters","m_events","m_exchange_categories","m_feature_lock_conditions","m_feature_locks","m_gacha_group_movies","m_gacha_groups","m_gachas","m_home_stage_characters","m_idle_exploration_log_messages","m_idle_exploration_map_areas","m_idle_exploration_maps","m_interaction_voices","m_item_obtains","m_items","m_jobs","m_level_synchros","m_limited_items","m_login_announcements","m_login_bonus_resources","m_mana_gem_auto_conditions","m_mana_gems","m_mileage_reward_details","m_mine_stages","m_mission_passes","m_mission_terms","m_missions","m_nether_battle_stages","m_nether_code_category_skills","m_nether_codes","m_nether_floor_event_parts","m_nether_floor_events","m_nether_floor_restricts","m_nether_spheres","m_nethers","m_novel_character_skins","m_novel_characters","m_novel_events","m_novel_homes","m_novel_main_chapters","m_novel_mains","m_novel_others","m_novel_prologues","m_override_buff_types","m_part_voices","m_payment_appstore_products","m_payment_dmm_products","m_payment_gachas","m_payment_googleplay_products","m_payment_lineups","m_payment_recommends","m_payment_sub_categories","m_payment_subscriptions","m_plan_restricts","m_plan_step_serifs","m_plan_steps","m_plans","m_preregist_taverns","m_preregist_x_messages","m_present_messages","m_present_titles","m_special_missions","m_stage_effects","m_supplied_items","m_tavern_building_info","m_tavern_cards","m_tavern_character_cards","m_tavern_dialogue","m_tavern_text_color","m_tavern_works","m_texts","m_transition_tips","m_union_request_stages","m_union_request_supplied_items","m_union_types","m_visitors","m_weapon_skins","m_weapons","names","ui_texts")
    STATIC_TYPE = "static"

    def __init__(self, translation_dir: str | Path, language: str = "zh_Hans"):
        self.base_dir = Path(translation_dir)
        self.language = language

    def _file(self, category: str) -> Path:
        return self.base_dir / category / f"{self.language}.json"

    def _static_file(self) -> Path:
        return self._file(self.STATIC_TYPE)

    def build(self):
        static_file = self._static_file()
        manifest: dict[str, Any] = {
            t: file_hash(f) for t in self.CONTENT_TYPES if (f := self._file(t)).exists()
        }

        if static_file.exists():
            manifest[self.STATIC_TYPE] = file_hash(static_file)

        manifest["novels"] = {
            f.parent.name: file_hash(f)
            for f in self.base_dir.glob(f"novels/*/{self.language}.json")
        }

        manifest["hash"] = obj_hash(manifest)
        return manifest

    def update(self):
        manifest = self.build()

        output = self.base_dir / "manifest" / f"{self.language}.json"
        output.parent.mkdir(parents=True, exist_ok=True)

        output.write_text(
            json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=4),
            encoding="utf-8",
        )


def main():
    for lang in ["zh_Hans", "zh_Hant"]:
        Manifest("translations", lang).update()


if __name__ == "__main__":
    main()
