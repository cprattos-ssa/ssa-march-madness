"""Apply editorial annotations to the Notion article page."""
import json
import os
import urllib.request

API_KEY = os.environ["NOTION_API_KEY"]
PAGE_ID = "329e20b4c263807dba41c0d3d66b2cb2"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}


def patch_block_color(block_id, color):
    """Set paragraph background color. Must include existing rich_text."""
    # First fetch the block's current rich_text
    url = f"https://api.notion.com/v1/blocks/{block_id}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        block = json.loads(resp.read())
    existing_rt = block["paragraph"]["rich_text"]
    # Now patch with existing rich_text + new color
    body = json.dumps(
        {"paragraph": {"rich_text": existing_rt, "color": color}}
    ).encode()
    req2 = urllib.request.Request(url, data=body, headers=headers, method="PATCH")
    with urllib.request.urlopen(req2) as resp2:
        return json.loads(resp2.read())


def insert_after(after_block_id, rich_text_segments):
    """Insert a new paragraph block after the specified block."""
    url = f"https://api.notion.com/v1/blocks/{PAGE_ID}/children"
    body = json.dumps(
        {
            "after": after_block_id,
            "children": [
                {
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": rich_text_segments,
                        "color": "default",
                    },
                }
            ],
        }
    ).encode()
    req = urllib.request.Request(url, data=body, headers=headers, method="PATCH")
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
    return result["results"][0]["id"]


def edit_note(label, text, color="green"):
    """Create rich_text segments for an editorial note."""
    return [
        {
            "type": "text",
            "text": {"content": f"{label}: "},
            "annotations": {
                "bold": True,
                "italic": False,
                "strikethrough": False,
                "underline": False,
                "code": False,
                "color": color,
            },
        },
        {
            "type": "text",
            "text": {"content": text},
            "annotations": {
                "bold": False,
                "italic": False,
                "strikethrough": False,
                "underline": False,
                "code": False,
                "color": color,
            },
        },
    ]


# ============================================================
# EDIT 1: Part 1 feature list is too dense (Block 9)
# ============================================================
patch_block_color("0f0d2f35-1534-4072-b737-9aae028564b8", "yellow_background")
insert_after(
    "0f0d2f35-1534-4072-b737-9aae028564b8",
    edit_note(
        "EDIT - trim feature list",
        'The 6-item feature list is dense for LinkedIn. Consider: "...engineered '
        "57 features per team-season covering efficiency metrics, Elo ratings, "
        "strength of schedule, and coaching experience, then trained five model "
        'architectures..." Same info, half the words. Keep the model list at the end.',
    ),
)
print("1/8 Part 1 feature list: highlighted + note")

# ============================================================
# EDIT 2: Part 2 match rate is unnecessary (Block 17)
# ============================================================
patch_block_color("eec01f19-5a4d-43bf-b5dc-8e66025ce6a4", "yellow_background")
insert_after(
    "eec01f19-5a4d-43bf-b5dc-8e66025ce6a4",
    edit_note(
        "EDIT - cut match rate",
        'Remove "I matched 99.3% of players to Kaggle team IDs and" - technical '
        "validation detail that reads like a peer review, not a LinkedIn article. "
        'Becomes: "...star dependency. I reran 30 model configurations across '
        'XGBoost, LightGBM, and the neural network."',
    ),
)
print("2/8 Part 2 match rate: highlighted + note")

# ============================================================
# EDIT 3: Part 3 Iowa detail repeated (Block 29)
# ============================================================
patch_block_color("32de20b4-c263-80e1-9ddf-ce4162e44d24", "yellow_background")
insert_after(
    "32de20b4-c263-80e1-9ddf-ce4162e44d24",
    edit_note(
        "EDIT - trim Iowa repetition",
        'The "three-pointer with 4.5 seconds left" detail is already in the table '
        "above and will appear again in the clipping paragraph. Consider: "
        '"The single worst miss: giving No. 1 seed Florida a 97.1% chance, only to '
        "watch Iowa end their season. That's the thing about Brier score - being "
        'confidently wrong is catastrophic - and I was precisely that, repeatedly."',
    ),
)
print("3/8 Part 3 Iowa repetition: highlighted + note")

