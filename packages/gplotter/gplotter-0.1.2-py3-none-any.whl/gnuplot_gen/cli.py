import argparse
import os
from .gnuplot_template import generate_gnuplot_script
from .utils import detect_headers_and_legends

def main():
    parser = argparse.ArgumentParser(description="Auto GNUPlot script generator")
    parser.add_argument("input", help="Input data file")
    parser.add_argument("-o", "--output", help="Output plot file (e.g., output.eps)", default="output")
    parser.add_argument("--font_size", type=int, default=14, help="Font size")
    parser.add_argument("--xlabel", help="X-axis label")
    parser.add_argument("--ylabel", help="Y-axis label")
    parser.add_argument("--title", help="Plot title")
    parser.add_argument("--plot_type", choices=["line", "histogram", "scatter", "points", "boxes"], default="line")
    parser.add_argument("--filetype", choices=["eps", "pdf", "png", "svg"], default="eps")
    parser.add_argument("--columns", nargs="+", type=int, help="Columns to plot (1-based index)")
    parser.add_argument("--legends", nargs="+", help="Legend labels")
    parser.add_argument("--script_only", action="store_true", help="Only generate .p script")
    parser.add_argument("--key_pos", default="top right", help="Position of the legend key")
    parser.add_argument("--left_margin", type=float, default=None, help="Left margin in inches")
    parser.add_argument("--right_margin", type=float, default=None, help="Right margin in inches")
    parser.add_argument("--top_margin", type=float, default=None, help="Top margin in inches")
    parser.add_argument("--bottom_margin", type=float, default=None, help="Bottom margin in inches")
    parser.add_argument("--xl_off_x", type=float, default=None, help="X offset for X label")
    parser.add_argument("--xl_off_y", type=float, default=None, help="Y offset for X label")
    parser.add_argument("--yl_off_x", type=float, default=None, help="X offset for Y label")
    parser.add_argument("--yl_off_y", type=float, default=None, help="Y offset for Y label")
    parser.add_argument("--xrange_min", type=float, help="Minimum X range")
    parser.add_argument("--xrange_max", type=float, help="Maximum X range")
    parser.add_argument("--yrange_min", type=float, help="Minimum Y range")
    parser.add_argument("--yrange_max", type=float, help="Maximum Y range")
    parser.add_argument("--y_x_diff", type=float, help="Difference between Y and X values for histogram")
    parser.add_argument("--colors", nargs="+", help="Colors for the plot lines/box")
    parser.add_argument("--width", type=float, default=8, help="Width of the plot in inches")
    parser.add_argument("--hight", type=float, default=6, help="Height of the plot in inches")
    parser.add_argument("--font", default="Helvetica", help="Font type for the plot")
    parser.add_argument("--rotate", type=int, default=None, help="Rotation angle for the plot (in degrees)")
    parser.add_argument("--line_type", action="store_true", help="add line type increemently with number")
    parser.add_argument("--point_type", type=int, default=None, help="Point type for the plot")
    parser.add_argument("--line_width", type=int, default=2, help="Line width for the plot")
    parser.add_argument("--left_in_off", type=float, default=None, help="Left inside offset for the plot")
    parser.add_argument("--right_in_off", type=float, default=None, help="Right inside offset for the plot")
    parser.add_argument("--bottom_in_off", type=float, default=None, help="Bottom inside offset for the plot")
    parser.add_argument("--top_in_off", type=float, default=None, help="Top inside offset for the plot")
    parser.add_argument("--point_size", type=float, default=None, help="set point size for line plot")
    args = parser.parse_args()

    columns = args.columns
    legends = args.legends
    if not columns or not legends:
        auto_columns, auto_legends = detect_headers_and_legends(args.input)
        columns = columns or auto_columns
        legends = legends or auto_legends
        if columns and legends:
            print(f"[auto] Detected columns: {columns}, legends: {legends}")

    script = generate_gnuplot_script(
        input_file=args.input,
        output_file=args.output,
        plot_type=args.plot_type,
        font_size=args.font_size,
        xlabel=args.xlabel,
        ylabel=args.ylabel,
        title=args.title,
        columns=columns,
        legends=legends,
        colors=args.colors,
        terminal_type=args.filetype,
        key_pos=args.key_pos,
        left_margin=args.left_margin,
        right_margin=args.right_margin,
        top_margin=args.top_margin,
        bottom_margin=args.bottom_margin,
        xl_off_x=args.xl_off_x,
        xl_off_y=args.xl_off_y,
        yl_off_x=args.yl_off_x,
        yl_off_y=args.yl_off_y,
        xrange_min=args.xrange_min,
        xrange_max=args.xrange_max,
        yrange_min=args.yrange_min,
        yrange_max=args.yrange_max,
        y_x_diff=args.y_x_diff,
        font=args.font,
        width=args.width,
        hight=args.hight,
        rotate=args.rotate,
        line_type=args.line_type,
        point_type=args.point_type,
        line_width=args.line_width,
        left_in_off=args.left_in_off,
        right_in_off=args.right_in_off,
        bottom_in_off=args.bottom_in_off,
        top_in_off=args.top_in_off,
        point_size=args.point_size
    )

    script_path = args.output + ".p"
    with open(script_path, "w") as f:
        f.write(script)

    print(f"Generated script at: {script_path}")
    if not args.script_only:
        os.system(f"gnuplot {script_path}")

