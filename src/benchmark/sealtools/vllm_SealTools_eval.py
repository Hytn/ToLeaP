# Copyright 2024 fairyshine/Seal-Tools
# Modifications Copyright 2024 BodhiAgent
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import os
import re

def transform_output_format(dataset_name, output_text):
    match dataset_name:
        case "TableEE":
            try:
                api_match = re.search(r"\[[^\[\]]*\]", output_text)
                if api_match is None:
                    all_matches = re.findall(r"\{[^{}]*\}", output_text)
                    structured = []
                    for item in all_matches:
                        try:
                            structured.append(json.loads(item))
                        except:
                            pass
                else:
                    structured = json.loads(api_match.group())
                if not isinstance(structured, list):
                    structured = [structured]
                predictions = []
                for entry in structured:
                    if isinstance(entry, dict):
                        # map Chinese key to English
                        entry['event_type'] = entry.pop('event_type', None)
                        predictions.append(entry)
                return predictions
            except:
                return -1

        case '14lap' | '14res' | '15res' | '16res':   # ABSA
            text = re.sub("'", '"', output_text)
            parts = re.split(r'\n\n', text)
            try:
                pattern = re.compile(r'\[[^\[\]]*\]')
                candidates = []
                for part in parts:
                    flat = re.sub(r"\n", "", part)
                    candidates.extend(pattern.findall(flat))

                # bring first non-empty
                for i, cand in enumerate(candidates):
                    if cand != '[]':
                        candidates[0], candidates[i] = candidates[i], candidates[0]
                        break
                if not candidates:
                    return -1

                for cand in candidates:
                    try:
                        items = json.loads(cand)
                        # filter invalid
                        valid = True
                        for item in items:
                            if (
                                item.get('Sentiment', -1) == -1 or
                                item.get('Aspect_Term', -1) == -1 or
                                item.get('Opinion_Term', -1) == -1
                            ):
                                valid = False
                                break
                        if valid:
                            return items
                    except:
                        continue
                return -1
            except:
                return -1

        case 'ag_news' | 'MedQA' | 'MRPC' | 'SNLI':  # Classification
            text = re.sub("'", '"', output_text)
            parts = re.split(r'\n\n', text)
            try:
                # try object then list
                obj_pattern = re.compile(r'\{[^\{\}]*\}')
                list_pattern = re.compile(r'\[[^\[\]]*\]')
                objs = []
                lists = []
                for part in parts:
                    flat = re.sub(r"\n", "", part)
                    objs.extend(obj_pattern.findall(flat))
                    lists.extend(list_pattern.findall(flat))

                if objs:
                    for s in objs:
                        snippet = s[1:-1]
                        try:
                            return json.loads(snippet)
                        except:
                            continue
                    return -1
                elif lists:
                    for s in lists:
                        try:
                            return json.loads(f'"{s}"')
                        except:
                            continue
                    return -1
                else:
                    return -1
            except:
                return -1

        case 'MIT_MOVIE_Review' | 'MIT_Restaurant_Review' | 'NCBIdisease' | 'ontoNotes5':  # NER
            text = re.sub("'", '"', output_text)
            parts = re.split(r'\n\n', text)
            try:
                pattern = re.compile(r'\[[^\[\]]*\]')
                candidates = []
                for part in parts:
                    flat = re.sub(r"\n", "", part)
                    candidates.extend(pattern.findall(flat))

                for i, cand in enumerate(candidates):
                    if cand != '[]':
                        candidates[0], candidates[i] = candidates[i], candidates[0]
                        break

                for cand in candidates:
                    try:
                        items = json.loads(cand)
                        valid = True
                        for entry in items:
                            if entry.get('text', -1) == -1 or entry.get('type', -1) == -1:
                                valid = False
                                break
                        if valid:
                            return items
                    except:
                        continue
                return -1
            except:
                return -1

        case 'scierc' | 'semeval' | 'WebNLG':  # RE
            text = re.sub("'", '"', output_text)
            parts = re.split(r'\n\n', text)
            try:
                pattern = re.compile(r'\[[^\[\]]*\]')
                candidates = []
                for part in parts:
                    flat = re.sub(r"\n", "", part)
                    candidates.extend(pattern.findall(flat))

                for i, cand in enumerate(candidates):
                    if cand != '[]':
                        candidates[0], candidates[i] = candidates[i], candidates[0]
                        break

                for cand in candidates:
                    try:
                        items = json.loads(cand)
                        valid = True
                        for entry in items:
                            if (
                                entry.get('relation', -1) == -1 or
                                entry.get('head', -1) == -1 or
                                entry.get('tail', -1) == -1
                            ):
                                valid = False
                                break
                        if valid:
                            return items
                    except:
                        continue
                return -1
            except:
                return -1

        case 'ace05-evt' | 'casie' | 'PHEE':  # EE
            text = re.sub("'", '"', output_text)
            parts = re.split(r'\n\n', text)
            try:
                pattern = re.compile(r'\[\{.*\}\]')
                candidates = []
                for part in parts:
                    flat = re.sub(r"\n", "", part)
                    candidates.extend(pattern.findall(flat))

                for i, cand in enumerate(candidates):
                    if cand != '[]':
                        candidates[0], candidates[i] = candidates[i], candidates[0]

                if not candidates:
                    candidates = re.compile(r'\[[^\[\]]*\]').findall(text)

                for cand in candidates:
                    try:
                        items = json.loads(cand)
                        valid = True
                        for entry in items:
                            if (
                                entry.get('event_type', -1) == -1 or
                                entry.get('trigger', -1) == -1 or
                                entry.get('args', -1) == -1
                            ):
                                valid = False
                                break
                            for arg in entry['args']:
                                if arg.get('role', -1) == -1 or arg.get('text', -1) == -1:
                                    valid = False
                                    break
                            if not valid:
                                break
                        if valid:
                            return items
                    except:
                        continue
                return -1
            except:
                return -1

        case 'api_we_instructed':
            try:
                pattern = re.compile(r"\{.*\}", re.DOTALL)
                match_obj = re.search(pattern, output_text)
                if match_obj:
                    return json.loads(match_obj.group(0))
                else:
                    return -1
            except:
                return -1

        case 'ToolLearning':
            def find_matching_bracket(text, start_pos):
                depth = -1
                for i in range(start_pos + 1, len(text)):
                    if text[i] == '[': depth -= 1
                    elif text[i] == ']': depth += 1
                    if depth == 0: return i
                return -1

            clean = re.sub("'", '"', output_text).replace("\n", "")
            search = re.search(r"\[\s*\{\s*\"api\"", clean, re.DOTALL)
            if not search:
                return -1

            s, _ = search.span()
            e = find_matching_bracket(clean, s)
            snippet = clean[s:e+1]
            if "api" in snippet and "response" in snippet:
                if "parameters" in snippet or "arguments" in snippet:
                    try:
                        return json.loads(snippet)
                    except:
                        return -1
            return -1

        case _:
            print("ERROR: unsupported dataset")
            return -1

