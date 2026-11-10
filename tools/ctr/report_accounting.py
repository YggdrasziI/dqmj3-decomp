#!/usr/bin/env python3
"""Preserve the project's original byte weights independently of ELF st_size.

Comparison scores and native extents are never changed. Historically the report
weighted functions after removing trailing LDR literals, including mixed pools.
That accounting basis remains fixed when comparison ELF metadata is corrected.
"""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ctr.image import Image, VersionConfig
from ctr.symbols import SymbolTable
from ctr.split import Splitter


def normalize(report, config):
    symbols = SymbolTable.load(config.symbols_path)
    splitter = Splitter(config, Image.load(config), symbols)
    native = {s.name: s for s in symbols}
    for unit in report['units']:
        measures = unit['measures']
        functions = unit.get('functions', [])
        old_total = sum(int(f['size']) for f in functions)
        prior_weight = sum(int(f.get('metadata', {}).get('code_accounting_size', f['size']))
                           for f in functions)
        assert int(measures.get('total_code', 0)) in (old_total, prior_weight), unit['name']
        total = matched = 0
        fuzzy = 0.0
        for function in functions:
            symbol = native[function['name']]
            assert symbol.size, function['name']
            if symbol.is_function:
                info = splitter.analyzer.analyze(symbol.address, symbol.end, symbol.thumb)
                end = symbol.end
                while end - 4 >= symbol.address and end - 4 in info.ldr_pool:
                    end -= 4
                if (symbol.thumb and end < symbol.end and end - 2 >= symbol.address
                        and end - 2 not in info.code and splitter.image.u16(end - 2) == 0):
                    end -= 2
            else:
                # Data inside .text (a table between functions): objdiff lists it with
                # the functions; it counts for its whole size
                end = symbol.end
            weight = end - symbol.address
            function.setdefault('metadata', {})['code_accounting_size'] = weight
            total += weight
            score = function.get('fuzzy_match_percent', 0.0)
            fuzzy += weight * score
            if score == 100.0:
                matched += weight
        complete = int(measures.get('complete_code', 0))
        assert complete in (0, old_total, prior_weight), unit['name']
        measures['total_code'] = str(total)
        measures['matched_code'] = str(matched)
        measures['complete_code'] = str(total if complete else 0)
        measures['fuzzy_match_percent'] = fuzzy / total if total else measures.get('fuzzy_match_percent', 100.0)
        percentages(measures)
    aggregate(report['measures'], report['units'])
    for category in report['categories']:
        aggregate(category['measures'], [u for u in report['units']
                  if category['id'] in u.get('metadata', {}).get('progress_categories', [])])


def percentages(measures):
    total = int(measures.get('total_code', 0))
    for name in ('matched_code', 'complete_code'):
        measures[name + '_percent'] = int(measures.get(name, 0)) / total * 100 if total else 100.0


def aggregate(measures, units):
    for name in ('total_code', 'matched_code', 'complete_code'):
        measures[name] = str(sum(int(u['measures'].get(name, 0)) for u in units))
    total = int(measures['total_code'])
    measures['fuzzy_match_percent'] = (sum(int(u['measures']['total_code'])
        * u['measures']['fuzzy_match_percent'] for u in units) / total if total else 100.0)
    percentages(measures)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('config', type=Path)
    parser.add_argument('report', type=Path)
    parser.add_argument('--standard-output', type=Path, help='Preserve the unmodified objdiff report before historical normalization')
    args = parser.parse_args()
    original = args.report.read_bytes()
    if args.standard_output is not None:
        assert args.standard_output.resolve() != args.report.resolve()
        args.standard_output.parent.mkdir(parents=True, exist_ok=True)
        args.standard_output.write_bytes(original)
    report = json.loads(original)
    normalize(report, VersionConfig(args.config))
    args.report.write_text(json.dumps(report, indent=2) + '\n')
