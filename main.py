#!/usr/bin/env python3
"""
Main entry point for the Automated Manga Generation Pipeline.
CLI tool for generating manga from text prompts with configurable options.
"""

import argparse
import sys
from dotenv import load_dotenv
from manga_generator import (
    generate_manga,
    MangaConfig,
    GenerationMode,
    CharRefMode,
    ColorMode
)

# Load environment variables from .env file
load_dotenv()


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Automated Manga Generation Pipeline - Generate manga from text prompts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick generation with default settings
  python main.py "A story about a space explorer"

  # Use per-page generation mode
  python main.py --mode page "Your story here"

  # Generate with character reference images
  python main.py --char-ref image "Your story here"

  # Generate colored manga
  python main.py --color "Your story here"

  # Full custom configuration
  python main.py --mode panel --char-ref image --color "Your story here"

  # Read prompt from file
  python main.py --prompt-file story.txt --mode page --color

Generation Modes:
  panel  - Generate each panel individually, then assemble into pages (more control)
  page   - Generate complete pages in a single generation (faster)

Character Reference Modes:
  text   - Use only text descriptions for character consistency
  image  - Generate character sheets and use as visual references

Color Modes:
  Default (no flag) - Monochrome black and white manga style
  --color          - Vibrant colored manga style
        """
    )

    # Positional argument for prompt
    parser.add_argument(
        'prompt',
        nargs='?',
        help='Story prompt for manga generation (or use --prompt-file)'
    )

    # Optional arguments for configuration
    parser.add_argument(
        '--mode',
        choices=['panel', 'page'],
        default='panel',
        help='Generation mode: "panel" (per-panel) or "page" (per-page). Default: panel'
    )

    parser.add_argument(
        '--char-ref',
        choices=['text', 'image'],
        default='text',
        help='Character reference mode: "text" (text-only) or "image" (with character sheets). Default: text'
    )

    parser.add_argument(
        '--color',
        action='store_true',
        help='Generate colored manga instead of monochrome black and white. Default: monochrome'
    )

    parser.add_argument(
        '--prompt-file',
        type=str,
        help='Read prompt from a text file instead of command line'
    )

    parser.add_argument(
        '--output',
        type=str,
        default='output/manga.pdf',
        help='Output PDF file path. Default: output/manga.pdf'
    )

    return parser.parse_args()


def get_user_prompt(args):
    """Get user prompt from CLI args or file."""
    if args.prompt_file:
        try:
            with open(args.prompt_file, 'r') as f:
                return f.read().strip()
        except FileNotFoundError:
            print(f"Error: Prompt file '{args.prompt_file}' not found")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading prompt file: {e}")
            sys.exit(1)
    elif args.prompt:
        return args.prompt
    else:
        # Interactive mode if no prompt provided
        print("No prompt provided. Enter your story prompt (press Ctrl+D or Ctrl+Z when done):")
        print("-" * 60)
        try:
            lines = []
            while True:
                try:
                    line = input()
                    lines.append(line)
                except EOFError:
                    break
            prompt = '\n'.join(lines).strip()
            if not prompt:
                print("Error: Empty prompt provided")
                sys.exit(1)
            return prompt
        except KeyboardInterrupt:
            print("\nCancelled by user")
            sys.exit(0)


def create_config(args):
    """Create MangaConfig from CLI arguments."""
    # Map CLI args to enum values
    generation_mode = GenerationMode.PER_PANEL if args.mode == 'panel' else GenerationMode.PER_PAGE
    char_ref_mode = CharRefMode.TEXT_ONLY if args.char_ref == 'text' else CharRefMode.IMAGE_INPUT
    color_mode = ColorMode.COLOR if args.color else ColorMode.MONOCHROME

    return MangaConfig(
        generation_mode=generation_mode,
        char_ref_mode=char_ref_mode,
        color_mode=color_mode
    )


def main():
    """Main entry point with CLI argument parsing."""
    args = parse_arguments()

    # Get user prompt
    user_prompt = get_user_prompt(args)

    # Create configuration from CLI arguments
    config = create_config(args)

    # Display configuration
    print("=" * 60)
    print("AUTOMATED MANGA GENERATION")
    print("=" * 60)
    print(f"\nConfiguration:")
    print(f"  Generation Mode: {config.generation_mode.value}")
    print(f"  Character Ref:   {config.char_ref_mode.value}")
    print(f"  Color Mode:      {config.color_mode.value}")
    print(f"  Output Path:     {args.output}")
    print(f"\nPrompt Preview:")
    print("-" * 60)
    # Show first 200 chars of prompt
    preview = user_prompt[:200] + "..." if len(user_prompt) > 200 else user_prompt
    print(preview)
    print("-" * 60)
    print()

    # Generate the manga
    generate_manga(user_prompt, config)

    # Update final output path if different from default
    if args.output != 'output/manga.pdf':
        import os
        import shutil
        try:
            os.makedirs(os.path.dirname(args.output), exist_ok=True)
            shutil.move('output/manga.pdf', args.output)
            print(f"\nMoved final PDF to: {args.output}")
        except Exception as e:
            print(f"\nWarning: Could not move PDF to {args.output}: {e}")
            print(f"PDF remains at: output/manga.pdf")


if __name__ == "__main__":
    main()
