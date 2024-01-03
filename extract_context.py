from bs4 import BeautifulSoup


def extract_context(dmn_filepath):
    with open(dmn_filepath) as f:
        soup = BeautifulSoup(f, features='xml')

    input_nodes = soup.find_all('input')
    inputs_context = {}

    # For each input, give the label
    for inputNode in input_nodes:
        # Get the input name
        input_node_name = inputNode.find('inputExpression').text.strip().replace("'","\\'")
        # Get the input label
        input_label = inputNode["label"]
        # Get annotations (if they exist)
        input_annotation = ''
        if len(soup.select("inputData[name='" + input_label + "']")) > 0:
            input_data_id = soup.select("inputData[name='" + input_label + "']")[0]["id"]
            for targetRef in soup.select("targetRef[href='#" + input_data_id + "']"):
                annotation_id = targetRef.parent.find('sourceRef')["href"].replace("#","")
                if len(soup.select("textAnnotation[id='" + annotation_id + "']")) > 0:
                    input_annotation = soup.select("textAnnotation[id='" + annotation_id + "']")[0].text.strip()
        inputs_context[input_node_name] = {"label": input_label, "annotation": input_annotation, 'input_options': []}

    # For each rule outcome, give the annotation for each possible solution and the knowledge source
    outputs_context = {}
    for dt in soup.find_all("decision"):
        # Output annotations
        output_name = dt.find('output')["name"]
        output_label = dt.find('output')["label"]
        outcomes_rules = []
        outcomes_annotations = {}
        input_options = {}
        for rule in dt.find_all('rule'):
            output_outcome = rule.find('outputEntry').text.strip().replace("'","\\'").replace('"', '').replace(' ', '_')
            # Show rule
            rule_query = 'WHEN '
            inputs = dt.find_all("input")
            input_entries = rule.find_all("inputEntry")
            for i in range(0, len(input_entries)):
                if i > 0:
                    rule_query += ' AND '
                input_name = beautify(inputs[i].inputExpression.text)
                input_value = beautify(input_entries[i].text)
                if input_value == '' or input_value == ' ':
                    input_value = "any"
                rule_query += input_name + " is " + input_value

            rule_query += ' THEN ' + output_label + " IS " + output_outcome
            outcomes_rules.append({'output_outcome': output_outcome, 'outcome_rule': rule_query.replace('\n', '')})

            try:
                inputs_context[input_name]["input_options"].append(input_value.replace("_", ""))
            except:
                print("Problem with input_name " + input_name)

            if rule.description is not None:
                output_value_annotation = rule.description.text.strip().replace("'","\\'")
                outcomes_annotations[output_outcome] = output_value_annotation

        # Knowlede sources
        knowledge_source = ''
        knowledge_source_id = dt.find('requiredAuthority')
        if knowledge_source_id:
            knowledge_source_id = knowledge_source_id["href"].replace("#", "")
            print(knowledge_source_id)
            if len(soup.select("knowledgeSource[id='" + knowledge_source_id + "']")) > 0:
                knowledge_source = soup.select("knowledgeSource[id='" + knowledge_source_id + "']")[0]["name"]


        outputs_context[output_name] = {"label": output_label, "outcomes": outcomes_annotations,
                                        "knowledge_source": knowledge_source, "outcomes_rules": outcomes_rules,
                                        "input_options": input_options}

    return {'inputs': inputs_context, 'outputs': outputs_context}


def beautify(string):
    return string.replace('\'','').replace('"', '').replace(' ', '_').replace('\n', '')