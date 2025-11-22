"""
Automated Manga Generation Pipeline (AMGP)
Using OpenRouter API
"""

import os
import json
import base64
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional
from openai import OpenAI
from PIL import Image
import io


# ========== Configuration Dataclass ==========

class GenerationMode(Enum):
    PER_PANEL = "PER_PANEL"
    PER_PAGE = "PER_PAGE"


class CharRefMode(Enum):
    TEXT_ONLY = "TEXT_ONLY"
    IMAGE_INPUT = "IMAGE_INPUT"


class ColorMode(Enum):
    MONOCHROME = "MONOCHROME"
    COLOR = "COLOR"


@dataclass
class MangaConfig:
    """Configuration for manga generation experiments"""
    generation_mode: GenerationMode
    char_ref_mode: CharRefMode
    color_mode: ColorMode

    def __str__(self):
        return (f"GenerationMode: {self.generation_mode.value}, "
                f"CharRefMode: {self.char_ref_mode.value}, "
                f"ColorMode: {self.color_mode.value}")


# ========== OpenRouter Client Setup ==========

def get_openrouter_client():
    """Initialize OpenRouter client."""
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ.get("OPENROUTER_API_KEY")
    )


# ========== Module 1: The Planner (Brain) ==========

SYSTEM_PROMPT = """
You are a professional Manga Editor.
1. Analyze the user's story request.
2. Create detailed character profiles with visual descriptions.
3. Create a storyboard with pages and panels.
4. OUTPUT MUST BE VALID JSON with this structure:
{
  "characters": [
    {
      "name": "Character Name",
      "visual_desc": "Detailed visual description including appearance, clothing, distinctive features, hair, eyes, etc."
    }
  ],
  "pages": [
    {
      "page_number": 1,
      "layout_desc": "Description of the overall page layout and flow",
      "panels": [
        {
          "id": 1,
          "description": "What happens in this panel",
          "visual_prompt": "Detailed visual description for image generation - scene, composition, character actions, background, mood",
          "dialogue": "Character dialogue or narration"
        }
      ]
    }
  ]
}

IMPORTANT NOTES:
- Create 3-6 pages for a short story
- Each page should have 3-6 panels
- Visual prompts should be very detailed and suitable for image generation
- Include character names in visual_prompt when they appear
- Describe the scene composition, camera angle, and mood
"""


def plan_manga(user_prompt: str, client: OpenAI) -> Optional[Dict]:
    """
    Uses Gemini Flash to plan the manga structure.
    Returns a JSON structure with characters, pages, and panels.
    """
    try:
        # Define JSON schema for structured output
        manga_schema = {
            "type": "object",
            "properties": {
                "characters": {
                    "type": "array",
                    "description": "List of characters in the manga",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Character name"
                            },
                            "visual_desc": {
                                "type": "string",
                                "description": "Detailed visual description including appearance, clothing, distinctive features"
                            }
                        },
                        "required": ["name", "visual_desc"],
                        "additionalProperties": False
                    }
                },
                "pages": {
                    "type": "array",
                    "description": "List of manga pages",
                    "items": {
                        "type": "object",
                        "properties": {
                            "page_number": {
                                "type": "integer",
                                "description": "Page number"
                            },
                            "layout_desc": {
                                "type": "string",
                                "description": "Description of the overall page layout and flow"
                            },
                            "panels": {
                                "type": "array",
                                "description": "List of panels on this page",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "id": {
                                            "type": "integer",
                                            "description": "Panel ID"
                                        },
                                        "description": {
                                            "type": "string",
                                            "description": "What happens in this panel"
                                        },
                                        "visual_prompt": {
                                            "type": "string",
                                            "description": "Detailed visual description for image generation"
                                        },
                                        "dialogue": {
                                            "type": "string",
                                            "description": "Character dialogue or narration"
                                        }
                                    },
                                    "required": ["id", "description", "visual_prompt", "dialogue"],
                                    "additionalProperties": False
                                }
                            }
                        },
                        "required": ["page_number", "layout_desc", "panels"],
                        "additionalProperties": False
                    }
                }
            },
            "required": ["characters", "pages"],
            "additionalProperties": False
        }

        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://github.com/heavendoor",
                "X-Title": "Manga Generator",
            },
            model="google/gemini-2.5-flash-preview-09-2025",
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": "Create a manga storyboard for this story:\n\n" + user_prompt
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "manga_plan",
                    "strict": True,
                    "schema": manga_schema
                }
            }
        )

        json_text = completion.choices[0].message.content
        return json.loads(json_text)

    except Exception as e:
        print(f"Error in plan_manga: {e}")
        import traceback
        traceback.print_exc()
        return None


