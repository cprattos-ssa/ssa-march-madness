"""Apply Takeaway update and Iowa edit note update."""
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


def patch_block(block_id, rich_text, color="default"):
    """Update a paragraph block's rich_text and color."""
    url = f"https://api.notion.com/v1/blocks/{block_id}"
    body = json.dumps(
        {"paragraph": {"rich_text": rich_text, "color": color}}
    ).encode()
    req = urllib.request.Request(url, data=body, headers=headers, method="PATCH")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def delete_block(block_id):
    """Delete a block."""
    url = f"https://api.notion.com/v1/blocks/{block_id}"
    req = urllib.request.Request(url, headers=headers, method="DELETE")
    try:
        with urllib.request.urlopen(req) as resp:
            return True
    except urllib.error.HTTPError:
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


def styled(text, bold=False, italic=False, color="default"):
    return {
        "type": "text",
        "text": {"content": text},
        "annotations": {
            "bold": bold, "italic": italic, "strikethrough": False,
            "underline": False, "code": False, "color": color,
        },
    }


# ============================================================
# 1. UPDATE TAKEAWAY: R32 stats, remove highlight, delete note
# ============================================================
# Block 55: 6f639671-deb5-4246-bcd7-788ce74b6c2e (Takeaway paragraph)
# Block 56: 32de20b4-c263-8134-b804-da5afcac6f22 (EDIT note to delete)

takeaway_text = (
    "I compressed a multi-week ML project into a couple of working sessions, "
    "trained five model architectures, tested a 30,000-record player data "
    "hypothesis, and submitted predictions for 132,000 tournament matchups. "
    "The model went 36 for 48 through two rounds, nailed four upset picks, "
    "and also gave Florida a 97% chance of beating a 9-seed that won on a "
    "three-pointer with 4.5 seconds left. It gave Wisconsin a 96% chance of "
    "beating a 12-seed that outperformed them in nearly every metric that "
    "mattered, and the game-winning basket came from Chase Johnston, a bench "
    "player who had not made a single two-point field goal all season. His "
    "first one ended Wisconsin's season with 11 seconds left."
)

patch_block(
    "6f639671-deb5-4246-bcd7-788ce74b6c2e",
    [plain(takeaway_text)],
    color="default",
)
print("1a. Takeaway updated with R32 stats + highlight removed")

delete_block("32de20b4-c263-8134-b804-da5afcac6f22")
print("1b. Takeaway EDIT note deleted")

# ============================================================
# 2. UPDATE IOWA EDIT NOTE: Show full replacement paragraph
# ============================================================
# Block 31: 32de20b4-c263-8191-a880-e065c3f7d950 (Iowa EDIT note)

replacement_para = (
    "Five games, all predicted at 89% or higher for the wrong team. "
    "Together they accounted for 47% of our total prediction error across "
    "48 games. The single worst miss: giving No. 1 seed Florida a 97.1% "
    "chance, only to watch Iowa end their season. That's the thing about "
    "Brier score - being confidently wrong is catastrophic - and I was "
    "precisely that, repeatedly."
)

patch_block(
    "32de20b4-c263-8191-a880-e065c3f7d950",
    [
        styled("EDIT - suggested replacement: ", bold=True, color="green"),
        styled(replacement_para, color="green"),
    ],
    color="default",
)
print("2. Iowa EDIT note updated with full replacement paragraph")

print()
print("Done. Takeaway is live, Iowa note updated.")
