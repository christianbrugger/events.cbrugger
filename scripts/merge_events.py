import re
import argparse
import json

import lib

def merge_events(input_basename, input_chunks, output_chunks):
    assert input_chunks > 0
    assert output_chunks > 0

    # import
    all_events = {}
    try:
        for i in range(input_chunks):
            filename = "{}{}.txt".format(input_basename, i)
            print("Opening file", filename)

            with open(filename) as file:
                events = json.load(file)
            all_events.update(events)
    except FileNotFoundError:
        print("ERROR: One or more files not available. Quitting")
        return

    print("Imported {} events.".format(len(all_events)))

    assert len(all_events) > 0

    # export
    for i, chunk in enumerate(lib.split(sorted(all_events), output_chunks)):
        filepath = lib.tagged_filename("merged{}.txt".format(i))
        chunk_data = {id_: all_events[id_] for id_ in chunk}

        with open(filepath, 'w') as file:
            json.dump(chunk_data, file, indent=4, sort_keys=True)

        print("written", filepath, flush=True)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_basename", type=str, help="beginning of filename with event ids, excluding id and extension")
    parser.add_argument("--input_chunks", type=int, help="number of input files", default=1)
    parser.add_argument("--output_chunks", type=int, help="number of input files", default=1)
    args = parser.parse_args()
    print("input_basename: {}".format(args.input_basename))
    print("input_chunks: {}".format(args.input_chunks))
    print("output_chunks: {}".format(args.output_chunks))
    return args


def main():
    args = get_args()
    merge_events(args.input_basename, args.input_chunks, args.output_chunks)


if __name__ == "__main__":
    main()