# ========== Module 2: The Character Designer ==========

def generate_character_sheets(characters: List[Dict], config: MangaConfig, client: OpenAI) -> Dict[str, str]:
    """
    Generate character reference images if config.char_ref_mode == IMAGE_INPUT.
    Returns a dictionary mapping character names to their reference image URLs (base64).
    """
    character_refs = {}

    if config.char_ref_mode == CharRefMode.TEXT_ONLY:
        return character_refs

    print("\n=== Generating Character Sheets ===")
    for char in characters:
        name = char['name']
        visual_desc = char['visual_desc']

        # Create character sheet prompt
        prompt = (f"Character reference sheet, multiple views, {name}, {visual_desc}, "
                 f"manga style, character design, turnaround, white background, "
                 f"professional anime character sheet, detailed line art")

        print(f"Generating character sheet for: {name}")

        # Generate character sheet image
        char_img = generate_image(prompt, client)

        if char_img:
            character_refs[name] = char_img
            # Save character sheet
            os.makedirs("output/character_refs", exist_ok=True)
            save_base64_image(char_img, f"output/character_refs/{name.replace(' ', '_')}.jpg")
            print(f"  Saved: output/character_refs/{name.replace(' ', '_')}.jpg")

    return character_refs


# ========== Module 3: The Artist (Generator) ==========

def image_to_base64_url(image: Image.Image) -> str:
    """Convert PIL Image to base64 data URL."""
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/jpeg;base64,{img_str}"


def save_base64_image(base64_data: str, filepath: str):
    """Save base64 image data to file."""
    # Remove data URL prefix if present
    if base64_data.startswith('data:image'):
        base64_data = base64_data.split(',')[1]

    img_data = base64.b64decode(base64_data)
    with open(filepath, 'wb') as f:
        f.write(img_data)


def generate_image(prompt: str, client: OpenAI, reference_images: Optional[List[str]] = None) -> Optional[str]:
    """
    Generate an image using Gemini 2.5 Flash Image via OpenRouter.

    Args:
        prompt: The image generation prompt
        client: The OpenAI client configured for OpenRouter
        reference_images: Optional list of reference images as base64 data URLs

    Returns:
        Base64 encoded image string or None
    """
    try:
        # Build content array
        content = [
            {
                "type": "text",
                "text": prompt
            }
        ]

        # Add reference images if provided
        if reference_images:
            for ref_img in reference_images:
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": ref_img
                    }
                })

        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://github.com/heavendoor",
                "X-Title": "Manga Generator",
            },
            model="google/gemini-2.5-flash-image",
            messages=[
                {
                    "role": "user",
                    "content": content
                }
            ]
        )

        # Extract base64 image from response
        # OpenRouter returns images in the message.images field
        message = completion.choices[0].message

        if hasattr(message, 'images') and message.images:
            # Extract the first image's base64 data URL
            image_data = message.images[0]
            if 'image_url' in image_data:
                return image_data['image_url']['url']

        return None

    except Exception as e:
        print(f"Error generating image: {e}")
        import traceback
        traceback.print_exc()
        return None


