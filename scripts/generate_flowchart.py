from PIL import Image, ImageDraw, ImageFont
import os

def create_flowchart(output_path):
    width, height = 800, 300
    img = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    boxes = [
        {"label": "Data Input", "pos": (50, 100, 150, 150), "color": "#E3F2FD"},
        {"label": "Isolation Forest\n(Outlier Removal)", "pos": (200, 100, 350, 150), "color": "#FFF9C4"},
        {"label": "HDBSCAN\n(Density Clustering)", "pos": (400, 100, 550, 150), "color": "#C8E6C9"},
        {"label": "K-Means\n(Centroid Optimization)", "pos": (600, 100, 750, 150), "color": "#FFCCBC"}
    ]

    for b in boxes:
        draw.rectangle(b["pos"], fill=b["color"], outline="black", width=2)
        # Calculate text position roughly (since we don't have font metrics without loading a ttf)
        x0, y0, x1, y1 = b["pos"]
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        lines = b["label"].split("\n")
        y_text = cy - (len(lines) * 8)
        for line in lines:
            # using default font, it's small, let's scale it slightly by drawing text
            draw.text((cx - len(line)*3, y_text), line, fill="black")
            y_text += 15

    # Draw arrows
    arrows = [
        ((150, 125), (200, 125)),
        ((350, 125), (400, 125)),
        ((550, 125), (600, 125))
    ]
    for start, end in arrows:
        draw.line([start, end], fill="black", width=2)
        # arrowhead
        draw.polygon([end, (end[0]-10, end[1]-5), (end[0]-10, end[1]+5)], fill="black")

    img.save(output_path)
    print(f"Flowchart saved to {output_path}")

out_path = r"D:\Kuliyeah\sem 6\Project HKI SENUWU\assets\flowchart_hibrida.png"
create_flowchart(out_path)
