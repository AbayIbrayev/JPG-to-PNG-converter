import os

from PIL import Image, ImageChops, ImageFilter


# This could be a more complex function that removes the background from an image
# For simplicity, this function just removes the background based on a tolerance value using flood fill algorithm
def remove_background(img, tolerance=200):
    # Convert to RGBA (if not already in that mode)
    img = img.convert("RGBA")
    width, height = img.size

    # Get image data
    data = img.load()

    # Create a mask image for flood fill
    mask = Image.new("L", (width, height), 0)
    mask_data = mask.load()

    # Flood fill from the corners to identify the background
    def flood_fill(x, y):
        stack = [(x, y)]
        visited = set()
        while stack:
            x, y = stack.pop()
            if (x, y) in visited:
                continue
            visited.add((x, y))
            if x < 0 or x >= width or y < 0 or y >= height:
                continue
            if all(channel > tolerance for channel in data[x, y][:3]):
                mask_data[x, y] = 255
                stack.extend([(x + dx, y + dy)
                             for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]])

    # Start flood fill from each corner
    for corner in [(0, 0), (0, height - 1), (width - 1, 0), (width - 1, height - 1)]:
        flood_fill(*corner)

    # Blur the mask to handle small empty spaces
    mask = mask.filter(ImageFilter.GaussianBlur(1))

    # Invert the mask
    mask = ImageChops.invert(mask)

    # Apply the mask to the image
    img.putalpha(mask)

    return img


def convert_images_to_png(input_directory, output_directory=None):
    # Use the same directory if no output directory is provided
    if output_directory is None:
        output_directory = input_directory

    # Create the output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    # Iterate through all files in the input directory
    for filename in os.listdir(input_directory):
        input_path = os.path.join(input_directory, filename)

        # Check if the file is an image
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff')):
            try:
                # Open the image
                with Image.open(input_path) as img:
                    # Remove the original extension and replace with '.png'
                    base_name = os.path.splitext(filename)[0]
                    output_path = os.path.join(
                        output_directory, f"{base_name}.png")

                    # Convert and save as PNG
                    remove_background(img).save(output_path, format='PNG')
                    print(f"Converted {filename} to {output_path}")
            except Exception as e:
                print(f"Failed to convert {filename}: {e}")


# Example usage
input_dir = 'images'
output_dir = 'converted_images'  # Use None to save in the same directory
convert_images_to_png(input_dir, output_dir)
