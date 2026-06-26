# texturegen.py
import random
import os
import numpy as np
from PIL import Image
from noise import pnoise2


def generate_texture(
    width=512,
    height=512,
    base_color=(220, 200, 130),
    scale=80,
    octaves=3,
    contrast=0.7,
    seed=None,
    filename="sand.png",
):

    if seed is None:
        seed = random.randint(0, 1000000)

    noise_map = np.zeros((height, width))

    for y in range(height):
        for x in range(width):
            value = pnoise2(
                x / scale,
                y / scale,
                octaves=octaves,
                persistence=0.5,
                lacunarity=2.0,
                repeatx=width,
                repeaty=height,
                base=seed,
            )

            noise_map[y, x] = value

    # Normalize to 0-1
    noise_map -= noise_map.min()
    noise_map /= noise_map.max()

    # Apply contrast
    noise_map = np.clip(
        ((noise_map - 0.5) * contrast) + 0.5,
        0,
        1,
    )

    # Create RGB image
    image = np.zeros((height, width, 3), dtype=np.uint8)

    for i in range(3):
        image[:, :, i] = np.clip(
            base_color[i] * (0.6 + noise_map * 0.8),
            0,
            255,
        )

    img = Image.fromarray(image)

    save_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        filename,
    )

    img.save(save_path)

    print(f"Texture saved to: {save_path}")

    return img


def terminal_mode():
    print("\n=== Perlin Texture Generator ===\n")

    width = int(input("Width [512]: ") or "512")
    height = int(input("Height [512]: ") or "512")

    r = int(input("Base color R [220]: ") or "220")
    g = int(input("Base color G [200]: ") or "200")
    b = int(input("Base color B [130]: ") or "130")

    scale = float(input("Scale [8]: ") or "8")
    octaves = int(input("Octaves [3]: ") or "3")
    contrast = float(input("Contrast [0.7]: ") or "0.7")
    seed = int(input("Seed [101010]: ") or "101010")

    filename = input("Filename [sand.png]: ") or "sand.png"

    generate_texture(
        width=width,
        height=height,
        base_color=(r, g, b),
        scale=scale,
        octaves=octaves,
        contrast=contrast,
        seed=seed,
        filename=filename,
    )


if __name__ == "__main__":
    terminal_mode()
