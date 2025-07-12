#!/usr/bin/env python3
"""
Robot Logo Generator for SysPilot
Creates robot-style logos inspired by the provided robot image
"""

import os

from PIL import Image, ImageDraw, ImageFont


def create_robot_logo():
    """Create a modern robot-style logo for SysPilot"""

    # Create base image (1024x1024 for high resolution)
    size = 1024
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Color scheme - modern blue/cyan robot theme
    primary_color = (41, 128, 185)  # Blue
    secondary_color = (52, 152, 219)  # Lighter blue
    accent_color = (26, 188, 156)  # Cyan/Teal
    dark_color = (44, 62, 80)  # Dark blue-gray
    light_color = (236, 240, 241)  # Light gray

    center_x, center_y = size // 2, size // 2

    # Robot head (main circle)
    head_radius = size // 3
    draw.ellipse(
        [
            center_x - head_radius,
            center_y - head_radius,
            center_x + head_radius,
            center_y + head_radius,
        ],
        fill=primary_color,
        outline=dark_color,
        width=8,
    )

    # Robot antenna/top element
    antenna_height = size // 8
    antenna_width = size // 20
    draw.rectangle(
        [
            center_x - antenna_width // 2,
            center_y - head_radius - antenna_height,
            center_x + antenna_width // 2,
            center_y - head_radius,
        ],
        fill=dark_color,
    )

    # Antenna tip
    tip_radius = size // 30
    draw.ellipse(
        [
            center_x - tip_radius,
            center_y - head_radius - antenna_height - tip_radius,
            center_x + tip_radius,
            center_y - head_radius - antenna_height + tip_radius,
        ],
        fill=accent_color,
    )

    # Robot eyes
    eye_radius = size // 12
    eye_offset = size // 8

    # Left eye
    draw.ellipse(
        [
            center_x - eye_offset - eye_radius,
            center_y - size // 12 - eye_radius,
            center_x - eye_offset + eye_radius,
            center_y - size // 12 + eye_radius,
        ],
        fill=light_color,
        outline=dark_color,
        width=4,
    )

    # Right eye
    draw.ellipse(
        [
            center_x + eye_offset - eye_radius,
            center_y - size // 12 - eye_radius,
            center_x + eye_offset + eye_radius,
            center_y - size // 12 + eye_radius,
        ],
        fill=light_color,
        outline=dark_color,
        width=4,
    )

    # Eye pupils
    pupil_radius = eye_radius // 3
    draw.ellipse(
        [
            center_x - eye_offset - pupil_radius,
            center_y - size // 12 - pupil_radius,
            center_x - eye_offset + pupil_radius,
            center_y - size // 12 + pupil_radius,
        ],
        fill=accent_color,
    )

    draw.ellipse(
        [
            center_x + eye_offset - pupil_radius,
            center_y - size // 12 - pupil_radius,
            center_x + eye_offset + pupil_radius,
            center_y - size // 12 + pupil_radius,
        ],
        fill=accent_color,
    )

    # Robot mouth/speaker grille
    mouth_width = size // 6
    mouth_height = size // 20
    mouth_y = center_y + size // 8

    # Main mouth rectangle
    draw.rectangle(
        [
            center_x - mouth_width // 2,
            mouth_y - mouth_height // 2,
            center_x + mouth_width // 2,
            mouth_y + mouth_height // 2,
        ],
        fill=dark_color,
        outline=dark_color,
    )

    # Speaker grille lines
    for i in range(5):
        line_x = center_x - mouth_width // 2 + (i + 1) * mouth_width // 6
        draw.line(
            [line_x, mouth_y - mouth_height // 3, line_x, mouth_y + mouth_height // 3],
            fill=secondary_color,
            width=2,
        )

    # Side panels/ears
    panel_width = size // 20
    panel_height = size // 6
    panel_offset = head_radius + size // 20

    # Left panel
    draw.rectangle(
        [
            center_x - panel_offset - panel_width,
            center_y - panel_height // 2,
            center_x - panel_offset,
            center_y + panel_height // 2,
        ],
        fill=secondary_color,
        outline=dark_color,
        width=4,
    )

    # Right panel
    draw.rectangle(
        [
            center_x + panel_offset,
            center_y - panel_height // 2,
            center_x + panel_offset + panel_width,
            center_y + panel_height // 2,
        ],
        fill=secondary_color,
        outline=dark_color,
        width=4,
    )

    # Panel details (small circles)
    detail_radius = size // 80
    for panel_x in [
        center_x - panel_offset - panel_width // 2,
        center_x + panel_offset + panel_width // 2,
    ]:
        for detail_y in [center_y - panel_height // 4, center_y + panel_height // 4]:
            draw.ellipse(
                [
                    panel_x - detail_radius,
                    detail_y - detail_radius,
                    panel_x + detail_radius,
                    detail_y + detail_radius,
                ],
                fill=accent_color,
            )

    # Robot neck/body connection
    neck_width = size // 8
    neck_height = size // 12
    draw.rectangle(
        [
            center_x - neck_width // 2,
            center_y + head_radius,
            center_x + neck_width // 2,
            center_y + head_radius + neck_height,
        ],
        fill=dark_color,
    )

    return img


def create_icon_version(logo_img, icon_size=256):
    """Create a smaller icon version of the logo"""
    return logo_img.resize((icon_size, icon_size), Image.Resampling.LANCZOS)


def create_banner_version(logo_img, width=800, height=200):
    """Create a banner version with the logo and text"""
    banner = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    # Resize logo to fit banner height
    logo_size = int(height * 0.8)
    logo_resized = logo_img.resize((logo_size, logo_size), Image.Resampling.LANCZOS)

    # Place logo on the left
    logo_x = height // 10
    logo_y = (height - logo_size) // 2
    banner.paste(logo_resized, (logo_x, logo_y), logo_resized)

    # Add text "SysPilot" next to the logo
    try:
        # Try to use a system font
        font_size = height // 4
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", font_size
        )
    except:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size)
        except:
            font = ImageFont.load_default()

    draw = ImageDraw.Draw(banner)
    text = "SysPilot"
    text_x = logo_x + logo_size + height // 10
    text_y = height // 3

    # Draw text with shadow effect
    shadow_offset = 2
    draw.text(
        (text_x + shadow_offset, text_y + shadow_offset),
        text,
        font=font,
        fill=(44, 62, 80, 128),
    )
    draw.text((text_x, text_y), text, font=font, fill=(41, 128, 185))

    return banner


def main():
    print("Creating robot-style logo for SysPilot...")

    # Create the main logo
    logo = create_robot_logo()

    # Save main logo
    logo_path = "assets/syspilot_logo.png"
    logo.save(logo_path)
    print(f"✓ Created main logo: {logo_path}")

    # Create and save icon version
    icon = create_icon_version(logo)
    icon_path = "assets/syspilot_icon.png"
    icon.save(icon_path)
    print(f"✓ Created icon: {icon_path}")

    # Create and save banner version
    banner = create_banner_version(logo)
    banner_path = "assets/syspilot_banner.png"
    banner.save(banner_path)
    print(f"✓ Created banner: {banner_path}")

    print("\n🤖 Robot-style logo generation complete!")
    print("All logo files have been updated with the new robot design.")


if __name__ == "__main__":
    main()
