"""Script to pre-label roles in the dataset."""
from pathlib import Path

import pandas as pd
import spacy
from prodigy.components.loaders import JSONL
from prodigy.models.matcher import PatternMatcher


PATH_INPUT_RAW = Path('input', 'roles.csv')
PATH_INPUT_PROC = Path('input', 'roles.jsonl')

PATH_PATTERNS = Path('patterns.jsonl')

PATH_OUTPUT_UNLAB = Path('input', 'roles_unlabeled.jsonl')
PATH_OUTPUT_LAB = Path('output', 'roles_labeled.csv')


if __name__ == '__main__':

    # load role strings and normalize
    df = pd.read_csv(PATH_INPUT_RAW, sep=';', index_col=0).sample(frac = 1)
    df['text'] = df['speaker'].str.replace(r'\.|-', ' ', regex=True).replace(r'\s{1,}', ' ', regex=True)
    with PATH_INPUT_PROC.open('w', encoding='utf-8') as f:
        print(PATH_INPUT_PROC.absolute())
        f.write(df.to_json(orient='records', lines=True))

    # label roles
    nlp = spacy.load('en_core_web_lg')
    matcher = PatternMatcher(nlp, combine_matches=True, all_examples=True).from_disk(PATH_PATTERNS)
    stream = JSONL(PATH_INPUT_PROC)
    stream = matcher(stream)
    labels = pd.DataFrame.from_records([example[1] for example in stream])
    labels['labels'] = labels['spans'].map(lambda x: None if (len(x) == 0) else set([i['label'] for i in x]))

    # save UNLABELED roles for further annotation in prodigy
    df = pd.merge(df, labels[['text', 'labels']], how='left', on='text')
    df = df[df['labels'].isna()]
    with PATH_OUTPUT_UNLAB.open('w', encoding='utf-8') as f:
        f.write(df.to_json(orient='records', lines=True))

    # save LABELED roles for descriptive analyses
    labels['labels'] = labels['labels'].map(lambda x: ', '.join(x) if x else None)
    labels[['speaker', 'labels']].to_csv(PATH_OUTPUT_LAB, sep=';')
