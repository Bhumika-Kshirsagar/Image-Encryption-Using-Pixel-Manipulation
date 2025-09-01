from PIL import Image
import numpy as np

# Create a simple 256x256 gradient image
width, height = 256, 256
array = np.zeros((height, width, 3), dtype=np.uint8)

for y in range(height):
    for x in range(width):
        array[y, x] = [x % 256, y % 256, (x*y) % 256]

img = Image.fromarray(array)
img.save("sample.png")
print("✅ sample.png created successfully!")

