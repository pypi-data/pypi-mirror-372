# GNUPlot Script Generator

A powerful and flexible Python-based CLI tool to automatically generate GNUPlot scripts from your data files.

This tool supports multiple plot types, auto-detects headers, manages legends, and allows advanced customization like margins, axis labels, offsets, and export formats (PNG, EPS, PDF).

---

## 📦 Installation

```bash
pip install .
````

Make sure your `gnuplot_gen` module is installed in the active environment and accessible via CLI as `gnuplot-gen`.

---

## 🚀 CLI Usage

```bash
gnuplot-gen --input data.csv --plot_type line --output plot.gnu --title "Sample Plot"
```

### Common Arguments

| Argument                        | Description                               |
| ------------------------------- | ----------------------------------------- |
| `--input`                       | Input data file (CSV or TSV)              |
| `--output`                      | Output `.gnu` file                        |
| `--plot_type`                   | Plot type: `line`, `histogram`, `scatter` |
| `--title`                       | Plot title                                |
| `--xlabel`                      | X-axis label                              |
| `--ylabel`                      | Y-axis label                              |
| `--legend`                      | Show legend (`yes` or `no`)               |
| `--font_size`                   | Font size (default: 14)                   |
| `--width`                       | Width of the output plot in inches        |
| `--height`                      | Height of the output plot in inches       |
| `--output_format`               | `png`, `eps`, `pdf`, or `svg`             |
| `--xrange_min` / `--xrange_max` | Limit the X-axis range                    |
| `--yrange_min` / `--yrange_max` | Limit the Y-axis range                    |
| `--y_x_diff`                    | Difference between ytics                  |

---

## 🧠 Features

✅ Auto-detect headers and use as legends
✅ Supports `line`, `histogram`, `scatter` plots
✅ Multiple output formats: PNG, EPS, PDF, SVG
✅ Custom margins, offsets, label positions
✅ Clean and reusable GNUPlot scripts
✅ Easily extendable and modular

---

## 📄 Example

### Input CSV (`example.csv`)

```csv
X,Y1,Y2
1,10,20
2,15,25
3,20,30
```

### Command

```bash
gnuplot-gen --input example.csv --plot_type line --title "My Line Plot" --output plot.gnu
```

This generates a script `plot.gnu` that can be run using:

```bash
gnuplot plot.gnu
```

---

## 🛠 Development

To run locally:

```bash
git clone https://github.com/yourusername/gnuplot-gen.git
cd gnuplot-gen
pip install -e .
gnuplot-gen --help
```

---

## 🤝 Contributing

Feel free to fork the repo and submit pull requests. Suggestions and feature requests are welcome!

---

## 📄 License

This project is licensed under the MIT License.
