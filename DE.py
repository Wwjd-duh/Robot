import re
import random

class Rule:
def **init**(self, level, pattern, output):
self.level = level
self.pattern = pattern.strip()
self.output = output.strip()
self.subrules = []

class DialogEngine:

```
def __init__(self, state_machine, action_runner, script_file):
    self.state_machine = state_machine
    self.action_runner = action_runner

    self.rules = []
    self.active_rules = []
    self.variables = {}
    self.definitions = {}

    self.load_script(script_file)

# --------------------------------------------------
# SCRIPT LOADING
# --------------------------------------------------

def load_script(self, filename):

    print("Loading dialog script:", filename)

    stack = []

    with open(filename, "r") as f:
        lines = f.readlines()

    for lineno, line in enumerate(lines, start=1):

        line = line.strip()

        if not line or line.startswith("#"):
            continue

        # -------------------------
        # DEFINITIONS (~name)
        # -------------------------
        if line.startswith("~"):

            try:
                name, values = line.split(":", 1)
                name = name[1:].strip()

                values = re.findall(r'"([^"]+)"|\b(\w+)\b', values)
                words = [a or b for a, b in values]

                self.definitions[name] = words

                print("Definition loaded:", name, words)

            except:
                print("Definition parse error line", lineno)

            continue

        # -------------------------
        # RULES
        # -------------------------
        if line.startswith("u"):

            try:

                # determine level
                if line[1].isdigit():
                    level = int(line[1])
                else:
                    level = 0

                if level > 6:
                    print(f"ERROR line {lineno}: nesting depth exceeded")
                    continue

                parts = line.split("):", 1)

                pattern_part = parts[0]
                output = parts[1] if len(parts) > 1 else ""

                pattern = pattern_part.split("(", 1)[1]

                rule = Rule(level, pattern, output)

                print(f"Parsed rule (level {level}):", pattern)

                if level == 0:

                    self.rules.append(rule)
                    stack = [rule]

                else:

                    if level - 1 >= len(stack):

                        print(f"Parser warning line {lineno}: missing parent")
                        continue

                    parent = stack[level - 1]
                    parent.subrules.append(rule)

                    stack = stack[:level] + [rule]

            except Exception as e:

                print(f"Parser error line {lineno}: {line}")
                print(e)

    self.active_rules = self.rules

    print("Dialog script loaded successfully.")
    print("Top level rules:", len(self.rules))

# --------------------------------------------------
# INPUT HANDLING
# --------------------------------------------------

def handle_input(self, text):

    text = self.normalize(text)

    print("\nUser input:", text)

    if text in ["stop", "cancel", "reset", "quit"]:

        print("Global interrupt detected")

        self.action_runner.stop_all()
        self.active_rules = self.rules

        return "Resetting."

    # try active conversation rules first
    rule = self.match_rules(self.active_rules, text)

    # if nothing matched, try global rules
    if not rule:
        rule = self.match_rules(self.rules, text)

    if rule:

        print("Matched rule:", rule.pattern)

        if rule.subrules:
            self.active_rules = rule.subrules
        else:
            self.active_rules = self.rules

        speak, actions = self.process_output(rule.output)

        print("Executing actions:", actions)

        self.action_runner.run_actions(actions)

        return speak

    print("No rule matched")

    return "I don't understand."

# --------------------------------------------------
# TEXT NORMALIZATION
# --------------------------------------------------

def normalize(self, text):

    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)

    return text.strip()

# --------------------------------------------------
# RULE MATCHING
# --------------------------------------------------

def match_rules(self, rules, text):

    for rule in rules:

        print("Checking rule:", rule.pattern)

        if self.match_pattern(rule.pattern, text):
            return rule

    return None

# --------------------------------------------------
# PATTERN MATCH
# --------------------------------------------------

def match_pattern(self, pattern, text):

    pattern = pattern.lower().strip()

    # -------------------------
    # definition match (~word)
    # -------------------------
    if pattern.startswith("~"):

        name = pattern[1:]

        if name in self.definitions:

            for word in self.definitions[name]:

                if text == word.lower():
                    return True

    # -------------------------
    # bracket choices
    # -------------------------
    if pattern.startswith("["):

        options = re.findall(r'"([^"]+)"|\b(\w+)\b', pattern)
        words = [a or b for a, b in options]

        if text in [w.lower() for w in words]:
            return True

    # -------------------------
    # variable capture
    # -------------------------
    if "_" in pattern:

        prefix = pattern.replace("_", "").strip()

        if text.startswith(prefix):

            captured = text[len(prefix):].strip()

            if captured:

                self.variables["name"] = captured
                print("Captured variable name:", captured)

                return True

    # -------------------------
    # exact match
    # -------------------------
    if text == pattern:
        return True

    return False

# --------------------------------------------------
# OUTPUT PROCESSING
# --------------------------------------------------

def process_output(self, output):

    # variable recall
    for var in self.variables:

        output = output.replace(f"${var}", self.variables[var])

    # random choices
    choices = re.findall(r"\[(.*?)\]", output)

    for c in choices:

        options = re.findall(r'"([^"]+)"|\b(\w+)\b', c)
        words = [a or b for a, b in options]

        if words:
            choice = random.choice(words)
            output = output.replace(f"[{c}]", choice)

    # extract actions
    actions = re.findall(r"<(.*?)>", output)

    speak = re.sub(r"<.*?>", "", output).strip()

    return speak, actions
```
