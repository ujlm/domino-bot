# In this file, we try to determine the risk level using the BMI DMN file

import time
import datetime
from operator import contains
from socket import timeout
from turtle import numinput
from cdmn.API import DMN
import re
from jinja2 import Undefined
from regex import P
from word2number import w2n
from extract_context import extract_context
import buttons
import unicodedata

class TimeoutException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)

def capitalize(string, start, length):
    string = str(string)
    return string[start:start+length].upper() + string[start+length:]

class Model:
    def __init__(self, file):
        # Set file
        self.file = file

        # Set model
        self.model = DMN(file, auto_propagate=True)

        self.context = extract_context(file)
        #print(str(extract_context(file)))

        # The variable for which we expect to get an input
        self.pending_input = ""

        # Remember input order for backintent
        self.processed_inputs = []

        # Create tree of this model
        self.decision_tree = self.create_tree()

        # Create saved state
        self.saved_state = {}

        # Are we working with unknown information?
        self.unknown_information_present = False

        # Unknown_information temp object
        self.unknown_information_obj = {
            "inputs": {},
            "result_options": {}
        }

        # We use this dict for setting the backwards reasoning values
        self.backwards_reasoning = {
            "variable": {
                "name": "",
                "value": ""
            },
            "target": {
                "name": "",
                "value": ""
            },
            "temp_input": {
                "name": "",
                "value": ""
            }
        }


    def setPending(self, val):
        if val != None & val != Undefined:
            self.pending_input = val


    def getPending(self):
        return self.pending_input
    
    def getPendingType(self):
        return self.model.type_of(self.getPending())


    def setValue(self, val, prop=''):
        print("Set value " + val + " for " + prop)
        # Get all outputs before assigning this value, to compare at the end of this fx
        all_outputs_initial = self.get_all_output_values()
        # Normal way of setting value: set value for the current 'open' variable
        if prop == '':
            prop = self.pending_input

        try:
            if val == "?":
                self.unknown_information_obj['inputs'][prop] = val
                return 'Don\'t worry about it, I got you.<br/>'
            print(self.model.possible_values_of(prop))
            print(self.model.type_of(prop))
            if(self.model.type_of(prop) == "Int"):
                if not val.isdigit():
                    print('Expected integer and got other type')
                    raise TypeError('Expected int and got ' + type(val))
            self.model.set_value(prop, val)
        except:
            # If number expected, try to convert word to number
            print("expect:" + str(self.model.type_of(prop)))
            if self.is_number(self.model.type_of(prop)):
                try:
                    val = w2n.word_to_num(val)
                    if(self.model.type_of(prop) == "Int"):
                        if type(val) is not int:
                            print('Not an integer.')
                            return 'error'
                    self.model.set_value(prop, val)
                except ValueError:
                    print('Word cannot be converted to number')
                    return 'error'
            else:
                # Else deny input
                print('Could not set value ' + str(val) + ' for ' + str(prop))
                return 'error'
        
        # If we're working with unknown variables
        if self.isUnknownInformationPresent():
            self.unknown_information_obj['inputs'][prop] = val
            print(str(self.unknown_information_obj))
            return 'Ok value is set. '

        # If we're working with the pending input
        if prop == self.pending_input:
            self.pending_input = "" # Make place for the next 'open' variable
            self.processed_inputs.append(prop)

        msg = ''
        all_outputs_updated = self.get_all_output_values()
        for output in all_outputs_updated:
            if True: # None in all_outputs_updated.values() --> If there is no unknown anymore, the display solution function will take over
                if all_outputs_updated[output] != all_outputs_initial[output]:
                    # We derived a value, let the user know
                    outcome_label, outcome_annotation = '',''
                    try:
                        outcome_label = self.context['outputs'][output]['label']

                        # Add annotations if exist
                        if str(all_outputs_updated[output]) in self.context['outputs'][output]['outcomes']:
                            outcome_annotation = self.context['outputs'][output]['outcomes'][str(all_outputs_updated[output])]
                        elif str(all_outputs_updated[output]).replace("_", " ") in self.context['outputs'][output]['outcomes']:
                            # cDMN might have replaced spaces with underscores
                            outcome_annotation = self.context['outputs'][output]['outcomes'][str(all_outputs_updated[output]).replace("_", " ")]
                        
                        # Add knowledge source if exists
                        if self.context['outputs'][output]["knowledge_source"] != '':
                            outcome_annotation += '<br/>Based on ' + self.context['outputs'][output]["knowledge_source"]
                        print('outcome ann:' + outcome_annotation)
                        
                    except:
                        print('no outcome found')
                    
                    output_display = output
                    if outcome_label != '':
                        output_display =  outcome_label
                    msg += 'Based on your input, I have set ' + str(output_display) + ' to <b>' + str(all_outputs_updated[output]) + '</b>.'
                    if outcome_annotation != '':
                        msg += '<br/>' + outcome_annotation + ''
                    msg += '<br/><br/>'
        
        return msg
    
    def get_all_output_values(self):
        all_outputs = self.get_all_outputs()
        out = {}
        for output_name in all_outputs:
            out[output_name] = self.getValue(output_name)
        return out

    def getValue(self, prop):
        return self.model.value_of(prop)
    
    def reset(self):
        self.model.clear()

    
    def getDependencies(self, prop, oneLevelDownOnly = False):
        dependencies = self.model.dependencies_of(prop)
        if(oneLevelDownOnly):
            dep2 = dependencies.copy()
            keys = dependencies.keys()
            for k in keys:
                level = dependencies[k]
                if level != 0:
                    dep2.pop(k)
            dependencies = dep2
                    
        return dependencies

    
    def get_previous_variable(self):
        if len(self.processed_inputs) > 0:
            previous_input = self.processed_inputs[len(self.processed_inputs)- 1]
            self.processed_inputs.remove(previous_input)
            return previous_input
        else:
            return None

    
    def set_backwards_reasoning(self, v, n, val):
        try:
            self.backwards_reasoning[v]["name"] = n
            self.backwards_reasoning[v]["value"] = val
        except:
            return 0
        return 1
    
    def reset_backwards_reasoning(self):
        self.backwards_reasoning = {
            "variable": {
                "name": "",
                "value": ""
            },
            "target": {
                "name": "",
                "value": ""
            }
        }

    
    def get_backwards_reasoning(self, v, t):
        return self.backwards_reasoning[v][t]

    
    def getVariableNames(self):
        return self.model.get_variable_names()


    def dependent_on_unsolved_intermediary(self,missing_values):
        intermediaries = self.get_all_outputs()  # Can outputs be intermediary?
        dependent = False
        for val in missing_values:
            for intermediary in intermediaries:
                if val == intermediary:
                    if not self.model.is_certain(intermediary):
                        dependent = True
                        break
        return dependent

    
    def extract_prop_from_string(self,string):
        string = string.replace("?", "")
        prop_dict = {
            "name": "",
            "type": None,
            "remaining_string": string
        }
        words = string.split(' ')
        var_names_lowercase = [w.lower() for w in self.model.get_variable_names()]
        print(str(self.model.get_variable_names()))
        for word in words:
            for i in range (len(var_names_lowercase)):
                if word == var_names_lowercase[i] or word == self.model.get_variable_names()[i] or word == var_names_lowercase[i] + "t":
                    # Capitalize input if needed
                    prop_dict = self.generate_prop_obj(self.model.get_variable_names()[i], string)

        return prop_dict


    def generate_prop_obj(self, prop, string):
        obj = {
            "name": prop,
            "type": self.model.type_of(prop),
            "remaining_string": remove_word_from_string(prop.lower(), string.lower())
        }
        return obj

    
    def extract_value_from_string(self, string, prop):
        words = string.lower().split(' ')
        values_lowercase = []
        
        try:
            all_possible_values = self.model.possible_values_of(prop)
            try:
                all_possible_values = all_possible_values.replace(' ', '').split(',')
                values_lowercase = [v.lower() for v in all_possible_values]
            except:
                values_lowercase = [v.lower() for v in all_possible_values]
            print(values_lowercase)
        except:
            print("No predefined types")
            
        for word in words:
            print(word)
            print(self.type_is_number(word))
            if self.model.type_of(prop) == 'NoneType' or self.model.type_of(prop) == None:
                # Boolean
                if word == "false" or word == "true":
                    return word
            if self.is_number(self.model.type_of(prop)):
                if self.type_is_number(word):
                    return word
            for i in range (len(values_lowercase)):
                if word == values_lowercase[i]:
                    return all_possible_values[i]
        return ''

    
    def type_is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            pass

        try:
            unicodedata.numeric(s)
            return True
        except (TypeError, ValueError):
            pass

        return False
    
    def what_if_reasoning(self, prop, val):
        try:
            self.setValue(val, prop)
            print(self.model.get_all_values())
        except:
            return 'In that case, the model wouldn\'t be satisfiable.'
        return 'In that case ' + str(self.model.get_outputs()[0]) + ' would be ' + str(self.model.value_of(self.model.get_outputs()[0])) + "<br/>" + buttons.create_button("exit", "Quit Model")


    def isUnknownInformationPresent(self):
        return self.unknown_information_present
    
    def setUnknownInformationPresent(self):
        self.unknown_information_present = True

    
    # Reasoning with unknown information: keep vars before inferring
    def unknown_information(self, prop):
        if not self.unknown_information_present:
            # Initialize
            self.save_state()
            print("Saved state: " + str(self.saved_state))
            self.unknown_information_present = True
            # Turn off auto_propagate
            self.model = DMN(self.file, auto_propagate=False)
            for inputName in self.model.get_inputs():
                if self.saved_state[inputName] is not None:
                    print(inputName + " is known")
                    self.unknown_information_obj['inputs'][inputName] = self.saved_state[inputName]
                else:
                    print(inputName + " is not known")
                    self.unknown_information_obj['inputs'][inputName] = None
        self.unknown_information_obj['inputs'][prop] = "?"
        print(str(self.unknown_information_obj))
        return self.unknown_information_obj
    
    def incomplete_information(self):
        self.save_state()
        self.unknown_information_present = True
        # Turn off auto_propagate
        self.model = DMN(self.file, auto_propagate=False)
        for inputName in self.model.get_inputs():
            if self.saved_state[inputName] is not None:
                print(inputName + " is known")
                self.unknown_information_obj['inputs'][inputName] = self.saved_state[inputName]
            else:
                print(inputName + " is not known")
                self.unknown_information_obj['inputs'][inputName] = "?"
        print(str(self.unknown_information_obj))
        return self.unknown_information_obj
            


    def all_possible_models(self, knowns, unknowns,  timeout_sec, time_start, count = 0):

        print("Knowns: " + str(knowns))
        print("Unknowns: " + str(unknowns))
        
        all_possible_solutions = []
        for known in knowns:
            self.model.set_value(known['inputName'], known['value'])
        # TODO: support for multiple unknowns
        for unknown in unknowns:
            # How to generalize to support multiple unknowns?
            for val in unknown["values"]:
                print('unknown val' + str(val))
                self.model.set_value(unknown['inputName'], val)

                # Time limit on loop
                time_elapsed = datetime.datetime.now() - time_start
                if time_elapsed > timeout_sec:
                    print('timeout!')
                    raise TimeoutException("Unfortunately, that is too hard for me to calculate.")

                if len(unknowns) > 1:
                    knowns_updated = knowns.copy()
                    knowns_updated.append({'inputName': unknown['inputName'], 'value': val})
                    unknowns_updated = unknowns.copy()
                    unknowns_updated.remove(unknown)
                    print("Updated unknowns: " + str(unknowns_updated))
                    print(str(knowns_updated))
                    recursive_models = self.all_possible_models(knowns_updated, unknowns_updated, timeout_sec, time_start, count + 1)
                    if recursive_models not in all_possible_solutions:
                        all_possible_solutions.append(recursive_models)
                else:
                    try:
                        self.model.propagate()
                        all_possible_solutions.append(self.model.get_all_values())
                    except:
                        pass
        # Reset Model autopropagation
        # Yes or no?
        if count == 0:
            self.unknown_information_present = False
            print('Possible solutions are ' + str(all_possible_solutions).replace("'", ""))
            return 'Possible solutions are: <br/><br/>' + str(all_possible_solutions).replace("'", "").replace("}, {", "<br/><br/>").replace("[{", "").replace("}]", "").replace(",", "<br/>")
        return '<br/>' + str(all_possible_solutions) + '<br/>'

    
    # Optimization: get min/max val that variable needs to have in order to come to certain output
    # Requirement: variable in INPUT
    def optimization(self, target, target_value, variable, min_or_max ='max'):
        self.save_state()
        if target in self.get_all_outputs():
            if variable not in self.getDependencies(target):
                return "Sorry, %s is not dependent on %s"%(target, variable)
        else:
            return "I'm sorry, target should be an output. %s is an input variable."%(target)

        missing_variables = []
        missing_variables = [x for x in self.model.dependencies_of(target)  # Calculate only the relevant input variables
                        if x in self.model.get_inputs()
                        and x in self.model.get_unknown_variables()]

        print('Target is: ' + target)
        print("Target value is: " + str(target_value))

        if variable in missing_variables:
            missing_variables.remove(variable)

        level_of_target = [d["level"] for d in self.decision_tree if d["name"] == target]
        print("Missing variables:")
        print(missing_variables)
        while len(missing_variables) > 0:
            print(len(missing_variables))
            level_of_dep = [d["level"] for d in self.decision_tree if d["name"] == missing_variables[0]]
            if level_of_dep[0] == level_of_target[0] + 1:
                # Only direct dependants are relevant here
                # Check if variable is in saved state; if so there's no need to ask for it
                print("Saved state: ")
                print(self.saved_state)

                if self.saved_state[missing_variables[0]] != None:
                    print("i set value %s for prop %s"%(missing_variables[0], self.saved_state[missing_variables[0]]))
                    self.model.set_value(missing_variables[0], self.saved_state[missing_variables[0]])
                    missing_variables.remove(missing_variables[0])
                    continue
                # Else ask for the input
                self.set_backwards_reasoning("temp_input", missing_variables[0] , "")
                return self.ask_general(missing_variables[0])
            # Else remove redundant dependant
            print("%s is not relevant for %s"%(missing_variables[0], target))
            missing_variables.remove(missing_variables[0])
        
        print(self.model.possible_values_of(target))
        msg = "This value cannot be reached using the given values.<br/>" + buttons.create_button("exit", "Quit Model")
        try:
            self.model.set_value(target, target_value)
        except:
            return msg

        """
        # If we want to choose between min or max
        model = self.model.maximize(variable)
        if min_or_max == 'min':
            model = self.model.minimize(variable)
        """
        
        if self.is_number(self.model.type_of(variable)):
            # Max/min numeric input
            display_model_max, outcomes_list_max = self.generate_display_model(self.model.maximize(variable), variable)
            display_model_min, outcomes_list_min = self.generate_display_model(self.model.minimize(variable), variable)
            print(outcomes_list_max)
            print(outcomes_list_min)
            msg = 'In order for {} to be {}, the {} value for {} is {}. In order for {} to be {}, the minimal value for {} is {}'.format(target, target_value, min_or_max, variable, str(outcomes_list_max[0]),target, target_value, variable, str(outcomes_list_min[0]))
            #msg += self.explain_solution()
        elif self.model.possible_values_of(variable) != None and len(self.model.possible_values_of(variable)) > 0:
            # Slower: try all possible categories for categorical variables
            # print('Possible guest count: ' + self.model.possible_values_of('guestCount'))
            self.model.set_value(target, None)
            for val in self.model.possible_values_of(variable).strip().split(","):
                try:
                    self.model.set_value(variable, val)
                except:
                    print('rror')
                    break

                if(self.model.value_of(target) == target_value):
                    msg = 'In order for <b class="font-yellow">{}</b> to be <b class="font-yellow">{}</b>, the value for <b class="font-blue">{}</b> needs to be <b class="font-blue">{}</b>.'.format(target, target_value, variable, val)
                    #msg += self.explain_solution()
                    break
        # TODO Everything back to normal
        
        self.set_backwards_reasoning("target", "", "")
        self.set_backwards_reasoning("variable", "", "")
        self.set_backwards_reasoning("temp_input", "", "")

        return msg


    def generate_display_model(self, model, variable):
        #print(model)
        display_model = model
        outcomes_list = []

        display_model = display_model.replace(':={', '')
        display_model = display_model.replace('}', '')
        display_model = display_model.replace('->', ' = ')

        dArray = display_model.split("\n")
        for i in range(0, len(dArray)):
            print(dArray[i])
            if variable in dArray[i]:
                val = dArray [i].split(":=")[1]
                if val[-1] == ".":
                    val = val[:-1]
                outcomes_list.append(val)

        return model, outcomes_list


    # Returns all outputs of the model (intermediaries and final outputs)
    def get_all_outputs(self):
        return self.model.get_intermediary() + self.model.get_outputs()
    

    def getUnsolvedIntermediary(self):
        if self.unknown_information_present:
            inputNames = list(self.unknown_information_obj['inputs'].keys())
            for inputName in inputNames:
                if self.unknown_information_obj['inputs'][inputName] == None:
                    self.pending_input = inputName
                    return self.ask_general(inputName)
        else:
            intermediaries = self.get_all_outputs()
            # Solve intermediaries
            for im in intermediaries:
                if not self.model.is_certain(im):
                    missing = self.model.missing_for(im)
                    print(missing)
                    levelOfIm = [d["level"] for d in self.decision_tree if d["name"] == im][0]
                    if missing and not self.dependent_on_unsolved_intermediary(missing):
                        
                        # Extra check bcs cDMN missing_for not always accurate
                        for mis in missing:
                            levelOfMissingVal = [d["level"] for d in self.decision_tree if d["name"] == mis][0]
                            levelGap = int(levelOfMissingVal) - int(levelOfIm)
                            if (len(missing) > 1 and levelGap == 1):
                                self.pending_input = mis
                                return str(self.ask_general(mis))

                        # Fallback for multilevel inputs
                        self.pending_input = mis
                        return str(self.ask_general(missing[0]))
        return self.display_solution()
    

    def partial_decision_making(self):
        if self.model.is_certain(self.model.get_outputs()[0]):
            return self.display_solution()
        else:
            print("Partial decision making time!")
            self.incomplete_information()
            solution = self.display_solution()
            self.unknown_information_present = False
            return solution
    
    def seek_goal(self, text, sub = False):
        target_prop =  self.extract_prop_from_string(text)
        print(target_prop)
        if target_prop["name"] == '':
            return 'no rules', 'no inter'

        target_value = self.extract_value_from_string(target_prop["remaining_string"], target_prop["name"])
        if target_value == '':
            return target_prop["name"], 'no inter for prop'
        print("Target: " + target_prop["name"] + ", target value: " + target_value)
        all_applicable_rules = self.get_applicable_rules(target_prop["name"], target_value)

        updated_rules = []
        intermediaries = []

        for rule in all_applicable_rules:
                rule_deconstructed = rule.split(' ')
                for i in range (0, len(rule_deconstructed)):
                    if rule_deconstructed[i] not in ("WHEN", "is", "AND", "OR", "THEN", "IS", target_prop["name"], target_value):
                        if rule_deconstructed[i] in self.model.get_intermediary():
                            # w is intermediary
                            possible_values = rule_deconstructed[i + 2].split(',')
                            intermediaries.append({
                                'prop': rule_deconstructed[i],
                                'values': possible_values
                            })
                            for val in possible_values:
                                print("how to get " + rule_deconstructed[i] + " = " + val)
                                #all_applicable_rules.append(self.seek_goal("how to get " + rule_deconstructed[i] + " = " + val))
                                new_rule = self.seek_goal("how to get " + rule_deconstructed[i] + " = " + val, True)
                                if sub:
                                    all_applicable_rules.append(new_rule)
                                else:
                                    new_rule = str(new_rule).split('THEN')[0]
                                    updated_rules.append(str(rule_deconstructed[:i]).replace(",", " ") + str(new_rule) + str(rule_deconstructed[i+3:len(rule_deconstructed)]).replace(",", " ") + " ")

        if sub:
            return all_applicable_rules
        else:
            return updated_rules, intermediaries
    

    def get_applicable_rules(self, target_prop_name, target_value):
        outcomes_rules = self.context['outputs'][target_prop_name]["outcomes_rules"]
        all_applicable_rules = []
        for rule_obj in outcomes_rules:
            if rule_obj['output_outcome'] == target_value:
                all_applicable_rules.append(rule_obj['outcome_rule'])
        if len(all_applicable_rules) == 0 and len(outcomes_rules) == 1:
            # Probably a formula
            all_applicable_rules.append(outcomes_rules[0]['output_outcome'])

        return all_applicable_rules
    
    def sensitivity_analysis(self):
        """
        I want the same output: what can I change
        In that table I look at all the lines with that output
        For each line I look at each input and for each input I check:

            If the input is boolean => it can't be changed
            If the input is an individual value => it can't be changed
            if the input can take several values then you just return that list/interval

        Some inputs depend on another table:

            Go to that table and repeat the above
        """
        result = self.model.get_outputs()[0]
        print("how to get " + result + " = " + self.model.value_of(result))
        return self.seek_goal("how to get " + result + " = " + self.model.value_of(result))


    def get_numerical_bounds(self, inputName):
        possible_values = []
        for option in self.context['inputs'][inputName]["input_options"]:
            if ("<=" in option or ">=" in option):
                if option.replace("<=","") not in possible_values:
                    possible_values.append(option.replace("<=",""))
            elif (">" in option):
                # TODO Generalize to support all numeric types
                possible_values.append(int(option.replace('>', '')) + 1)
            elif ("[" in option):
                possible_values.append(option.split('..')[0].replace("[", ""))
            elif ("]" in option):
                possible_values.append(option.split('..')[1].replace("]", ""))
            else:
                possible_values.append(option)
                # TODO support exclusive ranges
        return possible_values

    
    def minAndMaxBounds(self, prop):
        ranges = self.context['inputs'][prop]["input_options"]

        numericalVals = []
        for option in ranges:
            option = str(option).replace("(", "").replace("[", "").replace("]", "").replace(">", "").replace("<", "")
            option = str(option).replace("=", "").replace(")", "")
            for n in option.split(".."):
                if n != "any":
                    numericalVals.append(int(n))
        
        currentMin = min(numericalVals)
        currentMax = max(numericalVals)
        try:
            for i in range(0, len(numericalVals) - 1):
                # TODO: catch intermediate unallowed ranges
                if numericalVals[i] == max(numericalVals) and ">" in ranges[i]:
                    # Max is infinity
                    currentMax = "&infin;"
                    print(currentMax)
                if numericalVals[i] == min(numericalVals) and i > 0 and "<" in ranges[i]:
                    # Min is zero
                    currentMin = "&minus;&infin;"
        except Exception as e:
            print(e)
        
        return currentMin, currentMax


    def display_solution(self):
        res = ''
        if not self.unknown_information_present:
            # This msg is currently obsolete, since all intermediary and end outcomes are displayed in setValue()
            res = "This is the final outcome.<br/>"
            """
            for out in self.model.get_outputs():
                res += "The value of " + str(out) + " is <b>" + str(self.model.value_of(out)) + "</b>"
            """
            # End msg
        else:
            print("Unknown information: " + str(self.unknown_information_obj))
            # If there are no unknown inputs anymore: do the reasoning
            inputNames = list(self.unknown_information_obj['inputs'].keys())
            knowns = []
            unknowns = []
            for inputName in inputNames:
                if self.unknown_information_obj['inputs'][inputName] == "?":
                    inputType = self.model.type_of(inputName)
                    values = []
                    if self.is_number(inputType):
                        print("Okay ill look to the bounds")
                        print(self.context)
                        values = self.get_numerical_bounds(inputName)

                    elif inputType is None or inputType == 'NoneType':
                        # Boolean
                        values = ["true", "false"]
                    else:
                        try:
                            values = self.model.possible_values_of(inputName).strip().split(',')
                        except:
                            values = self.model.possible_values_of(inputName)
                    unknowns.append({'inputName': inputName, 'values': values})
                else:
                    knowns.append({'inputName': inputName, 'value': self.unknown_information_obj['inputs'][inputName]})
            try:
                res += self.all_possible_models(knowns, unknowns, datetime.timedelta(seconds=3), datetime.datetime.now())
            except Exception as e:
                print(e)
                res = str(e)
                return res
                
        #return res + buttons.create_link_button('https://bit.ly/3CmSkQh', 'Give feedback') + buttons.create_button('why?', 'View the reasoning') + buttons.create_button('exit', 'Choose another model')
        return res + "<br/>" + buttons.create_button('why?', 'View the reasoning') + buttons.create_button('exit', 'Restart')

    def clean_arraystring(self,string):
        return str(string).replace("['", "").replace("']", "")


    def explain_solution(self, prop =''):
        # Default: explain top outcome
        outputs = self.model.get_outputs() + self.model.get_intermediary()
        rule = ""
        res = ""
        if prop == '':
            prop = outputs[0]
        
        if prop in outputs:
            # Prop is an output, so show the rules
            rules = self.get_applicable_rules(prop, self.model.value_of(prop))
            rule = "<p><b>RULE: </b>" + self.clean_arraystring(str(rules)) + "</p>"

        if self.model.is_certain(prop):
            level_of_prop = [d["level"] for d in self.decision_tree if d["name"] == prop]
            res = "<span class='level level-%s'><b>%s</b>=<i>%s</i> because of the following inputs:</span><br/>"%(str(level_of_prop[0]),capitalize(prop, 0,1), self.model.value_of(prop))
            for dep in self.model.dependencies_of(prop):
                # Only explain solution if level of dependency is one lower than prop
                level_of_dep = [d["level"] for d in self.decision_tree if d["name"] == dep]
                if level_of_dep[0] == level_of_prop[0] + 1:
                    if len(self.model.dependencies_of(dep)) > 0:
                        res += self.explain_solution(dep)
                    else:
                        res += "<span class='level level-" + str(level_of_dep[0]) + "'><b>" + capitalize(dep, 0, 1) + "</b>=<i>" + str(self.model.value_of(dep)) + "</i></span>"
            return rule + res
        else:
            return "I'm sorry I cannot explain the current solution"


    def create_tree(self):
        varnames = self.model.get_variable_names()
        vars = []
        for varname in varnames:
            vars.append({
                "name": varname,
                "level": 0
            })
        for var in vars:
            for other_var in vars:
                if var["name"] != other_var["name"]:
                    if other_var["name"] in self.model.dependencies_of(var["name"]):
                        # Other var is child of var
                        other_var["level"] = max(other_var["level"] + 1, var["level"] + 1)
        return vars

    
    # Save state of model; save all values of model
    def save_state(self):
        if len(self.saved_state) == 0:
            self.saved_state = self.model.get_all_values().copy()

    def restore_state(self):
        if len(self.saved_state) > 0:
            self.model = DMN(self.file, auto_propagate=True)
            for prop in self.saved_state:
                   self.model.set_value(prop, self.saved_state[prop])
        return True

    # Go one step back
    def back_to(self, prop):
        try:
            self.restore_state()
        except Exception as e:
            print(e)

        if self.pending_input != '' and self.pending_input != None and self.pending_input != Undefined:
            self.model.set_value(self.pending_input, None)
        if self.pending_input == '' and len(self.processed_inputs) > 0:
            # Model is solved, yet go one step back
            self.model.set_value(prop, None)
        self.pending_input = prop

        return self.ask_general(prop)


    def ask_general(self, prop, redo = False):
        self.create_tree()
        inputName = str(prop)
        annotation = ''
        if prop in self.context['inputs']:
            if 'annotation' in self.context['inputs'][prop]:
                annotation = self.context['inputs'][prop]['annotation']
            if(self.context['inputs'][prop]['label'] != ''):
                inputName = self.context['inputs'][prop]['label']
        
        question = ''
        if '*?:' in annotation:
            question += '<i>' + annotation.replace("*?:", "") + '</i><br/>'
        else:
            question += '<i>What is the value for ' + inputName + '?</i><br/>'
            if annotation != '':
                question += '(' + annotation + ')'

        # If wrong input was given, explain what type is expected
        t = self.model.type_of(prop)
        if t is not None and redo:
            question += "\n\tPossible type is " + str(t.lower()) + "."
        if t in ('Real', 'Float', 'Double', 'Int', 'String', 'None') or t is None:
            # cDMN: Bool is defined as None
            if redo:
                print("Maybe give even more info?")
            question += "\n\t" + self.explain_type(t)
            try:
                min, max = self.minAndMaxBounds(prop)
                question += " between <b>" + str(min) + " </b>and<b> " + str(max) + "</b>"
            except Exception as e:
                print(e)
        possible_values = self.get_possible_values(prop)
        if t is None or t == 'NoneType':
            # Boolean
            possible_values = buttons.create_button("true", "True") + buttons.create_button("false", "False")
        if possible_values != '':
            question += '<br/>' + str(possible_values)
        return question
    

    def get_possible_values(self, prop):
        response = ''
        possible_values = self.model.possible_values_of(prop)
        if possible_values is not None:
            possible_values = possible_values.strip().split(',')  # ?? Am I correct to assume there are no white spaces in possible values?
            response += "Please choose one of the following:<br/>"
            for v in possible_values:
                response += buttons.create_button(v, v)
                
        return response


    def is_number(self,i):
        if i in ('Real', 'Float', 'Double', 'Int'):
            return True
        return False

    def get_bounds(self, prop):
        minim = self.model.minimize(prop)
        maxim = self.model.maximize(prop)

        lower_range = re.findall('HP:={->(\d+)}', minim)[0]
        upper_range = re.findall('HP:={->(\d+)}', maxim)[0]

        msg = f'In range of ({lower_range}..{upper_range})'
        return msg


    def explain_type(self,t):
        explain = "Put in <b>"

        if t in ('Real', 'Float', 'Double'):
            explain += "a number" # (like this: 1.1)
        elif t == 'Int':
            explain += "an integer" # (like this: 3)
        elif t == 'Str':
            explain += "a string" # (like this: 'Table'
        else:
            explain += "a boolean" # (true/false)
        explain += "</b>"
        return explain

    def not_valid(self, text):
        q = ""
        if text != 'no': # No input is expected when user doesn't want to quit the model
            q += "Sorry, \"" + text + "\" is not a valid input for variable \"" + self.getPending() + "\".<br/>"
        q += self.ask_general(self.getPending(), True)
        return q
    

