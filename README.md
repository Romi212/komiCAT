<p align="center"> <img width="1544" height="482" alt="logo-horizontal-byn" src="https://github.com/user-attachments/assets/b5e5599b-4037-4e91-8b82-6c9b658dfd51" />
 <b>A computer-assisted translation (CAT) tool for manga.</b> </p> <p align="center"> <a href="../../releases/latest"><b>⬇ Download the latest release</b></a> </p>

## Features
 
- **Bubble and panel detection:** automatically finds speech bubbles, free text and SFX on each page, and detects the panels.
- **Text extraction (OCR):** reads Japanese text from the detected boxes, one page or the whole chapter at once.
- **Segment editor:** translate each segment next to the page, confirm it when done, and reorder segments automatically or by hand.
- **Translation Memory and Termbase:** reuse earlier translations and keep terminology consistent across a project.
- **Dictionary lookup:** select source text to get Japanese-English dictionary entries.
- **Spell checking** for your translation.
- **Projects and chapters:** organize a series into chapters, and reopen recent projects from the launcher.

## Installation

### Windows installer (recommended)
 
1. Go to the [Releases page](../../releases/latest).
2. Download `KomiCAT-Setup-x.y.z.exe`.
3. Run it. No admin rights are needed, and it installs to your user folder.
> Windows SmartScreen may show an "unknown publisher" warning because the installer is not code-signed. Click **More info > Run anyway**.
 
You do **not** need Python installed.

### System requirements
 
| | |
|---|---|
| **OS** | Windows 10 / 11, 64-bit |
| **RAM** | 2 GB minimum, 8 GB recommended |
| **Disk space** | 5 GB free |
| **GPU** | Not required |
| **Internet** | Needed on first run to download the models |
 




## Quick start
1) Open KomiCAT and click Create New (or Load Project).
2) Add a chapter and open its images with Open Images.
3) Click Detect page Bubbles (or Batch detect Bubbles for the whole chapter).
4) Click Extract Text (or Extract all text) to run OCR.
5) Translate each segment in the left panel and confirm it.
6) Use Edition Mode to fix boxes, combine bubbles or change their type.

## Models
 
KomiCAT relies on these pretrained models. They are downloaded on first run and are **not** part of this repository's code.
 
| Task | Model | License |
|---|---|---|
| Panel detection | [leoxs22/manga-panel-detector-yolo26n](https://huggingface.co/leoxs22/manga-panel-detector-yolo26n) (Hugging Face) | AGPL-3.0 (fine-tuned from Ultralytics YOLO) |
| Text and bubble detection | [ogkalu/comic-text-and-bubble-detector](https://huggingface.co/ogkalu/comic-text-and-bubble-detector)(Hugging Face) | See the model page |
| Japanese OCR | [manga-ocr](https://github.com/kha-white/manga-ocr) ([model on Hugging Face](https://huggingface.co/kha-white/manga-ocr-base)) | See the project page |
 
Thanks to the authors for making these models available.

## Dictionaries
- Spellchecker using [symspell](https://github.com/wolfgarbe/SymSpell) and [hunspell](https://hunspell.github.io/) libraries.
- Japanese dictionery using [Jamdict](https://github.com/neocl/jamdic) library.

## Credits
Created by Romi. 

Komi-chan mascot designed by Abi Melina Panis.


Logo and app graphic design by María Paz Berterreix.

## License

KomiCAT is free software licensed under the
[GNU Affero General Public License v3.0](https://www.gnu.org/licenses/agpl-3.0.html) (AGPL-3.0).
You can use, study, modify and redistribute it under the terms of that license.
The full text is in the [LICENSE](LICENSE) file, and the complete source code is available in this repository.
