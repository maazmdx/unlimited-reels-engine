from engine.agents.hook_master import HookMasterAgent


def test_dad_clash_strips_card_data():
    hm = HookMasterAgent()
    topic = {
        "title": "Dad Discovers 80% Phone Battery Charging Alarm",
        "format_type": "dad_clash",
        "left_character": "dad",
        "right_character": "claude",
        "auto_dm_keyword": "ALARM",
        "scene_preset": "living_room",
    }
    screenplay = hm.craft_reel_screenplay(topic)

    assert screenplay.get("cardData") is None
    assert screenplay.get("proof_steps") == []
    assert screenplay.get("proofImagePath") is None
    assert screenplay.get("logoPath") is None
