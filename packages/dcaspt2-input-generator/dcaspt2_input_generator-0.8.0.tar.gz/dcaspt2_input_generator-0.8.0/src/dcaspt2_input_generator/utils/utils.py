def create_ras_str(ras_list: "list[int]") -> str:
    # ras_str: if the consecutive numbers are found, replace them with ".."
    # (e.g.) [1, 2, 3, 4, 5, 6, 7, 8, 11, 12] -> "1..8, 11..12"
    # Return empty string if ras_list is empty
    if not ras_list:
        return ""
    # if ras_list contains negative or zero, raise an error
    if any(i <= 0 for i in ras_list):
        msg = "ras_list must contain only positive integers"
        raise ValueError(msg)
    ranges: "list[str]" = []
    start = ras_list[0]
    end = ras_list[0]

    for i in range(1, len(ras_list)):
        if ras_list[i] == end + 1:  # consecutive numbers
            end = ras_list[i]
        else:  # not consecutive numbers
            if start == end:
                ranges.append(str(start))
            else:
                ranges.append(f"{start}..{end}")
            start = ras_list[i]
            end = ras_list[i]

    ranges.append(f"{start}..{end}") if start != end else ranges.append(str(start))
    return ",".join(ranges)


def debug_print(s: str):
    from dcaspt2_input_generator.utils.args import args

    if args.debug:
        print(s)