def generate_panel_image(panel: Dict, character_refs: Dict[str, str], config: MangaConfig, client: OpenAI) -> Optional[Image.Image]:
    """Generate a single panel image."""

    # Build the prompt with manga style enforcement
    base_prompt = panel['visual_prompt']

    # Add style suffix based on color mode
    if config.color_mode == ColorMode.COLOR:
        style_suffix = ", manga style, vibrant colors, anime art style, professional manga artwork, colorful illustration"
    else:
        style_suffix = ", manga style, monochrome, black and white, screentones, ink lines, high contrast, anime art style, professional manga artwork"

    full_prompt = base_prompt + style_suffix

    # Prepare reference images if using IMAGE_INPUT mode
    ref_images = None
    if config.char_ref_mode == CharRefMode.IMAGE_INPUT and character_refs:
        ref_images = list(character_refs.values())

    base64_img = generate_image(full_prompt, client, ref_images)

    if base64_img:
        # Convert base64 to PIL Image
        try:
            if base64_img.startswith('data:image'):
                base64_img = base64_img.split(',')[1]
            img_data = base64.b64decode(base64_img)
            return Image.open(io.BytesIO(img_data))
        except Exception as e:
            print(f"Error converting base64 to image: {e}")
            return None

    return None


def generate_page_image(page: Dict, character_refs: Dict[str, str], config: MangaConfig, client: OpenAI) -> Optional[Image.Image]:
    """Generate a full page image with all panels in one generation."""

    # Combine all panel descriptions into a cohesive page prompt
    layout_desc = page.get('layout_desc', '')
    panel_descriptions = []

    for i, panel in enumerate(page['panels'], 1):
        panel_desc = f"Panel {i}: {panel['visual_prompt']}"
        if panel.get('dialogue'):
            panel_desc += f" (Dialogue: {panel['dialogue']})"
        panel_descriptions.append(panel_desc)

    # Build comprehensive page prompt based on color mode
    if config.color_mode == ColorMode.COLOR:
        full_prompt = (f"Full manga page, vibrant colors, high quality professional manga. "
                      f"Page layout: {layout_desc}. "
                      f"{' '.join(panel_descriptions)}. "
                      f"Manga style, colorful illustration, anime art style, "
                      f"panel borders clearly visible")
    else:
        full_prompt = (f"Full manga page, black and white, high quality professional manga. "
                      f"Page layout: {layout_desc}. "
                      f"{' '.join(panel_descriptions)}. "
                      f"Manga style, monochrome, screentones, ink lines, high contrast, anime art style, "
                      f"panel borders clearly visible")

    # Prepare reference images if using IMAGE_INPUT mode
    ref_images = None
    if config.char_ref_mode == CharRefMode.IMAGE_INPUT and character_refs:
        ref_images = list(character_refs.values())

    base64_img = generate_image(full_prompt, client, ref_images)

    if base64_img:
        # Convert base64 to PIL Image
        try:
            if base64_img.startswith('data:image'):
                base64_img = base64_img.split(',')[1]
            img_data = base64.b64decode(base64_img)
            return Image.open(io.BytesIO(img_data))
        except Exception as e:
            print(f"Error converting base64 to image: {e}")
            return None

    return None


# ========== Module 4: The Assembler ==========

def assemble_page(panel_images: List[Image.Image], page_num: int) -> Image.Image:
    """
    Assemble individual panel images into a full page.
    Uses a simple grid layout: 2 columns, variable rows.
    """
    # Create a blank A4-like canvas (2480 x 3508 pixels at 300 DPI)
    page_width, page_height = 2480, 3508
    full_page = Image.new("RGB", (page_width, page_height), "white")

    num_panels = len(panel_images)
    if num_panels == 0:
        return full_page

    # Calculate grid layout
    cols = 2
    rows = (num_panels + 1) // 2

    # Calculate panel dimensions with margins
    margin = 40
    panel_width = (page_width - margin * 3) // cols
    panel_height = (page_height - margin * (rows + 1)) // rows

    # Paste panels into grid
    for idx, panel_img in enumerate(panel_images):
        row = idx // cols
        col = idx % cols

        # Resize panel to fit
        panel_resized = panel_img.resize((panel_width, panel_height), Image.Resampling.LANCZOS)

        # Calculate position
        x = margin + col * (panel_width + margin)
        y = margin + row * (panel_height + margin)

        # Paste panel
        full_page.paste(panel_resized, (x, y))

    return full_page


