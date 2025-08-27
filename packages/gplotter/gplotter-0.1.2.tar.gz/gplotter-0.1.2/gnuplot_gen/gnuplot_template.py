def generate_gnuplot_script(
    input_file,
    output_file="output.eps",
    plot_type="line",
    font_size=14,
    xlabel=None,
    ylabel=None,
    title=None,
    columns=None,
    legends=None,
    colors=None,
    terminal_type="eps",
    key_pos="top right",
    left_margin=None,
    right_margin=None,
    top_margin=None,
    bottom_margin=None,
    xl_off_x=None,
    xl_off_y=None,
    yl_off_x=None,
    yl_off_y=None,
    xrange_min=None,
    xrange_max=None,
    yrange_min=None,
    yrange_max=None,
    y_x_diff=None,
    font="Helvetica",
    width=8,
    hight=6,
    rotate=None,
    line_type=False,
    point_type=None,
    line_width=2,
    left_in_off=None,
    right_in_off=None,
    bottom_in_off=None,
    top_in_off=None,
    point_size=None

):
    if not columns:
        columns = [2]
    if not legends:
        legends = [f"Col {i}" for i in columns]

    terminal_dict = {
        "eps": f"set terminal postscript eps enhanced color solid font '{font},{font_size}' size {width},{hight}",
        "pdf": f"set terminal pdf enhanced font 'Helvetica,{font_size}'",
        "png": f"set terminal pngcairo enhanced font 'Helvetica,{font_size}'",
        "svg": f"set terminal svg enhanced font 'Helvetica,{font_size}'"
    }

    if terminal_type not in terminal_dict:
        raise ValueError(f"Unsupported terminal type: {terminal_type}")

    script = (
        f"{terminal_dict[terminal_type]}\n"
        f"set output '{output_file}.{terminal_type}'\n"
        # f"set grid\n"
        # f"set xlabel '{xlabel or 'X'}' offset {xl_off_x},{xl_off_y}\n"
        # f"set ylabel '{ylabel or 'Y'}' offset {yl_off_x},{yl_off_y}\n"
        # f"set xlabel '{xlabel}'{f' offset {xl_off_x},{xl_off_y}' if xl_off_x is not None and xl_off_y is not None else ''}\n"
        # f"set ylabel '{ylabel}'{f' offset {yl_off_x},{yl_off_y}' if yl_off_x is not None and yl_off_y is not None else ''}\n"

        # f"set title '{title or plot_type.capitalize()} Plot'\n"
        f"set key {key_pos}\n"
        # f"set lmargin {left_margin}\n"
        # f"set rmargin {right_margin}\n"
        # f"set tmargin {top_margin}\n"
        # f"set bmargin {bottom_margin}\n"
        # f"set xrange [{xrange_min}:{xrange_max}]\n"
        # f"set yrange [{yrange_min}:{yrange_max}]\n"
        # f"set ytics {y_x_diff}\n"
    )

    script += "\n".join(filter(None, [

    f"set lmargin {left_margin}\n" if left_margin is not None else None,
    f"set rmargin {right_margin}\n" if right_margin is not None else None,
    f"set tmargin {top_margin}\n" if top_margin is not None else None,
    f"set bmargin {bottom_margin}\n" if bottom_margin is not None else None,
    f"set xlabel '{xlabel}'\n" if xlabel else None,
    f"set ylabel '{ylabel}'\n" if ylabel else None,
    f"set xlabel '{xlabel}' offset {xl_off_x or 0},{xl_off_y or 0}\n" if xl_off_x is not None or xl_off_y is not None else None,
    f"set ylabel '{ylabel}' offset {yl_off_x or 0},{yl_off_y or 0}\n" if yl_off_x is not None or yl_off_y is not None else None,
    f"set xrange [{xrange_min or ''}:{xrange_max or ''}]\n" if xrange_min is not None or xrange_max is not None else None,
    f"set yrange [{yrange_min or ''}:{yrange_max or ''}]\n" if yrange_min is not None or yrange_max is not None else None,
    f"set ytics {y_x_diff}\n" if y_x_diff is not None else None,
    f"set xtics rotate by {rotate}\n" if rotate is not None else None,
    f"set title '{title}'\n" if title else None,
    f"set offsets {left_in_off or 0},{right_in_off or 0},{bottom_in_off or 0},{top_in_off or 0}\n" if left_in_off is not None or right_in_off is not None or bottom_in_off is not None or top_in_off is not None else None,
    f"set pointsize '{point_size}'\n" if point_size is not None else None,
    ]))


    # Plot style additions
    if plot_type == "histogram":
        script += "set style data histograms\nset style fill solid 1.00 border lt -1\nset boxwidth 0.9 absolute\n"
    elif plot_type == "boxes":
        script += "set style fill solid\n"
    elif plot_type == "line":
        script += "set style data linespoints\nset style fill solid 1.0 border -1\n"
    # Generate plot commands
    plot_cmds = []
    for i, col in enumerate(columns):
        title_str = legends[i] if i < len(legends) else f"Col {col}"
        color_str = f"lc rgb '{colors[i]}'" if colors and i < len(colors) else ""
        using_str = f"using {col}:xtic(1)" if plot_type == "histogram" else f"using ($0):{col}:xtic(1)"
        line_type_str = f"lt {i + 1}" if line_type and plot_type == "line" else ""
        line_point_type_str = f"pt {point_type}" if point_type and plot_type == "line" else ""
        line_width_str = f"lw {line_width}" if line_width and plot_type == "line" else ""
        with_what = {
            "line": "with linespoints",
            "scatter": "with points pointtype 7",
            "points": "with points",
            "histogram": "",
            "boxes": "with boxes"
        }[plot_type]
        plot_cmds.append(f"'{input_file}' {using_str} title '{title_str}' {with_what} {color_str} {line_type_str} {line_point_type_str} {line_width_str}")

    script += "plot \\\n    " + ", \\\n    ".join(plot_cmds) + "\n"
    return script