# ============================================================
# EDIT 4: Part 4 table - BYU row is redundant (after table Block 37)
# ============================================================
insert_after(
    "32de20b4-c263-80dc-b592-e00486a68674",
    edit_note(
        "EDIT - consider removing BYU row from table",
        'The BYU row ("coach with 22 tourney wins") repeats what the Texas '
        "paragraph above already says. Texas appears in 2 of 5 table rows, which "
        "dilutes the other examples. One Texas row (Gonzaga) is enough since the "
        "paragraph already tells the full Texas Cinderella story.",
        "orange",
    ),
)
print("4/8 Part 4 table BYU row: note inserted")

# ============================================================
# EDIT 5: Part 4 clipping paragraph breaks the irony (Block 39)
# ============================================================
patch_block_color("ac625fae-19f9-45a8-9c47-9789b1263c99", "red_background")
insert_after(
    "ac625fae-19f9-45a8-9c47-9789b1263c99",
    edit_note(
        "EDIT - move, condense, or remove",
        "This paragraph breaks the irony climax. Three options: "
        "(A) REMOVE entirely - the irony paragraph is the real closer for Part 4. "
        "(B) CONDENSE to one sentence appended to the irony paragraph above: "
        '"It also didn\'t help that we skipped probability clipping, a standard '
        "Kaggle technique that caps predictions at 2.5%-97.5% so no single miss is "
        "catastrophic - or that Vegas was more calibrated than we were in all 12 "
        'wrong picks." '
        "(C) MOVE to end of Part 3, after 'I was precisely that, repeatedly,' "
        "where it flows naturally from the scorecard.",
        "red",
    ),
)
print("5/8 Part 4 clipping paragraph: red highlight + note")

# ============================================================
# EDIT 6: Part 5 Duke example is longest but least impactful (Block 46)
# ============================================================
patch_block_color("32de20b4-c263-80d3-a45b-f55e9db750de", "yellow_background")
insert_after(
    "32de20b4-c263-80d3-a45b-f55e9db750de",
    edit_note(
        "EDIT - trim Duke (we got this game right)",
        "Duke is 4 sentences about a game we predicted correctly. Gonzaga/BYU "
        "(next paragraph) are the impactful ones because those injuries caused "
        "wrong picks. Consider condensing to 1 sentence: "
        '"When we adjusted Duke\'s 99.4% prediction for two injured players '
        "representing 26% of their roster's WAR, it dropped to 86.6% - and Duke "
        'ended up winning by just 6 after trailing by 13."',
    ),
)
print("6/8 Part 5 Duke example: highlighted + note")

# ============================================================
# EDIT 7: Takeaway is still Day 1 only (Block 52)
# ============================================================
patch_block_color("6f639671-deb5-4246-bcd7-788ce74b6c2e", "yellow_background")
insert_after(
    "6f639671-deb5-4246-bcd7-788ce74b6c2e",
    edit_note(
        "EDIT - update to R32 stats",
        'Still shows Day 1 numbers. Update to: "The model went 36 for 48 through '
        "two rounds, nailed four upset picks, and also gave Florida a 97% chance of "
        "beating a 9-seed that won on a last-second three. It gave Wisconsin a 96% "
        'chance of beating a 12-seed..." '
        "Also: the first sentence re-summarizes Parts 1-2. Per the style guide "
        '("Trust the reader"), consider trimming it.',
    ),
)
print("7/8 Takeaway stats: highlighted + note")

# ============================================================
# EDIT 8: Part 2 goto_conversion wording (Block 22)
# ============================================================
patch_block_color("677b1e8e-dc64-4c33-a084-92733425e207", "yellow_background")
insert_after(
    "677b1e8e-dc64-4c33-a084-92733425e207",
    edit_note(
        "EDIT - minor",
        'Change "a few lines of math" to "a handful of lines of math" (the core '
        'function is ~15-20 lines, not "a few").',
        "blue",
    ),
)
print("8/8 Part 2 goto_conversion wording: highlighted + note")

print()
print("All 8 editorial annotations applied to Notion page.")
