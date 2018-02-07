from typing import Dict, List, NamedTuple

RawRule = NamedTuple('RawRule', [('name', str), ('raw_alternates', str)])
Rule = NamedTuple('Rule', [('name', str), ('alternates', List[str])])

ASSIGN_TOKEN = '::='
START_RULE_TOKEN = '<'
END_RULE_TOKEN = '>'


def parse_grammar_file(filename: str):
    raw_rules = get_raw_rules_from_file(filename)
    rules = process_raw_rules(raw_rules)
    ... # TODO: process each rule's alternates


def get_raw_rules_from_file(filename: str) -> List[RawRule]:
    lines = get_nonempty_lines_from_file(filename)
    rules = {}
    current_rule = None
    for line in lines:
        if line.find(ASSIGN_TOKEN) > 0:
            # This line names a rule.
            if line.count(ASSIGN_TOKEN) > 1:
                # Can only define one rule per line.
                raise RuntimeError(f"Too many rule assignments in one line.")
            # Process the name of the rule.
            name, raw_rule = line.split(ASSIGN_TOKEN)
            name = name.strip()
            if not (name.startswith(START_RULE_TOKEN) and name.endswith(END_RULE_TOKEN)):
                raise RuntimeError(f"Invalid rule name: '{name}'")
            name = name[1:-1]
            # If the rule has not been named previously, create it.
            if name in rules:
                raise RuntimeError(f"Cannot create multiple rules with the same name: '{name}'")
            rules[name] = [raw_rule.strip()]
            current_rule = name
        else:
            if current_rule is None:
                raise RuntimeError(f"First nonempty line must name a new rule.")
            # We must be continuing a rule.
            rules[current_rule].append(line.strip())
    rule_list: List[RawRule] = []
    for name, raw_rules in rules.items():
        alternates = ' '.join(raw_rules)
        rule = RawRule(name, alternates)
        rule_list.append(rule)
    return rule_list


def get_nonempty_lines_from_file(filename: str) -> List[str]:
    lines = []
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if line:
                lines.append(line)
    return lines


def process_raw_rules(rules: List[RawRule]) -> Dict[str, List[str]]:
    processed_rules = {}
    for rule in rules:
        # Split the rule into its alternates.
        raw_alternates = rule.raw_alternates
        inside_quotes = False
        quote_type = None
        start_index = -1
        alternates = []
        for i, c in enumerate(raw_alternates):
            if c == '"' or c == '\'':
                if inside_quotes and c == quote_type:
                    # Just finished the quoted portion.
                    inside_quotes = False
                elif not inside_quotes:
                    # Starting a quoted string.
                    quote_type = c
                    inside_quotes = True
            elif c == '|' and not inside_quotes:
                # Add this alternate to the list.
                alternates.append(raw_alternates[start_index+1:i])
                start_index = i
        if inside_quotes:
            raise RuntimeError(f"Missing closing quote ({quote_type}) for rule: '{rule.name}'")
        alternates.append(raw_alternates[start_index+1:len(raw_alternates)])
        processed_rules[rule.name] = alternates
    return processed_rules
