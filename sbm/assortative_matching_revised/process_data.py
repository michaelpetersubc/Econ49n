import datetime
import json
# to install mysql: pip install mysql-connector-python
import mysql.connector as sql
import os

from collections import defaultdict
from dotenv import load_dotenv
load_dotenv()
# to install dotenv: run pip install python-dotenv in your terminal
# to use dotenv: https://github.com/theskumar/python-dotenv

DEBUG = True

# STEP 1: hook up to the database and retrieve the placement outcomes
db_connection = sql.connect(host='127.0.0.1', port = 3306, database=os.getenv("DB"), user=os.getenv("USER"), password=os.getenv("PASS"))
db_cursor = db_connection.cursor(dictionary=True)
db_cursor.execute('select * from to_data t join from_data f on t.aid=f.aid where to_oid != 893')
placement_outcomes = db_cursor.fetchall()

# STEP 2: delete all post-doc positions (postype 6)
# these are usually awarded alongside longer-term positions and are thus duplicate
no_postdoc = []
for entry in placement_outcomes:
    if entry["postype"] != 6:
        no_postdoc.append(entry)

# STEP 3: group all placements by applicant ID
applicants = defaultdict(list)
for entry in no_postdoc:
    applicants[str(int(entry["aid"]))].append(entry)

# STEP 4: retrieve only the first placement outcome of each individual
applicant_outcomes = {}
for applicant_id in applicants:
    for outcome in applicants[applicant_id]:
        if applicant_id not in applicant_outcomes:
            applicant_outcomes[applicant_id] = outcome
        else:
            if outcome["startdate"] < applicant_outcomes[applicant_id]["startdate"]:
                # take the earliest outcome
                applicant_outcomes[applicant_id] = outcome
            elif outcome["startdate"] == applicant_outcomes[applicant_id]["startdate"]:
                # sometimes we may have multiple outcomes that started on the same date - follow priority listing:
                if applicant_outcomes[applicant_id]["position_name"] in ["Assistant Professor"]:
                    applicant_outcomes[applicant_id] = outcome
                elif applicant_outcomes[applicant_id]["position_name"] in ["Lecturer", "Consultant"] and outcome["position_name"] not in ["Assistant Professor"]:
                    applicant_outcomes[applicant_id] = outcome  
                elif applicant_outcomes[applicant_id]["position_name"] in ["Other Academic", "Other Non-Academic"] and outcome["position_name"] not in ["Assistant Professor", "Lecturer", "Consultant"]:
                    applicant_outcomes[applicant_id] = outcome

# STEP 5: filter so this is only assistant professors and sink types
for key in list(applicant_outcomes.keys()):
    outcome = applicant_outcomes[key]
    if outcome["position_name"] not in ["Assistant Professor", "Lecturer", "Consultant", "Other Academic", "Other Non-Academic"]:
        del applicant_outcomes[key]

# STEP 6: seek names and attach to applicant IDs
names_clear = defaultdict(list)
with open("names.json") as f:
    # this is a json file mapping applicant IDs to stringed names
    list_of_names = json.load(f)
    for applicant_id in list_of_names:
        if applicant_id in applicant_outcomes:
            name = " ".join(list_of_names[applicant_id].lower().lstrip().rstrip().split())
            if "test" not in name or applicant_id in os.getenv("EXCEPTIONS").split(): 
                # EXCEPTIONS is a space-separated list of applicant_ids on a single line with test in their name that are not test accounts
                names_clear[name].append(applicant_id)

# STEP 7: eliminate duplicates by cross-indexing with university and date
# if two individuals came from different universities, they are assumed to be different people ("career reset")
# otherwise:
#   if two individuals came from the same university, they are assumed to be the same person (exceptions are assumed rare)
while True:
    must_loop_again = False
    for name in names_clear:
        if len(names_clear[name]) > 1:
            move_on = False
            for i in range(len(names_clear[name])):
                comparator = names_clear[name][i]
                object_r = applicant_outcomes[comparator]
                from_university_r = object_r["from_institution_name"]
                for reference in names_clear[name][i+1:]:
                    object = applicant_outcomes[reference]
                    from_university = object["from_institution_name"]
                    if from_university == from_university_r:
                        # the to_university of the two individuals is the same
                        # take the earliest position
                        must_loop_again = True
                        if object["startdate"] < object_r["startdate"]:
                            names_clear[name].remove(comparator)
                            del applicant_outcomes[comparator]
                        else:
                            names_clear[name].remove(reference)
                            del applicant_outcomes[reference]
                        move_on = True
                        break
                    # otherwise they are different and dont touch them
                if move_on:
                    break

    if not must_loop_again:
        break

# STEP 8: use the list of notes to get rid of bad data
db_cursor.execute('select * from applicant_results')
notes = db_cursor.fetchall()
note_lookup = defaultdict(list)
for note in notes:
    if note["notes"] and "import from data collected by" not in note["notes"]:
        note_lookup[(str(note["aid"]), note["postype"], note["startdate"])].append(note["notes"].lower())

def matches(keywords, phrases):
    for phrase in phrases:
        for keyword in keywords:
            if keyword in phrase:
                return True
    return False

