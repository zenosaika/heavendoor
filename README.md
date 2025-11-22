# HeavenDoor: Automated Manga Generation Pipeline

**Generate professional manga from text prompts using AI!**

[![Version](https://img.shields.io/badge/version-2.0-blue.svg)](CHANGELOG.md)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

---

## 📖 Table of Contents

- [Quick Start](#quick-start)
- [Features](#features)
- [Usage Examples](#usage-examples)
- [Command Reference](#command-reference)
- [Writing Prompts](#writing-prompts)
- [Configuration](#configuration)
- [Architecture](#architecture)
- [Cost & Performance](#cost--performance)
- [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone repository
git clone https://github.com/yourusername/heavendoor.git
cd heavendoor

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Setup API Key

Create a `.env` file:
```bash
echo "OPENROUTER_API_KEY=your_key_here" > .env
```

Get your API key from: https://openrouter.ai/keys

### 3. Generate Your First Manga!

```bash
# Simple monochrome manga
./venv/bin/python main.py "A story about a space explorer"

# Colored manga
./venv/bin/python main.py --color "A magical girl story"

# From a file
./venv/bin/python main.py --prompt-file example_prompt.txt
```

**Output:**
- `output/manga.pdf` - Final manga PDF ⭐
- `output/page_*.jpg` - Individual page images
- `output/manga_plan.json` - Story structure

---

## ✨ Features

### 🎨 Dual Color Modes

**Monochrome (Default)**
```bash
./venv/bin/python main.py "Your story"
```
- Traditional manga style
- Black & white with screentones
- High contrast ink lines
- Perfect for classic manga

**Color Mode**
```bash
./venv/bin/python main.py --color "Your story"
```
- Vibrant full-color manga
- Modern anime art style
- Perfect for webtoons
- Great for children's content

### 🎯 Flexible Generation Modes

**Panel Mode** - Maximum Quality
```bash
./venv/bin/python main.py --mode panel "Your story"
```
- Generates each panel individually
- Assembles panels into pages
- Higher detail per panel
- More API calls (slower, higher cost)

**Page Mode** - Speed & Efficiency
```bash
./venv/bin/python main.py --mode page "Your story"
```
- Generates entire pages at once
- Better panel composition
- Faster generation
- Lower cost

### 👥 Character Consistency

**Text-Only (Default)**
```bash
./venv/bin/python main.py "Your story"
```
- Uses text descriptions
- Faster generation
- Lower cost

**Image-Based References**
```bash
./venv/bin/python main.py --char-ref image "Your story"
```
- Generates character sheets first
- Better character consistency
- Professional character designs
- Saved to `output/character_refs/`

---

## 📚 Usage Examples

### Basic Generation

```bash
# Quick monochrome manga
./venv/bin/python main.py "A samurai in a bamboo forest"

# Quick colored manga
./venv/bin/python main.py --color "A magical transformation scene"
```

### Advanced Generation

```bash
# High-quality colored manga with character sheets
./venv/bin/python main.py \
  --mode page \
  --char-ref image \
  --color \
  "A fantasy adventure story"

# From file with custom output
./venv/bin/python main.py \
  --prompt-file my_story.txt \
  --output projects/manga1.pdf \
  --color
```

### Batch Processing

```bash
# Process multiple stories
for story in stories/*.txt; do
    ./venv/bin/python main.py --mode page --prompt-file "$story"
done

# Generate colored versions
for story in stories/*.txt; do
    ./venv/bin/python main.py --color --prompt-file "$story"
done
```

---

## 🎛️ Command Reference

### Syntax
```bash
./venv/bin/python main.py [OPTIONS] [PROMPT]
```

### Options

| Flag | Values | Default | Description |
|------|--------|---------|-------------|
| `--mode` | `panel`, `page` | `panel` | Generation strategy |
| `--char-ref` | `text`, `image` | `text` | Character reference mode |
| `--color` | flag | off | Enable colored manga |
| `--prompt-file` | `path` | - | Read prompt from file |
| `--output` | `path` | `output/manga.pdf` | Custom output path |

### Help

```bash
./venv/bin/python main.py --help
```

---

## ✍️ Writing Prompts

### Prompt Structure

Good prompts include:

1. **Character Descriptions**
   - Name, age, appearance
   - Clothing, distinctive features
   - Personality traits

2. **Story Summary**
   - Beginning (setup)
   - Middle (conflict)
   - End (resolution)

3. **Page Count**
   - "Make this 3-4 pages"
   - Helps AI plan properly

4. **Tone & Style**
   - "Lighthearted comedy"
   - "Dark mystery"
   - "Action-packed adventure"

### Example Prompt Template

```
[Character name] is a [age/description] who [normal life].

One day, [inciting incident happens].
They must [main goal] before [deadline/consequence].

Key scenes:
- [Scene 1]
- [Scene 2]
- [Climax]

The story ends with [resolution].

Make this [X] pages with [tone].
```

### Sample Prompt

```
Luna is a 16-year-old witch who just discovered she can talk to spirits.

One day, a ghost named Eldrin appears and tells her the spirit world is dying
from an ancient curse. Luna must journey through haunted forests and mystical
temples to break the curse before midnight.

Key scenes:
- Luna's discovery of her power on her birthday
- Meeting Eldrin and learning about the curse
- Battling dark creatures in the haunted forest
- Confronting the curse at the ancient temple
- Breaking the curse and saving the spirit world

The story ends with Luna accepting her role as a bridge between worlds.

Make this 4 pages with action, emotion, and a hopeful ending.
```

---

## ⚙️ Configuration

### MangaConfig Class

```python
@dataclass
class MangaConfig:
    generation_mode: GenerationMode  # PER_PANEL or PER_PAGE
    char_ref_mode: CharRefMode       # TEXT_ONLY or IMAGE_INPUT
    color_mode: ColorMode            # MONOCHROME or COLOR
```

### Environment Variables

Required in `.env` file:
```bash
OPENROUTER_API_KEY=sk-or-v1-...
```

---

## 🏗️ Architecture

### System Overview

```
User Prompt
    ↓
[Module 1] Planner (Gemini Flash)
    ├─ Story structure
    ├─ Character profiles
    └─ Panel descriptions
    ↓
[Module 2] Character Designer (optional)
    └─ Character reference sheets
    ↓
[Module 3] Image Generator (Gemini Flash Image)
    ├─ Panel/page images
    └─ Applies color/monochrome style
    ↓
[Module 4] Assembler
    ├─ Combines panels (if panel mode)
    └─ Creates PDF
    ↓
Final Manga PDF
```

### Modules

**1. Planner (Brain)**
- Model: `google/gemini-2.5-flash-preview-09-2025`
- Uses structured outputs (JSON Schema)
- Creates characters, pages, and panels
- Output: `manga_plan.json`

**2. Character Designer**
- Model: `google/gemini-2.5-flash-image`
- Generates character sheets (if `--char-ref image`)
- Output: `character_refs/*.jpg`

**3. Image Generator (Artist)**
- Model: `google/gemini-2.5-flash-image`
- Generates manga panels or pages
- Supports multimodal input (text + reference images)
- Applies color or monochrome style
- Output: `page_*.jpg`

**4. Assembler**
- Combines panels into pages (if panel mode)
- Creates final PDF from all pages
- Output: `manga.pdf`

---

## 💰 Cost & Performance

### Cost Breakdown

**Per 4-Page Manga:**
```
Planning:             $0.0001
Image Generation:     $0.12    (4 pages × $0.03)
─────────────────────────────
Total:                ~$0.13 USD
```

**With Character Sheets (+3 characters):**
```
Planning:             $0.0001
Character Sheets:     $0.09    (3 × $0.03)
Image Generation:     $0.12    (4 pages × $0.03)
─────────────────────────────
Total:                ~$0.22 USD
```

**Cost Factors:**
- Panel mode costs more (multiple images per page)
- Character sheets add one-time generation cost
- Color mode has same cost as monochrome

### Performance Metrics

**4-Page Manga Generation:**
- Planning: ~20 seconds
- Character Sheets (optional): ~45 seconds
- Page Generation: ~30-45 seconds per page
- PDF Assembly: <5 seconds
- **Total**: ~2-3 minutes

**Quality:**
- Story planning: Professional narrative structure
- Character design: High-quality anime/manga style
- Image generation: Publication-ready
- PDF output: Optimized file size (~1 MB for 4 pages)

---

## 🔧 Troubleshooting

### Common Issues

**"OPENROUTER_API_KEY not found"**
```bash
# Create .env file with your API key
echo "OPENROUTER_API_KEY=your_key" > .env
```

**"Module 'openai' not found"**
```bash
# Reinstall dependencies
./venv/bin/pip install -r requirements.txt
```

**"No images generated"**
- Check OpenRouter account balance
- Verify API key is correct
- Check output directory permissions
- Review API logs at https://openrouter.ai/activity

**Images not colorful**
- Ensure you used `--color` flag
- Verify configuration shows `Color Mode: COLOR`
- Check generated images in `output/` directory

**JSON parsing errors** (should not happen in v2.0)
- Update to latest version
- Structured outputs guarantee valid JSON
- Report issue if still occurring

### Getting Help

1. Check documentation in this repository
2. Review example prompts and outputs
3. Open an issue on GitHub
4. Check OpenRouter status page

---

## 🎯 Use Cases

### Perfect For

✅ **Content Creators**
- Generate storyboards for animation
- Create comic book prototypes
- Visualize story ideas quickly

✅ **Writers & Authors**
- Visualize scenes from novels
- Create chapter illustrations
- Prototype graphic novel concepts

✅ **Educators**
- Create educational comics
- Visualize historical events
- Make learning materials engaging

✅ **Game Developers**
- Generate character designs
- Create cutscene storyboards
- Prototype visual novel art

✅ **Artists**
- Generate reference images
- Explore composition ideas
- Create portfolio pieces

---

## 📊 Technical Details

### Structured Outputs

v2.0 uses OpenRouter's structured outputs for 100% reliable JSON:

```python
response_format={
    "type": "json_schema",
    "json_schema": {
        "name": "manga_plan",
        "strict": True,
        "schema": manga_schema
    }
}
```

**Benefits:**
- Zero JSON parsing errors
- Type-safe outputs
- Guaranteed schema compliance
- Simpler error handling

### Models Used

| Purpose | Model | Provider |
|---------|-------|----------|
| Planning | `google/gemini-2.5-flash-preview-09-2025` | OpenRouter |
| Images | `google/gemini-2.5-flash-image` | OpenRouter |

Both models support:
- Structured outputs
- Multimodal inputs (text + images)
- High-quality generation

---

## 📁 File Structure

```
heavendoor/
├── venv/                      # Virtual environment
├── .env                       # API keys (create this!)
├── main.py                    # CLI entry point
├── manga_generator.py         # Core generation logic
├── requirements.txt           # Dependencies
├── example_prompt.txt         # Example story
├── README.md                  # This file
├── QUICK_START.md            # Quick start guide
├── CHANGELOG.md              # Version history
├── FEATURE_COMPARISON.md     # v1 vs v2 comparison
├── FINAL_TEST_REPORT.md      # Test report
└── output/                    # Generated files
    ├── manga_plan.json        # Story structure
    ├── manga.pdf              # Final PDF ⭐
    ├── page_1.jpg             # Page images
    ├── page_2.jpg
    └── character_refs/        # Character sheets (if used)
        ├── Character1.jpg
        └── Character2.jpg
```

---

## 🗺️ Roadmap

### v2.1 (Planned)
- [ ] Custom color palettes
- [ ] Dialogue text overlay on images
- [ ] Panel border drawing
- [ ] Style presets (shounen, shoujo, seinen)
- [ ] Batch processing improvements

### v3.0 (Future)
- [ ] Web UI interface
- [ ] Multiple image model support (Stable Diffusion, DALL-E)
- [ ] Advanced layout templates
- [ ] Real-time preview
- [ ] Collaborative editing

### Suggestions Welcome!
Open an issue to suggest features or improvements.

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/heavendoor.git
cd heavendoor

# Create venv and install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set up API key
echo "OPENROUTER_API_KEY=your_key" > .env

# Run tests
./venv/bin/python main.py --prompt-file example_prompt.txt
```

---

## 📜 License

MIT License - See [LICENSE](LICENSE) file for details

---

## 🙏 Credits

**Built With:**
- [OpenRouter](https://openrouter.ai/) - AI model API
- [Google Gemini](https://deepmind.google/technologies/gemini/) - AI models
- [Pillow](https://python-pillow.org/) - Image processing
- [OpenAI Python SDK](https://github.com/openai/openai-python) - API client

**Special Thanks:**
- OpenRouter team for excellent API service
- Google AI team for Gemini models
- Open source community

---

## 📞 Support

- **Documentation**: See files in this repository
- **Issues**: https://github.com/yourusername/heavendoor/issues
- **API Provider**: https://openrouter.ai/docs
- **Community**: [Discord/Forum link if available]

---

## 🎨 Example Gallery

### Monochrome Manga
Traditional black and white manga style with screentones and high contrast.

**Generated from:**
```bash
./venv/bin/python main.py "A samurai warrior in a bamboo forest"
```

**Output:**
- 4 pages, traditional manga style
- Black and white with screentones
- Professional ink lines

### Colored Manga
Modern full-color manga with vibrant anime art style.

**Generated from:**
```bash
./venv/bin/python main.py --color --char-ref image \
  --prompt-file example_prompt.txt
```

**Output:**
- 4 pages, full color
- Character reference sheets included
- Modern webtoon style

### With Character Sheets
Character-focused manga with reference sheets for consistency.

**Generated from:**
```bash
./venv/bin/python main.py --char-ref image "Your story"
```

**Output:**
- High-quality character designs
- Consistent appearance across pages
- Reference sheets saved separately

---

## 🚀 Quick Examples

Try these commands to see different features:

```bash
# 1. Simple monochrome manga (fastest)
./venv/bin/python main.py "A cat discovering magic powers"

# 2. Colored manga
./venv/bin/python main.py --color "A magical girl transformation"

# 3. With character sheets for consistency
./venv/bin/python main.py --char-ref image "A detective solving a mystery"

# 4. Full-featured (best quality)
./venv/bin/python main.py --mode page --char-ref image --color \
  "An epic space adventure"

# 5. From example file
./venv/bin/python main.py --prompt-file example_prompt.txt --color
```

---

## 📈 Version History

**v2.0** (2025-11-22) - Current
- ✅ Structured outputs with JSON Schema
- ✅ Color mode support
- ✅ OpenRouter API integration
- ✅ 100% reliability

**v1.0** (2025-11-22)
- Initial OpenRouter migration
- Per-panel and per-page modes
- Character reference sheets
- PDF assembly

**Pre-v1.0**
- Original Google AI Studio implementation

[View full changelog →](CHANGELOG.md)

---

## ⚡ Performance Tips

### For Best Results

**Speed:**
- Use `--mode page` (faster)
- Use `--char-ref text` (skip character sheets)
- Generate monochrome (same speed, but simpler prompts)

**Quality:**
- Use `--mode panel` (more control)
- Use `--char-ref image` (better consistency)
- Use `--color` for modern style

**Cost Optimization:**
- Skip character sheets for simple stories
- Use page mode to reduce API calls
- Batch process multiple stories

**Optimal Balance:**
```bash
./venv/bin/python main.py --mode page --color "Your story"
```
- Fast generation (page mode)
- Modern look (color)
- Good quality
- Reasonable cost

---

**Ready to create amazing manga? Let's get started!** 🎨📚

```bash
./venv/bin/python main.py --color "Your story begins here..."
```
