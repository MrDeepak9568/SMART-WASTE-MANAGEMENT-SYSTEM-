from PIL import Image, ImageChops

def are_images_equal(img1_path, img2_path):
    img1 = Image.open(img1_path).convert('RGB')
    img2 = Image.open(img2_path).convert('RGB')

    # Check if sizes match
    if img1.size != img2.size:
        return False

    # Compute difference
    diff = ImageChops.difference(img1, img2)

    # If there's no difference, images are identical
    return not diff.getbbox()

# Example usage
result = are_images_equal(r"D:\PYTHON\waste-management-system\image.png", "D:\Arsh Goel.jpg")
print(result)  # True or False

