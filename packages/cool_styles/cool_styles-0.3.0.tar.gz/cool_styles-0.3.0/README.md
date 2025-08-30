# Cool Styles for Matplotlib

A collection of carefully crafted, visually appealing matplotlib styles for your data visualization needs.

## Installation

At the moment the package is not yet on pypi.
// ```bash
// pip install cool_styles

## Usage

```python
import matplotlib.pyplot as plt
import cool_styles
import numpy as np

# Apply a style
plt.style.use(cool_styles.sealight)

# Create your plot
x = np.linspace(0, 10, 100)
fig, ax = plt.subplots()
ax.plot(x, np.sin(x), label='Sin(x)')
ax.plot(x, np.cos(x), label='Cos(x)')
ax.legend()
ax.set_title('Trigonometric Functions')
ax.set_xlabel('x')
ax.set_ylabel('y')
fig.show()
```

## Available Styles

### Sea Light

A light ocean-inspired theme with varying shades of blue. Features a clean, minimal design with a light background and deep blue text. The color palette consists of different blue hues, making it perfect for water-related data, financial visualizations, or any professional presentation.

![Sea Light](test_images/sealight.png)

### Coastal Harvest

A warm, sophisticated color palette inspired by autumn harbors and coastal towns. This style combines deep navy, burnt orange, golden yellow, sage green, and teal green for a balanced, natural look. Ideal for seasonal data, environmental sciences, or any visualization that benefits from a warm, natural color scheme.

![Coastal Harvest](test_images/coastalarvest.png)

### Charcoal

A bold, modern style with high contrast and clean lines. Features a versatile color palette that includes teal, orange, and yellow accents. Perfect for presentations, reports, and visualizations that need to make a strong visual impact.

![Charcoal](test_images/charcoal.png)

### Forest Dark

A dark woodland-inspired theme with earthy tones and muted contrast. Uses a dark background with forest brown text and an earthy color palette. Excellent for night mode applications, environmental data, or creating a calm visual experience with reduced eye strain.

![Forest Dark](test_images/forestdark.png)

### Forest Light

A light woodland-inspired theme with natural earthy tones. Uses a light parchment background with forest green text and a natural color palette. Great for environmental sciences, agricultural data, or any visualization that benefits from an organic, natural aesthetic.

![Forest Light](test_images/forestlight.png)

### Ivory Grid

A dark theme with prominent grid lines and vibrant color accents. The dark background makes the colorful data elements pop while maintaining readability with light text and grid lines. Perfect for complex visualizations where data clarity against a dark background is preferred.

![Ivory Grid](test_images/ivorygrid.png)

### Golden Peachy

A light theme with warm organce tones. Perfect as a standard theme for your presentations.

![Golden Peachy](test_images/goldenpeachy.png)

## Features

- Golden ratio inspired figure proportions for aesthetically pleasing visualizations
- High DPI settings for crisp rendering
- Carefully selected color palettes for data clarity and visual appeal
- Consistent design elements across all styles
- Optimized for both screen display and print output
- Compatible with various plot types (line plots, scatter plots, histograms, etc.)

## Requirements

- Python ≥ 3.11
- matplotlib ≥ 3.10.5

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
