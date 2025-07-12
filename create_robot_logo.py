#!/usr/bin/env python3
"""
SysPilot Robot Logo Generator
Creates a robot-style logo similar to the provided design
"""

import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont


def create_robot_logo():
    """Create a robot-style logo for SysPilot"""

    # Canvas settings
    width, height = 800, 600
    bg_color = (240, 235, 220)  # Light beige background

    # Create image
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Robot colors
    robot_blue = (85, 170, 200)
    robot_dark_blue = (65, 130, 160)
    robot_light_blue = (105, 190, 220)
    outline_color = (40, 40, 40)
    white = (255, 255, 255)
    black = (40, 40, 40)
    wrench_gray = (100, 100, 100)

    # Center position
    cx, cy = width // 2, height // 2 - 50

    # Robot body (main rectangle)
    body_width, body_height = 120, 100
    body_left = cx - body_width // 2
    body_top = cy - 20
    body_right = body_left + body_width
    body_bottom = body_top + body_height

    # Draw robot body
    draw.rounded_rectangle(
        [body_left, body_top, body_right, body_bottom],
        radius=15,
        fill=robot_blue,
        outline=outline_color,
        width=4,
    )

    # Robot head (circle)
    head_radius = 50
    head_cx, head_cy = cx, cy - 70

    # Draw robot head
    draw.ellipse(
        [
            head_cx - head_radius,
            head_cy - head_radius,
            head_cx + head_radius,
            head_cy + head_radius,
        ],
        fill=robot_blue,
        outline=outline_color,
        width=4,
    )

    # Robot helmet/visor
    visor_width = 70
    visor_height = 25
    visor_left = head_cx - visor_width // 2
    visor_top = head_cy - 15

    draw.rounded_rectangle(
        [visor_left, visor_top, visor_left + visor_width, visor_top + visor_height],
        radius=8,
        fill=robot_dark_blue,
        outline=outline_color,
        width=3,
    )

    # Visor screen
    screen_width = 50
    screen_height = 15
    screen_left = head_cx - screen_width // 2
    screen_top = head_cy - 10

    draw.rounded_rectangle(
        [
            screen_left,
            screen_top,
            screen_left + screen_width,
            screen_top + screen_height,
        ],
        radius=5,
        fill=white,
        outline=outline_color,
        width=2,
    )

    # Robot eyes (two circles)
    eye_radius = 6
    eye_spacing = 15
    eye_y = head_cy - 5

    # Left eye
    draw.ellipse(
        [
            head_cx - eye_spacing - eye_radius,
            eye_y - eye_radius,
            head_cx - eye_spacing + eye_radius,
            eye_y + eye_radius,
        ],
        fill=black,
    )

    # Right eye
    draw.ellipse(
        [
            head_cx + eye_spacing - eye_radius,
            eye_y - eye_radius,
            head_cx + eye_spacing + eye_radius,
            eye_y + eye_radius,
        ],
        fill=black,
    )

    # Robot smile
    smile_width = 20
    smile_left = head_cx - smile_width // 2
    smile_top = head_cy + 8

    draw.arc(
        [smile_left, smile_top, smile_left + smile_width, smile_top + 15],
        start=0,
        end=180,
        fill=black,
        width=3,
    )

    # Robot antenna
    antenna_x = head_cx
    antenna_y1 = head_cy - head_radius - 5
    antenna_y2 = antenna_y1 - 20

    draw.line(
        [antenna_x, antenna_y1, antenna_x, antenna_y2], fill=outline_color, width=4
    )

    # Antenna tip (circle)
    tip_radius = 8
    draw.ellipse(
        [
            antenna_x - tip_radius,
            antenna_y2 - tip_radius,
            antenna_x + tip_radius,
            antenna_y2 + tip_radius,
        ],
        fill=outline_color,
    )

    # Robot arms
    arm_width = 25
    arm_height = 80

    # Left arm
    left_arm_x = body_left - 15
    arm_y = body_top + 10

    draw.rounded_rectangle(
        [left_arm_x - arm_width, arm_y, left_arm_x, arm_y + arm_height],
        radius=12,
        fill=robot_blue,
        outline=outline_color,
        width=4,
    )

    # Right arm
    right_arm_x = body_right + 15

    draw.rounded_rectangle(
        [right_arm_x, arm_y, right_arm_x + arm_width, arm_y + arm_height],
        radius=12,
        fill=robot_blue,
        outline=outline_color,
        width=4,
    )

    # Robot legs
    leg_width = 30
    leg_height = 60
    leg_spacing = 20
    leg_y = body_bottom

    # Left leg
    left_leg_x = cx - leg_spacing - leg_width // 2

    draw.rounded_rectangle(
        [
            left_leg_x - leg_width // 2,
            leg_y,
            left_leg_x + leg_width // 2,
            leg_y + leg_height,
        ],
        radius=12,
        fill=robot_blue,
        outline=outline_color,
        width=4,
    )

    # Right leg
    right_leg_x = cx + leg_spacing + leg_width // 2

    draw.rounded_rectangle(
        [
            right_leg_x - leg_width // 2,
            leg_y,
            right_leg_x + leg_width // 2,
            leg_y + leg_height,
        ],
        radius=12,
        fill=robot_blue,
        outline=outline_color,
        width=4,
    )

    # Robot feet
    foot_width = 40
    foot_height = 15
    foot_y = leg_y + leg_height - 5

    # Left foot
    draw.rounded_rectangle(
        [
            left_leg_x - foot_width // 2,
            foot_y,
            left_leg_x + foot_width // 2,
            foot_y + foot_height,
        ],
        radius=8,
        fill=robot_dark_blue,
        outline=outline_color,
        width=3,
    )

    # Right foot
    draw.rounded_rectangle(
        [
            right_leg_x - foot_width // 2,
            foot_y,
            right_leg_x + foot_width // 2,
            foot_y + foot_height,
        ],
        radius=8,
        fill=robot_dark_blue,
        outline=outline_color,
        width=3,
    )

    # Wrench (in right hand)
    wrench_x = right_arm_x + arm_width // 2
    wrench_y = arm_y + arm_height - 20
    wrench_length = 60
    wrench_width = 8

    # Wrench handle
    draw.line(
        [
            wrench_x,
            wrench_y,
            wrench_x + wrench_length * 0.7,
            wrench_y - wrench_length * 0.7,
        ],
        fill=wrench_gray,
        width=wrench_width,
    )

    # Wrench head
    head_size = 20
    head_x = wrench_x + wrench_length * 0.7
    head_y = wrench_y - wrench_length * 0.7

    # Wrench jaws
    draw.polygon(
        [
            (head_x - 5, head_y - head_size // 2),
            (head_x + 15, head_y - head_size // 2 - 8),
            (head_x + 15, head_y - head_size // 2 + 5),
            (head_x + 5, head_y),
            (head_x + 15, head_y + head_size // 2 - 5),
            (head_x + 15, head_y + head_size // 2 + 8),
            (head_x - 5, head_y + head_size // 2),
        ],
        fill=wrench_gray,
        outline=outline_color,
        width=2,
    )

    # Sparkles around the wrench
    sparkle_positions = [
        (wrench_x + 40, wrench_y - 30),
        (wrench_x + 55, wrench_y - 45),
        (wrench_x + 35, wrench_y - 50),
    ]

    for sx, sy in sparkle_positions:
        # Draw sparkle as small cross
        draw.line([sx - 6, sy, sx + 6, sy], fill=black, width=3)
        draw.line([sx, sy - 6, sx, sy + 6], fill=black, width=3)
        # Small center dot
        draw.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=black)

    # Body details
    # Chest panel
    panel_width = 60
    panel_height = 40
    panel_x = cx - panel_width // 2
    panel_y = body_top + 20

    draw.rounded_rectangle(
        [panel_x, panel_y, panel_x + panel_width, panel_y + panel_height],
        radius=8,
        fill=robot_light_blue,
        outline=outline_color,
        width=2,
    )

    # Control buttons
    button_radius = 4
    button_y = panel_y + 15

    for i, button_x in enumerate([panel_x + 15, panel_x + 30, panel_x + 45]):
        color = [robot_dark_blue, (200, 100, 100), (100, 200, 100)][i]
        draw.ellipse(
            [
                button_x - button_radius,
                button_y - button_radius,
                button_x + button_radius,
                button_y + button_radius,
            ],
            fill=color,
            outline=outline_color,
            width=1,
        )

    # Add "SysPilot" text
    text_y = cy + 150
    text = "SysPilot"

    try:
        # Try to use a bold font if available
        font_size = 72
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size
        )
    except:
        # Fallback to default font
        font = ImageFont.load_default()

    # Get text dimensions
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    text_x = cx - text_width // 2

    # Draw text with outline effect
    outline_offset = 2
    for dx in [-outline_offset, 0, outline_offset]:
        for dy in [-outline_offset, 0, outline_offset]:
            if dx != 0 or dy != 0:
                draw.text(
                    (text_x + dx, text_y + dy), text, font=font, fill=outline_color
                )

    # Draw main text
    draw.text((text_x, text_y), text, font=font, fill=black)

    return img


def create_icon_versions(logo_img):
    """Create different sized versions for icons"""
    versions = {}

    # Extract just the robot part for icons (crop and resize)
    # Focus on the robot without the text
    crop_box = (150, 50, 650, 450)  # Adjust based on robot position
    robot_only = logo_img.crop(crop_box)

    # Icon sizes
    sizes = [16, 32, 48, 64, 128, 256, 512]

    for size in sizes:
        versions[size] = robot_only.resize((size, size), Image.Resampling.LANCZOS)

    return versions


def main():
    """Generate all logo files"""
    print("🤖 Generating SysPilot Robot Logo...")

    # Create main logo
    logo = create_robot_logo()

    # Save main logo
    logo.save(
        "/var/www/Zidan/Ubuntu_Cleanup_App/assets/syspilot_logo_new.png",
        "PNG",
        quality=95,
    )
    print("✅ Created main logo: syspilot_logo_new.png")

    # Create and save icon versions
    icons = create_icon_versions(logo)

    # Save main icon (256x256)
    icons[256].save(
        "/var/www/Zidan/Ubuntu_Cleanup_App/assets/syspilot_icon_new.png",
        "PNG",
        quality=95,
    )
    print("✅ Created icon: syspilot_icon_new.png")

    # Create banner version (wider format)
    banner_width, banner_height = 1200, 400
    banner = Image.new("RGB", (banner_width, banner_height), (240, 235, 220))

    # Resize logo to fit banner
    logo_resized = logo.resize((300, 225), Image.Resampling.LANCZOS)

    # Paste logo on banner
    logo_x = (banner_width - 300) // 2
    logo_y = (banner_height - 225) // 2
    banner.paste(logo_resized, (logo_x, logo_y))

    banner.save(
        "/var/www/Zidan/Ubuntu_Cleanup_App/assets/syspilot_banner_new.png",
        "PNG",
        quality=95,
    )
    print("✅ Created banner: syspilot_banner_new.png")

    print("\n🎉 Robot logo generation complete!")
    print("📁 New files created in assets/ directory")


if __name__ == "__main__":
    main()
