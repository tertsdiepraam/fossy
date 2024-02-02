import xml.etree.ElementTree as ET
import json
import glob
import datetime

tree = ET.parse('fosdem.xml')
root = tree.getroot()

# Just get stuff in a slightly nicer format
def transform(elem):
    obj = {}
    obj |= {str(k): str(v) for k,v in elem.attrib.items()}

    children = {}
    for child in elem:
        tag = child.tag
        children.setdefault(tag, [])
        children[tag].append(transform(child))
    
    obj |= children
    
    if elem.text:
        obj["text"] = elem.text
    return obj

def event(e):
    start = datetime.datetime.fromisoformat(e["date"][0]["text"])
    
    if start.date() == datetime.date(year=2024, month=2, day=3):
        day = 1
    else:
        day = 2
    h, m = e["duration"][0]["text"].split(":")
    end = start + datetime.timedelta(hours=int(h), minutes=int(m))
    return {
        "id": e["id"],
        "day": day,
        "title": e["title"][0]["text"],
        "date": e["date"][0]["text"],
        "start": start.strftime("%H:%M"),
        "end": end.strftime("%H:%M"),
        "duration": e["duration"][0]["text"],
        "url": e["url"][0]["text"],
    }

def room(r):
    events = [event(e) for e in r.get("event", [])]
    return {
        "name": r["name"],
        "events": events,
    }

def day(d):
    rooms = [room(r) for r in d["room"]]
    return {
        "date": d["date"],
        "start": d["start"],
        "end": d["end"],
        "rooms": rooms,
    }

schedule = transform(root)

# print(schedule["day"][0]["room"][0]["event"][0])
with open("fosdem.json", "w") as f:
    json.dump([day(d) for d in schedule["day"]], f, indent=4)

selection = {}
for filename in glob.glob("*.ics"):
    name = filename.removesuffix(".ics")
    events = []
    with open(filename) as f:
        for line in f:
            if line.startswith("UID"):
                events.append(line.split(":")[1].split("@")[0])
    
    selection[name] = events

with open("selection.json", "w") as f:
    json.dump(selection, f, indent=4)