def transform_thought_output_format(dataset_name, output_text):
    if dataset_name != 'ToolLearning':
        print("ERROR: unsupported dataset")
        return -1

    def find_matching_bracket(text, start_pos):
        depth = -1
        for i in range(start_pos + 1, len(text)):
            if text[i] == '[': depth -= 1
            elif text[i] == ']': depth += 1
            if depth == 0: return i
        return -1

    if "Output:" in output_text:
        clean = output_text.split("Output:",1)[1]
    else:
        return -1

    clean = re.sub("'", '"', clean).replace("\n", "")
    search = re.search(r"\[\s*\{\s*\"api\"", clean, re.DOTALL)
    if not search:
        return -1

    s, _ = search.span()
    e = find_matching_bracket(clean, s)
    snippet = clean[s:e+1]
    if "api" in snippet and "response" in snippet:
        if "parameters" in snippet or "arguments" in snippet:
            try:
                return json.loads(snippet)
            except:
                return -1
    return -1

def write_jsonl(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        for entry in data:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def write_json(path, data, indent=0):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)

def read_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def list_json_files(directory):
    return [fn for fn in os.listdir(directory) if fn.endswith('.json')]

def read_jsonl(path):
    with open(path, 'r', encoding='utf-8') as f:
        return [json.loads(line) for line in f]

