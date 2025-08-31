import enum
from multiprocessing import Value
from PIL import Image, ImageDraw, ImageFont
import argparse
import numpy as np
import os
from typing import List, Tuple, Optional

# Define the character set, arranged in order from dark to light
ASCII_CHARS = ["@", "#", "$", "%", "?", "*", "*", "+", ";", ":", ",", "."]
COLOR_MODES = ["none", "ansi", "html", "rgb"]
OUTPUT_FORMATS = ["text", "html", "image"]

def get_font_size(image_size: Tuple[int, int], char_size: Tuple[int, int]) -> int:
    """Calculate the appropriate font size based on the image size and character size"""
    width, height = image_size
    char_width, char_height = char_size
    font_width = width // char_width
    font_height = height // char_height
    return min(font_width, font_height)

def resize_image(image: Image.Image, new_width: int, char_aspect: float = 0.5) -> Image.Image:
    """Adjust the character size, considering the aspect ratio of the character."""
    width, height = image.size
    ratio = height / width * char_aspect # Adjust the scale, consider the shape of the characters
    new_height = int(new_width * ratio)
    resized_image = image.resize((new_width, new_height))
    return resized_image

def image_to_ascii(
    image: Image.Image,
    char_set: List[str] = ASCII_CHARS,
    color_mode: str = "none",
    invert: bool = False
    ) -> Tuple[List[str], List[Tuple[int, int, int]]]:
    """Convert images into ASCII characters and color data"""
    if color_mode not in COLOR_MODES:
        raise ValueError(f"Invalid color mode. Choose from {COLOR_MODES}")

    # Convert to RGB mode to get the color information
    rgb_image = image.convert("RGB")
    # Convert to grayscale image for brightness calculation
    gray_image = image.convert("L")

    pixels = list(gray_image.getdata())
    rgb_pixels = list(rgb_image.getdata())

    # invert light
    if invert:
        pixels = [255 - p for p in pixels]

    # Map pixels to characters
    char_range = 256 // len(char_set)
    characters = []
    colors = []

    for i, pixel in enumerate(pixels):
        char_index = min(pixel // char_range, len(char_set) - 1)
        characters.append(char_set[char_index])
        colors.append(rgb_pixels[i])

    return characters, colors

def format_output(
    characters: List[str],
    colors: List[Tuple[int, int, int]],
    width: int,
    output_format: str = "text",
    color_mode: str = "none",
    font_name: str = "Courier",
    font_size: int = 12,
    bg_color: Tuple[int, int, int] = (0, 0, 0)
    ) -> str:
    """Format the output into different formats"""
    pixel_count = len(characters)
    lines = []

    if output_format == "text":
        if color_mode == "ansi":
            for i in range(0, pixel_count, width):
                line_chars = characters[i:i + width]
                line_colors = colors[i:i + width]
                line = []
                for char, color in zip(line_chars, line_colors):
                    r, g, b = color
                    line.append(f"\033[38:2;{r};{g};{b}m{char}\033[0m")
                lines.append("".join(line))
        else:
            for i in range(0, pixel_count, width):
                lines.append("".join(characters[i:i + width]))

    elif output_format == "html":
        html = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            f"<title>ASCII Art</title>",
            "<style>",
            f"body {{background-color: rgb{bg_color}; }}",
            f".ascii {{ font-family: '{font_name}', monospace; font-size: {font_size}px; line-height: 1; white-space: pre; }}",
            "</style>",
            "</head>",
            "<body>",
            "<div class='ascii'>"
            ]

        for i in range(0, pixel_count, width):
            line_chars = characters[i:i + width]
            line_colors = colors[i:i + width]

            if color_mode in ["html", "rgb"]:
                line = []
                for char, color in zip(line_chars, line_colors):
                    r, g, b = color
                    line.append(f"<span style>='color:rgb({r},{g},{b})'>{char}</span>")

                html.append("".join(line))
            else:
                html.append("".join(line_chars))

        html.extend(["</div>","</body>","</html>"])
        return "\n".join(html)

    elif output_format == "image":
        # Create a new image to render ASCII art
        char_width = font_size // 2 # Approximate character width
        img_width = width * char_width
        img_height = (pixel_count // width) * font_size

        img = Image.new("RGB", (img_width, img_height), color=bg_color)
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype(font_name + ".ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()

        x, y = 0, 0
        for i, (char, color) in enumerate(zip(characters, colors)):
            if color_mode != "none":
                draw.text((x, y), char, fill=color, font=font)
            else:
                # Use average brightness as grayscale color
                avg = sum(color) // 3
                draw.text((x, y), char, fill=(avg, avg, avg), font=font)

            x += char_width
            if (i + 1) % width == 0:
                x = 0
                y += font_size

        return img

    return "\n".join(lines)

def main():
    # Create a parameter parser
    parser = argparse.ArgumentParser(description="Turn picture into ASCII art")
    parser.add_argument("--input", "-i", type=str, help="Input the image path")
    parser.add_argument("--width", type=int, default=100, help="Output width of character picture (default 100)")
    parser.add_argument("--chars", type=str, default="".join(ASCII_CHARS), help="Custom character set, arranged from dark to light")
    parser.add_argument("--output", type=str, default="output.txt", help="Output file path (format detected automatically according to the extension)")
    parser.add_argument("--color", type=str, default="none", choices=COLOR_MODES, help="Color modes: none, ansi, html, rgb (default none)")
    parser.add_argument("--format", type=str, default="auto", choices=["auto"] + OUTPUT_FORMATS, help="Output formats: auto, text, html, image (default auto)")
    parser.add_argument("--invert", action="store_true", help="Invert light")
    parser.add_argument("--font", type=str, default="Courier", help="Font name for image output")
    parser.add_argument("--font-size", type=int, default=12, help="Font size for image output")
    parser.add_argument("--bg-color", type=str, default="0,0,0", help="Background color (RGB, comma-separated)")
    parser.add_argument("--char-aspect", type=float, default=0.5, help="Character aspect ratio (default 0.5)")

    args = parser.parse_args()

    # If no input file is provided, prompt the user to enter one.
    if not args.input:
        args.input = input("Please enter the image path: ").strip()
        if not args.input:
            print("Error, the image path must be provided!")
            return 

    # Analyse background color
    try:
        bg_color = tuple(map(int, args.bg_color.split(",")))
        if len(bg_color) != 3:
            raise ValueError
    except:
        bg_color = (0, 0, 0)

    # Determine the output format
    if args.format == "auto":
        ext = os.path.splitext(args.output)[1].lower()
        if ext in [".htm", ".html"]:
            output_format = "html"
        elif ext in [".png", ".jpg", ".jpeg", ".bmp"]:
            output_format = "image"
        else:
            output_format = "text"
    else:
        output_format = args.format

    try:
        # open the picture
        image = Image.open(args.input)

        # adjust the size
        resized_image = resize_image(image, args.width, args.char_aspect)

        # transform to ASCII
        characters, colors = image_to_ascii(
            resized_image,
            char_set=list(args.chars),
            color_mode=args.color,
            invert=args.invert
            )

        # output formattedly
        result = format_output(
            characters, 
            colors, 
            args.width, 
            output_format=output_format,
            color_mode=args.color,
            font_name=args.font,
            font_size=args.font_size,
            bg_color=bg_color
            )

        # save the result
        if output_format == "image":
            result.save(args.output)
            print(f"The picture has been saved to {args.output}")
        else:
            with open(args.output, "w", encoding="utf-8") as f:
                if isinstance(result, str):
                    f.write(result)
                else:
                    f.write(str(result))
            print(f"The file has been saved to {args.output}")

        # If it is in text format and is run in the terminal, display it on the screen
        if output_format == "text" and args.color == "none":
            print("\nPreview: ")
            print(result[:2000] + "..." if len(result) > 2000 else result)

    except FileNotFoundError:
        print(f"Error: file '{args.input}' is not found.")
    except Exception as e:
        print(f"Error occurs: {str(e)}")

if __name__ == "__main__":
    main()