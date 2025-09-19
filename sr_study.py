import json, os, random
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import List, Dict, Optional

DATA_FILE = "cards.json"
DATE_FMT = "%Y-%m-%d"

@dataclass
class Card:
    id: int
    front: str
    back: str
    tags: List[str]
    ef: float = 2.5
    interval: int = 0
    reps: int = 0
    due: str = datetime.today().strftime(DATE_FMT)
    last_review: Optional[str] = None

def load_cards() -> List[Card]:
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return [Card(**c) for c in raw]

def save_cards(cards: List[Card]) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump([asdict(c) for c in cards], f, ensure_ascii=False, indent=2)

def today_str() -> str:
    return datetime.today().strftime(DATE_FMT)

def parse_date(s: str) -> datetime:
    return datetime.strptime(s, DATE_FMT)

def next_id(cards: List[Card]) -> int:
    return 1 + max([c.id for c in cards], default=0)

def add_card(front: str, back: str, tags: List[str]):
    cards = load_cards()
    c = Card(id=next_id(cards), front=front.strip(), back=back.strip(), tags=[t.strip() for t in tags if t.strip()])
    cards.append(c)
    save_cards(cards)
    print(f"Added card #{c.id} with tags {c.tags}")

def list_cards(tag: Optional[str] = None):
    cards = load_cards()
    if tag:
        cards = [c for c in cards if tag in c.tags]
    if not cards:
        print("No cards found.")
        return
    for c in cards:
        print(f"#{c.id} [{', '.join(c.tags)}] due {c.due} | {c.front} -> {c.back}")

def apply_sm2(card: Card, quality: int):
    if quality < 3:
        card.reps = 0
        card.interval = 1
    else:
        card.reps += 1
        if card.reps == 1:
            card.interval = 1
        elif card.reps == 2:
            card.interval = 6
        else:
            card.interval = int(round(card.interval * card.ef))
        card.ef = card.ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        if card.ef < 1.3:
            card.ef = 1.3
    next_due = parse_date(today_str()) + timedelta(days=card.interval)
    card.due = next_due.strftime(DATE_FMT)

def review_loop():
    cards = load_cards()
    due = [c for c in cards if c.due <= today_str()]
    if not due:
        print("Nothing due today.")
        return
    random.shuffle(due)
    for c in due:
        input(f"Q: {c.front}\nPress Enter to see answer")
        print(f"A: {c.back}")
        grade = int(input("Grade 0-5: "))
        apply_sm2(c, grade)
        c.last_review = today_str()
    save_cards(cards)

def stats():
    cards = load_cards()
    if not cards:
        print("No cards.")
        return
    due = sum(1 for c in cards if c.due <= today_str())
    print(f"Total: {len(cards)} | Due: {due}")

def delete_card(card_id: int):
    cards = load_cards()
    new_cards = [c for c in cards if c.id != card_id]
    if len(new_cards) == len(cards):
        print(f"No card found with ID {card_id}")
    else:
        save_cards(new_cards)
        print(f"Deleted card #{card_id}")

def help_menu():
    print("Commands:\n"
          "  add\n"
          "  list [tag]\n"
          "  review\n"
          "  stats\n"
          "  delete <id>\n"
          "  help\n"
          "  exit")

def main():
    print("Study Planner CLI")
    help_menu()
    while True:
        cmd = input("> ").strip().split()
        if not cmd: continue
        if cmd[0] == "add":
            front = input("Front: ")
            back = input("Back: ")
            tags = input("Tags (comma sep): ").split(",")
            add_card(front, back, tags)
        elif cmd[0] == "list":
            list_cards(cmd[1] if len(cmd) > 1 else None)
        elif cmd[0] == "review":
            review_loop()
        elif cmd[0] == "stats":
            stats()
        elif cmd[0] == "delete":
            if len(cmd) < 2 or not cmd[1].isdigit():
                print("Usage: delete <id>")
            else:
                delete_card(int(cmd[1]))
        elif cmd[0] == "help":
            help_menu()
        elif cmd[0] == "exit":
            break
        else:
            print("Unknown command")

if __name__ == "__main__":
    main()