for applicant_id in list(applicant_outcomes.keys()):
    outcome = applicant_outcomes[applicant_id]
    identifier = (str(applicant_id), outcome["postype"], outcome["startdate"])
    if identifier in note_lookup:
        # check 8-1: remove pre-doctoral positions
        if matches(["predoc", "pre-doc"], note_lookup[identifier]):
            del applicant_outcomes[applicant_id]
        # check 8-2: remove research assistants and TA positions
        elif matches(["research assistant", "graduate ta", "teaching assistant"], note_lookup[identifier]) or "ra" in note_lookup[identifier]:
            del applicant_outcomes[applicant_id]
        # check 8-3: remove post-doctoral positions
        elif matches(["post doc", "postdoc", "post-doc"], note_lookup[identifier]):
            del applicant_outcomes[applicant_id]
        # check 8-4: candidate is still on the job market
        elif matches(["job market", "expected"], note_lookup[identifier]):
            del applicant_outcomes[applicant_id]
        # check 8-5: candidate is a student (ignore any employment positions with student in the title)
        elif matches(["student"], note_lookup[identifier]) and str(applicant_id) not in os.getenv("IDX").split():
            # IDX is a list of space-separated applicant ids on a single line that are of students that have not yet graduated (given in the note; use print() to search for them)
            del applicant_outcomes[applicant_id]
        # check 8-6: employment during PhD
        elif matches(["temporary", "graduate researcher", "phd trainee", "phd researcher", " but started lecturing in "], note_lookup[identifier]) or str(applicant_id) in os.getenv("DURN").split():
            # DURN is a list of space-separated applicant ids on a single line where the recorded position was prior to graduation (given in the note; use print() to search for them)
            del applicant_outcomes[applicant_id]
        # check 8-7: candidate just graduated
        elif matches(["just finished"], note_lookup[identifier]):
            del applicant_outcomes[applicant_id]
        # check 8-8: candidate recorded as an assistant professor outside of the economic sciences
        elif matches(["cs department", "civil engineering"], note_lookup[identifier]):
            del applicant_outcomes[applicant_id]
        # check 8-9: visiting position (all of these are time-limited rather than permanent or continuing)
        elif matches(["visiting"], note_lookup[identifier]):            
            del applicant_outcomes[applicant_id]
        # check 8-A: temporary removal of known reversed placements
        elif matches(["other way"], note_lookup[identifier]):            
            del applicant_outcomes[applicant_id]

# STEP 9: self-self positions may be broken - this needs to be reviewed
for key in os.getenv("ERRORS").split(): 
    # ERRORS is a list of space-separated applicant IDs on a single line that are confirmable to be mis-reported as graduating from a private company
    # this can be computed by checking the category of the graduating institution
    del applicant_outcomes[key] # any placement from a private company to a private company
if DEBUG:
    i = 0
    for applicant_id in list(applicant_outcomes.keys()):
        outcome = applicant_outcomes[applicant_id]
        if outcome["from_institution_name"] == outcome["to_name"]:
            print(outcome["from_institution_name"], applicant_id)
            i += 1
    print(i, "total diagonals")

# STEP A: deal with the UK lecturer is really assistant professor issue
# the list of institutions that use the lecturer system is produced by manually looking them up online

switch_to_professor = [3333, 1228, 1403, 220, 1492, 90, 1148, 435, 1660, 2442, 1981, 333, 1569, 657, 810, 894, 538, 1818, 1252, 652, 1648, 1341, 1871, 607, 2383, 1894, 757, 1179, 1089, 1757, 555, 1037, 1640, 2485, 796, 874, 120, 744, 858, 1261, 2688, 1177, 362, 124, 801, 1338, 83, 861]
save = None
for key in applicant_outcomes:
    if applicant_outcomes[key]["to_institution_id"] in switch_to_professor:
        applicant_outcomes[key]["postype"] = 1
        applicant_outcomes[key]["position_name"] = "Assistant Professor"
        save = key

# STEP B: filter-by-year
sorted_by_year = defaultdict(dict) 
for applicant_id in list(applicant_outcomes.keys()):
    outcome = applicant_outcomes[applicant_id]
    identifier = (str(applicant_id), outcome["postype"], outcome["startdate"])
    if identifier in note_lookup:
        # check B-1: delete anything prior to 2003
        if matches([str(i) for i in range(1990, 2003)], note_lookup[identifier]):
            del applicant_outcomes[applicant_id]
        # check B-2: manually correct 2003, 2004 and 2006
        elif matches(["2003"], note_lookup[identifier]):
            outcome["startdate"] = datetime.date(2003, 7, 1)
            sorted_by_year[2003][str(applicant_id)] = outcome
        elif matches(["2004"], note_lookup[identifier]):
            outcome["startdate"] = datetime.date(2004, 7, 1)
            sorted_by_year[2004][str(applicant_id)] = outcome
        elif matches(["2006"], note_lookup[identifier]):
            outcome["startdate"] = datetime.date(2006, 7, 1)
            sorted_by_year[2006][str(applicant_id)] = outcome
    # check B-3: remove all 2022 entries, as this is a catch-all zone
    if "2022" in str(outcome["startdate"]):
        del applicant_outcomes[applicant_id]
    else:
        sorted_by_year[int(str(outcome["startdate"]).split("-")[0])][str(applicant_id)] = outcome

# STEP C: save to disk
result = {}
if DEBUG: 
    print()
for key in sorted(sorted_by_year.keys()):
    if DEBUG:
        print("Year", key, "has", len(sorted_by_year[key]), "placement outcomes")
    result[key] = sorted_by_year[key]
with open("to_from_by_year.json", "w") as f:
    json.dump(dict(result), f, default = str, indent = 4)