def save_to_pdf(page_images: List[Image.Image], output_filename: str = "output/manga.pdf"):
    """Save all page images to a single PDF file."""
    if not page_images:
        print("No pages to save!")
        return

    os.makedirs(os.path.dirname(output_filename), exist_ok=True)

    # Convert all images to RGB mode (required for PDF)
    rgb_pages = []
    for img in page_images:
        if img.mode != 'RGB':
            rgb_pages.append(img.convert('RGB'))
        else:
            rgb_pages.append(img)

    # Save as PDF
    rgb_pages[0].save(
        output_filename,
        "PDF",
        resolution=100.0,
        save_all=True,
        append_images=rgb_pages[1:] if len(rgb_pages) > 1 else []
    )

    print(f"\nFinal PDF saved to: {output_filename}")


# ========== Main Execution Logic ==========

def generate_manga(user_prompt: str, config: MangaConfig):
    """
    Main function to generate manga from user prompt.

    Args:
        user_prompt: The story/scene description from user
        config: MangaConfig with experiment flags
    """

    print("=" * 60)
    print("AUTOMATED MANGA GENERATION PIPELINE")
    print("=" * 60)
    print(f"\nConfiguration:\n{config}\n")
    print(f"User Prompt: {user_prompt}\n")

    # Initialize client
    client = get_openrouter_client()

    # Step 1: Plan the manga
    print("\n=== Step 1: Planning Manga Structure ===")
    plan = plan_manga(user_prompt, client)

    if not plan:
        print("Error: Failed to generate manga plan!")
        return

    print(f"Plan generated successfully!")
    print(f"  Characters: {len(plan.get('characters', []))}")
    print(f"  Pages: {len(plan.get('pages', []))}")

    # Save plan for reference
    os.makedirs("output", exist_ok=True)
    with open("output/manga_plan.json", "w") as f:
        json.dump(plan, f, indent=2)
    print("  Plan saved to: output/manga_plan.json")

    # Step 2: Generate character references (if needed)
    print("\n=== Step 2: Character Design ===")
    characters = plan.get('characters', [])
    character_refs = generate_character_sheets(characters, config, client)

    if config.char_ref_mode == CharRefMode.TEXT_ONLY:
        print("Using TEXT_ONLY mode - no character images generated")
    else:
        print(f"Generated {len(character_refs)} character reference sheets")

    # Step 3: Generate pages/panels
    print("\n=== Step 3: Generating Pages ===")
    pages = plan.get('pages', [])
    page_images = []

    for page in pages:
        page_num = page['page_number']
        panels = page.get('panels', [])

        print(f"\n--- Page {page_num} ({len(panels)} panels) ---")

        if config.generation_mode == GenerationMode.PER_PAGE:
            # Generate entire page at once
            print(f"  Generating full page image...")
            page_img = generate_page_image(page, character_refs, config, client)

            if page_img:
                page_images.append(page_img)
                # Save individual page
                page_img.save(f"output/page_{page_num}.jpg")
                print(f"  Saved: output/page_{page_num}.jpg")
            else:
                print(f"  Error generating page {page_num}")

        else:  # PER_PANEL mode
            # Generate each panel individually
            panel_imgs = []
            for panel in panels:
                panel_id = panel['id']
                print(f"  Generating panel {panel_id}...")
                panel_img = generate_panel_image(panel, character_refs, config, client)

                if panel_img:
                    panel_imgs.append(panel_img)
                    # Save individual panel
                    os.makedirs(f"output/page_{page_num}_panels", exist_ok=True)
                    panel_img.save(f"output/page_{page_num}_panels/panel_{panel_id}.jpg")
                    print(f"    Saved: output/page_{page_num}_panels/panel_{panel_id}.jpg")
                else:
                    print(f"    Error generating panel {panel_id}")

            # Assemble panels into page
            if panel_imgs:
                print(f"  Assembling {len(panel_imgs)} panels into page...")
                page_img = assemble_page(panel_imgs, page_num)
                page_images.append(page_img)
                page_img.save(f"output/page_{page_num}.jpg")
                print(f"  Saved: output/page_{page_num}.jpg")

    # Step 4: Create final PDF
    print("\n=== Step 4: Creating Final PDF ===")
    save_to_pdf(page_images, "output/manga.pdf")

    print("\n" + "=" * 60)
    print("MANGA GENERATION COMPLETE!")
    print("=" * 60)
    print(f"Total pages generated: {len(page_images)}")
    print(f"Output directory: output/")
    print(f"Final PDF: output/manga.pdf")