def calculate_score_toollearning(data_path):
    dataset = read_jsonl(data_path)
    result = {}
    error_cases = []

    correct_format = 0
    correct_api = 0
    pred_api = 0
    gold_api = 0
    correct_param = 0
    pred_param = 0
    gold_param = 0

    error_counts = {
        "Format_Error": 0,
        "Missing_API": 0,
        "Wrong_API": 0,
        "Missing_Parameter": 0,
        "Wrong_Parameter_Value": 0
    }

    for entry in dataset:
        gold = json.loads(json.dumps(eval(entry['gold_data']["conversations"][1]["value"])))
        gold_api += len(gold)
        for api in gold:
            gold_param += len(api['parameters'])

        if entry['predict'][0] != -1:
            predict = entry['predict'][0]
            correct_format += 1
            entry_ok = True

            for api_pred in predict:
                if "api" in api_pred:
                    pred_api += 1
                    params = api_pred.get("parameters", {}) or api_pred.get("arguments", {})
                    if isinstance(params, dict):
                        pred_param += len(params)
                    # find matching gold index
                    idx = next((i for i, g in enumerate(gold) if g["api"] == api_pred["api"]), -1)
                    if idx >= 0:
                        correct_api += 1
                        params_ok = True
                        for pname, pval in params.items():
                            if pname in gold[idx]["parameters"] and str(pval) == str(gold[idx]["parameters"][pname]):
                                correct_param += 1
                            else:
                                params_ok = False
                                if pname not in gold[idx]["parameters"]:
                                    error_counts["Missing_Parameter"] += 1
                                else:
                                    error_counts["Wrong_Parameter_Value"] += 1
                        if not params_ok:
                            entry_ok = False
                    else:
                        entry_ok = False
                        error_counts["Wrong_API"] += 1
                else:
                    entry_ok = False
                    error_counts["Missing_API"] += 1

            if not entry_ok:
                error_cases.append(entry)
        else:
            error_cases.append(entry)
            error_counts["Format_Error"] += 1

    n = len(dataset)
    if correct_format > 0:
        result["Format_Rate"] = round(correct_format / n * 100, 2)
    if correct_api * pred_api * gold_api > 0:
        p_api = correct_api / pred_api
        r_api = correct_api / gold_api
        result["Precision_API"] = round(p_api * 100, 2)
        result["Recall_API"]    = round(r_api * 100, 2)
        result["F1_API"]        = round(2 * p_api * r_api / (p_api + r_api) * 100, 2)
    if correct_param * pred_param * gold_param > 0:
        p_param = correct_param / pred_param
        r_param = correct_param / gold_param
        result["Precision_Param"] = round(p_param * 100, 2)
        result["Recall_Param"]    = round(r_param * 100, 2)
        result["F1_Param"]        = round(2 * p_param * r_param / (p_param + r_param) * 100, 2)

    # result["Error_Type_Counts"] = error_counts
    return result, error_cases

def raw_to_pred(raw_path, label_path):
    raw = read_json(raw_path)
    labels = read_json(label_path)
    output = []
    for r, l in zip(raw, labels):
        pred = transform_output_format("ToolLearning", r)
        output.append({'id': l["id"], 'predict': [pred], 'gold_data': l})
    return output

def raw_cot_to_pred(raw_path, label_path):
    raw = read_json(raw_path)
    labels = read_json(label_path)
    output = []
    for r, l in zip(raw, labels):
        pred = transform_thought_output_format("ToolLearning", r)
        output.append({'id': l["id"], 'predict': [pred], 'gold_data': l})
    return output