def all_unknowns(m):
    all_inputs = m.get_inputs()
    for i in all_inputs:
        print(i, ':', m.value_of(i))
        if m.value_of(i) is None:
            print(i, ' is not set\n')


def contains_word(s, w):
    return f' {w} ' in f' {s} '


def remove_word_from_string(word, string):
    removal_list = [word]
    edit_string_as_list = string.split()
    final_list = [word for word in edit_string_as_list if word not in removal_list]
    return ' '.join(final_list)


def no_valid_prop(m):
    msg = "I'm sorry I don't recognize this property. Please use one of the following variable names:"
    for varName in m.getVariableNames():
        msg += '<br/>' + varName
    return msg


def get_res(m, text):
    if(text.lower() in ('hi', 'greet')):
        return "Hi I'm your DMN bot." + buttons.create_button('exit', 'Please choose a model')
    # Recognize certain action words (for the moment, this part is redundant)
    if(text in ('ok', 'alright', 'okay', 'proceed')):
        #m.restore_state()
        intermediaries = m.getUnsolvedIntermediary()
        return str(intermediaries)
    
    # Reset to begin state
    if text.lower() == "reset":
        print("Reset")
        m.reset_backwards_reasoning()
        m.reset()
        return True
    
    # Target fx
    if text == "GET ALL Y":
        yvalues = []
        for val in m.get_all_output_values():
            print(val)
            yvalues.append(val)
        return  yvalues

    if "GET ALL X FOR:" in text:
        y = text.replace("GET ALL X FOR:", "")
        if y not in m.get_all_output_values():
            if capitalize(y,0,1) in m.get_all_output_values():
                y = capitalize(y,0,1)
            else:
                return ["None"]
        xvalues = []
        for val in m.getDependencies(y, True):
            print(val)
            xvalues.append(val)
        return xvalues
    

    if text.lower() == "back":
        prev = m.get_previous_variable()
        
        if prev != None:
            # There is a previous value: set this as pending variable, clear current val from model and ask for this one
            print("Okay I'll go back to " + str(prev))
            return m.back_to(prev)
        # If there is no previous value, backintent equals stop intent
        quit_msg = "Are you sure you want to quit the model?<br/>"
        quit_msg += buttons.create_button("quit", "Quit")
        quit_msg += buttons.create_button("_stay_", "Stay")
        return quit_msg

    # Backwards reasoning start
    # Example sentence: "<<What should>>**TRIGGER** my <<weight>>**var_prop** be to alter my <<bmi>>**target_prop**?""
    # 2nd example: what should my surface_skin_temperature be to alter my skin_temperature?
    # 3th example: what should my bmi be to alter my BMILevel?
    # Future work: interpret commas and dots depending on context
    if contains_word(text.lower(), 'what should'):
        # Extract the variable and the target output from the sentence
        var_prop =  m.extract_prop_from_string(text)
        target_prop = m.extract_prop_from_string(var_prop["remaining_string"])

        if var_prop["name"] == '' or target_prop["name"] == '':
            return no_valid_prop(m)
        # Check which one is the higher one --> the higher one becomes the target property
        if target_prop["name"] in m.getDependencies(var_prop["name"]):
            old_var_prop = var_prop
            var_prop = target_prop
            target_prop = old_var_prop
        m.set_backwards_reasoning("variable", var_prop["name"],"") 
        m.set_backwards_reasoning("target", target_prop["name"], "")

        if target_prop["name"] != None:
            return "What is the target value that you want to obtain for " + target_prop["name"] + "? " + str(m.get_possible_values(target_prop["name"]))
        return "I'm sorry, I didn't get that"

    if m.get_backwards_reasoning("target", "name") != "":
        varname = m.get_backwards_reasoning("variable", "name")
        targetname = m.get_backwards_reasoning("target", "name")
        print(varname)
        print(targetname)

        if m.get_backwards_reasoning("temp_input", "name") == "":
            m.set_backwards_reasoning("target", targetname, text)
            m.save_state()
            m.reset() # Model need to be cleared for optimization
        else:
            # Set temp input to text
            m.setValue(text, m.get_backwards_reasoning("temp_input", "name"))
            m.set_backwards_reasoning("temp_input", "", "") # Then, clear temp input
        return m.optimization(targetname, m.get_backwards_reasoning("target", "value"), varname, 'max')
    # End general backward reasoning

    # What if reasoning
    if contains_word(text.lower(), 'what if'):
        try:
            var_prop =  m.extract_prop_from_string(text)
            target_prop = m.extract_value_from_string(var_prop["remaining_string"], var_prop["name"])
        except:
            return no_valid_prop(m)
        if var_prop["name"] == '':
            return no_valid_prop(m)
        # Check which one is th
        print("remaining:" + var_prop["remaining_string"])
        print("target prop: " + target_prop)
        return m.what_if_reasoning(var_prop["name"], target_prop)

    # partial decision making
    if text == "break":
        print("enter partial dm")
        res = m.partial_decision_making()
        return res

    # Reasoning towards outcome
    if contains_word(text.lower(), 'how to get'):
        answer = ''
        rules, inter = m.seek_goal(text)
        print(rules)
        print(inter)
        if rules == 'no rules' and inter == 'no inter':
            print("no valid prop")
            return no_valid_prop(m)
        if inter == 'no inter for prop':
            return "Value not recognized, please use one of the following:<br/> " + m.model.possible_values_of(rules).replace(',', '<br/>')
        for rule in rules:
            answer += str(rule).replace("['", "").replace("']", "").replace("'", "").replace("WHENWHEN", "WHEN") + "<br/><br/>"
        return answer

    # Sensitivity
    # After getting an outcome, the user might want to know what inputs he/she can change without changing the outcome 
    if text.lower() in  ('show all paths', 'all paths', 'what can I change to keep this outcome?', 'other options for this outcome', 'other paths'):
        answer = 'The same outcome can be obtained in these cases:<br/><br/>'
        rules, inter = m.sensitivity_analysis()
        for i in inter:
            answer += i['prop'] + ' can be: '
            for n in range (0, len(i['values'])):
                if n < len(i["values"]) - 1:
                    answer += "\t\t" + i['values'][n] + ",<br/>"
                else:
                    answer += "\t\t" + i['values'][n] + "<br/><br/>"

        for rule in rules:
            answer += str(rule).split('THEN')[0].replace("AND", "<br/>AND").replace("['", "").replace("']", "").replace("'", "").replace("WHENWHEN", "WHEN").replace("WHEN", "WHEN<br/>") + "<br/><br/>"
        return answer

    # Explain decision
    elif text.lower() in ("why", "why?", "explain"):
        try:
            return str(m.explain_solution()) + '<br/>' + buttons.create_button("exit", "Quit Model")
        except Exception as e:
            print(e)
            return "I'm sorry I cannot explain the reasoning at this point."
    else:
        # If there is a pending variable (we expect an input value for the pending variable)
        if m.getPending() != "":
            try:
                # All input is decapitalized, so capitalize relevant input attributes again if needed
                if capitalize(text,0,1) in m.get_possible_values(m.getPending()):
                    text = capitalize(text,0,1)

                # Input is unkown
                print("text is " + text.lower())
                if text.lower() in ("?", "i don't know", "ik weet het niet", "i do not know", "don't know", "dunno"):
                    text = "?"
                    m.unknown_information(m.getPending())
                
                # Convert to boolean input if boolean is expected
                print(m.getPendingType())
                if m.getPendingType() == None:
                    if text.lower() in ("yes", "true", "t", "y", "1", "yep"):
                        text = "true"
                    if text.lower() in ("no", "false", "f", "n", "0", "nope"):
                        text = "false"

                set_msg = ''
                if(text != "_stay_"):
                    set_msg = m.setValue(text)
                if set_msg == 'error':
                    return m.not_valid(text)
                
                return set_msg + str(m.getUnsolvedIntermediary())
            except:
                return m.not_valid(text)
        else:
            intermediaries = m.getUnsolvedIntermediary()
            return str(intermediaries)