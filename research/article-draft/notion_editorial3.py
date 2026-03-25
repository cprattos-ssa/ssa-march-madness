"""Apply 3 content edits, delete edit notes, remove highlights."""
import json
import os
import urllib.request
import urllib.error

API_KEY = os.environ["NOTION_API_KEY"]
PAGE_ID = "329e20b4c263807dba41c0d3d66b2cb2"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}


def get_block(block_id):
    url = f"https://api.notion.com/v1/blocks/{block_id}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def patch_block(block_id, rich_text, color="default"):
    url = f"https://api.notion.com/v1/blocks/{block_id}"
    body = json.dumps(
        {"paragraph": {"rich_text": rich_text, "color": color}}
    ).encode()
    req = urllib.request.Request(url, data=body, headers=headers, method="PATCH")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def delete_block(block_id):
    url = f"https://api.notion.com/v1/blocks/{block_id}"
    req = urllib.request.Request(url, headers=headers, method="DELETE")
    try:
        with urllib.request.urlopen(req) as resp:
            return True
    except urllib.error.HTTPError as e:
        print(f"  Warning: could not delete {block_id}: {e}")
        return False


def plain(text):
    return {
        "type": "text",
        "text": {"content": text},
        "annotations": {
            "bold": False, "italic": False, "strikethrough": False,
            "underline": False, "code": False, "color": "default",
        },
    }


# ============================================================
# EDIT 1: Trim feature list (Block 9)
# ============================================================
feature_text = (
    "The pipeline itself is fairly standard for this type of competition: "
    "I ingested 101 data files across four sources (Kaggle historical data, "
    "KenPom-equivalent efficiency metrics from Barttorvik, coaching records, "
    "and player-level stats), engineered 57 features per team-season covering "
    "efficiency metrics, Elo ratings, strength of schedule, and coaching "
    "experience, then trained five model architectures against each other. "
    "Logistic regression, a pure Elo-based Bradley-Terry model, XGBoost, "
    "LightGBM, and a neural network."
)
patch_block("0f0d2f35-1534-4072-b737-9aae028564b8", [plain(feature_text)])
print("1/3 Feature list: trimmed + highlight removed")

# Delete the EDIT note (Block 10)
delete_block("32de20b4-c263-812d-bcbf-edcdf9f55ea6")
print("     EDIT note deleted")

# ============================================================
# EDIT 2: Iowa paragraph trim (Block 30)
# ============================================================
iowa_text = (
    "Five games, all predicted at 89% or higher for the wrong team. "
    "Together they accounted for 47% of our total prediction error across "
    "48 games. The single worst miss: giving No. 1 seed Florida a 97.1% "
    "chance, only to watch Iowa end their season. That's the thing about "
    "Brier score - being confidently wrong is "
)
iowa_italic = "catastrophic"
iowa_end = " - and I was precisely that, repeatedly."

patch_block(
    "32de20b4-c263-80e1-9ddf-ce4162e44d24",
    [
        plain(iowa_text),
        {
            "type": "text",
            "text": {"content": iowa_italic},
            "annotations": {
                "bold": False, "italic": True, "strikethrough": False,
                "underline": False, "code": False, "color": "default",
            },
        },
        plain(iowa_end),
    ],
)
print("2/3 Iowa paragraph: trimmed + highlight removed")

# Delete the EDIT note (Block 31)
delete_block("32de20b4-c263-8191-a880-e065c3f7d950")
print("     EDIT note deleted")

# ============================================================
# EDIT 3: Duke paragraph condensed (Block 48)
# ============================================================
duke_text = (
    "When we adjusted Duke's 99.4% prediction for two injured players "
    "representing 26% of their roster's WAR, it dropped to 86.6% - and "
    "Duke ended up winning by just 6 after trailing by 13."
)
patch_block("32de20b4-c263-80d3-a45b-f55e9db750de", [plain(duke_text)])
print("3/3 Duke paragraph: condensed + highlight removed")

# Delete the EDIT note (Block 49)
delete_block("32de20b4-c263-81ec-99b0-dea72eabf65d")
print("     EDIT note deleted")

# ============================================================
# Also remove BYU table EDIT note (Block 40) since user is keeping it
# ============================================================
delete_block("32de20b4-c263-8151-b1c4-c0de90c91bab")
print("     BYU table EDIT note deleted (keeping the row)")

print()
print("All 3 edits applied, 4 EDIT notes deleted, all highlights removed.")
